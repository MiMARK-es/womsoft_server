import pytest
import time
import os
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Use environment variables for configuration
APP_URL = os.environ.get("APP_URL", "http://womsoft:8000")
SELENIUM_URL = os.environ.get("SELENIUM_REMOTE_URL", "http://chrome:4444/wd/hub")

class TestEntryForm:
    @pytest.fixture(scope="function")
    def driver(self):
        # Setup Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.set_capability("goog:loggingPrefs", {"browser": "ALL"})
        
        # Create a remote WebDriver
        driver = webdriver.Remote(
            command_executor=SELENIUM_URL,
            options=chrome_options
        )
        driver.implicitly_wait(10)
        driver.set_window_size(1920, 1080)  # Make browser larger for better visibility
        
        yield driver
        
        # Write browser logs for debugging
        try:
            print("Browser logs:")
            for log in driver.get_log('browser'):
                print(json.dumps(log))
        except Exception as e:
            print(f"Could not get browser logs: {e}")
            
        # Save screenshot on failure
        try:
            driver.save_screenshot("/app/screenshots/error_screenshot.png")
            print("Screenshot saved as error_screenshot.png")
            
            # Print page source for debugging
            with open("/app/page_source.html", "w") as f:
                f.write(driver.page_source)
            print("Page source saved as page_source.html")
        except Exception as e:
            print(f"Could not save screenshot: {e}")
        
        # Teardown
        driver.quit()
    
    def test_entry_form_submission(self, driver):
        """
        Test the entry form submission process
        """
        # 1. Login to the application
        driver.get(f"{APP_URL}/")
        print(f"Opened URL: {APP_URL}")
        
        # Fill in login credentials
        driver.find_element(By.ID, "username").send_keys("admin")
        driver.find_element(By.ID, "password").send_keys("admin")
        driver.find_element(By.ID, "login-form").submit()
        print("Submitted login form")
        
        # Wait for dashboard to load
        WebDriverWait(driver, 10).until(
            EC.url_to_be(f"{APP_URL}/dashboard")
        )
        print(f"Dashboard loaded: {driver.current_url}")
        
        # Save a screenshot for debugging
        driver.save_screenshot("/app/screenshots/dashboard.png")
        print("Saving dashboard screenshot")
        
        # 2. Navigate to entry form - try with more robust selectors
        # First try: Wait for the navigation to be visible and check what's available
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "navbar"))
        )
        print("Navbar found")
        
        # Try different ways to find the link
        try:
            # Try finding by CSS selector (more robust)
            entry_link = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='/entry']"))
            )
            print("Found entry link by URL")
            entry_link.click()
        except Exception as e:
            print(f"Could not find by CSS selector: {e}")
            try:
                # Try finding by partial link text
                entry_link = driver.find_element(By.PARTIAL_LINK_TEXT, "New")
                print("Found entry link by partial text")
                entry_link.click()
            except Exception as e:
                print(f"Could not find by partial text: {e}")
                # Last resort - try to navigate directly to the URL
                print("Navigating directly to entry form URL")
                driver.get(f"{APP_URL}/entry")
        
        print("Navigated to entry form")
        
        # Wait for form to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "diagnostic-form"))
        )
        print("Entry form loaded")
        
        # Save a screenshot of the form
        driver.save_screenshot("/app/screenshots/entry_form.png")
        
        # 3. Fill out the form with test data
        test_id = f"TEST-SELENIUM-{int(time.time())}"
        test_agrin = "1.23"
        test_timp2 = "2.34"
        test_mmp9 = "3.45"
        
        driver.find_element(By.ID, "identifier").send_keys(test_id)
        driver.find_element(By.ID, "agrin").send_keys(test_agrin)
        driver.find_element(By.ID, "timp2").send_keys(test_timp2)
        driver.find_element(By.ID, "mmp9").send_keys(test_mmp9)
        print(f"Filled form with ID: {test_id}, values: {test_agrin}, {test_timp2}, {test_mmp9}")
        
        # 4. Submit the form
        driver.find_element(By.ID, "diagnostic-form").submit()
        print("Form submitted")
        
        # Wait for success message
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "success-message"))
        )
        print("Success message appeared")
        
        # 5. Verify redirection to dashboard (happens after delay)
        WebDriverWait(driver, 15).until(
            EC.url_to_be(f"{APP_URL}/dashboard")
        )
        print(f"Redirected to dashboard: {driver.current_url}")
        
        # 6. Verify the new entry is visible in the table
        # Wait for the table to load/refresh
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "diagnostics-table-body"))
        )
        
        # Get the table body HTML
        table_html = driver.find_element(By.ID, "diagnostics-table-body").get_attribute("innerHTML")
        
        # Assert that our test identifier is in the table
        assert test_id in table_html, f"New entry with ID {test_id} not found in dashboard table"
        print(f"Found test ID {test_id} in table")
        
        # Verify the values are in the table
        assert test_agrin in table_html, f"Agrin value {test_agrin} not found in dashboard table"
        assert test_timp2 in table_html, f"TIMP2 value {test_timp2} not found in dashboard table"
        assert test_mmp9 in table_html, f"MMP9 value {test_mmp9} not found in dashboard table"
        assert "Positive" in table_html, "Result 'Positive' not found in dashboard table"
        print("All values verified in dashboard table")