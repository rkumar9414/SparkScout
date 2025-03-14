from flask import Flask, jsonify, render_template, request, g
import sqlite3
import requests
from datetime import datetime
from backend.api.auth import get_headers, BASE_URL

# Initialize Flask app
app = Flask(__name__)

# Database configuration
DATABASE = 'team_notes.db'

# --------------------------------------
# Root route (MUST BE AT THE TOP)
# --------------------------------------
@app.route('/')
def index():
    return render_template('main.html')

# --------------------------------------
# Database functions
# --------------------------------------
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
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
            print(f"Error: {response.status_code}")
            return None
    return {"data": sort_events_newest_to_oldest(all_events)}

def get_team_details(team_id):
    url = f"{BASE_URL}/teams/{team_id}"
    response = requests.get(url, headers=get_headers())
    if response.status_code == 200:
        return response.json()
    return None

def get_team_skills(team_id):
    all_skills = []
    page = 1
    while True:
        url = f"{BASE_URL}/teams/{team_id}/skills?page={page}"
        response = requests.get(url, headers=get_headers())
        
        print(f"\n[DEBUG] Fetching skills page {page}")
        print(f"[DEBUG] Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            filtered_skills = [
                skill for skill in data.get("data", [])
                if "2024-2025" in skill.get("season", {}).get("name", "")
            ]
            all_skills.extend(filtered_skills)
            if not data["meta"]["next_page_url"]:
                break
            page += 1
        else:
            print(f"[ERROR] Failed to fetch skills: {response.status_code}")
            return None
    print(f"\n[DEBUG] Total skills for 2024-2025: {len(all_skills)}")
    return {"data": all_skills}

# --------------------------------------
# Other routes
# --------------------------------------
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
            if not data["meta"]["next_page_url"]:
                break
            page += 1
        else:
            print(f"Failed to fetch event teams. Status code: {response.status_code}")
            return jsonify({"error": "Failed to fetch event teams"}), 500
    return jsonify({"data": all_teams})

@app.route('/team/<team_id>')
def team_details(team_id):
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
                         skills=skills, 
                         notes_by_type=notes_by_type)

@app.route('/api/team/<int:team_id>/notes', methods=['POST'])
def save_note(team_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        note_type = data.get('note_type')
        note = data.get('note')
        if not note_type or not note:
            return jsonify({"error": "Note type and note are required"}), 400

        db = get_db()
        db.execute('INSERT INTO notes (team_id, note_type, note) VALUES (?, ?, ?)', 
                  (team_id, note_type, note))
        db.commit()
        return jsonify({"message": "Note saved successfully"}), 201
    except Exception as e:
        print(f"Error saving note: {e}")
        return jsonify({"error": "An error occurred while saving the note"}), 500

@app.route('/api/team/<int:team_id>/notes', methods=['GET'])
def get_notes(team_id):
    try:
        db = get_db()
        cursor = db.execute('SELECT id, note_type, note FROM notes WHERE team_id = ?', (team_id,))
        notes = cursor.fetchall()
        return jsonify({"notes": [dict(note) for note in notes]}), 200
    except Exception as e:
        print(f"Error fetching notes: {e}")
        return jsonify({"error": "An error occurred while fetching notes"}), 500

@app.route('/api/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    try:
        db = get_db()
        db.execute('DELETE FROM notes WHERE id = ?', (note_id,))
        db.commit()
        return jsonify({"message": "Note deleted successfully"}), 200
    except Exception as e:
        print(f"Error deleting note: {e}")
        return jsonify({"error": "An error occurred while deleting the note"}), 500

@app.route('/api/team-events/<team_number>')
def team_events(team_number):
    team_id = get_team_id(team_number)
    if team_id:
        events = get_team_events(team_id)
        if events:
            return jsonify(events)
    return jsonify({"error": "Failed to fetch team events"}), 500

# --------------------------------------
# Run the app
# --------------------------------------
if __name__ == '__main__':
    app.run(debug=True)