import json
import os
import jsbeautifier
import time


class SaveFileHandler:
    valid_file_types = ("jpg", "jpeg", "png", "webp", "jfif")

    def __init__(self, root_path, save_file_path="savefile.json"):
        self.root_path = root_path
        self.save_file_path = save_file_path
        self.data_dict = {}  # stores the json data of the save file as dict

        # Check if savefile exists. If yes load its data
        try:
            self.data_dict = self.read_from_save_file()
        except Exception as e:
            print("(!) Failed to load save file:", e)

        # Update savefile with current root directory content
        self.update_save_file()

    def read_from_save_file(self):
        timer_start = time.time()
        print("(i) Reading save file...", end="")

        with open(self.save_file_path, 'r') as json_file:
            data = json.load(json_file)

        print(f"DONE ({round(time.time() - timer_start, 2)}s)")
        return data

    def write_to_save_file(self):
        timer_start = time.time()
        print("(i) Writing to save file...", end="")

        with open(self.save_file_path, 'w') as json_file:
            options = jsbeautifier.default_options()
            options.indent_size = 4
            json_file.write(jsbeautifier.beautify(json.dumps(self.data_dict), options))

        print(f"DONE ({round(time.time()-timer_start, 2)}s)")

    def update_save_file(self, write_to_file=True):
        timer_start = time.time()
        deletions_missing_file, deletions_modified_file, additions = [], [], []
        print("(i) Updating saved image paths...", end="")

        # Get current files of root folder
        all_file_paths = self.get_root_folder_files()
        # Remove deleted files from dict
        to_be_deleted = []
        for file_path in self.data_dict:
            # Delete savefile entry if file no longer exists
            if file_path not in all_file_paths:
                to_be_deleted.append(file_path)
                deletions_missing_file.append(file_path)
            # Delete savefile entry if file was modified
            elif self.data_dict[file_path]["info"]["last_modified"] != os.path.getmtime(file_path):
                to_be_deleted.append(file_path)
                deletions_modified_file.append(file_path)

        for file_path in to_be_deleted:
            del self.data_dict[file_path]

        # Add new files to dict
        for file_path in all_file_paths:
            if file_path not in self.data_dict:
                self.data_dict[file_path] = {"features": {},
                                             "info": {"compared": False, "last_modified": os.path.getmtime(file_path)}}
                additions.append(file_path)

        print(f"DONE (Removed: {len(deletions_missing_file + deletions_modified_file)} "
              f"({len(deletions_missing_file)} missing files, {len(deletions_modified_file)} modified files) | "
              f"Added: {len(additions)}) ({round(time.time()-timer_start, 2)}s)")

        # Update savefile with new dict data
        if (len(deletions_missing_file + deletions_modified_file) != 0 or len(additions) != 0) and write_to_file:
            self.write_to_save_file()

        return {"additions": additions, "deletions": deletions_missing_file + deletions_modified_file}

    def edit_image_features(self, file_path, new_features_dict):
        if file_path in self.data_dict:
            self.data_dict[file_path]["features"] = new_features_dict
        else:
            print(f"(!) Can not update features for {file_path}. File path not in save file.")

    def get_all_images_features(self, split_compared=True):
        if split_compared:
            # Return separate lists for previously compared and uncompared images
            uncompared_features_dict = {key: value['features'] for key, value in self.data_dict.items() if
                                        not value["info"]["compared"]}
            compared_features_dict = {key: value['features'] for key, value in self.data_dict.items() if
                                      value["info"]["compared"]}

            return compared_features_dict, uncompared_features_dict

        else:
            # Return one List of all features
            only_features_dict = {key: value['features'] for key, value in self.data_dict.items()}
            return only_features_dict

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

    def mark_all_as_compared(self, write_to_file=True, unmark_all=False):
        new_completions = 0

        for file_path in self.data_dict.keys():
            if self.data_dict[file_path]["info"]["compared"] == unmark_all:

                self.data_dict[file_path]["info"]["compared"] = True if not unmark_all else False
                new_completions += 1

        # Update savefile with new dict data
        if new_completions != 0 and write_to_file:
            self.write_to_save_file()

        return new_completions


if __name__ == '__main__':
    s = SaveFileHandler(root_path="./data/test", save_file_path="./data.json")
    s.update_data()
    s.write_to_save_file()
