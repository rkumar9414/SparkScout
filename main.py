from flask import Flask, jsonify, render_template
import requests
from datetime import datetime
from backend.api.auth import get_headers, BASE_URL

# Initialize Flask app
app = Flask(__name__)

# Function to sort events from most recent to oldest
def sort_events_newest_to_oldest(events):
    return sorted(events, key=lambda x: datetime.fromisoformat(x["start"]), reverse=True)

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

# Function to Fetch Team Events (with pagination and sorting)
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
    return {"data": sort_events_newest_to_oldest(all_events)}

# Function to Fetch Team Details
def get_team_details(team_id):
    url = f"{BASE_URL}/teams/{team_id}"
    response = requests.get(url, headers=get_headers())
    if response.status_code == 200:
        return response.json()
    return None

# Function to Fetch Team Skills
def get_team_skills(team_id):
    url = f"{BASE_URL}/teams/{team_id}/skills"
    response = requests.get(url, headers=get_headers())
    if response.status_code == 200:
        return response.json()
    return None

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

# New endpoint to fetch teams for an event
@app.route('/api/event-teams/<event_id>')
def event_teams(event_id):
    print(f"Fetching teams for event ID: {event_id}")  # Debugging line
    url = f"{BASE_URL}/events/{event_id}/teams"
    print(f"API URL: {url}")  # Debugging line
    headers = get_headers()
    print(f"Headers: {headers}")  # Debugging line
    response = requests.get(url, headers=headers)
    print(f"Response status code: {response.status_code}")  # Debugging line
    if response.status_code == 200:
        return jsonify(response.json())
    print(f"Failed to fetch event teams. Status code: {response.status_code}")  # Debugging line
    return jsonify({"error": "Failed to fetch event teams"}), 500

# New route to display team details
@app.route('/team/<team_id>')
def team_details(team_id):
    team = get_team_details(team_id)
    skills = get_team_skills(team_id)
    print(f"Team: {team}")  # Debugging line
    print(f"Skills: {skills}")  # Debugging line
    if team and skills:
        return render_template('team-details.html', team=team, skills=skills)
    else:
        return render_template('team-details.html', team=team, skills=None)

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)