from flask import Flask, jsonify, render_template, request, g
import sqlite3
import requests
from datetime import datetime
from backend.api.auth import get_headers, BASE_URL

app = Flask(__name__)
DATABASE = 'team_notes.db'


# Root route

@app.route('/')
def index():
    return render_template('main.html')


# Database setup and access

def get_db():
    if '_database' not in g:
        g._database = sqlite3.connect(DATABASE)
        g._database.row_factory = sqlite3.Row
    return g._database

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

@app.teardown_appcontext
def close_connection(exception):
    db = g.pop('_database', None)
    if db is not None:
        db.close()

init_db()


# API utilities

def sort_events_newest_to_oldest(events):
    return sorted(events, key=lambda x: datetime.fromisoformat(x["start"]), reverse=True)

def get_team_id(team_number):
    response = requests.get(f"{BASE_URL}/teams", headers=get_headers(), params={"number[]": team_number})
    if response.ok:
        data = response.json()
        return data["data"][0]["id"] if data["data"] else None
    return None

def get_team_events(team_id):
    all_events, page = [], 1
    while True:
        response = requests.get(f"{BASE_URL}/teams/{team_id}/events?page={page}", headers=get_headers())
        if not response.ok:
            return None
        data = response.json()
        all_events.extend(data["data"])
        if not data["meta"]["next_page_url"]:
            break
        page += 1
    return {"data": sort_events_newest_to_oldest(all_events)}

def get_team_details(team_id):
    response = requests.get(f"{BASE_URL}/teams/{team_id}", headers=get_headers())
    return response.json() if response.ok else None

def get_team_skills(team_id):
    all_skills, page = [], 1
    while True:
        response = requests.get(f"{BASE_URL}/teams/{team_id}/skills?page={page}", headers=get_headers())
        if not response.ok:
            return None
        data = response.json()
        skills_2024 = [s for s in data.get("data", []) if "2024-2025" in s.get("season", {}).get("name", "")]
        all_skills.extend(skills_2024)
        if not data["meta"]["next_page_url"]:
            break
        page += 1
    return {"data": all_skills}


# Routes

@app.route('/api/event-teams/<event_id>')
def event_teams(event_id):
    all_teams, page = [], 1
    while True:
        response = requests.get(f"{BASE_URL}/events/{event_id}/teams?page={page}", headers=get_headers())
        if not response.ok:
            return jsonify({"error": "Failed to fetch event teams"}), 500
        data = response.json()
        all_teams.extend(data["data"])
        if not data["meta"]["next_page_url"]:
            break
        page += 1
    return jsonify({"data": all_teams})

@app.route('/team/<team_id>')
def team_details(team_id):
    team = get_team_details(team_id)
    skills = get_team_skills(team_id)
    db = get_db()
    notes = db.execute('SELECT id, note_type, note FROM notes WHERE team_id = ?', (team_id,)).fetchall()

    notes_by_type = {
        "Autonomous Details": [],
        "Endgame Details": [],
        "Driver Details": [],
        "Misc": [],
    }
    for note in notes:
        if note["note_type"] in notes_by_type:
            notes_by_type[note["note_type"]].append({"id": note["id"], "note": note["note"]})

    return render_template('team-details.html', team=team, skills=skills, notes_by_type=notes_by_type)

@app.route('/api/team/<int:team_id>/notes', methods=['POST'])
def save_note(team_id):
    data = request.get_json()
    if not data or not data.get('note_type') or not data.get('note'):
        return jsonify({"error": "Note type and note are required"}), 400

    try:
        db = get_db()
        db.execute('INSERT INTO notes (team_id, note_type, note) VALUES (?, ?, ?)',
                   (team_id, data['note_type'], data['note']))
        db.commit()
        return jsonify({"message": "Note saved successfully"}), 201
    except Exception:
        return jsonify({"error": "An error occurred while saving the note"}), 500

@app.route('/api/team/<int:team_id>/notes', methods=['GET'])
def get_notes(team_id):
    try:
        db = get_db()
        notes = db.execute('SELECT id, note_type, note FROM notes WHERE team_id = ?', (team_id,)).fetchall()
        return jsonify({"notes": [dict(note) for note in notes]}), 200
    except Exception:
        return jsonify({"error": "An error occurred while fetching notes"}), 500

@app.route('/api/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    try:
        db = get_db()
        db.execute('DELETE FROM notes WHERE id = ?', (note_id,))
        db.commit()
        return jsonify({"message": "Note deleted successfully"}), 200
    except Exception:
        return jsonify({"error": "An error occurred while deleting the note"}), 500

@app.route('/api/team-events/<team_number>')
def team_events(team_number):
    team_id = get_team_id(team_number)
    if team_id:
        events = get_team_events(team_id)
        if events:
            return jsonify(events)
    return jsonify({"error": "Failed to fetch team events"}), 500


if __name__ == '__main__':
    app.run(debug=True)
