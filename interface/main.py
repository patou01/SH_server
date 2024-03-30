import logging
import os
import sys
from datetime import datetime
from pathlib import Path

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

from interface.data_fetcher import CsvFetcher

logging.basicConfig(level=logging.INFO)


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.fetcher = CsvFetcher(Path("../server/data"))

        self.current_folder = "bedroom"

        axis = DateAxisItem()
        self.layout = QVBoxLayout()

        horiz1 = QHBoxLayout()

        self.graphWidget = pg.PlotWidget(axisItems={"bottom": axis})

        axis2 = DateAxisItem()
        self.graphWidget2 = pg.PlotWidget(axisItems={"bottom": axis2})

        types = self.fetcher.get_available_data_types(self.current_folder)

        folder_button = QPushButton("Select folder")
        folder_button.clicked.connect(self.find_folder)
        widget = QWidget()
        widget.setLayout(self.layout)
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

        from_box = QHBoxLayout()
        self.from_date = QDateTimeEdit(self.fetcher.get_start_date())
        self.from_date.setCalendarPopup(True)
        self.from_date.setDisplayFormat("yyyy/M/d")
        self.from_date.dateTimeChanged.connect(self.hours_callback)
        self.from_hour = QDateTimeEdit(QDate.currentDate())
        self.from_hour.setDisplayFormat("h:mm")
        self.from_hour.dateTimeChanged.connect(self.hours_callback)
        from_box.addWidget(QLabel("From"))
        from_box.addWidget(self.from_date)
        from_box.addWidget(self.from_hour)

        until_box = QHBoxLayout()
        self.until_date = QDateTimeEdit(self.fetcher.get_end_date())
        self.until_date.setCalendarPopup(True)
        self.until_date.setDisplayFormat("yyyy/M/d")
        self.until_date.dateTimeChanged.connect(self.hours_callback)
        self.until_hour = QDateTimeEdit(QDate.currentDate())
        self.until_hour.setDisplayFormat("h:mm")
        self.until_hour.dateTimeChanged.connect(self.hours_callback)
        until_box.addWidget(QLabel("Until"))
        until_box.addWidget(self.until_date)
        until_box.addWidget(self.until_hour)

        self.layout.addWidget(folder_button)
        self.layout.addLayout(from_box)
        self.layout.addLayout(until_box)
        self.layout.addLayout(horiz1)
        self.layout.addLayout(horiz2)

        add_plot_layout = QHBoxLayout()
        add_button = QPushButton("Add plot")
        add_button.pressed.connect(self.add_button)
        add_plot_layout.addWidget(add_button)
        self.layout.addLayout(add_plot_layout)
        self.setCentralWidget(widget)
        self.replot()

    def add_button(self):
        print("pressed")

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

    def hours_callback(self, date):
        self.replot()

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
        start_ts = start.timestamp()

        until_date = self.until_date.dateTime().toPython()
        until_hour = self.until_hour.dateTime().toPython()
        end = datetime(
            until_date.year,
            until_date.month,
            until_date.day,
            until_hour.hour,
            until_hour.minute,
        )
        end_ts = end.timestamp()

        for ts, dat in zip(timestamps, data):
            if start_ts < ts < end_ts:
                if dat > 0:
                    clear_time.append(ts)
                    clear_dat.append(dat)

        if clear_time:
            target.plot(clear_time, clear_dat)


app = QApplication(sys.argv)
w = MainWindow()
w.show()
app.exec()
