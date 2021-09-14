from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import Chrome
import time
import selenium.webdriver
import logging

def wait(driver, condition, timeout=10):
    driver_wait = WebDriverWait(driver, timeout)
    element = driver_wait.until(condition)

    return element


def scroll_end_of_page(driver, scroll_pause_time=0.5, SCROLL_TOP=False):
    # Src: https://stackoverflow.com/a/27760083

    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(scroll_pause_time)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    if SCROLL_TOP:
        driver.execute_script("window.scroll({top: 0,left: 0,behavior: 'smooth'});")

def driver(path = "C:\selenium\chromedriver.exe"):
    selenium_logger = logging.getLogger('selenium.webdriver.remote.remote_connection')
    selenium_logger.setLevel(logging.WARNING)

    chrome_options = selenium.webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    # chrome_options.add_argument('--incognito')
    chrome_options.add_argument('log-level=3')
    chrome_options.add_argument('--disable-dev-shm-usage')

    driver = Chrome(path, options=chrome_options, service_args=["--quiet"])
    driver.maximize_window()
    return driver
