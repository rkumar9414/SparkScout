from flask import Flask, jsonify, render_template
from api.teams import get_team_id, get_team_events, get_team_details
from api.events import get_event_details

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

# API endpoint to get event details, app.py
@app.route('/api/event-details/<event_id>')
def event_details(event_id):
    details = get_event_details(event_id)
    if details:
        return jsonify(details)
    return jsonify({"error": "Failed to fetch event details"}), 500

if __name__ == '__main__':
    app.run(debug=True)