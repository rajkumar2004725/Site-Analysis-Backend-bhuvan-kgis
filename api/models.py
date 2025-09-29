from django.db import models
import json

# Enable PostGIS fields if using geospatial extensions (optional)
# from django.contrib.gis.db import models

class ApiRequest(models.Model):
    endpoint = models.CharField(max_length=50, null=False)
    request_timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='pending')
    response_data = models.JSONField(null=True, blank=True)  # Stores ApiResponse data or error
    error_message = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.endpoint} - {self.request_timestamp}"

    class Meta:
        indexes = [
            models.Index(fields=['endpoint', 'request_timestamp'], name='idx_api_request_endpoint_time'),
        ]


class ThematicStatisticsInput(models.Model):
    api_request = models.ForeignKey(ApiRequest, on_delete=models.CASCADE)
    lat = models.FloatField(null=False)
    lng = models.FloatField(null=False)
    distcode = models.CharField(max_length=10, null=False)
    year = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return f"TSI - {self.lat}, {self.lng} - {self.distcode}"

    class Meta:
        indexes = [
            models.Index(fields=['lat', 'lng'], name='idx_thematic_stats_coords'),
        ]


class LULCAOIStatisticsInput(models.Model):
    api_request = models.ForeignKey(ApiRequest, on_delete=models.CASCADE)
    geometry_wkt = models.TextField(null=False)

    def __str__(self):
        return f"LASI - {self.geometry_wkt[:50]}..."


class LULCPolygonStatisticsInput(models.Model):
    api_request = models.ForeignKey(ApiRequest, on_delete=models.CASCADE)
    coordinates_list = models.JSONField(null=False)  # Stores list of [lng, lat]

    def __str__(self):
        return f"LPSI - {json.dumps(self.coordinates_list)[:50]}..."


class LULCBoundingBoxStatisticsInput(models.Model):
    api_request = models.ForeignKey(ApiRequest, on_delete=models.CASCADE)
    min_lng = models.FloatField(null=False)
    min_lat = models.FloatField(null=False)
    max_lng = models.FloatField(null=False)
    max_lat = models.FloatField(null=False)

    def __str__(self):
        return f"LBSI - {self.min_lat},{self.min_lng} to {self.max_lat},{self.max_lng}"

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(min_lat__lte=models.F('max_lat')) &
                      models.Q(min_lng__lte=models.F('max_lng')) &
                      models.Q(min_lat__gte=-90) & models.Q(max_lat__lte=90) &
                      models.Q(min_lng__gte=-180) & models.Q(max_lng__lte=180),
                name='chk_bounding_box'
            ),
        ]


class GeoidElevationInput(models.Model):
    api_request = models.ForeignKey(ApiRequest, on_delete=models.CASCADE)
    area_id = models.CharField(max_length=50, null=False)
    datum = models.CharField(max_length=20, default='geoid')
    se = models.CharField(max_length=10, default='CDEM')

    def __str__(self):
        return f"GEI - {self.area_id}"


class RoutingInput(models.Model):
    api_request = models.ForeignKey(ApiRequest, on_delete=models.CASCADE)
    start_lat = models.FloatField(null=False)
    start_lng = models.FloatField(null=False)
    end_lat = models.FloatField(null=False)
    end_lng = models.FloatField(null=False)

    def __str__(self):
        return f"RI - {self.start_lat},{self.start_lng} to {self.end_lat},{self.end_lng}"

    class Meta:
        indexes = [
            models.Index(fields=['start_lat', 'start_lng', 'end_lat', 'end_lng'], name='idx_routing_coords'),
        ]


class PostalHospitalProximityInput(models.Model):
    api_request = models.ForeignKey(ApiRequest, on_delete=models.CASCADE)
    lat = models.FloatField(null=False)
    lng = models.FloatField(null=False)
    theme = models.CharField(max_length=20, default='all')
    buffer = models.IntegerField(default=3000)

    def __str__(self):
        return f"PHPI - {self.lat},{self.lng} - {self.theme}"

    class Meta:
        indexes = [
            models.Index(fields=['lat', 'lng'], name='idx_proximity_coords'),
        ]


class VillageGeocodingInput(models.Model):
    api_request = models.ForeignKey(ApiRequest, on_delete=models.CASCADE)
    village_name = models.CharField(max_length=100, null=False)

    def __str__(self):
        return f"VGI - {self.village_name}"


class VillageReverseGeocodingInput(models.Model):
    api_request = models.ForeignKey(ApiRequest, on_delete=models.CASCADE)
    lat = models.FloatField(null=False)
    lng = models.FloatField(null=False)

    def __str__(self):
        return f"VRGI - {self.lat},{self.lng}"

    class Meta:
        indexes = [
            models.Index(fields=['lat', 'lng'], name='idx_reverse_geocoding_coords'),
        ]