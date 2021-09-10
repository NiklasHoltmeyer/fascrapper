import time

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from util.web.dynamic import wait, scroll_end_of_page


class _WebElements:
    """ HTML Elements """

    def __init__(self, driver, logger, LOAD_VIEW_ELEMENTS=True):
        self.driver = driver
        self.selectors = _Mango_Selectors()
        self.logger = logger

        if LOAD_VIEW_ELEMENTS:
            self.category = _Mango_Category_Elements(driver, logger)
            self.categories = _Mango_Categories_Elements(driver, logger)

    def header(self):
        header = self.driver.find_elements_by_css_selector("header")
        assert len(header) != 0
        headerHTML = header[0].get_attribute("outerHTML")
        doc = BeautifulSoup(headerHTML, "html.parser")

        return doc

    def accept_cookies(self):
        wait(self.driver, EC.element_to_be_clickable((By.ID, self.selectors.ID.CHANGE_VIEW_COLUMNS))).click()
        try:
            self.driver.find_element_by_id(self.selectors.ID.ACCEPT_COOKIES).click()  # Cookies
        except Exception as e:
            raise e


class _Mango_Selectors:
    class ID:
        CHANGE_VIEW_COLUMNS = 'navColumns4'  # ID to Change View from 2 to 4 Columns
        ACCEPT_COOKIES = "onetrust-accept-btn-handler"
        HEADER = "header"


class _Mango_Global_Elements:
    def __init__(self, driver):
        self.driver = driver


class _Mango_Category_Elements:
    """ List all Links/Images withing an Category (T-Shirts) """

    def __init__(self, driver, logger):
        self.driver = driver
        self.elements = _WebElements(driver, logger=logger, LOAD_VIEW_ELEMENTS=False)
        self.logger = logger

    def load_html(self, url, timeout=1.5):
        self.driver.get(url)

        wait(self.driver, EC.presence_of_element_located((By.ID, 'app')))

        self.elements.accept_cookies()

        last_article_count = -1

        while True:  # Scroll as Long as new Content is Loaded
            scroll_end_of_page(self.driver, SCROLL_TOP=True)

            catalog = self.driver.find_elements_by_css_selector("#app>.catalog")
            catalog_flattend = "\n".join([x.get_attribute('innerHTML') for x in catalog])

            if last_article_count == len(catalog_flattend):
                return catalog_flattend
            else:
                last_article_count = len(catalog_flattend)
                time.sleep(timeout)

    def list_images(self, url):
        self.logger.debug("Loading: ", url)

        html = self.load_html(url)

        doc = BeautifulSoup(html, "html.parser")
        article_imgs = doc.findAll("img", attrs={'class': 'product'})

        return article_imgs


class _Mango_Categories_Elements:
    """ List all Categories withing an Category ()
        Top-(Level)-Categories: Male, Female, ...
        Sub-Categories: T-Shirt, Shorts, ...
    """

    def __init__(self, driver, logger):
        self.driver = driver
        self.elements = _WebElements(driver, logger=logger, LOAD_VIEW_ELEMENTS=False)
        self.logger = logger

    def load_sub_categories(self, url):
        self.logger.debug("Loading Sub Category", url)
        self.driver.get(url)
        header = self.elements.header()
        hrefs = header.find_all(href=True)
        hrefs = [{'href': href["href"], "text": href.text} for href in hrefs]
        cat_top, cat_sub = [], []

        for href in hrefs:
            if (len(href["href"].split("/"))) == 5:
                cat_top.append(href)
            else:
                cat_sub.append(href)

        assert len(hrefs) == len(cat_top) + len(cat_sub)

        return cat_top, cat_sub

    def list_categories(self, url):
        visited_links = []
        urls = [url]
        categories = []

        while len(urls) > 0:
            url = urls.pop()
            cat_top, cat_sub = self.load_sub_categories(url)
            visited_links.append(url)

            categories.extend(cat_top)
            categories.extend(cat_sub)

            for x in cat_top:
                if not x["href"] in visited_links:
                    urls.append(x["href"])

        return categories
