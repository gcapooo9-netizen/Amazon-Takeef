import time
import random
import html
import ssl
import json
import os
import re
import requests
import cloudscraper
from bs4 import BeautifulSoup

# ⚠️ التوكن ومعرف الشات الخاص بك
TOKEN = "8996279782:AAEJ-n3vP4K9bts15GC0_htKMceRC4yHj8E"
CHAT = "5124680786"

# قائمة الـ ASINs المستهدفة
TARGET_ASINS = [
    "B0GHS9TS5Z", "B0CTKGY2BR", "B0BXSTDJ7V", "B0H2BF6HKJ", "B0DBR2DRXP", 
    "B0BXPPM3HR", "B0G2JW3JF2", "B0BXPKSVFQ", "B0F5VDGK7H", "B0DGF8PX4Z", 
    "B01LCVQ0UY", "B09YYP2LC2", "B0DFCMFD8J", "B0H2BVQ27G", "B0G2JNFS6P", 
    "B0D3WV9RM4", "B0101RZ71S", "B08Y8YTQGP", "B0H68LZFYD", "B0FLWVKXZS", 
    "B0H2BJ19DV", "B0FQBZG498", "B091JF5YJC", "B0GHSLYR5C", "B0GYLS6CD7", 
    "B0CLVSYCYT", "B0CBVPX5CZ", "B0H2MF1D6N", "B0FGXSKT74", "B0D9TQY7V2", 
    "B091CXDCTT", "B0GSKYT9P2", "B0H6VKX5Q9", "B0H1D2S3WY", "B0BXST5BQB", 
    "B01LCVOK06", "B09V4LT8VV", "B0FQC1WY73", "B08WJMZM7W", "B0D42DNVXY", 
    "B0FQ39Q3YF", "B0H2BJXGDF", "B0H1NJF67H", "B0HD1H97P8", "B0F4D3Z447", 
    "B09TSQ4897", "B09NYKDPRS", "B0101SX5NE", "B0CBQN599H", "B08TBRYVZB", 
    "B0101RYSJA", "B0FQBZCGCF", "B0FPJRVW58", "B0GMWTHDW7", "B0H2MY722K", 
    "B08Z49DXMD", "B0C5B7QQT1", "B0FQC2DD5Q", "B09TSM2JMC", "B091D892YT", 
    "B0H2BM4WR1", "B0CSYVHZ4R", "B093W76H71", "B0101RY1RO", "B0CW1NYQ7N", 
    "B0DT2M7YWW", "B0GRPMWT6D", "B0FGXSNNNP", "B09MC6CX2W", "B0DT2H5RC8", 
    "B098TXJRPS", "B0H2BKBXS6", "B0H2BKS84H", "B0F89F41Q8", "B0CSX89CM1", 
    "B0C2VN95K3", "B0CC6N12B9", "B097LTGV21", "B0CSZ1HMQL", "B084DRQJ72", 
    "B0C9MFF9MX", "B0H2BKJ897", "B0D3431RJG", "B0GVB6MXHM", "B01LCVR50S", 
    "B0GHT3RWP8", "B0101RY88G", "B0F8R6R4S1", "B098VYWTXS", "B089G97MK3", 
    "B0101RXZK8", "B0B5DYTCJC", "B0DHXGGTPB", "B07MW44JP3", "B0H2N18H7Y", 
    "B0DY86DQ5K", "B0GHS61LBR", "B0DD76VSYL", "B0BXPMRTM5", "B0F626T15H"
]

DB_FILE = "custom_products.json"

H = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Upgrade-Insecure-Requests": "1",
    "Connection": "keep-alive"
}

AR = str.maketrans("٠١٢٣٤٥٦٧٨٩٫٬", "0123456789.,")

if os.path.exists(DB_FILE):
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            last_prices = json.load(f)
        print(f"📂 تم استرجاع {len(last_prices)} منتج محفوظ من قبل.")
    except Exception:
        last_prices = {}
else:
    last_prices = {}

