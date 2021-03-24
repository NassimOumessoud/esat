from pathlib import Path

import cv2


def analyse(path):
    for impath in Path(path).iterdir():
        image = cv2.imread(str(impath))


def run(*paths, outfolder="esat_results"):
    embryos = [analyse(path) for path in paths]
