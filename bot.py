import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
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
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        # A101 arama linki
        url = f"https://www.a101.com.tr/list/?search_text={arama_sorgusu}"
        driver.get(url)
        print(f"🔗 A101'de {arama_sorgusu} araniyor...")
        
        time.sleep(10) # Sayfa yüklensin

        # A101 ürün kartlarını yakala
        urunler = driver.find_elements(By.CSS_SELECTOR, "li article.product-card")
        print(f"🔎 Sonuç: {len(urunler)} ürün bulundu.")

        for urun in urunler[:8]:
            try:
                isim = urun.find_element(By.CSS_SELECTOR, "h3.name").text.strip()
                # Fiyatı çek ve temizle (Örn: "150,00 TL" -> 150.00)
                fiyat_text = urun.find_element(By.CSS_SELECTOR, "span.current").text
                fiyat_temiz = fiyat_text.replace("TL", "").replace(".", "").replace(",", ".").strip()
                
                link = urun.find_element(By.CSS_SELECTOR, "a").get_attribute("href")

                data = {
                    "isim": isim,
                    "fiyat": float(fiyat_temiz),
                    "market": "A101",
                    "link": link,
                    "indirim_orani": "%0"
                }

                supabase.table("urunler").insert(data).execute()
                print(f"🚀 A101 Verisi Kaydedildi: {isim}")

            except Exception as e:
                continue

    except Exception as e:
        print(f"❌ Hata: {e}")
    finally:
        driver.quit()

# Botu A101 için ateşle!
a101_tara_ve_kaydet("aycicek yagi")