import pytest
import time
import os
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Add the pytest marker decorator
pytestmark = pytest.mark.selenium

# Use environment variables for configuration
APP_URL = os.environ.get("APP_URL", "http://womsoft:8000")
SELENIUM_URL = os.environ.get("SELENIUM_REMOTE_URL", "http://chrome:4444/wd/hub")

class TestAuditLogsUI:
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
        driver.set_window_size(1920, 1080)
        
        yield driver
        
        # Save screenshot on failure
        try:
            driver.save_screenshot("/app/screenshots/audit_logs_error.png")
            with open("/app/screenshots/audit_logs_page_source.html", "w") as f:
                f.write(driver.page_source)
        except Exception as e:
            print(f"Could not save screenshot: {e}")
        
        # Teardown
        driver.quit()
    
    def test_admin_can_access_audit_logs(self, driver, admin_user):
        """Test that admin users can access the audit logs page"""
        # 1. Login as admin
        driver.get(f"{APP_URL}/")
        print(f"Opened URL: {APP_URL}")
        
        # Fill in admin credentials
        driver.find_element(By.ID, "username").send_keys("adminuser")
        driver.find_element(By.ID, "password").send_keys("admin123")
        driver.find_element(By.ID, "login-form").submit()
        print("Submitted login form")
        
        # Wait for dashboard to load
        WebDriverWait(driver, 10).until(
            EC.url_to_be(f"{APP_URL}/dashboard")
        )
        print(f"Dashboard loaded: {driver.current_url}")
        
        # Take a screenshot
        driver.save_screenshot("/app/screenshots/admin_dashboard.png")
        
        # 2. Wait for the admin navigation item to appear
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "nav-audit"))
        )
        print("Audit logs nav item is visible")
        
        # 3. Click on the Audit Logs link
        driver.find_element(By.ID, "nav-audit").click()
        print("Clicked on Audit Logs link")
        
        # 4. Verify redirect to audit logs page
        WebDriverWait(driver, 10).until(
            EC.url_to_be(f"{APP_URL}/admin/audit")
        )
        print(f"Audit logs page loaded: {driver.current_url}")
        
        # Save screenshot of audit logs page
        driver.save_screenshot("/app/screenshots/audit_logs_page.png")
        
        # 5. Verify page elements
        assert "Audit Logs" in driver.title or "Audit Logs" in driver.page_source
        
        # Check that the filter form exists
        filter_form = driver.find_element(By.ID, "filter-form")
        assert filter_form is not None
        
        # Check that the audit logs table exists
        audit_table = driver.find_element(By.ID, "audit-logs-table-body")
        assert audit_table is not None
    
    def test_audit_logs_filtering(self, driver, admin_user):
        """Test that audit logs filtering works correctly"""
        # 1. Login as admin
        driver.get(f"{APP_URL}/")
        driver.find_element(By.ID, "username").send_keys("adminuser")
        driver.find_element(By.ID, "password").send_keys("admin123")
        driver.find_element(By.ID, "login-form").submit()
        
        # Wait for dashboard to load
        WebDriverWait(driver, 10).until(
            EC.url_to_be(f"{APP_URL}/dashboard")
        )
        
        # 2. Go to audit logs page
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "nav-audit"))
        )
        driver.find_element(By.ID, "nav-audit").click()
        
        WebDriverWait(driver, 10).until(
            EC.url_to_be(f"{APP_URL}/admin/audit")
        )
        
        # 3. Generate some login activity to ensure logs exist
        # First logout
        driver.find_element(By.ID, "logout-btn").click()
        
        # Wait for login page
        WebDriverWait(driver, 10).until(
            EC.url_to_be(f"{APP_URL}/")
        )
        
        # Login again
        driver.find_element(By.ID, "username").send_keys("adminuser")
        driver.find_element(By.ID, "password").send_keys("admin123")
        driver.find_element(By.ID, "login-form").submit()
        
        # Wait for dashboard
        WebDriverWait(driver, 10).until(
            EC.url_to_be(f"{APP_URL}/dashboard")
        )
        
        # Go back to audit logs
        driver.find_element(By.ID, "nav-audit").click()
        
        # 4. Test filtering by action
        action_input = driver.find_element(By.ID, "action")
        action_input.clear()
        action_input.send_keys("login_success")
        
        # Submit filter form
        driver.find_element(By.ID, "filter-form").submit()
        print("Applied filter for login_success actions")
        
        # Wait for table to refresh
        time.sleep(2)  # Give JavaScript time to update the table
        
        # Check table contains login_success actions
        table_html = driver.find_element(By.ID, "audit-logs-table-body").get_attribute("innerHTML")
        assert "login_success" in table_html, "Table should show login_success actions after filtering"
        
        # Take screenshot of filtered results
        driver.save_screenshot("/app/screenshots/audit_logs_filtered.png")
        
        # 5. Check pagination info updated
        pagination_info = driver.find_element(By.ID, "pagination-info").text
        assert "Showing page" in pagination_info, "Pagination info should update after filtering"