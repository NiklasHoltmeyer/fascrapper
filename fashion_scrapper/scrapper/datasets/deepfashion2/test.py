from multiprocessing.dummy import freeze_support
from pathlib import Path

import albumentations as A
import numpy as np

from scrapper.datasets.deepfashion2.deepfashion2_preprocessor import DeepFashion2Preprocessor

annotations_path, images_path = (Path(f'F:/workspace/datasets/DeepFashion2 Dataset/train/annos'),
                                 Path(f'F:/workspace/datasets/DeepFashion2 Dataset/train/image'))

coco_train_path = r"F:\workspace\datasets\DeepFashion2 Dataset\train\train_coco.json"

preprocessor_settings = {
    "annotations_path": annotations_path,
    "images_path": images_path,
    "IGNORE_CHECK": True,
    "threads": 8,
}

if __name__ == '__main__':
    freeze_support()

    preprocessor = DeepFashion2Preprocessor(**preprocessor_settings)

    transform = A.Compose([
        A.Resize(width=256, height=256),
        A.RandomCrop(width=244, height=244),
        #    A.HorizontalFlip(p=0.5),
        #    A.RandomBrightnessContrast(p=0.2),
    ], bbox_params=preprocessor.BboxParams())

    preprocessor.semantic_segmentation(coco_train_path)
    exit(0)
    r_true, r_false = preprocessor.bounding_boxes(transform)

    try:
        np.save(r"F:/workspace/datasets/DeepFashion2 Dataset/train/244x244_true", r_true)
    except Exception as e:
        print(str(e))

    try:
        np.save(r"F:/workspace/datasets/DeepFashion2 Dataset/train/244x244_false", r_false)
    except Exception as e:
        print(str(e))
