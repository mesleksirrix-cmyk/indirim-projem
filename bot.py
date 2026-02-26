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

def mega_test_tara():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new") # Daha yeni ve gizli headless modu
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # Bot olduğumuzu saklayan en kritik ayarlar
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    # WebDriver izini sil
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })

    try:
        # Bu sefer direk ana sayfaya gidelim, arama yapmadan önce sitenin bizi kabul edip etmediğini görelim
        url = "https://www.google.com/search?q=aycicek+yagi+fiyatlari"
        driver.get(url)
        print(f"🔗 Sayfa Basligi: {driver.title}") # Eğer 'Access Denied' veya 'Robot' yazarsa anlarız.
        
        time.sleep(10)

        # Google sonuçlarında fiyat içeren kısımları çekmeye çalışalım (Test amaçlı)
        sonuclar = driver.find_elements(By.CSS_SELECTOR, "div.g")
        print(f"🔎 Google'da {len(sonuclar)} sonuc yakalandi.")

        if len(sonuclar) > 0:
            # Eğer Google'dan sonuç gelirse, sistemin çalışıyor demektir.
            data = {
                "isim": "Sistem Calisiyor Testi",
                "fiyat": 1.0,
                "market": "SistemTest",
                "link": "https://google.com"
            }
            supabase.table("urunler").insert(data).execute()
            print("🚀 Test verisi Supabase'e gönderildi!")

    except Exception as e:
        print(f"❌ Hata: {e}")
    finally:
        driver.quit()

mega_test_tara()