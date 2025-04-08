import pytest
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Use environment variable to determine the application URL
# In local Docker network, use service name; for CI, use localhost
APP_URL = os.environ.get("APP_URL", "http://womsoft:8000")

class TestEntryForm:
    @pytest.fixture(scope="function")
    def driver(self):
        # Setup Chrome options for headless browser
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Create a new ChromeDriver instance
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.implicitly_wait(10)
        
        yield driver
        
        # Teardown
        driver.quit()
    
    def test_entry_form_submission(self, driver):
        """
        Test the entry form submission process:
        1. Log in
        2. Navigate to the entry form
        3. Fill out the form
        4. Submit the form
        5. Verify redirection to dashboard
        6. Verify the new entry appears in the dashboard
        """
        # 1. Login to the application
        driver.get(f"{APP_URL}/")
        
        # Fill in login credentials
        driver.find_element(By.ID, "username").send_keys("admin")
        driver.find_element(By.ID, "password").send_keys("admin")
        driver.find_element(By.ID, "login-form").submit()
        
        # Wait for dashboard to load
        WebDriverWait(driver, 10).until(
            EC.url_to_be(f"{APP_URL}/dashboard")
        )
        
        # 2. Navigate to entry form
        driver.find_element(By.LINK_TEXT, "New Entry").click()
        
        # Wait for form to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "diagnostic-form"))
        )
        
        # 3. Fill out the form with test data
        test_id = f"TEST-SELENIUM-{int(time.time())}"
        test_agrin = "1.23"
        test_timp2 = "2.34"
        test_mmp9 = "3.45"
        
        driver.find_element(By.ID, "identifier").send_keys(test_id)
        driver.find_element(By.ID, "agrin").send_keys(test_agrin)
        driver.find_element(By.ID, "timp2").send_keys(test_timp2)
        driver.find_element(By.ID, "mmp9").send_keys(test_mmp9)
        
        # 4. Submit the form
        driver.find_element(By.ID, "diagnostic-form").submit()
        
        # Wait for success message
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "success-message"))
        )
        
        # 5. Verify redirection to dashboard (happens after delay)
        WebDriverWait(driver, 15).until(
            EC.url_to_be(f"{APP_URL}/dashboard")
        )
        
        # 6. Verify the new entry is visible in the table
        # Wait for the table to load/refresh
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "diagnostics-table-body"))
        )
        
        # Get the table body HTML
        table_html = driver.find_element(By.ID, "diagnostics-table-body").get_attribute("innerHTML")
        
        # Assert that our test identifier is in the table
        assert test_id in table_html, f"New entry with ID {test_id} not found in dashboard table"
        
        # Verify the values are in the table
        assert test_agrin in table_html, f"Agrin value {test_agrin} not found in dashboard table"
        assert test_timp2 in table_html, f"TIMP2 value {test_timp2} not found in dashboard table"
        assert test_mmp9 in table_html, f"MMP9 value {test_mmp9} not found in dashboard table"
        assert "Positive" in table_html, "Result 'Positive' not found in dashboard table"