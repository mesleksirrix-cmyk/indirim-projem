import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from supabase import create_client, Client

# 1. Supabase Bağlantı Ayarları (GitHub Secrets'tan alır, yoksa senin verdiğin değerleri kullanır)
SUPABASE_URL = os.environ.get("SUPABASE_URL") or "https://elfqezouruoeujneicbg.supabase.co"
SUPABASE_KEY = os.environ.get("SUPABASE_KEY") or "sb_publishable_gNKpUgSPhtGgPGcvQbuyzA_E0pfly6c"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def migros_tara_ve_kaydet(arama_sorgusu):
    # --- Tarayıcı Ayarları (Bulut uyumlu) ---
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Arka planda çalışır
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    # Gerçek kullanıcı gibi görünmek için User-Agent
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        url = f"https://www.migros.com.tr/arama?q={arama_sorgusu}"
        driver.get(url)
        print(f"🔗 {url} taranıyor...")
        
        # Sayfanın ve JavaScript'in yüklenmesi için bekle
        time.sleep(10) 

        # Migros ürün kartlarını bul (Güncel etiket: fe-product-card)
        urunler = driver.find_elements(By.TAG_NAME, "fe-product-card")
        
        print(f"🔎 {len(urunler)} adet ürün bulundu. Veritabanına aktarılıyor...")

        for urun in urunler[:10]:  # Şimdilik her aramadan en ucuz ilk 10 ürünü alalım
            try:
                # Migros içindeki etiketleri yakala
                isim = urun.find_element(By.CSS_SELECTOR, "a.mat-caption").text.strip()
                ana_fiyat = urun.find_element(By.CSS_SELECTOR, "span.amount").text.strip()
                kurus = urun.find_element(By.CSS_SELECTOR, "span.decimal").text.strip()
                tam_fiyat = f"{ana_fiyat}.{kurus}"
                
                urun_linki = urun.find_element(By.CSS_SELECTOR, "a.mat-caption").get_attribute("href")

                # Veriyi Hazırla
                data = {
                    "isim": isim,
                    "fiyat": float(tam_fiyat.replace(",", ".")), # Sayısal format
                    "link": urun_linki,
                    "market": "Migros",
                    "indirim_orani": "%0" # Migros'ta indirim etiketi varsa burası geliştirilebilir
                }

                # 2. Supabase'e Kaydet
                supabase.table("urunler").insert(data).execute()
                print(f"✅ Kaydedildi: {isim} - {tam_fiyat} TL")

            except Exception as e:
                continue # Bir üründe hata olursa diğerine geç

    except Exception as e:
        print(f"❌ Ana hata: {e}")
    finally:
        driver.quit()

# BOTU ÇALIŞTIR
# İstediğin ürünleri buraya ekle kanka
hedefler = ["aycicek yagi", "toz seker", "cay"]

for hedef in hedefler:
    migros_tara_ve_kaydet(hedef)
    time.sleep(5) # Marketler banlamasın diye aralarda nefes alalım