from datetime import datetime
from pathlib import Path

from tinydb import where
from tqdm.auto import tqdm

from scrapper import util
from scrapper.brand.mango.helper.download.MangoPaths import MangoPaths
from scrapper.util.io import Json_DB


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
                util.web.static.download_file(url=image["src"], path=path, exist_ok=True)
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



