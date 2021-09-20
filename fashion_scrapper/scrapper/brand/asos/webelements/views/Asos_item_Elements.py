from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from scrapper.util.list import distinct_list_of_dicts
from scrapper.util.web.dynamic import wait, scroll_end_of_page
from scrapper.util.web.dynamic import wait


class Asos_Article_Elements:
    """
    Web-Elements of/for a Single Item
    """

    def __init__(self, driver, logger):#web_elements):
        self.driver = driver
        self.logger = logger

    def show(self, url):
        """

        :param url: URL of Item
        :return: Name, Color, Price, Images, Related Items of Item
        """

        product_doc, doc_might_like = self._load_html(url)
        return self._parse_item(product_doc, doc_might_like)

    def _parse_item(self, product_doc, doc_might_like):
        def _parse_img(img):
            return {
                "url": img["src"].split("?")[0],
                "url_full": img["src"],
                "description": img["alt"]
            }

        def _parse_price(price):
            if not price:
                return {"price": "UNK", "currency": "UNK"}
            elif "€" in price:
                _splitted = price.split(" ")
                return {"price": _splitted[0], "currency": _splitted[1]}
            elif "£" in price:
                return {"price": price.replace("£", "").replace(".", ","), "currency": "£"}
            return {"price": price, "currency": "UNK"}

        imgs = product_doc.find_all("img", src=True)
        imgs = distinct_list_of_dicts([_parse_img(x) for x in imgs], key="url")
        price_value = product_doc.find("span", {"data-id": "current-price"})
        price_value = price_value.text if price_value else ""

        might_like_urls = [x["href"] for x in
                           doc_might_like.find("section", {"data-test-id": "mightLikeCarousel"}).find_all("a",
                                                                                                          href=True)]

        return {
            "name": product_doc.find(id="aside-content").find("h1").text,
            "color": product_doc.find("span", {"class": "product-colour"}).text,
            "price": _parse_price(price_value),
            "images": imgs,
            "related_items": might_like_urls
        }


    def _load_html(self, url):
        self.driver.get(url)
        # wait for id
        wait(self.driver, EC.presence_of_element_located((By.ID, "chrome-main-content")))

        scroll_end_of_page(self.driver, SCROLL_TOP=True)

        product_container = self.driver.find_element_by_id("core-product")
        product_container_html = product_container.get_attribute("innerHTML")
        product_doc = BeautifulSoup(product_container_html, 'html.parser')

        might_like = self.driver.find_elements_by_id("mightLike")
        might_like_container_html = might_like[0].get_attribute("innerHTML") if len(might_like) > 0 else ""

        might_like_doc = BeautifulSoup(might_like_container_html, 'html.parser')

        return product_doc, might_like_doc












