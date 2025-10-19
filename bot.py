import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import asyncio
import aiohttp
import os
from threading import Thread

# Use environment variable for security
BOT_TOKEN = os.getenv('BOT_TOKEN', '8172438543:AAG3VNfOrwxPJoQQ6ZGSsXbzOLFenA-r1vk')
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def get_player_name_fast(player_id):
    """Your working function here"""
    options = uc.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-images')
    options.add_argument('--blink-settings=imagesEnabled=false')
    options.add_argument('--window-size=1920,1080')
    
    driver = uc.Chrome(options=options)
    try:
        print(f"⚡ Searching for: {player_id}")
        driver.get("https://www.midasbuy.com/midasbuy/us/buy/pubgm")
        time.sleep(2)
        
        # Close popup
        try:
            driver.execute_script("document.querySelector('div.PatFacePopWrapper_close-btn__erWAb')?.click();")
            time.sleep(1)
        except:
            pass
        
        # Open search
        try:
            enter_btn = driver.find_element(By.CSS_SELECTOR, "div.UserTabBox_login_text__8GpBN")
            driver.execute_script("arguments[0].click();", enter_btn)
            time.sleep(1)
        except:
            driver.quit()
            return "Error: Could not open search popup"
        
        # Enter ID
        try:
            input_field = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Enter Player ID']"))
            )
            input_field.clear()
            input_field.send_keys(player_id)
            input_field.send_keys(Keys.ENTER)
            time.sleep(2.5)
        except:
            driver.quit()
            return "Error: Could not enter ID"
        
        # Get name
        try:
            name_element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "span.UserTabBox_name__4ogGM"))
            )
            player_name = name_element.text.strip()
            driver.quit()
            return player_name
        except:
            driver.quit()
            return "Name not found"
        
    except Exception as e:
        try:
            driver.quit()
        except:
            pass
        return f"Error: {str(e)}"

async def send_message(chat_id, text):
    async with aiohttp.ClientSession() as session:
        payload = {'chat_id': chat_id, 'text': text}
        async with session.post(f"{API_URL}/sendMessage", json=payload) as response:
            return await response.json()

async def handle_updates():
    last_update_id = 0
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                params = {'offset': last_update_id + 1, 'timeout': 10}
                async with session.get(f"{API_URL}/getUpdates", params=params) as response:
                    updates = await response.json()
                
                if updates.get('ok'):
                    for update in updates['result']:
                        last_update_id = update['update_id']
                        if 'message' in update:
                            message = update['message']
                            chat_id = message['chat']['id']
                            text = message.get('text', '').strip()
                            
                            if text == '/start':
                                await send_message(chat_id, "🤖 PUBG Name Bot - Send Player ID")
                            elif text.isdigit():
                                await send_message(chat_id, "🔍 Searching...")
                                loop = asyncio.get_event_loop()
                                player_name = await loop.run_in_executor(None, get_player_name_fast, text)
                                await send_message(chat_id, f"🎮 {player_name}")
                            else:
                                await send_message(chat_id, "❌ Send only numbers")
            
            except Exception as e:
                print(f"Update error: {e}")
                await asyncio.sleep(2)

# Keep alive for hosting
def keep_alive():
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/')
    def home():
        return "Bot is running!"
    
    Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()

async def main():
    print("🚀 Bot Started on Railway!")
    await handle_updates()

if __name__ == '__main__':
    keep_alive()
    asyncio.run(main())