from django.shortcuts import render
from ninja import NinjaAPI, Router
from api.schemas import (
    Coordinates, Details, GeometryWKT, PolygonCoordinates, BoundingBox,
    RouteCoordinates, Proximity, VillageName, VillageCoordinates, Geoid, ApiResponse
)
from bhuvan_apis import (
    ThematicStatisticsAPI, LULCAOIWiseAPI, GeoidAPI, RoutingAPI,
    PostalHospitalAPI, VillageGeocodingAPI, VillageReverseGeocodingAPI
)
from api.models import ApiRequest, ThematicStatisticsInput, LULCAOIStatisticsInput, LULCPolygonStatisticsInput, LULCBoundingBoxStatisticsInput, GeoidElevationInput, RoutingInput, PostalHospitalProximityInput, VillageGeocodingInput, VillageReverseGeocodingInput

api = NinjaAPI(title="Bhuvan APIs", version="1.0.0")

# Initialize API clients
thematic_api = ThematicStatisticsAPI()
lulc_aoi_api = LULCAOIWiseAPI()
geoid_api = GeoidAPI()
routing_api = RoutingAPI()
postal_hospital_api = PostalHospitalAPI()
village_geocode_api = VillageGeocodingAPI()
village_reverse_api = VillageReverseGeocodingAPI()

@api.post("/thematic_statistics", response=ApiResponse)
def get_thematic_statistics(request, coordinates: Coordinates, details: Details):
    api_request = ApiRequest.objects.create(endpoint="/thematic_statistics")
    ThematicStatisticsInput.objects.create(
        api_request=api_request,
        lat=coordinates.lat,
        lng=coordinates.lng,
        distcode=details.distcode,
        year=details.year
    )
    try:
        result = thematic_api.get_statistics(coordinates.dict(), details.dict())
        api_request.status = 'success'
        api_request.response_data = {"data": result}
    except Exception as e:
        api_request.status = 'failed'
        api_request.error_message = str(e)
    api_request.save()
    return ApiResponse(data=result) if api_request.status == 'success' else ApiResponse(error=str(e))

@api.post("/lulc_aoi_statistics", response=ApiResponse)
def get_lulc_aoi_statistics(request, body: GeometryWKT):
    api_request = ApiRequest.objects.create(endpoint="/lulc_aoi_statistics")
    LULCAOIStatisticsInput.objects.create(
        api_request=api_request,
        geometry_wkt=body.geometry_wkt
    )
    try:
        result = lulc_aoi_api.get_aoi_statistics(body.geometry_wkt)
        api_request.status = 'success'
        api_request.response_data = {"data": result}
    except Exception as e:
        api_request.status = 'failed'
        api_request.error_message = str(e)
    api_request.save()
    return ApiResponse(data=result) if api_request.status == 'success' else ApiResponse(error=str(e))

@api.post("/lulc_polygon_statistics", response=ApiResponse)
def get_lulc_polygon_statistics(request, body: PolygonCoordinates):
    api_request = ApiRequest.objects.create(endpoint="/lulc_polygon_statistics")
    LULCPolygonStatisticsInput.objects.create(
        api_request=api_request,
        coordinates_list=body.coordinates_list
    )
    try:
        result = lulc_aoi_api.get_polygon_statistics(body.coordinates_list)
        api_request.status = 'success'
        api_request.response_data = {"data": result}
    except Exception as e:
        api_request.status = 'failed'
        api_request.error_message = str(e)
    api_request.save()
    return ApiResponse(data=result) if api_request.status == 'success' else ApiResponse(error=str(e))

@api.post("/lulc_bounding_box_statistics", response=ApiResponse)
def get_lulc_bounding_box_statistics(request, body: BoundingBox):
    api_request = ApiRequest.objects.create(endpoint="/lulc_bounding_box_statistics")
    LULCBoundingBoxStatisticsInput.objects.create(
        api_request=api_request,
        min_lng=body.min_lng,
        min_lat=body.min_lat,
        max_lng=body.max_lng,
        max_lat=body.max_lat
    )
    try:
        result = lulc_aoi_api.get_bounding_box_statistics(
            body.min_lng, body.min_lat, body.max_lng, body.max_lat
        )
        api_request.status = 'success'
        api_request.response_data = {"data": result}
    except Exception as e:
        api_request.status = 'failed'
        api_request.error_message = str(e)
    api_request.save()
    return ApiResponse(data=result) if api_request.status == 'success' else ApiResponse(error=str(e))

