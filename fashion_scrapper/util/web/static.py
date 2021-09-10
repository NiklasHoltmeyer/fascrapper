def find_first_parent_href(element, depth=0, max_depth=None):
    if max_depth and depth >= max_depth:
        raise Exception("not implemented")

    element = element.parent

    if "href" in element.attrs.keys():
        return element["href"]

    return find_first_parent_href(element, depth=depth + 1)
