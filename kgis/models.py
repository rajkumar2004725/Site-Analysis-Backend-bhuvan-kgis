from django.db import models
from django.core.validators import MinValueValidator


class District(models.Model):
    """Model to store district information"""
    district_code = models.CharField(max_length=50, unique=True)
    district_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'kgis_district'
        ordering = ['district_name']
        indexes = [
            models.Index(fields=['district_code']),
            models.Index(fields=['district_name']),
        ]

    def __str__(self):
        return f"{self.district_name} ({self.district_code})"


class Taluk(models.Model):
    """Model to store taluk information"""
    taluk_code = models.CharField(max_length=50, unique=True)
    taluk_name = models.CharField(max_length=255)
    district = models.ForeignKey(
        District, 
        on_delete=models.CASCADE, 
        related_name='taluks',
        null=True,
        blank=True
    )
    district_code = models.CharField(max_length=50, null=True, blank=True)
    district_name = models.CharField(max_length=255, null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'kgis_taluk'
        ordering = ['taluk_name']
        indexes = [
            models.Index(fields=['taluk_code']),
            models.Index(fields=['district_code']),
        ]

    def __str__(self):
        return f"{self.taluk_name} ({self.taluk_code})"


class Hobli(models.Model):
    """Model to store hobli information"""
    hobli_code = models.CharField(max_length=50, unique=True)
    hobli_name = models.CharField(max_length=255)
    taluk = models.ForeignKey(
        Taluk, 
        on_delete=models.CASCADE, 
        related_name='hoblis',
        null=True,
        blank=True
    )
    taluk_code = models.CharField(max_length=50, null=True, blank=True)
    taluk_name = models.CharField(max_length=255, null=True, blank=True)
    district_code = models.CharField(max_length=50, null=True, blank=True)
    district_name = models.CharField(max_length=255, null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'kgis_hobli'
        ordering = ['hobli_name']
        indexes = [
            models.Index(fields=['hobli_code']),
            models.Index(fields=['taluk_code']),
        ]

    def __str__(self):
        return f"{self.hobli_name} ({self.hobli_code})"


class Village(models.Model):
    """Model to store village information"""
    village_code = models.CharField(max_length=50, unique=True)
    village_name = models.CharField(max_length=255)
    lgd_village_code = models.CharField(max_length=50, null=True, blank=True)
    hobli = models.ForeignKey(
        Hobli, 
        on_delete=models.CASCADE, 
        related_name='villages',
        null=True,
        blank=True
    )
    hobli_code = models.CharField(max_length=50, null=True, blank=True)
    hobli_name = models.CharField(max_length=255, null=True, blank=True)
    taluk_code = models.CharField(max_length=50, null=True, blank=True)
    taluk_name = models.CharField(max_length=255, null=True, blank=True)
    district_code = models.CharField(max_length=50, null=True, blank=True)
    district_name = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'kgis_village'
        ordering = ['village_name']
        indexes = [
            models.Index(fields=['village_code']),
            models.Index(fields=['hobli_code']),
            models.Index(fields=['lgd_village_code']),
        ]

    def __str__(self):
        return f"{self.village_name} ({self.village_code})"


class Town(models.Model):
    """Model to store town information"""
    town_code = models.CharField(max_length=50, unique=True)
    town_name = models.CharField(max_length=255)
    district = models.ForeignKey(
        District, 
        on_delete=models.CASCADE, 
        related_name='towns',
        null=True,
        blank=True
    )
    district_code = models.CharField(max_length=50, null=True, blank=True)
    district_name = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'kgis_town'
        ordering = ['town_name']
        indexes = [
            models.Index(fields=['town_code']),
            models.Index(fields=['district_code']),
        ]

    def __str__(self):
        return f"{self.town_name} ({self.town_code})"


class Zone(models.Model):
    """Model to store zone information"""
    zone_code = models.CharField(max_length=50, unique=True)
    zone_name = models.CharField(max_length=255)
    town = models.ForeignKey(
        Town, 
        on_delete=models.CASCADE, 
        related_name='zones',
        null=True,
        blank=True
    )
    town_code = models.CharField(max_length=50, null=True, blank=True)
    town_name = models.CharField(max_length=255, null=True, blank=True)
    district_code = models.CharField(max_length=50, null=True, blank=True)
    district_name = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'kgis_zone'
        ordering = ['zone_name']
        indexes = [
            models.Index(fields=['zone_code']),
            models.Index(fields=['town_code']),
        ]

    def __str__(self):
        return f"{self.zone_name} ({self.zone_code})"


class Ward(models.Model):
    """Model to store ward information"""
    ward_code = models.CharField(max_length=50, unique=True)
    ward_name = models.CharField(max_length=255)
    lgd_ward_code = models.CharField(max_length=50, null=True, blank=True)
    zone = models.ForeignKey(
        Zone, 
        on_delete=models.CASCADE, 
        related_name='wards',
        null=True,
        blank=True
    )
    zone_code = models.CharField(max_length=50, null=True, blank=True)
    zone_name = models.CharField(max_length=255, null=True, blank=True)
    town_code = models.CharField(max_length=50, null=True, blank=True)
    town_name = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'kgis_ward'
        ordering = ['ward_name']
        indexes = [
            models.Index(fields=['ward_code']),
            models.Index(fields=['zone_code']),
            models.Index(fields=['lgd_ward_code']),
        ]

    def __str__(self):
        return f"{self.ward_name} ({self.ward_code})"


class LocationDetail(models.Model):
    """Model to store location details retrieved from coordinates"""
    TYPE_CHOICES = [
        ('urban', 'Urban'),
        ('rural', 'Rural'),
        ('both', 'Both'),
    ]

    coordinates = models.CharField(max_length=255)
    location_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    aoi = models.CharField(max_length=255, null=True, blank=True)
    
    # District info
    district_code = models.CharField(max_length=50, null=True, blank=True)
    district_name = models.CharField(max_length=255, null=True, blank=True)
    
    # Urban area info
    town_code = models.CharField(max_length=50, null=True, blank=True)
    town_name = models.CharField(max_length=255, null=True, blank=True)
    zone_code = models.CharField(max_length=50, null=True, blank=True)
    zone_name = models.CharField(max_length=255, null=True, blank=True)
    ward_code = models.CharField(max_length=50, null=True, blank=True)
    ward_name = models.CharField(max_length=255, null=True, blank=True)
    lgd_ward_code = models.CharField(max_length=50, null=True, blank=True)
    
    # Rural area info
    hobli_code = models.CharField(max_length=50, null=True, blank=True)
    hobli_name = models.CharField(max_length=255, null=True, blank=True)
    village_code = models.CharField(max_length=50, null=True, blank=True)
    village_name = models.CharField(max_length=255, null=True, blank=True)
    lgd_village_code = models.CharField(max_length=50, null=True, blank=True)
    taluk_code = models.CharField(max_length=50, null=True, blank=True)
    taluk_name = models.CharField(max_length=255, null=True, blank=True)
    
    survey_num = models.CharField(max_length=100, null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'kgis_location_detail'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['coordinates']),
            models.Index(fields=['district_code']),
            models.Index(fields=['village_code']),
            models.Index(fields=['ward_code']),
        ]

    def __str__(self):
        return f"Location at {self.coordinates}"


class PincodeDistance(models.Model):
    """Model to store distance between pincodes"""
    pincodes = models.CharField(max_length=255)
    distance = models.CharField(max_length=50, null=True, blank=True, help_text="Distance as string")
    key_message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'kgis_pincode_distance'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['pincodes']),
        ]

    def __str__(self):
        return f"Distance for {self.pincodes}"


