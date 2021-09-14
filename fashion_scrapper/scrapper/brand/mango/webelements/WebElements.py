from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from scrapper.brand.mango.webelements.views.Mango_Item_Elements import Mango_Article_Elements
from scrapper.brand.mango.webelements.views.Mango_Categories_Elements import Mango_Categories_Elements
from scrapper.brand.mango.webelements.views.Mango_Category_Elements import Mango_Category_Elements
from scrapper.brand.mango.webelements.consts.Mango_Selectors import Mango_Selectors
from scrapper.util.web.dynamic import wait


class WebElements:
    """ HTML Elements """

    def __init__(self, driver, logger):
        self.driver = driver
        self.selectors = Mango_Selectors()
        self.logger = logger

        self.category = Mango_Category_Elements(self)
        self.categories = Mango_Categories_Elements(self)
        self.article = Mango_Article_Elements(self)

    def header(self):
        header = self.driver.find_elements_by_css_selector("header")
        assert len(header) != 0
        headerHTML = header[0].get_attribute("outerHTML")
        doc = BeautifulSoup(headerHTML, "html.parser")

        return doc

    def accept_cookies(self):
        wait(self.driver, EC.element_to_be_clickable((By.ID, self.selectors.ID.CHANGE_VIEW_COLUMNS))).click()


#        wait(self.driver, EC.element_to_be_clickable((By.ID, self.selectors.ID.CHANGE_VIEW_COLUMNS))).click()
#        try:
#            self.driver.find_element_by_id(self.selectors.ID.ACCEPT_COOKIES).click()  # Cookies
#        except Exception as e:
#            raise e

