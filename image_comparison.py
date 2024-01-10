# Inspiration: https://stackoverflow.com/questions/843972/image-comparison-fast-algorithm
import os
import cv2
import time
import numpy as np
from PIL import Image
from typing import Union
import base64
import io


def load_img(path, load_size=250):
    pil_img = Image.open(path)
    pil_img.draft('RGB', (load_size, load_size))  # Using shrink-on-load to speed up image load times significantly
    img = np.array(pil_img, dtype=np.uint8)

    return img


def load_img_from_b64(b64_string, load_size=250):
    img_data = base64.b64decode(b64_string)
    img = Image.open(io.BytesIO(img_data))
    # img.thumbnail((load_size, load_size), Image.ANTIALIAS)  # Using thumbnail to resize while maintaining aspect ratio
    img = np.array(img, dtype=np.uint8)

    return img


def bytes_to_image(byte_data):
    print(byte_data)
    image_stream = io.BytesIO(byte_data)
    image = Image.open(image_stream)
    img = np.array(image, dtype=np.uint8)
    return img

def color_histogram(img_data, bins=8):
    """
    Calculate image features based on color distribution.
    :param img_data: 3d numpy array of image pixel values
    :param bins: number of bins (features) per color
    :return: 1d array of feature values. Length based on the bins (bins times 3 because of 3 colors)
    """
    # Verify image shape
    if len(img_data.shape) != 3:
        raise Exception(f"Image has wrong channel dimensions (Needs to be 3, image has {len(img_data.shape)}).")

    # Variable inits
    channels = ("red", "green", "blue")
    num_of_pixels = img_data.shape[0] * img_data.shape[1]
    return_data = []

    # Get histograms for RGB and normalize
    for i, channel in enumerate(channels):
        hist_data, _ = np.histogram(img_data[:, :, i], bins=bins)
        hist_data_norm = [round(val/num_of_pixels, 4) for val in hist_data]  # Normalize
        return_data += hist_data_norm

    return np.array(return_data)


def edge_histogram(img_data, bins=8):
    """
    Calculate image features based on the edge orientation distribution
    :param img_data:  3d numpy array of image pixel values
    :param bins: number of bins (features)
    :return: 1d array of feature values. Length equal to the bins
    """
    greyscale_img = cv2.cvtColor(img_data, cv2.COLOR_BGR2GRAY)

    # Calculate edges and compute orientations
    gx, gy = np.gradient(greyscale_img)  # compute the gradients along x and y axes
    eo = np.arctan2(gy, gx)  # compute the edge orientations in radians

    # Calculate histogram values and normalize
    hist_data, _ = np.histogram(eo, bins=bins, range=(-np.pi, np.pi))
    total_edges = np.sum(hist_data)
    hist_data_norm = np.array([round(val/total_edges, 4) for val in hist_data])

    return hist_data_norm


def get_img_features(img_data, bins=8, resize: Union[bool, int] = False):
    """
    Calculate the image features for one image
    :param img_data: 3d numpy array of image pixel values
    :param bins: number of features per feature type (eg. color green or edge orientation)
    :param resize: False or int. resize image data before computing features (saves a lot of feature compute time)
    :return: dictionary of features
    """
    return_data = {}

    # Resize Image if defined
    if resize:
        img_data = cv2.resize(img_data, (resize, resize))

    try:
        # Get color features
        hist_data = color_histogram(img_data, bins=bins)
        return_data["color"] = hist_data

        # Get edge normal orientation features
        edge_data = edge_histogram(img_data, bins=bins)
        return_data["edge_orientation"] = edge_data
    except Exception as e:
        # print("(!) Could not calculate features for image:", e)
        raise Exception("Could not calculate features for image:", e)

    return return_data


def compare_features(features_a, features_b):
    """
    Calculate absolute difference between 2 feature arrays
    :param features_a: image 1 features
    :param features_b: image 2 features
    :return: normalized float representing difference score. Lower is more similar
    """

    diff = np.absolute(np.array(features_a) - np.array(features_b))
    mae = round(np.mean(diff), 4)

    return mae


def compare_two_images(image_a_data, image_b_data):
    features_diffs = 0

    for feature in image_a_data:  # TODO Weights and filtering
        feature_diff = compare_features(image_a_data[feature], image_b_data[feature])
        features_diffs += feature_diff

    # Calc total avg difference for all features of 2 images
    try:
        total_diff = round(features_diffs / len(image_a_data), 4)
    except ZeroDivisionError:
        total_diff = 0

    similarity = 1 - total_diff  # Flip to more understandable similarity percentage

    return similarity
