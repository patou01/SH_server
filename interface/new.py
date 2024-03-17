import logging
from pathlib import Path

import numpy as np
from PySide6.QtWidgets import QApplication, QMainWindow
import pyqtgraph as pg
import sys

from pyqtgraph import DateAxisItem

from interface.data_fetcher import CsvFetcher

logging.basicConfig(level=logging.INFO)


class MainWindow(QMainWindow):
    def __init__(self, timestamps, data):
        super(MainWindow, self).__init__()

        axis = DateAxisItem()
        self.graphWidget = pg.PlotWidget(axisItems={'bottom': axis})
        self.setCentralWidget(self.graphWidget)

        np.isfinite(timestamps[0:3])
        self.graphWidget.plot(timestamps, data)


fetcher = CsvFetcher(Path("../server/data"))

data = fetcher.fetch("bedroom", "co2")

app = QApplication(sys.argv)
w = MainWindow(data[0], data[1])
w.show()
app.exec()
