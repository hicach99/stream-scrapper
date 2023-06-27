import undetected_chromedriver as uc

validating_urls=['Streaming','streaming', 'saison', 'Saison', 'vf hd', 'Complet HD']
run_in_background=True
use_subprocess=True

def init_driver():

    driver = uc.Chrome(use_subprocess=use_subprocess,headless=run_in_background,driver_executable_path="chromedriver.exe")
    return driver

def wait_until_title_contains(driver, wait):
    wait.until(lambda driver: any(match in driver.title for match in validating_urls))