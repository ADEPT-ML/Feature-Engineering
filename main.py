"""The main module with all API definitions of the Feature-Engineering service"""
from fastapi import FastAPI, Body, HTTPException
import dataclasses
import pandas
import json

from src import features, schema, normalization

app = FastAPI()


class JSONEncoder(json.JSONEncoder):
    """An enhanced version of the JSONEncoder class containing support for dataclasses and DataFrames."""

    def default(self, o):
        """Adds JSON encoding support for dataclasses and DataFrames.

        This function overrides the default function of JSONEncoder and adds support for encoding dataclasses and
        Pandas DataFrames as JSON. Uses the superclass default function for all other types.

        Args:
            o: The object to serialize into a JSON representation.

        Returns:
            The JSON representation of the specified object.
        """

        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        if isinstance(o, pandas.DataFrame):
            return o.to_json()
        return super().default(o)


@app.get(
    "/",
    name="Root path",
    summary="Returns the routes available through the API",
    description="Returns a route list for easier use of API through HATEOAS",
    response_description="List of urls to all available routes",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {
                        "payload": [
                            {
                                "path": "/examplePath",
                                "name": "example route"
                            }
                        ]
                    }
                }
            },
        }
    }
)
async def root():
    """Root API endpoint that lists all available API endpoints.

    Returns:
        A complete list of all possible API endpoints.
    """
    route_filter = ["openapi", "swagger_ui_html", "swagger_ui_redirect", "redoc_html"]
    url_list = [{"path": route.path, "name": route.name} for route in app.routes if route.name not in route_filter]
    return url_list


