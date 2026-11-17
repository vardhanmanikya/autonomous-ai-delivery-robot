import numpy as np
import matplotlib.pyplot as plt

from perception.ai_detection import detect_obstacles


# Create 10x10 grid
grid = np.zeros((10, 10))

# Existing static obstacles
grid[3:7, 4] = 1
grid[6, 4:8] = 1


# Detect objects using YOLO
obstacles = detect_obstacles("bus.jpg")


# Convert AI detections to grid cells
for obstacle in obstacles:

    confidence = obstacle["confidence"]
    position = obstacle["position"]

    # Ignore low-confidence detections
    if confidence < 0.70:
        continue

    if position == "LEFT":
        x, y = 3, 4

    elif position == "CENTER":
        x, y = 4, 4

    else:
        x, y = 5, 4

    # Mark AI obstacle on grid
    grid[y, x] = 1


# Robot and destination
robot_x = 1
robot_y = 1

destination_x = 8
destination_y = 8


# Display grid
plt.figure(figsize=(7, 7))

plt.imshow(grid, cmap="gray_r")

# Robot
plt.scatter(
    robot_x,
    robot_y,
    color="blue",
    s=150,
    label="Robot"
)

# Destination
plt.scatter(
    destination_x,
    destination_y,
    color="red",
    marker="*",
    s=200,
    label="Destination"
)

plt.title("AI-Generated Obstacles on Simulation Grid")

plt.xticks(range(10))
plt.yticks(range(10))

plt.grid(True)

plt.legend()

plt.show()