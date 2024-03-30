"""
Provides an interface to fetch the data that can then be used to make plots.
"""
import csv
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from time import time_ns


class DataFetcher(ABC):
    @abstractmethod
    def fetch(self, room: str, data_type: str):
        """
        Return eg the temperatures for the bedroom.
        """


class CsvFetcher(DataFetcher):
    def __init__(self, folder: Path):
        self.files = list(folder.glob("**/*.csv"))
        logging.info(f"Found {len(self.files)} files")

    def fetch(self, room: str, data_type: str):
        """
        Returns the content of the file at "**/room/data_type.csv"
        """
        for file in self.files:
            if file.parts[-2] == room:
                if file.name == f"{data_type}.csv":
                    logging.info(f"Found {file}")
                    with open(file, "r") as f:
                        start = time_ns()
                        reader = csv.reader(f)
                        data = [row for row in reader if row]
                        read = time_ns()
                    timestamps = [float(row[0]) for row in data]
                    points = [float(row[1]) for row in data]
                    convert = time_ns()
                    logging.info(f"time to read: {(read-start)/1e9}")
                    logging.info(f"Time to convert: {(convert-read)/1e9}")
                    return [timestamps, points]

        logging.warning(f"Nothing found for {room} {data_type}")

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
