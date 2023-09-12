import numpy as np
import pyiqa
import torchvision.transforms.functional as F
from PIL import Image
from skimage import color, filters, img_as_ubyte, measure
from image_similarity_measures.quality_metrics import rmse, ssim, fsim, psnr, uiq


def pyiqa_single_image_score(image: Image.Image, model, device):
    iqa_metric = pyiqa.create_metric(model, metric_mode="NR", device=device)
    image_tensor = F.to_tensor(image).unsqueeze(0)
    return iqa_metric(image_tensor).cpu().item()


def sharpness_score(image: Image.Image):
    image = img_as_ubyte(image)
    gray_image = color.rgb2gray(image)
    return filters.sobel(gray_image).var()


def blur_score(image: Image.Image):
    image = img_as_ubyte(image)
    gray_image = color.rgb2gray(image)
    return filters.laplace(gray_image).var()


def noise_score(image: Image.Image):
    image = img_as_ubyte(image)
    return np.std(image)


def similarity(measure_fn, image: Image.Image, target: Image.Image):
    image = img_as_ubyte(image)
    target = img_as_ubyte(target)
    return measure_fn(org_img=image, pred_img=target)


def is_visual_duplicate(image: Image.Image, target: Image.Image):
    is_dup_ssim = similarity(ssim, image, target) > 0.95
    is_dup_fsim = similarity(fsim, image, target) > 0.95
    is_dup_rsme = similarity(rmse, image, target) < 0.05
    is_dup_psnr = similarity(psnr, image, target) < 0.05
    is_dup_uiq = similarity(uiq, image, target) < 0.05

    return is_dup_ssim or is_dup_fsim or is_dup_rsme or is_dup_psnr or is_dup_uiq
