"""
Provides an interface to fetch the data that can then be used to make plots.
"""
import datetime
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from time import time_ns
from typing import Dict, List

import pandas as pd


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
        self.data: Dict[Dict[str, DataPoints]] = {}
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

            df = pd.read_csv(file, names=["time", "data"])
            data = df.loc[df["data"] > 0]
            self.data[room][file.name.replace(".csv", "")] = DataPoints(
                data["time"], data["data"]
            )

        end = time_ns()
        logging.info(f"Took {(end-start)/1e9} s to read all files")

    def get_start_date(self):
        """
        Returns first date found in files
        :return:
        """
        earliest = datetime.datetime.now().timestamp()

        for room in self.data.values():
            for data_type in room.values():
                if data_type.timestamps[0] < earliest:
                    earliest = data_type.timestamps[0]
        return datetime.datetime.fromtimestamp(earliest)  # todo, handle timezone

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
