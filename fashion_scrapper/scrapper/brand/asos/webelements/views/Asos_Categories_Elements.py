from selenium.webdriver.common.by import By

from scrapper.brand.asos.webelements.consts.Asos_Selectors import Asos_Selectors
from scrapper.util.list import flatten, distinct
from scrapper.brand.asos.helper.download.AsosPaths import AsosPaths
from bs4 import BeautifulSoup

from scrapper.util.web.dynamic import wait
from selenium.webdriver.support import expected_conditions as EC

class Asos_Categories_Elements:
    """ List all Categories withing an Category ()
        Top-(Level)-Categories: Male, Female, ...
        Sub-Categories: T-Shirt, Shorts, ...
    """

    def __init__(self, driver, logger):#web_elements):
        #self.elements = web_elements
        #self.driver = web_elements.driver
        #self.logger = web_elements.logger
        self.driver = driver
        self.logger = logger

    def list_categories(self):
        self.driver.get(Asos_Selectors.URLS.BASE_URL_MEN)
        try:
            wait(self.driver, EC.presence_of_element_located((By.ID, 'chrome-sticky-header')))
        except Exception as e:
            self.debugger.error("Asos_Categories_Elements::list_categories")
            raise Exception(e)
        full_html = self.driver.page_source
        doc = BeautifulSoup(full_html, 'html.parser')

        nav_ids = doc.select('h2[id]')

        categories = self._parse_nav_for_cat(nav_ids)
        assert len(distinct([x["url"] for x in categories])) == len(categories), "List is not Distinct"

        return categories

    def _parse_nav_for_cat(self, navs):
        def __parse_nav_for_cat(nav):
            hrefs = nav.parent.find_all(href=True)
            return [{"name": href.text, "url": href["href"], "category": AsosPaths.category_from_url(href["href"])} for
                    href in hrefs]

        cats = [__parse_nav_for_cat(x) for x in navs]
        cats = flatten(cats)
        return cats