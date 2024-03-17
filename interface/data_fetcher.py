"""
Provides an interface to fetch the data that can then be used to make plots.
"""
import csv
import logging
from abc import abstractmethod, ABC
from datetime import datetime
from pathlib import Path


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
                    with open(file, 'r') as f:
                        reader = csv.reader(f)
                        data = [row for row in reader if row]
                    timestamps = [float(row[0]) for row in data]
                    points = [float(row[1]) for row in data]
                    return [timestamps, points]

        logging.warning(f"Nothing found for {room} {data_type}")

    def get_available_data_types(self):
        return [file.parts[-1].replace(".csv", "") for file in self.files]
