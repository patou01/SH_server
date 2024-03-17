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
    def __init__(self):
        super(MainWindow, self).__init__()
        self.fetcher = CsvFetcher(Path("../server/data"))

        data1 = self.fetcher.fetch("bedroom", "co2")
        data2 = self.fetcher.fetch("bedroom", "temperature")

        axis = DateAxisItem()
        layout = QVBoxLayout()

        horiz1 = QHBoxLayout()

        self.graphWidget = pg.PlotWidget(axisItems={'bottom': axis})
        self.graphWidget.plot(data1[0], data1[1])

        axis2 = DateAxisItem()
        self.graphWidget2 = pg.PlotWidget(axisItems={'bottom': axis2})
        self.graphWidget2.plot(data2[0], data2[1])

        types = self.fetcher.get_available_data_types()

        widget = QWidget()
        widget.setLayout(layout)
        box1 = QComboBox()
        box1.addItems(types)
        box1.currentTextChanged.connect(self.combo1_callback)

        horiz1.addWidget(box1)
        horiz1.addWidget(self.graphWidget)

        horiz2 = QHBoxLayout()
        box2 = QComboBox()
        box2.addItems(types)
        box2.currentTextChanged.connect(self.combo2_callback)
        horiz2.addWidget(box2)
        horiz2.addWidget(self.graphWidget2)

        layout.addLayout(horiz1)
        layout.addLayout(horiz2)

        self.setCentralWidget(widget)

    def combo1_callback(self, text: str):
        self.plot(text, 0)

    def combo2_callback(self, text: str):
        self.plot(text, 1)


    def plot(self, item: str, index: int):
        """
        Fetches the data and plots.
        """
        timestamps, data = self.fetcher.fetch("bedroom", item)

        if index == 0:
            target = self.graphWidget
        else:
            target = self.graphWidget2

        target.plotItem.clear()
        target.plot(timestamps, data)


app = QApplication(sys.argv)
w = MainWindow()
w.show()
app.exec()
