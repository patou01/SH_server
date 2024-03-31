"""
Responsible for the attempt to display a map of the sensor data.
TBD how to make that nicely, for now we'll hard code coordinates
"""
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class MapWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Trying to map it out"))
        window = pg.GraphicsLayoutWidget(show=True)
        plt = window.addPlot(title="Plot")
        line = pg.PolyLineROI(
            [[0, 0], [10, 10], [10, 30], [30, 10]],
            closed=False,
            maxBounds=QtCore.QRectF(0, 0, 30, 30),
        )
        plt.addItem(line)
        plt.disableAutoRange("xy")
        plt.autoRange()
        layout.addItem(window)
        self.setLayout(layout)
