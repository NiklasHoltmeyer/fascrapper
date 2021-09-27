from scrapper.brand.hm.helper.database.dbhelper import list_dbs_by_category
from scrapper.brand.hm.consts.parser import (CATEGORIES as HM_CATEGORIES, BASE_PATH as HM_BASE_PATH)

##['id', 'images'], 'images' = ['view', 'path', {...}, ...]
from scrapper.brand.hm.helper.download.HMPaths import HMPaths
from scrapper.brand.hm.webelements.consts.HM_Selectors import HM_Selectors
from scrapper.util.io import Json_DB
from scrapper.util.list import distinct_list_of_dicts, flatten


def list_hm_entries_by_cat(category_name):
    def clean_entry(entry):
        return {"id": entry["url"].replace(HM_Selectors.URLS.BASE, ""),
                "images": [{"path": brand_path.relative_image_path_from_url(img["url"]), "view": img["name"]}
                           for img in entry["images"]]}

    brand_path = HMPaths(HM_BASE_PATH)
    entries_db_path = brand_path.get_entries_db_base_path()
    entries = list_dbs_by_category(entries_db_path, HM_CATEGORIES)
    entries_by_cat_distinct = distinct_list_of_dicts(flatten([Json_DB(x).all() for x in entries[category_name]]),
                                                     key="url")

    anchor_items = list(map(clean_entry, entries_by_cat_distinct))
    return anchor_items
