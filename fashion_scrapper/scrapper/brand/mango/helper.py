from urllib.parse import urlparse

import util
from default_logger.defaultLogger import defaultLogger
from scrapper.brand.mango.Mango import Mango
from util.web.dynamic import *
from pathlib import Path

from tinydb import where

from util.io import Json_DB

from datetime import datetime
from tqdm.auto import tqdm

from scrapper.brand.mango.webelements._WebElements import _Mango_Selectors

class MangoPaths:
    def __init__(self, BASE_PATH):
        self.BASE_PATH = BASE_PATH

    def relative_image_path(self, URL, create=True):  # falscher name -> eig. relative cat path
        category = URL.replace(_Mango_Selectors.URLS.BASE_FULL, "")
        p = Path(self.BASE_PATH, category)
        if create:
            p.mkdir(parents=True, exist_ok=True)
        return p

    def relative_img_real_path(self, image_url):
        return urlparse(image_url).path.split("/fotos")[-1]


class DownloadHelper:
    def __init__(self, **args):
        self.visited_db = args.get("visited_db")
        self.logger = args.get("logger")
        self.mango = args.get("mango")
        self.BASE_PATH = args.get("BASE_PATH")

        self.mango_path = MangoPaths(self.BASE_PATH)

    def download_images(self, category_url, IGNORE_CATEGORY_EXISTING=False):
        category_path = self.mango_path.relative_image_path(category_url)
        category_database = Json_DB(category_path, "data.json")

        parse_images = self.parse_image_urls(category_url, category_path, category_database,
                                             IGNORE_CATEGORY_EXISTING=IGNORE_CATEGORY_EXISTING)

        def dl_job(image):
            path = Path(self.BASE_PATH + image["path"])
            path.parent.mkdir(parents=True, exist_ok=True)
            try:
                util.web.static.download_file(url=image["src"], path=path)
                return 0
            except:
                return 1

        dl_jobs_results = [[dl_job(image) for image in item["images"]]
            for item in tqdm(category_database.all(), desc="Download Images")]

        parse_images["num_exceptions"] = sum([sum(x) for x in dl_jobs_results])
        return parse_images

    def parse_image_urls(self, category_url, category_path, category_database, IGNORE_CATEGORY_EXISTING=False):
        if not IGNORE_CATEGORY_EXISTING and len(self.visited_db.search(where('url') == category_url)) != 0:
            self.logger.debug(f"Category Vistied: {category_url}")
            return {
                "db_path": f"{category_path}/data.json"
            }

        category_items = self._list_category_clean(category_url)

        exceptions = []

        for item in tqdm(category_items, desc=f'Category {category_url}'):
            item_in_db = len(category_database.search(where('url') == item["url"])) > 0
            if item_in_db:
                continue

            try:
                info = self.mango.show(item["url"])
                info['images'] = [{"description": x["description"], "src": x["src"], \
                                   "path": self.mango_path.relative_img_real_path(x["src"])} for x in info['images']]
                info["url"] = item["url"]
                category_database.insert(info)
            except Exception as e:
                exceptions.append({"item": item, "exception": e})
                self.logger.error(e)

        if len(exceptions) > 0:
            failed_db = Json_DB(category_path, "failed.json")
            [failed_db.insert(x) for x in exceptions]

            self.logger.debug("Error")

        return {
            "exceptions": exceptions,
            "db_path": f"{category_path}/data.json"
        }

    def _list_category_clean(self, category_url):
        self.visited_db.insert({'url': category_url, 'last_visit': datetime.now()})
        category_items = self.mango.list_category(category_url)

        _clean_info = lambda d: {"url": d["url"], "name": d["alt"]}
        return [_clean_info(x) for x in category_items]

if __name__ == "__main__":


    SCRAP_PATH = r"F:\workspace\fascrapper\scrap_results\mango"
    Path(SCRAP_PATH).mkdir(parents=True, exist_ok=True)

    logger = defaultLogger("Mango")
    driver = driver()
    mango = Mango(driver=driver, logger=logger)

    category_url = "https://shop.mango.com/de/herren/polo-shirts_c20667557"

    dl_settings = {
        "visited_db": Json_DB(SCRAP_PATH, "visited.json"),
        "logger": logger,
        "mango": mango,
        "BASE_PATH": r"F:\workspace\fascrapper\scrap_results\mango"
    }
    dl_helper = DownloadHelper(**dl_settings)

    print(dl_helper.download_images(category_url))
    driver.close()


