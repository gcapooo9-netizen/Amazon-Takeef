import time
import json
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

TOKEN = "8996279782:AAEJ-n3vP4K9bts15GC0_htKMceRC4yHj8E"
CHAT = "@gcapooo9"
DATA_FILE = "prices_cache.json"

# لستة المنتجات المدمجة
PRODUCTS = [
    # --- قسم التكييفات (81 منتج) ---
    "https://kenzz.com/en/product/LUBX8N7XUA4Q/LG-Dual-Cool-Split-Air-Conditioner-3-HP%2C-Cooling-%26-Heating-White-S4-W24K22ME",
    "https://kenzz.com/product/44N3SYU6UF7Q/%D8%AA%D9%83%D9%8A%D9%8A%D9%81-%D8%B3%D8%A8%D9%84%D9%8A%D8%AA-%D9%87%D8%A7%D9%8A%D8%B1-1.5-%D8%AD%D8%B5%D8%A7%D9%86-%D8%A8%D8%A7%D8%B1%D8%AF-%D9%88%D8%B3%D8%A7%D8%AE%D9%86-%D8%A3%D8%A8%D9%8A%D8%B6-HSU-12KHROCC",
    "https://kenzz.com/en/product/9STXGD9JPN4W/Midea-Split-Air-Conditioner-1.5-HP-Cooling-Only-White-MSC1T-12CR-N",
    "https://kenzz.com/en/product/2XR8F6QXNC3P/LG-Split-Air-Conditioner-3-HP%2C-Cooling-%26-Heating-Black-S4-W24K2RME",
    "https://kenzz.com/en/product/T8MG5MHABR3B/Midea-Mission-Pro-Air-Conditioner-3-HP-Cooling-and-Heating-White-MSC1T-24HR-N-F",
    "https://kenzz.com/en/product/NQRBU36VQXAA/Carrier-Optimax-Pro-Cooling-Split-Air-Conditioner-1.5-HP-White-53KHCT12N-708",
    "https://kenzz.com/en/product/PB7EMU9ZX59K/Haier-Split-Air-Conditioner-1.5-HP%2C-Cooling-Only-White-HSU-12KCRIC",
    "https://kenzz.com/en/product/S47QVMX8XZZD/Sharp-Split-Air-Conditioner-3-HP%2C-Cooling-%26-Heating-White-AY-A24ZSE",
    "https://kenzz.com/en/product/CMNHCZYZFWP5/Beko-Split-Air-Conditioner-Inverter-Motor-2.25-HP-Cooling-Only-White-BICT1820",
    "https://kenzz.com/en/product/DLKP9QK4XCXM/Sharp-Split-Air-Conditioner-1.5-HP%2C-Cooling-Only-White-AH-AP12ZHE",
    "https://kenzz.com/en/product/ZXU4UF445QRG/Beko-Split-Air-Conditioner-Inverter-Motor-1.5-HP-Cooling-and-Heating-White-BIHT1240",
    "https://kenzz.com/en/product/SA7EE5P97A5B/%D8%AA%D9%83%D9%8A%D9%8A%D9%81-%D8%B3%D8%A8%D9%84%D9%8A%D8%AA-%D9%87%D8%A7%D9%8A%D8%B1-2.25-%D8%AD%D8%B5%D8%A7%D9%86-%D8%A8%D8%A7%D8%B1%D8%AF-%D9%88%D8%B3%D8%A7%D8%AE%D9%86-%D8%A3%D8%A8%D9%8A%D8%B6-HSU-18KHROC",
    "https://kenzz.com/en/product/WMPKMUQ7ABVP/LG-Art-Cool-Inverter-Split-Air-Conditioner-1.5-HP%2C-Cooling-%26-Heating-Gray-S4-W12JARZA",
    "https://kenzz.com/en/product/7ZANQ2MFRJLW/Carrier-Air-Conditioner-1.5-HP-Split-Cool-Optimax-Inverter-53KHCT12DN-708F",
    "https://kenzz.com/en/product/EM8CRL45HWDU/Air-Conditioner-3-Hp-Hot-Cold-White-Ay-Xp24Uhe",
    "https://kenzz.com/en/product/KNWVEWC5UCTM/Carrier-Optimax-Split-Air-Conditioner%2C-Cooling%2C-3-HP%2C-White-53KHCT24N-708",
    "https://kenzz.com/en/product/YRPG3FFBV8L7/LG-Split-Air-Conditioner-2.25-HP%2C-Cooling-%26-Heating-White-S4-H18RZAAA",
    "https://kenzz.com/en/product/4XPMVKAJ7EAQ/Sharp-Inverter-Split-Air-Conditioner-2.25-HP%2C-Cooling-Only-Silver-AH-XP18UHE",
    "https://kenzz.com/en/product/XX5VKC847X8L/Sharp-Split-Air-Conditioner-2.25-HP%2C-Cooling-Digital-Plasma-Cluster-White-AH-AP18ZHE",
    "https://kenzz.com/en/product/6GCM6UAS9YTF/LG-Split-Air-Conditioner-3-HP%2C-Cooling-Only-White-S4-Q24K22ME",
    "https://kenzz.com/en/product/FMULFQUJ2KGR/Beko-Split-Air-Conditioner-Inverter-Motor-3-HP-Cooling-Only-White-BICT2420",
    "https://kenzz.com/en/product/2FXVUX4W8WTT/Tornado-Split-Air-Conditioner-1.5-Hp-Fast-Cooling-White-Th-C12Bee",
    "https://kenzz.com/en/product/ZE5H7WYPFNBZ/%D8%AA%D9%83%D9%8A%D9%8A%D9%81-%D9%87%D9%88%D8%A7%D8%A1-%D9%87%D8%A7%D9%8A%D8%B1-%D8%B3%D8%A8%D9%84%D9%8A%D8%AA-%D8%B3%D9%85%D8%A7%D8%B1%D8%AA-%D9%83%D9%88%D9%88%D9%84-1.5-%D8%AD%D8%B5%D8%A7%D9%86-%D8%A8%D8%A7%D8%B1%D8%AF-%D8%A8%D9%84%D8%A7%D8%B2%D9%85%D8%A7-%D8%B4%D8%A7%D8%B4%D8%A9-%D8%AF%D9%8A%D8%AC%D9%8A%D8%AA%D8%A7%D9%84-%D8%A3%D8%A8%D9%8A%D8%B6-HSU-12KCROCC",
    "https://kenzz.com/en/product/P7CY9X3MXB4N/Hisense-Split-Air-Conditioner-1.5-HP-Cooling-%26-Heating-Digital-Inverter-White-HI-E12INVHP",
    "https://kenzz.com/en/product/T49DJPYPCZ8B/Sharp-Inverter-Split-Air-Conditioner-2.25-HP%2C-Cooling-%26-Heating-Silver-AY-XP18UHE",
    "https://kenzz.com/en/product/ZA6TKBKJH87G/Eta-King-Desert-Air-Conditioner-220-Watts-75-Liters-Ac-075N",
    "https://kenzz.com/en/product/HB2GNHQ77PUT/LG-Hero-Split-Air-Conditioner-1.5-HP%2C-Cooling-%26-Heating-White-S4-H12RZAAA",
    "https://kenzz.com/en/product/SDHV9PETTSXJ/Sharp-Inverter-Digital-Plasma-Cluster-Split-Air-Conditioner-1.5-Hp-White-Ah-Xp12Bme",
    "https://kenzz.com/en/product/DNF4G64GULG2/%D8%AA%D9%83%D9%8A%D9%8A%D9%81-%D8%B3%D8%A8%D9%84%D9%8A%D8%AA-%D9%87%D8%A7%D9%8A%D8%B1-2.25-%D8%AD%D8%B5%D8%A7%D9%86-%D8%A8%D8%A7%D8%B1%D8%AF-%D9%81%D9%82%D8%B7-%D8%A3%D8%A8%D9%8A%D8%B6-HSU-18KCRIC",
    "https://kenzz.com/en/product/735FX38YXKZU/Carrier-Split-Air-Conditioner-1.5-Hp-Optimax%2C-Cooling-%26-Heating-53Qhct-12",
    "https://kenzz.com/en/product/7CPFL2AWR3CN/Sharp-Inverter-Split-Air-Conditioner-2.25-HP%2C-Cooling-Plasma-Cluster-Black-AY-XP18YHEB",
    "https://kenzz.com/en/product/3NLVJXXE2MQN/%D8%AA%D9%83%D9%8A%D9%8A%D9%81-%D8%B3%D8%A8%D9%84%D9%8A%D8%AA-%D9%87%D8%A7%D9%8A%D8%B1-1.5-%D8%AD%D8%B5%D8%A7%D9%86-%D8%A8%D8%A7%D8%B1%D8%AF-%D8%A7%D9%86%D9%81%D8%B1%D8%AA%D8%B1-%D8%A8%D9%84%D8%A7%D8%B2%D9%85%D8%A7-%D8%A3%D8%A8%D9%8A%D8%B6-HSU-12KCRIA",
    "https://kenzz.com/en/product/VVW8PQYLTTFN/Carrier-%D8%AA%D9%83%D9%8A%D9%8A%D9%81-%D8%B3%D8%A8%D9%84%D9%8A%D8%AA-%D8%A3%D9%88%D8%A8%D8%AA%D9%8A%D9%85%D8%A7%D9%83%D8%B3-1.5-%D8%AD%D8%B5%D8%A7%D9%86-%D8%A8%D8%A7%D8%B1%D8%AF-%D8%A3%D8%A8%D9%8A%D8%B6-KHCT-12-OPTIMAX",
    "https://kenzz.com/en/product/VKAVZG7UN64X/LG-Split-Air-Conditioner-2.25-HP%2C-Cooling-Only-White-S4-C18RZAAA",
    "https://kenzz.com/en/product/6FKKTC68ATFK/Media-Split-Air-Conditioner-3-HP%2C-Cooling-Only-White-MSCT-24CR",
    "https://kenzz.com/en/product/KFXBMXGMUAZR/LG-Dual-Cool-Split-Air-Conditioner-1.5-HP%2C-Cooling-%26-Heating-White-S4NW12JA2MA",
    "https://kenzz.com/en/product/2AK92F6VE84S/Fresh-Split-Air-Conditioner-1.5-HP%2C-Cooling-%26-Heating-White-SFW13H-IP-SEW13H-O",
    "https://kenzz.com/en/product/YNSGS7TFK93J/LG-Split-Air-Conditioner-1.5-HP%2C-Cooling-%26-Heating-White-S4-W12JA3AE",
    "https://kenzz.com/en/product/TP6GFPV39NS9/%D8%AA%D9%83%D9%8A%D9%8A%D9%81-%D8%B3%D8%A8%D9%84%D9%8A%D8%AA-%D9%87%D8%A7%D9%8A%D8%B1-3-%D8%AD%D8%B5%D8%A7%D9%86-%D8%A8%D9%84%D8%A7%D8%B2%D9%85%D8%A7-%D8%A8%D8%A7%D8%B1%D8%AF-%D9%81%D9%82%D8%B7-%D8%A3%D8%A8%D9%8A%D8%B6-HSU-24KCROCC",
    "https://kenzz.com/en/product/49ZXBH6FDV68/Sharp-Split-Air-Conditioner-3-HP%2C-Cooling-%26-Heating-Digital-Plasma-Cluster-White-AY-AP24ZHE",
    "https://kenzz.com/en/product/L6SK5FZVEMYF/LG-Split-Air-Conditioner-1.5-HP%2C-Cooling-Only-White-S4-C12RZAAA",
    "https://kenzz.com/en/product/VUY7ZSL88LVV/%D8%AA%D9%83%D9%8A%D9%8A%D9%81-%D9%87%D9%88%D8%A7%D8%A1-%D9%87%D8%A7%D9%8A%D8%B1-%D8%B3%D8%A8%D9%84%D9%8A%D8%AA-%D8%B3%D9%85%D8%A7%D8%B1%D8%AA-%D9%83%D9%88%D9%88%D9%84-2.25-%D8%AD%D8%B5%D8%A7%D9%86-%D8%A8%D8%A7%D8%B1%D8%AF-%D8%A8%D9%84%D8%A7%D8%B2%D9%85%D8%A7-%D8%B4%D8%A7%D8%B4%D8%A9-%D8%AF%D9%8A%D8%AC%D9%8A%D8%AA%D8%A7%D9%84-%D8%A3%D8%A8%D9%8A%D8%B6-HSU-18KCROCC",
    "https://kenzz.com/en/product/CK84SSK22XYU/LG-Split-Air-Conditioner-2.25-HP%2C-Cooling-Only-White-S4-Q18KL2MD",
    "https://kenzz.com/en/product/SA7EE5P97A5B/Haier-Split-Air-Conditioner-2.25-HP%2C-Cooling-%26-Heating-White-HSU-18KHROC",
    "https://kenzz.com/en/product/P948HWR9ZKYC/LG-Inverter-Split-Air-Conditioner-3-HP%2C-Cooling-%26-Heating-White-S4-W24K23AE",
    "https://kenzz.com/en/product/VVW8PQYLTTFN/Air-Conditioner-1.5-Hp-Cold-White-Khct-12-Optimax",
    "https://kenzz.com/en/product/7QJWNHR9MZJZ/Midea-Mission-Pro-Air-Conditioner%2C-1.5-HP%2C-Cooling-and-Heating%2C-White-M1SCT-12HRNF-Q8",
    "https://kenzz.com/en/product/DNF4G64GULG2/Haier-Split-Air-Conditioner-2.25-HP%2C-Cooling-Only-White-HSU-18KCRIC",
    "https://kenzz.com/en/product/QJ7KDUJYVKXR/Haier-HSU-12KHRIBC-1.5-HP-Split-Inverter-Air-Conditioner-WiFi-White",
    "https://kenzz.com/en/product/3NLVJXXE2MQN/Haier-Split-Air-Conditioner-1.5-HP-Cooling-Inverter-Plasma-White-HSU-12KCRIA",
    "https://kenzz.com/en/product/CZ365MA4SSGM/Carrier-Optimax-Air-Conditioner-1.5-HP-Cooling-%26-Heating-White-42QHCT12N-708F",
    "https://kenzz.com/en/product/QJ7KDUJYVKXR/%D8%AA%D9%83%D9%8A%D9%8A%D9%81-%D9%87%D9%88%D8%A7%D8%A1-%D9%87%D8%A7%D9%8A%D8%B1-%D8%B3%D8%A8%D9%84%D9%8A%D8%AA-1.5-%D8%AD%D8%B5%D8%A7%D9%86-%D8%A8%D8%A7%D8%B1%D8%AF-%D8%B3%D8%A7%D8%AE%D9%86-%D8%A5%D9%86%D9%81%D8%B1%D8%AA%D8%B1-%D9%88%D8%A7%D9%8A-%D9%81%D8%A7%D9%8A-%D8%A7%D8%A8%D9%8A%D8%B6-HSU-12KHRIBC",
    "https://kenzz.com/en/product/2GBPPGPLMXK9/Hisense-Split-Air-Conditioner-2.25-Hp-Cold-And-Hot-Hi-E18Invhp",
    "https://kenzz.com/en/product/FNCYAMR8N3BS/Haier-Split-Air-Conditioner-3-HP%2C-Cooling-Only-White-HSU-24KCRIC",
    "https://kenzz.com/en/product/7SJ7S7DEDSPQ/LG-Art-Cool-Inverter-Split-Air-Conditioner-2.25-HP%2C-Cooling-%26-Heating-Gray-S4-W18KLRZA",
    "https://kenzz.com/en/product/PB7EMU9ZX59K/%D8%AA%D9%83%D9%8A%D9%8A%D9%81-%D8%B3%D8%A8%D9%84%D9%8A%D8%AA-%D9%87%D8%A7%D9%8A%D8%B1-1.5-%D8%AD%D8%B5%D8%A7%D9%86-%D8%A8%D8%A7%D8%B1%D8%AF-%D9%81%D9%82%D8%B7-%D8%A3%D8%A8%D9%8A%D8%B6-HSU-12KCRIC",
    "https://kenzz.com/en/product/7H9Z9QZPQ4SG/Sharp-Split-Air-Conditioner-3-HP%2C-Cooling-White-AH-A24ZSE",
    "https://kenzz.com/en/product/4XBS82NWELKA/Sharp-Inverter-Split-Air-Conditioner-2.25-HP%2C-Cooling-%26-Heating-White-AY-XP18YHE",
    "https://kenzz.com/en/product/44N3SYU6UF7Q/Haier-Split-Air-Conditioner-1.5-Hp-Cold-And-Hot-White-Hsu-12Khrocc",
    "https://kenzz.com/en/product/HE6676GTX9BK/LG-Split-Air-Conditioner-1.5-HP%2C-Cooling-Only-White-S4-Q12JA2MC",
    "https://kenzz.com/en/product/WM4BWCMETDWE/Sharp-Split-Air-Conditioner-2.25-HP%2C-Cooling-White-AH-A18ZSE",
    "https://kenzz.com/en/product/FWLPVEQMKZHN/Sharp-Split-Air-Conditioner-1.5-HP%2C-Cooling-White-AH-A12ZSE",
    "https://kenzz.com/en/product/ARZT2CUWDNGU/Fresh-Split-Air-Conditioner-1.5-HP%2C-Cooling-Only-White-SIFW13C-IP--SIFW13C-OX2",
    "https://kenzz.com/en/product/Y3TGAHZJ7433/LG-Split-Air-Conditioner-1.5-HP-Cooling-Only-White-S4-Q12JA3AE",
    "https://kenzz.com/en/product/3TZ96Y9FWZ6X/Fresh-Cooling-Split-Air-Conditioner-2.25-HP-White-FUFW18C-IW-AG-FUFW18C-O-X2",
    "https://kenzz.com/en/product/FNCYAMR8N3BS/%D8%AA%D9%83%D9%8A%D9%8A%D9%81-%D8%B3%D8%A8%D9%84%D9%8A%D8%AA-%D9%87%D8%A7%D9%8A%D8%B1-3-%D8%AD%D8%B5%D8%A7%D9%86-%D8%A8%D8%A7%D8%B1%D8%AF-%D9%81%D9%82%D8%B7-%D8%A3%D8%A8%D9%8A%D8%B6-HSU-24KCRIC",
    "https://kenzz.com/en/product/ZVKF6MWRQD76/Carrier-Xcool-Split-Air-Conditioner-Cooling-and-Heating-Inverter-Technology-1.5-HP-White-53QHEFT12DN8-708F",
    "https://kenzz.com/en/product/JF5G3ECXRGDT/Carrier-Split-Air-Conditioner-2.25-Hp%2C-Cooling-%26-Heating-Digital-White-53QHCT18N-708F",
    "https://kenzz.com/en/product/EHQYZK749Y6G/Carrier-Optimax-Pro-Air-Conditioner-Cooling-and-Heating-3-HP-53QHCT24N-708F",
    "https://kenzz.com/en/product/TP6GFPV39NS9/Haier-Split-Air-Conditioner-3-HP-Plasma-Cooling-Only-White-HSU-24KCROCC",
    "https://kenzz.com/en/product/2QX4UM8AZLHN/LG-Inverter-Split-Air-Conditioner-5-HP%2C-Cooling-%26-Heating-White-S4-W3R43EA",
    "https://kenzz.com/en/product/27AV9LTYPPR9/Sharp-Split-Air-Conditioner-1.5-HP%2C-Cooling-%26-Heating-White-AY-AP12ZHE",
    "https://kenzz.com/en/product/VUY7ZSL88LVV/Haier-Smart-Cool-Split-Air-Conditioner%2C-2.25-HP%2C-Cooling%2C-Plasma%2C-Digital-Display%2C-White-HSU-18KCROCC",
    "https://kenzz.com/en/product/MHZED8D2RXU9/Sharp-Inverter-Split-Air-Conditioner-2.25-HP%2C-Cooling-Plasma-Cluster-Silver-AY-XP18YHES",
    "https://kenzz.com/en/product/W7X5YRB5V2XG/Fresh-Professional-Turbo-Split-Air-Conditioner-Cool-Hot-3-HP-White-FUFW24H-IW-AG",
    "https://kenzz.com/en/product/2B6DUSYBVKSU/Fresh-Split-Air-Conditioner-1.5-HP%2C-Cooling-Only-White-FUFW12C-IW",
    "https://kenzz.com/en/product/W7HGC6MA4AK2/Carrier-Split-Air-Conditioner-4-Hp%2C-Cooling-%26-Heating-Digital-White-42Qhet30N-708F",
    "https://kenzz.com/en/product/34AE5QMYQQ3K/Carrier-Split-Optimax-Inverter-Air-Conditioner-2.25-Hp%2C-Cooling-%26-Heating-White-53Qhct18Dn-708F",
    "https://kenzz.com/en/product/28WJ5S9YZ4Z5/Midea-Mission-Pro-Air-Conditioner-1.5-HP-Cooling-Only-M1SCT-12CRN-Q8",
    "https://kenzz.com/en/product/P2XH3386GLJT/Media-Mission-Pro-Split-Air-Conditioner%2C-Cooling%2C-3-HP%2C-White-MSC1T-24CR-N",
    "https://kenzz.com/en/product/97P3PEYL3BQH/Beko-Split-Air-Conditioner-1.5-Hp-Inverter-Motor-Cold-Only-White-Bict1221X",

    # --- قسم الشاشات الصافية الحقيقية (60+ شاشة مظبوطة) ---
    "https://kenzz.com/en/product/2C4UKSKQVG2E/Fresh-32-inch-Frameless-HD-LED-Smart-TV-Black-32LH423CT",
    "https://kenzz.com/en/product/2WN6YM2Y8EM8/Haier-TV-50-inch-Smart-4K-UHD-LED-TV-with-Built-in-Receiver-H50K80EU",
    "https://kenzz.com/en/product/2X4HT6GS9YXF/Grohe-Smart-TV-50-inch-4K-Android-LED-Frameless-GLD50SAWORV2",
    "https://kenzz.com/en/product/3DSN4EHXZHRE/Hyundai-43-Inch-Smart-LED-TV-L43HYNDA630",
    "https://kenzz.com/en/product/5CRURB65XCHH/Jack-32-Inch-HD-LED-TV-Black-32JC3110B",
    "https://kenzz.com/en/product/6SW56BKLPDML/LG-65-inch-4K-UHD-LED-Smart-TV-with-Built-in-Receiver-65UA85006LA",
    "https://kenzz.com/en/product/72F23QNCFUM5/LG-Smart-TV-55-inches-Black-55UR78006LL",
    "https://kenzz.com/en/product/8DZQ2LQV2HJ8/Xenix-LED-Smart-TV-32-Inch-Bluetooth-Black-32E4M",
    "https://kenzz.com/en/product/8JJKJVX6SFFV/LG-LED-Smart-TV-55-Inch-4K-UHD-Black-55UQ75006LG",
    "https://kenzz.com/en/product/8KYCWYNKG8MC/Samsung-Smart-TV-98-inch-4K-Tizen-Crystal-UHD-DU9000",
    "https://kenzz.com/en/product/ANFQLUK3TDNJ/Mirage-50-Inch-4K-Smart-TV-Built-in-Receiver-50MRU720",
    "https://kenzz.com/en/product/B6C846V76LEZ/Toshiba-LED-Smart-TV-50-Inch-4K-Black-50U5965EA",
    "https://kenzz.com/en/product/BETHALZVGABD/Smart-Tv-Screen-32-Inches-Black-Le32Dn4",
    "https://kenzz.com/en/product/BFHZSWZJQR4M/LG-Smart-TV-55-Inch-Silver-55NANO776QA",
    "https://kenzz.com/en/product/BUF486L9C4FD/ATA-43-Inch-LED-FHD-TV-Black-ATA43FON",
    "https://kenzz.com/en/product/C5P69Y68X7HE/Haier-Smart-55-Inch-4K-UHD-LED-TV-Built-in-Receiver-H55K80EU",
    "https://kenzz.com/en/product/D8HANESRB8UU/Samsung-65-inch-Smart-4K-UHD-QLED-TV-with-Built-in-Receiver-65Q80CA",
    "https://kenzz.com/en/product/DHCQA9366DM8/LG-43LM6370PVA-43-inch-FHD-Smart-LED-TV-Black",
    "https://kenzz.com/en/product/EBTYCPV7QG2G/Toshiba-LED-Smart-TV-55-Inch-4K-Black-55U5965EA",
    "https://kenzz.com/en/product/EYLJ5T9ZWM2F/LG-TV-50-inch-4K-UHD-Smart-LED-TV-with-Built-in-Receiver-50UT801C0LB",
    "https://kenzz.com/en/product/F9LFL76RNHRL/H1-26-Inch-FHD-LED-TV-Black-HTV26",
    "https://kenzz.com/en/product/GBXB7D4DNLSV/Jack-32-Inch-HD-LED-TV-Hs-Black-32JB611",
    "https://kenzz.com/en/product/GMAAUUTEJCZF/Haier-65-Inch-4K-UHD-Smart-LED-TV-Black-H65K80EU",
    "https://kenzz.com/en/product/GN66P5TJH4W2/Grohe-Smart-TV-32-inch-HD-LED-Frameless-Built-in-Receiver-GLD32SDV2",
    "https://kenzz.com/en/product/GPUM6LCPBYRS/Castle-HD-TV-32-inch-Black-LED-AC2132",
    "https://kenzz.com/en/product/HGFEELAENCB8/Evolve-Smart-TV-43-inch-FHD-LED-Frameless-VLD43SAWOR",
    "https://kenzz.com/en/product/HR4HTPXQWPAW/Haier-Smart-32-Inch-LED-HD-TV-Black-H32K80E",
    "https://kenzz.com/en/product/J3FAVNKHSJ2G/Samsung-32-Inch-Smart-TV-Built-in-Receiver-UA32T5300",
    "https://kenzz.com/en/product/J7YUNXT4WEV2/Sharp-50-Inch-4K-Smart-TV-Frameless-Built-in-Receiver-4T-C50FL6EX",
    "https://kenzz.com/en/product/JCTNNKBRF6L4/Sharp-4K-Smart-Tv-Without-Frame-55-Inches-With-Built-In-Receiver-4T-C55Fl6Ex",
    "https://kenzz.com/en/product/JTEE6KJMH8YG/Evolve-Smart-TV-43-inch-FHD-Frameless-Built-in-Receiver-VLD43SD",
    "https://kenzz.com/en/product/K6CC5ED7GARN/Ata-43-Inch-Fhd-Led-Smart-Tv-Black-43fls",
    "https://kenzz.com/en/product/KGX5T5AKDDVB/Ata-32-Inch-Led-Hd-Tv-Black",
    "https://kenzz.com/en/product/KT4K86RF22VF/LG-Smart-TV-50-inches-LED-with-built-in-receiver-50UT80006LA",
    "https://kenzz.com/en/product/L3NNCWQLB3NT/Castle-Smart-TV-43-inch-Smart-LED-AC2543-S",
    "https://kenzz.com/en/product/LTK8C8ZVK4UP/Jack-Frameless-50-Inch-Led-Smart-Tv-4K-Uhd-50Jc7132F",
    "https://kenzz.com/en/product/MW6UDJUGKWSE/Mirage-32-Inch-HD-LED-TV-Black-32MRNF820",
    "https://kenzz.com/en/product/N4N8GZKTDNPB/Castle-HD-TV-43-inch-Black-AC2543",
    "https://kenzz.com/en/product/NPN84XL8VVWU/Samsung-50-Inch-QLED-Q60D-4K-Tizen-OS-Smart-TV-QA50Q60DAUXEG",
    "https://kenzz.com/en/product/NTAAUDGWVGN7/ATA-Smart-TV-55-Inch-4K-Black-ATA55U0S",
    "https://kenzz.com/en/product/NTV8SM8EKG5H/Mirage-43-Inch-Smart-TV-with-Built-in-Receiver-FHD-43MA6000",
    "https://kenzz.com/en/product/PEW6Y5KH9QPQ/Samsung-TV-75-inch-QLED-4K-UHD-Built-in-Receiver-75Q70DAUXEG",
    "https://kenzz.com/en/product/PFVA9YQ9DW3A/Tornado-4K-Smart-TV-50-Inch-Built-in-Receiver-50UA3400E",
    "https://kenzz.com/en/product/PKJU4ZKLKZNC/Jack-43-Inch-FHD-Smart-LED-TV-Black-NGLD-143ASS-143N-JB621",
    "https://kenzz.com/en/product/PY8W8BL5YWPT/Samsung-43-T5300-LED-FHD-Smart-TV-UA43T5300AUXEG",
    "https://kenzz.com/en/product/Q59EUEC8R36B/Evolve-Smart-TV-32-inch-HD-LED-Frameless-VLD32NA",
    "https://kenzz.com/en/product/QNDPDFBX4NYB/Hyundai-Smart-TV-65-Inch-LED-4K-UHD-Built-in-Receiver-L65HYNDA650",
    "https://kenzz.com/en/product/RKKERANW6R9D/ATA-Smart-TV-65-inch-4K-LED-ATA65UOS",
    "https://kenzz.com/en/product/SS479XYN72LZ/Tornado-Smart-TV-50-Inch-D-LED-4K-UHD-Built-in-Receiver-50US3500E",
    "https://kenzz.com/en/product/SVJDQJ82MMAD/Samsung-55-inch-Crystal-UHD-Smart-TV-with-Built-in-Receiver-UA55DU8000",
    "https://kenzz.com/en/product/TG75EV4F3CFP/Samsung-43-Inch-Full-HD-Smart-LED-TV-with-Built-in-Receiver-Black-UA43F6000FUXEG",
    "https://kenzz.com/en/product/THXQCGC9W775/LG-Smart-TV-43-inches-LED-with-built-in-receiver-43UT80006LA",
    "https://kenzz.com/en/product/TQTESFFKHHZ6/Nautical-43-Inch-LED-FHD-TV-Black-DLP43-AM4600N",
    "https://kenzz.com/en/product/V2FPJUKMWU8T/HD-Smart-Screen-32-inches-Silver-2T-C32FG6EX",
    "https://kenzz.com/en/product/VL7AA9WSGGRJ/Hyundai-Smart-LED-TV-55-inch-UHD-4K-webOS-L55HYNDA650",
    "https://kenzz.com/en/product/WBFTAWRSLNA3/Grohe-Smart-TV-32-inch-HD-LED-Frameless-GLD32NAV2",
    "https://kenzz.com/en/product/X7556K2CAKCQ/Sharp-55-inch-LED-4K-UHD-Smart-TV-with-Google-TV-Frameless-4T-C55FJ16EX",
    "https://kenzz.com/en/product/Y9EPFE24JT7F/Sharp-Smart-TV-75-Inch-4K-Built-in-Receiver-4T-C75FN6EX",
    "https://kenzz.com/en/product/YCFQYQ7J8G4V/4K-Smart-TV-55-inches-Silver-4T-C55DL6EX",
    "https://kenzz.com/en/product/Z9K4M3PK4CZB/Fresh-Smart-Tv-43-Inches-Fhd-Led-43Lf423Ce",
    "https://kenzz.com/product/D8HANESRB8UU/%D8%AA%D9%84%D9%81%D8%B2%D9%8A%D9%88%D9%86-%D8%B3%D8%A7%D9%85%D8%B3%D9%88%D9%86%D8%AC-65-%D8%A8%D9%88%D8%B5%D8%A9-%D8%A7%D9%84%D8%B0%D9%83%D9%8A-4K-UHD-QLED-%D9%85%D8%B9-%D8%B1%D8%B3%D9%8A%D9%81%D8%B1-%D8%AF%D8%A7%D8%AE%D9%84%D9%8A-65Q80CA",
    "https://kenzz.com/product/NPN84XL8VVWU/Q60D-%D8%AA%D9%84%D9%8A%D9%81%D8%B2%D9%8A%D9%88%D9%86-%D8%B3%D8%A7%D9%85%D8%B3%D9%88%D9%86%D8%AC-2024-QLED-Tizen-OS-%D8%B3%D9%85%D8%A7%D8%B1%D8%AA-55-%D8%A8%D9%88%D8%B5%D8%A9-QA50Q60DAUXEG",
    "https://kenzz.com/product/PEW6Y5KH9QPQ/%D8%AA%D9%84%D9%81%D8%B2%D9%8A%D9%88%D9%86-%D8%B3%D8%A7%D9%85%D8%B3%D9%88%D9%86%D8%AC-75-%D8%A8%D9%88%D8%B5%D8%A9-QLED-4K-UHD-%D8%B1%D9%8A%D8%B3%D9%85%D9%81%D8%B5-%D8%AF%D8%A7%D8%AE%D9%84%D9%8A-75Q70DAUXEG",
    "https://kenzz.com/product/VJAA64HRV7YW/%D8%AA%D9%84%D9%81%D8%B2%D9%8A%D9%88%D9%86-%D8%B3%D8%A7%D9%85%D8%B3%D9%88%D9%86%D8%AC-The-Frame-%D8%B3%D9%85%D8%A7%D8%B1%D8%AA-55-%D8%A8%D9%88%D8%B5%D8%A9-4K-LS03D-QLED"
]

H = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
}

AR = str.maketrans("٠١٢٣٤٥٦٧٨٩٫٬", "0123456789.,")

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_data(data):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"خطأ في حفظ الملف: {e}")

stored_data = load_data()

def send(msg):
    u = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(u, json={"chat_id": CHAT, "text": msg, "parse_mode": "Markdown"}, timeout=10)
    except Exception as e:
        print(f"خطأ في إرسال رسالة التليجرام: {e}")

def check_prices():
    global stored_data
    
    total_products_count = len(PRODUCTS)
    print(f"\n[🔄] بدء فحص عدد {total_products_count} منتج بصمت...")
    
    changes_count = 0
    checked_count = 0
    current_time_str = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    for index, url in enumerate(PRODUCTS, 1):
        try:
            response = requests.get(url, headers=H, timeout=15, allow_redirects=True)
            
            if response.status_code != 200:
                print(f"[{index}/{total_products_count}] فشل فحص المنتج (كود الاستجابة: {response.status_code})")
                continue
            
            soup = BeautifulSoup(response.text, 'html.parser')
            current_price = None
            product_name = None
            
            for script in soup.find_all('script', type='application/ld+json'):
                try:
                    data = json.loads(script.string)
                    data_items = data if isinstance(data, list) else [data]
                    
                    for item in data_items:
                        if isinstance(item, dict) and item.get('@type') == 'Product':
                            product_name = item.get('name')
                            offers = item.get('offers')
                            if isinstance(offers, dict):
                                p = offers.get('price') or offers.get('lowPrice')
                                if p:
                                    current_price = float(p)
                                    break
                            elif isinstance(offers, list) and len(offers) > 0:
                                p = offers[0].get('price')
                                if p:
                                    current_price = float(p)
                                    break
                    if current_price:
                        break
                except:
                    pass
            
            if not product_name:
                h1 = soup.find('h1')
                product_name = h1.get_text().strip() if h1 else "منتج بدون اسم"
            
            if not current_price:
                price_element = (
                    soup.find('span', {'class': 'price'}) or 
                    soup.find('div', {'class': 'price'}) or 
                    soup.find('span', {'class': 'current-price'}) or
                    soup.find('span', class_=lambda x: x and 'price' in x.lower())
                )
                if price_element:
                    price_text = price_element.get_text().strip().translate(AR)
                    price_str = ''.join(c for c in price_text if c.isdigit() or c == '.')
                    if price_str:
                        current_price = float(price_str)
            
            if current_price:
                checked_count += 1
                is_new_product = url not in stored_data
                
                if is_new_product:
                    stored_data[url] = {
                        "name": product_name,
                        "current_price": current_price,
                        "history": [{"price": current_price, "time": current_time_str}]
                    }
                else:
                    item_data = stored_data[url]
                    old_price = item_data["current_price"]
                    
                    # الفحص لا يتم إلا عند تغير السعر الفعلي
                    if current_price != old_price:
                        prices_list = [h["price"] for h in item_data["history"]]
                        prices_list.append(current_price)
                        avg_price = round(sum(prices_list) / len(prices_list), 2)
                        lowest_historical_price = min(prices_list[:-1]) if len(prices_list) > 1 else old_price
                        
                        # حساب دقيق للخصم أو الزيادة
                        if current_price < old_price:
                            diff_pct = round(((old_price - current_price) / old_price) * 100, 1)
                            discount_text = f"📉 نسبة الخصم: %{diff_pct}"
                        else:
                            diff_pct = round(((current_price - old_price) / old_price) * 100, 1)
                            discount_text = f"📈 نسبة الزيادة: %{diff_pct}"
                        
                        # تحديد أقل سعر تاريخي بحق
                        is_lowest = current_price <= lowest_historical_price
                        tagline = "🔥 أقل سعر تاريخي!" if is_lowest else "📊 تحديث جديد في السعر"
                        
                        item_data["current_price"] = current_price
                        item_data["name"] = product_name
                        item_data["history"].append({"price": current_price, "time": current_time_str})
                        
                        history_text = ""
                        for h in reversed(item_data["history"][-5:]):
                            history_text += f"➡️ EGP {h['price']} – {h['time']}\n"
                        
                        # رسالة تنبيه تغير السعر (مع رابط الشراء وتنسيق سليم)
                        msg = (
                            f"✨ عرض كنز ✨\n\n"
                            f"🛒 {product_name}\n\n"
                            f"💵 السعر الحالي: EGP {current_price}\n"
                            f"💵 السعر السابق: EGP {old_price}\n"
                            f"📊 متوسط الأسعار: EGP {avg_price}\n"
                            f"{discount_text}\n"
                            f"{tagline}\n\n"
                            f"📜 تاريخ الأسعار:\n"
                            f"{history_text}\n"
                            f"🛍️ **رابط المنتج:**\n{url}\n\n"
                            f"🔗 [اضغط هنا للشراء مباشرة]({url})"
                        )
                        send(msg)
                        changes_count += 1
                
                print(f"[{index}/{total_products_count}] ✅ تم الفحص - {product_name} | السعر: {current_price}")
            else:
                print(f"[{index}/{total_products_count}] ⚠️ لم يتم العثور على السعر.")
            
            time.sleep(1.5)
            
        except Exception as e:
            print(f"[{index}/{total_products_count}] ❌ خطأ: {e}")
            
    save_data(stored_data)
    print(f"\n[⏳] انتهت الدورة الحالية (تم فحص {checked_count} منتج، رصد {changes_count} تغيير).")

if __name__ == "__main__":
    print("البوت يعمل الآن في الخلفية لمراقبة الأسعار بصمت...")
    while True:
        check_prices()
        time.sleep(900)  # الفحص كل 15 دقيقة بدون إزعاج