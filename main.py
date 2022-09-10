import dataclasses
import json
import pandas
import features

from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        if isinstance(o, pandas.DataFrame):
            return o.to_json()
        return super().default(o)


@app.get("/")
def read_root():
    return {"Hello": "there!"}


@app.post("/diff")
def create_diff(payload: str = Body(..., embed=True)):
    buildings = features.json_to_buildings(json.loads(payload))
    features.add_diff_cols_for_consumption_units(buildings)
    return json.dumps(buildings, cls=JSONEncoder)
