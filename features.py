import json
from dataclasses import dataclass
import pandas as pd

@dataclass
class Building:
    @dataclass
    class Sensor:
        type: str
        desc: str
        unit: str

    name: str
    sensors: list[Sensor]
    dataframe: pd.DataFrame

def json_to_buildings(data: dict) -> dict:
    buildings = dict()
    for k, b in data.items():
        sensors = [Building.Sensor(s["type"], s["desc"], s["unit"]) for s in b["sensors"]]
        df_json = json.loads(b["dataframe"])
        df = pd.DataFrame(df_json)
        df.index = pd.to_datetime(df.index.values, unit='ms')
        buildings[k] = Building(k, sensors, df)
    return buildings

def add_diff_cols_for_consumption_units(buildings: dict) -> None:
    for _, building in buildings.items():
        sensors = [s for s in building.sensors if s.unit in ["kWh", "m³", "kvarh"]]
        diff_values = building.dataframe.diff(periods=1)
        for s in sensors:
            building.dataframe[s.type + " Diff"] = diff_values[s.type]
            building.sensors.append(Building.Sensor(s.type + " Diff", s.desc, s.unit + " / 15 min"))