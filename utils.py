import os, shutil
from glob import glob

import cv2
import numpy as np
import matplotlib.pyplot as plt


def crop_center(img, cropx, cropy):
    y, x, _ = img.shape
    startx = x // 2 - (cropx // 2)
    starty = y // 2 - (cropy // 2)
    return img[starty:starty + cropy, startx:startx + cropx, :]


def prepare_data(dir_path, hr_reso=256, lr_reso=64):
    img_list, img_low_list = [], []
    for img_path in glob(dir_path + '/*.png'):
        img = cv2.imread(img_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_crop = crop_center(img, hr_reso, hr_reso)
        img_list.append(img_crop)
        img_low_list.append(cv2.resize(img_crop, (lr_reso, lr_reso)))

    high_reso_imgs = np.array(img_list)
    low_reso_imgs = np.array(img_low_list)
    return high_reso_imgs, low_reso_imgs


def plot_predict(low_reso_imgs, high_reso_imgs, srgan_model, n_imgs=4):
    plt.figure(figsize=(12, 12))
    plt.tight_layout()
    for i in range(0, n_imgs * 3, 3):
        idx = np.random.randint(0, low_reso_imgs.shape[0] - 1)
        plt.subplot(n_imgs, 3, i + 1)
        plt.imshow(high_reso_imgs[idx])
        plt.grid('off')
        plt.axis('off')
        plt.title('Source')
        plt.subplot(n_imgs, 3, i + 2)
        plt.imshow(cv2.resize(low_reso_imgs[idx], (256, 256),
                              interpolation=cv2.INTER_CUBIC))
        plt.grid('off')
        plt.axis('off')
        plt.title('X4 (bicubic)')

        img = srgan_model.generator.predict(np.expand_dims(low_reso_imgs[idx], axis=0) / 127.5 - 1)
        img_unnorm = (img + 1) * 127.5
        plt.subplot(n_imgs, 3, i + 3)
        plt.imshow(np.squeeze(img_unnorm, axis=0).astype(np.uint8))
        plt.grid('off')
        plt.axis('off')
        plt.title('SRGAN')

    plt.savefig('predicted.png')
