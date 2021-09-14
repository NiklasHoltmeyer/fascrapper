from pathlib import Path
from urllib.parse import urlparse

from scrapper.brand.mango.webelements.WebElements import Mango_Selectors


class MangoPaths:
    def __init__(self, BASE_PATH):
        self.BASE_PATH = BASE_PATH

    def relative_image_path(self, URL, create=True):  # falscher name -> eig. relative cat path
        category = URL.replace(Mango_Selectors.URLS.BASE_FULL, "")
        p = Path(self.BASE_PATH, category)
        if create:
            p.mkdir(parents=True, exist_ok=True)
        return p

    def relative_img_real_path(self, image_url):
        return urlparse(image_url).path.split("/fotos")[-1]
