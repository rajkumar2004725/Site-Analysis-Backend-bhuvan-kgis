from ninja import Schema 
from pydantic import field_validator
from typing import List

class AdminHierarchyRequest(Schema):
    deptcode: int
    applncode: int
    code: int
    type: str

class AdminHierarchyResponse(Schema):
    districtName: str | None = None
    districtCode: str | None = None
    talukName: str | None = None
    talukCode: str | None = None
    hobliName: str | None = None
    hobliCode: str | None = None
    villageName: str | None = None
    villageCode: str | None = None
    message: str | None = None

    @field_validator("*", mode="before")
    def empty_str_to_none(cls, v):
        if v == "":
            return None
        return v    

class DistrictNameRequest(Schema):
    districtname: str

class DistrictNameResponse(Schema):
    districtCode: str | None = None

class LocationDetailsRequest(Schema):
    coordinates: str
    type: str
    aoi: str | None = None

class LocationDetailsResponse(Schema):
    message: str | None = None
    type: str | None = None
    districtCode: str | None = None
    districtName: str | None = None
    townCode: str | None = None
    townName: str | None = None
    zoneCode: str | None = None
    zoneName: str | None = None
    wardCode: str | None = None
    wardName: str | None = None 
    LGD_WardCode: str | None = None
    hobliCode: str | None = None
    hobliName: str | None = None
    villageCode: str | None = None
    villageName: str | None = None
    LGD_VillageCode: str | None = None
    talukCode: str | None = None
    talukName: str | None = None
    surveynum: str | None = None

    @field_validator("*", mode="before")
    def empty_str_to_none(cls, v):
        if v == "":
            return None
        return v

class HobliCodeRequest(Schema):
    hobliname: str

class HobliCodeResponse(Schema):
    districtName: str | None = None
    districtCode: str | None = None
    talukName: str | None = None
    talukCode: str | None = None
    hobliName: str | None = None
    hobliCode: str | None = None
    message: str 

    @field_validator("*", mode="before")
    def empty_str_to_none(cls, v):
        if v == "":
            return None
        return v


class TalukCodeRequest(Schema):
    talukname: str

class TalukCodeResponse(Schema):
    districtName: str | None = None
    districtCode: str | None = None
    talukName: str | None = None
    talukCode: str | None = None
    message: str 

    @field_validator("*", mode="before")
    def empty_str_to_none(cls, v):
        if v == "":
            return None
        return v

class PinCodeDistanceRequest(Schema):
    pincodes: str

class PinCodeDistanceResponse(Schema):
    keymsg: str 
    distance: str | None = None

    @field_validator("*", mode="before")
    def empty_str_to_none(cls, v):
        if v == "":
            return None
        return v
    
class NearbyHierarchyRequest(Schema):
    coordinates: str
    distance:str
    type:str
    aoi:str 

class NearbyHierarchyResponse(Schema):
    districtName: str 
    districtCode: str 

    @field_validator("*", mode="before")
    def empty_str_to_none(cls, v):
        if v == "":
            return None
        return v
    
class GeometricPolygonRequest(Schema):
    village_id: int
    survey_no: int
    coord_type: str 

class PolygonItem(Schema):
    message: str
    geom: str


class GeometricPolygonResponse(Schema):
    polygons: List[PolygonItem]