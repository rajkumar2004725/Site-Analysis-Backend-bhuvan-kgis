from typing import List, Dict, Optional, Any
from ninja import Schema

class Coordinates(Schema):
    lat: float
    lng: float

class Details(Schema):
    distcode: str
    year: Optional[str] = None

class GeometryWKT(Schema):
    geometry_wkt: str

class PolygonCoordinates(Schema):
    coordinates_list: List[List[float]]  # List of [lng, lat]

class BoundingBox(Schema):
    min_lng: float
    min_lat: float
    max_lng: float
    max_lat: float

class RouteCoordinates(Schema):
    start: Coordinates
    end: Coordinates

class Proximity(Schema):
    coordinates: Coordinates
    theme: Optional[str] = 'all'
    buffer: Optional[int] = 3000

class VillageName(Schema):
    village_name: str

class VillageCoordinates(Schema):
    coordinates: Coordinates

class Geoid(Schema):
    area_id: str
    datum: Optional[str] = 'geoid'
    se: Optional[str] = 'CDEM'

from pydantic import BaseModel

class ApiResponse(BaseModel):
    data: dict | None = None
    error: str | None = None