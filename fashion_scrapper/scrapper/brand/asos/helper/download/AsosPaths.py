from pathlib import Path

from scrapper.brand.asos.webelements.consts.Asos_Selectors import Asos_Selectors


class AsosPaths:
    def __init__(self, BASE_PATH):
        self.BASE_PATH = BASE_PATH

    def relative_image_path(self, URL, create=True):  # falscher name -> eig. relative cat path
        category = AsosPaths.category_from_url(URL)# relative_url <- geht safe
        p = Path(self.BASE_PATH, category)
        if create:
            p.mkdir(parents=True, exist_ok=True)
        return p

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