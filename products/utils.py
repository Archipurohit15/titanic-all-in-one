import os
import requests

def fetch_image_for(query):
    api_key = os.environ.get('PEXELS_API_KEY')
    if not api_key:
        return None
    try:
        response = requests.get(
            'https://api.pexels.com/v1/search',
            headers={'Authorization': api_key},
            params={'query': query, 'per_page': 1},
            timeout=5,
        )
        data = response.json()
        photos = data.get('photos')
        if photos:
            return photos[0]['src']['medium']
    except requests.RequestException:
        pass
    return None