import requests 

BASE_URL = "https://kgis.ksrsac.in:9000/genericwebservices/ws"

def call_kgis_api(endpoint ,payload): 
    url = f"{BASE_URL}/{endpoint}"

    params = payload.model_dump()

    try:
        response = requests.get(url,params) 
        response.raise_for_status()
        data = response.json()[0]
        return data
    except requests.RequestException as e:
        return(f"Request failed:{str(e)}")
    except Exception as e:
        return(f"Unexpected error:{str(e)}")
def get_admin_hierarchy(payload):
    return call_kgis_api("kgisadminhierarchy",payload)
    
def get_district_name(payload):
    return call_kgis_api("districtname",payload)

def get_location_details(payload):
    return call_kgis_api("getlocationdetails",payload)

def get_hobli_code(payload):
    return call_kgis_api("hoblicode",payload)

def get_taluk_code(payload):
    return call_kgis_api("talukcode",payload)

def get_distance_btw_pin_codes(payload):
    return call_kgis_api("getDistanceBtwPincode",payload)

def get_nearby_admin_hierarchy(payload):
    return call_kgis_api("nearbyadminhierarchy",payload)

def get_geometric_polygon(payload):
    """
    Calls the KGIS API to fetch geometric polygons for a given survey number.
    """
    try:
        url = f"{BASE_URL}/geomForSurveyNum/{payload.village_id}/{payload.survey_no}/{payload.coord_type}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()  
        return {"polygons": data}  
    except requests.RequestException as e:
        return {"polygons": []}
    except Exception as e:
        return {"polygons": []}