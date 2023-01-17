"""Contains all functions related to normalizing"""
from dataclasses import dataclass

import pandas as pd


@dataclass
class Building:
    """Contains all information of a building"""

    @dataclass
    class Sensor:
        """Contains all information to describe a sensor"""
        type: str
        desc: str
        unit: str

    name: str
    sensors: list[Sensor]
    dataframe: pd.DataFrame


def min_max_normalization(data: dict[str, Building]) -> None:
    """Normalizes all data in the building-dicts dataframes to a range from 0 to 1.

    Args:
        data: A dictionary of buildings
    """
    for _, building in data.items():
        df = building.dataframe
        df = (df - df.min()) / (df.max() - df.min())
        building.dataframe = df


def mean_normalization(data: dict[str, Building]) -> None:
    """Normalizes all data in the building-dicts dataframes into a standard score.

    Args:
        data: A dictionary of buildings
    """
    for _, building in data.items():
        df = building.dataframe
        df = (df - df.mean()) / df.std()
        building.dataframe = df
