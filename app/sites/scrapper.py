import undetected_chromedriver as uc
from django.conf import settings
import platform

os_type = platform.system()
chromedriver="chromedriver.exe" if os_type == 'Windows' else 'chromedriver'
validating_urls=['Streaming','streaming', 'saison', 'Saison', 'vf hd', 'Complet HD']
run_in_background=False
use_subprocess=True

def init_driver():
    driver = uc.Chrome(
        use_subprocess=use_subprocess,
        headless=run_in_background,
        #driver_executable_path= str(settings.BASE_DIR / chromedriver)
    )
    return driver

def wait_until_title_contains(driver, wait):
    wait.until(lambda driver: any(match in driver.title for match in validating_urls))