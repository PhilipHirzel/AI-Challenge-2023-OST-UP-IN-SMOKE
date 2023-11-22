import json
import os


class Config:
    def __init__(self, default_output_path="./config.json"):
        self.default_output_path = default_output_path

        self.source_image_path = "./sampleData"
        self.output_folder_path = "./labeledData"
        self.stop_output_folder_path = "/stopSigns"
        self.no_stop_output_folder_path = "/noStopSigns"
        self.skip_output_folder_path = "/skip"

        self.image_output_width = 160
        self.image_output_height = 120
        self.history_size = 100

        self.fast_auto_labeling = False

        if os.path.exists(self.default_output_path):
            self.load_config()
            print("Config loaded from File")
        else:
            self.write_config()

    def update_source_image_path(self, new_path):
        if len(new_path) > 0:
            self.source_image_path = new_path
            self.write_config()

    def load_config(self):
        with open(self.default_output_path, "r", encoding="utf-8") as file_in:
            raw_config = json.load(file_in)

            self.source_image_path = raw_config["source_image_path"]
            self.output_folder_path = raw_config["output_folder_path"]
            self.stop_output_folder_path = raw_config["stop_output_folder_path"]
            self.no_stop_output_folder_path = raw_config["no_stop_output_folder_path"]
            self.history_size = raw_config["history_size"]
            self.skip_output_folder_path = raw_config["skip_output_folder_path"]
            self.image_output_width = raw_config["image_output_width"]
            self.image_output_height = raw_config["image_output_height"]
            self.fast_auto_labeling = raw_config["fast_auto_labeling"]

    def write_config(self):
        with open(self.default_output_path, "w", encoding="utf-8") as file_out:
            json.dump({"source_image_path": self.source_image_path,
                       "output_folder_path": self.output_folder_path,
                       "stop_output_folder_path": self.stop_output_folder_path,
                       "no_stop_output_folder_path": self.no_stop_output_folder_path,
                       "history_size": self.history_size,
                       "skip_output_folder_path": self.skip_output_folder_path,
                       "image_output_width": self.image_output_width,
                       "image_output_height": self.image_output_height,
                       "fast_auto_labeling":self.fast_auto_labeling
                       }, file_out)
