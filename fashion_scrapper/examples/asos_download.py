import pickle
from multiprocessing import Pool, freeze_support

import numpy as np
from tqdm.auto import tqdm

from default_logger.defaultLogger import defaultLogger
from scrapper.brand.asos.Asos import Asos
from scrapper.brand.asos.helper.download.DownloadHelper import DownloadHelper
from scrapper.util.io import Json_DB
from scrapper.util.list import includes_excludes_filter, flatten
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
    category_jobs = flatten_categories(filter_categories())
    BASE_PATH = r"F:\workspace\fascrapper\scrap_results\asos"
    dl_settings = {
        "base_path": BASE_PATH,
        "visited_db": Json_DB(BASE_PATH, "visited.json"),
        "logger": logger,
        "threads": 8
    }
    dl_helper = DownloadHelper(**dl_settings)
    save_frequency = 0.1
    chunk_size = max(0, int(len(category_jobs) * save_frequency))
    category_jobs_chunked = np.array_split(category_jobs, chunk_size)
    exceptions = []
    for job in tqdm(category_jobs_chunked, desc="OUTER"):
        exceptions.append(dl_helper.prepare_categories(job))

    exceptions = np.array(exceptions)

    with open(r"F:\workspace\fascrapper\scrap_results\asos\exceptions.pkl") as db_file:
        pickle.dump(obj=exceptions, file=db_file)



    #categories_data = flatten(prepare_categories())


    #for x in categories_data:
        #print("o"*8)
        #print(x)
        #print("*"*8)


