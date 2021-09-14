from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from scrapper.util.web.dynamic import wait, scroll_end_of_page


class Mango_Article_Elements:
    """
    Web-Elements of/for a Single Item
    """
    def __init__(self, web_elements):
        self.elements = web_elements
        self.driver = web_elements.driver
        self.logger = web_elements.logger

    def show(self, url):
        """

        :param url: URL of Item
        :return: Name, Color, Price, Images, Related Items of Item
        """
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
