#!/usr/bin/env python3
"""
Car Valuation Tool for webuyanycar.com
Automates the process of getting car valuations by entering registration, mileage, and contact details.
Uses the same Selenium setup as CarScraper for consistency.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import re


class CarValuationTool:
    def __init__(self, chromedriver_path, headless=False):
        """Initialize the car valuation tool with Chrome WebDriver."""
        self.chromedriver_path = chromedriver_path
        self.driver = None
        self.wait = None
        self.setup_driver(headless)
    
    def setup_driver(self, headless=False):
        """Set up Chrome WebDriver with options - matching CarScraper configuration."""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--window-size=1920x1080")
        # Increase page load timeout
        chrome_options.add_argument("--page-load-strategy=none")
        # Disable images to improve performance
        chrome_options.add_argument("--blink-settings=imagesEnabled=false")
        
        try:
            service = Service(self.chromedriver_path)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.set_page_load_timeout(60)  # Increase timeout to 60 seconds
            self.wait = WebDriverWait(self.driver, 10)  # Increased timeout to 10 seconds
            print("WebDriver initialized successfully")
        except Exception as e:
            print(f"Error initializing WebDriver: {e}")
            print("Make sure Chrome and ChromeDriver are installed")
            raise
    
    def accept_cookies(self):
        """Automatically accept cookies if cookie banner is present."""
        print("Checking for cookie banner...")
        cookie_selectors = [
            "button#onetrust-accept-btn-handler",  # Common OneTrust accept button
            "button.cookie-banner__accept",  # Common class-based selector
            "button[aria-label*='accept']",  # ARIA label based
            "button[aria-label*='Accept']",
            "button[data-testid*='cookie']",  # Data testid based
            "button[class*='cookie']",  # Class contains cookie
            "button[class*='accept']",  # Class contains accept
            "button.js-cookie-accept",  # JS class based
            "a.cookie-accept",  # Link based accept
            "div.cookie-banner button",  # Button inside cookie banner
            "button.btn-accept-cookies",  # Common button class
        ]
        
        for selector in cookie_selectors:
            try:
                cookie_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                if cookie_button.is_displayed():
                    print("Cookie banner found, accepting cookies...")
                    cookie_button.click()
                    time.sleep(1)
                    print("Cookies accepted successfully")
                    return True
            except (NoSuchElementException, Exception):
                continue
        
        print("No cookie banner found or already accepted")
        return False
    
    def validate_inputs(self, registration, mileage, email, postcode, phone):
        """Validate all input parameters."""
        errors = []
        
        # Validate registration (UK format)
        if not re.match(r'^[A-Z0-9]{1,7}$', registration.upper().replace(' ', '')):
            errors.append("Registration must be 1-7 alphanumeric characters")
        
        # Validate mileage
        try:
            mileage_int = int(mileage.replace(',', ''))
            if mileage_int < 0 or mileage_int > 500000:
                errors.append("Mileage must be between 0 and 500,000")
        except ValueError:
            errors.append("Mileage must be a valid number")
        
        # Validate email
        email_pattern = r'^[a-zA-Z0-9!#$%&\'*+/=?^_`{|}~-]+(?:\.[a-zA-Z0-9!#$%&\'*+/=?^_`{|}~-]+)*@(?:[a-zA-Z0-9-]{2,}(?:[a-zA-Z0-9-]*[a-zA-Z0-9])?\.)+[a-zA-Z-]{2,}(?:[a-zA-Z]*[a-zA-Z])?$'
        if not re.match(email_pattern, email):
            errors.append("Invalid email format")
        
        # Validate UK postcode
        postcode_pattern = r'^(([gG][iI][rR] {0,}0[aA]{2})|((([a-pr-uwyzA-PR-UWYZ][a-hk-yA-HK-Y]?[0-9][0-9]?)|(([a-pr-uwyzA-PR-UWYZ][0-9][a-hjkstuwA-HJKSTUW])|([a-pr-uwyzA-PR-UWYZ][a-hk-yA-HK-Y][0-9][abehmnprv-yABEHMNPRV-Y]))) {0,}[0-9][abd-hjlnp-uw-zABD-HJLNP-UW-Z]{2}))$'
        if not re.match(postcode_pattern, postcode):
            errors.append("Invalid UK postcode format")
        
        # Validate UK phone number
        phone_pattern = r'^(((\+44\s?\d{4}|\(?0\d{4}\)?)\s?\d{3}\s?\d{3})|((\+44\s?\d{3}|\(?0\d{3}\)?)\s?\d{3}\s?\d{4})|((\+44\s?\d{2}|\(?0\d{2}\)?)\s?\d{4}\s?\d{4}))(\s?\#(\d{4}|\d{3}))?$'
        if not re.match(phone_pattern, phone):
            errors.append("Invalid UK phone number format")
        
        return errors
    
    def debug_page_content(self):
        """Debug method to see what's on the page"""
        print("=== PAGE DEBUG INFO ===")
        print(f"Current URL: {self.driver.current_url}")
        print(f"Page title: {self.driver.title}")
        
        # Get all visible text
        try:
            body = self.driver.find_element(By.TAG_NAME, "body")
            print(f"Body text: {body.text[:500]}...")  # First 500 chars
        except:
            print("Could not get body text")
        
        # Look for any elements that might contain the valuation
        try:
            elements = self.driver.find_elements(By.XPATH, "//div | //span | //h1 | //h2 | //h3")
            print("First 20 visible elements:")
            for i, element in enumerate(elements[:20]):
                if element.is_displayed() and element.text.strip():
                    print(f"  {i+1}. {element.tag_name}: '{element.text.strip()}'")
        except:
            print("Could not get elements for debugging")
    
    def get_valuation(self, registration, mileage, email, postcode, phone):
        """
        Get car valuation from webuyanycar.com
        
        Args:
            registration (str): Vehicle registration number
            mileage (str): Vehicle mileage
            email (str): Email address
            postcode (str): UK postcode
            phone (str): UK phone number
            
        Returns:
            dict: Contains success status, valuation amount, and any error messages
        """
        # Validate inputs
        validation_errors = self.validate_inputs(registration, mileage, email, postcode, phone)
        if validation_errors:
            return {
                'success': False,
                'error': 'Validation failed: ' + ', '.join(validation_errors)
            }
        
        try:
            # Navigate to the website
            print("Loading webuyanycar.com...")
            self.driver.get("https://www.webuyanycar.com/car-valuation/")
            
            # Wait for the page to load
            time.sleep(3)
            
            # Automatically accept cookies
            self.accept_cookies()
            
            # Step 1: Enter registration number
            print(f"Entering registration: {registration}")
            reg_input = self.wait.until(
                EC.element_to_be_clickable((By.NAME, "registrationNumber"))
            )
            reg_input.clear()
            reg_input.send_keys(registration.upper())
            
            # Step 2: Enter mileage
            print(f"Entering mileage: {mileage}")
            mileage_input = self.wait.until(
                EC.element_to_be_clickable((By.NAME, "mileage"))
            )
            mileage_input.clear()
            mileage_input.send_keys(mileage)
            
            # Step 3: Click the first submit button
            print("Clicking 'Get my car valuation' button...")
            submit_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.cta.primary[type='submit']"))
            )
            submit_button.click()
            
            # Wait for the next page to load
            time.sleep(3)
            
            # Step 4: Enter email address
            print(f"Entering email: {email}")
            email_input = self.wait.until(
                EC.element_to_be_clickable((By.ID, "EmailAddress"))
            )
            email_input.clear()
            email_input.send_keys(email)
            
            # Step 5: Enter postcode
            print(f"Entering postcode: {postcode}")
            postcode_input = self.wait.until(
                EC.element_to_be_clickable((By.ID, "Postcode"))
            )
            postcode_input.clear()
            postcode_input.send_keys(postcode)
            
            # Step 6: Enter phone number
            print(f"Entering phone: {phone}")
            phone_input = self.wait.until(
                EC.element_to_be_clickable((By.ID, "TelephoneNumber"))
            )
            phone_input.clear()
            phone_input.send_keys(phone)
            
            # Step 7: Click the final submit button
            print("Clicking 'Get my valuation' button...")
            final_button = self.wait.until(
                EC.element_to_be_clickable((By.ID, "advance-btn"))
            )
            final_button.click()
            
            # Step 8: Wait for and extract the valuation amount
            print("Waiting for valuation result...")
            time.sleep(5)  # Give extra time for the valuation to load
            
            # Try multiple approaches to find the valuation amount
            valuation_element = None
            valuation_text = ""

            # Approach 1: Try the specific XPath you provided
            try:
                valuation_element = self.driver.find_element(By.XPATH, "/html/body/div[1]/wbac-app/div/div/div/valuation/section[2]/div/div/div[1]/div[1]/div/div[1]/div/div[1]")
                valuation_text = valuation_element.text.strip()
                print(f"Found valuation using XPath: {valuation_text}")
            except NoSuchElementException:
                print("XPath approach failed, trying alternative selectors...")

            # Approach 2: If XPath failed, try other common patterns
            if not valuation_text:
                selectors_to_try = [
                    "div.amount", 
                    "span.amount",
                    "[class*='amount']",
                    "[class*='value']",
                    "[class*='price']",
                    "[class*='valuation']",
                    "div.valuation-amount",
                    "span.valuation-amount",
                    "div.result-amount",
                    "span.result-amount",
                    "div.valuation-result",
                    "div.valuation__amount",
                    "span.valuation__amount",
                    "div[data-testid*='amount']",
                    "div[data-testid*='valuation']",
                    "div.ng-star-inserted .amount",
                ]
                
                for selector in selectors_to_try:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for element in elements:
                            if element.is_displayed() and element.text.strip():
                                text = element.text.strip()
                                if '£' in text or any(char.isdigit() for char in text):
                                    valuation_element = element
                                    valuation_text = text
                                    print(f"Found valuation using selector '{selector}': {valuation_text}")
                                    break
                        if valuation_text:
                            break
                    except Exception:
                        continue

            # Approach 3: Look for any element containing £ symbol
            if not valuation_text:
                try:
                    elements_with_pound = self.driver.find_elements(By.XPATH, "//*[contains(text(), '£')]")
                    for element in elements_with_pound:
                        if element.is_displayed() and element.text.strip():
                            text = element.text.strip()
                            if '£' in text:
                                valuation_element = element
                                valuation_text = text
                                print(f"Found valuation using £ symbol: {valuation_text}")
                                break
                except Exception:
                    pass

            # Approach 4: Look for large numbers that might be the valuation
            if not valuation_text:
                try:
                    # Look for elements with large numbers (likely to be the valuation)
                    all_elements = self.driver.find_elements(By.XPATH, "//div | //span | //h1 | //h2 | //h3")
                    for element in all_elements:
                        if element.is_displayed() and element.text.strip():
                            text = element.text.strip()
                            # Look for patterns like £1,234 or 1234
                            if (('£' in text and any(char.isdigit() for char in text)) or 
                                (len(text) <= 10 and any(char.isdigit() for char in text) and 
                                 sum(1 for c in text if c.isdigit()) >= 3)):
                                valuation_element = element
                                valuation_text = text
                                print(f"Found potential valuation: {valuation_text}")
                                break
                except Exception:
                    pass

            if not valuation_text:
                # Debug and take screenshot
                self.debug_page_content()
                self.driver.save_screenshot("valuation_page.png")
                print("Screenshot saved as 'valuation_page.png' for debugging")
                return {
                    'success': False,
                    'error': 'Could not find valuation amount element on page'
                }

            print(f"Valuation found: {valuation_text}")

            # Extract numeric value
            amount_match = re.search(r'£(\d{1,3}(?:,\d{3})*)', valuation_text)
            if amount_match:
                amount = int(amount_match.group(1).replace(',', ''))
                return {
                    'success': True,
                    'valuation': amount,
                    'valuation_text': valuation_text,
                    'registration': registration,
                    'mileage': mileage
                }
            else:
                # Try alternative pattern without pound sign
                alt_match = re.search(r'(\d{1,3}(?:,\d{3})*)', valuation_text)
                if alt_match:
                    amount = int(alt_match.group(1).replace(',', ''))
                    return {
                        'success': True,
                        'valuation': amount,
                        'valuation_text': valuation_text,
                        'registration': registration,
                        'mileage': mileage
                    }
                else:
                    return {
                        'success': False,
                        'error': f'Could not parse valuation amount from: {valuation_text}'
                    }
                
        except TimeoutException as e:
            return {
                'success': False,
                'error': f'Timeout waiting for page element: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}'
            }
    
    def close(self):
        """Close the WebDriver."""
        if self.driver:
            self.driver.quit()
            print("WebDriver closed")


