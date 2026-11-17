import numpy as np


# Create the same virtual map
grid = np.zeros((10, 10))

# Add fixed obstacles
grid[3:7, 4] = 1
grid[6, 4:8] = 1


# Function to detect obstacles around the robot
def detect_obstacles(robot_position):

    x, y = robot_position

    nearby_obstacles = []

    # Positions around the robot
    surrounding_positions = [
        (x + 1, y),  # Right
        (x - 1, y),  # Left
        (x, y + 1),  # Down
        (x, y - 1)   # Up
    ]

    # Check each position
    for position in surrounding_positions:

        px, py = position

        # Make sure position is inside the map
        if 0 <= px < 10 and 0 <= py < 10:

            # Check if there is an obstacle
            if grid[py, px] == 1:

                nearby_obstacles.append(position)

    return nearby_obstacles


# Test the detector
robot_position = (4, 5)

obstacles = detect_obstacles(robot_position)

print("Robot position:", robot_position)
print("Nearby obstacles:", obstacles)