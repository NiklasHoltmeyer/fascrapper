from pathlib import Path

from scrapper.util.io import Json_DB
from default_logger.defaultLogger import defaultLogger


BASE_PATH = r"F:\workspace\fascrapper\scrap_results\hm"
THREADS = 8
PAGINATE = True

logger = defaultLogger("H&M")

CATEGORIES = [
    { "name": "schuhe", "includes": ["schuhe"], "excludes": ["schuhe-accessoires"]},
    { "name": "hose", "includes": ['hosen', "jeans", "roecke", "shorts"], "excludes": [""]},
    {"name": "shirt", "includes": ["shirt", 'blazer-westen', "hemden", "top"], "excludes": []},
    {"name": "pullover", "includes": ["pullover",'cardigan', "hoodies", "westen"], "excludes": []},
    {"name": "jacke", "includes": ['jacke',], "excludes": []},
    {"name": "kleid", "includes": ["kleider"], "excludes": []},
    {"name": "anzug", "includes": [], "excludes": []}]

excludes = ["-accessoires"]

Path(BASE_PATH).mkdir(parents=True, exist_ok=True)

dl_settings = {
            "base_path": BASE_PATH,
            "visited_db": Json_DB(BASE_PATH, "visited_hm.json"),
            "logger": logger,
            "threads": THREADS
}
