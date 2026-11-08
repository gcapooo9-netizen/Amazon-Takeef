import csv
import json
import os
import re
import time
import traceback
from datetime import datetime
from urllib.parse import urljoin, urlparse, parse_qs, urlencode, urlunparse

import requests
from bs4 import BeautifulSoup

API_KEY = "a910760e328d613a889ff63b14a4fd49"
TOKEN = "8996279782:AAEJ-n3vP4K9bts15GC0_htKMceRC4yHj8E"
CHAT_ID = "5124680786"

BASE = "https://www.jumia.com.eg"
LISTING_URLS = [
    "https://www.jumia.com.eg/ar/mens-jackets-coats/defacto/",
]
MAX_PAGES = 6

CHECK_EVERY_SECONDS = 30 * 60  # كل نص ساعة
CSV_FILE = "price_history.csv"
ALERTS_FILE = "alerts_sent.json"
MIN_DROP_PERCENT = 20
LOW_CREDITS_WARNING = 400  # تنبيه مبكر
REPEAT_ERROR_EVERY = 8
RUN_SANITY_CHECK = False


class OutOfCredits(Exception):
    pass


# ---------------------------- أدوات عامة ----------------------------

def clean_error(e):
    s = str(e)
    for secret in (API_KEY, TOKEN):
        if secret:
            s = s.replace(secret, "***")
    return s[:300]


def send_telegram(text):
    for attempt in range(1, 4):
        try:
            r = requests.post(
                f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                data={
                    "chat_id": CHAT_ID,
                    "text": text[:4000],
                    "disable_web_page_preview": True,
                },
                timeout=30,
            )
            if r.status_code == 200:
                return True
            print(f"تليجرام رد بخطأ {r.status_code}: {clean_error(r.text)}")
            if r.status_code == 429:
                time.sleep(5)
                continue
            return False
        except Exception as e:
            print(f"فشل إرسال تليجرام (محاولة {attempt}): {clean_error(e)}")
            time.sleep(3)
    return False


def send_critical(text):
    """للرسايل المهمة: يفضل يحاول دقيقة بدقيقة لحد 30 مرة"""
    for i in range(30):
        if send_telegram(text):
            return True
        print(f"التنبيه المهم لسه ما وصلش، هحاول تاني ({i + 1}/30)")
        time.sleep(60)
    return False


def get_credits():
    try:
        r = requests.get(
            "https://api.scraperapi.com/account",
            params={"api_key": API_KEY},
            timeout=30,
        )
        if r.status_code == 200:
            d = r.json()
            return d.get("requestCount"), d.get("requestLimit")
    except Exception as e:
        print("مقدرتش أعرف الرصيد:", clean_error(e))
    return None


def to_number(text):
    cleaned = re.sub(r"[^\d.]", "", text.replace(",", ""))
    return float(cleaned) if cleaned else None


def confirm_out_of_credits(code):
    """401/403 ممكن تكون رصيد خلص أو سبب تاني، فنتأكد من حسابك الأول"""
    credits = get_credits()
    if credits and credits[0] is not None and credits[1] is not None:
        remaining = credits[1] - credits[0]
        if remaining > 50:
            raise RuntimeError(
                f"ScraperAPI رد بخطأ {code} رغم إن الرصيد المتبقي {remaining}"
            )
    raise OutOfCredits(f"ScraperAPI رد بخطأ {code}")


def fetch(url):
    last_error = None
    for attempt in range(1, 4):
        try:
            r = requests.get(
                "https://api.scraperapi.com/",
                params={"api_key": API_KEY, "url": url, "country_code": "eg"},
                timeout=90,
            )
            if r.status_code in (401, 403):
                confirm_out_of_credits(r.status_code)
            r.raise_for_status()
            return r.text
        except OutOfCredits:
            raise
        except Exception as e:
            last_error = e
            print(f"  محاولة {attempt} فشلت: {clean_error(e)}")
            time.sleep(3 * attempt)
    raise last_error


# ---------------------------- قراءة الصفحات ----------------------------

def parse_listing(soup):
    items = []
    for card in soup.select("article.prd"):
        a = card.select_one("a.core") or card.find("a", href=True)
        if not a or not a.get("href"):
            continue
        link = urljoin(BASE, a["href"].split("?")[0].split("#")[0])
        name_el = card.select_one(".name")
        name = name_el.get_text(strip=True) if name_el else ""
        price_el = card.select_one(".prc")
        price = to_number(price_el.get_text()) if price_el else None
        items.append((name, price, link))
    return items


