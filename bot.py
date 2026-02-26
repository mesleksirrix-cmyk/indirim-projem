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

def sistem_testi():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        # Wikipedia asla bloklamaz!
        url = "https://tr.wikipedia.org/wiki/Ay%C3%A7i%C3%A7ek_ya%C4%9F%C4%B1"
        driver.get(url)
        print(f"🔗 Baglanilan Site: {driver.title}")
        
        # Sayfadaki ilk başlığı alalım
        baslik = driver.find_element(By.ID, "firstHeading").text
        print(f"🔎 Wikipedia'dan çekilen veri: {baslik}")

        if baslik:
            data = {
                "isim": "SİSTEM ÇALIŞIYOR: " + baslik,
                "fiyat": 999.0,
                "market": "WikipediaTest",
                "link": url
            }
            supabase.table("urunler").insert(data).execute()
            print("🚀 ZAFER! Veri Supabase'e başarıyla gönderildi.")

    except Exception as e:
        print(f"❌ Hata: {e}")
    finally:
        driver.quit()

sistem_testi()