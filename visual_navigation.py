import numpy as np
import matplotlib.pyplot as plt
import heapq


# --------------------------------------------------
# 1. CREATE THE VIRTUAL MAP
# --------------------------------------------------

grid = np.zeros((10, 10))

# Add obstacles
grid[3:7, 4] = 1
grid[6, 4:8] = 1


# --------------------------------------------------
# 2. START AND DESTINATION
# --------------------------------------------------

start = (1, 1)
goal = (8, 8)


# --------------------------------------------------
# 3. POSSIBLE MOVEMENTS
# --------------------------------------------------

movements = [
    (1, 0),
    (-1, 0),
    (0, 1),
    (0, -1)
]


# --------------------------------------------------
# 4. CHECK VALID POSITION
# --------------------------------------------------

def is_valid_position(position):

    x, y = position

    if x < 0 or x >= 10 or y < 0 or y >= 10:
        return False

    if grid[y, x] == 1:
        return False

    return True


# --------------------------------------------------
# 5. HEURISTIC
# --------------------------------------------------

def heuristic(position, goal):

    distance_x = abs(position[0] - goal[0])
    distance_y = abs(position[1] - goal[1])

    return distance_x + distance_y


# --------------------------------------------------
# 6. A* ALGORITHM
# --------------------------------------------------

def a_star(start, goal):

    open_list = []

    heapq.heappush(open_list, (0, start))

    came_from = {}

    g_cost = {start: 0}

    while open_list:

        current_f, current = heapq.heappop(open_list)

        # Destination reached
        if current == goal:

            path = []

            while current in came_from:

                path.append(current)
                current = came_from[current]

            path.append(start)

            path.reverse()

            return path

        # Check neighboring cells
        for movement in movements:

            new_x = current[0] + movement[0]
            new_y = current[1] + movement[1]

            neighbor = (new_x, new_y)

            if not is_valid_position(neighbor):
                continue

            new_g_cost = g_cost[current] + 1

            if neighbor not in g_cost or new_g_cost < g_cost[neighbor]:

                g_cost[neighbor] = new_g_cost

                h_cost = heuristic(neighbor, goal)

                f_cost = new_g_cost + h_cost

                came_from[neighbor] = current

                heapq.heappush(
                    open_list,
                    (f_cost, neighbor)
                )

    return None


# --------------------------------------------------
# 7. FIND THE A* PATH
# --------------------------------------------------

path = a_star(start, goal)


# --------------------------------------------------
# 8. CREATE THE FIGURE
# --------------------------------------------------

plt.figure(figsize=(9, 7))

plt.imshow(grid, cmap="gray_r")

# Draw destination
plt.scatter(
    goal[0],
    goal[1],
    color="red",
    marker="*",
    s=300,
    label="Destination"
)

# Draw A* path
if path:

    path_x = [position[0] for position in path]
    path_y = [position[1] for position in path]

    plt.plot(
        path_x,
        path_y,
        linewidth=3,
        label="A* Path"
    )


# --------------------------------------------------
# 9. ANIMATE THE ROBOT
# --------------------------------------------------

robot = plt.scatter(
    start[0],
    start[1],
    color="blue",
    s=180,
    label="Robot"
)

plt.title("Autonomous AI Delivery Robot - A* Navigation")

plt.xlabel("X Position")
plt.ylabel("Y Position")

plt.grid(True)
plt.legend()

# Show the initial map
plt.pause(1)


# --------------------------------------------------
# 10. MOVE ROBOT THROUGH THE PATH
# --------------------------------------------------

if path:

    for position in path:

        # Move the robot
        robot.set_offsets([position])

        # Print current position
        print("Robot position:", position)

        # Update the screen
        plt.pause(0.5)


# --------------------------------------------------
# 11. DELIVERY COMPLETE
# --------------------------------------------------

print()
print("Destination reached!")
print("Package delivered successfully.")

plt.show()