def next_page_url(soup):
    a = soup.select_one(
        'a[aria-label="Next Page"], a[aria-label="الصفحة التالية"]'
    )
    if a and a.get("href"):
        return urljoin(BASE, a["href"])
    return None


def with_page(url, page):
    parts = urlparse(url)
    q = parse_qs(parts.query)
    q.pop("srsltid", None)
    q["page"] = [str(page)]
    return urlunparse(parts._replace(query=urlencode(q, doseq=True), fragment=""))


def scan_listings():
    found = {}
    partial = False
    for start in LISTING_URLS:
        url = start
        for page in range(1, MAX_PAGES + 1):
            print(f"  صفحة {page}: {url}")
            try:
                soup = BeautifulSoup(fetch(url), "html.parser")
            except OutOfCredits:
                raise
            except Exception as e:
                if page == 1 and not found:
                    raise
                print("  فشلت الصفحة:", clean_error(e))
                partial = True
                break

            items = parse_listing(soup)
            new = 0
            for name, price, link in items:
                if link not in found:
                    found[link] = (name, price)
                    new += 1
            print(f"  لقيت {len(items)} منتج ({new} جديد)")

            if not items or new == 0:
                break
            url = next_page_url(soup) or with_page(start, page + 1)
            time.sleep(2)
    return found, partial


def parse_product_page(html):
    soup = BeautifulSoup(html, "html.parser")
    name = None
    price = None

    for tag in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(tag.string or "")
        except json.JSONDecodeError:
            continue
        items = data if isinstance(data, list) else [data]
        for item in items:
            if not isinstance(item, dict):
                continue
            if not name and item.get("name"):
                name = item["name"]
            offers = item.get("offers")
            if isinstance(offers, list):
                offers = offers[0] if offers else None
            if not price and isinstance(offers, dict) and offers.get("price"):
                price = to_number(str(offers["price"]))

    if not name:
        og = soup.find("meta", property="og:title")
        if og and og.get("content"):
            name = og["content"]
    if not price:
        meta = soup.find("meta", property="product:price:amount")
        if meta and meta.get("content"):
            price = to_number(meta["content"])
    if not price:
        el = soup.select_one("span.-b.-ubpt, span[class*='-fs24']")
        if el:
            price = to_number(el.get_text())
    return name, price


def get_product(url):
    return parse_product_page(fetch(url))


# ---------------------------- التخزين ----------------------------

def load_history():
    last, highest = {}, {}
    try:
        with open(CSV_FILE, encoding="utf-8") as f:
            for row in list(csv.reader(f))[1:]:
                if len(row) > 3:
                    try:
                        p = float(row[1])
                    except ValueError:
                        continue
                    last[row[3]] = p
                    highest[row[3]] = max(highest.get(row[3], 0), p)
    except FileNotFoundError:
        pass
    return last, highest


def save_price(price, name, url):
    new_file = not os.path.exists(CSV_FILE)
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new_file:
            w.writerow(["time", "price", "product", "url"])
        w.writerow([datetime.now().strftime("%Y-%m-%d %H:%M"), price, name, url])


