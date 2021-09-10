import time

from selenium.webdriver.support.ui import WebDriverWait


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
