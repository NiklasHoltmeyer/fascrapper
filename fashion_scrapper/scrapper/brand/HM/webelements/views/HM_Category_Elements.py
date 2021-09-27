from time import sleep
from selenium.webdriver.common.action_chains import ActionChains

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from scrapper.brand.hm.webelements.consts.HM_Selectors import HM_Selectors
from scrapper.util.web.dynamic import driver as d_driver
from scrapper.util.web.dynamic import scroll_end_of_page
from scrapper.util.web.dynamic import wait
from selenium.webdriver.common.keys import Keys


class HM_Category_Elements:
    """ List all Links/Images withing an Category (e.g. T-Shirts) """

    def __init__(self, web_elements):
        self.driver = web_elements.driver
        self.logger = web_elements.logger

    def list_category(self, url, PAGINATE=True):
        html = self._load_html(url, PAGINATE=PAGINATE)
        items = html.find_all("li", {"class": "product-item"})
        get_href = lambda item: HM_Selectors.URLS.BASE + item.find(href=True)["href"]
        to_dict = lambda href: {"id": href, "url": href}
        items = map(get_href, items)
        items = map(to_dict, items)
        return list(items)

    def _load_html(self, url, PAGINATE=True):
        self.driver.get(url)
        wait(self.driver, EC.presence_of_element_located((By.ID, "page-content")))
        scroll_end_of_page(self.driver)

        if PAGINATE:
            self.paginate_all_products()

        container_html = self.driver.find_element_by_id("page-content").get_attribute("innerHTML")
        container = BeautifulSoup(container_html, 'html.parser')
        return container

    def paginate_all_products(self):
        def click(btn):
            try:
#                self.driver.execute_script("arguments[0].scrollIntoView(true);", btn)
                ActionChains(self.driver).move_to_element(btn).click(btn).perform()
                btn.scrollIntoView()
            except:
                pass

        while load_more_btn_s := self._load_more_button():
            scroll_end_of_page(self.driver)
            [load_more_btn_s[0].send_keys(Keys.ARROW_UP) for i in range(15)]
            sleep(0.1)
            #ActionChains(self.driver).move_to_element(load_more_btn).click(load_more_btn).perform()
            list(map(click, load_more_btn_s))

            sleep(0.2)

        scroll_end_of_page(self.driver, SCROLL_TOP=True)
        scroll_end_of_page(self.driver)

    def _load_more_button(self):

        value, max = self._load_progress_bar_progress()
        value, max = int(value), int(max)

#        self.logger.debug(f"{value} / {max} = {value / max}%")

        if max <= value:
            return None

        more_btn = self.driver.find_elements_by_css_selector("button.js-load-more")
        if len(more_btn) > 0:
            return more_btn
        else:
            raise Exception("Cant Locate Load More Button and Progress != 100%")

    def _load_progress_bar_progress(self):
        progress_bar = self.driver.find_element_by_css_selector(".load-more-products>h2.load-more-heading")
        value = progress_bar.get_attribute("data-items-shown")
        max = progress_bar.get_attribute("data-total")
        return value, max

if __name__ == "__main__":
    with d_driver(headless=False) as driver:
        items = HM_Category_Elements(driver=driver, logger=None).list_category("https://www2.hm.com/de_de/herren/produkte/schuhe.html?sort=stock&image-size=small&image=model&offset=0&page-size=180")
        print(items)