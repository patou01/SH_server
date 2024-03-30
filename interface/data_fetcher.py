"""
Provides an interface to fetch the data that can then be used to make plots.
"""
import csv
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from time import time_ns
from typing import List


@dataclass
class DataPoints:
    timestamps: List[float]
    points: List[float]


class DataFetcher(ABC):
    @abstractmethod
    def fetch(self, room: str, data_type: str):
        """
        Return eg the temperatures for the bedroom.
        """


class CsvFetcher(DataFetcher):
    """
    Fetch data from csv files. THe files are expected to sit under the folder in the constructor.
    The files should be of the type "folder/room/data_type.csv".
    eg "folder/bedroom/temperature.csv"
    Data inside each csv is expected as "timestamp, data" for each row
    """

    def __init__(self, folder: Path):
        self.files = list(folder.glob("**/*.csv"))
        logging.info(f"Found {len(self.files)} files")
        self.data = {}
        self.read_all_files()

    def read_all_files(self):
        """
        Read content of all files and stores in the data dictionary.
        :return:
        """
        start = time_ns()
        for file in self.files:
            room = file.parts[-2]
            if room not in self.data:
                self.data[room] = {}

            with open(file, "r") as f:
                reader = csv.reader(f)
                data = [row for row in reader if row]  # remove empty rows
            datapoints = DataPoints(
                [float(row[0]) for row in data], [float(row[1]) for row in data]
            )
            self.data[room][file.name.replace(".csv", "")] = datapoints

        end = time_ns()
        logging.info(f"Took {(end-start)/1e9} s to read all files")

    def fetch(self, room: str, data_type: str):
        """
        Returns the content of the file at "**/room/data_type.csv"
        """
        logging.info(f"Looking for {room}, {data_type}")
        if room in self.data:
            if data_type in self.data[room]:
                return (
                    self.data[room][data_type].timestamps,
                    self.data[room][data_type].points,
                )

        logging.warning(f"Nothing found for {room}, {data_type}")
        return [], []

    def get_available_data_types(self, room: str):
        """
        Return the different type of measurements that are available for room
        :param room:
        :return:
        """
        ret_values = []
        for file in self.files:
            if file.parts[-2] == room:
                ret_values.append(file.parts[-1].replace(".csv", ""))
        return ret_values
        return [
            file.parts[-1].replace(".csv", "")
            for file in self.files
            if file.parts[-2] == room
        ]
