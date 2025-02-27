//script.js
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
                <p>Date: ${event.start}</p>
            `;
            eventsList.appendChild(eventItem);
        });
    } else {
        eventsList.innerHTML = "<p>No events found.</p>";
    }
}

// Example usage
displayTeamEvents("750S");