import requests

def get_location_details():
    try:
        response = requests.get('https://ipinfo.io/')
        data = response.json()

        location_details = {
            'IP': data.get('ip', 'Not Available'),
            'City': data.get('city', 'Not Available'),
            'Region': data.get('region', 'Not Available'),
            'Country': data.get('country', 'Not Available'),
            'Coordinates': data.get('loc', 'Not Available')  # Latitude and Longitude
        }

        return location_details

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def location_details_string(location):
    out = ""
    if location:
        for key, value in location.items():
            out += f"{key}: {value}\n"
    
    return out

def city(location):
    return location['City']

# This block will only execute if the script is run directly (not imported)
if __name__ == "__main__":
    location = get_location_details()
    location_details_string(location)
    
