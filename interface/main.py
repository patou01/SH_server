import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List

import pyqtgraph as pg
from pyqtgraph import DateAxisItem
from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDateTimeEdit,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from interface.data_fetcher import CsvFetcher, DataFetcher

logging.basicConfig(level=logging.INFO)


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


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.fetcher = CsvFetcher(Path("../server/data"))
        self.fetcher.set_room("bedroom")
        self.current_folder = "bedroom"

        self.layout = QVBoxLayout()
        self.start_timestamp = 0
        self.end_timestamp = 2000000000

        folder_button = QPushButton("Select folder")
        folder_button.clicked.connect(self.find_folder)
        widget = QWidget()
        widget.setLayout(self.layout)

        from_box = self._init_from_boxes()
        until_box = self._init_end_boxes()

        self.layout.addWidget(folder_button)
        self.layout.addLayout(from_box)
        self.layout.addLayout(until_box)
        self.plots = [
            PlotLayout(
                self.fetcher,
                self.start_timestamp,
                self.end_timestamp,
                self.delete_plot,
                0,
            )
        ]
        self.layout.addLayout(self.plots[0])

        add_plot_layout = QHBoxLayout()
        add_button = QPushButton("Add plot")
        add_button.pressed.connect(self.add_button)
        add_plot_layout.addWidget(add_button)
        self.layout.addLayout(add_plot_layout)
        self.setCentralWidget(widget)

    def _init_from_boxes(self):
        """
        Initialize the part that is "from timestamp" box
        :return:
        """
        from_box = QHBoxLayout()
        self.from_date = QDateTimeEdit(self.fetcher.get_start_date())
        self.from_date.setCalendarPopup(True)
        self.from_date.setDisplayFormat("yyyy/M/d")
        self.from_date.dateTimeChanged.connect(self.start_hours_callback)
        self.from_hour = QDateTimeEdit(QDate.currentDate())
        self.from_hour.setDisplayFormat("h:mm")
        self.from_hour.dateTimeChanged.connect(self.start_hours_callback)
        from_box.addWidget(QLabel("From"))
        from_box.addWidget(self.from_date)
        from_box.addWidget(self.from_hour)
        return from_box

    def _init_end_boxes(self):
        until_box = QHBoxLayout()
        self.until_date = QDateTimeEdit(self.fetcher.get_end_date())
        self.until_date.setCalendarPopup(True)
        self.until_date.setDisplayFormat("yyyy/M/d")
        self.until_date.dateTimeChanged.connect(self.end_hours_callback)
        self.until_hour = QDateTimeEdit(QDate.currentDate())
        self.until_hour.setDisplayFormat("h:mm")
        self.until_hour.dateTimeChanged.connect(self.end_hours_callback)
        until_box.addWidget(QLabel("Until"))
        until_box.addWidget(self.until_date)
        until_box.addWidget(self.until_hour)

        return until_box

    def start_hours_callback(self):
        # todo fix timezones stuff, it's ugly.
        from_date = self.from_date.dateTime().toPython()
        from_hour = self.from_hour.dateTime().toPython()
        start = datetime(
            from_date.year,
            from_date.month,
            from_date.day,
            from_hour.hour,
            from_hour.minute,
        )
        self.start_timestamp = start.timestamp()
        for plot in self.plots:
            plot.set_start(self.start_timestamp)

    def end_hours_callback(self):
        until_date = self.until_date.dateTime().toPython()
        until_hour = self.until_hour.dateTime().toPython()
        end = datetime(
            until_date.year,
            until_date.month,
            until_date.day,
            until_hour.hour,
            until_hour.minute,
        )
        self.end_timestamp = end.timestamp()
        for plot in self.plots:
            plot.set_end(self.end_timestamp)

    def add_button(self):
        layout = PlotLayout(
            self.fetcher,
            self.start_timestamp,
            self.end_timestamp,
            self.delete_plot,
            len(self.plots),
        )
        self.plots.append(layout)
        self.layout.insertLayout(self.layout.count() - 1, layout)

    def find_folder(self):
        logging.info("Searching!")
        dialog = QFileDialog(directory=os.path.dirname(__file__))
        folder_path = dialog.getExistingDirectory()
        self.current_folder = Path(folder_path).parts[-1]
        logging.info(f"Updated current folder to {self.current_folder}")
        self.fetcher.set_room(self.current_folder)
        self.update_combo_texts()

    def update_combo_texts(self):
        """
        When the folder is changed, we need to update the data that can be plotted
        """
        types = self.fetcher.get_available_data_types(self.current_folder)
        logging.info(f"Updated combo texts to {types}")
        for plot in self.plots:
            plot.update_combo_texts(types)

    def delete_plot(self, which: int):
        """
        Delete the plot layout with id which and remove it from the list of plots.
        Note: This function is called after the delete of the layout itself
        :param which:
        :return:
        """
        self.layout.removeItem(self.plots[which])
        for n, plot in enumerate(self.plots):
            if plot.id == which:
                self.plots.pop(n)


app = QApplication(sys.argv)
w = MainWindow()
w.show()
app.exec()
