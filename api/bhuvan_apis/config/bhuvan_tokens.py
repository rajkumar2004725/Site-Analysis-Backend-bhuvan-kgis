"""
Bhuvan API Token Configuration
Centralized management of different API tokens for various Bhuvan services
"""

import os
import logging
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Look for .env file in the project root
    env_path = Path(__file__).parent.parent.parent.parent / '.env'
    load_dotenv(env_path)
    print(f"Loaded .env from: {env_path}")
except ImportError:
    logging.warning("python-dotenv not installed. Environment variables must be set manually.")

logger = logging.getLogger(__name__)

class BhuvanTokenManager:
    """
    Manages API tokens for different Bhuvan services
    """
    
    def __init__(self):
        self.tokens = {
            'lulc_statistics': os.getenv('BHUVAN_LULC_STATISTICS_TOKEN'),
            'lulc_aoi_wise': os.getenv('BHUVAN_LULC_AOI_WISE_TOKEN'),
            'postal_hospital': os.getenv('BHUVAN_POSTAL_HOSPITAL_TOKEN'),
            'village_geocoding': os.getenv('BHUVAN_VILLAGE_GEOCODING_TOKEN'),
            'village_reverse_geocoding': os.getenv('BHUVAN_VILLAGE_REVERSE_GEOCODING_TOKEN'),
            'routing': os.getenv('BHUVAN_ROUTING_TOKEN'),
            'geoid': os.getenv('BHUVAN_GEOID_TOKEN'),
            'legacy': os.getenv('BHUVAN_API_TOKEN')  # Re-enabled fallback token
        }
        
        # Debug: Print token values
        for service, token in self.tokens.items():
            print(f"{service} token: {token}")
        
        # Log which tokens are available
        self._log_token_status()
    
    def get_token(self, service_type):
        """
        Get the appropriate token for a service type
        
        Args:
            service_type (str): Type of service (lulc_statistics, routing, geoid, etc.)
            
        Returns:
            str: API token or raises ValueError if not found
        """
        token = self.tokens.get(service_type)
        if not token:
            logger.warning(f"No token found for service '{service_type}', falling back to legacy token")
            token = self.tokens.get('legacy')
        
        if not token:
            logger.error(f"No token available for service '{service_type}'")
            raise ValueError(f"No valid token available for {service_type}")
        
        return token
    
    def _log_token_status(self):
        """Log the status of available tokens"""
        available_tokens = []
        missing_tokens = []
        
        for service, token in self.tokens.items():
            if token:
                available_tokens.append(service)
            else:
                missing_tokens.append(service)
        
        if available_tokens:
            logger.info(f"Available tokens for services: {', '.join(available_tokens)}")
        
        if missing_tokens:
            logger.warning(f"Missing tokens for services: {', '.join(missing_tokens)}")
    
    def validate_tokens(self):
        """
        Validate that essential tokens are available
        
        Returns:
            dict: Status of token validation
        """
        essential_services = ['lulc_statistics', 'geoid', 'routing']
        validation_result = {
            'valid': True,
            'missing_essential': [],
            'available_services': [],
            'total_tokens': 0
        }
        
        for service in essential_services:
            token = self.get_token(service)
            if token:
                validation_result['available_services'].append(service)
            else:
                validation_result['missing_essential'].append(service)
                validation_result['valid'] = False
        
        validation_result['total_tokens'] = len([t for t in self.tokens.values() if t])
        
        return validation_result

# Global instance
token_manager = BhuvanTokenManager()

def get_service_token(service_type):
    """
    Convenience function to get a token for a specific service
    
    Args:
        service_type (str): Type of service
        
    Returns:
        str: API token
    """
    return token_manager.get_token(service_type)