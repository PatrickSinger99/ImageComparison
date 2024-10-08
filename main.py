import os
from save_file_handling import SaveFileHandler
from image_comparison import *
import time
from matplotlib import pyplot as plt


class ImageCompare:
    def __init__(self, savefile_path="savefile.json", bins=6, resize=250):
        self.save_file_handler = SaveFileHandler(save_file_path=savefile_path)

        """PARAMETERS"""

        # Feature computation parameters
        self.bins = bins
        self.resize = resize

        """INITIAL CALLS"""

        # Update image features
        self.update_features()

    def update_features(self, write_to_file=True):
        """
        Add features to all save file entries that do not have features yet
        :param write_to_file: Update savefile if changes occur (can be time intensive)
        """
        updates = 0
        skipped = 0  # Skipped images due to errors

        all_images_features = self.save_file_handler.get_all_images_features(split_compared=False)

        # Iterate through every save file entry
        for file_path, features in all_images_features.items():
            if features == {}:
                # If the image does not have features, calculate them
                try:
                    new_features = get_img_features(load_img(file_path), bins=self.bins, resize=self.resize)

                    for feature in new_features:
                        new_features[feature] = new_features[feature].tolist()

                    self.save_file_handler.edit_image_features(file_path, new_features)
                    updates += 1

                except Exception as e:
                    skipped += 1

        if skipped != 0:
            print(f"(!) Skipped computing features for {skipped} image{'s' if skipped != 1 else ''} "
                  f"(Invalid number of channels).")
        # Only update the save file, if changes were made (Updating large save files takes several seconds)
        if updates != 0 and write_to_file:
            self.save_file_handler.write_to_save_file()

    def compare_new_image(self, new_image_path, threshold=0.99):
        """
        Compare a new image to the existing images in the save file
        :param new_image_path: Path of the new image to be compared
        :param threshold: threshold for minimum similarity score for the comparison to be saved
        :return: Array of tuples with the results of the comparison: [(other_image_path, similarity), ...]
        """

        timer_start = time.time()
        num_comparisons = 0

        # Load new image and compute features
        new_img_data = load_img(new_image_path)
        new_img_features = get_img_features(new_img_data, bins=self.bins, resize=self.resize)

        # Get all features from existing images in the save file
        all_imgs_features = self.save_file_handler.get_all_images_features(split_compared=False)

        # Compare the new image to every other image and save the results in an array
        results = []
        for img_path, img_features in all_imgs_features.items():
            if new_image_path != img_path:
                similarity = compare_two_images(img_features, new_img_features)
                num_comparisons += 1

                # Only save comparison result if above the defined threshold
                if similarity >= threshold:
                    results.append((img_path, similarity))

        # Sort results
        results = sorted(results, key=lambda x: x[1], reverse=True)
        self.save_file_handler.add_to_lifetime_stats(matches=len(results), comparisons=num_comparisons)
        final_time = time.time()-timer_start
        print(f"(i) Comparison with {os.path.basename(new_image_path)} finished. "
              f"Found {len(results)} match{'es' if len(results) != 1 else ''} above threshold {threshold} "
              f"({round(final_time, 2)}s total | "
              f"{round((final_time / len(all_imgs_features))*10000, 2)}s per 10k comparisons)")

        return results

    def compare_all_images(self, threshold=0.99, skip_compared=True):
        """
        Compare all images in the save file with each other
        :param threshold: threshold for minimum similarity score for the comparison to be saved
        :param skip_compared: skip images that have already been compared with every other image
        :return: Array of tuples with the results of the comparison: [(image_a_path, image_b_path, similarity), ...]
        """

        timer_start = time.time()
        num_comparisons = 0
        results = []

        # Get all features from existing images in the save file
        if skip_compared:
            # If previous compared images are skipped, get 2 lists for already compared and uncompared images
            compared_imgs_features, uncompared_imgs_features = self.save_file_handler.get_all_images_features()
        else:
            uncompared_imgs_features = self.save_file_handler.get_all_images_features(split_compared=False)
            compared_imgs_features = []  # Define so the IDE doesnt act up + for printing results

        # Compare all uncompared images with each other and save the results in an array
        for img_a_index, (img_a_path, img_a_features) in enumerate(uncompared_imgs_features.items()):
            for img_b_path, img_b_features in list(uncompared_imgs_features.items())[img_a_index + 1:]:

                try:
                    similarity = compare_two_images(img_a_features, img_b_features)

                    # Only save comparison result if above the defined threshold
                    if similarity >= threshold:
                        results.append((img_a_path, img_b_path, similarity))

                except Exception as e:
                    pass

                num_comparisons += 1

        # Compare all uncompared images to all compared images. Only when compared images are skipped
        if skip_compared:
            for img_a_path, img_a_features in uncompared_imgs_features.items():
                for img_b_path, img_b_features in compared_imgs_features.items():

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
        num_of_imgs = len(compared_imgs_features) + len(uncompared_imgs_features)

        if num_comparisons != 0:
            self.save_file_handler.add_to_lifetime_stats(matches=len(results), comparisons=num_comparisons)

            print(f"(i) Comparison of {num_of_imgs} image{'s' if num_of_imgs != 1 else ''} finished. "
                  f"{num_comparisons} total comparison{'s' if num_comparisons != 1 else ''}. "
                  f"Found {len(results)} match{'es' if len(results) != 1 else ''} above threshold {threshold} "
                  f"({round(final_time, 2)}s total | "
                  f"{round((final_time / num_comparisons)*10000, 2)}s per 10k comparisons)")
        else:
            print(f"(i) Comparison finished. No images could be compared (Reason could be that all images have been "
                  f"compared with each other already).")

        _ = self.save_file_handler.mark_all_as_compared()

        return results


if __name__ == '__main__':
    img_comp = ImageCompare()
    img = r"./imgs/test (49).jpg"

    # TEST COMPARE TO NEW IMAGE
    res = img_comp.compare_new_image(img, threshold=.97)

    # TEST COMPARE ALL IMAGES
    img_comp.save_file_handler.mark_all_as_compared(unmark_all=True)
    res_all = img_comp.compare_all_images(threshold=.99)

    """
    for match in res_all:
        f, axarr = plt.subplots(1, 2)
        axarr[0].imshow(load_img(match[0]))
        axarr[1].imshow(load_img(match[1]))
        f.suptitle(match[2])
        plt.show()
    """