"""The main module with all API definitions of the Feature-Engineering service"""
from fastapi import FastAPI, Body
import dataclasses
import pandas
import json

from src import features, schema


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


@app.post("/diff")
def create_diff(payload: str = Body(..., embed=True)):
    """API endpoint for the creation of differential values for all sensors that measure consumption units.

    Args:
        payload: The JSON representation of building objects.

    Returns:
        The JSON representation of the updated buildings.
    """
    buildings = features.json_to_buildings(json.loads(payload))
    features.add_diff_cols_for_consumption_units(buildings)
    return json.dumps(buildings, cls=JSONEncoder)


schema.custom_openapi(app)
