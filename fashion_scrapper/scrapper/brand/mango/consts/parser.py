from default_logger.defaultLogger import defaultLogger

BASE_PATH = r"F:\workspace\fascrapper\scrap_results\mango"
CATEGORIES = [
    {"name": "schuhe", "includes": ["sneaker", "schuhe"], "excludes": ["edits/sneakers"]},
    {"name": "hose", "includes": ["short", "jeans", "rocke", "hose"], "excludes": []},
    {"name": "shirt", "includes": ["shirt", "hemd", "blazer"], "excludes": []},
    {"name": "pullover", "includes": ["pullover"], "excludes": []},
    {"name": "jacke", "includes": ["jacke", "mantel"], "excludes": []},
    {"name": "kleid", "includes": ["kleid"], "excludes": ["kleidung"]},
    {"name": "anzug", "includes": ["anzug", "overalls"], "excludes": []}
]

THREADS = 8
FORCE_RESCAN = True
logger = defaultLogger("Mango")