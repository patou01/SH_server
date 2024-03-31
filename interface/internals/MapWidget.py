"""
Responsible for the attempt to display a map of the sensor data.
TBD how to make that nicely, for now we'll hard code coordinates
"""
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class MapWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Trying to map it out"))

        self.setLayout(layout)
