from flask import Flask, jsonify, render_template
from api.teams import get_team_id, get_team_events, get_team_details
from api.events import get_event_details
import requests
from api.auth import BASE_URL, get_headers

app = Flask(__name__)

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
    details = get_team_details(team_id)
    if details:
        return jsonify(details)
    return jsonify({"error": "Failed to fetch team details"}), 500

# API endpoint to get event details
@app.route('/api/event-details/<event_id>')
def event_details(event_id):
    details = get_event_details(event_id)
    if details:
        return jsonify(details)
    return jsonify({"error": "Failed to fetch event details"}), 500

# New endpoint to fetch teams for an event
@app.route('/api/event-teams/<event_id>')
def event_teams(event_id):
    print(f"Fetching teams for event ID: {event_id}")  # Debugging line
    url = f"{BASE_URL}/events/{event_id}/teams"
    response = requests.get(url, headers=get_headers())
    if response.status_code == 200:
        return jsonify(response.json())
    print(f"Failed to fetch event teams. Status code: {response.status_code}")  # Debugging line
    return jsonify({"error": "Failed to fetch event teams"}), 500

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)