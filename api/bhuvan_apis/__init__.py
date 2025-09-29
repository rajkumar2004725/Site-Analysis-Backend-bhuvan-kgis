"""
API module for Bhuvan services integration
"""

from .thematic_statistics import ThematicStatisticsAPI
from .geoid import GeoidAPI
from .routing import RoutingAPI
from .postal_hospital import PostalHospitalAPI
from .village_geocoding import VillageGeocodingAPI
from .village_reverse_geocoding import VillageReverseGeocodingAPI
from .lulc_aoi_wise import LULCAOIWiseAPI

__all__ = [
    'ThematicStatisticsAPI',
    'GeoidAPI', 
    'RoutingAPI',
    'PostalHospitalAPI',
    'VillageGeocodingAPI',
    'VillageReverseGeocodingAPI',
    'LULCAOIWiseAPI'
]
