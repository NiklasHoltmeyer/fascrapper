from scrapper.brand.hm.webelements.consts.HM_Selectors import HM_Selectors
from scrapper.util.list import flatten, distinct, distinct_list_of_dicts
from scrapper.util.web.dynamic import wait, driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


class HM_Categories_Elements:
    """ List all Categories: T-Shirt, Shorts, ... """

    def __init__(self, web_elements):
        self.elements = web_elements
        self.driver = web_elements.driver
        self.logger = web_elements.logger

    def list_categories(self):
        self.driver.get(HM_Selectors.URLS.BASE_FULL)
        wait(self.driver, EC.visibility_of_element_located((By.CSS_SELECTOR, HM_Selectors.CSS.HEADER)))

        sub_categories_from_header = lambda header: header.find_elements_by_css_selector("a.menu__sub-link")
        headers = self.driver.find_elements_by_css_selector(HM_Selectors.CSS.HEADER)

        sub_categories_elm = flatten((map(sub_categories_from_header, headers)))
        categories = map(lambda x: {"name": x.get_attribute('name'), "url": x.get_attribute('href')},
                         sub_categories_elm)
        categories = filter(lambda x: x["url"].startswith(HM_Selectors.URLS.BASE_FULL), categories)
        categories = distinct_list_of_dicts(categories, "url")

        return categories
#    def load_sub_categories(self, url):
#        self.logger.debug(f"Loading Sub Category {url}")
#        self.driver.get(url)
#        header = self.elements.header()
#        hrefs = header.find_all(href=True)
#        hrefs = [{'href': href["href"], "text": href.text} for href in hrefs]
#        cat_top, cat_sub = [], []

#        for href in hrefs:
#            if (len(href["href"].split("/"))) == 5:
# cat_top.append(href)
#            else:
# cat_sub.append(href)

#        assert len(hrefs) == len(cat_top) + len(cat_sub)

#        return cat_top, cat_sub

#    def list_categories(self, url):
#        visited_links = []
#        urls = [url]
#        categories = []

#        while len(urls) > 0:
#            url = urls.pop()
#            cat_top, cat_sub = self.load_sub_categories(url)
#            visited_links.append(url)

#            categories.extend(cat_top)
#            categories.extend(cat_sub)

#            for x in cat_top:
# if not x["href"] in visited_links:
# urls.append(x["href"])

#        return categories
