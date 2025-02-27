import requests
from .auth import BASE_URL, get_headers
#teams.py
def get_team_id(team_number):
    url = f"{BASE_URL}/teams"
    params = {"number[]": team_number}
    response = requests.get(url, headers=get_headers(), params=params)
    if response.status_code == 200:
        data = response.json()
        if data["data"]:
            return data["data"][0]["id"]
    return None

def get_team_events(team_id):
    all_events = []
    page = 1
    while True:
        url = f"{BASE_URL}/teams/{team_id}/events?page={page}"
        response = requests.get(url, headers=get_headers())
        if response.status_code == 200:
            data = response.json()
            all_events.extend(data["data"])
            if not data["meta"]["next_page_url"]:
                break
            page += 1
        else:
            return None
    return {"data": all_events}

def get_team_details(team_id):
    url = f"{BASE_URL}/teams/{team_id}"
    response = requests.get(url, headers=get_headers())
    if response.status_code == 200:
        return response.json()
    return None