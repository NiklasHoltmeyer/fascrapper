from time import sleep

from default_logger.defaultLogger import defaultLogger
from scrapper.brand.asos.consts.parser import excludes, CATEGORIES
from scrapper.brand.asos.webelements.WebElements import WebElements
from scrapper.util.list import includes_excludes_filter


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

    def list_categories_groupey_by_name(self):
        def flatten_category(category):
            cat_name, cat_data = category
            cat_urls = [x["url"] for x in cat_data]
            return list(zip([cat_name] * len(cat_urls), cat_urls))

        categories = self.list_categories()

        filter_category = lambda category: (category["name"], [x for x in categories if
                                                               includes_excludes_filter(x["url"],
                                                                                        includes=category["includes"],
                                                                                        excludes=excludes)])
        filterd_categories = map(filter_category, CATEGORIES)
        filterd_categories = map(flatten_category, filterd_categories)
        return list(filterd_categories)

    def list_category(self, url, retries=2, PAGINATE=True):
        category = self.elements.category.list_category(url, PAGINATE=PAGINATE)
        if len(category) == 0 and retries > 0:
            sleep(0.5)
            return self.list_category(url, (retries - 1))
        return category

    def show(self, url):
        return self.elements.article.show(url)
