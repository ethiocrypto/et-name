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

print("🚀 Starting FAST PUBG Name Bot...")

# Use environment variable for security
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN environment variable is missing!")

API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def setup_driver():
    """Optimized Chrome driver for cloud speed"""
    chrome_options = Options()
    
    # Performance-optimized options
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-images')
    chrome_options.add_argument('--blink-settings=imagesEnabled=false')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--disable-plugins')
    chrome_options.add_argument('--disable-background-timer-throttling')
    chrome_options.add_argument('--disable-backgrounding-occluded-windows')
    chrome_options.add_argument('--disable-renderer-backgrounding')
    
    # Use system Chrome
    chrome_options.binary_location = '/usr/bin/google-chrome'
    
    # Set ChromeDriver path
    service = Service(executable_path='/usr/bin/chromedriver')
    
    return webdriver.Chrome(service=service, options=chrome_options)

def get_player_name(player_id):
    """OPTIMIZED for cloud speed - FAST VERSION"""
    driver = setup_driver()
    try:
        print(f"🔍 FAST Searching for: {player_id}")
        
        # Set shorter timeouts
        driver.set_page_load_timeout(10)
        driver.implicitly_wait(5)
        
        # Load page with minimal waiting
        driver.get("https://www.midasbuy.com/midasbuy/us/buy/pubgm")
        time.sleep(1)  # Reduced from 3 seconds
        
        # Ultra-fast popup close (single attempt)
        driver.execute_script("""
        setTimeout(function() {
            var closeBtn = document.querySelector('div.PatFacePopWrapper_close-btn__erWAb');
            if (closeBtn) { 
                closeBtn.click(); 
                console.log('Popup closed');
            }
        }, 500);
        """)
        time.sleep(0.5)  # Reduced wait
        
        # Fast search open
        driver.execute_script("""
        var searchBtn = document.querySelector('div.UserTabBox_login_text__8GpBN');
        if (searchBtn) { 
            searchBtn.click(); 
            console.log('Search opened');
        }
        """)
        time.sleep(1)  # Reduced from 2 seconds
        
        # Fast input and submit
        input_field = driver.find_element(By.CSS_SELECTOR, "input[placeholder='Enter Player ID']")
        input_field.clear()
        input_field.send_keys(player_id)
        
        # Submit instantly with JavaScript (faster than ENTER key)
        driver.execute_script("""
        var input = document.querySelector('input[placeholder="Enter Player ID"]');
        var form = input.closest('form');
        if (form) {
            form.submit();
        } else {
            // Find and click OK button
            var okBtn = document.querySelector('div.Button_text__WeIeb');
            if (okBtn) okBtn.click();
        }
        """)
        
        time.sleep(2)  # Reduced from 3 seconds
        
        # Fast name extraction with multiple attempts
        name = None
        for attempt in range(3):  # Try 3 times quickly
            try:
                name_element = driver.find_element(By.CSS_SELECTOR, "span.UserTabBox_name__4ogGM")
                name = name_element.text.strip()
                if name:
                    print(f"✅ FAST Found: {name}")
                    return name
            except:
                time.sleep(0.5)  # Very short wait between attempts
        
        # Fallback: try title attribute
        try:
            container = driver.find_element(By.CSS_SELECTOR, "div.UserTabBox_user_head_text__M0ViN")
            title_text = container.get_attribute("title")
            if title_text:
                name = title_text.split('(')[0].strip()
                print(f"✅ FAST Found via title: {name}")
                return name
        except:
            pass
            
        return "Name not found"
        
    except Exception as e:
        print(f"❌ Fast search error: {e}")
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
                                await send_message(chat_id, "🤖 FAST PUBG Name Bot\n\nSend me a Player ID to get the name instantly!")
                            elif text.isdigit():
                                search_msg = await send_message(chat_id, "⚡ FAST Searching...")
                                loop = asyncio.get_event_loop()
                                player_name = await loop.run_in_executor(None, get_player_name, text)
                                await send_message(chat_id, f"🎮 ID: {text}\nName: {player_name}")
                            else:
                                await send_message(chat_id, "❌ Please send only numbers (Player ID)")
            
            except Exception as e:
                print(f"Update error: {e}")
                await asyncio.sleep(5)

async def main():
    print("✅ FAST Bot is starting...")
    await handle_updates()

if __name__ == '__main__':
    print("🚀 Starting FAST bot application...")
    asyncio.run(main())