def load_alerts():
    try:
        with open(ALERTS_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_alerts(alerts):
    try:
        with open(ALERTS_FILE, "w", encoding="utf-8") as f:
            json.dump(alerts, f)
    except Exception as e:
        print("مقدرتش أحفظ التنبيهات:", e)


# ---------------------------- المشاكل والرصيد ----------------------------

def report_problem(state, key, text):
    count = state["problems"].get(key, 0) + 1
    state["problems"][key] = count
    print(f"مشكلة ({count}): {text}")
    if count == 1 or count % REPEAT_ERROR_EVERY == 0:
        send_telegram(f"حصلت مشكلة في المراقبة!\n{text}\nعدد اللفات ورا بعض: {count}")


def clear_problem(state, key):
    if state["problems"].pop(key, 0) > 0:
        send_telegram(f"المشكلة اتحلت ({key})، المراقبة شغالة تمام.")


def check_credits_warning(state):
    credits = get_credits()
    if not credits or credits[0] is None or credits[1] is None:
        return
    used, limit = credits
    remaining = limit - used
    print(f"الرصيد المتبقي: {remaining} من {limit}")
    if remaining <= LOW_CREDITS_WARNING and not state["warned_credits"]:
        send_telegram(
            f"تنبيه: رصيد ScraperAPI قرب يخلص!\n"
            f"المتبقي: {remaining} نقطة من {limit}\n"
            f"جهّز مفتاح جديد."
        )
        state["warned_credits"] = True


# ---------------------------- المنطق الأساسي ----------------------------

def process_item(url, name, price, last, highest, alerted, rejected):
    if price is None or price <= 0:
        return
    if rejected.get(url) == price:
        return

    prev = last.get(url)
    hi = highest.get(url)

    verify = False
    if prev is not None and hi:
        big_move = price > prev * 2 or price < prev * 0.5
        drop = (hi - price) / hi * 100
        would_alert = drop >= MIN_DROP_PERCENT and (
            url not in alerted or price < alerted[url]
        )
        verify = big_move or would_alert

    if verify:
        vname, vprice = get_product(url)
        if vprice is None or vprice <= 0:
            print("  مقدرتش أتأكد من صفحة المنتج، تجاهلت القراءة:", url)
            return
        if abs(vprice - price) / price > 0.02:
            print(f"  القايمة {price} والصفحة {vprice}، تجاهلت التنبيه:", url)
            rejected[url] = price
            return
        price = vprice
        name = vname or name

    save_price(price, name, url)
    last[url] = price
    highest[url] = max(highest.get(url, 0), price)
    print(f"  {name} | {price:.0f} جنيه")

    if prev is not None and hi:
        drop = (hi - price) / hi * 100
        if drop >= MIN_DROP_PERCENT and (url not in alerted or price < alerted[url]):
            msg = (
                f"تخفيض {drop:.1f}%!\n{name}\n"
                f"من {hi:.0f} إلى {price:.0f} جنيه\n"
                f"وفرت {hi - price:.0f} جنيه\n"
                f"(السعر متأكد منه من صفحة المنتج)\n"
                f"رابط الشراء: {url}"
            )
            print(msg)
            send_telegram(msg)
            alerted[url] = price
            save_alerts(alerted)


def main():
    state = {"warned_credits": False, "problems": {}, "known_count": 0}
    last, highest = load_history()
    alerted = load_alerts()
    rejected = {}
    print("بدأت المراقبة في صمت (كل نص ساعة)...")

    while True:
        try:
            found, partial = scan_listings()

            if not found:
                report_problem(state, "scan", "القايمة رجعت فاضية (ممكن شكل الصفحة اتغير)")
            else:
                clear_problem(state, "scan")

                if state["known_count"] and len(found) < state["known_count"] * 0.5:
                    report_problem(
                        state, "count",
                        f"عدد المنتجات نزل من {state['known_count']} إلى {len(found)}",
                    )
                else:
                    clear_problem(state, "count")

                if partial:
                    report_problem(state, "partial", "في صفحة قايمة فشلت، فحصت جزء بس من المنتجات")
                else:
                    clear_problem(state, "partial")

                for url, (name, price) in found.items():
                    try:
                        process_item(url, name, price, last, highest, alerted, rejected)
                    except OutOfCredits:
                        raise
                    except Exception as e:
                        print("  خطأ في منتج:", clean_error(e))

                state["known_count"] = len(found)

            check_credits_warning(state)

        except OutOfCredits as e:
            print("الرصيد خلص:", e)
            send_critical(
                "رصيد ScraperAPI خلص! المراقبة وقفت.\n\n"
                "اعمل كده:\n"
                "1) اعمل حساب جديد في scraperapi.com وخد المفتاح\n"
                "2) غيّر قيمة API_KEY في السكريبت\n"
                "3) شغّل السكريبت تاني\n\n"
                "الأسعار المتسجلة محفوظة، هيكمل من عندها."
            )
            return
        except Exception as e:
            report_problem(state, "loop", f"خطأ: {clean_error(e)}")

        time.sleep(CHECK_EVERY_SECONDS)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        send_telegram("المراقبة اتوقفت يدويًا.")
    except Exception as e:
        send_critical(
            f"السكريبت وقع وبطل يشتغل!\nالسبب: {clean_error(e)}\n"
            f"{clean_error(traceback.format_exc()[-400:])}"
        )
        raise
