import os
from flask import Flask, jsonify, render_template, request, g
import sqlite3
import requests
from datetime import datetime
from dotenv import load_dotenv
from backend.api.auth import get_headers, BASE_URL

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['DATABASE'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'team_notes.db')

# --------------------------------------
# Database functions
# --------------------------------------
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
        db.row_factory = sqlite3.Row
    return db

def init_db():
    with app.app_context():
        db = get_db()
        db.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                team_id INTEGER NOT NULL,
                note_type TEXT NOT NULL,
                note TEXT NOT NULL
            );
        ''')
        db.commit()

init_db()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# --------------------------------------
# Team/event functions
# --------------------------------------
def sort_events_newest_to_oldest(events):
    return sorted(events, key=lambda x: datetime.fromisoformat(x["start"]), reverse=True)

def get_team_id(team_number):
    try:
        url = f"{BASE_URL}/teams"
        params = {"number[]": team_number}
        response = requests.get(url, headers=get_headers(), params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data["data"][0]["id"] if data["data"] else None
    except Exception as e:
        print(f"Error getting team ID: {str(e)}")
        return None

def get_team_events(team_id):
    try:
        all_events = []
        page = 1
        
        while True:
            url = f"{BASE_URL}/teams/{team_id}/events?page={page}"
            response = requests.get(url, headers=get_headers(), timeout=10)
            response.raise_for_status()
            
            data = response.json()
            filtered_events = [
                event for event in data["data"]
                if event.get("season", {}).get("name") == "2024-2025"
            ]
            all_events.extend(filtered_events)
            
            if not data["meta"]["next_page_url"]:
                break
            page += 1

        return {"data": sort_events_newest_to_oldest(all_events)}
    except Exception as e:
        print(f"Error getting team events: {str(e)}")
        return {"data": []}

def get_team_details(team_id):
    try:
        url = f"{BASE_URL}/teams/{team_id}"
        response = requests.get(url, headers=get_headers(), timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error getting team details: {str(e)}")
        return None

def get_team_skills(team_id):
    try:
        all_skills = []
        page = 1
        while True:
            url = f"{BASE_URL}/teams/{team_id}/skills?page={page}"
            response = requests.get(url, headers=get_headers(), timeout=10)
            response.raise_for_status()
            
            data = response.json()
            filtered_skills = [
                skill for skill in data.get("data", [])
                if skill.get("season", {}).get("name") == "2024-2025"
            ]
            all_skills.extend(filtered_skills)
            
            if not data["meta"]["next_page_url"]:
                break
            page += 1
            
        return {"data": all_skills}
    except Exception as e:
        print(f"Error getting team skills: {str(e)}")
        return {"data": []}

# --------------------------------------
# Application routes
# --------------------------------------
@app.route('/')
def index():
    return render_template('main.html')

@app.route('/api/team-events/<team_number>')
def api_team_events(team_number):
    try:
        team_id = get_team_id(team_number)
        if not team_id:
            return jsonify({"error": "Team not found", "data": []}), 404
        events = get_team_events(team_id)
        return jsonify(events)
    except Exception as e:
        return jsonify({"error": str(e), "data": []}), 500

@app.route('/team/<team_id>')
def team_details(team_id):
    try:
        team = get_team_details(team_id)
        skills = get_team_skills(team_id)
        
        db = get_db()
        cursor = db.execute('SELECT id, note_type, note FROM notes WHERE team_id = ?', (team_id,))
        notes = cursor.fetchall()
        
        notes_by_type = {
            "Autonomous Details": [],
            "Endgame Details": [],
            "Driver Details": [],
            "Misc": [],
        }
        for note in notes:
            if note["note_type"] in notes_by_type:
                notes_by_type[note["note_type"]].append({"id": note["id"], "note": note["note"]})
        
        return render_template('team-details.html', 
                            team=team, 
                            skills=skills["data"], 
                            notes_by_type=notes_by_type)
    except Exception as e:
        print(f"Error in team details: {str(e)}")
        return render_template('error.html'), 500

@app.route('/api/team/<int:team_id>/notes', methods=['POST'])
def save_note(team_id):
    try:
        data = request.get_json()
        if not data or 'note_type' not in data or 'note' not in data:
            return jsonify({"error": "Invalid request format"}), 400

        db = get_db()
        db.execute('INSERT INTO notes (team_id, note_type, note) VALUES (?, ?, ?)', 
                  (team_id, data['note_type'], data['note']))
        db.commit()
        return jsonify({"message": "Note saved successfully"}), 201
    except Exception as e:
        print(f"Error saving note: {str(e)}")
        return jsonify({"error": "Database error"}), 500

@app.route('/api/team/<int:team_id>/notes', methods=['GET'])
def get_notes(team_id):
    try:
        db = get_db()
        cursor = db.execute('SELECT id, note_type, note FROM notes WHERE team_id = ?', (team_id,))
        return jsonify({"notes": [dict(note) for note in cursor.fetchall()]}), 200
    except Exception as e:
        print(f"Error fetching notes: {str(e)}")
        return jsonify({"error": "Database error"}), 500

@app.route('/api/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    try:
        db = get_db()
        db.execute('DELETE FROM notes WHERE id = ?', (note_id,))
        db.commit()
        return jsonify({"message": "Note deleted successfully"}), 200
    except Exception as e:
        print(f"Error deleting note: {str(e)}")
        return jsonify({"error": "Database error"}), 500

@app.route('/api/event-teams/<event_id>')
def event_teams(event_id):
    try:
        all_teams = []
        page = 1
        while True:
            url = f"{BASE_URL}/events/{event_id}/teams?page={page}"
            response = requests.get(url, headers=get_headers(), timeout=10)
            
            if response.status_code != 200:
                return jsonify({
                    "error": "Failed to fetch teams",
                    "status": response.status_code
                }), 500

            data = response.json()
            all_teams.extend(data.get("data", []))
            
            if not data.get("meta", {}).get("next_page_url"):
                break
            page += 1

        return jsonify({"data": all_teams})
    except Exception as e:
        print(f"Error getting event teams: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)