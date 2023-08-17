from multiprocessing import Pool, freeze_support
from itertools import repeat, starmap
from PIL import Image
import numpy as np
import generation
import sys
import os

def take_input(msg, t):
    while True:
        s = input(msg)
        try:
            s = t(s)
        except:
            print("Wrong type")
        else:
            return s

def main():

    SOURCE_IMAGES = input("Images folder name (only .jpg): ")
    ORIGINAL_NAME = input("Specify source image file: ")
    PIXEL_SIZE = take_input("Specify each image size (recommended 50): ", int)
    TRIES_PER_PIXEL = take_input("Specify tries per pixel (recommended 300): ", int)
    NEW_IMAGE_RATIO = take_input("Specify new image size ratio (recommended 0.4): ", float)

    if not os.path.isdir(SOURCE_IMAGES):
        print("No such directory:", SOURCE_IMAGES)
        quit()
    
    if not os.path.isfile(ORIGINAL_NAME):
        print("No such file:", ORIGINAL_NAME)
        quit()

    MULTIPLE_CORES = input("Use multiprocessing? [yes/no]: ")

    MULTIPLE_CORES = MULTIPLE_CORES == "yes"

    if MULTIPLE_CORES:
        CORES = take_input("How many processes to spawn: ", int)

    tree = os.walk(SOURCE_IMAGES)
    images = []

    for i in tree:
        for file in i[2]:
            if os.path.splitext(file)[1] == '.jpg':
                path = i[0] + '/'
                path += file
                images.append(path)

    print(f"Loaded {len(images)} images")

    print("Cropping and resizing..", end = " ")
    sys.stdout.flush()

    if MULTIPLE_CORES:
        p = Pool(CORES)
        images = p.starmap(generation.path_to_img, zip(images, repeat(PIXEL_SIZE)))
    else:
        images = starmap(generation.path_to_img, zip(images, repeat(PIXEL_SIZE)))

    print("ok")
    print("Generating assets and calculating average color..", end = " ")

    assets = []
    for img in images:
        a = generation.Asset(img)
        a.calcColor()
        assets.append(a)

    print("ok")

    source = Image.open(ORIGINAL_NAME)
    source = source.resize(( round(source.size[0] * NEW_IMAGE_RATIO), round(source.size[1] * NEW_IMAGE_RATIO)))
    source = np.array(source)

    h, w, _ = source.shape

    print("New image size relative:", h, w)
    print("New image size absolute:", h * PIXEL_SIZE, w * PIXEL_SIZE)
    print("Picking image for each pixel, calculating errors..", end = " ")
    sys.stdout.flush()

    finalAssets = source.reshape(h * w, 3)

    if MULTIPLE_CORES:
        p = Pool(CORES)
        finalAssets = p.starmap(generation.pixel_to_asset, zip(finalAssets, repeat(TRIES_PER_PIXEL), repeat(assets)))
    else:
        finalAssets = map(generation.pixel_to_asset, zip(finalAssets, repeat(TRIES_PER_PIXEL), repeat(assets)))

    print("ok")
    print("Building final image..", end = " ")

    sys.stdout.flush()

    new_size = (w * PIXEL_SIZE, h * PIXEL_SIZE)
    result = Image.new('RGB', new_size)

    # it is possible to run it multiprocessed, but it seems to be working fast
    for row in range(h):
        for col in range(w):
            idx = row * w + col # Index of the image
            result.paste(finalAssets[idx].image, (col * PIXEL_SIZE, row * PIXEL_SIZE))


    print("ok")
    print("Done. Saving as result.jpg")

    result.save("result.jpg")

if __name__ == '__main__':
    freeze_support()
    main()