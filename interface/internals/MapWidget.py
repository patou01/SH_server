"""
Responsible for the attempt to display a map of the sensor data.
TBD how to make that nicely, for now we'll hard code coordinates
"""
from typing import List

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore

from interface.internals.geometry import house


class MapWidget(pg.GraphicsLayoutWidget):
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
        return [  # bedroom
            [0, 0],
            [3, 0],
            [3, -3],
            [2.75, -3],
            [3, -3],
            # corridor
            [3, -5],
            # living room
            [3, -2.5],
            [6, -2.5],
            [6, -6],
            [3, -6],
            [3, -5.5],
            [3, -7.5],
            [2, -7.5],
            [2, -7],
            [2, -7.5],
            [0, -7.5],
            [0, -6],
            [2, -6],
            [2, -6.5],
            [2, -4.5],
            [2, -5],
            [0, -5],
            [0, -3],
            [2, -3],
            [2, -3.5],
            [2, -3],
            [2.25, -3],
            [0, -3],
        ]
