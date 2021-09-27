from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from scrapper.brand.hm.webelements.consts.HM_Selectors import HM_Selectors
from scrapper.util.list import distinct_list_of_dicts, flatten
from scrapper.util.web.dynamic import wait, scroll_end_of_page
from scrapper.util.web.dynamic import driver as d_driver
from scrapper.util.web.dynamic import scroll_end_of_page
from scrapper.util.web.dynamic import wait
from scrapper.util.web.static import find_first_parent_href


class HM_Article_Elements:
    """
    Web-Elements of/for a Single Item
    """

    def __init__(self, web_elements):
        self.driver = web_elements.driver
        self.logger = web_elements.logger

    def show(self, url):
        """

        :param url: URL of Item
        :return: Name, Color, Price, Images, Related Items of Item
        """

        product_doc, doc_might_like = self._load_html(url)
        try:
            return self._parse_item(product_doc, doc_might_like)
        except Exception as e:
            print(f"Exception: {url}")
            raise e

    def _parse_item(self, product_doc, doc_might_like):
        def _parse_imgs(product_doc):
            img_info = lambda i: {"name": i["alt"], "url": "https:" + i["src"]}
            imgs = product_doc.select("figure.pdp-image", src=True)
            imgs = map(lambda x: x.find("img", src=True), imgs)
            imgs = map(img_info, imgs)
            return list(imgs)

        def _parse_price(product_doc):
            container = product_doc.select("#product-price")
            if len(container) < 1:
                return {"price": "UNK", "currency": "UNK"}
            price = product_doc.select("#product-price")[0].text
            price = price.split(" ")

            if len(price) == 2:
                return {"price": price[0], "currency": price[1]}
            return {"price": price, "currency": "UNK"}

        def _parse_might_like(doc_might_like):
            might_like_imgs = doc_might_like.find(id="product-reco-pra1").find_all("img")
            find_href = lambda img: HM_Selectors.URLS.BASE_FULL + find_first_parent_href(img)
            might_like = map(find_href, might_like_imgs)
            return list(might_like)

        return {
            "name": product_doc.find(class_="product-item-headline").text.replace("\t", "").replace("\n", "").strip(),
            "color": product_doc.find("div", class_="product-colors").find("h3", class_="product-input-label").text,
            "price": _parse_price(product_doc),
            "images": _parse_imgs(product_doc),
            "related_items": _parse_might_like(doc_might_like)
        }

    def _load_html(self, url):
        self.driver.get(url)

        wait(self.driver, EC.presence_of_element_located((By.ID, "main-content")))
        scroll_end_of_page(self.driver, SCROLL_TOP=True)

        product_container = self.driver.find_element_by_css_selector("div.pdp-wrapper")
        product_container_html = product_container.get_attribute("innerHTML")
        product_doc = BeautifulSoup(product_container_html, 'html.parser')

        might_like = self.driver.find_elements_by_css_selector("div.productrecommendationarea")
        might_like_container_html = might_like[0].get_attribute("innerHTML") if len(might_like) > 0 else ""

        might_like_doc = BeautifulSoup(might_like_container_html, 'html.parser')

        return product_doc, might_like_doc
