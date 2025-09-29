import requests
import json
import os
import math
from datetime import datetime
import logging
from .config.bhuvan_tokens import get_service_token

class RoutingAPI:
    """
    Client for interacting with Bhuvan Routing API
    Get shortest path between two points using Bhuvan's road network data.
    """
    
    def __init__(self):
        self.base_url = 'https://bhuvan-app1.nrsc.gov.in/api/routing/curl_routing_state.php'
        self.api_token = get_service_token('routing')
        self.logger = logging.getLogger(__name__)
        
        # Configure logging if not already configured
        if not self.logger.handlers:
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
    
    def get_route(self, start_coordinates, end_coordinates, parameters=None):
        """
        Get shortest path route between two coordinates
        
        Args:
            start_coordinates (dict): Dictionary with lat and lng keys for start point
            end_coordinates (dict): Dictionary with lat and lng keys for end point
            parameters (dict): Additional query parameters
            
        Returns:
            dict: Formatted response with route information
        """
        self.logger.info(f"Fetching route from {start_coordinates} to {end_coordinates}")
        
        if not self.api_token:
            self.logger.warning("Routing API token not configured, creating error response")
            return self._create_error_response(start_coordinates, end_coordinates, "Routing API token not configured")
        
        # Check if coordinates are likely in the same state/region
        if not self._are_coordinates_in_same_region(start_coordinates, end_coordinates):
            error_msg = "Coordinates appear to be in different states. Bhuvan routing API requires coordinates within the same state."
            self.logger.warning(error_msg)
            return self._create_error_response(start_coordinates, end_coordinates, error_msg)
        
        if parameters is None:
            parameters = {}
        
        # Build request parameters
        params = {
            'lat1': start_coordinates['lat'],
            'lon1': start_coordinates['lng'],
            'lat2': end_coordinates['lat'],
            'lon2': end_coordinates['lng'],
            'token': self.api_token
        }
        
        # Add any additional parameters
        params.update(parameters)
        
        try:
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            response = requests.get(
                self.base_url,
                params=params,
                headers=headers,
                timeout=60  # Longer timeout for routing calculations
            )
            
            response.raise_for_status()
            
            # Check if response is JSON or text
            content_type = response.headers.get('content-type', '').lower()
            response_text = response.text.strip()
            
            if 'application/json' in content_type or response_text.startswith('{'):
                # Parse JSON response (should be GeoJSON)
                data = response.json()
                
                # Format and extract relevant data
                formatted_response = self._format_response(data, start_coordinates, end_coordinates, params)
                
                # Save response to file
                self._save_response(formatted_response, start_coordinates, end_coordinates, parameters)
                
                self.logger.info("Successfully retrieved routing data")
                return formatted_response
            else:
                # Handle text error responses
                self.logger.error(f"API returned text response: {response_text}")
                return self._create_error_response(start_coordinates, end_coordinates, f"API error: {response_text}")
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON response: {str(e)}")
            self.logger.error(f"Response content: {response.text[:200]}...")
            return self._create_error_response(start_coordinates, end_coordinates, f"Failed to parse JSON response: {str(e)}")
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API request failed: {str(e)}")
            return self._create_error_response(start_coordinates, end_coordinates, f"API request failed: {str(e)}")
        except Exception as e:
            import traceback
            self.logger.error(f"Unexpected error: {str(e)}")
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return self._create_error_response(start_coordinates, end_coordinates, f"Unexpected error: {str(e)}")
    
    def _create_error_response(self, start_coords, end_coords, error_message):
        """Create error response when API fails"""
        
        return {
            'timestamp': datetime.now().isoformat(),
            'origin': start_coords,
            'destination': end_coords,
            'error': error_message,
            'route_data': None,
            'summary': {
                'distance_km': 0,
                'estimated_duration_minutes': 0,
                'route_found': False,
                'total_segments': 0,
                'start_point': None,
                'end_point': None,
                'error': error_message
            }
        }
    
    def _format_response(self, raw_data, start_coords, end_coords, params):
        """Format the API response into a standardized structure"""
        
        formatted_data = {
            'timestamp': datetime.now().isoformat(),
            'origin': start_coords,
            'destination': end_coords,
            'parameters_used': params,
            'route_data': raw_data,
            'summary': {
                'distance_km': 0,
                'estimated_duration_minutes': 0,
                'route_found': False,
                'total_segments': 0,
                'start_point': None,
                'end_point': None
            }
        }
        
        # Extract route information from GeoJSON response
        if isinstance(raw_data, dict):
            if 'features' in raw_data and raw_data['features']:
                formatted_data['summary']['route_found'] = True
                
                total_distance = 0
                segments = 0
                
                for feature in raw_data['features']:
                    segments += 1
                    
                    if 'properties' in feature:
                        props = feature['properties']
                        # Extract distance if available
                        distance = props.get('distance', 0) or props.get('length', 0)
                        if distance:
                            total_distance += float(distance)
                    
                    # Extract geometry information
                    if 'geometry' in feature and 'coordinates' in feature['geometry']:
                        coords = feature['geometry']['coordinates']
                        if coords and isinstance(coords, list) and len(coords) > 0:
                            # Handle different coordinate structures
                            # For MultiLineString, coordinates is array of LineString coordinate arrays
                            # For LineString, coordinates is array of [lng, lat] pairs
                            
                            # Get first coordinate pair
                            first_coord = None
                            last_coord = None
                            
                            if feature['geometry']['type'] == 'MultiLineString':
                                # MultiLineString: coords is array of LineString coordinate arrays
                                if len(coords) > 0 and len(coords[0]) > 0:
                                    first_coord = coords[0][0] if len(coords[0][0]) >= 2 else None
                                    last_coord = coords[-1][-1] if len(coords[-1]) > 0 and len(coords[-1][-1]) >= 2 else None
                            else:
                                # LineString: coords is array of [lng, lat] pairs
                                if len(coords) > 0 and isinstance(coords[0], list) and len(coords[0]) >= 2:
                                    first_coord = coords[0]
                                    last_coord = coords[-1] if isinstance(coords[-1], list) and len(coords[-1]) >= 2 else None
                            
                            if first_coord and not formatted_data['summary']['start_point']:
                                formatted_data['summary']['start_point'] = {
                                    'lng': first_coord[0],
                                    'lat': first_coord[1]
                                }
                            
                            if last_coord:
                                formatted_data['summary']['end_point'] = {
                                    'lng': last_coord[0],
                                    'lat': last_coord[1]
                                }
                
                formatted_data['summary']['distance_km'] = total_distance / 1000 if total_distance > 1000 else total_distance
                formatted_data['summary']['total_segments'] = segments
                
                # Estimate duration (rough calculation: average 40 km/h)
                if total_distance > 0:
                    formatted_data['summary']['estimated_duration_minutes'] = (total_distance / 1000) * (60 / 40)
            
            elif 'type' in raw_data and raw_data['type'] == 'LineString':
                # Handle direct LineString response
                formatted_data['summary']['route_found'] = True
                coords = raw_data.get('coordinates', [])
                if coords:
                    formatted_data['summary']['start_point'] = {
                        'lng': coords[0][0] if len(coords[0]) > 0 else None,
                        'lat': coords[0][1] if len(coords[0]) > 1 else None
                    }
                    formatted_data['summary']['end_point'] = {
                        'lng': coords[-1][0] if len(coords[-1]) > 0 else None,
                        'lat': coords[-1][1] if len(coords[-1]) > 1 else None
                    }
                    
                    # Calculate approximate distance
                    distance = self._calculate_line_distance(coords)
                    formatted_data['summary']['distance_km'] = distance
                    formatted_data['summary']['estimated_duration_minutes'] = distance * (60 / 40)
        
        return formatted_data
    
    def _calculate_line_distance(self, coordinates):
        """Calculate total distance of a line from coordinate array"""
        total_distance = 0
        
        for i in range(1, len(coordinates)):
            lat1, lng1 = coordinates[i-1][1], coordinates[i-1][0]
            lat2, lng2 = coordinates[i][1], coordinates[i][0]
            
            # Calculate distance between consecutive points using Haversine formula
            distance = self._haversine_distance(lat1, lng1, lat2, lng2)
            total_distance += distance
        
        return total_distance
    
    def _haversine_distance(self, lat1, lng1, lat2, lng2):
        """Calculate the great circle distance between two points in kilometers"""
        # Convert decimal degrees to radians
        lat1, lng1, lat2, lng2 = map(math.radians, [lat1, lng1, lat2, lng2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlng = lng2 - lng1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
        c = 2 * math.asin(math.sqrt(a))
        r = 6371  # Radius of earth in kilometers
        
        return c * r
    
    def _are_coordinates_in_same_region(self, coord1, coord2):
        """
        Check if two coordinates are likely in the same state/region
        This is a rough approximation based on distance and known state boundaries
        """
        lat1, lng1 = coord1['lat'], coord1['lng']
        lat2, lng2 = coord2['lat'], coord2['lng']
        
        # Calculate distance between points
        distance = self._haversine_distance(lat1, lng1, lat2, lng2)
        
        # If distance is more than 1000km, likely different states
        if distance > 1000:
            return False
        
        # Check if both coordinates are within known state boundaries
        # This is a simplified check - in production you'd use proper GIS data
        
        # Karnataka boundaries (approximate)
        if (11.5 <= lat1 <= 18.5 and 74 <= lng1 <= 78.5 and
            11.5 <= lat2 <= 18.5 and 74 <= lng2 <= 78.5):
            return True
            
        # Andhra Pradesh + Telangana boundaries (approximate)
        if (12.5 <= lat1 <= 19.5 and 77 <= lng1 <= 85 and
            12.5 <= lat2 <= 19.5 and 77 <= lng2 <= 85):
            return True
            
        # Tamil Nadu boundaries (approximate)
        if (8 <= lat1 <= 13.5 and 76.5 <= lng1 <= 80.5 and
            8 <= lat2 <= 13.5 and 76.5 <= lng2 <= 80.5):
            return True
            
        # Kerala boundaries (approximate)
        if (8 <= lat1 <= 12.5 and 74.5 <= lng1 <= 77.5 and
            8 <= lat2 <= 12.5 and 74.5 <= lng2 <= 77.5):
            return True
            
        # If not within any known same-state boundaries, check distance
        # If distance is less than 500km, assume same state
        return distance < 500
    
    def _save_response(self, data, start_coords, end_coords, parameters):
        """Save the API response to a JSON file"""
        try:
            # Create data directory if it doesn't exist
            os.makedirs('data', exist_ok=True)
            
            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            param_suffix = ""
            if parameters:
                param_suffix = "_" + "_".join([f"{k}_{v}" for k, v in parameters.items() if k != 'token'])
            
            filename = f"data/route_{start_coords['lat']}_{start_coords['lng']}_to_{end_coords['lat']}_{end_coords['lng']}{param_suffix}_{timestamp}.json"
            
            # Save to file
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            
            self.logger.info(f"Saved routing response to {filename}")
            
        except Exception as e:
            self.logger.warning(f"Failed to save response to file: {str(e)}")
