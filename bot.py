import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from supabase import create_client, Client

# --- 1. Supabase Bağlantı Ayarları (Yedekli Sistem) ---
# GitHub Secrets'tan almaya çalışır, bulamazsa tırnak içindeki yedekleri kullanır.
SUPABASE_URL = os.environ.get("SUPABASE_URL") or "https://elfqezouruoeujneicbg.supabase.co"
# Buraya tırnak içine Service Role Key'ini veya anon key'ini yaz kanka (Garanti olsun)
SUPABASE_KEY = os.environ.get("SUPABASE_KEY") or "sb_publishable_gNKpUgSPhtGgPGcvQbuyzA_E0pfly6c"

print(f"DEBUG: URL Kontrol -> {SUPABASE_URL[:15]}...") # Loglarda URL'nin geldiğini görmek için

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    print(f"❌ Supabase bağlantı hatası: {e}")

def migros_tara_ve_kaydet(arama_sorgusu):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    # Migros'un bizi sevmesi için modern bir kimlik (User-Agent)
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        url = f"https://www.migros.com.tr/arama?q={arama_sorgusu}"
        driver.get(url)
        print(f"🔗 {arama_sorgusu} taranıyor...")
        
        # Sayfanın yüklenmesi için 15 saniye verelim (GitHub bazen yavaştır)
        time.sleep(15) 

        # --- ENGEL AŞMA: Lokasyon ve Çerezleri Temizle ---
        try:
            # Kapatma çarpısı (fa-icon close-icon) varsa bas
            kapatma_butonlari = driver.find_elements(By.CSS_SELECTOR, "fa-icon.close-icon, .close-button, #reject-all")
            for btn in kapatma_butonlari:
                if btn.is_displayed():
                    btn.click()
                    time.sleep(1)
        except:
            pass

        # Sayfayı aşağı kaydır (Ürünlerin yüklenmesini tetikler)
        driver.execute_script("window.scrollTo(0, 800);")
        time.sleep(2)

        # Ürün kartlarını yakala
        # Migros bazen 'fe-product-card' bazen 'mat-card' kullanır.
        urunler = driver.find_elements(By.TAG_NAME, "fe-product-card")
        if not urunler:
            urunler = driver.find_elements(By.CSS_SELECTOR, "mat-card.product-card")

        print(f"🔎 {len(urunler)} adet ürün yakalandı.")

        for urun in urunler[:8]: # İlk 8 ürünü alalım
            try:
                # İsim
                isim_elementi = urun.find_element(By.CSS_SELECTOR, "a.mat-caption")
                isim = isim_elementi.text.strip()
                link = isim_elementi.get_attribute("href")
                
                # Fiyat
                ana_fiyat = urun.find_element(By.CSS_SELECTOR, "span.amount").text.replace(".", "").replace(",", "")
                kurus = urun.find_element(By.CSS_SELECTOR, "span.decimal").text
                tam_fiyat = float(f"{ana_fiyat}.{kurus}")

                # Veriyi Hazırla
                data = {
                    "isim": isim,
                    "fiyat": tam_fiyat,
                    "link": link,
                    "market": "Migros",
                    "indirim_orani": "%0"
                }

                # Supabase'e fırlat
                supabase.table("urunler").insert(data).execute()
                print(f"✅ Kaydedildi: {isim} - {tam_fiyat} TL")

            except Exception as e:
                continue

    except Exception as e:
        print(f"❌ Ana hata: {e}")
    finally:
        driver.quit()

# BOTU ÇALIŞTIR
hedefler = ["aycicek yagi", "cay"] # Şimdilik 2 ürünle test edelim hızlı olsun

for hedef in hedefler:
    migros_tara_ve_kaydet(hedef)
    time.sleep(5)
