import datetime
import os
import csv
from playwright.sync_api import sync_playwright

def scrape_public_gold():
    # 1. Setup Paths
    # This ensures the CSV is saved in the same folder as the script
    base_path = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_path, 'gold_prices.csv')
    
    target_url = "https://publicgold.me/ainadnan?gad_source=1&gad_campaignid=17061611250&gbraid=0AAAAAok_0voTZIF7xN_ROLrbVYphW5x0R&gclid=Cj0KCQiA6Y7KBhCkARIsAOxhqtNx2jjWjIltKkqYCYWniQovJ75HYIVXpRk3H0PXcv7aUtj1eIOPWiwaAsskEALw_wcB"
    
    with sync_playwright() as p:
        # Launch browser in headless mode (essential for GitHub Actions)
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        try:
            print(f"Navigating to {target_url}...")
            # wait_until="networkidle" is safer for sites with dynamic price updates
            page.goto(target_url, wait_until="networkidle", timeout=60000)
            
            # Selector for the price element
            selector = 'h4:has(sup):has(span)'
            page.wait_for_selector(selector, timeout=20000)

            price_element = page.locator(selector).first
            raw_text = price_element.inner_text()
            
            # Clean the price string
            clean_price = raw_text.replace("RM", "").replace("/ gram", "").replace(",", "").strip()
            
            # 2. Handle Malaysia Timezone (UTC+8)
            # GitHub Actions uses UTC; this adds 8 hours to match Malaysia
            now_utc = datetime.datetime.now(datetime.timezone.utc)
            now_myt = now_utc + datetime.timedelta(hours=8)
            timestamp = now_myt.strftime("%Y-%m-%d %H:%M:%S")
            
            # 3. Save to CSV
            file_exists = os.path.isfile(csv_path)
            with open(csv_path, 'a', newline='') as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(["timestamp", "price_rm"])
                writer.writerow([timestamp, clean_price])
                
            print(f"✅ Success: {timestamp} -> RM {clean_price}")

        except Exception as e:
            print(f"❌ Error occurred: {e}")
            # Optional: Take a screenshot on failure to debug in GitHub Artifacts
            page.screenshot(path=os.path.join(base_path, "error_screenshot.png"))
        finally:
            browser.close()

if __name__ == "__main__":
    scrape_public_gold()