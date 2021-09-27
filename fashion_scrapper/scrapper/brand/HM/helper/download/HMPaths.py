from pathlib import Path

from default_logger.defaultLogger import defaultLogger
from scrapper.brand.hm.webelements.consts.HM_Selectors import HM_Selectors
from urllib.parse import unquote
from urllib import parse

class HMPaths:
    def __init__(self, BASE_PATH):
        self.BASE_PATH = BASE_PATH

    def get_entries_db_base_path(self):
        return Path(self.BASE_PATH, "entries_db")

    def get_category_db_base_path(self):
        return Path(self.BASE_PATH, "categories_db")

    def relative_image_path_backup(self, URL, create=True):  # falscher name -> eig. relative cat path
        category = HMPaths.category_from_url(URL)# relative_url <- geht safe
        p = Path(self.BASE_PATH, category)
        if create:
            p.mkdir(parents=True, exist_ok=True)
        return p

    def relative_image_path_from_url(self, URL, create=True):  # falscher name -> eig. relative cat path
        URL = URL.replace("https:https://", "https://")
        try:
            if URL.startswith("https://lp2.hm.com/"):
                return self._relative_img_path_from_url_decoded(URL, create)
            elif URL.startswith("https://image.hm.com"):
                return self._relative_img_path_from_url_clean_url(URL, create)
            else:
                raise Exception(f"relative_image_path_from_url ({URL})")
        except Exception as e:
            defaultLogger("HMPaths").error(URL)
            raise e #https://image.hm.com/assets/hm/8d/9d/8d9d4f54bb5833a3940da4fce3f3f3b9529b98e1.jpg?cat=ladies_dresses_aline&type=DESCRIPTIVEDETAIL&imwidth=657

    def _relative_img_path_from_url_decoded(self, URL, create=True):  # falscher name -> eig. relative cat path
        """

        :param URL: e.G. https://lp2.hm.com/hmgoepprod?set=quality%5B79%5D%2Csource%5B%2Fb3%2F39%2Fb33921c87fd00e8ef15831e82bede44f92753cf3.jpg%5D%2Corigin%5Bdam%5D%2Ccategory%5Bladies_trousers_chinosslacks%5D%2Ctype%5BLOOKBOOK%5D%2Cres%5Bm%5D%2Chmver%5B1%5D&call=url[file:/product/main]
        :param create: Create Path
        :return: {BASE_PATH}\pics\b3_39\b33921c87fd00e8ef15831e82bede44f92753cf3.jpg
        """
        url_cleaned = unquote(URL)
        url_cleaned = parse.parse_qs(parse.urlsplit(url_cleaned).query)["set"][0]
        url_cleaned = url_cleaned.split("source[")[1].split("]")[0]

#       url_splitted = (url_cleaned.split("/"))
#        relative_path, file_name = "_".join([x for x in url_splitted[:-1] if len(x) > 0]), url_splitted[-1]

#        p = Path(f"{self.BASE_PATH}/pics/{relative_path}/{file_name}")
        p = Path(f"{self.BASE_PATH}/pics/{url_cleaned}")

        if create:
            p.parent.mkdir(parents=True, exist_ok=True)
        return p

    def _relative_img_path_from_url_clean_url(self, URL, create=True):
        """

        :param URL: e.G. https://image.hm.com/assets/hm/8d/9d/8d9d4f54bb5833a3940da4fce3f3f3b9529b98e1.jpg?cat=ladies_dresses_aline&type=DESCRIPTIVEDETAIL&imwidth=657
        :param create: Create Path
        :return: ##{BASE_PATH}\pics\b3_39\b33921c87fd00e8ef15831e82bede44f92753cf3.jpg
        """
        url = URL.split("?")[0].replace("https://image.hm.com/assets/hm/", "")

#        url_splitted = url.split("/")
#        relative_path, file_name = "/".join(url_splitted[:-1]), url_splitted[-1]

        #p = Path(f"{self.BASE_PATH}/pics/{relative_path}/{file_name}")
        p = Path(f"{self.BASE_PATH}/pics/{url}")

        if create:
            p.parent.mkdir(parents=True, exist_ok=True)
        return p


    def list_all_images(self):
        pics_base = Path(self.BASE_PATH, "pics")
        pics = filter(lambda x: x.is_file(), pics_base.rglob("*"))
        return list(pics)

    @staticmethod
    def category_from_url(URL):
        return URL.replace(HM_Selectors.URLS.BASE_FULL, "").replace(".html", "")
