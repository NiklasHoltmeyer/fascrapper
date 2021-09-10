from urllib.parse import urlparse

from default_logger.defaultLogger import defaultLogger
from scrapper.brand.mango.MangoElements import MangoElements
from util.web.static import find_first_parent_href


class MongoCategory:
    def __init__(self, driver, logger=None):
        self.driver = driver
        self.logger = logger if logger else defaultLogger("Mongo")

        self.elements = MangoElements(driver)

    def list_categories(self, url):
        return self.elements.categories.list_categories(url)

    def list_category(self, url):
        def parse_preview_images(preview_img):
            img_info = preview_img.attrs
            article_url = find_first_parent_href(preview_img)
            article_url = urlparse(article_url).path  # removing fragments / querys / ...

            img_info["url"] = f"https://shop.mango.com/{article_url}".replace("//", "/")

            return img_info

        # -> List all Links withing an Category (T-Shirts)
        article_imgs = self.elements.category.list_images(url)

        articles = [parse_preview_images(x) for x in article_imgs]
        articles = list({x['url']: x for x in articles}.values())  # remove duplications (based on url)

        return articles


if __name__ == "__main__":
    from selenium.webdriver import Chrome

    print("Test")
    driver = Chrome("C:\selenium\chromedriver.exe")
    driver.maximize_window()

    test = MongoCategory(driver)
    _test = test.list_category("https://shop.mango.com/de/herren/t-shirts_c12018147")
    print("***")
    print(_test)
    print("***")
    print(len(_test))
    print("***")
    driver.close()
    exit(0)

    categories = test.list_categories("https://shop.mango.com/de/herren")
    print(categories)
    print(len(categories))

    print("---")
    i = 0
    while True:
        try:
            articles = test.list_category(categories[i]["href"])
            print(articles)
            print(len(articles))
            i = i + 1
            break
        except:
            pass
    print(5, categories[5])

    #driver.close()  #