import undetected_chromedriver as uc
from django.conf import settings
import platform
from selenium_stealth import stealth

os_type = platform.system()
chromedriver="chromedriver.exe" if os_type == 'Windows' else 'chromedriver'
browser = "chrome-win64/chrome.exe"
validating_urls=['Streaming','streaming', 'saison', 'Saison', 'vf hd', 'Complet HD']
run_in_background=True
use_subprocess=True

def init_driver():
    chrome_options = uc.ChromeOptions()
    chrome_options.headless=run_in_background
    chrome_options.add_argument('--headless')
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-logging")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument("--window-size=800,600")
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    chrome_options.add_argument(f"--user-agent={user_agent}")
    driver = uc.Chrome(
        options=chrome_options,
        use_subprocess=use_subprocess,
        #headless=run_in_background
        #driver_executable_path= str(settings.BASE_DIR / chromedriver),
        browser_executable_path= str(settings.BASE_DIR / browser),
    )
    stealth(
        driver,
        languages=["en-US", "en"],  # Set preferred languages
        vendor="Google Inc.",  # Set vendor
        platform="Win32",  # Set platform
        webgl_vendor="Intel Inc.",  # Set WebGL vendor
        renderer="Intel Iris OpenGL Engine",  # Set WebGL renderer
        fix_hairline=True,  # Fix hairline rendering
        run_on_insecure_origins=True,  # Allow running on insecure origins
    )
    return driver

def wait_until_title_contains(driver, wait):
    wait.until(lambda driver: any(match in driver.title for match in validating_urls))
