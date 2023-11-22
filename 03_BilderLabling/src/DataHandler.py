import glob
import os
import shutil

from PIL import Image

from History import History
from ImageQueue import ImageQueue


class DataHandler:
    def __init__(self, config):
        self.config = config
        self.classified_images = set([])

        self.history = History(self.config.history_size)
        self.image_queue = ImageQueue()

        self.setup_folders()
        self.index_classified_images()
        self.create_image_path_list()

    def setup_folders(self):
        if not os.path.exists(self.config.output_folder_path):
            os.makedirs(self.config.output_folder_path)
            os.makedirs(self.config.output_folder_path + self.config.stop_output_folder_path)
            os.makedirs(self.config.output_folder_path + self.config.no_stop_output_folder_path)
            os.makedirs(self.config.output_folder_path + self.config.skip_output_folder_path)
            return True
        else:
            return False

    def shuffle(self):
        self.image_queue.shuffle()

    def reindex(self):
        self.index_classified_images()
        self.create_image_path_list()

    def index_classified_images(self):
        self.classified_images.update([path.replace("\\", "/").split("/")[-1] for path in glob.glob(
            f"{self.config.output_folder_path + self.config.stop_output_folder_path}/*.png")])
        self.classified_images.update([path.replace("\\", "/").split("/")[-1] for path in glob.glob(
            f"{self.config.output_folder_path + self.config.no_stop_output_folder_path}/*.png")])
        self.classified_images.update([path.replace("\\", "/").split("/")[-1] for path in glob.glob(
            f"{self.config.output_folder_path + self.config.skip_output_folder_path}/*.png")])

    def create_image_path_list(self, silent=False):
        images = (os.path.join(root, filename)
                  for root, _, filenames in os.walk(self.config.source_image_path)
                  for filename in filenames
                  if filename.endswith('.png'))

        images = list(images)

        self.total_images_found = len(images)
        self.image_queue.queue = [path for path in images if
                                  path.replace("\\", "/").split("/")[-1] not in self.classified_images]

        if not silent:
            self.images_to_classifiy = len(self.image_queue)

            if self.total_images_found > 0:
                self.progress = 1 - (self.images_to_classifiy / self.total_images_found)
                print(
                    f"{100 * (self.progress):.2f}% Done (Labeled:{self.total_images_found - self.images_to_classifiy}/ Total:{self.total_images_found})")
            else:
                print(f"100.00% Done (Labeled:0/ Total:0)  -> No Images Found please check the source folder!")
                self.progress = 0

            print(self.image_queue)

    def get_next_image_path(self):
        try:
            return self.image_queue.get_next()
        except RuntimeError as e:
            print(e)
            raise e

    def view_next_image(self):
        try:
            return self.image_queue.peak()
        except RuntimeError as e:
            print(e)
            raise e

    def add_previous_image(self):
        try:
            previous_image = self.history.back_step()
            self.image_queue.add_to_top(previous_image["source"])
            os.remove(previous_image["destination"] + "/" + previous_image["source"].replace("\\", "/").split("/")[-1])
        except RuntimeWarning:
            print("History is empty")

    def get_number_of_images_to_classifiy(self):
        return len(self.image_queue)

    def skip_image(self):
        destination = self.config.output_folder_path + self.config.skip_output_folder_path
        source = self.get_next_image_path()
        self.history.add({"source": source, "destination": destination})
        shutil.copy(source, destination)

    def write_image(self, contains_a_stop_sign):

        if contains_a_stop_sign:
            destination = self.config.output_folder_path + self.config.stop_output_folder_path
        else:
            destination = self.config.output_folder_path + self.config.no_stop_output_folder_path

        source = self.get_next_image_path()
        self.history.add({"source": source, "destination": destination})

        img = Image.open(source)
        img = img.resize((self.config.image_output_width, self.config.image_output_height))
        output_file_name = destination + "/" + source.replace("\\", "/").split("/")[-1]
        img.save(output_file_name)

        # shutil.copy(source, destination)
