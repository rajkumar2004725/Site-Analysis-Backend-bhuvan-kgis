from django.contrib import admin

# Register your models here.

from .models import (
    ApiRequest, ThematicStatisticsInput,LULCAOIStatisticsInput,LULCPolygonStatisticsInput,
    LULCBoundingBoxStatisticsInput,GeoidElevationInput,RoutingInput,PostalHospitalProximityInput,
    VillageGeocodingInput,VillageReverseGeocodingInput)

admin.site.register(ApiRequest)
admin.site.register(ThematicStatisticsInput)
admin.site.register(LULCAOIStatisticsInput)
admin.site.register(LULCPolygonStatisticsInput)
admin.site.register(LULCBoundingBoxStatisticsInput)
admin.site.register(GeoidElevationInput)
admin.site.register(RoutingInput)
admin.site.register(PostalHospitalProximityInput)
admin.site.register(VillageGeocodingInput)
admin.site.register(VillageReverseGeocodingInput)



