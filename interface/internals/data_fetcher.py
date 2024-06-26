"""
Provides an interface to fetch the data that can then be used to make plots.
"""
import datetime
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import pandas as pd


@dataclass
class DataPoints:
    timestamps: List[float]
    points: List[float]


class DataFetcher(ABC):
    @abstractmethod
    def fetch(self, data_type: str) -> DataPoints:
        """
        Return eg the temperatures for the currently selected room
        """

    @abstractmethod
    def get_start_date(self) -> datetime.datetime:
        """
        Return the first timestamp found
        :return:
        """

    @abstractmethod
    def get_end_date(self) -> datetime.datetime:
        """
        return the last timestamp found
        :return:
        """

    @abstractmethod
    def get_available_data_types(self) -> List[str]:
        """
        Return type of measurements that can be used
        :return:
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
        self.room = None
        logging.info(f"Found {len(self.files)} files")
        self.data: Dict[str, Dict[str, DataPoints]] = {}
        self.read_all_files()

    def set_room(self, room: str):
        self.room = room

    def read_all_files(self):
        """
        Read content of all files and stores in the data dictionary.
        :return:
        """
        for file in self.files:
            room = file.parts[-2]
            if room not in self.data:
                self.data[room] = {}

            df = pd.read_csv(file, names=["time", "data"])
            data = df.loc[df["data"] > 0]
            self.data[room][file.name.replace(".csv", "")] = DataPoints(
                data["time"].array, data["data"].array
            )

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

    def get_end_date(self):
        latest = datetime.datetime(
            2000, 1, 1
        ).timestamp()  # use a datetime from somewhat long ago

        for room in self.data.values():
            for data_type in room.values():
                if data_type.timestamps[-1] > latest:
                    latest = data_type.timestamps[-1]
        return datetime.datetime.fromtimestamp(latest)  # todo, handle timezone

    def fetch(self, data_type: str):
        """
        Returns the content of the file at "**/room/data_type.csv"
        """
        logging.info(f"Looking for {self.room}, {data_type}")
        if self.room in self.data:
            if data_type in self.data[self.room]:
                return (
                    self.data[self.room][data_type].timestamps,
                    self.data[self.room][data_type].points,
                )

        logging.warning(f"Nothing found for {self.room}, {data_type}")
        return [], []

    def get_available_data_types(self, room: str = None):
        """
        Return the different type of measurements that are available for room
        :param room:
        :return:
        """
        if self.room is None or room is not None:
            self.room = room

        ret_values = []
        for file in self.files:
            if file.parts[-2] == self.room:
                ret_values.append(file.parts[-1].replace(".csv", ""))
        return ret_values