@api.post("/geoid_elevation", response=ApiResponse)
def get_geoid_elevation(request, body: Geoid):
    api_request = ApiRequest.objects.create(endpoint="/geoid_elevation")
    GeoidElevationInput.objects.create(
        api_request=api_request,
        area_id=body.area_id,
        datum=body.datum,
        se=body.se
    )
    try:
        result = geoid_api.get_elevation_data(body.area_id, datum=body.datum, se=body.se)
        api_request.status = 'success'
        api_request.response_data = {"data": result}
    except Exception as e:
        api_request.status = 'failed'
        api_request.error_message = str(e)
    api_request.save()
    return ApiResponse(data=result) if api_request.status == 'success' else ApiResponse(error=str(e))

@api.post("/routing", response=ApiResponse)
def get_routing(request, body: RouteCoordinates):
    api_request = ApiRequest.objects.create(endpoint="/routing")
    RoutingInput.objects.create(
        api_request=api_request,
        start_lat=body.start.lat,
        start_lng=body.start.lng,
        end_lat=body.end.lat,
        end_lng=body.end.lng
    )
    try:
        result = routing_api.get_route(body.start.dict(), body.end.dict())
        api_request.status = 'success'
        api_request.response_data = {"data": result}
    except Exception as e:
        api_request.status = 'failed'
        api_request.error_message = str(e)
    api_request.save()
    return ApiResponse(data=result) if api_request.status == 'success' else ApiResponse(error=str(e))

@api.post("/postal_hospital_proximity", response=ApiResponse)
def get_postal_hospital_proximity(request, body: Proximity):
    api_request = ApiRequest.objects.create(endpoint="/postal_hospital_proximity")
    PostalHospitalProximityInput.objects.create(
        api_request=api_request,
        lat=body.coordinates.lat,
        lng=body.coordinates.lng,
        theme=body.theme,
        buffer=body.buffer
    )
    try:
        result = postal_hospital_api.get_proximity_data(
            body.coordinates.dict(), theme=body.theme, buffer=body.buffer
        )
        api_request.status = 'success'
        api_request.response_data = {"data": result}
    except Exception as e:
        api_request.status = 'failed'
        api_request.error_message = str(e)
    api_request.save()
    return ApiResponse(data=result) if api_request.status == 'success' else ApiResponse(error=str(e))

@api.post("/village_geocoding", response=ApiResponse)
def get_village_geocoding(request, body: VillageName):
    api_request = ApiRequest.objects.create(endpoint="/village_geocoding")
    VillageGeocodingInput.objects.create(
        api_request=api_request,
        village_name=body.village_name
    )
    try:
        result = village_geocode_api.get_village_data(body.village_name)
        api_request.status = 'success'
        api_request.response_data = {"data": result}
    except Exception as e:
        api_request.status = 'failed'
        api_request.error_message = str(e)
    api_request.save()
    return ApiResponse(data=result) if api_request.status == 'success' else ApiResponse(error=str(e))

@api.post("/village_reverse_geocoding", response=ApiResponse)
def get_village_reverse_geocoding(request, body: VillageCoordinates):
    api_request = ApiRequest.objects.create(endpoint="/village_reverse_geocoding")
    VillageReverseGeocodingInput.objects.create(
        api_request=api_request,
        lat=body.coordinates.lat,
        lng=body.coordinates.lng
    )
    try:
        result = village_reverse_api.get_village_at_location(body.coordinates.dict())
        api_request.status = 'success'
        api_request.response_data = {"data": result}
    except Exception as e:
        api_request.status = 'failed'
        api_request.error_message = str(e)
    api_request.save()
    return ApiResponse(data=result) if api_request.status == 'success' else ApiResponse(error=str(e))