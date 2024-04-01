"""
Responsible for the attempt to display a map of the sensor data.
TBD how to make that nicely, for now we'll hard code coordinates
"""
from datetime import datetime
from typing import List

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QSlider, QVBoxLayout, QWidget

from interface.internals.data_fetcher import DataFetcher
from interface.internals.geometry import house


class TempWidget(QWidget):
    def __init__(self, fetcher: DataFetcher):
        super().__init__()
        self.fetcher = fetcher
        layout = QVBoxLayout()
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Select date"))
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(self.fetcher.get_start_date().timestamp())
        slider.setMaximum(self.fetcher.get_end_date().timestamp())
        self.time_slider = slider
        self.time_slider.valueChanged.connect(self.time_slider_cb)
        self.date_label = QLabel("N/A")
        self.time_slider_cb()
        self.slider_date = None
        date_layout.addWidget(slider)
        date_layout.addWidget(self.date_label)
        layout.addLayout(date_layout)
        layout.addWidget(Map())
        self.layout = layout
        self.setLayout(layout)

    def time_slider_cb(self):
        self.slider_date = datetime.fromtimestamp(self.time_slider.value())
        self.date_label.setText(self.slider_date.strftime("%Y-%m-%d  %H:%M"))


class Map(pg.GraphicsLayoutWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        plt = self.addPlot(title="Plot")

        polyline = pg.PolyLineROI(
            self.wall_points, closed=True, maxBounds=QtCore.QRectF(0, 0, 30, 30)
        )

        plt.addItem(polyline)

        plt.disableAutoRange("xy")
        plt.autoRange()

    @property
    def wall_points(self) -> List[List[float]]:
        """
        Kinda yikes to do it this way, but at least it gets out of the way.
        :return:
        """
        return house.as_points()
