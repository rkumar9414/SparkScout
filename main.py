from flask import Flask, jsonify, render_template, request, g
import sqlite3
import requests
from datetime import datetime
from backend.api.auth import get_headers, BASE_URL

# Initialize Flask app
app = Flask(__name__)

# Database configuration
DATABASE = 'team_notes.db'

# Function to get the database connection
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row  # Return rows as dictionaries
    return db

# Function to initialize the database
def init_db():
    with app.app_context():
        db = get_db()
        db.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                team_id INTEGER NOT NULL,
                note TEXT NOT NULL
            );
        ''')
        db.commit()

# Initialize the database when the app starts
init_db()

# Close the database connection when the app context ends
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

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
    all_teams = []
    page = 1
    while True:
        url = f"{BASE_URL}/events/{event_id}/teams?page={page}"
        response = requests.get(url, headers=get_headers())
        if response.status_code == 200:
            data = response.json()
            all_teams.extend(data["data"])
            if not data["meta"]["next_page_url"]:  # Stop if there are no more pages
                break
            page += 1
        else:
            print(f"Failed to fetch event teams. Status code: {response.status_code}")
            return jsonify({"error": "Failed to fetch event teams"}), 500
    return jsonify({"data": all_teams})

# New route to display team details
@app.route('/team/<team_id>')
def team_details(team_id):
    team = get_team_details(team_id)
    skills = get_team_skills(team_id)
    
    # Fetch notes for the team
    db = get_db()
    cursor = db.execute('SELECT note FROM notes WHERE team_id = ?', (team_id,))
    notes = cursor.fetchall()
    
    if team and skills:
        return render_template('team-details.html', team=team, skills=skills, notes=notes)
    else:
        return render_template('team-details.html', team=team, skills=None, notes=notes)

# Route to save a note for a team
@app.route('/api/team/<int:team_id>/notes', methods=['POST'])
def save_note(team_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        note = data.get('note')
        if not note:
            return jsonify({"error": "Note is required"}), 400

        db = get_db()
        db.execute('INSERT INTO notes (team_id, note) VALUES (?, ?)', (team_id, note))
        db.commit()
        return jsonify({"message": "Note saved successfully"}), 201
    except Exception as e:
        print(f"Error saving note: {e}")  # Log the error
        return jsonify({"error": "An error occurred while saving the note"}), 500

# Route to get all notes for a team
@app.route('/api/team/<int:team_id>/notes', methods=['GET'])
def get_notes(team_id):
    try:
        db = get_db()
        cursor = db.execute('SELECT note FROM notes WHERE team_id = ?', (team_id,))
        notes = cursor.fetchall()
        return jsonify({"notes": [note["note"] for note in notes]}), 200
    except Exception as e:
        print(f"Error fetching notes: {e}")  # Log the error
        return jsonify({"error": "An error occurred while fetching notes"}), 500

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)