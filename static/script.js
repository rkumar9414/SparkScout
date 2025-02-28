// Fetch team events
async function fetchTeamEvents(teamNumber) {
    const response = await fetch(`/api/team-events/${teamNumber}`);
    const data = await response.json();
    return data;
}

// Fetch team details
async function fetchTeamDetails(teamId) {
    const response = await fetch(`/api/team-details/${teamId}`);
    const data = await response.json();
    return data;
}

// Fetch event details
async function fetchEventDetails(eventId) {
    const response = await fetch(`/api/event-details/${eventId}`);
    const data = await response.json();
    return data;
}

// Fetch teams for an event
async function fetchEventTeams(eventId) {
    try {
        const response = await fetch(`/api/event-teams/${eventId}`);
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error("Error fetching event teams:", error);
        return null;
    }
}

// Display team events on the main page
async function displayTeamEvents(teamNumber) {
    const events = await fetchTeamEvents(teamNumber);
    const eventsList = document.getElementById("eventsList");
    eventsList.innerHTML = "";

    if (events.data) {
        events.data.forEach(event => {
            const eventItem = document.createElement("div");
            eventItem.className = "event";
            eventItem.innerHTML = `
                <h3>${event.name}</h3>
                <p>Location: ${event.location.venue}, ${event.location.city}, ${event.location.region}</p>
                <p>Date: ${new Date(event.start).toLocaleDateString()}</p>
                <button onclick="handleViewTeams(${event.id})">View Teams</button>
            `;
            eventsList.appendChild(eventItem);
        });
    } else {
        eventsList.innerHTML = "<p>No events found.</p>";
    }
}

// Handle "View Teams" button click
async function handleViewTeams(eventId) {
    console.log("Button clicked for event ID:", eventId); // Debugging line
    const teams = await fetchEventTeams(eventId);
    const eventsList = document.getElementById("eventsList");
    eventsList.innerHTML = ""; // Clear the events list

    if (teams && teams.data) {
        const teamsList = document.createElement("div");
        teamsList.className = "teams-list";
        teamsList.innerHTML = "<h2>Teams Attending</h2>";

        teams.data.forEach(team => {
            const teamItem = document.createElement("div");
            teamItem.className = "team";
            teamItem.innerHTML = `
                <strong>${team.team_name} (${team.number})</strong>
                <span>Organization: ${team.organization}</span>
                <span>Grade: ${team.grade}</span>
            `;
            teamsList.appendChild(teamItem);
        });

        eventsList.appendChild(teamsList);
    } else {
        eventsList.innerHTML = "<p>No teams found for this event. Please check the event ID or API key.</p>";
    }
}

// Example usage
displayTeamEvents("750S");