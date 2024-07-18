import numpy as np
import time


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

def compare_all_images(all_imgs_features, threshold=0.99):
    """
    Compare all images in the save file with each other
    :param threshold: threshold for minimum similarity score for the comparison to be saved
    :return: Array of tuples with the results of the comparison: [(image_a_path, image_b_path, similarity), ...]
    """

    if len(all_imgs_features) > 1:
        timer_start = time.time()
        num_comparisons = 0

        # Compare all images with each other and save the results in an array
        results = []
        for img_a_index, (img_a_path, img_a_features) in enumerate(all_imgs_features.items()):
            for img_b_path, img_b_features in list(all_imgs_features.items())[img_a_index + 1:]:

                try:
                    similarity = compare_two_images(img_a_features, img_b_features)

                    # Only save comparison result if above the defined threshold
                    if similarity >= threshold:
                        results.append((img_a_path, img_b_path, similarity))

                except Exception as e:
                    pass

                num_comparisons += 1

        # Sort results
        results = sorted(results, key=lambda x: x[1], reverse=True)

        final_time = time.time() - timer_start
        num_of_imgs = len(all_imgs_features)
        print(f"Comparison of {num_of_imgs} image{'s' if num_of_imgs != 1 else ''} finished. "
              f"{num_comparisons} total comparison{'s' if num_comparisons != 1 else ''}. "
              f"Found {len(results)} match{'es' if len(results) != 1 else ''} above threshold {threshold} "
              f"({round(final_time, 2)}s total | "
              f"{round((final_time / num_comparisons)*10000, 2)}s per 10k comparisons)")

        return results

    else:
        print("Not enough images to compare!")
        return []
