import logging
from pathlib import Path

import numpy as np
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QHBoxLayout, QComboBox
import pyqtgraph as pg
import sys

from pyqtgraph import DateAxisItem, Color

from interface.data_fetcher import CsvFetcher

logging.basicConfig(level=logging.INFO)


class MainWindow(QMainWindow):
    def __init__(self, timestamps, data):
        super(MainWindow, self).__init__()

        axis = DateAxisItem()
        layout = QVBoxLayout()

        horiz1 = QHBoxLayout()

        self.graphWidget = pg.PlotWidget(axisItems={'bottom': axis})
        self.graphWidget.plot(timestamps[0], data[0])

        axis2 = DateAxisItem()
        self.graphWidget2 = pg.PlotWidget(axisItems={'bottom': axis2})
        self.graphWidget2.plot(timestamps[1], data[1])

        types = fetcher.get_available_data_types()


        widget = QWidget()
        widget.setLayout(layout)
        box1 = QComboBox()
        box1.addItems(types)
        horiz1.addWidget(box1)
        horiz1.addWidget(self.graphWidget)

        horiz2 = QHBoxLayout()
        box2 = QComboBox()
        box2.addItems(types)
        horiz2.addWidget(box2)
        horiz2.addWidget(self.graphWidget2)


        layout.addLayout(horiz1)
        layout.addLayout(horiz2)

        self.setCentralWidget(widget)


fetcher = CsvFetcher(Path("../server/data"))

data1 = fetcher.fetch("bedroom", "co2")
data2 = fetcher.fetch("bedroom", "temperature")

app = QApplication(sys.argv)
w = MainWindow([data1[0], data2[0]], [data1[1], data2[1]])
w.show()
app.exec()
