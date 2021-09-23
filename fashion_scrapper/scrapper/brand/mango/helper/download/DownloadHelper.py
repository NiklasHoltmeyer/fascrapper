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
        self.category_path = args.get("category_path")
        self.brand_api = args.get("brand_api")
        self.brand_path = MangoPaths(self.category_path)

    def download_images(self, category_url, IGNORE_CATEGORY_EXISTING=False):
        category_as_filename = self.brand_path.category_from_url(category_url).replace("/", "_")
        #category_database = Json_DB(category_path, "data.json")
        category_database = Json_DB(self.category_path, f"{category_as_filename}.json")

        parse_images = self.parse_image_urls(category_url, category_database,
                                             IGNORE_CATEGORY_EXISTING=IGNORE_CATEGORY_EXISTING)

        def dl_job(image):
            path = Path(str(self.category_path) + image["path"])
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

    def parse_image_urls(self, category_url, category_database, IGNORE_CATEGORY_EXISTING=False):
        category_as_filename = self.brand_path.category_from_url(category_url).replace("/", "_")

        if not IGNORE_CATEGORY_EXISTING and len(self.visited_db.search(where('url') == category_url)) != 0:
            self.logger.debug(f"Category Vistied: {category_url}")
            return {
                "db_path": f"{self.category_path}/{category_as_filename}.json"
            }

        category_items = self._list_category_clean(category_url)

        exceptions = []

        for item in tqdm(category_items, desc=f'Category {category_url}'):
            item_in_db = len(category_database.search(where('url') == item["url"])) > 0
            if item_in_db:
                continue

            try:
                info = self.brand_api.show(item["url"])
                info['images'] = [{"description": x["description"], "src": x["src"], \
                                   "path": self.brand_path.relative_img_real_path(x["src"])} for x in info['images']]
                info["url"] = item["url"]
                category_database.insert(info)
            except Exception as e:
                exceptions.append({"item": item, "exception": e, "function": "parse_image_urls"})
                self.logger.error(e)

        if len(exceptions) > 0:
            failed_db = Json_DB(self.category_path, f"{category_as_filename}_failed.json") #Json_DB(category_path, "failed.json")
            failed_db.insert_multiple(exceptions)

        return {
            "exceptions": exceptions,
            "db_path": f"{self.category_path}/{category_as_filename}.json"
        }

    def _list_category_clean(self, category_url):
        self.visited_db.insert({'url': category_url, 'last_visit': datetime.now()})
        category_items = self.brand_api.list_category(category_url)

        _clean_info = lambda d: {"url": d["url"], "name": d["alt"]}
        return [_clean_info(x) for x in category_items]



