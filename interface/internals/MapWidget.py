"""
Responsible for the attempt to display a map of the sensor data.
TBD how to make that nicely, for now we'll hard code coordinates
"""
from datetime import datetime
from typing import List

from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPixmap
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


class Map(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        canvas = QPixmap(self.size())
        canvas.fill(Qt.white)
        self.setPixmap(canvas)
        self.draw_something()

    def draw_something(self):
        canvas = self.pixmap()
        painter = QPainter(canvas)
        x_offset = 50
        y_offset = 50
        for n, point in enumerate(self.wall_points):
            if n < len(self.wall_points) - 1:
                start = [int(point[0]) + x_offset, int(point[1]) + y_offset]
                end = [
                    int(self.wall_points[n + 1][0]) + x_offset,
                    int(self.wall_points[n + 1][1]) + y_offset,
                ]
                painter.drawLine(*start, *end)

        # close it
        end = self.wall_points[0]
        start = self.wall_points[-1]
        painter.drawLine(
            int(start[0]) + x_offset,
            int(start[1]) + y_offset,
            int(end[0]) + x_offset,
            int(end[1]) + y_offset,
        )
        painter.end()
        self.setPixmap(canvas)

    @property
    def wall_points(self) -> List[List[float]]:
        """
        Kinda yikes to do it this way, but at least it gets out of the way.
        :return:
        """
        return house.as_points()
