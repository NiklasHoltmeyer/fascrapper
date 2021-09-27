class Mango_Categories_Elements:
    """ List all Categories withing an Category ()
        Top-(Level)-Categories: Male, Female, ...
        Sub-Categories: T-Shirt, Shorts, ...
    """

    def __init__(self, web_elements):
        self.elements = web_elements
        self.driver = web_elements.driver
        self.logger = web_elements.logger

    def load_sub_categories(self, url):
        self.logger.debug(f"Loading Sub Category {url}")
        self.driver.get(url)
        header = self.elements.header()
        hrefs = header.find_all(href=True)
        hrefs = [{'href': href["href"], "text": href.text} for href in hrefs]
        cat_top, cat_sub = [], []

        for href in hrefs:
            if (len(href["href"].split("/"))) == 5:
                cat_top.append(href)
            else:
                cat_sub.append(href)

        assert len(hrefs) == len(cat_top) + len(cat_sub)

        return cat_top, cat_sub

    def list_categories(self, url):
        visited_links = []
        urls = [url]
        categories = []

        while len(urls) > 0:
            url = urls.pop()
            cat_top, cat_sub = self.load_sub_categories(url)
            visited_links.append(url)

            categories.extend(cat_top)
            categories.extend(cat_sub)

            for x in cat_top:
                if not x["href"] in visited_links:
                    urls.append(x["href"])

        return categories
