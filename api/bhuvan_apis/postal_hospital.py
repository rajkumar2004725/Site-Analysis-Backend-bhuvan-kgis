import requests
import json
import os
from datetime import datetime
import logging
from .config.bhuvan_tokens import get_service_token

class PostalHospitalAPI:
    """
    Client for interacting with Bhuvan Postal and Hospital Proximity API
    Get details of Hospitals and Post Offices near a location with buffer in meters.
    """
    
    def __init__(self):
        self.base_url = 'https://bhuvan-app1.nrsc.gov.in/api/api_proximity/curl_hos_pos_prox.php'
        self.api_token = get_service_token('postal_hospital')
        self.logger = logging.getLogger(__name__)
        
        # Configure logging if not already configured
        if not self.logger.handlers:
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
    
    def get_proximity_data(self, coordinates, theme='all', buffer=3000, parameters=None):
        """
        Get details of Hospitals and Post Offices near a location
        
        Args:
            coordinates (dict): Dictionary with lat and lng keys
            theme (str): Type of facilities ('hospital', 'postal', 'all')
            buffer (int): Buffer distance in meters
            parameters (dict): Additional query parameters
            
        Returns:
            dict: Formatted response with extracted data points
        """
        self.logger.info(f"Fetching {theme} proximity data for coordinates: {coordinates} with buffer: {buffer}m")
        
        if not self.api_token:
            raise ValueError("Postal Hospital API token not configured")
        
        if parameters is None:
            parameters = {}
        
        # Build request parameters
        params = {
            'lat': coordinates['lat'],
            'lon': coordinates['lng'],
            'buffer': buffer,
            'theme': theme,
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
            formatted_response = self._format_response(data, coordinates, theme, buffer, params)
            
            # Save response to file
            self._save_response(formatted_response, coordinates, theme, buffer)
            
            self.logger.info(f"Successfully retrieved {theme} proximity data")
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
    
    def _format_response(self, raw_data, coordinates, theme, buffer, params):
        """Format the API response into a standardized structure"""
        
        formatted_data = {
            'timestamp': datetime.now().isoformat(),
            'coordinates': coordinates,
            'theme': theme,
            'buffer_meters': buffer,
            'parameters_used': params,
            'proximity_data': raw_data,
            'summary': {
                'total_facilities': 0,
                'hospitals': 0,
                'post_offices': 0,
                'facilities_by_type': {}
            }
        }
        
        # Extract summary information if data structure allows
        if isinstance(raw_data, dict):
            if 'features' in raw_data:
                features = raw_data['features']
                formatted_data['summary']['total_facilities'] = len(features)
                
                # Count by facility type
                for feature in features:
                    if 'properties' in feature:
                        facility_type = feature['properties'].get('type', 'unknown')
                        if facility_type in formatted_data['summary']['facilities_by_type']:
                            formatted_data['summary']['facilities_by_type'][facility_type] += 1
                        else:
                            formatted_data['summary']['facilities_by_type'][facility_type] = 1
                        
                        # Count specific types
                        if 'hospital' in facility_type.lower():
                            formatted_data['summary']['hospitals'] += 1
                        elif 'post' in facility_type.lower() or 'postal' in facility_type.lower():
                            formatted_data['summary']['post_offices'] += 1
        
        return formatted_data
    
    def _save_response(self, data, coordinates, theme, buffer):
        """Save the API response to a JSON file"""
        try:
            # Create data directory if it doesn't exist
            os.makedirs('data', exist_ok=True)
            
            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"data/proximity_{theme}_{coordinates['lat']}_{coordinates['lng']}_buffer{buffer}_{timestamp}.json"
            
            # Save to file
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            
            self.logger.info(f"Saved proximity response to {filename}")
            
        except Exception as e:
            self.logger.warning(f"Failed to save response to file: {str(e)}")
    
    def get_hospitals(self, coordinates, buffer=3000, parameters=None):
        """Get hospital proximity data specifically"""
        return self.get_proximity_data(coordinates, theme='hospital', buffer=buffer, parameters=parameters)
    
    def get_post_offices(self, coordinates, buffer=3000, parameters=None):
        """Get post office proximity data specifically"""
        return self.get_proximity_data(coordinates, theme='postal', buffer=buffer, parameters=parameters)
    
    def get_all_facilities(self, coordinates, buffer=3000, parameters=None):
        """Get both hospital and post office proximity data"""
        return self.get_proximity_data(coordinates, theme='all', buffer=buffer, parameters=parameters)
