import os
from collections import defaultdict
from datetime import datetime
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from tinydb import where
from tqdm.auto import tqdm

from default_logger.defaultLogger import defaultLogger
from scrapper.brand.asos.Asos import Asos
from scrapper.brand.asos.helper.download.AsosPaths import AsosPaths
from scrapper.util.io import Json_DB, time_logger
from scrapper.util.list import flatten, distinct_list_of_dicts
from scrapper.util.web.dynamic import driver as d_driver
from scrapper.util.web.static import download_file


class DownloadHelper:
    def __init__(self, **args):
        self.visited_db = args.get("visited_db")
        self.logger = args.get("logger")
        self.base_path = args.get("base_path")
        self.brand_api = args.get("brand_api")
        self.brand_path = AsosPaths(self.base_path)
        self.threads = args.get("threads", os.cpu_count())

    @staticmethod
    def load_category(cat_data):
        category_name, category_url = cat_data
        try:
            with d_driver(headless=False) as driver:
                asos = Asos(driver=driver, logger=None)
                # self.logger.debug("Loading" + category_url)
                items = asos.list_category(category_url, PAGINATE=True)
                return [{"success": True, "name": category_name, "url": category_url, "items": [x],
                         "cat_path": AsosPaths.category_from_url(category_url).replace("/", "_")} for x in items]
        except Exception as e:
            return [{"success": False, "name": category_name, "url": category_url, "exception": str(e)}]

    @time_logger(name="Prepare Categories", header="DL-Helper", padding_length=50)
    def prepare_categories(self, category_jobs, IGNORE_CATEGORY_EXISTING=False):
        """

        :param category_jobs: Prepared Categories (already filterd)
        :return: Exceptions (Results are Saved to DB)
        """

        def filter_category_downloaded(job, force=IGNORE_CATEGORY_EXISTING):
            return force or len(self.visited_db.search(where('url') == job[1])) == 0

        category_jobs = list(filter(filter_category_downloaded, category_jobs))

        def load_categories(jobs):
            _threads = min(self.threads, len(jobs))
            if _threads < 1:
                return []
            self.logger.debug("Download Categories")
            with Pool(_threads) as p:
                r = list(
                    tqdm(p.imap(DownloadHelper.load_category, jobs), desc=f"Prepare Categories - {_threads} Threads",
                         total=len(jobs)))
                self.logger.debug("Download Categories [Done]")
                return flatten(r)

        results = load_categories(category_jobs)

        def group_results_by_category(results):
            grouped_results = defaultdict(lambda: [])
            exceptions = []
            for result in results:
                if result["success"]:
                    grouped_results[result["name"]].append(result)
                else:
                    exceptions.append(result)
            return grouped_results, exceptions

        results_grouped, exceptions = group_results_by_category(results)

        def save_visited_categories(results_grouped):
            self.logger.debug("Save downloaded Categories")
            def _filter_db_memory(db_all, id):
                for entry in db_all:
                    if entry["id"] == id:
                        return True
                return False

            for cat_name, cat_entries in tqdm(results_grouped.items(), desc="ii Save downloaded Categories - DB"):
                for entry in tqdm(cat_entries, desc="iii Save Entr"):
                    db_path = self.brand_path.get_category_db_base_path() / f"{entry['cat_path']}.json"
                    # self.logger.debug(f"Saving to DB: {db_path}")
                    db_path.parent.mkdir(parents=True, exist_ok=True)
                    with Json_DB(db_path) as db:
                        db_all = db.all()

                        #items = [item for item in entry["items"] if not DownloadHelper.entry_in_db(db, item["id"])]
                        items = [item for item in entry["items"] if not _filter_db_memory(db_all, item["id"])]
                        db.insert_multiple(items)

                    if filter_category_downloaded(entry["url"], False):
                        self.visited_db.insert({'url': entry["url"], 'last_visit': datetime.now()})
            self.logger.debug("Save downloaded Categories")

        save_visited_categories(results_grouped)
        return exceptions

    @staticmethod
    def entry_in_db(db, id_):
        return len(db.search(where('id') == id_)) > 0

    @time_logger(name="Prepare Articles", header="DL-Helper", padding_length=50)
    def prepare_articles(self, categories_db):
        """

        :param categories_db:
        :return:
        """

        def download_entries_by_cat(cat_name, visited_paths):
            cat_db_path = Path(self.base_path, "entries_db", cat_name + ".json")
            cat_db_path.parent.mkdir(parents=True, exist_ok=True)
            with Json_DB(cat_db_path) as cat_db:
                print("cat_db-len", len(cat_db))
                for visited_db_path in tqdm(visited_paths, desc="i Walk DB"):
                    self.logger.debug("WALK-DB: Find new Articles")
                    with Json_DB(visited_db_path) as db:
                        new_entries = [entry for entry in db.all() if not DownloadHelper.entry_in_db(cat_db, entry["id"])]

                    if len(new_entries) == 0:
                        continue
                    _threads = min(self.threads, len(new_entries))

                    new_entries_splitted = np.array_split(new_entries, _threads)
                    self.logger.debug("WALK-DB: Download Articles")
                    with Pool(_threads) as p:
                            entries = flatten(list(tqdm(p.imap(DownloadHelper._download_entries, new_entries_splitted),
                                    desc=f"ii Download Articles - {_threads} Threads",
                                    total=len(new_entries_splitted))))
                            cat_db.insert_multiple(entries)

        _threads = min(self.threads, len(categories_db.items()))
        [download_entries_by_cat(cat_name, visited_paths) for (cat_name, visited_paths) in tqdm(categories_db.items(), desc=f"Download Articles")]

