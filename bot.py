import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from supabase import create_client, Client

# --- 1. Supabase Bağlantı Ayarları (SABİTLEDİK) ---
# Secrets çalışmadığı için direkt buraya yazıyoruz kanka
SUPABASE_URL = "https://elfqezouruoeujneicbg.supabase.co" 
SUPABASE_KEY = "sb_publishable_gNKpUgSPhtGgPGcvQbuyzA_E0pfly6c" 

print(f"DEBUG: Bot basliyor... Hedef: {SUPABASE_URL}")

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Supabase bağlantısı kuruldu.")
except Exception as e:
    print(f"❌ Supabase bağlantı hatası: {e}")

def migros_tara_ve_kaydet(arama_sorgusu):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        url = f"https://www.migros.com.tr/arama?q={arama_sorgusu}"
        driver.get(url)
        print(f"🔗 {arama_sorgusu} için sayfa açıldı, bekleniyor...")
        
        # GitHub sunucuları yavaş olduğu için 15 saniye şart
        time.sleep(15) 

        # Ürünleri yakalamaya çalış
        urunler = driver.find_elements(By.TAG_NAME, "fe-product-card")
        if not urunler:
            urunler = driver.find_elements(By.CSS_SELECTOR, "mat-card.product-card")

        print(f"🔎 Sonuç: {len(urunler)} ürün bulundu.")

        for urun in urunler[:5]: # Test için ilk 5 ürün yeterli
            try:
                isim = urun.find_element(By.CSS_SELECTOR, "a.mat-caption").text.strip()
                
                # Fiyat çekme
                ana_fiyat = urun.find_element(By.CSS_SELECTOR, "span.amount").text.replace(".", "").replace(",", "")
                kurus = urun.find_element(By.CSS_SELECTOR, "span.decimal").text
                tam_fiyat = float(f"{ana_fiyat}.{kurus}")

                data = {
                    "isim": isim,
                    "fiyat": tam_fiyat,
                    "market": "Migros",
                    "link": urun.find_element(By.CSS_SELECTOR, "a.mat-caption").get_attribute("href")
                }

                supabase.table("urunler").insert(data).execute()
                print(f"🚀 Veritabanına uçtu: {isim}")

            except Exception as e:
                continue

    except Exception as e:
        print(f"❌ Hata: {e}")
    finally:
        driver.quit()

# BOTU ÇALIŞTIR
migros_tara_ve_kaydet("aycicek yagi")