import requests
from django.conf import settings

def get_formatted_address_from_coords(latitude, longitude):
  api_key = settings.GOOGLE_MAPS_API_KEY
  url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={latitude},{longitude}&key={api_key}"
  response = requests.get(url)
  data = response.json()
  
  if response.status_code == 200 and data['status'] == 'OK':
    results = data['results']
    if results:
      result = results[0]
      formatted_address = result['formatted_address']

      # Extract components from address
      city = "Failed to retrieve City"
      state = "Failed to retrive State"
      postal_code = "Failed to retrive postal_code"
      for component in result['address_components']:
        types = component['types']
        if 'locality' in types:
          city = component['long_name']
        elif 'administrative_area_level_1' in types:
          state = component['long_name']
        elif 'postal_code' in types:
          postal_code = component['long_name']
      return {'formatted_address': formatted_address, 'city': city, 'state': state, 'postal_code': postal_code}
    else:
      return {'message':'Failed to retrieve Details'}
  else:
    return response


