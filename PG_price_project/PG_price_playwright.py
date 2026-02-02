import datetime
import os
from playwright.sync_api import sync_playwright

def scrape_public_gold():
    target_url = "https://publicgold.me/ainadnan?gad_source=1&gad_campaignid=17061611250&gbraid=0AAAAAok_0voTZIF7xN_ROLrbVYphW5x0R&gclid=Cj0KCQiA6Y7KBhCkARIsAOxhqtNx2jjWjIltKkqYCYWniQovJ75HYIVXpRk3H0PXcv7aUtj1eIOPWiwaAsskEALw_wcB" # Your full URL
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        try:
            page.goto(target_url, wait_until="domcontentloaded", timeout=60000)
            selector = 'h4:has(sup):has(span)'
            page.wait_for_selector(selector, timeout=15000)

            price_element = page.locator(selector).first
            clean_price = price_element.inner_text().replace("RM", "").replace("/ gram", "").strip()
            
            # Use Malaysia time (UTC+8) or standard UTC
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            file_exists = os.path.isfile('gold_prices.csv')
            with open('gold_prices.csv', 'a') as f:
                if not file_exists:
                    f.write("timestamp,price_rm\n")
                f.write(f"{timestamp},{clean_price}\n")
                
            print(f"Success: {timestamp} -> RM {clean_price}")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    scrape_public_gold()