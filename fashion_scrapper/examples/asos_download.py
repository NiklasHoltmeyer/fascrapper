from multiprocessing import Pool, freeze_support
from time import sleep

from tqdm.auto import tqdm

from scrapper.brand.asos.Asos import Asos
from scrapper.brand.asos.consts.parser import *
from scrapper.brand.asos.helper.database.dbhelper import list_dbs_by_category
from scrapper.brand.asos.helper.download.AsosPaths import AsosPaths
from scrapper.brand.asos.helper.download.Asos_DownloadHelper import Asos_DownloadHelper
from scrapper.util.list import flatten
from scrapper.util.web.dynamic import driver as d_driver


def prepare_categories(category_jobs):
    def load_category(cat_data):
        category_name, category_url = cat_data
        with d_driver(headless=False) as driver:
            asos = Asos(driver=driver, logger=logger)
            logger.debug("Loading" + category_url)
            items = asos.list_category(category_url, PAGINATE=PAGINATE)
            return [{"category": {"name": category_name, "url": category_url, "items": [x]}} for x in items]

    categories_data = []
    with Pool(THREADS) as p:
        r = p.map(load_category, tqdm(category_jobs, desc=f"i) List Cat. {THREADS} Threads", total=len(category_jobs)))
        categories_data.append(r)
        return flatten(categories_data)


def prepare_categories(dl_helper):
    with d_driver(headless=False) as driver:
        category_jobs_ = Asos(driver=driver).list_categories_groupey_by_name()
    exceptions = dl_helper.prepare_categories(category_jobs_)
    for exceptions in exceptions:
        if len(exceptions) > 0:
            print(exceptions)
            print("")


def prepare_articles(dl_helper):
    categories_db_path = AsosPaths(BASE_PATH).get_category_db_base_path()

    categories_db = list_dbs_by_category(db_base_Path=categories_db_path, CATEGORIES=CATEGORIES,
                                         unknown_category_allowed=unknown_category_allowed)
    dl_helper.prepare_articles(categories_db)

def download_images(dl_helper):
    entries_db_path = AsosPaths(BASE_PATH).get_entries_db_base_path()
    entries_db = list_dbs_by_category(db_base_Path=entries_db_path, CATEGORIES=CATEGORIES,
                                      unknown_category_allowed=unknown_category_allowed)
    exceptions = dl_helper.download_images(entries_db)
    exceptions = list(filter(lambda x: x, exceptions))
    for url, dst, exception in exceptions:
        print(url, exception)
    print("Len Excp", len(exceptions))

def describe_results(dl_helper):
    results = dl_helper.describe_results(FORCE=True)
    for key, value in results.items():
        print(key)
        #print(max(len(key), len(value)) * "v")
        print(value)
        #print(max(len(key), len(value)) * "-")
        print("-" * 16)

if __name__ == "__main__":
    freeze_support()

    dl_helper = Asos_DownloadHelper(**dl_settings)
    prepare_categories(dl_helper)
    prepare_articles(dl_helper)
    download_images(dl_helper)
    describe_results(dl_helper)

