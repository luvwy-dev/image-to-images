from PIL import Image
import numpy as np
import random

class Asset:
        image = None
        color = None

        def __init__(self, img):
            self.image = img

        def calcColor(self):
            image_array = np.array(self.image)
            if image_array.ndim == 2:
                rgb_image = np.stack((image_array,)*3, axis=-1)
            elif image_array.shape[2] == 3:
                rgb_image = image_array
            elif image_array.shape[2] == 4:
                rgb_image = image_array[:, :, :3]
            self.color = np.mean(rgb_image, axis=(0, 1)).astype(int)


def path_to_img(path, PIXEL_SIZE):
    if type(path) != str:
        return path
    img = Image.open(path)
    
    width, height = img.size
    min_dim = min(width, height)
    
    left = (width - min_dim) // 2
    upper = (height - min_dim) // 2
    right = left + min_dim
    lower = upper + min_dim
    
    cropped_img = img.crop((left, upper, right, lower))
    resized_img = cropped_img.resize((PIXEL_SIZE, PIXEL_SIZE))
    
    return resized_img

def pixel_to_asset(pixel, TRIES_PER_PIXEL, assets):
    best = [1000, None] # Error, asset

    for _ in range(TRIES_PER_PIXEL):
        asset = random.choice(assets)
        error = pixel - asset.color
        error = map(abs, error)
        error = sum(error)
        if error < best[0]:
            best[0] = error
            best[1] = asset
            
    return best[1]