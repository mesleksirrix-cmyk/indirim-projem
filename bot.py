import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from supabase import create_client, Client

# --- 1. Supabase Bağlantı Ayarları ---
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
    # Gerçek bir kullanıcı gibi görünmek için güncel bir kimlik
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        url = f"https://www.migros.com.tr/arama?q={arama_sorgusu}"
        driver.get(url)
        print(f"🔗 {arama_sorgusu} sayfası açıldı. Bot taktikleri uygulanıyor...")
        
        # 1. Sayfanın yüklenmesi için 15 saniye şart (GitHub yavaş kalabiliyor)
        time.sleep(15) 

        # 2. ENGEL AŞMA: Sayfayı aşağı kaydırarak ürünlerin yüklenmesini (Lazy Load) tetikle
        driver.execute_script("window.scrollTo(0, 600);")
        time.sleep(3)
        driver.execute_script("window.scrollTo(600, 1200);")
        time.sleep(2)

        # 3. Ürünleri Yakalama (Farklı etiketleri sırayla dene)
        urunler = []
        etiketler = ["fe-product-card", "mat-card.product-card", "sm-product-card", ".product-card"]
        
        for etiket in etiketler:
            found = driver.find_elements(By.CSS_SELECTOR, etiket) if "." in etiket else driver.find_elements(By.TAG_NAME, etiket)
            if found:
                urunler = found
                print(f"🎯 Ürünler '{etiket}' etiketiyle başarıyla yakalandı!")
                break

        print(f"🔎 Sonuç: {len(urunler)} ürün bulundu.")

        for urun in urunler[:8]: # Test için ilk 8 ürün yeterli
            try:
                # İsim ve Link çekme
                link_elementi = urun.find_element(By.CSS_SELECTOR, "a.mat-caption")
                isim = link_elementi.text.strip()
                link = link_elementi.get_attribute("href")
                
                # Fiyat çekme
                ana_fiyat = urun.find_element(By.CSS_SELECTOR, "span.amount").text.replace(".", "").replace(",", "")
                kurus = urun.find_element(By.CSS_SELECTOR, "span.decimal").text
                tam_fiyat = float(f"{ana_fiyat}.{kurus}")

                data = {
                    "isim": isim,
                    "fiyat": tam_fiyat,
                    "market": "Migros",
                    "link": link,
                    "indirim_orani": "%0"
                }

                # Supabase'e gönder
                supabase.table("urunler").insert(data).execute()
                print(f"🚀 Veritabanına uçtu: {isim} - {tam_fiyat} TL")

            except Exception as e:
                continue

    except Exception as e:
        print(f"❌ Ana Hata: {e}")
    finally:
        driver.quit()

# BOTU ÇALIŞTIR
# Önce tek bir ürünle test edelim, çalışırsa listeyi büyütürüz.
migros_tara_ve_kaydet("aycicek yagi")