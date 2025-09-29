import requests
import json
import os
from datetime import datetime
import logging
from .config.bhuvan_tokens import get_service_token

class VillageReverseGeocodingAPI:
    """
    Client for interacting with Bhuvan Village Reverse Geocoding API
    Get village information at a particular Latitude and Longitude for AP and Karnataka.
    """
    
    def __init__(self):
        self.base_url = 'https://bhuvan-app1.nrsc.gov.in/api/api_proximity/curl_reverse_village.php'
        self.api_token = get_service_token('village_reverse_geocoding')
        self.logger = logging.getLogger(__name__)
        
        # Configure logging if not already configured
        if not self.logger.handlers:
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
    
    def get_village_at_location(self, coordinates, parameters=None):
        """
        Get village information at specific coordinates
        
        Args:
            coordinates (dict): Dictionary with lat and lng keys
            parameters (dict): Additional query parameters
            
        Returns:
            dict: Formatted response with village information
        """
        self.logger.info(f"Fetching village reverse geocoding data for coordinates: {coordinates}")
        
        if not self.api_token:
            raise ValueError("Village Reverse Geocoding API token not configured")
        
        if parameters is None:
            parameters = {}
        
        # Build request parameters
        params = {
            'lat': coordinates['lat'],
            'lon': coordinates['lng'],
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
                timeout=30
            )
            
            response.raise_for_status()
            
            # Parse JSON response
            data = response.json()
            
            # Format and extract relevant data
            formatted_response = self._format_response(data, coordinates, params)
            
            # Save response to file
            self._save_response(formatted_response, coordinates)
            
            self.logger.info(f"Successfully retrieved village data for coordinates: {coordinates}")
            return formatted_response
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API request failed: {str(e)}")
            raise
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON response: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error: {str(e)}")
            raise
    
    def _format_response(self, raw_data, coordinates, params):
        """Format the API response into a standardized structure"""
        
        formatted_data = {
            'timestamp': datetime.now().isoformat(),
            'coordinates': coordinates,
            'parameters_used': params,
            'village_data': raw_data,
            'summary': {
                'village_found': False,
                'village_name': None,
                'state': None,
                'district': None,
                'population': None,
                'census_year': '2001',
                'distance_from_query': None
            }
        }
        
        # Extract summary information if data structure allows
        if isinstance(raw_data, dict):
            if 'features' in raw_data and raw_data['features']:
                formatted_data['summary']['village_found'] = True
                feature = raw_data['features'][0]  # Take closest match
                
                if 'properties' in feature:
                    props = feature['properties']
                    formatted_data['summary']['village_name'] = props.get('village_name') or props.get('name')
                    formatted_data['summary']['state'] = props.get('state')
                    formatted_data['summary']['district'] = props.get('district')
                    formatted_data['summary']['population'] = props.get('population')
                    formatted_data['summary']['distance_from_query'] = props.get('distance')
                
            elif 'village_name' in raw_data or 'name' in raw_data:
                # Handle direct object response
                formatted_data['summary']['village_found'] = True
                formatted_data['summary']['village_name'] = raw_data.get('village_name') or raw_data.get('name')
                formatted_data['summary']['state'] = raw_data.get('state')
                formatted_data['summary']['district'] = raw_data.get('district')
                formatted_data['summary']['population'] = raw_data.get('population')
                formatted_data['summary']['distance_from_query'] = raw_data.get('distance')
        
        elif isinstance(raw_data, list) and raw_data:
            formatted_data['summary']['village_found'] = True
            village_info = raw_data[0]  # Take first result
            if isinstance(village_info, dict):
                formatted_data['summary']['village_name'] = village_info.get('village_name') or village_info.get('name')
                formatted_data['summary']['state'] = village_info.get('state')
                formatted_data['summary']['district'] = village_info.get('district')
                formatted_data['summary']['population'] = village_info.get('population')
                formatted_data['summary']['distance_from_query'] = village_info.get('distance')
        
        return formatted_data
    
    def _save_response(self, data, coordinates):
        """Save the API response to a JSON file"""
        try:
            # Create data directory if it doesn't exist
            os.makedirs('data', exist_ok=True)
            
            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"data/village_reverse_{coordinates['lat']}_{coordinates['lng']}_{timestamp}.json"
            
            # Save to file
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            
            self.logger.info(f"Saved village reverse geocoding response to {filename}")
            
        except Exception as e:
            self.logger.warning(f"Failed to save response to file: {str(e)}")
    
    def get_villages_for_locations(self, coordinates_list, parameters=None):
        """
        Get village information for multiple locations
        
        Args:
            coordinates_list (list): List of coordinate dictionaries
            parameters (dict): Additional query parameters
            
        Returns:
            dict: Results for all locations
        """
        results = {}
        
        for i, coordinates in enumerate(coordinates_list):
            try:
                location_key = f"{coordinates['lat']}_{coordinates['lng']}"
                results[location_key] = self.get_village_at_location(coordinates, parameters)
            except Exception as e:
                location_key = f"{coordinates['lat']}_{coordinates['lng']}"
                self.logger.error(f"Failed to get village data for location {location_key}: {str(e)}")
                results[location_key] = {
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
        
        return results
