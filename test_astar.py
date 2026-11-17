import numpy as np

from navigation.astar import astar


# Create a 10x10 grid
grid = np.zeros((10, 10))


# Add the same static obstacles
grid[3:7, 4] = 1
grid[6, 4:8] = 1


# Robot and destination
start = (1, 1)
goal = (8, 8)


# Find path
path = astar(
    grid,
    start,
    goal
)


print("A* Navigation Test")
print("------------------")

if path is None:

    print("No path found!")

else:

    print("Path found:")

    for position in path:
        print(position)

    print(f"\nTotal steps: {len(path) - 1}")