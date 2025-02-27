from flask import Flask, jsonify, render_template
import requests
from backend.api.auth import get_headers, BASE_URL  # Import from auth.py
# main.py
# Initialize Flask app
app = Flask(__name__)

# Function to Get Team ID
def get_team_id(team_number):
    url = f"{BASE_URL}/teams"
    params = {"number[]": team_number}
    response = requests.get(url, headers=get_headers(), params=params)
    
    if response.status_code == 200:
        data = response.json()
        if data["data"]:
            return data["data"][0]["id"]
        else:
            print(f"No team found with number {team_number}")
            return None
    else:
        print(f"Error: {response.status_code}")
        return None

# Function to Fetch Team Events (with pagination)
def get_team_events(team_id):
    all_events = []
    page = 1
    while True:
        url = f"{BASE_URL}/teams/{team_id}/events?page={page}"
        response = requests.get(url, headers=get_headers())
        if response.status_code == 200:
            data = response.json()
            all_events.extend(data["data"])
            if not data["meta"]["next_page_url"]:  # Stop if there are no more pages
                break
            page += 1
        else:
            print(f"Error: {response.status_code}")
            return None
    return {"data": all_events}

# Function to Extract Season Name
def extract_season_name(events):
    for event in events["data"]:
        if "2024-2025" in event["season"]["name"]:  # Look for the 2024-2025 season
            return event["season"]["name"]
    return None

# Function to Filter Events by Season
def filter_events_by_season(events, season_name):
    filtered_events = []
    for event in events["data"]:
        if event["season"]["name"] == season_name:
            filtered_events.append(event)
    return filtered_events

# Serve the main page
@app.route('/')
def index():
    return render_template('main.html')

# API endpoint to get team events
@app.route('/api/team-events/<team_number>')
def team_events(team_number):
    team_id = get_team_id(team_number)
    if team_id:
        events = get_team_events(team_id)
        if events:
            return jsonify(events)
    return jsonify({"error": "Failed to fetch team events"}), 500

# API endpoint to get team details
@app.route('/api/team-details/<team_id>')
def team_details(team_id):
    url = f"{BASE_URL}/teams/{team_id}"
    response = requests.get(url, headers=get_headers())
    if response.status_code == 200:
        return jsonify(response.json())
    return jsonify({"error": "Failed to fetch team details"}), 500

# API endpoint to get event details
@app.route('/api/event-details/<event_id>')
def event_details(event_id):
    url = f"{BASE_URL}/events/{event_id}"
    response = requests.get(url, headers=get_headers())
    if response.status_code == 200:
        return jsonify(response.json())
    return jsonify({"error": "Failed to fetch event details"}), 500

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)