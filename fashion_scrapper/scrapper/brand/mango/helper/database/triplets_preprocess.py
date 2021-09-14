from random import shuffle
import numpy as np
from scrapper.brand.mango.helper.database.filter import filterd_entries, validate_triplets
from scrapper.util.io import walk_entries
from scrapper.util.list import flatten, idx_self_reference

import pandas as pd


def as_df(triplets):
    anchors = [x["anchor"] for x in triplets]
    positives = [x["positive"] for x in triplets]
    negatives = [x["negative"] for x in triplets]

    triplet_df = pd.DataFrame()

    triplet_df["a_id"] = [x["id"] for x in anchors]
    triplet_df["a_view"] = [x["view"] for x in anchors]
    triplet_df["a_path"] = [x["path"] for x in anchors]

    triplet_df["p_id"] = [x["id"] for x in positives]
    triplet_df["p_view"] = [x["view"] for x in positives]
    triplet_df["p_path"] = [x["path"] for x in positives]

    triplet_df["n_id"] = [x["id"] for x in negatives]
    triplet_df["n_view"] = [x["view"] for x in negatives]
    triplet_df["n_path"] = [x["path"] for x in negatives]
    return triplet_df


def _random_references(num_idxs, max_retries=150):
    random_idxs = list(range(num_idxs))
    for _ in range(max_retries):
        shuffle(random_idxs)  # in place
        if not idx_self_reference(random_idxs):
            break
    return np.array(random_idxs)  # copy -> None otherwise


def preprocess_negative_entries(anchor_items):
    negative_items = np.array(anchor_items)
    shuffle(negative_items)

    def __clean_entry(entry):
        return [{**x, 'id': entry["id"]} for x in entry["images"]]

    assert len(anchor_items) == len(negative_items)
    negative_items = [__clean_entry(x) for x in negative_items]
    negative_flat = flatten(negative_items)

    shuffle(negative_flat)

    return negative_flat


def build_positive_anchors(entry):
    images_anchor, anchor_id = entry["images"], entry["id"]
    positive_idxs = _random_references(len(images_anchor))
    images_positives = [images_anchor[idx] for idx in positive_idxs]
    return [{"anchor": {**a, "id": anchor_id}, "positive": {**p, "id": anchor_id}} for (a, p) in
            zip(images_anchor, images_positives)]


def preprocess_positive_entries(entries):
    return flatten([build_positive_anchors(entry) for entry in entries])


def build_triplets(path):
    entries = walk_entries(path)
    anchor_items = (list(filterd_entries(entries)))
    negative_items = np.array(anchor_items)
    shuffle(negative_items)

    assert len(anchor_items) == len(negative_items)

    negative_items = preprocess_negative_entries(anchor_items)
    positive_items = preprocess_positive_entries(anchor_items)
    assert len(negative_items) == len(positive_items)

    data = []
    for row in positive_items:
        anchor_id, positive_id = row["anchor"]["id"], row["positive"]["id"]
        negative_anchor = None

        while not negative_anchor:
            possible_n_anchor = negative_items.pop()
            if possible_n_anchor["id"] != anchor_id:
                negative_anchor = possible_n_anchor
            elif len(negative_items) < 2:  # for the random chance of only the same id beeing left
                break
            else:
                negative_items.insert(0, possible_n_anchor)

        data.append({**row, "negative": negative_anchor})
    validate_triplets(data)
    return data

if __name__ == "__main__":
    triplets_df = as_df(build_triplets(r"F:\workspace\fascrapper\scrap_results\mango"))
    print("Columns", triplets_df.columns)
    print(triplets_df.head(3))
