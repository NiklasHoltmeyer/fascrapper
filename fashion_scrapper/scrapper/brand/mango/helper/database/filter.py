from random import sample

from scrapper.brand.mango.helper.download.MangoPaths import MangoPaths


def filterd_entries(entries, shuffle_images=True):
    """
    Filter Entries>Images by View
    """
    views_filter = ['Mittlere Ansicht', 'Allgemeine Ansicht', 'Rückseite des Artikels', 'Artikel ohne Model']
    for entry in entries:
        _id, images = MangoPaths.relative_url(entry["url"]), entry["images"]
        images_filterd = [{"view": x["description"], "path": x["path"]} for x in images if
                          x["description"] in views_filter]
        if shuffle_images:
            yield {"id": _id, "images": sample(images_filterd, len(images_filterd))}
        else:
            yield {"id": _id, "images": images_filterd}


