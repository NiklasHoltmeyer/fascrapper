from time import sleep

from default_logger.defaultLogger import defaultLogger
from scrapper.brand.asos.webelements.WebElements import WebElements


class Asos:
    def __init__(self, driver, logger=None):
        self.driver = driver
        self.logger = logger if logger else defaultLogger("Asos")

        self.elements = WebElements(driver, self.logger)

    def list_categories(self, retries=3):
        categories = self.elements.categories.list_categories()
        if len(categories) == 0 and retries > 0:
            sleep(0.5)
            return self.list_categories((retries - 1))
        return categories

    def list_category(self, url, retries=2, PAGINATE=True):
        category = self.elements.category.list_category(url, PAGINATE=PAGINATE)
        if len(category) == 0 and retries > 0:
            sleep(0.5)
            return self.list_category(url, (retries - 1))
        return category

    def show(self, url):
        return self.elements.article.show(url)
