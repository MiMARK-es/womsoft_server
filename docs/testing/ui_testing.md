# UI Testing

This document describes the UI testing approach for the WomSoft Server application.

## Overview

UI tests verify that the user interface works correctly from an end-user perspective. These tests simulate user interactions with the web interface and validate expected behaviors.

## Technology Stack

- **Testing Framework**: pytest
- **Browser Automation**: Selenium WebDriver
- **Browser**: Chrome (in headless mode for CI)
- **Test Runner**: pytest-selenium
- **Visual Testing**: Screenshots comparison
- **Container**: Selenium Grid Docker container

## Directory Structure

UI tests are organized in the `tests/ui` directory:

```
tests/ui/
├── conftest.py              # Test fixtures and setup
├── page_objects/            # Page Object Model classes
│   ├── base_page.py         # Base page class
│   ├── login_page.py        # Login page interactions
│   ├── dashboard_page.py    # Dashboard page interactions
│   └── diagnostic_page.py   # Diagnostic form page interactions
├── test_authentication.py   # Tests for login/logout flows
├── test_navigation.py       # Tests for navigation between pages
└── test_diagnostics.py      # Tests for diagnostic form submission
```

## Page Object Pattern

UI tests use the Page Object Model pattern to separate test logic from page interaction details:

``` python
class LoginPage:
    def __init__(self, driver):
        self.driver = driver
        self.url = "http://localhost:8000/login"
        
    def navigate(self):
        self.driver.get(self.url)
        return self
        
    def login(self, username, password):
        self.driver.find_element(By.ID, "username").send_keys(username)
        self.driver.find_element(By.ID, "password").send_keys(password)
        self.driver.find_element(By.ID, "login-button").click()
        
    def get_error_message(self):
        return self.driver.find_element(By.CLASS_NAME, "error-message").text
        
    def is_login_page(self):
        return "Login" in self.driver.title
```

## Selenium Test Fixtures

Set up WebDriver instance for tests:

``` python
@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1920, 1080)
    
    yield driver
    
    driver.quit()

@pytest.fixture
def login_page(driver):
    return LoginPage(driver)

@pytest.fixture
def authenticated_driver(driver):
    login_page = LoginPage(driver)
    login_page.navigate()
    login_page.login("testuser", "password123")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "dashboard"))
    )
    return driver
```

## Basic UI Test Examples

### Login Tests

``` python
def test_successful_login(login_page):
    login_page.navigate()
    login_page.login("testuser", "password123")
    
    dashboard = DashboardPage(login_page.driver)
    assert dashboard.is_dashboard_page()
    assert dashboard.get_welcome_message() == "Welcome, testuser!"

def test_failed_login(login_page):
    login_page.navigate()
    login_page.login("testuser", "wrongpassword")
    
    assert login_page.is_login_page()
    assert "Invalid username or password" in login_page.get_error_message()
```

### Navigation Tests

``` python
def test_navigation_between_pages(authenticated_driver):
    dashboard = DashboardPage(authenticated_driver)
    
    # Navigate to diagnostics page
    diagnostic_page = dashboard.navigate_to_diagnostics()
    assert diagnostic_page.is_diagnostic_page()
    
    # Navigate back to dashboard
    dashboard = diagnostic_page.navigate_to_dashboard()
    assert dashboard.is_dashboard_page()
```

### Form Submission Tests

``` python
def test_diagnostic_form_submission(authenticated_driver):
    # Navigate to the diagnostic form
    dashboard = DashboardPage(authenticated_driver)
    diagnostic_page = dashboard.navigate_to_diagnostics()
    
    # Fill and submit the form
    result_page = diagnostic_page.submit_diagnostic_form(
        patient_id="P12345",
        age=45,
        gender="Female",
        protein1=1.2,
        protein2=3.4,
        protein3=5.6
    )
    
    # Verify the result page
    assert result_page.is_result_page()
    assert "Diagnostic Result" in result_page.get_page_title()
    assert result_page.get_result_value() in ["Positive", "Negative", "Borderline"]
```

## Testing Responsive Design

Test the UI at different viewport sizes:

``` python
@pytest.mark.parametrize("viewport", [
    (1920, 1080),  # Desktop
    (768, 1024),   # Tablet
    (375, 812),    # Mobile
])
def test_responsive_design(driver, viewport, login_page):
    width, height = viewport
    driver.set_window_size(width, height)
    
    login_page.navigate()
    
    if width < 768:
        # Check mobile menu is present
        assert login_page.is_mobile_menu_visible()
    else:
        # Check desktop navigation is present
        assert login_page.is_desktop_nav_visible()
```

## Visual Regression Testing

Capture and compare screenshots to detect visual changes:

``` python
def test_dashboard_visual(authenticated_driver):
    dashboard = DashboardPage(authenticated_driver)
    dashboard.navigate()
    
    # Wait for page to fully load
    time.sleep(1)
    
    # Take screenshot
    screenshot = authenticated_driver.get_screenshot_as_png()
    
    # Compare with baseline (simplified example)
    baseline = get_baseline_screenshot("dashboard.png")
    assert compare_screenshots(screenshot, baseline) > 0.95  # 95% similarity
```

## Running UI Tests

UI tests can be run in different environments:

### Local Development

```
pytest tests/ui/ -v
```

### Docker Environment

```
docker-compose -f docker-compose.selenium.yml up -d
pytest tests/ui/ --driver Remote --capability browserName chrome --host chrome
```

### Watch Tests Execute

To visually observe test execution in real-time:

1. Start Selenium with VNC:

```
   docker-compose -f docker-compose.selenium-debug.yml up -d
```

2. Connect to VNC:
   - VNC Viewer: localhost:5900
   - Web VNC: http://localhost:7900 (password: secret)

3. Run tests:

```
   pytest tests/ui/ --driver Remote --capability browserName chrome --host chrome
```

## Test Data Management

UI tests require data setup and teardown:

``` python
@pytest.fixture
def setup_test_data():
    # Create test users
    create_test_user("testuser", "password123")
    
    # Create test patients
    create_test_patient("P12345")
    
    yield
    
    # Clean up
    delete_test_user("testuser")
    delete_test_patient("P12345")
```

## Critical User Journeys

These critical user journeys must be covered by UI tests:

1. **User Authentication**
   - Login with valid credentials
   - Attempt login with invalid credentials
   - Password reset flow
   - Logout

2. **Diagnostic Workflow**
   - Submit new diagnostic data
   - Review diagnostic result
   - Download diagnostic report

3. **User Management** (Admin only)
   - Create new user
   - Edit user details
   - Disable user account

## Handling Dynamic Elements

Strategies for dealing with dynamic elements:

- Use explicit waits:

```
  WebDriverWait(driver, 10).until(
      EC.element_to_be_clickable((By.ID, "submit-button"))
  )
```

- Use stable selectors (prefer IDs and data-testid attributes)
- Add stability hooks in frontend code for testing

## Integration with CI/CD

UI tests are integrated into the CI/CD pipeline:

- Run after successful integration tests
- Scheduled runs daily on main branch
- Screenshots of failures stored as artifacts
- Test reports published as pipeline results

## Related QMS Documents

- UI Test Plan: <!-- TODO: Add document ID -->
- User Journey Validation: <!-- TODO: Add document ID -->

## Version History

| Version | Date | Description | Author |
|---------|------|-------------|--------|
| 1.0 | <!-- TODO: Add date --> | Initial UI testing guidelines | <!-- TODO: Add author --> |