import os
import asyncio
import aiohttp
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time

print("🚀 Starting PUBG Name Bot...")

# Use environment variable for security
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN environment variable is missing!")

API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def setup_driver():
    """Setup Chrome driver for Railway"""
    chrome_options = Options()
    
    # Railway-specific options
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-images')
    chrome_options.add_argument('--blink-settings=imagesEnabled=false')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--remote-debugging-port=9222')
    
    # Use system Chrome
    chrome_options.binary_location = '/usr/bin/google-chrome'
    
    # Set ChromeDriver path for Railway
    service = Service(executable_path='/usr/bin/chromedriver')
    
    return webdriver.Chrome(service=service, options=chrome_options)

def get_player_name(player_id):
    """Get player name from Midasbuy website"""
    driver = setup_driver()
    try:
        print(f"🔍 Searching for: {player_id}")
        driver.get("https://www.midasbuy.com/midasbuy/us/buy/pubgm")
        time.sleep(3)
        
        # Close popup
        try:
            driver.execute_script("document.querySelector('div.PatFacePopWrapper_close-btn__erWAb')?.click();")
            time.sleep(1)
            print("✅ Closed popup")
        except:
            print("ℹ️ No popup found")
        
        # Open search
        try:
            enter_btn = driver.find_element(By.CSS_SELECTOR, "div.UserTabBox_login_text__8GpBN")
            driver.execute_script("arguments[0].click();", enter_btn)
            time.sleep(2)
            print("✅ Opened search popup")
        except Exception as e:
            driver.quit()
            return f"Error: Could not open search - {e}"
        
        # Enter ID
        try:
            input_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Enter Player ID']"))
            )
            input_field.clear()
            input_field.send_keys(player_id)
            input_field.send_keys(Keys.ENTER)
            time.sleep(3)
            print("✅ Submitted ID")
        except Exception as e:
            driver.quit()
            return f"Error: Could not enter ID - {e}"
        
        # Get name
        try:
            name_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "span.UserTabBox_name__4ogGM"))
            )
            player_name = name_element.text.strip()
            print(f"✅ Found name: {player_name}")
            return player_name
        except Exception as e:
            print(f"❌ Name not found: {e}")
            return "Name not found"
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return f"Error: {str(e)}"
    finally:
        try:
            driver.quit()
        except:
            pass

async def send_message(chat_id, text):
    """Send message to Telegram"""
    async with aiohttp.ClientSession() as session:
        payload = {'chat_id': chat_id, 'text': text}
        async with session.post(f"{API_URL}/sendMessage", json=payload) as response:
            return await response.json()

async def handle_updates():
    """Handle Telegram updates"""
    last_update_id = 0
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                params = {'offset': last_update_id + 1, 'timeout': 30}
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
                                await send_message(chat_id, "🤖 PUBG Name Bot\n\nSend me a Player ID to get the name!")
                            elif text.isdigit():
                                search_msg = await send_message(chat_id, "🔍 Searching...")
                                loop = asyncio.get_event_loop()
                                player_name = await loop.run_in_executor(None, get_player_name, text)
                                await send_message(chat_id, f"🎮 ID: {text}\nName: {player_name}")
                            else:
                                await send_message(chat_id, "❌ Please send only numbers (Player ID)")
            
            except Exception as e:
                print(f"Update error: {e}")
                await asyncio.sleep(5)

async def main():
    print("✅ Bot is starting...")
    await handle_updates()

if __name__ == '__main__':
    print("🚀 Starting bot application...")
    asyncio.run(main())
