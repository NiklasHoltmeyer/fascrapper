from pathlib import Path

from scrapper.brand.mango.helper.download.MangoPaths import MangoPaths
from scrapper.util.io import Json_DB

SCRAP_PATH = r"F:\workspace\fascrapper\scrap_results\mango\shirt"

def get_databases(SCRAP_PATH):
    for db in Path(SCRAP_PATH).rglob('*data.json'):
        yield Json_DB(db)

for db in get_databases(SCRAP_PATH):
    data = db.all()
    for d in data:
        url = d["url"]
        cat = MangoPaths.category_from_url(url).split("/")
        if len(cat) != 2:
            print(url, cat)

    #print("/".join(url.split("/")[:-1]))
    #print("/".join(url.split("/")))


Asos()


