from save_file_handling import SaveFileHandler
from image_comparison import *


class ImageCompare:
    def __init__(self, root_path, savefile_path="savefile.json", bins=6, resize=250):
        self.save_file_handler = SaveFileHandler(root_path, save_file_path=savefile_path)

        self.bins = bins
        self.resize = resize

        # Update image features
        self.update_features()

    def update_features(self):
        # Add features to all images that dont have them
        all_images_features = self.save_file_handler.get_all_images_features()

        for file_path, features in all_images_features.items():
            if features == {}:
                new_features = get_img_features(load_img(file_path), bins=self.bins, resize=self.resize)

                for feature in new_features:
                    new_features[feature] = new_features[feature].tolist()

                self.save_file_handler.edit_image_features(file_path, new_features)

        self.save_file_handler.write_to_save_file()

    def compare_new_image(self, new_image_path):
        new_img_data = load_img(new_image_path)
        new_img_features = get_img_features(new_img_data, bins=self.bins, resize=self.resize)

        all_imgs_features = self.save_file_handler.get_all_images_features()

        results = []
        for img_path, img_features in all_imgs_features.items():
            similarity = compare_two_images(img_features, new_img_features)
            results.append((img_path, similarity))

        return results


if __name__ == '__main__':
    img_comp = ImageCompare(root_path="./data/raw-img")
    img = r"C:\Users\sip4abt\Documents\GitHub\ImageComparison\data\raw-img\cat\1.jpeg"
    res = img_comp.compare_new_image(img)
    print(res)