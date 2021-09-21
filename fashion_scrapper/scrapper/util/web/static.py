from pathlib import Path

import requests


def find_first_parent_href(element, depth=0, max_depth=None):
    if max_depth and depth >= max_depth:
        raise Exception("not implemented")

    element = element.parent

    if "href" in element.attrs.keys():
        return element["href"]

    return find_first_parent_href(element, depth=depth + 1)

def download_file(url, path, exist_ok = False):
    if path.exists():
        if exist_ok:
            return
        raise Exception(f"{path} already exists!")

    response = requests.get(url)
    if not response.ok:
        raise Exception(f"Request failed. Status_Code: {response.status_code}")

    with open(path, 'wb') as f:
        f.write(response.content)





