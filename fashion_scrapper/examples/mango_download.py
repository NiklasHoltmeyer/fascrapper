from default_logger.defaultLogger import defaultLogger
from scrapper.brand.mango.Mango import Mango
from scrapper.brand.mango.helper.download.DownloadHelper import DownloadHelper
from scrapper.util.io import Json_DB
from scrapper.util.web.dynamic import driver as d_driver
from tqdm.auto import tqdm

BASE_PATH = r"F:\workspace\fascrapper\scrap_results\mango"
CATEGORY_FILTER = lambda x: "shirt" in x

logger = defaultLogger("Mango")

with d_driver() as driver:
    mango = Mango(driver=driver, logger=logger)

    dl_settings = {
        "visited_db": Json_DB(BASE_PATH, "visited.json"),
        "logger": logger,
        "mango": mango,
        "BASE_PATH": BASE_PATH
    }
    dl_helper = DownloadHelper(**dl_settings)

    categories = mango.list_categories("https://shop.mango.com/de/herren")
    categories_filterd = [x for x in categories if CATEGORY_FILTER(x)]
    print("Categories", len(categories_filterd), categories_filterd)

    responses = [dl_helper.download_images(x, IGNORE_CATEGORY_EXISTING=True) \
                 for x in tqdm(categories_filterd, desc="Download Category")]

    for response in responses:
        print(response)
