import time
from multiprocessing import Pool, freeze_support
from pathlib import Path

from tinydb import where
from tqdm.auto import tqdm
from default_logger.defaultLogger import defaultLogger
from scrapper.brand.asos.Asos import Asos
from scrapper.brand.asos.helper.database.dbhelper import list_dbs_by_category
from scrapper.brand.asos.helper.download.DownloadHelper import DownloadHelper
from scrapper.util.io import Json_DB
from scrapper.util.web.dynamic import driver as d_driver

CATEGORIES = [
    {"name": "schuhe", "includes": ["shoe"], "excludes": []},
    {"name": "hose", "includes": ["short", "jeans", "leggings", "trousers"], "excludes": []},
    {"name": "shirt", "includes": ["shirt", "skirt", "blazer", "top"], "excludes": []},
    {"name": "pullover", "includes": ["pullover", "cardigans"], "excludes": []},
    {"name": "jacke", "includes": ["coat"], "excludes": []},
    {"name": "kleid", "includes": ["dresses"], "excludes": ["kleidung"]},
    {"name": "anzug", "includes": ["suit", "overalls"], "excludes": []}
]

excludes = ["sale",  "view+all", "new-in-clothing", "accessories", "face-body", "topshop",  "back-in-stock", \
            "fashion-online-4", "curve-plus-size", "maternity", "petite", "tall", "fashion-online-12", "generic-promos", \
           "designer", "a-to-z-of-brands", "exclusives", "activewear", "co-ords", "multipacks", "bags", \
            "bras", "fashion-online-", "yoga-studio", "ski-snowboard", "running", "outdoors", "ss-fashion-trend-", \
            "gym-training", "gifts", "wedding-attire", "underwear", \
            "plus-size", "outlet-edits", "back-to-school", "modestwear", "socks-tights", "swim", "lingerie", \
            "loungewear", "-essentials", "responsible-edit", "wedding", "workwear", "jewellery", "sunglasses", "party-wear", \
           "licence"]

from scrapper.brand.asos.helper.download.AsosPaths import AsosPaths

logger = defaultLogger("asos")
THREADS = 2

BASE_PATH = r"F:\workspace\fascrapper\scrap_results\asos"
brand_path = AsosPaths(BASE_PATH)
#asos = Asos(d_driver(headless=False))

categories_db_path = brand_path.get_category_db_base_path()
entries_db_path = brand_path.get_entries_db_base_path()
IGNORE_CATEGORY_EXISTING = False

BASE_PATH = r"F:\workspace\fascrapper\scrap_results\asos"


if __name__ == "__main__":
    freeze_support()


    while True:
        with Json_DB(BASE_PATH, "visited.json") as visited_db:
            dl_settings = {
                "base_path": BASE_PATH,
                "visited_db": visited_db,
                "logger": logger,
                "threads": 4
            }
            dl_helper = DownloadHelper(**dl_settings)
            categories_db = list_dbs_by_category(db_base_Path=categories_db_path, CATEGORIES=CATEGORIES)
            entries_db = list_dbs_by_category(db_base_Path=entries_db_path, CATEGORIES=CATEGORIES)

            dl_helper.prepare_articles(categories_db)
            #dl_helper.download_images(entries_db)
        break
        #time.sleep(60*60)
