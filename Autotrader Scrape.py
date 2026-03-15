import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import lognorm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scipy import stats
import seaborn as sns
import time
import re
import json
import os
import csv
from pathlib import Path
from ImageExtractor import CarDetailExtractor 
from sklearn.linear_model import LinearRegression
from scipy import stats as scipy_stats
from datetime import datetime

extractor = CarDetailExtractor()
screenshot_data = extractor.process_clipboard()


class CarScraper:
    def __init__(self):
        self.driver = None
        self.mileage = 0
        self.session_file = os.path.join(
            '/Users/salahbaaziz/Desktop/Projects/Autotrader Scrape',
            "autotrader_cars_session.json"
        )

        self.mileage = 0
        self.session_file = os.path.join('/Users/salahbaaziz/Desktop/Projects/Autotrader Scrape',"autotrader_cars_session.json")

    def setup_driver(self, headless=False, clear_cookies=True):

        chrome_options = Options()

        if headless:
            chrome_options.add_argument("--headless=new")

        if clear_cookies:
            chrome_options.add_argument("--incognito")

        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--window-size=1920x1080")
        chrome_options.add_argument("--disable-dev-shm-usage")

        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.set_page_load_timeout(60)

    def accept_cookies(self, timeout=5):
        """
        Accept cookies on AutoTrader - fast version
        """
        # Check main document immediately
        try:
            cookie_button = self.driver.find_element(By.CSS_SELECTOR, "button.message-component.message-button.sp_choice_type_11[aria-label='Accept All']")
            cookie_button.click()
            print("Cookies accepted from main document")
            return True
        except:
            pass
        
        # Quick iframe check
        iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
        for iframe in iframes:
            try:
                self.driver.switch_to.frame(iframe)
                cookie_button = self.driver.find_element(By.CSS_SELECTOR, "button.message-component.message-button.sp_choice_type_11[aria-label='Accept All']")
                cookie_button.click()
                self.driver.switch_to.default_content()
                print("Cookies accepted from iframe")
                return True
            except:
                self.driver.switch_to.default_content()
                continue
        
        # Fallback to XPath method
        try:
            button = WebDriverWait(self.driver, 2).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@title='Accept All']"))
            )
            button.click()
            print("Cookies accepted via XPath fallback")
            return True
        except:
            print("No cookie banner found (or already accepted)")
            return False

    def save_session(self, data):
        """Save session data to a file"""
        session_data = {
            "make": data[0],
            "model": data[1],
            "variant": data[2],
            "engine_size": data[3],
            "plate": data[4],
            "mileage": data[5],
            "fuel_type": data[6],
            "cap_price": data[7],
            "year_diff": data[8],
            "mileage_diff": data[9]
        }
        
        with open(self.session_file, 'w') as f:
            json.dump(session_data, f)
        
        print(f"Session data saved to {self.session_file}")

    def load_session(self):
        """Load session data from file if it exists"""
        if os.path.exists(self.session_file):
            try:
                with open(self.session_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading session data: {e}")
                return None
        return None

    def determine_fuel_type(self, engine_size):
        """Determine fuel type based on engine size string"""
        if engine_size.lower().endswith('d'):
            return "Diesel"
        else:
            return "Petrol"

    def get_clean_engine_size(self, engine_size):
        """Remove any 'd' or 'D' from the end of engine size and return as float"""
        clean_size = engine_size.rstrip('dD')
        try:
            return float(clean_size)
        except ValueError:
            raise ValueError(f"Invalid engine size format: {engine_size}")

    def get_input(self):
        # Use screenshot data
        parts = screenshot_data
        
        # Handle test case automatically
        if parts == ["test"]:
            make, model, variant, engine_size, plate, mileage = "Ford", "Fiesta", "Zetec", "1.0", "2013", 50000
            fuel_type = "Petrol"
            cap_price = 2700
            year_diff = 1
            mileage_diff = 30000
            print("Using test data: Ford Fiesta Zetec 1.6, 2013, 50000 miles")
        else:
            # Validate input length
            if len(parts) != 10:
                raise ValueError("Invalid screenshot data format. Expected 10 values.")

            make, model, variant, engine_size, plate, mileage, cap_price, fuel_type, doors, transmission = parts[0], parts[1], parts[2], parts[3], parts[4], int(parts[5]), int(parts[6]), parts[7], parts[8], parts[9]
            
            year_diff = 0  # Default year difference
            mileage_diff = 30000  # Default mileage difference

            def calculate_fixed_auction_fee(cap_price, interval_ranges, auction_fee_list):
                """
                Finds the correct interval for cap_price and returns the corresponding fixed auction_fee.
                """
                for i, (low, high) in enumerate(interval_ranges):
                    if low <= cap_price <= high:
                        return auction_fee_list[i]
                return None  # Return None if no interval is found (cap_price is too high or invalid)
            
            interval_ranges = [
                (11, 49), (50, 99), (100, 149), (150, 199), (200, 249), (250, 299),
                (300, 349), (350, 399), (400, 449), (450, 499), (500, 749), (750, 999),
                (1000, 1249), (1250, 1499), (1500, 1749), (1750, 1999), (2000, 2249),
                (2250, 2499), (2500, 2749), (2750, 2999), (3000, 3249), (3250, 3499),
                (3500, 3749), (3750, 3999), (4000, 4249), (4250, 4499), (4500, 4749),
                (4750, 4999), (5000, 5249), (5250, 5499), (5500, 5749), (5750, 5999),
                (6000, 6249), (6250, 6499), (6500, 6749), (6750, 6999), (7000, 7249),
                (7250, 7499), (7500, 7749), (7750, 7999), (8000, 8249), (8250, 8499),
                (8500, 8749), (8750, 8999), (9000, 9249), (9250, 9499), (9500, 9749),
                (9750, 9999), (10000, 10249), (10250, 10499), (10500, 10749),
                (10750, 10999), (11000, 11249), (11250, 11499), (11500, 1000000)
            ]

            auction_fee_list = [
                49.84, 83.85, 123.00, 169.39, 182.99, 190.84, 243.01, 249.22, 263.16, 269.57,
                307.21, 325.23, 345.51, 359.11, 373.25, 393.68, 413.14, 418.07, 422.36, 422.64,
                480.48, 485.25, 494.20, 497.24, 501.67, 503.81, 508.21, 512.36, 520.22, 525.00,
                529.83, 536.08, 536.26, 539.44, 546.80, 553.20, 553.19, 558.81, 569.34, 580.50,
                584.67, 590.43, 590.97, 591.92, 600.54, 605.38, 607.52, 620.72, 645.84, 660.03,
                662.42, 679.61, 695.34, 709.29, 1435.00
            ]
            auction_fee = calculate_fixed_auction_fee(cap_price, interval_ranges, auction_fee_list)
            assurance_fee = 66
            advertising_fee = 50
            transport_fee = 80
            v5_fee = 0

            cap_price += auction_fee + assurance_fee + v5_fee + advertising_fee + transport_fee

        # Store the input mileage as an instance variable
        self.mileage = int(mileage)

        # Extract year from plate
        try:
            year = int(re.search(r'\d+', plate).group())
        except AttributeError:
            raise ValueError("Invalid plate format. Could not extract year.")

        # Compute min/max mileage and year
        min_mileage = 30000
        max_mileage = 100000
        min_year = year - year_diff
        max_year = min(2025, year + year_diff)

        print(f"Searching for cars with mileage between {min_mileage} and {max_mileage} miles. Within the years {min_year} and {max_year}")
        
        # Clean engine size for URL
        clean_engine_size = self.get_clean_engine_size(engine_size)
        
        # Save session data for next run
        self.save_session([make, model, variant, engine_size, plate, mileage, fuel_type, cap_price, year_diff, mileage_diff])
        
        return make, model, variant, cap_price, min_mileage, max_mileage, min_year, max_year, fuel_type, clean_engine_size, doors, transmission

    def generate_base_url(self, make, model, variant, min_mileage, max_mileage, min_year, max_year, fuel_type, engine_size, doors, transmission):
        return f"https://www.autotrader.co.uk/car-search?advertising-location=at_cars&aggregatedTrim={variant}&body-type=&colour=&exclude-writeoff-categories=on&fuel-type={fuel_type}&make={make}&maximum-badge-engine-size={float(engine_size) + 0.1}&maximum-mileage={max_mileage}&minimum-badge-engine-size={float(engine_size)}&minimum-mileage={min_mileage}&model={model}&postcode=yo1+0sb&quantity-of-doors={doors}&sort=price-asc&transmission={transmission}&year-from={min_year}&year-to={max_year}&page="

    def load_page(self, url, page):
        print(f"Loading page {page}: {url}")
        self.driver.get(url)
        
        # Accept cookies immediately after page load
        self.accept_cookies()
        
        try:
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='search-listing-title']"))
            )
        except Exception as e:
            print(f"Error loading page {page}: {e}")
            return False
        return True

    def scroll_and_collect_titles(self):
        all_titles = set()
        scroll_attempts = 0
        max_scroll_attempts = 10

        while scroll_attempts < max_scroll_attempts:
            self.driver.execute_script("window.scrollTo(0, (document.body.scrollHeight));")
            time.sleep(2)

            title_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid='search-listing-title']")
            for elem in title_elements:
                all_titles.add(elem.text)

            
            if scroll_attempts > 5:
                last_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid='search-listing-title']") # 
                if len(last_elements) == len(all_titles):
                    break

            scroll_attempts += 1

        return all_titles

    def extract_mileage_and_calculate_avg(self):
        # Scroll down and collect mileage data
        mileages = []
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Give it time to load

            # Find mileage data using the JSON path provided
            mileage_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid='mileage']")   
            for mileage in mileage_elements:
                try:
                    mileages.append(int(mileage.text.strip().replace(' miles', '').replace(',', '')))
                except ValueError:
                    continue  # Skip if mileage is not a valid number

            # Check if we have reached the end of the page
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        # Calculate average mileage
        if mileages:
            avg_mileage = sum(mileages) / len(mileages)
            return mileages, avg_mileage
        else:
            return [], 0

    def run(self, max_pages=1):
        make, model, variant, cap_price, min_mileage, max_mileage, min_year, max_year, fuel_type, engine_size, doors, transmission = self.get_input()
        
        # Setup driver with cookie handling
        self.setup_driver(headless=False, clear_cookies=True)  # Set headless=True for production

        base_url = self.generate_base_url(make, model, variant, min_mileage, max_mileage, min_year, max_year, fuel_type, engine_size, doors, transmission)

        car_data = []

        for page in range(1, max_pages + 1):
            url = base_url + str(page)

            if not self.load_page(url, page):
                continue

            all_titles = self.scroll_and_collect_titles()

            for title in all_titles:
                car_data.append(title)

        # Call mileage extraction function
        mileages, avg_mileage = self.extract_mileage_and_calculate_avg()

        self.driver.quit()

        print(f"Average Mileage: {round(avg_mileage,-2)} miles")
        #print(f"Collected Mileage Data: {mileages}")  # This will output all collected mileage data
        
        # Return fuel_type as part of the results
        return car_data, make, model, variant, cap_price, min_year, max_year, engine_size, avg_mileage, mileages, self.mileage, fuel_type, doors, transmission