def save_prices():
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(last_prices, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("خطأ في حفظ الملف:", e)

def create_scraper():
    ctx = ssl.create_default_context()
    ctx.set_ciphers("DEFAULT@SECLEVEL=1")
    scraper = cloudscraper.create_scraper(
        browser={"browser": "chrome", "platform": "windows", "desktop": True},
        ssl_context=ctx
    )
    scraper.headers.update(H)
    return scraper

scraper = create_scraper()

def send(msg):
    u = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        res = requests.post(
            u, 
            json={"chat_id": CHAT, "text": msg, "parse_mode": "HTML", "disable_web_page_preview": False}, 
            timeout=15
        )
        if res.status_code != 200:
            print("مشكلة من تيليجرام:", res.text)
        time.sleep(1.5)
    except Exception as e:
        print("خطأ في إرسال تيليجرام:", e)

def clean(text):
    x = text.translate(AR).replace(",", "")
    m = re.search(r"\d+(?:\.\d+)?", x)
    return float(m.group(0)) if m else None

def extract_product_name(soup, asin):
    for selector in ["span#productTitle", "h1.a-size-large", "#title"]:
        tag = soup.select_one(selector)
        if tag:
            text = tag.get_text(strip=True)
            if text:
                return text
    return f"منتج ({asin})"

def extract_price(soup):
    for selector in [".a-price .a-offscreen", "#priceblock_ourprice", "#priceblock_dealprice", ".a-color-price"]:
        tag = soup.select_one(selector)
        if tag:
            p = clean(tag.get_text())
            if p is not None and p > 0:
                return p
    return None

def check_products():
    global scraper
    print(f"[{time.strftime('%H:%M:%S')}] جاري فحص المنتجات المخصصة ({len(TARGET_ASINS)} منتج)...")
    
    if not TARGET_ASINS:
        print("⚠️ قائمة المنتجات (TARGET_ASINS) فارغة!")
        return False

    updated_any = False

    for asin in TARGET_ASINS:
        product_link = f"https://www.amazon.eg/dp/{asin}"
        try:
            r = scraper.get(product_link, timeout=25)
            if r.status_code != 200:
                print(f"تحذير: أمازون ردت بالكود {r.status_code} للمنتج {asin}")
                continue

            if "api-services-support@amazon.com" in r.text or "Enter the characters you see below" in r.text:
                print("⚠️ أمازون طلبت كابتشا. جاري تجديد الجلسة...")
                scraper = create_scraper()
                time.sleep(5)
                continue

            soup = BeautifulSoup(r.text, "html.parser")
            price = extract_price(soup)
            
            if price is None:
                print(f"⚠️ تعذر استخراج السعر للمنتج {asin}")
                continue

            raw_name = extract_product_name(soup, asin)
            safe_name = html.escape(raw_name)
            old_price = last_prices.get(asin)

            if old_price is None:
                # أول مرة نسجل المنتج مش هنبعت رسالة، هنحفظ سعره بس كمرجع
                last_prices[asin] = price
                updated_any = True
                print(f"✨ تسجيل أول للمنتج: {raw_name} | السعر: {price} ج.م")

            elif price != old_price:
                diff = price - old_price
                
                if diff < 0:
                    # السعر نزل، نحسب نسبة الخصم
                    discount_percentage = abs(diff) / old_price * 100
                    print(f"📉 نزول سعر: {raw_name} | من {old_price} إلى {price} (نسبة الخصم: {discount_percentage:.1f}%)")
                    
                    # الشرط: هل نسبة الخصم أكتر من 20%؟
                    if discount_percentage > 20:
                        msg = (
                            f"🔥 <b>لقطة! تخفيض أكتر من 20%!</b>\n\n"
                            f"📦 <a href='{product_link}'>{safe_name}</a>\n"
                            f"📉 نسبة الخصم: <b>{discount_percentage:.1f}%</b>\n"
                            f"من: <s>{old_price}</s> ج.م\n"
                            f"إلى: <b>{price} ج.م</b>"
                        )
                        send(msg)
                else:
                    print(f"📈 زيادة سعر (تم التجاهل): {raw_name} من {old_price} إلى {price} ج.م")

                # نحدث السعر الجديد في قاعدة البيانات في كل الأحوال عشان المقارنة القادمة
                last_prices[asin] = price
                updated_any = True
            else:
                print(f"✔️ مستقر: {raw_name} | السعر: {price} ج.م")

            time.sleep(random.uniform(3, 6))

        except Exception as e:
            print(f"خطأ أثناء فحص المنتج {asin}:", e)
            scraper = create_scraper()

    if updated_any:
        save_prices()

    return True

print("مراقبة التخفيضات الكبرى (أكتر من 20%) شغالة...")
while True:
    check_products()
    sleep_time = random.randint(1680, 1980)
    print(f"انتظار اللفة القادمة بعد {sleep_time // 60} دقيقة...")
    time.sleep(sleep_time)
