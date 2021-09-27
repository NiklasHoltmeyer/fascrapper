from scrapper.brand.hm.webelements.consts.HM_Selectors import HM_Selectors
from scrapper.brand.hm.webelements.views.HM_Article_Elements import HM_Article_Elements
from scrapper.brand.hm.webelements.views.HM_Categories_Elements import HM_Categories_Elements
from scrapper.brand.hm.webelements.views.HM_Category_Elements import HM_Category_Elements


class HMWebElements:
    """ HTML Elements """

    def __init__(self, driver, logger):
        self.driver = driver
        self.selectors = HM_Selectors()
        self.logger = logger

        self.category = HM_Category_Elements(self)
        self.categories = HM_Categories_Elements(self)
        self.article = HM_Article_Elements(self)

