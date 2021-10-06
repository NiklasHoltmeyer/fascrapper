from multiprocessing.dummy import freeze_support
from pathlib import Path
from tqdm.auto import tqdm
from PIL import Image
import os
import albumentations as A
from tqdm.contrib.concurrent import thread_map
import numpy as np
#from default_logger.defaultLogger import defaultLogger
from scrapper.datasets.deepfashion2.deepfashion2_preprocessor import save_image_PMODE, get_color_map_list
from scrapper.util.io import list_dir_abs_path, load_img, save_image
from scrapper.util.list import filter_is_dir
from scrapper.util.parallel_proggraming import calc_chunksize


def filter_dst_not_exists(job):
    return not job[1].exists()

def transform_image(transformer, hide_exceptions):
    def __call__(job):
        src, dst, is_mask = job
        try:
            img = np.array(load_img(src))
            img_transformed = transformer(image=img)["image"]

            if is_mask:
                save_image_PMODE(img_transformed, str(dst))
            else:
                save_image(img_transformed, dst)

            return 1
        except Exception as e:
            if hide_exceptions:
                return 0
            raise e

    return __call__


def batch_transform(src, dst, folders_to_resize, transform, threads=os.cpu_count() * 2):
    src, dst = Path(src), Path(dst)
#    logger = defaultLogger("Batch Transform Images")
    assert src.exists()

    assert all(map(lambda x: (src / x).exists(), folders_to_resize)), "Atleast one Folder doesnt exist"

    def resize_jobs(folders):
        for folder in folders:
            is_mask = "anno" in folder or "label" in "folder"
            (dst / folder).mkdir(exist_ok=True, parents=True)

            for file in os.listdir(src/folder):
                yield src/folder/file, dst/folder/file, is_mask

    def filter_not_dst_exists(job):
        return not job[1].exists()

#    logger.debug("List Images")
    print("List Images")
    jobs = list(resize_jobs(folders_to_resize))
    jobs = filter(filter_not_dst_exists, tqdm(jobs, desc="Filter DST::Exists", total=len(jobs)))
    jobs = list(jobs)

    hide_exceptions = False #len(jobs) > 100

    chunk_size = calc_chunksize(n_workers=threads, len_iterable=len(jobs))

#    logger.debug("Transform Images")
    print("Transform Images")

    if len(jobs) < 1:
        exit(0)

    r = thread_map(transform_image(transform, hide_exceptions), jobs, max_workers=threads, total=len(jobs),
                   chunksize=chunk_size, desc=f"Transform Images ({threads} Threads)")

    n_succ = sum(r)
#    logger.debug(f"{n_succ} / {len(jobs)} = {100*n_succ/len(jobs)}%  Resized")

    print(f"{n_succ} / {len(jobs)} = {100*n_succ/len(jobs)}%  Resized")

if __name__ == "__main__":
    freeze_support()
    transform = A.Compose([
        A.Resize(width=256, height=256),
        # A.RandomCrop(width=244, height=244),
    ])

    src_dir = r"F:\workspace\datasets\DeepFashion2 Dataset\train"
    dst_dir = r"F:\workspace\datasets\DeepFashion2 Dataset\train_256"
    folders_to_resize = ["annotations", "images"]

    batch_transform(src_dir, dst_dir, folders_to_resize, transform)
