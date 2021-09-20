from scrapper.brand.asos.webelements.views.Asos_Categories_Elements import Asos_Categories_Elements
from scrapper.brand.asos.webelements.views.Asos_Category_Elements import Asos_Category_Elements
from scrapper.brand.asos.webelements.views.Asos_item_Elements import Asos_Article_Elements


class WebElements:
    """ HTML Elements """

    def __init__(self, driver, logger):
        self.driver = driver
        # self.selectors = Mango_Selectors()
        self.logger = logger

        self.category = Asos_Category_Elements(driver, logger)
        self.categories = Asos_Categories_Elements(driver, logger)
        self.article = Asos_Article_Elements(driver, logger)
