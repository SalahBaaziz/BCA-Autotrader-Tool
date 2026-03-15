# Wait for page to load initially
        print("Waiting for page to load...")
        time.sleep(2)
        
        # Click the close button (X) if it appears
        print("Looking for close button...")
        try:
            close_button = driver.find_element(By.CSS_SELECTOR, "i.fa.fa-times.cursor-pointer")
            close_button.click()
            print("✓ Closed popup/modal")
            time.sleep(0.5)
        except NoSuchElementException:
            print("No close button found (might not be visible)")
        except Exception as e:
            print(f"Could not click close button: {e}")
        
        # Wait for dynamic content to load
        print("Waiting for content to load...")
        time.sleep(1)from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time

def setup_driver(headless=False):
    """Set up Chrome driver with options"""
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")
    
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def scrape_trackr_links(url):
    """
    Scrape all links with class 'text-trackr-link-blue hover:underline' from the page
    """
    driver = None
    links_data = []
    
    try:
        print("Setting up Chrome driver...")
        driver = setup_driver(headless=False)  # Set to True for headless mode
        
        print(f"Navigating to: {url}")
        driver.get(url)
        
        # Wait for page to load initially
        print("Waiting for page to load...")
        time.sleep(3)
        
        # Click the close button (X) if it appears
        print("Looking for close button...")
        try:
            close_button = driver.find_element(By.CSS_SELECTOR, "i.fa.fa-times.cursor-pointer")
            close_button.click()
            print("✓ Closed popup/modal")
            time.sleep(1)
        except NoSuchElementException:
            print("No close button found (might not be visible)")
        except Exception as e:
            print(f"Could not click close button: {e}")
        
        # Wait longer for dynamic content to load (Trackr likely uses JS to load content)
        print("Waiting for content to load...")
        time.sleep(3)
        
        # Scroll to load any lazy-loaded content
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.5)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(0.5)
        
        print(f"Current page title: {driver.title}")
        print(f"Current URL: {driver.current_url}")
        
        # Find all links with the specific classes
        print("\nSearching for links...")
        try:
            # Wait for links to be present
            wait = WebDriverWait(driver, 5)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "a")))
            
            # CSS selector for the specific link classes
            links = driver.find_elements(By.CSS_SELECTOR, "a.text-trackr-link-blue.hover\\:underline")
            
            if not links:
                print("No links found with exact class match. Trying alternative selectors...")
                # Try just the main class
                links = driver.find_elements(By.CSS_SELECTOR, "a.text-trackr-link-blue")
            
            if not links:
                print("Still no links. Checking all links on page...")
                all_links = driver.find_elements(By.TAG_NAME, "a")
                print(f"Total links found on page: {len(all_links)}")
                # Filter for links containing lever.co or job-related URLs
                links = [link for link in all_links if link.get_attribute('href') and 'lever.co' in link.get_attribute('href')]
            
            print(f"\n✓ Found {len(links)} links:\n")
            print("=" * 80)
            
            # Extract and print link data
            for i, link in enumerate(links, 1):
                link_href = link.get_attribute('href')
                
                if link_href:  # Only add if href exists
                    links_data.append(link_href)
                    
                    print(f"{i}. {link_href}")
                    print("-" * 80)
            
            # Save to file
            if links_data:
                import os
                output_path = os.path.join(os.path.expanduser("~"), "Desktop", "scraped_links.txt")
                with open(output_path, 'w', encoding='utf-8') as f:
                    for link_url in links_data:
                        f.write(f"{link_url}\n")
                print(f"\n✓ Saved {len(links_data)} links to: {output_path}")
            else:
                print("\n⚠ No valid links found to save")
                
        except Exception as e:
            print(f"Error finding links: {e}")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    
    finally:
        if driver:
            driver.quit()
            print("Browser closed")
    
    return links_data

if __name__ == "__main__":
    # Trackr UK Finance Graduate Programmes URL
    url = "https://app.the-trackr.com/uk-finance/graduate-programmes"
    
    links = scrape_trackr_links(url)
    
    # Print summary
    print(f"\n{'='*80}")
    print(f"SUMMARY: Scraped {len(links)} links in total")
    print(f"{'='*80}")