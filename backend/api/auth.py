import os
# RobotEvents API Configuration
BASE_URL = "https://www.robotevents.com/api/v2"

def get_headers():
    """
    Returns the headers required for RobotEvents API requests.
    Includes the API key for authentication.
    """
    api_key = os.environ.get("ROBOT_EVENTS_API_KEY")  # Fetch from environment variables
    if not api_key:
        raise ValueError("ROBOT_EVENTS_API_KEY environment variable is not set")
    
    return {
        "Authorization": f"Bearer {api_key}",  # Use the fetched API key
        "Accept": "application/json"
    }