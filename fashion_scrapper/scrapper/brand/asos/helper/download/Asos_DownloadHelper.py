import os
from collections import defaultdict
from datetime import datetime
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from PIL import Image
from tinydb import where
from tqdm.auto import tqdm
from default_logger.defaultLogger import defaultLogger
from scrapper.brand.asos.Asos import Asos
from scrapper.brand.asos.helper.download.AsosPaths import AsosPaths
from scrapper.util.io import Json_DB, time_logger
from scrapper.util.list import flatten, distinct_list_of_dicts
from scrapper.util.web.dynamic import driver as d_driver
from scrapper.util.web.static import download_file
import pandas as pd


class Asos_DownloadHelper:
    def __init__(self, **args):
        self.visited_db = args.get("visited_db")
        self.logger = args.get("logger")
        self.base_path = args.get("base_path")
        self.brand_api = args.get("brand_api")
        self.brand_path = AsosPaths(self.base_path)
        self.threads = args.get("threads", os.cpu_count())

    @staticmethod
    def load_category(cat_data, PAGINATE=True):
        category_name, category_url = cat_data
        try:
            with d_driver(headless=False) as driver:
                asos = Asos(driver=driver, logger=None)
                items = asos.list_category(category_url, PAGINATE=PAGINATE)
                return [{"success": True, "name": category_name, "cat_url": category_url, "items": [x],
                         "cat_path": AsosPaths.category_from_url(category_url).replace("/", "_")} for x in items]
        except Exception as e:
            return [{"success": False, "name": category_name, "url": category_url, "exception": str(e)}]

    #    @time_logger(name="Prepare Categories", header="DL-Helper", padding_length=50)

    def prepare_categories(self, category_jobs, IGNORE_CATEGORY_EXISTING=False):
        jobs_iter = tqdm(category_jobs, "Prepare Category")
        jobs_iter = map(lambda j: self.prepare_sub_categories(j, IGNORE_CATEGORY_EXISTING=IGNORE_CATEGORY_EXISTING),
                        jobs_iter)
        exceptions = flatten(list(jobs_iter))
        return exceptions

    def prepare_sub_categories(self, sub_category_jobs, IGNORE_CATEGORY_EXISTING=False):

        def filter_category_downloaded(job, force=IGNORE_CATEGORY_EXISTING):
            return force or len(self.visited_db.search(where('url') == job[1])) == 0

        sub_category_jobs = list(filter(filter_category_downloaded, sub_category_jobs))

        #        @time_logger(name="load_categories", header="DL-Helper load_categories", padding_length=50)
        def load_categories(jobs):
            _threads = min(self.threads, len(jobs))
            if _threads < 1:
                return []
            with Pool(_threads) as p:
                r = list(
                    tqdm(p.imap(Asos_DownloadHelper.load_category, jobs), desc=f"Prepare Categories - {_threads} Threads",
                         total=len(jobs), mininterval=30))
                return flatten(r)

        results = load_categories(sub_category_jobs)

        def flatten_result(result):
            if not result["success"]:
                return [result]

            result_items = result.pop("items", None)
            if not result_items:
                print(result)
                raise Exception("prepare_categories::flatten_result #TODO")
            return [{**result, **x} for x in result_items]

        #        @time_logger(name="group_results_by_category", header="DL-Helper group_results_by_category", padding_length=50)
        def group_results_by_category(results):
            grouped_results = defaultdict(lambda: [])
            exceptions = []
            flatten_results = flatten(map(flatten_result, results))
            for result in flatten_results:
                if result["success"]:
                    grouped_results[result["cat_path"]].append(result)
                else:
                    exceptions.append(result)
            return grouped_results, exceptions

        results_grouped, exceptions = group_results_by_category(results)

        #        @time_logger(name="save_visited_categories", header="DL-Helper save_visited_categories", padding_length=50)
        def save_visited_categories(results_grouped):

            #            @time_logger(name="insert_items", header="dl::save_visited_categories::insert_items", padding_length=50)
            def insert_items(cat_path, entries):
                db_path = self.brand_path.get_category_db_base_path() / f"{cat_path}.json"
                db_path.parent.mkdir(parents=True, exist_ok=True)

                with Json_DB(db_path) as db:
                    db_all = db.all()
                    clean_item = lambda item: {'id': item["id"], 'url': item["url"]}
                    items = filter(lambda item: not Asos_DownloadHelper.filter_entries_by_id(db_all, item["id"]), entries)
                    items = list(map(clean_item, items))
                    db.insert_multiple(items)

            for cat_path, entries in results_grouped.items():
                insert_items(cat_path, entries)
                cat_url = entries[0]["cat_url"]
                if filter_category_downloaded(cat_url, False):
                    self.visited_db.insert({'url': cat_url, 'last_visit': datetime.now()})
            self.visited_db.storage.flush()

        save_visited_categories(results_grouped)
        return exceptions

    @staticmethod
    def filter_entries_by_id(db_all, id):  # <- in memory
        return Asos_DownloadHelper.find_first(db_all, "id", id)

    @staticmethod
    def find_first(db_all, key, value):
        for entry in db_all:
            if entry[key] == value:
                return True
        return False

    #    @time_logger(name="Prepare Articles", header="DL-Helper", padding_length=50)
    def prepare_articles(self, categories_db):
        """

        :param categories_db:
        :return:
        """

        def download_new(visited_db_path, cat_db):
            with Json_DB(visited_db_path) as db:
                existing_items = cat_db.all()

                new_entries = [entry for entry in db.all() if
                               not Asos_DownloadHelper.filter_entries_by_id(existing_items, entry["id"])]

                if len(new_entries) == 0:
                    return

                _threads = min(self.threads, len(new_entries))

                new_entries_splitted = np.array_split(new_entries, _threads)
                with Pool(_threads) as p:
                    entries = flatten(list(tqdm(p.imap(Asos_DownloadHelper._download_entries, new_entries_splitted),
                                                desc=f"Prepare Articles - {_threads} Threads",
                                                total=len(new_entries_splitted))))
                    cat_db.insert_multiple(entries)

        def download_entries_by_cat(cat_name, visited_paths):
            cat_db_path = Path(self.base_path, "entries_db", cat_name + ".json")
            cat_db_path.parent.mkdir(parents=True, exist_ok=True)

            with Json_DB(cat_db_path) as cat_db:
                for visited_db_path in visited_paths:
                    download_new(visited_db_path, cat_db)

        [download_entries_by_cat(cat_name, visited_paths) for (cat_name, visited_paths) in
         tqdm(categories_db.items(), desc=f"Walk Category DB")]

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

        img_urls = list(flatten_image_urls())
        download_jobs = create_download_jobs(img_urls)
        _threads = min(self.threads, len(download_jobs))

        with Pool(_threads) as p:
            return list(
                tqdm(p.imap(Asos_DownloadHelper.download_image, download_jobs), desc=f"Download Images - {_threads} Threads",
                     total=len(download_jobs)))

    def describe_results(self):
        @time_logger(name="List all Images", header="List all Images", padding_length=50)
        def load_imgs():
            pics_base = Path(self.base_path, "pics")
            pics = filter(lambda x: x.is_file(), pics_base.rglob("*"))
            pics = map(lambda x: str(x.resolve()), pics)
            return list(pics)

        def collect_result(r):
            img_infos, failed = [], []

            for path, info in r:
                if info:
                    img_infos.append({"path": path, **info})
                else:
                    failed.append(path)

            return img_infos, failed

        imgs = load_imgs()
        img_info_db_path = Path(self.base_path, "img_info.json")
        img_info_db_path.unlink(
            missing_ok=True)  # <- faster (factor > 100) to just create new, then to read old db and only insert new entries

        with Json_DB(img_info_db_path) as db, Pool(self.threads) as p:
            # all_entries = db.all()
            # new_img = lambda path: not DownloadHelper.find_first(all_entries, key="path", value=path)
            # imgs_new = list(filter(new_img, tqdm(imgs, desc="Filter IMG in Info-DB")))

            r = list(tqdm(p.imap(Asos_DownloadHelper.load_image_data, imgs), desc=f"Load IMG Info - {self.threads} Threads",
                          total=len(imgs)))

            img_infos, errors = collect_result(r)

            db.insert_multiple(img_infos)

            def group_by_format_count(df):
                countdict = defaultdict(lambda: 0)
                for format in df["format"]:
                    countdict[format] += 1
                return countdict.items()

            df = pd.DataFrame(img_infos)
            format = group_by_format_count(df)

            return {
                "db_path": img_info_db_path,
                "dataframe": df,
                "image_formats": format,
                "describe": df.describe(),
                "errors": errors
            }

    @staticmethod
    def download_image(job):
        url, dst = job
        try:
            download_file(url=url, path=dst, exist_ok=True)
            return None
        except Exception as e:
            return (url, dst, e)

    @staticmethod
    def load_image_data(path):
        try:
            img = Image.open(path)
            info = {"width": img.width, "height": img.height, "format": img.format}
            return (path, info)
        except:
            return (path, None)

    @staticmethod
    def _download_entry(entry, asos):
        try:
            return {**entry, **asos.show(entry["url"])}
        except Exception as e:
            logger = defaultLogger("asos")
            logger.error("Prop-Unknown-Container " + entry["url"])
            # print("Prop-Unknown-Container", entry["url"])
            # raise e

    @staticmethod
    def _download_entries(entries):
        with d_driver(headless=False) as driver:
            asos = Asos(driver=driver)
            d = [Asos_DownloadHelper._download_entry(entry, asos) for entry in entries]
            return [x for x in d if x]
