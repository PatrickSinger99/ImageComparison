import os
import cv2
import time
from matplotlib import image
import numpy as np
from matplotlib import pyplot as plt


# Load an image from a directory path
def load_img(path):
    # PIL Alternative: img = np.asarray(Image.open(path), dtype=np.uint8)
    img = image.imread(path)
    return img


def color_histogram(img_data, bins=8):
    """
    Calculate image features based on color distribution.
    :param img_data: 3d numpy array of image pixel values
    :param bins: number of bins (features) per color
    :return: 1d array of feature values. length based on the bins
    """
    # Verify image shape
    if len(img_data.shape) != 3:
        raise Exception(f"Image has wrong channel dimensions. Needs to be 3. Image has {len(img_data.shape)}")

    # Variable inits
    channels = ("red", "green", "blue")
    num_of_pixels = img_data.shape[0] * img_data.shape[1]
    return_data = []

    # Get histograms for RGB and normalize
    for i, channel in enumerate(channels):
        hist_data, _ = np.histogram(img_data[:, :, i], bins=bins)
        hist_data_norm = [round(val/num_of_pixels, 4) for val in hist_data]  # Normalize
        return_data += hist_data_norm

    return return_data


def edge_histogram(img_data, bins=8):
    """
    img_gray = np.dot(img_data[:, :, :3], [0.299, 0.587, 0.114]) / 255  # Convert to greyscale

    plt.imshow(img_gray, cmap="gray")
    plt.show()
    """

    img_canny = cv2.Canny(img_data, 100, 200)
    """
    plt.imshow(img_canny, cmap="gray")
    plt.show()
    """


def get_img_features(img_data, bins=8, resize=False):
    """
    Calculate the image features for one image
    :param img_data: 3d numpy array of image pixel values
    :param bins: number of features per feature type (eg. color green or edge orientation)
    :param resize: resize image data to a set scale (recommended as it saves a lot of feature compute time)
    :return: 1d array of feature values
    """
    return_data = []  # ORDER: red, green, blue

    # Resize Image if defined
    if resize:
        img_data = cv2.resize(img_data, (resize, resize))

    # Get color features
    try:
        hist_data = color_histogram(img_data, bins=bins)
        return_data += hist_data
    except Exception as e:
        print(f"Could not get color features for image. Error:\n{e}")

    # Get feature xx
    # TODO

    return return_data


def compare_features(features_a, features_b):
    """
    Calculate absolute difference between 2 images based on image features
    :param features_a: image 1 features
    :param features_b: image 2 features
    :return: normalized float representing difference score. Lower is more similar
    """
    diff = np.absolute(features_a - features_b)
    norm_diff = np.sum(diff)/len(features_a)
    return round(norm_diff, 4)


def compare_image_data(img_data_list):
    """
    Compares all images. Images must be given as their features. Returns the index to identify the images
    :param img_data_list: array of features of images
    :return: array with results as (img_1_index, img_2_index, difference_score)
    """

    results, total_comparisons = [], 0
    start_time = time.time()

    for index_a in range(len(img_data_list)):
        for index_b in range(index_a + 1, len(img_data_list)):
            diff = compare_features(img_data_list[index_a], img_data_list[index_b])
            results.append((index_a, index_b, diff))
            total_comparisons += 1

    final_time = time.time()-start_time
    print(f"(i) Compared {len(img_data_list)} images in {total_comparisons} comparisons. "
          f"[{round(final_time, 4)}s total | {round((final_time / total_comparisons)*1000, 4)}s per 1k comparisons]")

    return results


def load_images_from_directory(path, bin_accuracy=6, scaling=False):
    valid_formats = ("jpg", "jpeg", "png", "webp")
    load_time, feature_extract_time = 0, 0  # Timing vars

    # Get valid image paths
    verify_start = time.time()
    path_contents = [os.path.join(root, file) for file in os.listdir(path)]
    valid_images = [file for file in path_contents if file.split(".")[-1].lower() in valid_formats]
    verify_time = time.time() - verify_start

    # Load image data as np array
    return_data = {}
    for img in valid_images:
        # Load image pixel data
        load_start = time.time()
        img_data = load_img(img)
        load_time += time.time() - load_start

        # Compute features
        feature_start = time.time()
        img_features = get_img_features(img_data, bins=bin_accuracy, resize=scaling)
        feature_extract_time += time.time() - feature_start

        # Add to return data
        return_data[img] = img_features

    print(f"(i) Loaded {len(valid_images)} images from {path}. [Verify: {round(verify_time, 2)}s | "
          f"Load: {round(load_time, 2)}s | Extract: {round(feature_extract_time, 2)}s]")

    return return_data


def find_matches(comparison_data, img_paths_by_index, threshold=0.02, sort_by_score=True):
    all_matches = []
    start_time = time.time()

    for comparison in comparison_data:
        if comparison[2] <= threshold:
            all_matches.append((img_paths_by_index[comparison[0]], img_paths_by_index[comparison[1]], comparison[2]))

    if sort_by_score:
        all_matches = sorted(all_matches, key=lambda entry: entry[2])

    print(f"(i) Found {len(all_matches)} {'match' if len(all_matches) == 2 else 'matches'}. "
          f"[{round(time.time()-start_time, 4)}s]")

    return all_matches


if __name__ == "__main__":
    root = r"E:\GitHub Repositories\ImageComparison\imgs"

    imgs_features = load_images_from_directory(root, scaling=250)

    np_array = np.array(list(imgs_features.values()))
    images_paths = list(imgs_features.keys())
    comparison_data = compare_image_data(np_array)
    matches = find_matches(comparison_data, images_paths)

    for match in matches:
        f, axarr = plt.subplots(1, 2)
        axarr[0].imshow(load_img_pil(match[0]))
        axarr[1].imshow(load_img_pil(match[1]))
        f.suptitle(match[2])
        plt.show()


    """
    plt.imshow(test)
    plt.show()

    hists = histogram(test, bins=8)
    for hist in hists:
        print(hists[hist])
        plt.bar([str(i) for i in range(len(hists[hist]))], hists[hist])
        plt.title(hist)
        plt.show()
    """
