from pathlib import Path

from scrapper.brand.asos.webelements.consts.Asos_Selectors import Asos_Selectors


class AsosPaths:
    def __init__(self, BASE_PATH):
        self.BASE_PATH = BASE_PATH

    def get_entries_db_base_path(self):
        return Path(self.BASE_PATH, "entries_db")

    def get_category_db_base_path(self):
        return Path(self.BASE_PATH, "categories_db")

    def relative_image_path_backup(self, URL, create=True):  # falscher name -> eig. relative cat path
        category = AsosPaths.category_from_url(URL)# relative_url <- geht safe
        p = Path(self.BASE_PATH, category)
        if create:
            p.mkdir(parents=True, exist_ok=True)
        return p

    def relative_image_path_from_url(self, URL, create=True):  # falscher name -> eig. relative cat path
        img_relative_path = URL.replace(Asos_Selectors.URLS.BASE_IMAGE_URL, "")
        #img_relative_file_path = img_relative_path + ".webp"

        p = Path(self.BASE_PATH, "pics", img_relative_path)
        if create:
            p.parent.mkdir(parents=True, exist_ok=True)
        return p

    def list_all_images(self):
        pics_base = Path(self.BASE_PATH, "pics")
        pics = filter(lambda x: x.is_file(), pics_base.rglob("*"))
        return list(pics)

    @staticmethod
    def category_from_url(URL):
        _url = URL.replace(Asos_Selectors.URLS.BASE, "")
        _url_splitted = _url.split("?")

        if len(_url_splitted) > 2:
            raise Exception(f"TODO: {URL}")

        _url = _url if len(_url_splitted) == 0 else _url_splitted[:-1][0]

        if _url.endswith("/cat/"):
            _url = _url[:-5]  # -> remove /cat/
        return _url