class SurveyPolygon(models.Model):
    """Model to store geometric polygons for survey numbers"""
    COORD_TYPE_CHOICES = [
        ('latlong', 'Latitude/Longitude'),
        ('utm', 'UTM'),
        ('other', 'Other'),
    ]

    village_id = models.IntegerField(validators=[MinValueValidator(1)])
    survey_no = models.IntegerField(validators=[MinValueValidator(1)])
    coord_type = models.CharField(max_length=20, choices=COORD_TYPE_CHOICES)
    # Store the entire polygon item (message + geom)
    message = models.TextField()
    geometry = models.TextField(help_text="Geometric polygon data (geom field)")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'kgis_survey_polygon'
        ordering = ['village_id', 'survey_no']
        indexes = [
            models.Index(fields=['village_id', 'survey_no']),
            models.Index(fields=['village_id']),
        ]

    def __str__(self):
        return f"Survey {self.survey_no} in Village {self.village_id}"


class NearbyHierarchy(models.Model):
    """Model to store nearby administrative hierarchy results"""
    coordinates = models.CharField(max_length=255)
    distance = models.CharField(max_length=50)
    location_type = models.CharField(max_length=20)
    aoi = models.CharField(max_length=255)
    
    # Results - REQUIRED fields (matching schema)
    district_code = models.CharField(max_length=50)
    district_name = models.CharField(max_length=255)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'kgis_nearby_hierarchy'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['coordinates']),
            models.Index(fields=['district_code']),
        ]

    def __str__(self):
        return f"Nearby {self.district_name} at {self.coordinates}"


class APILog(models.Model):
    """Model to log API requests and responses"""
    endpoint = models.CharField(max_length=255)
    request_payload = models.JSONField()
    response_data = models.JSONField(null=True, blank=True)
    status_code = models.IntegerField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'kgis_api_log'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['endpoint']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.endpoint} - {self.created_at}"