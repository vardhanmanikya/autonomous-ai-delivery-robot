import json
import os


MEMORY_FILE = "data/robot_experience.json"


def load_experience():
    """Load the robot's previous experience."""

    if not os.path.exists(MEMORY_FILE):
        return {
            "successful_missions": 0,
            "failed_missions": 0,
            "problem_locations": [],
            "problem_routes": []
        }

    try:
        with open(MEMORY_FILE, "r") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return {
            "successful_missions": 0,
            "failed_missions": 0,
            "problem_locations": [],
            "problem_routes": []
        }


def save_experience(experience):
    """Save the robot's experience."""

    os.makedirs("data", exist_ok=True)

    with open(MEMORY_FILE, "w") as file:
        json.dump(experience, file, indent=4)


def record_success():
    """Record a successful delivery."""

    experience = load_experience()
    experience["successful_missions"] += 1
    save_experience(experience)


def record_failure():
    """Record a failed delivery."""

    experience = load_experience()
    experience["failed_missions"] += 1
    save_experience(experience)


def record_problem_location(location):
    """Remember a location where the robot experienced a problem."""

    experience = load_experience()

    location = list(location)

    if location not in experience["problem_locations"]:
        experience["problem_locations"].append(location)

    save_experience(experience)


def get_problem_locations():
    """Return locations that caused problems in previous missions."""

    experience = load_experience()
    return experience["problem_locations"]