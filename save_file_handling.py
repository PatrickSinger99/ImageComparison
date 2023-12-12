import json
import os
import jsbeautifier


class SaveFileHandler:
    valid_file_types = ("jpg", "jpeg", "png", "webp", "jfif")

    def __init__(self, root_path, save_file_path="savefile.json"):
        self.root_path = root_path
        self.save_file_path = save_file_path
        self.data_dict = {}  # stores json data as dict

        # Check if savefile exists. If yes load its data
        if os.path.exists(self.save_file_path):
            try:
                self.data_dict = self.read_from_save_file()
            except Exception as e:
                print("(!) Failed to load save file:", e)

        # Update savefile with current root directory content
        self.update_save_file()

    def read_from_save_file(self):
        with open(self.save_file_path, 'r') as json_file:
            data = json.load(json_file)

        print("Loaded data from savefile.")
        return data

    def write_to_save_file(self):
        with open(self.save_file_path, 'w') as json_file:
            options = jsbeautifier.default_options()
            options.indent_size = 4
            json_file.write(jsbeautifier.beautify(json.dumps(self.data_dict), options))

        print("Updated savefile.")

    def update_save_file(self):
        # Get current files of root folder
        all_file_paths = self.get_root_folder_files()

        # Add new files to dict
        for file_path in all_file_paths:
            if file_path not in self.data_dict:
                self.data_dict[file_path] = {}

        # Remove deleted files from dict
        to_be_deteted = []
        for file_path in self.data_dict:
            if file_path not in all_file_paths:
                to_be_deteted.append(file_path)

        for file_path in to_be_deteted:
            del self.data_dict[file_path]

        # Update savefile with new dict data
        self.write_to_save_file()

    def edit_image_features(self, file_path, new_features_dict):
        if file_path in self.data_dict:
            self.data_dict[file_path] = new_features_dict
        else:
            print(f"(!) Can not update features for {file_path}. File path not in save file.")

    def get_all_images_features(self):
        return self.data_dict

    def get_root_folder_files(self):
        valid_files = []

        for path, sub_folders, file_names in os.walk(self.root_path):

            for file_name in file_names:
                for file_type in SaveFileHandler.valid_file_types:
                    if file_name.lower().endswith(file_type):
                        refactored_path = os.path.join(path, file_name).replace("\\", "/")
                        valid_files.append(refactored_path)
                        break

        return valid_files


if __name__ == '__main__':
    s = SaveFileHandler(root_path="./data/test", save_file_path="./data.json")
    s.update_data()
    s.write_to_save_file()
