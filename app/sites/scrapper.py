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
    chrome_options = uc.ChromeOptions()
    if run_in_background: chrome_options.add_argument('--headless')
    chrome_options.add_argument('--load-extension='+str(settings.BASE_DIR / 'ublock.crx'))
    chrome_options.add_argument('--load-extension='+str(settings.BASE_DIR / 'vpn.crx'))
    chrome_options.add_argument("--start-maximized")
    driver = uc.Chrome(
        options=chrome_options,
        use_subprocess=use_subprocess,
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