#        with Pool(_threads) as p:
#            tqdm(p.imap(download_entries_by_cat, visited_dbs.items()),
#                    desc=f"Download Articles - {_threads} Threads",
#                    total=len(visited_dbs.items()))

    @time_logger(name="Download Images", header="DL-Helper", padding_length=50)
    def download_images(self, entries_dbs):
        def list_entries_by_cat(entries_dbs):
            for cat_name, db_paths in entries_dbs.items():
                all_entries_by_cat = flatten(map(lambda p: Json_DB(p).all(), db_paths))
                all_entries_by_cat_distinct = distinct_list_of_dicts(all_entries_by_cat, key="url")
                yield cat_name, all_entries_by_cat_distinct

        def flatten_image_urls():
            for cat_name, entries in list_entries_by_cat(entries_dbs):
                for entry in entries:
                    images = entry["images"]
                    for img in images:
                        assert "https://images.asos-media.com/" in img["url"], img
                        assert len(img["url"].split("/")) == 6, img
                        yield img["url"]

        def create_download_jobs(image_urls):
            jobs = [{"url": img_url, "path": self.brand_path.relative_image_path_from_url(img_url)}
                    for img_url in tqdm(image_urls, desc="Create Dst-Paths")]
            jobs_d = distinct_list_of_dicts(jobs, key="url")
            return [(x["url"], x["path"]) for x in jobs_d]
        ##for dl nochmal nach exist filtern (sequenz.) und beim dl job (para) exist verbieten
        img_urls = list(flatten_image_urls())
        download_jobs = create_download_jobs(img_urls)
        _threads = min(self.threads, len(download_jobs))

        with Pool(_threads) as p:
            list(
                tqdm(p.imap(DownloadHelper.download_image, download_jobs), desc=f"Download Images - {_threads} Threads",
                     total=len(download_jobs)))
            self.logger.debug("Download Images [Done]")

    @staticmethod
    def download_image(job):
        url, dst = job
        download_file(url=url, path=dst, exist_ok=True)

    @staticmethod
    def _download_entry(entry, asos):
        try:
            return {**entry, **asos.show(entry["url"])}
        except Exception as e:
            logger = defaultLogger("asos")
            logger.error("Prop-Unknown-Container " + entry["url"])
            #print("Prop-Unknown-Container", entry["url"])
            #raise e

    @staticmethod
    def _download_entries(entries):
        with d_driver(headless=False) as driver:
            asos = Asos(driver=driver)
            d = [DownloadHelper._download_entry(entry, asos) for entry in entries]
            return [x for x in d if x]
