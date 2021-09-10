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
            self.article = _Mango_Article_Elements(driver, logger)

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

    class URLS:
        BASE = "https://shop.mango.com"
        LANGUAGE = "de"



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

class _Mango_Article_Elements:
    """
    Parse Show-Page
    """
    def __init__(self, driver, logger):
        self.driver = driver
        self.elements = _WebElements(driver, logger=logger, LOAD_VIEW_ELEMENTS=False)
        self.logger = logger

        ##self.data = {}

    def show(self, url):
        doc = self._load_html(url)

        def _parse_price(price):
            _price = price.split(" ")
            return {"value": _price[0], "currency": _price[1]}

        return {
            "name": doc.find(class_="product-name").text,
            "color": doc.find(class_="colors-info-name").text,
            "price": _parse_price(doc.find(class_="product-sale").text),
            "images": self._list_item_images(doc),
            "related_items": self._list_related_items(doc)
        }

    def _load_html(self, url):
        self.driver.get(url)
        wait(self.driver, EC.presence_of_element_located((By.ID, "renderedImages")))
        scroll_end_of_page(self.driver, SCROLL_TOP=True)

        container = self.driver.find_element(By.CLASS_NAME, "main-contentContainer")
        container_html = container.get_attribute('innerHTML')

        return BeautifulSoup(container_html, "html.parser")

    def _list_item_images(self, doc):
        """ List/Parse Images of Pivot-Item """

        def parse_show_image(image_element):
            """ Parse HTML-Attrs. for a Single Show-Image """
            return {
                "description": image_element["alt"].split(" - ")[-1].strip(),
                "description-full": image_element["alt"],
                "src-full": f"https:{image_element['src']}",
                "src": f"https:{image_element['src']}".split("?")[0]
            }

        show_images_container = doc.find(id='renderedImages')
        show_images = show_images_container.select("img")
        return [parse_show_image(x) for x in show_images]

    def _list_related_items(self, doc):
        def _parse_links(id):
            hrefs = [x.find(href=True)["href"] for x in doc.find_all(id=id)]
            return [f"{self.elements.selectors.URLS.BASE}{x}" for x in hrefs]

        return {
            "similars": _parse_links(id="similars"),
            "recommendations": _parse_links(id="recommendations"),
            "other": _parse_links(id="lookTotal")
        }



