import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from supabase import create_client, Client

# --- Supabase Bağlantısı ---
SUPABASE_URL = "https://elfqezouruoeujneicbg.supabase.co" 
SUPABASE_KEY = "sb_publishable_gNKpUgSPhtGgPGcvQbuyzA_E0pfly6c" 
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def a101_tara_ve_kaydet(arama_sorgusu):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # Gerçek insan taklidi için en üst seviye ayarlar
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    # Bot olduğumuzu saklayan sihirli komut
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })

    try:
        url = f"https://www.a101.com.tr/list/?search_text={arama_sorgusu}"
        driver.get(url)
        print(f"🔗 A101'e girildi, {arama_sorgusu} bekleniyor...")

        # Ürünlerin yüklenmesi için 20 saniye boyunca her 2 saniyede bir kontrol et
        found_products = []
        for i in range(10):
            time.sleep(2)
            driver.execute_script("window.scrollTo(0, 500);")
            found_products = driver.find_elements(By.CSS_SELECTOR, "article.product-card")
            if found_products:
                print(f"🎯 {i*2}. saniyede ürünler yakalandı!")
                break
        
        print(f"🔎 Toplam bulunan: {len(found_products)}")

        for urun in found_products[:5]:
            try:
                isim = urun.find_element(By.CSS_SELECTOR, "h3.name").text.strip()
                fiyat_text = urun.find_element(By.CSS_SELECTOR, "span.current").text
                # Fiyat temizleme
                fiyat_temiz = fiyat_text.replace("TL", "").replace(".", "").replace(",", ".").strip()
                link = urun.find_element(By.TAG_NAME, "a").get_attribute("href")

                data = {
                    "isim": isim,
                    "fiyat": float(fiyat_temiz),
                    "market": "A101",
                    "link": link,
                    "indirim_orani": "%0"
                }

                supabase.table("urunler").insert(data).execute()
                print(f"🚀 Başarılı: {isim}")

            except:
                continue

    except Exception as e:
        print(f"❌ Hata: {e}")
    finally:
        driver.quit()

a101_tara_ve_kaydet("aycicek yagi")