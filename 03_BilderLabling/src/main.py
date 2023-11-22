import sys
import time

from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QHBoxLayout, \
    QLineEdit, QProgressBar
from PySide6.QtGui import QPixmap, QShortcut, QKeySequence
from PySide6.QtCore import Qt
from PySide6.QtCore import QThread, Signal

from Config import Config
from DataHandler import DataHandler

def runner_all_images(data_handler,contains_a_stop_sign):
         
         for idx in range(data_handler.total_images_found-len(data_handler.image_queue),data_handler.total_images_found):
            if QThread.currentThread().isInterruptionRequested():
                break
            data_handler.write_image(contains_a_stop_sign=contains_a_stop_sign)
            yield idx+1

class WorkerThread(QThread):
    update_signal = Signal(int)
    stop_signal = Signal()

    def __init__(self, data_handler, contains_a_stop_sign):
        super().__init__()
        self.data_handler = data_handler
        self.contains_a_stop_sign = contains_a_stop_sign
        self._stop_requested = False

    def run(self):
        self._stop_requested = False
        for progress in runner_all_images(self.data_handler,self.contains_a_stop_sign):
            if self._stop_requested:
                break
            self.update_signal.emit(progress)

    def stop(self):
        self._stop_requested = True


class ImageViewer(QWidget):

    def __init__(self):
        super().__init__()
        self.config = Config()
        self.data_handler = DataHandler(self.config)

        self.background_task_is_running = False

        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.source_folder_view = QHBoxLayout()

        # --Source Folder Select

        self.button_set_source_folder = QPushButton('Select Source Folder', self)
        self.source_folder_view.addWidget(self.button_set_source_folder)
        self.button_set_source_folder.clicked.connect(self.on_click_set_source_folder)

        self.test_field_source_folder = QLineEdit(self)
        self.source_folder_view.addWidget(self.test_field_source_folder)
        self.test_field_source_folder.setReadOnly(True)
        self.test_field_source_folder.setText(self.config.source_image_path)

        layout.addLayout(self.source_folder_view)

        # --Utility Buttons

        self.utiltiy_view = QHBoxLayout()

        self.button_shuffle = QPushButton('Shuffle', self)
        self.utiltiy_view.addWidget(self.button_shuffle)
        self.button_shuffle.clicked.connect(self.on_click_shuffle)

        self.button_all_images_with_stops_signs = QPushButton('All Images contain Stop Signs', self)
        self.utiltiy_view.addWidget(self.button_all_images_with_stops_signs)
        self.button_all_images_with_stops_signs.clicked.connect(self.on_click_all_images_with_stops_signs)

        self.button_all_images_with_no_stops_signs = QPushButton('All Images contain NO Stop Signs', self)
        self.utiltiy_view.addWidget(self.button_all_images_with_no_stops_signs)
        self.button_all_images_with_no_stops_signs.clicked.connect(self.on_click_all_images_with_no_stops_signs)

        self.button_back = QPushButton('Previous Image (B)', self)
        self.utiltiy_view.addWidget(self.button_back)
        self.button_back.clicked.connect(self.on_click_show_previous_image)



        layout.addLayout(self.utiltiy_view)

        # --ProgressBar

        self.progrssBar_view = QHBoxLayout()

        self.progrss_label = QLabel("-/-", self)
        self.progrss_label.setFixedHeight(30)
        self.progressBar = QProgressBar(self)

        self.progrssBar_view.addWidget(self.progressBar)
        self.progrssBar_view.addWidget(self.progrss_label)

        layout.addLayout(self.progrssBar_view)

        self.progressBar.setMaximum(100)
        self.progressBar.setMinimum(0)
        self.update_progressbar()

        # --Image View

        self.imageLabel = QLabel(self)
        layout.addWidget(self.imageLabel)

        self.draw_image()

        # --Classification Buttons

        self.button_stop_in_image = QPushButton('Stop (A)', self)
        layout.addWidget(self.button_stop_in_image)
        self.button_stop_in_image.clicked.connect(self.on_click_stop_in_image)

        self.button_no_stop_in_image = QPushButton('No Stop (L)', self)
        layout.addWidget(self.button_no_stop_in_image)
        self.button_no_stop_in_image.clicked.connect(self.on_click_stop_not_in_image)

        self.button_skip_image = QPushButton('Skip (S)', self)
        layout.addWidget(self.button_skip_image)
        self.button_skip_image.clicked.connect(self.on_click_skip_image)

        # --Key Bindings

        load_shortcut = QShortcut(QKeySequence(Qt.Key.Key_A), self)
        load_shortcut.activated.connect(self.on_click_stop_in_image)

        load_shortcut = QShortcut(QKeySequence(Qt.Key.Key_L), self)
        load_shortcut.activated.connect(self.on_click_stop_not_in_image)

        load_shortcut = QShortcut(QKeySequence(Qt.Key.Key_S), self)
        load_shortcut.activated.connect(self.on_click_skip_image)

        load_shortcut = QShortcut(QKeySequence(Qt.Key.Key_B), self)
        load_shortcut.activated.connect(self.on_click_show_previous_image)


        # -- Worker Thread for folder classification
        self.worker_thread_no_stop_signs = WorkerThread(self.data_handler,False)
        self.worker_thread_no_stop_signs.update_signal.connect(self.update_progress)

        self.worker_thread_stop_signs = WorkerThread(self.data_handler,True)
        self.worker_thread_stop_signs.update_signal.connect(self.update_progress)

        self.setLayout(layout)

    def draw_image(self):
        try:
            if len(self.data_handler.image_queue) > 0:  # Normal case images found and there are more images to label
                pixmap = QPixmap(self.data_handler.view_next_image())
                self.imageLabel.setPixmap(pixmap)
                self.imageLabel.setScaledContents(True)

            elif self.data_handler.total_images_found > 0:  # All images are labeled
                self.imageLabel.clear()
                self.imageLabel.setText("Done")
                self.imageLabel.setAlignment(Qt.AlignCenter)
                self.imageLabel.setScaledContents(True)
                print("All images are labeled")

            else:  # No images found in the folder
                self.imageLabel.clear()
                self.imageLabel.setText(f"No Images were found in the Source Folder! \n{self.config.source_image_path}")
                self.imageLabel.setAlignment(Qt.AlignCenter)
                self.imageLabel.setScaledContents(True)

        except RuntimeError as e:
            print(f"--Runtime Error: {e}")

    def update_progressbar(self):
        if self.data_handler.total_images_found > 0:
            self.progressBar.setValue(
                100 - int(100 * len(self.data_handler.image_queue) / self.data_handler.total_images_found))
            self.progrss_label.setText(f"{self.data_handler.total_images_found-len(self.data_handler.image_queue)}/{self.data_handler.total_images_found}")

    def on_click_shuffle(self):
        self.data_handler.reindex()
        self.data_handler.shuffle()
        self.draw_image()
        self.update_progressbar()

    def on_click_stop_in_image(self):
        try:
            self.data_handler.write_image(contains_a_stop_sign=True)
            self.draw_image()
            self.update_progressbar()
        except RuntimeError as e:
            print(e)


    def on_click_stop_not_in_image(self):
        try:
            self.data_handler.write_image(contains_a_stop_sign=False)
            self.draw_image()
            self.update_progressbar()
        except RuntimeError as e:
            print(e)

    def on_click_all_images_with_stops_signs(self):
        if self.background_task_is_running:
            self.worker_thread_stop_signs.stop()
            self.background_task_is_running = False
            self.helper_enable_ui_buttons(enable=True,exclude="Stop")
            self.button_all_images_with_stops_signs.setText("All Images contain Stop Signs")
            self.draw_image()
        else:
            self.worker_thread_stop_signs.start()
            self.background_task_is_running = True
            self.helper_enable_ui_buttons(enable=False,exclude="Stop")
            self.button_all_images_with_stops_signs.setText("Cancel")

    def on_click_all_images_with_no_stops_signs(self):
        if self.background_task_is_running:
            self.worker_thread_no_stop_signs.stop()
            self.background_task_is_running = False
            self.helper_enable_ui_buttons(enable=True,exclude="No Stop")
            self.button_all_images_with_no_stops_signs.setText("All Images contain NO Stop Signs")
            self.draw_image()
        else:
            self.worker_thread_no_stop_signs.start()
            self.background_task_is_running = True
            self.helper_enable_ui_buttons(enable=False,exclude="No Stop")
            self.button_all_images_with_no_stops_signs.setText("Cancel")
        

    def update_progress(self,progress):
        self.progressBar.setValue(
                int(100 * progress / self.data_handler.total_images_found))
        self.progrss_label.setText(f"{progress}/{self.data_handler.total_images_found}")
        if not self.config.fast_auto_labeling:
            self.draw_image()
        if progress == self.data_handler.total_images_found:
            self.background_task_is_running = False
            self.draw_image()
            self.helper_enable_ui_buttons(enable=True)
            self.button_all_images_with_no_stops_signs.setText("All Images contain NO Stop Signs")
            self.button_all_images_with_stops_signs.setText("All Images contain Stop Signs")

    def on_click_skip_image(self):
        try:
            self.data_handler.skip_image()
            self.draw_image()
            self.update_progressbar()
        except RuntimeError as e:
            print(e)

    def on_click_set_source_folder(self):
        self.config.update_source_image_path(QFileDialog.getExistingDirectory(self, 'Select Folder'))
        self.test_field_source_folder.setText(self.config.source_image_path)
        self.data_handler.reindex()
        self.draw_image()
        self.update_progressbar()

    def on_click_show_previous_image(self):
        self.data_handler.add_previous_image()
        self.draw_image()
        self.update_progressbar()


    def helper_enable_ui_buttons(self,enable=True,exclude=None):
        self.button_set_source_folder.setEnabled(enable)
        self.button_shuffle.setEnabled(enable)
        self.button_back.setEnabled(enable)
        self.button_stop_in_image.setEnabled(enable)
        self.button_no_stop_in_image.setEnabled(enable)
        self.button_skip_image.setEnabled(enable)

        if exclude == "Stop":
            self.button_all_images_with_no_stops_signs.setEnabled(enable)

        elif exclude == "No Stop":
            self.button_all_images_with_stops_signs.setEnabled(enable)
        else:
            self.button_all_images_with_no_stops_signs.setEnabled(enable)
            self.button_all_images_with_stops_signs.setEnabled(enable)


def main():
    app = QApplication(sys.argv)
    viewer = ImageViewer()
    viewer.setWindowTitle('AI Challenge @ OST Data Labeling')
    viewer.resize(800, 600)
    viewer.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