def get_valuation_for_car(chromedriver_path, registration, mileage, email, postcode, phone, headless=True):
    """
    Standalone function to get car valuation - can be called from other scripts
    
    Args:
        chromedriver_path (str): Path to ChromeDriver executable
        registration (str): Vehicle registration number
        mileage (str): Vehicle mileage
        email (str): Email address
        postcode (str): UK postcode
        phone (str): UK phone number
        headless (bool): Run browser in headless mode
        
    Returns:
        dict: Contains success status, valuation amount, and any error messages
    """
    tool = CarValuationTool(chromedriver_path, headless=headless)
    
    try:
        result = tool.get_valuation(registration, mileage, email, postcode, phone)
        return result
    finally:
        tool.close()


def main():
    """Main function to run the car valuation tool interactively."""
    print("=== Car Valuation Tool ===")
    print("This tool will get your car's valuation from webuyanycar.com\n")
    
    # Set chromedriver path (update this path to match your system)
    chromedriver_path = "/opt/anaconda3/envs/myenv/bin/chromedriver"  # Update this path
    
    # Get user inputs
    registration = input("Enter your registration number: ").strip()
    mileage = input("Enter your car's mileage: ").strip()
    email = "hamza12ali786@gmail.com"
    postcode = "bd15 7ud"
    phone = "07368832422"
    
    # Ask if user wants to run in headless mode
    headless_choice = 'n'
    headless = headless_choice in ['y', 'yes']
    
    # Initialize the tool with chromedriver path
    tool = CarValuationTool(chromedriver_path, headless=headless)
    
    try:
        print("\nStarting valuation process...")
        result = tool.get_valuation(registration, mileage, email, postcode, phone)
        
        print("\n" + "="*50)
        if result['success']:
            print("✅ VALUATION SUCCESSFUL!")
            print(f"Registration: {result['registration']}")
            print(f"Mileage: {result['mileage']}")
            print(f"Valuation: £{result['valuation']:,}")
            print(f"Raw text: {result['valuation_text']}")
        else:
            print("❌ VALUATION FAILED!")
            print(f"Error: {result['error']}")
        print("="*50)
        
    except KeyboardInterrupt:
        print("\n\nProcess interrupted by user")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
    finally:
        tool.close()


if __name__ == "__main__":
    main()