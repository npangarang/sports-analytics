from selenium.webdriver.chrome.options import Options

# Headless selenium configs

SELENIUM_CONFIGS = Options()
SELENIUM_CONFIGS.add_argument("--headless")  # ensure GUI is off
SELENIUM_CONFIGS.add_argument("--no-sandbox")  # bypass OS security model
SELENIUM_CONFIGS.add_argument("--disable-dev-shm-usage") # surpass limited resource problems