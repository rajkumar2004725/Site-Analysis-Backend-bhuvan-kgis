import requests
import json
import os
from datetime import datetime
import logging
from .config.bhuvan_tokens import get_service_token

class VillageGeocodingAPI:
    """
    Client for interacting with Bhuvan Village Geocoding API
    Get census data of villages by name for Andhra Pradesh and Karnataka.
    """
    
    def __init__(self):
        self.base_url = 'https://bhuvan-app1.nrsc.gov.in/api/api_proximity/curl_village_geocode.php'
        self.api_token = get_service_token('village_geocoding')
        self.logger = logging.getLogger(__name__)
        
        # Configure logging if not already configured
        if not self.logger.handlers:
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
    
    def get_village_data(self, village_name, parameters=None):
        """
        Get census data for a village by name
        
        Args:
            village_name (str): Name of the village (case insensitive)
            parameters (dict): Additional query parameters
            
        Returns:
            dict: Formatted response with village census data
        """
        self.logger.info(f"Fetching village geocoding data for: {village_name}")
        
        if not self.api_token:
            raise ValueError("Village Geocoding API token not configured")
        
        if parameters is None:
            parameters = {}
        
        # Build request parameters
        params = {
            'village': village_name,
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
            formatted_response = self._format_response(data, village_name, params)
            
            # Save response to file
            self._save_response(formatted_response, village_name)
            
            self.logger.info(f"Successfully retrieved village data for: {village_name}")
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
    
    def _format_response(self, raw_data, village_name, params):
        """Format the API response into a standardized structure"""
        
        formatted_data = {
            'timestamp': datetime.now().isoformat(),
            'village_name': village_name,
            'parameters_used': params,
            'village_data': raw_data,
            'summary': {
                'found': False,
                'state': None,
                'district': None,
                'coordinates': None,
                'population': None,
                'census_year': '2001'
            }
        }
        
        # Extract summary information if data structure allows
        if isinstance(raw_data, dict):
            if 'features' in raw_data and raw_data['features']:
                formatted_data['summary']['found'] = True
                feature = raw_data['features'][0]  # Take first match
                
                if 'properties' in feature:
                    props = feature['properties']
                    formatted_data['summary']['state'] = props.get('state')
                    formatted_data['summary']['district'] = props.get('district')
                    formatted_data['summary']['population'] = props.get('population')
                
                if 'geometry' in feature and 'coordinates' in feature['geometry']:
                    coords = feature['geometry']['coordinates']
                    if coords:
                        formatted_data['summary']['coordinates'] = {
                            'lng': coords[0] if len(coords) > 0 else None,
                            'lat': coords[1] if len(coords) > 1 else None
                        }
            elif isinstance(raw_data, list) and raw_data:
                formatted_data['summary']['found'] = True
                # Handle if response is a list
                village_info = raw_data[0]
                if isinstance(village_info, dict):
                    formatted_data['summary']['state'] = village_info.get('state')
                    formatted_data['summary']['district'] = village_info.get('district')
                    formatted_data['summary']['population'] = village_info.get('population')
                    formatted_data['summary']['coordinates'] = {
                        'lng': village_info.get('longitude'),
                        'lat': village_info.get('latitude')
                    }
        
        return formatted_data
    
    def _save_response(self, data, village_name):
        """Save the API response to a JSON file"""
        try:
            # Create data directory if it doesn't exist
            os.makedirs('data', exist_ok=True)
            
            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            safe_village_name = village_name.replace(' ', '_').replace('/', '_')
            filename = f"data/village_geocode_{safe_village_name}_{timestamp}.json"
            
            # Save to file
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            
            self.logger.info(f"Saved village geocoding response to {filename}")
            
        except Exception as e:
            self.logger.warning(f"Failed to save response to file: {str(e)}")
    
    def search_villages(self, village_names, parameters=None):
        """
        Search for multiple villages
        
        Args:
            village_names (list): List of village names to search
            parameters (dict): Additional query parameters
            
        Returns:
            dict: Results for all villages
        """
        results = {}
        
        for village_name in village_names:
            try:
                results[village_name] = self.get_village_data(village_name, parameters)
            except Exception as e:
                self.logger.error(f"Failed to get data for village {village_name}: {str(e)}")
                results[village_name] = {
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
        
        return results
