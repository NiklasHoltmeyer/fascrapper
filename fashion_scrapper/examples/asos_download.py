from pathlib import Path
from bs4 import BeautifulSoup

from scrapper.brand.asos.helper.download.DownloadHelper import DownloadHelper
from scrapper.util.io import Json_DB
from scrapper.util.web.static import find_first_parent_href
from scrapper.util.list import flatten, distinct, distinct_list_of_dicts
from scrapper.util.web.dynamic import driver as ddriver
from scrapper.brand.asos.webelements.views.Asos_Categories_Elements import Asos_Categories_Elements
from scrapper.brand.asos.webelements.views.Asos_Category_Elements import Asos_Category_Elements
from scrapper.brand.asos.webelements.views.Asos_item_Elements import Asos_Article_Elements
from default_logger.defaultLogger import defaultLogger

from random import shuffle
from tqdm.auto import tqdm
from scrapper.util.web.dynamic import driver as d_driver

from time import sleep
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from scrapper.util.web.dynamic import wait, scroll_end_of_page
from scrapper.brand.asos.Asos import Asos
from scrapper.util.list import includes_excludes_filter, flatten
from multiprocessing import Pool, freeze_support

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

logger = defaultLogger("asos")
THREADS = 2


def filter_categories():
    logger.debug("Filter Categories")
    with d_driver(headless=False) as driver:
        asos = Asos(driver=driver, logger=logger)
        categories = asos.list_categories()

        filter_category = lambda category: (category["name"], [x for x in categories if
                                                               includes_excludes_filter(x["url"],
                                                                                        includes=category["includes"],
                                                                                        excludes=excludes)])
        filterd_categories = [filter_category(x) for x in CATEGORIES]
        return filterd_categories


def flatten_category(category):
    cat_name, cat_data = category
    cat_urls = [x["url"] for x in cat_data]
    return list(zip([cat_name] * len(cat_urls), cat_urls))


def flatten_categories(categories):
    return flatten([flatten_category(x) for x in categories])

def load_category(cat_data):
    category_name, category_url = cat_data
    print(category_name)
    with d_driver(headless=False) as driver:
        asos = Asos(driver=driver, logger=logger)
        logger.debug("Loading" + category_url)
        print("Loading" + category_url)
        items = asos.list_category(category_url, PAGINATE=False)
        return [{"category": {"name": category_name, "url": category_url, "items": [x]}} for x in items]

def prepare_categories(category_jobs):
    """
    Alle Items laden (kein DL)
    :return:
    """


    categories_data = []
    with Pool(THREADS) as p:
        r = p.map(load_category, tqdm(category_jobs, desc=f"i) List Cat. {THREADS} Threads", total=len(category_jobs)))
        categories_data.append(r)
        return flatten(categories_data)




if __name__ == "__main__":
    freeze_support()
    #category_jobs = flatten_categories(filter_categories())
    #category_jobs = category_jobs[:2]
    BASE_PATH = r"F:\workspace\fascrapper\scrap_results\asos"
    dl_settings = {
        "category_path": BASE_PATH,
        "visited_db": Json_DB(BASE_PATH, "visited.json")
    }
    dl_helper = DownloadHelper(**dl_settings)
    category_jobs = [('schuhe', 'https://www.asos.com/women/new-in/new-in-shoes/cat/?cid=6992&nlid=ww|new+in|new+products|shoes'), ('schuhe', 'https://www.asos.com/women/new-in/new-in-shoes/cat/?cid=6992&nlid=ww|shoes|shop+by+product|new+in')]

    dl_helper.prepare_categories(category_jobs)


    #categories_data = flatten(prepare_categories())


    #for x in categories_data:
        #print("o"*8)
        #print(x)
        #print("*"*8)


