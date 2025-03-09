import undetected_chromedriver as uc
from django.conf import settings
import platform
from selenium_stealth import stealth

os_type = platform.system()
chromedriver="chromedriver.exe" if os_type == 'Windows' else 'chromedriver'
browser = "chrome-win64/chrome.exe"
validating_urls=['Streaming','streaming', 'saison', 'Saison', 'vf hd', 'Complet HD']
run_in_background=False
use_subprocess=True

def init_driver():
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.140 Safari/537.36"
    chrome_options = uc.ChromeOptions()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("user-agent={}".format(user_agent))
    driver = uc.Chrome(
        options=chrome_options,
        use_subprocess=use_subprocess,
        headless=run_in_background,
        #driver_executable_path= str(settings.BASE_DIR / chromedriver),
        browser_executable_path= str(settings.BASE_DIR / browser),
    )
    stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True
    )
    return driver

def wait_until_title_contains(driver, wait):
    wait.until(lambda driver: any(match in driver.title for match in validating_urls))
