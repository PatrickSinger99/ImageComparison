import json
import os
import jsbeautifier
import time


class SaveFileHandler:
    valid_file_types = ("jpg", "jpeg", "png", "webp", "jfif")
    base_save_file_structure = {"meta": {"root": "", "created": 0, "lifetime_matches": 0, "lifetime_comparisons": 0},
                                "data": {}}

    def __init__(self, save_file_path="savefile.json"):
        self.save_file_path = save_file_path
        self.data_dict = {}  # stores the json data of the save file as dict

        # Check if savefile exists. If yes load its data
        try:
            self.data_dict = self.read_from_save_file()
            self.root_path = self.data_dict["meta"]["root"]
        except Exception as e:
            print("FAILED. Can not load save file:", e)
            self.create_save_file()

        # Update savefile with current root directory content
        self.update_save_file()

    def read_from_save_file(self):
        timer_start = time.time()
        print("(i) Reading save file...", end="")

        with open(self.save_file_path, 'r') as json_file:
            data = json.load(json_file)

        print(f"DONE ({round(time.time() - timer_start, 2)}s)")
        return data

    def create_save_file(self):
        print("(i) Creating new savefile.")

        # Create new data structure
        self.data_dict = SaveFileHandler.base_save_file_structure
        self.data_dict["meta"]["root"] = os.path.dirname(os.path.abspath(__file__))
        self.data_dict["meta"]["created"] = int(time.time())

        self.write_to_save_file()

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
        for file_path in self.data_dict["data"]:
            # Delete savefile entry if file no longer exists
            if file_path not in all_file_paths:
                to_be_deleted.append(file_path)
                deletions_missing_file.append(file_path)
            # Delete savefile entry if file was modified
            elif self.data_dict["data"][file_path]["info"]["last_modified"] != os.path.getmtime(file_path):
                to_be_deleted.append(file_path)
                deletions_modified_file.append(file_path)

        for file_path in to_be_deleted:
            del self.data_dict["data"][file_path]

        # Add new files to dict
        for file_path in all_file_paths:
            if file_path not in self.data_dict["data"]:
                self.data_dict["data"][file_path] = {"features": {},
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
        if file_path in self.data_dict["data"]:
            self.data_dict["data"][file_path]["features"] = new_features_dict
        else:
            print(f"(!) Can not update features for {file_path}. File path not in save file.")

    def get_all_images_features(self, split_compared=True):
        if split_compared:
            # Return separate lists for previously compared and uncompared images
            uncompared_features_dict = {key: value['features'] for key, value in self.data_dict["data"].items() if
                                        not value["info"]["compared"]}
            compared_features_dict = {key: value['features'] for key, value in self.data_dict["data"].items() if
                                      value["info"]["compared"]}

            return compared_features_dict, uncompared_features_dict

        else:
            # Return one List of all features
            only_features_dict = {key: value['features'] for key, value in self.data_dict["data"].items()}
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

        for file_path in self.data_dict["data"].keys():
            if self.data_dict["data"][file_path]["info"]["compared"] == unmark_all:

                self.data_dict["data"][file_path]["info"]["compared"] = True if not unmark_all else False
                new_completions += 1

        # Update savefile with new dict data
        if new_completions != 0 and write_to_file:
            self.write_to_save_file()

        return new_completions

    def get_number_of_files(self):
        return len(self.data_dict["data"])

    def get_lifetime_stats(self):
        return {"matches": self.data_dict["meta"]["lifetime_matches"],
                "comparisons": self.data_dict["meta"]["lifetime_comparisons"]}

    def add_to_lifetime_stats(self, matches=0, comparisons=0, write_to_file=True):

        self.data_dict["meta"]["lifetime_matches"] += matches
        self.data_dict["meta"]["lifetime_comparisons"] += comparisons

        # Update savefile with new dict data
        if write_to_file:
            self.write_to_save_file()
