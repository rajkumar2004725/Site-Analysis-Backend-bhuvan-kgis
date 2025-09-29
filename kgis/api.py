from ninja import Router
from ninja import NinjaAPI
from .schemas import AdminHierarchyRequest, AdminHierarchyResponse, DistrictNameRequest, DistrictNameResponse ,LocationDetailsRequest, LocationDetailsResponse,HobliCodeRequest,HobliCodeResponse,TalukCodeRequest,TalukCodeResponse, PinCodeDistanceResponse ,PinCodeDistanceRequest,NearbyHierarchyRequest,NearbyHierarchyResponse,GeometricPolygonRequest,GeometricPolygonResponse
from .services import get_admin_hierarchy ,get_district_name ,get_location_details,get_hobli_code ,get_taluk_code,get_distance_btw_pin_codes,get_nearby_admin_hierarchy,get_geometric_polygon

api2=NinjaAPI(title="kgis APIs", version="2.0.0")


@api2.get("/test")
def hello(request):
    return{"message":"kgis api endpoint  is working"}

@api2.post("/admin-hierarchy",response=AdminHierarchyResponse)
def admin_hierarchy(request,payload:AdminHierarchyRequest):
    data = get_admin_hierarchy(payload)
    return data

@api2.post("/district-name",response=DistrictNameResponse,exclude_none=True)
def district_name(request,payload:DistrictNameRequest):
    data = get_district_name(payload)
    if data:
        if data.get("districtCode")== "":
          data["districtCode"] = data["message"]
    return data

@api2.post("/location-details",response=LocationDetailsResponse , exclude_none=True)
def location_details(request,payload:LocationDetailsRequest):
    data = get_location_details(payload)
    return data

@api2.post("/hobli-code",response=HobliCodeResponse,exclude_none=True)
def hobli_code(request,payload:HobliCodeRequest):
    data = get_hobli_code(payload)
    return data

@api2.post("/taluk-code",response=TalukCodeResponse,exclude_none=True)
def taluk_code(request,payload:TalukCodeRequest):
    data = get_taluk_code(payload)
    return data

@api2.post("/distance-btw-pincodes",response=PinCodeDistanceResponse,exclude_none=True)
def distance_btw_pincodes(request,payload:PinCodeDistanceRequest):
    data = get_distance_btw_pin_codes(payload)
    return data

@api2.post("/nearby-hierarchy",response=NearbyHierarchyResponse,exclude_none=True)
def nearby_admin_hierarchy(request,payload:NearbyHierarchyRequest):
    data = get_nearby_admin_hierarchy(payload)
    return data

@api2.post("/geo-polygon-area", response=GeometricPolygonResponse, exclude_none=True)
def geo_polygon_area(request, payload: GeometricPolygonRequest):
    data = get_geometric_polygon(payload)
    return data


