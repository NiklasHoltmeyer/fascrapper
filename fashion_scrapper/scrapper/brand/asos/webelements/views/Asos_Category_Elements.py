from time import sleep

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from scrapper.brand.asos.webelements.consts.Asos_Selectors import Asos_Selectors
from scrapper.util.web.dynamic import wait, scroll_end_of_page
from bs4 import BeautifulSoup

class Asos_Category_Elements:
    """ List all Links/Images withing an Category (e.g. T-Shirts) """

    def __init__(self, driver, logger):#web_elements):
        #self.elements = web_elements
        #self.driver = web_elements.driver
        #self.logger = web_elements.logger
        self.driver = driver
        self.logger = logger

    def list_category(self, url, PAGINATE=True):
        html = self._load_html(url, PAGINATE=PAGINATE)

        items = html.find_all("article", {"data-auto-id": "productTile"})

        def parse_item(item):
            return {
                "id": item["id"], "url": item.find("a", href=True)["href"]
            }

        items_parsed = [parse_item(item) for item in items]
        return items_parsed

    def _load_html(self, url, PAGINATE=True):
        self.driver.get(url)
        wait(self.driver, EC.presence_of_element_located((By.ID, Asos_Selectors.ID.MAIN_CONTENT)))

        if PAGINATE:
            self.paginate_all_products()
        container_html = self.driver.find_element_by_id("plp").get_attribute("innerHTML")
        container = BeautifulSoup(container_html, 'html.parser')
        return container

    def paginate_all_products(self):
        load_btn = self._load_more_button()

        def wait_for_button():
            while not load_btn.get_attribute("data-auto-id") == "loadMoreProducts":
                sleep(0.5)

        try:
            while True:
                wait_for_button()
                scroll_end_of_page(self.driver)
                load_btn.click()
                sleep(0.25)
        except StaleElementReferenceException:
            pass

        scroll_end_of_page(self.driver, SCROLL_TOP=True)
        scroll_end_of_page(self.driver)

    def _load_more_button(self):
        all_as = list(self.driver.find_element_by_id("plp").find_elements_by_tag_name("a"))
        more_btn = [a for a in reversed(all_as) if "LOAD" in a.text]
        #assert len(more_btn) == 1, len(more_btn)
        return more_btn[0]