@app.post(
    "/diff",
    name="Creates diff values for all sensors that measure consumption units",
    summary="Endpoint for the creation of differential values for all sensors that measure consumption units",
    description="Add news columns to the building-dicts dataframe with diff values",
    response_description="A JSON representation of the supplied building objects with the added diff columns",
    responses={
        200: {
            "description": "JSON representation of the supplied building objects.",
            "content": {
                "application/json": {
                    "example":
                        "{\"EF 40a_small\": {"
                            "\"name\": \"EF 40a_small\", "
                            "\"sensors\": [{\"type\": \"Elektrizit\ät\", \"desc\": \"P Summe\", \"unit\": \"kW\"}], "
                            "\"dataframe\": \"{"
                                "\\\"Elektrizit\\\ät\\\":{"
                                    "\\\"1642809600000\\\":4.658038,\\\"1642810500000\\\":4.426662,"
                                    "\\\"1642811400000\\\":4.195286,\\\"1642812300000\\\":4.1157735,"
                                    "\\\"1642813200000\\\":4.036261,\\\"1642814100000\\\":4.0861445,"
                                    "\\\"1642815000000\\\":4.136028,\\\"1642815900000\\\":4.1354125,"
                                    "\\\"1642816800000\\\":4.134797,\\\"1642817700000\\\":4.1507635,"
                                    "\\\"1642818600000\\\":4.16673,\\\"1642819500000\\\":4.1331225,"
                                    "\\\"1642820400000\\\":4.099515,\\\"1642821300000\\\":4.108903,"
                                    "\\\"1642822200000\\\":4.118291,\\\"1642823100000\\\":4.366549,"
                                    "\\\"1642824000000\\\":4.614807,\\\"1642824900000\\\":4.5520855,"
                                    "\\\"1642825800000\\\":4.489364,\\\"1642826700000\\\":4.5500675,"
                                    "\\\"1642827600000\\\":4.610771,\\\"1642828500000\\\":4.618229,"
                                    "\\\"1642829400000\\\":4.625687},"
                                    "\\\"Elektrizit\\\ät Diff\\\":{\\\"1642809600000\\\":null,\\\"1642810500000\\\":-0.231376,"
                                    "\\\"1642811400000\\\":-0.231376,\\\"1642812300000\\\":-0.0795125,\\\"1642813200000\\\":-0.0795125,"
                                    "\\\"1642814100000\\\":0.0498835,\\\"1642815000000\\\":0.0498835,\\\"1642815900000\\\":-0.0006155,"
                                    "\\\"1642816800000\\\":-0.0006155,\\\"1642817700000\\\":0.0159665,\\\"1642818600000\\\":0.0159665,"
                                    "\\\"1642819500000\\\":-0.0336075,\\\"1642820400000\\\":-0.0336075,\\\"1642821300000\\\":0.009388,"
                                    "\\\"1642822200000\\\":0.009388,\\\"1642823100000\\\":0.248258,\\\"1642824000000\\\":0.248258,"
                                    "\\\"1642824900000\\\":-0.0627215,\\\"1642825800000\\\":-0.0627215,\\\"1642826700000\\\":0.0607035,"
                                    "\\\"1642827600000\\\":0.0607035,\\\"1642828500000\\\":0.007458,\\\"1642829400000\\\":0.007458"
                                "}"
                            "}\""
                        "}}"
                }
            },
        },
        400: {
            "description": "Payload can not be empty.",
            "content": {
                "application/json": {
                    "example": {"detail": "Payload can not be empty"}
                }
            },
        },
        500: {
            "description": "Internal server error.",
            "content": {
                "application/json": {
                    "example": {"detail": "Internal server error"}
                }
            },
        }
    },
    tags=["Features"]
)
def create_diff(payload: str = Body(..., embed=True)):
    """API endpoint for the creation of differential values for all sensors that measure consumption units.

    Args:
        payload: The JSON representation of building objects.

    Returns:
        The JSON representation of the updated buildings.
    """
    try:
        if not payload:
            raise HTTPException(status_code=400, detail="Payload can not be empty")
        buildings = features.json_to_buildings(json.loads(payload))
        features.add_diff_cols_for_consumption_units(buildings)

        return json.dumps(buildings, cls=JSONEncoder)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.post(
    "/normalize/minmax",
    name="Min-Max-Normalization",
    summary="Normalizes all columns in the building-dicts dataframe using Min-Max-Normalization",
    description="Normalizes all available columns in the building-dicts dataframe using min-max-normalization",
    response_description="A JSON representation of the supplied building object",
    responses={
        200: {
            "description": "JSON representation of the supplied building objects.",
            "content": {
                "application/json": {
                    "example":
                        "{\"EF 40a_small\": {"
                            "\"name\": \"EF 40a_small\", "
                            "\"sensors\": [{\"type\": \"Elektrizit\ät\", \"desc\": \"P Summe\", \"unit\": \"kW\"}], "
                            "\"dataframe\": \"{"
                                "\\\"Elektrizit\\\ät\\\":{"
                                    "\\\"1642809600000\\\":1.0,\\\"1642810500000\\\":0.6278794487,"
                                    "\\\"1642811400000\\\":0.2557588975,\\\"1642812300000\\\":0.1278794487,"
                                    "\\\"1642813200000\\\":0.0,\\\"1642814100000\\\":0.0802273162,"
                                    "\\\"1642815000000\\\":0.1604546324,\\\"1642815900000\\\":0.1594647277,"
                                    "\\\"1642816800000\\\":0.158474823,\\\"1642817700000\\\":0.1841536435,"
                                    "\\\"1642818600000\\\":0.2098324641,\\\"1642819500000\\\":0.1557817353,"
                                    "\\\"1642820400000\\\":0.1017310065,\\\"1642821300000\\\":0.1168296672,"
                                    "\\\"1642822200000\\\":0.131928328,\\\"1642823100000\\\":0.5312000926,"
                                    "\\\"1642824000000\\\":0.9304718573,\\\"1642824900000\\\":0.8295972672,"
                                    "\\\"1642825800000\\\":0.7287226771,\\\"1642826700000\\\":0.8263517306,"
                                    "\\\"1642827600000\\\":0.9239807841,\\\"1642828500000\\\":0.9359754381,"
                                    "\\\"1642829400000\\\":0.9479700922"
                                "}"
                            "}\""
                        "}}"
                }
            },
        },
        400: {
            "description": "Payload can not be empty.",
            "content": {
                "application/json": {
                    "example": {"detail": "Payload can not be empty"}
                }
            },
        },
        500: {
            "description": "Internal server error.",
            "content": {
                "application/json": {
                    "example": {"detail": "Internal server error"}
                }
            },
        }
    },
    tags=["Normalization"]
)
def normalize_minmax(payload: str = Body(..., embed=True)):
    """API endpoint for normalizing all data in a building objects dataframe to a range from 0 to 1.

    Args:
        payload: The JSON representation of building objects.

    Returns:
        The JSON representation of the updated buildings.
    """
    try:
        if not payload:
            raise HTTPException(status_code=400, detail="Payload can not be empty")
        buildings = features.json_to_buildings(json.loads(payload))
        normalization.min_max_normalization(buildings)

        return json.dumps(buildings, cls=JSONEncoder)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.post(
    "/normalize/mean",
    name="Mean-Normalization",
    summary="Normalizes all columns in the building-dicts dataframe using Mean-Normalization",
    description="Normalizes all available columns in the building-dicts dataframe using mean-normalization",
    response_description="A JSON representation of the supplied building object",
    responses={
        200: {
            "description": "JSON representation of the supplied building objects.",
            "content": {
                "application/json": {
                    "example":
                        "{\"EF 40a_small\": {"
                            "\"name\": \"EF 40a_small\", "
                            "\"sensors\": [{\"type\": \"Elektrizit\ät\", \"desc\": \"P Summe\", \"unit\": \"kW\"}], "
                            "\"dataframe\": \"{"
                                "\\\"Elektrizit\\\ät\\\":{"
                                    "\\\"1642809600000\\\":1.5355268051,\\\"1642810500000\\\":0.5147979489,"
                                    "\\\"1642811400000\\\":-0.5059309073,\\\"1642812300000\\\":-0.8567049857,"
                                    "\\\"1642813200000\\\":-1.2074790642,\\\"1642814100000\\\":-0.9874150649,"
                                    "\\\"1642815000000\\\":-0.7673510656,\\\"1642815900000\\\":-0.7700663801,"
                                    "\\\"1642816800000\\\":-0.7727816947,\\\"1642817700000\\\":-0.7023445392,"
                                    "\\\"1642818600000\\\":-0.6319073837,\\\"1642819500000\\\":-0.7801688501,"
                                    "\\\"1642820400000\\\":-0.9284303164,\\\"1642821300000\\\":-0.8870146013,"
                                    "\\\"1642822200000\\\":-0.8455988862,\\\"1642823100000\\\":0.2496059077,"
                                    "\\\"1642824000000\\\":1.3448107015,\\\"1642824900000\\\":1.0681111088,"
                                    "\\\"1642825800000\\\":0.7914115162,\\\"1642826700000\\\":1.0592085829,"
                                    "\\\"1642827600000\\\":1.3270056497,\\\"1642828500000\\\":1.3599070561,"
                                    "\\\"1642829400000\\\":1.3928084625"
                                "}"
                            "}\""
                        "}}"
                }
            },
        },
        400: {
            "description": "Payload can not be empty.",
            "content": {
                "application/json": {
                    "example": {"detail": "Payload can not be empty"}
                }
            },
        },
        500: {
            "description": "Internal server error.",
            "content": {
                "application/json": {
                    "example": {"detail": "Internal server error"}
                }
            },
        }
    },
    tags=["Normalization"]
)
def normalize_mean(payload: str = Body(..., embed=True)):
    """API endpoint for normalizing all data in a building objects dataframe into a standard score.

    Args:
        payload: The JSON representation of building objects.
        
    Returns:
        The JSON representation of the updated buildings.
    """
    try:
        if not payload:
            raise HTTPException(status_code=400, detail="Payload can not be empty")
        buildings = features.json_to_buildings(json.loads(payload))
        normalization.mean_normalization(buildings)

        return json.dumps(buildings, cls=JSONEncoder)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Internal Server Error")


schema.custom_openapi(app)