class PriceExtractor:
    def __init__(self):
        pass

    def extract_price(self, car_data):
        price_data = []
        for car in car_data:
            price_match = re.search(r'£([\d,]+)', car)
            if price_match:
                price = int(price_match.group(1).replace(',', ''))
                price_data.append(price)
            else:
                price_data.append(None)
        return price_data


class PricePlotter:
    def __init__(self, folder='/Users/salahbaaziz/Desktop/Projects/Autotrader Scrape'):
        self.folder = folder
        self.results_file = os.path.join(folder, "autotrader_cars.json")
        self.csv_file = os.path.join(folder, "autotrader_cars.csv")
    
    def _is_valid_file(self, file_path, extensions):
        """Check if the file exists and has a valid extension."""
        return os.path.isfile(file_path) and file_path.endswith(extensions)
    
    def save_results(self, prices, mileages, cap_price, input_mileage, make, model, variant, engine_size, min_year, max_year, fuel_type=None):
        """Save analysis results to a JSON file and append to CSV"""
        valid_data = [(p, m) for p, m in zip(prices, mileages) if p is not None and m > 0]
        if not valid_data:
            print("No valid data to save.")
            return

        filtered_prices = [p for p in prices if p is not None and p > 0]
        log_prices = np.log(filtered_prices)
        mu, std = np.mean(log_prices), np.std(log_prices)
        mean_price = np.exp(mu)
        lower_std = np.exp(mu - std)
        upper_std = np.exp(mu + std)

        # Compute peak density
        prices_array, mileages_array = np.array([p for p, m in valid_data]), np.array([m for p, m in valid_data])
        if len(prices_array) >= 2:
            kde = stats.gaussian_kde([mileages_array, prices_array])
            mg, pg = np.meshgrid(np.linspace(min(mileages_array), max(mileages_array), 100),
                                 np.linspace(min(prices_array), max(prices_array), 100))
            positions = np.vstack([mg.ravel(), pg.ravel()])
            density = kde(positions).reshape(mg.shape)
            max_density_idx = np.unravel_index(np.argmax(density), density.shape)
            peak_mileage = mg[0][max_density_idx[1]]
            peak_price = pg[max_density_idx[0]][0]
        else:
            peak_mileage, peak_price = input_mileage, cap_price

        avg_mileage = sum(mileages_array) / len(mileages_array) if len(mileages_array) > 0 else input_mileage
        vehicle_key = f"{min_year}-{max_year}_{make}_{model}_{variant}_{engine_size}L"
        new_result = {
            "vehicle": f"{min_year}-{max_year} {engine_size}L {make} {model} {variant}",
            "input_mileage": input_mileage,
            "avg_mileage": avg_mileage,
            "cap_price": cap_price,
            "mean_price": mean_price,
            "lower_std_price": lower_std,
            "upper_std_price": upper_std,
            "peak_density_mileage": peak_mileage,
            "peak_density_price": peak_price,
            "sample_size": len(filtered_prices),
            "fuel_type": fuel_type,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        try:
            results_data = {}  # Default empty dict
            if self._is_valid_file(self.results_file, (".json",)):
                with open(self.results_file, 'r') as f:
                    try:
                        results_data = json.load(f)
                    except json.JSONDecodeError:
                        pass  # Invalid JSON, overwrite with new data
            results_data[vehicle_key] = new_result
            with open(self.results_file, 'w') as f:
                json.dump(results_data, f, indent=4)
            print(f"Analysis results saved to {self.results_file}")

            self.append_to_csv(make, model, variant, engine_size, fuel_type, f"{min_year}-{max_year}", input_mileage, avg_mileage, cap_price, lower_std, mean_price, upper_std)
        except Exception as e:
            print(f"Error saving results: {e}")
    
    def append_to_csv(self, make, model, variant, engine_size, fuel_type, year, mileage, avg_mileage, cap_price, lower_std, mean_price, upper_std):
        """Append the data to the CSV file"""
        headers = ['Date', 'Make', 'Model', 'Variant', 'Engine Size', 'Fuel Type', 'Year', 'Mileage', 'Average Mileage', 'CAP Price', 'Lower SD', 'Mean', 'Upper SD', 'Profit']
        lower_profitt = (lower_std - cap_price) / cap_price * 100 if cap_price > 0 else 0
        data_row = {
            'Date': time.strftime("%Y-%m-%d"),
            'Make': make, 'Model': model, 'Variant': variant,
            'Engine Size': engine_size, 'Fuel Type': fuel_type, 'Year': year,
            'Mileage': int(mileage), 'Average Mileage': int(round(avg_mileage)),
            'CAP Price': int(cap_price), 'Lower SD': int(round(lower_std)),
            'Mean': int(round(mean_price)), 'Upper SD': int(round(upper_std)),
            'Profit': round(lower_profitt, 2)
        }
        try:
            file_exists = self._is_valid_file(self.csv_file, (".csv",))
            with open(self.csv_file, 'a', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=headers)
                if not file_exists:
                    writer.writeheader()
                writer.writerow(data_row)
                print(f"Data appended to CSV: {self.csv_file}")
        except Exception as e:
            print(f"Error appending to CSV: {e}")

    def plot_combined_analysis(self, prices, mileages, cap_price, input_mileage, make, model, variant, engine_size, min_year, max_year, fuel_type, doors, transmission):

        # Filter data
        filtered_prices = [price for price in prices if price is not None and price > 0]
        valid_data = [(price, mileage) for price, mileage in zip(prices, mileages) if price is not None and mileage > 0]
        
        if not valid_data or len(filtered_prices) == 0:
            print("No valid data to plot.")
            return
        
        prices_data, mileages_data = zip(*valid_data)
        prices_array = np.array(prices_data)
        mileages_array = np.array(mileages_data)
        
        # Calculate statistics
        log_prices = np.log(filtered_prices)
        mu, std = np.mean(log_prices), np.std(log_prices)
        mean_price = np.exp(mu)
        lower_std = np.exp(mu - std)
        upper_std = np.exp(mu + std)
        
        # Create KDE for finding peak density
        kde = stats.gaussian_kde([mileages_array, prices_array])
        mileage_grid = np.linspace(min(mileages_array), max(mileages_array), 100)
        price_grid = np.linspace(min(prices_array), max(prices_array), 100)
        mg, pg = np.meshgrid(mileage_grid, price_grid)
        positions = np.vstack([mg.ravel(), pg.ravel()])
        density = kde(positions).reshape(mg.shape)
        max_density_idx = np.unravel_index(np.argmax(density), density.shape)
        peak_mileage = mileage_grid[max_density_idx[1]]
        peak_price = price_grid[max_density_idx[0]]
        
        # Calculate lower_profit
        lower_profit_percent = (lower_std - cap_price) / cap_price * 100 if cap_price > 0 else 0

        # Calculate mean profit
        mean_profit_percent = (mean_price - cap_price) / cap_price * 100 if cap_price > 0 else 0
        
        # Create the combined figure
        fig = plt.figure(figsize=(16, 10))
        fig.suptitle(f'{min_year}-{max_year} {make} {model} {variant} {engine_size}L {fuel_type} Analysis', fontsize=20)
        
        # Price Distribution - Histogram
        ax1 = plt.subplot2grid((2, 2), (0, 0))
        counts, bins, patches = ax1.hist(filtered_prices, bins=20, color='blue', edgecolor='black', alpha=0.6, density=False)
        
        # Add counts on top of bars
        for count, bin_patch in zip(counts, patches):
            if count > 0:  # Only show labels for non-zero counts
                ax1.text(bin_patch.get_x() + bin_patch.get_width() / 2, count, f'{int(count)}',
                        ha='center', va='bottom', fontsize=8, color='black')
        
        # Log-normal distribution curve
        xmin, xmax = ax1.get_xlim()
        x = np.linspace(xmin, xmax, 100)
        pdf = lognorm.pdf(x, s=std, scale=np.exp(mu))
        ax1.plot(x, pdf * len(filtered_prices) * (bins[1] - bins[0]), 'k', linewidth=2, label='Log-normal fit')
        
        # Vertical lines for key statistics
        ax1.axvline(mean_price, color='red', linestyle='dotted', linewidth=2, label='Mean Price')
        ax1.axvline(lower_std, color='red', linestyle='dashed', linewidth=2, label='-1 Std Dev')
        ax1.axvline(upper_std, color='red', linestyle='dashed', linewidth=2, label='+1 Std Dev')
        ax1.axvline(cap_price, color='green', linestyle='solid', linewidth=2, label='CAP Price')
        
        ax1.set_title('Price Distribution', fontsize=14)
        ax1.set_xlabel('Price (£)', fontsize=12)
        ax1.set_ylabel('Frequency', fontsize=12)
        ax1.legend(loc='upper right', fontsize=8)
        
        # Scatter Plot
        ax2 = plt.subplot2grid((2, 2), (0, 1))
        ax2.scatter(mileages_data, prices_data, c='black', alpha=0.5, s=30, label='Market Data')
        
        # Determine color based on lower_profit
        point_color = '#00FF00' if lower_profit_percent > 0 else '#FF0000'
        
        # Plot the input point and highest density point
        ax2.scatter(input_mileage, cap_price, c=point_color, s=100, edgecolors='black', zorder=5, label=f'CAP Price (£{cap_price})')
        ax2.scatter(peak_mileage, peak_price, c='purple', marker='o', s=100, zorder=4, edgecolors='black', label=f'Peak Density (£{int(peak_price)})')
        
        # Draw connection line
        ax2.plot([input_mileage, peak_mileage], [cap_price, peak_price], 'k--', linewidth=1.5, zorder=1)
        
        # Add reference lines
        ax2.axhline(mean_price, color='red', linestyle='dotted', linewidth=2, label=f'Mean (£{int(mean_price)})')
        ax2.axhline(lower_std, color='green', linestyle='dashed', linewidth=2, label=f'-1 Std Dev (£{int(lower_std)})')
        ax2.axhline(upper_std, color='red', linestyle='dashed', linewidth=2, label=f'+1 Std Dev (£{int(upper_std)})')
        
        ax2.set_title('Price vs Mileage', fontsize=14)
        ax2.set_xlabel('Mileage (miles)', fontsize=12)
        ax2.set_ylabel('Price (£)', fontsize=12)
        ax2.legend(loc='upper right', fontsize=8)
        
        # Fit a linear regression model
        ax3 = plt.subplot2grid((2, 2), (1, 0))

        X = mileages_array.reshape(-1, 1)
        y = prices_array.reshape(-1)  # Ensure 1D for y
        model = LinearRegression()
        model.fit(X, y)

        # Predict prices based on the model
        mileage_range = np.linspace(min(mileages_array), max(mileages_array), 100).reshape(-1, 1)
        price_predictions = model.predict(mileage_range)

        # Calculate R-squared
        r_squared = model.score(X, y)

        # Calculate depreciation per mile
        depreciation_per_mile = abs(model.coef_[0])

        # Calculate depreciation per 1000 miles
        depreciation_per_1000_miles = depreciation_per_mile * 1000

        # Plot the data points
        ax3.scatter(mileages_array, prices_array, c='black', alpha=0.5, s=30, label='Market Data')

        # Plot the regression line
        ax3.plot(mileage_range, price_predictions, 'r-', linewidth=2, 
                label=f'Regression (R² = {r_squared:.2f})')

        # Calculate prediction interval
        n = len(mileages_array)
        y_pred = model.predict(X)
        mse = np.sum((y - y_pred) ** 2) / (n - 2)
        std_error = np.sqrt(mse)

        # Confidence bands (ensure dimensions align)
        t_value = scipy_stats.t.ppf(0.975, n - 2)
        interval = t_value * std_error * np.sqrt(1 + 1/n + ((mileage_range - np.mean(mileages_array))**2 / 
                                                        np.sum((mileages_array - np.mean(mileages_array))**2)))

        upper_bound = price_predictions + interval.flatten()
        lower_bound = price_predictions - interval.flatten()

        ax3.fill_between(mileage_range.flatten(), lower_bound, upper_bound, color='gray', alpha=0.2, label='95% Confidence')

        # Add the car's position
        ax3.scatter(input_mileage, cap_price, c=point_color, s=100, edgecolors='black', zorder=5, 
                    label=f'CAP Price (£{cap_price})')

        # Add annotation for depreciation rate
        ax3.text(0.05, 0.95, f"Depreciation: £{depreciation_per_1000_miles:.2f} per 1000 miles", 
                transform=ax3.transAxes, fontsize=10, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

        ax3.set_title('Price-Mileage Regression Analysis', fontsize=14)
        ax3.set_xlabel('Mileage (miles)', fontsize=12)
        ax3.set_ylabel('Price (£)', fontsize=12)
        ax3.set_xlim(20000, max(mileages_array) + 10000)
        ax3.legend(loc='upper right', fontsize=8)

        # Heatmap
        ax4 = plt.subplot2grid((2, 2), (1, 1))
        sns.kdeplot(ax=ax4, x=mileages_data, y=prices_data, cmap='plasma', fill=True, alpha=0.7, levels=50)
        
        # Overlay data points
        ax4.scatter(mileages_data, prices_data, c='black', alpha=0.3, s=15)
        
        # Add key points
        ax4.scatter(input_mileage, cap_price, c=point_color, s=100, edgecolors='black', zorder=5, label=f'CAP Price (£{cap_price})')
        ax4.scatter(peak_mileage, peak_price, c='white', marker='o', s=100, zorder=4, edgecolors='black', label=f'Peak Density (£{int(peak_price)})')
        
        # Draw connection line
        ax4.plot([input_mileage, peak_mileage], [cap_price, peak_price], 'k--', linewidth=1.5, zorder=2)
         
        ax4.set_title('Price Density Heatmap', fontsize=14)
        ax4.set_xlabel('Mileage (miles)', fontsize=12)
        ax4.set_ylabel('Price (£)', fontsize=12)
        ax4.legend(loc='upper right', fontsize=8)
        
        # Add lower_profit information as text
        profit_text = f"Worst/Mean Case: {lower_profit_percent:.2f}% (£{int(lower_std - cap_price)}) / {mean_profit_percent:.2f}% (£{int(mean_price - cap_price)})"
        profit_color = 'green' if lower_profit_percent > 0 else 'red'
        fig.text(0.5, 0.02, profit_text, ha='center', fontsize=14, color=profit_color, 
            bbox=dict(facecolor='white', alpha=0.8, edgecolor=profit_color, boxstyle='round,pad=0.5'))
        
        # Add sample size information
        sample_text = f"Sample Size: {len(filtered_prices)} vehicles"
        fig.text(0.02, 0.02, sample_text, ha='left', fontsize=10)
        

        plt.tight_layout(rect=[0, 0.07, 1, 0.95])
        plt.show()

class BCACarDataSaver:
    def __init__(self, folder='/Users/salahbaaziz/Desktop/Projects/Autotrader Scrape'):
        self.folder = folder
        self.json_file = os.path.join(folder, "bca_car.json")
        self.csv_file = os.path.join(folder, "bca_car.csv")
    
    def calculate_statistics(self, prices, cap_price):
        """Calculate price statistics and profit margins"""
        # Filter out None values and ensure we have valid price data
        filtered_prices = [price for price in prices if price is not None and price > 0]
        
        if len(filtered_prices) == 0:
            return {
                'mean_price': 0,
                'lower_std': 0,
                'upper_std': 0,
                'lower_profit_percent': 0,
                'mean_profit_percent': 0,
                'upper_profit_percent': 0,
                'sample_size': 0
            }
        
        # Calculate log-normal statistics
        log_prices = np.log(filtered_prices)
        mu, std = np.mean(log_prices), np.std(log_prices)
        mean_price = np.exp(mu)
        lower_std = np.exp(mu - std)
        upper_std = np.exp(mu + std)
        
        # Calculate profit margins as percentages
        lower_profit_percent = ((lower_std - cap_price) / cap_price * 100) if cap_price > 0 else 0
        mean_profit_percent = ((mean_price - cap_price) / cap_price * 100) if cap_price > 0 else 0
        upper_profit_percent = ((upper_std - cap_price) / cap_price * 100) if cap_price > 0 else 0
        
        return {
            'mean_price': round(mean_price, 2),
            'lower_std': round(lower_std, 2),
            'upper_std': round(upper_std, 2),
            'lower_profit_percent': round(lower_profit_percent, 2),
            'mean_profit_percent': round(mean_profit_percent, 2),
            'upper_profit_percent': round(upper_profit_percent, 2),
            'sample_size': len(filtered_prices)
        }
    
    def save_bca_car_data(self, make, model, variant, cap_price, min_year, max_year, 
                         engine_size, avg_mileage, mileages, input_mileage, fuel_type, 
                         doors, transmission, prices):
        """Save car data and statistics to both JSON and CSV files"""
        
        # Get current date
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        # Calculate statistics
        stats = self.calculate_statistics(prices, cap_price)
        
        # Create comprehensive data record
        car_record = {
            'timestamp': current_date,
            'make': make,
            'model': model,
            'variant': variant,
            'cap_price': cap_price,
            'min_year': min_year,
            'max_year': max_year,
            'engine_size': engine_size,
            'avg_mileage': round(avg_mileage, 0) if avg_mileage > 0 else 0,
            'input_mileage': input_mileage,
            'fuel_type': fuel_type,
            'doors': doors,
            'transmission': transmission,
            'lower_std_price': stats['lower_std'],
            'mean_price': stats['mean_price'],
            'upper_std_price': stats['upper_std'],
            'lower_profit_percent': stats['lower_profit_percent'],
            'mean_profit_percent': stats['mean_profit_percent'],
            'upper_profit_percent': stats['upper_profit_percent'],
            'sample_size': stats['sample_size'],
            'all_mileages': mileages[:50] if len(mileages) > 50 else mileages,
            'all_prices': [p for p in prices if p is not None][:50] if prices else []
        }
        
        # Save to JSON
        self._save_to_json(car_record, current_date)
        
        # Save to CSV
        self._save_to_csv(car_record)
        
        print(f"BCA car data saved successfully:")
        print(f"- JSON: {self.json_file}")
        print(f"- CSV: {self.csv_file}")
        print(f"- Vehicle: {min_year}-{max_year} {make} {model} {variant}")
        print(f"- Profit margins: Lower: {stats['lower_profit_percent']:.2f}%, Mean: {stats['mean_profit_percent']:.2f}%, Upper: {stats['upper_profit_percent']:.2f}%")
    
    def _save_to_json(self, car_record, current_date):
        """Save data to JSON file"""
        try:
            # Load existing data if file exists
            json_data = {}
            if os.path.exists(self.json_file):
                try:
                    with open(self.json_file, 'r') as f:
                        json_data = json.load(f)
                except json.JSONDecodeError:
                    json_data = {}
            
            # Create unique key for this car record
            vehicle_key = f"{current_date}_{car_record['make']}_{car_record['model']}_{car_record['variant']}_{car_record['engine_size']}L"
            json_data[vehicle_key] = car_record
            
            # Save back to file
            with open(self.json_file, 'w') as f:
                json.dump(json_data, f, indent=4)
                
        except Exception as e:
            print(f"Error saving to JSON: {e}")
    
    def _save_to_csv(self, car_record):
        """Save data to CSV file"""
        # Define CSV headers
        csv_headers = [
            'timestamp', 'make', 'model', 'variant', 'cap_price', 'min_year', 'max_year',
            'engine_size', 'avg_mileage', 'input_mileage', 'fuel_type', 'doors', 
            'transmission', 'mean_price', 'lower_std_price', 'upper_std_price',
            'lower_profit_percent', 'mean_profit_percent', 'upper_profit_percent', 'sample_size'
        ]
        
        try:
            # Check if file exists to determine if we need headers
            file_exists = os.path.exists(self.csv_file)
            
            with open(self.csv_file, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=csv_headers)
                
                # Write header if file doesn't exist
                if not file_exists:
                    writer.writeheader()
                
                # Prepare row data (exclude lists that aren't suitable for CSV)
                csv_row = {key: value for key, value in car_record.items() 
                          if key in csv_headers}
                
                writer.writerow(csv_row)
                
        except Exception as e:
            print(f"Error saving to CSV: {e}")        

def main():
    scraper = CarScraper()

    car_data, make, model, variant, cap_price, min_year, max_year, engine_size, avg_mileage, mileages, input_mileage, fuel_type, doors, transmission = scraper.run()

    print(f"Total number of cars extracted: {len(car_data)}")

    price_extractor = PriceExtractor()
    extracted_prices = price_extractor.extract_price(car_data)

    # Save BCA car data with profit margins - ADD THESE LINES
    bca_saver = BCACarDataSaver()
    bca_saver.save_bca_car_data(make, model, variant, cap_price, min_year, max_year, 
                               engine_size, avg_mileage, mileages, input_mileage, 
                               fuel_type, doors, transmission, extracted_prices)

    plotter = PricePlotter()
    
    # Use the new combined plot instead of separate plots
    plotter.plot_combined_analysis(extracted_prices, mileages, cap_price, input_mileage, 
                                   make, model, variant, engine_size, min_year, max_year, fuel_type, doors, transmission)
    
    # Ensure data is saved even if plotting fails
    plotter.save_results(extracted_prices, mileages, cap_price, input_mileage, 
                         make, model, variant, engine_size, min_year, max_year, fuel_type, doors, transmission)
if __name__ == "__main__":
    main()