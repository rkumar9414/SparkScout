import requests
from .auth import BASE_URL, get_headers
#events.py
def get_event_details(event_id):
    url = f"{BASE_URL}/events/{event_id}"
    response = requests.get(url, headers=get_headers())
    if response.status_code == 200:
        return response.json()
    return None