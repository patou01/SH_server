import logging
import os
from pathlib import Path

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QHBoxLayout, QComboBox, QPushButton, \
    QFileDialog
import pyqtgraph as pg
import sys

from pyqtgraph import DateAxisItem

from interface.data_fetcher import CsvFetcher

logging.basicConfig(level=logging.INFO)


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.fetcher = CsvFetcher(Path("../server/data"))

        self.current_folder = "bedroom"

        axis = DateAxisItem()
        layout = QVBoxLayout()

        horiz1 = QHBoxLayout()

        self.graphWidget = pg.PlotWidget(axisItems={'bottom': axis})

        axis2 = DateAxisItem()
        self.graphWidget2 = pg.PlotWidget(axisItems={'bottom': axis2})

        types = self.fetcher.get_available_data_types(self.current_folder)

        folder_button = QPushButton("Select folder")
        folder_button.clicked.connect(self.find_folder)
        widget = QWidget()
        widget.setLayout(layout)
        self.box1 = QComboBox()
        self.box1.addItems(types)
        self.box1.currentTextChanged.connect(self.combo1_callback)

        horiz1.addWidget(self.box1)
        horiz1.addWidget(self.graphWidget)

        horiz2 = QHBoxLayout()
        self.box2 = QComboBox()
        self.box2.addItems(types)
        if len(types) > 1:
            self.box2.setCurrentIndex(1)
        self.box2.currentTextChanged.connect(self.combo2_callback)
        horiz2.addWidget(self.box2)
        horiz2.addWidget(self.graphWidget2)

        layout.addWidget(folder_button)
        layout.addLayout(horiz1)
        layout.addLayout(horiz2)

        self.setCentralWidget(widget)
        self.replot()

    def find_folder(self):
        logging.info("Searching!")
        dialog = QFileDialog(directory=os.path.dirname(__file__))
        folder_path = dialog.getExistingDirectory()
        self.current_folder = Path(folder_path).parts[-1]
        logging.info(f"Updated current folder to {self.current_folder}")
        self.update_combo_texts()
        self.replot()

    def update_combo_texts(self):
        """
        When the folder is changed, we need to update the data that can be plotted
        """
        types = self.fetcher.get_available_data_types(self.current_folder)
        logging.info(f"Updated combo texts to {types}")
        self.box1.blockSignals(True)
        self.box1.clear()
        self.box1.addItems(types)
        self.box1.blockSignals(True)
        self.box1.setCurrentIndex(0)

        self.box2.blockSignals(True)
        self.box2.clear()
        self.box2.addItems(types)
        self.box2.blockSignals(False)
        if len(types) > 1:
            self.box2.setCurrentIndex(1)

    def combo1_callback(self, text: str):
        logging.info(f"Got callback for {text} on combo1")
        self.plot(text, 0)

    def combo2_callback(self, text: str):
        logging.info(f"Got callback for {text} on combo2")
        self.plot(text, 1)

    def replot(self):
        """
        Replots
        """
        self.plot(self.box1.currentText(), 0)
        self.plot(self.box2.currentText(), 1)

    def plot(self, item: str, index: int):
        """
        Fetches the data and plots.
        """
        timestamps, data = self.fetcher.fetch(self.current_folder, item)

        if index == 0:
            target = self.graphWidget
        else:
            target = self.graphWidget2

        target.plotItem.clear()
        clear_time = []
        clear_dat = []
        for ts, dat in zip(timestamps, data):
            if dat > 0:
                clear_time.append(ts)
                clear_dat.append(dat)

        target.plot(clear_time, clear_dat)


app = QApplication(sys.argv)
w = MainWindow()
w.show()
app.exec()
