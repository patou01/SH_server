"""
Responsible for the plot, combo box and "delete me" button that appears on the main tab
"""
from typing import List

import pyqtgraph as pg
from pyqtgraph import DateAxisItem
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QPushButton, QVBoxLayout

from interface.internals.data_fetcher import DataFetcher


class PlotLayout(QHBoxLayout):
    def __init__(
        self,
        fetcher: DataFetcher,
        start_timestamp: float,
        end_timestamp: float,
        delete_callback,
        plot_id: int,
    ):
        super().__init__()
        self.fetcher = fetcher
        self.start_timestamp = start_timestamp
        self.end_timestamp = end_timestamp
        self.delete_callback = delete_callback
        self.id = plot_id

        available_data = self.fetcher.get_available_data_types()

        vert_layout = QVBoxLayout()
        self.box = QComboBox()
        self.box.addItems(available_data)
        self.box.currentTextChanged.connect(self.combo_callback)
        axis = DateAxisItem()
        self.graph = pg.PlotWidget(axisItems={"bottom": axis})

        vert_layout.addWidget(self.box)

        if self.id > 0:
            self.delete_button = QPushButton("Delete me")
            self.delete_button.pressed.connect(self.delete)
            vert_layout.addWidget(self.delete_button)
        self.addLayout(vert_layout)
        self.addWidget(self.graph)
        self.plot()

    def delete(self):
        self.delete_button.deleteLater()
        self.box.deleteLater()
        self.deleteLater()
        self.delete_callback(self.id)

    def combo_callback(self, text: str):
        """
        Just done to get rid of the "text" input. But maybe it's not needed...
        :param text:
        :return:
        """
        self.plot()

    def set_start(self, start_ts: float):
        """
        Set start timestamp
        :param start_ts:
        :return:
        """
        self.start_timestamp = start_ts
        self.plot()

    def set_end(self, end_ts: float):
        """
        Set end timestamp
        :param end_ts:
        :return:
        """
        self.end_timestamp = end_ts
        self.plot()

    def plot(self):
        measurement = self.box.currentText()
        timestamps, data = self.fetcher.fetch(measurement)

        self.graph.plotItem.clear()
        clear_time = []
        clear_dat = []

        for ts, dat in zip(timestamps, data):
            if self.start_timestamp < ts < self.end_timestamp:
                if dat > 0:
                    clear_time.append(ts)
                    clear_dat.append(dat)

        if clear_time:
            self.graph.plot(clear_time, clear_dat)

    def update_combo_texts(self, types: List[str]):
        self.box.blockSignals(True)
        self.box.clear()
        self.box.addItems(types)
        self.box.blockSignals(False)
        self.box.setCurrentIndex(0)
