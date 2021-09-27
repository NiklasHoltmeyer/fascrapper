from scrapper.util.io import Json_DB
from default_logger.defaultLogger import defaultLogger


BASE_PATH = r"F:\workspace\fascrapper\scrap_results\asos"
THREADS = 3
PAGINATE = True
IGNORE_EXISTING = False
unknown_category_allowed = True
save_frequency = 1.0

logger = defaultLogger("asos")

CATEGORIES = [
    {"name": "schuhe", "includes": ["shoe"], "excludes": []},
    {"name": "hose", "includes": ["short", "jeans", "leggings", "trousers"], "excludes": []},
    {"name": "shirt", "includes": ["shirt", "skirt", "blazer", "top"], "excludes": []},
    {"name": "pullover", "includes": ["pullover", "cardigans"], "excludes": []},
    {"name": "jacke", "includes": ["coat"], "excludes": []},
    {"name": "kleid", "includes": ["dresses"], "excludes": ["kleidung"]},
    {"name": "anzug", "includes": ["suit", "overalls"], "excludes": []}
]

excludes = ["sale", "view+all", "new-in-clothing", "accessories", "face-body", "topshop", "back-in-stock", \
            "fashion-online-4", "curve-plus-size", "maternity", "petite", "tall", "fashion-online-12", "generic-promos", \
            "designer", "a-to-z-of-brands", "exclusives", "activewear", "co-ords", "multipacks", "bags", \
            "bras", "fashion-online-", "yoga-studio", "ski-snowboard", "running", "outdoors", "ss-fashion-trend-", \
            "gym-training", "gifts", "wedding-attire", "underwear", \
            "plus-size", "outlet-edits", "back-to-school", "modestwear", "socks-tights", "swim", "lingerie", \
            "loungewear", "-essentials", "responsible-edit", "wedding", "workwear", "jewellery", "sunglasses",
            "party-wear", \
            "licence"]

dl_settings = {
            "base_path": BASE_PATH,
            "visited_db": Json_DB(BASE_PATH, "visited.json"),
            "logger": logger,
            "threads": THREADS
}

