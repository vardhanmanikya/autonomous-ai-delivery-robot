import numpy as np
import matplotlib.pyplot as plt

# Create a 10 x 10 virtual map
grid = np.zeros((10, 10))

# Add obstacles
grid[3:7, 4] = 1
grid[6, 4:8] = 1

# Robot starting position
start = (1, 1)

# Delivery destination
destination = (8, 8)

# A simple test path
path = [
    (1, 1),
    (2, 1),
    (3, 1),
    (3, 2),
    (3, 3),
    (3, 4),
    (3, 5),
    (3, 6),
    (3, 7),
    (3, 8),
    (4, 8),
    (5, 8),
    (6, 8),
    (7, 8),
    (8, 8)
]

# Create the figure
plt.figure(figsize=(8, 6))

# Display the map
plt.imshow(grid, cmap="gray_r")

# Display destination
plt.scatter(
    destination[0],
    destination[1],
    color="red",
    marker="*",
    s=250,
    label="Destination"
)

# Add title and labels
plt.title("Autonomous AI Delivery Robot")
plt.xlabel("X Position")
plt.ylabel("Y Position")
plt.grid(True)
plt.legend()

# Move the robot through the path
for position in path:

    # Draw the robot
    plt.scatter(
        position[0],
        position[1],
        color="blue",
        s=150
    )

    # Show the current position
    print("Robot position:", position)

    # Pause so we can see the movement
    plt.pause(0.8)

plt.show()