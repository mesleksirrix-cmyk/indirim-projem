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

# 1. Supabase Bağlantı Ayarları
SUPABASE_URL = os.environ.get("SUPABASE_URL") or "https://elfqezouruoeujneicbg.supabase.co"
SUPABASE_KEY = os.environ.get("SUPABASE_KEY") or "sb_publishable_gNKpUgSPhtGgPGcvQbuyzA_E0pfly6c"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def migros_tara_ve_kaydet(arama_sorgusu):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        url = f"https://www.migros.com.tr/arama?q={arama_sorgusu}"
        driver.get(url)
        print(f"🔗 {arama_sorgusu} için Migros taranıyor...")
        
        # Sayfanın yüklenmesi için biraz süre tanıyalım
        time.sleep(12) 

        # --- ENGEL AŞMA: Eğer bölge seçme penceresi gelirse kapatmaya çalış ---
        try:
            # Çerezleri kabul et veya pencereyi kapat (Varsa)
            pencere_kapat = driver.find_elements(By.CSS_SELECTOR, "fa-icon.close-icon")
            if pencere_kapat:
                pencere_kapat[0].click()
                time.sleep(2)
        except:
            pass

        # Ürünleri bulmak için 2 farklı yöntem deneyelim
        urunler = driver.find_elements(By.TAG_NAME, "fe-product-card")
        if not urunler:
            urunler = driver.find_elements(By.CSS_SELECTOR, ".product-card")

        print(f"🔎 {len(urunler)} adet ürün bulundu.")

        for urun in urunler[:10]:
            try:
                # Migros'un güncel yapısında metinleri çekelim
                isim = urun.find_element(By.CSS_SELECTOR, "a.mat-caption").text.strip()
                
                # Fiyat çekme (Migros'ta ana fiyat ve kuruş ayrıdır)
                ana_fiyat = urun.find_element(By.CSS_SELECTOR, "span.amount").text.replace(".", "").replace(",", "")
                kurus = urun.find_element(By.CSS_SELECTOR, "span.decimal").text
                tam_fiyat_str = f"{ana_fiyat}.{kurus}"
                
                urun_linki = urun.find_element(By.CSS_SELECTOR, "a.mat-caption").get_attribute("href")

                # Veriyi Hazırla
                data = {
                    "isim": isim,
                    "fiyat": float(tam_fiyat_str),
                    "link": urun_linki,
                    "market": "Migros",
                    "indirim_orani": "%0"
                }

                # 2. Supabase'e Kaydet
                supabase.table("urunler").insert(data).execute()
                print(f"✅ Kaydedildi: {isim} - {tam_fiyat_str} TL")

            except Exception as e:
                # print(f"Ürün hatası: {e}") # Debug için açılabilir
                continue

    except Exception as e:
        print(f"❌ Ana hata: {e}")
    finally:
        driver.quit()

# BOTU ÇALIŞTIR
hedefler = ["aycicek yagi", "toz seker", "cay"]

for hedef in hedefler:
    migros_tara_ve_kaydet(hedef)
    time.sleep(5)