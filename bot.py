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

def amazon_test_tara(arama_sorgusu):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        # Amazon Türkiye Testi
        url = f"https://www.amazon.com.tr/s?k={arama_sorgusu}"
        driver.get(url)
        print(f"🔗 Amazon'da {arama_sorgusu} araniyor...")
        
        time.sleep(10) # Sayfa yüklensin

        # Amazon ürün kartlarını bul
        urunler = driver.find_elements(By.CSS_SELECTOR, "div[data-component-type='s-search-result']")
        print(f"🔎 Sonuç: {len(urunler)} ürün bulundu.")

        for urun in urunler[:5]:
            try:
                isim = urun.find_element(By.CSS_SELECTOR, "h2 a span").text.strip()
                fiyat_ana = urun.find_element(By.CSS_SELECTOR, "span.a-price-whole").text.replace(",", "").replace(".", "")
                fiyat_kurus = "00"
                try:
                    fiyat_kurus = urun.find_element(By.CSS_SELECTOR, "span.a-price-fraction").text
                except:
                    pass
                
                fiyat_final = float(f"{fiyat_ana}.{fiyat_kurus}")
                link = urun.find_element(By.CSS_SELECTOR, "h2 a").get_attribute("href")

                data = {
                    "isim": isim,
                    "fiyat": fiyat_final,
                    "market": "Amazon",
                    "link": link,
                    "indirim_orani": "%0"
                }

                supabase.table("urunler").insert(data).execute()
                print(f"🚀 Amazon Verisi Kaydedildi: {isim} - {fiyat_final} TL")

            except Exception as e:
                continue

    except Exception as e:
        print(f"❌ Hata: {e}")
    finally:
        driver.quit()

# Botu Amazon için test edelim
amazon_test_tara("pirinc")