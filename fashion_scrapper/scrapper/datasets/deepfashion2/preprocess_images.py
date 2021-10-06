import os
from pathlib import Path
from tqdm.auto import tqdm
from scrapper.util.io import list_dir_abs_path, load_img, save_image
import albumentations as A
from scrapper.util.parallel_proggraming import calc_chunksize
from tqdm.contrib.concurrent import thread_map
from multiprocessing.dummy import freeze_support
from multiprocessing import RLock
tqdm.set_lock(RLock())

images_path = Path(f'F:/workspace/datasets/DeepFashion2 Dataset/train/images')
masks_path = Path(f'F:/workspace/datasets/DeepFashion2 Dataset/train/annotations')

resized_img_path = Path(f'F:/workspace/datasets/DeepFashion2 Dataset/train_256/images')
resized_msk_path = Path(f'F:/workspace/datasets/DeepFashion2 Dataset/train_256/annotations')

def create_job(src_path, dst_path):
    src_abs_path = list_dir_abs_path(src_path)
    dst_abs_imgs = map(lambda x: dst_path/x, os.listdir(src_path))
    dst_abs_imgs = list(dst_abs_imgs)

    return zip(src_abs_path, dst_abs_imgs)

def filter_dst_not_exists(job):
    return not job[1].exists()

def transform_image(transformer):
    def __call__(job):
        src, dst = job
        try:
            img = load_img(src)
            img_transformed = transformer(image=img)["image"]
            save_image(img_transformed, dst)
            return 1
        except:
            return 0
    return __call__

if __name__ == "__main__":
    freeze_support()

    transform = A.Compose([
        A.Resize(width=256, height=256),
        #A.RandomCrop(width=244, height=244),
    ])

    image_transform_jobs = list(create_job(images_path, resized_img_path))
    mask_transform_jobs = list(create_job(masks_path, resized_msk_path))
    jobs = image_transform_jobs + mask_transform_jobs

    assert len(jobs) == (len(image_transform_jobs) + len(mask_transform_jobs))

    resized_img_path.mkdir(exist_ok=True, parents=True)
    resized_msk_path.mkdir(exist_ok=True, parents=True)

    jobs = list(filter(filter_dst_not_exists, tqdm(jobs, "Filter DST::Exists", total=len(jobs))))
    threads = 8
    chunk_size = calc_chunksize(n_workers=threads, len_iterable=len(jobs))

    r = thread_map(transform_image(transform), jobs, max_workers=threads, total=len(jobs),
                   chunksize=chunk_size, desc=f"Resize Images ({threads} Threads)")

    n_succ = sum(r)
    print(f"{n_succ} / {len(jobs)} = {100*n_succ/len(jobs)}%  Resized")

