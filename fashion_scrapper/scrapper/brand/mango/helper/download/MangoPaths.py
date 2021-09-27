from pathlib import Path
from urllib.parse import urlparse

from scrapper.brand.mango.webelements.MangoWebElements import Mango_Selectors


class MangoPaths:
    def __init__(self, BASE_PATH):
        self.BASE_PATH = BASE_PATH

    def relative_image_path(self, URL, create=True):  # falscher name -> eig. relative cat path
        category = MangoPaths.category_from_url(URL)# relative_url <- geht safe
        p = Path(self.BASE_PATH, category)
        if create:
            p.mkdir(parents=True, exist_ok=True)
        return p

    def relative_img_real_path(self, image_url):
        """
        "https://st.mngbcn.com/rcs/pics/static/T1/fotos/outfit/S20/17060293_01-99999999_01.jpg?ts=1620389591187&imwidth=630&imdensity=1"
        -> "'/outfit/S20/17060293_01-99999999_01.jpg'"
        :param image_url: Full Image-URL
        :return: relative Path to File
        """
        return urlparse(image_url).path.split("/fotos")[-1]

    @staticmethod
    def category_from_url(URL):
        cats_path = MangoPaths.remove_file_from_url(MangoPaths.relative_url(URL))
        cats_clean = "/".join([x for x in cats_path.split("/") if len(x) > 0])
        return cats_clean

    @staticmethod
    def relative_url(URL):
        return URL.replace(Mango_Selectors.URLS.BASE_FULL, "") \
                    .replace(Mango_Selectors.URLS.BASE_FULL.replace("//", "/"), "")

    @staticmethod
    def remove_file_from_url(URL):
        last_file = URL.split("/")[-1]
        if "." in last_file:
            return URL.replace(last_file, "")
        return URL

