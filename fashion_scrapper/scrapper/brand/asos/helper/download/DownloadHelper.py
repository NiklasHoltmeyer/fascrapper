import os
from collections import defaultdict
from multiprocessing import Pool

from scrapper.brand.asos.Asos import Asos
from scrapper.brand.asos.helper.download.AsosPaths import AsosPaths
from pathlib import Path
from tinydb import where

from datetime import datetime
from pathlib import Path

from tinydb import where
from tqdm.auto import tqdm

from scrapper.util.list import flatten
from scrapper.util.web.dynamic import driver as d_driver

from scrapper import util
from scrapper.brand.asos.helper.download.AsosPaths import AsosPaths
from scrapper.util.io import Json_DB

class DownloadHelper:
    def __init__(self, **args):
        self.visited_db = args.get("visited_db")
        self.logger = args.get("logger")
        self.category_path = args.get("category_path")
        #self.brand_api = args.get("brand_api")
        self.brand_path = AsosPaths(self.category_path)
        self.threads = args.get("threads", os.cpu_count())


        self.tmp_path = Path(str(self.category_path) + "/tmp")
        self.tmp_path.mkdir(parents=True, exist_ok=True)
        print(self.tmp_path.resolve())


    def prepare_categories(self, category_jobs, IGNORE_CATEGORY_EXISTING=False):
        """

        :param category_jobs: Prepared Categories (already filterd)
        :return:
        """
        def filter_category_downloaded(job):
            return IGNORE_CATEGORY_EXISTING or len(self.visited_db.search(where('url') == job["url"])) == 0

        category_jobs = filter(filter_category_downloaded, category_jobs)

        def load_category(cat_data):
            category_name, category_url = cat_data
            with d_driver(headless=False) as driver:
                asos = Asos(driver=driver, logger=self.logger)
                self.logger.debug("Loading" + category_url)
                items = asos.list_category(category_url, PAGINATE=False)
                return [{"name": category_name, "url": category_url, "items": [x]} for x in items]

        def load_categories(jobs):
            with Pool(self.threads) as p:
                r = p.map(load_category, tqdm(jobs, desc=f"Prepare Categories - {self.THREADS} Threads", total=len(jobs)))
                return flatten(r)

        results = load_categories(category_jobs)

        def group_results_by_category(results):
            grouped_results = defaultdict(lambda: [])
            for result in results:
                grouped_results[result["name"]].append(result)
            return grouped_results

        results_grouped = group_results_by_category(results)

        def save_visited_categories(results_grouped):
            for result in results_grouped:
                #name, url, items =



