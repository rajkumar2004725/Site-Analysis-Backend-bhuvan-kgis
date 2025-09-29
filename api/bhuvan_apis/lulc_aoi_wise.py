import requests
import json
import os
from datetime import datetime
import logging
from urllib.parse import quote
from .config.bhuvan_tokens import get_service_token

class LULCAOIWiseAPI:
    """
    Client for interacting with Bhuvan LULC Area of Interest Wise API
    Calculate LULC stats for specific areas using polygon geometry.
    """
    
    def __init__(self):
        self.base_url = 'https://bhuvan-app1.nrsc.gov.in/api/lulc/curl_aoi.php'
        self.api_token = get_service_token('lulc_aoi_wise')
        self.logger = logging.getLogger(__name__)
        
        # Configure logging if not already configured
        if not self.logger.handlers:
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
    
    def get_aoi_statistics(self, geometry_wkt, parameters=None):
        """
        Get LULC statistics for an Area of Interest
        
        Args:
            geometry_wkt (str): Polygon geometry in WKT format
            parameters (dict): Additional query parameters
            
        Returns:
            dict: Formatted response with LULC statistics for the AOI
        """
        self.logger.info(f"Fetching LULC AOI statistics for geometry: {geometry_wkt[:100]}...")
        
        if not self.api_token:
            raise ValueError("LULC AOI Wise API token not configured")
        
        if parameters is None:
            parameters = {}
        
        # Build request parameters
        params = {
            'geom': geometry_wkt,
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
                timeout=60  # Longer timeout for AOI processing
            )
            
            response.raise_for_status()
            
            # Parse JSON response
            data = response.json()
            
            # Format and extract relevant data
            formatted_response = self._format_response(data, geometry_wkt, params)
            
            # Save response to file
            self._save_response(formatted_response, geometry_wkt)
            
            self.logger.info("Successfully retrieved LULC AOI statistics")
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
    
    def _format_response(self, raw_data, geometry_wkt, params):
        """Format the API response into a standardized structure"""
        
        formatted_data = {
            'timestamp': datetime.now().isoformat(),
            'geometry_wkt': geometry_wkt,
            'parameters_used': params,
            'aoi_data': raw_data,
            'summary': {
                'total_area': 0,
                'lulc_classes': {},
                'states_covered': [],
                'dominant_lulc_class': None
            }
        }
        
        # Extract summary information
        if isinstance(raw_data, dict):
            # Calculate total area and extract LULC classes
            total_area = 0
            lulc_classes = {}
            
            # Look for area data in various possible structures
            if 'features' in raw_data:
                for feature in raw_data['features']:
                    if 'properties' in feature:
                        props = feature['properties']
                        # Extract area information
                        area = props.get('area', 0)
                        lulc_code = props.get('lulc_code') or props.get('class_code')
                        lulc_name = props.get('lulc_name') or props.get('class_name')
                        
                        if lulc_code and area:
                            lulc_classes[lulc_code] = {
                                'name': lulc_name,
                                'area': area,
                                'code': lulc_code
                            }
                            total_area += area
                        
                        # Extract state information
                        state = props.get('state')
                        if state and state not in formatted_data['summary']['states_covered']:
                            formatted_data['summary']['states_covered'].append(state)
            
            elif 'lulc_statistics' in raw_data:
                stats = raw_data['lulc_statistics']
                if isinstance(stats, list):
                    for stat in stats:
                        area = stat.get('area', 0)
                        lulc_code = stat.get('code')
                        lulc_name = stat.get('name')
                        
                        if lulc_code:
                            lulc_classes[lulc_code] = {
                                'name': lulc_name,
                                'area': area,
                                'code': lulc_code
                            }
                            total_area += area
            
            formatted_data['summary']['total_area'] = total_area
            formatted_data['summary']['lulc_classes'] = lulc_classes
            
            # Find dominant LULC class
            if lulc_classes:
                dominant_class = max(lulc_classes.items(), key=lambda x: x[1]['area'])
                formatted_data['summary']['dominant_lulc_class'] = {
                    'code': dominant_class[0],
                    'name': dominant_class[1]['name'],
                    'area': dominant_class[1]['area'],
                    'percentage': (dominant_class[1]['area'] / total_area * 100) if total_area > 0 else 0
                }
        
        return formatted_data
    
    def _save_response(self, data, geometry_wkt):
        """Save the API response to a JSON file"""
        try:
            # Create data directory if it doesn't exist
            os.makedirs('data', exist_ok=True)
            
            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            # Create a short hash for the geometry to keep filename manageable
            geom_hash = str(hash(geometry_wkt))[-8:]
            filename = f"data/lulc_aoi_{geom_hash}_{timestamp}.json"
            
            # Save to file
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            
            self.logger.info(f"Saved LULC AOI response to {filename}")
            
        except Exception as e:
            self.logger.warning(f"Failed to save response to file: {str(e)}")
    
    def get_polygon_statistics(self, coordinates_list, parameters=None):
        """
        Get LULC statistics for a polygon defined by coordinate list
        
        Args:
            coordinates_list (list): List of [lng, lat] coordinate pairs
            parameters (dict): Additional query parameters
            
        Returns:
            dict: LULC statistics for the polygon
        """
        # Convert coordinates to WKT POLYGON format
        coord_strings = [f"{coord[0]} {coord[1]}" for coord in coordinates_list]
        
        # Ensure polygon is closed (first and last points are the same)
        if coordinates_list[0] != coordinates_list[-1]:
            coord_strings.append(coord_strings[0])
        
        wkt_polygon = f"POLYGON(({','.join(coord_strings)}))"
        
        return self.get_aoi_statistics(wkt_polygon, parameters)
    
    def get_bounding_box_statistics(self, min_lng, min_lat, max_lng, max_lat, parameters=None):
        """
        Get LULC statistics for a bounding box
        
        Args:
            min_lng (float): Minimum longitude
            min_lat (float): Minimum latitude  
            max_lng (float): Maximum longitude
            max_lat (float): Maximum latitude
            parameters (dict): Additional query parameters
            
        Returns:
            dict: LULC statistics for the bounding box
        """
        # Create bounding box polygon
        bbox_coords = [
            [min_lng, min_lat],
            [max_lng, min_lat],
            [max_lng, max_lat],
            [min_lng, max_lat],
            [min_lng, min_lat]  # Close the polygon
        ]
        
        return self.get_polygon_statistics(bbox_coords, parameters)
