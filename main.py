import dataclasses
import json
import pandas
from src import features, schema

from fastapi import FastAPI, Body
# from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
# origins = ["*"]
#
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
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
    buildings = features.json_to_buildings(json.loads(payload))
    features.add_diff_cols_for_consumption_units(buildings)
    return json.dumps(buildings, cls=JSONEncoder)


schema.custom_openapi(app)
