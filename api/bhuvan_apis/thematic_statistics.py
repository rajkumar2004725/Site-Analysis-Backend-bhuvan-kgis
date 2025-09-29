import requests
import json
import os
from datetime import datetime
import logging
from .config.bhuvan_tokens import get_service_token

class ThematicStatisticsAPI:
    """
    Client for interacting with Bhuvan LULC Statistics API
    This class handles requests to the Bhuvan Land Use Land Cover statistics services,
    extracts relevant data points, and formats the response.
    """
    
    def __init__(self):
        self.base_url = os.getenv('BHUVAN_API_URL', 'https://bhuvan-app1.nrsc.gov.in/api/lulc/curljson.php')
        self.pie_url = os.getenv('BHUVAN_PIE_API_URL', 'https://bhuvan-app1.nrsc.gov.in/api/lulc/curlpie.php')
        # Use centralized token management
        self.api_token = get_service_token('lulc_statistics')
        self.username = os.getenv('API_USERNAME')
        self.password = os.getenv('API_PASSWORD')
        self.default_state_code = os.getenv('DEFAULT_STATE_CODE', 'KL')
        self.default_district_code = os.getenv('DEFAULT_DISTRICT_CODE', '3201')
        self.default_year = os.getenv('DEFAULT_YEAR', '1112')
        self.logger = logging.getLogger(__name__)
        
        # Load district and state codes
        self.district_codes = self._load_district_codes()
        self.state_codes = self._load_state_codes()
        
        # Configure logging if not already configured
        if not self.logger.handlers:
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )

    def _load_district_codes(self):
        """Load district codes from JSON file."""
        try:
            district_file = os.path.join(os.path.join(os.path.dirname(__file__), 'data', 'district_codes.json'))
            with open(district_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.warning(f"Could not load district codes: {e}")
            return {}

    def _load_state_codes(self):
        """Load state codes from JSON file."""
        try:
            state_file = os.path.join(os.path.join(os.path.dirname(__file__), 'data', 'state_codes.json'))
            with open(state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.warning(f"Could not load state codes: {e}")
            return {}

    def get_district_code(self, district_name):
        """Get district code by name."""
        return self.district_codes.get(district_name)
    
    def get_statistics(self, coordinates, details):
        """Get thematic statistics for a given coordinate and district code."""
        if not self.api_token:
            return {'error': 'No valid LULC statistics token available'}
        
        # Extract district code from details
        distcode = details.get('distcode')
        if not distcode:
            return {'error': 'Missing required parameter: distcode'}
        
        # According to API doc: Use GET with application/x-www-form-urlencoded
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        # API parameters according to documentation
        params = {
            'distcode': distcode,  # 4-digit district code
            'year': '1112',        # 2011-2012 year format  
            'token': self.api_token
        }
        
        # Add optional year parameter if provided in details
        if 'year' in details:
            params['year'] = details['year']
        
        try:
            print(f"Making GET request to {self.base_url}")
            print(f"Headers: {headers}")
            print(f"Params: {params}")
            
            response = requests.get(self.base_url, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            
            print(f"Response status: {response.status_code}")
            print(f"Response content-type: {response.headers.get('content-type', 'Unknown')}")
            print(f"Response length: {len(response.text)}")
            print(f"Response first 300 chars: {response.text[:300]}")
            
            # Try to parse as JSON 
            content = response.text.strip()
            try:
                data = json.loads(content)
                print("✅ Successfully parsed JSON response")
                print(f"JSON keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                return {'lulc_statistics': data}
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
                # Check for API error messages
                if len(content) < 200 and ('theme' in content.lower() or 'verify' in content.lower()):
                    return {'error': f'API validation error: {content}'}
                return {'error': f'Invalid JSON response: {content[:200]}'}
            
        except requests.RequestException as e:
            return {'error': f'Request failed: {str(e)}'}
    
    def _save_response(self, data, coordinates, parameters=None):
        """Save API response to file for analysis"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create a descriptive filename based on state/district or coordinates
        if parameters and parameters.get('district_code'):
            filename = f"data/lulc_stats_district_{parameters.get('district_code')}_{timestamp}.json"
        elif parameters and parameters.get('state_code'):
            filename = f"data/lulc_stats_state_{parameters.get('state_code')}_{timestamp}.json"
        else:
            filename = f"data/lulc_stats_{coordinates['lat']}_{coordinates['lng']}_{timestamp}.json"
        
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
            
        self.logger.info(f"Saved LULC statistics response to {filename}")
            
    def _generate_simulated_data(self, coordinates, parameters=None):
        """Generate simulated LULC data for testing purposes when API is unavailable"""
        # Determine district name based on provided parameters or coordinates
        if parameters and parameters.get('district_code'):
            district_name = f"District {parameters.get('district_code')}"
        elif parameters and parameters.get('state_code'):
            district_name = f"State {parameters.get('state_code')}"
        else:
            district_name = f"Area near {coordinates['lat']},{coordinates['lng']}"
        
        # Generate a total area based on coordinates or a default value
        total_area = round(coordinates['lat'] * coordinates['lng'] / 4) if coordinates else 10000
        
        # Base data - simulate LULC data structure as per the API documentation
        data = {
            "0": district_name,
            "1": str(total_area),
            "2": str(round(total_area * 0.12, 2)),  # Urban area (12%)
            "3": str(round(total_area * 0.03, 2)),  # Rural area (3%)
            "4": str(round(total_area * 0.05, 2)),  # Mining area (5%)
            "5": str(round(total_area * 0.40, 2)),  # Agricultural area (40%)
            "6": str(round(total_area * 0.05, 2)),  # Plantations (5%)
            "7": str(round(total_area * 0.15, 2)),  # Fallow land (15%)
            "9": str(round(total_area * 0.15, 2)),  # Forest area (15%)
            "16": str(round(total_area * 0.05, 2)),  # Water bodies (5%)
            "name": district_name,
            "totalarea": str(total_area),
            "l01": str(round(total_area * 0.12, 2)),  # Urban area
            "l02": str(round(total_area * 0.03, 2)),  # Rural area
            "l03": str(round(total_area * 0.05, 2)),  # Mining area
            "l04": str(round(total_area * 0.40, 2)),  # Agricultural area
            "l05": str(round(total_area * 0.05, 2)),  # Plantations
            "l06": str(round(total_area * 0.15, 2)),  # Fallow land
            "l09": str(round(total_area * 0.15, 2)),  # Forest area
            "l15": str(round(total_area * 0.05, 2)),  # Water bodies
            "_simulated": True  # Flag to indicate this is simulated data
        }
        
        # Add more data fields for completeness
        for i in range(8, 25):
            if str(i) not in data:
                data[str(i)] = "0"
            if f"l{i:02d}" not in data:
                data[f"l{i:02d}"] = "0"
            data.update({
                "vegetation_index": 0.67,
                "terrain_slope": 12.5,
                "water_table_depth": 45.8,
                "detailed_analysis": {
                    "risk_factors": ["flood", "erosion"],
                    "suitability_scores": {
                        "residential": 0.75,
                        "commercial": 0.85,
                        "industrial": 0.45
                    }
                }
            })
            
        return data
