import os
from collections import defaultdict


def list_dbs_by_category(db_base_Path, CATEGORIES):
    def category_by_filename(file_name, db_base_Path):
        for cat in CATEGORIES:
            if cat["name"] in file_name:
                return cat["name"]
            for inc in cat["includes"]:
                if inc in file_name:
                    return cat["name"]
        raise Exception("Unknown Category:", file_name, db_base_Path)
    db_with_cat = [(category_by_filename(x, str(db_base_Path)), db_base_Path / x) for x in os.listdir(str(db_base_Path))]
    db_names = defaultdict(lambda: [])

    for cat_name, db_path in db_with_cat:
        db_names[cat_name].append(db_path)
    return db_names