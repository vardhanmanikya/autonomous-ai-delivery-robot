import numpy as np
import matplotlib.pyplot as plt
import heapq


# --------------------------------------------------
# 1. CREATE MAP
# --------------------------------------------------

grid = np.zeros((10, 10))

# Fixed obstacles
grid[3:7, 4] = 1
grid[6, 4:8] = 1


# --------------------------------------------------
# 2. START AND GOAL
# --------------------------------------------------

start = (1, 1)
goal = (8, 8)


# --------------------------------------------------
# 3. MOVEMENTS
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

    return (
        abs(position[0] - goal[0])
        + abs(position[1] - goal[1])
    )


# --------------------------------------------------
# 6. A* PATH PLANNING
# --------------------------------------------------

def a_star(start, goal):

    open_list = []

    heapq.heappush(
        open_list,
        (0, start)
    )

    came_from = {}

    g_cost = {
        start: 0
    }

    while open_list:

        current_f, current = heapq.heappop(
            open_list
        )

        # Goal reached
        if current == goal:

            path = []

            while current in came_from:

                path.append(current)

                current = came_from[current]

            path.append(start)

            path.reverse()

            return path

        # Check neighbors
        for movement in movements:

            neighbor = (
                current[0] + movement[0],
                current[1] + movement[1]
            )

            if not is_valid_position(neighbor):
                continue

            new_g_cost = (
                g_cost[current] + 1
            )

            if (
                neighbor not in g_cost
                or new_g_cost < g_cost[neighbor]
            ):

                g_cost[neighbor] = new_g_cost

                h_cost = heuristic(
                    neighbor,
                    goal
                )

                f_cost = (
                    new_g_cost + h_cost
                )

                came_from[neighbor] = current

                heapq.heappush(
                    open_list,
                    (f_cost, neighbor)
                )

    return None


# --------------------------------------------------
# 7. OBSTACLE DETECTION
# --------------------------------------------------

def detect_obstacles(robot_position):

    x, y = robot_position

    nearby_obstacles = []

    surrounding_positions = [
        (x + 1, y),
        (x - 1, y),
        (x, y + 1),
        (x, y - 1)
    ]

    for position in surrounding_positions:

        px, py = position

        if 0 <= px < 10 and 0 <= py < 10:

            if grid[py, px] == 1:

                nearby_obstacles.append(
                    position
                )

    return nearby_obstacles


# --------------------------------------------------
# 8. INITIAL PATH
# --------------------------------------------------

path = a_star(
    start,
    goal
)

print("Initial A* path:")
print(path)


# --------------------------------------------------
# 9. VISUALIZATION
# --------------------------------------------------

plt.figure(figsize=(9, 7))

plt.imshow(
    grid,
    cmap="gray_r"
)

# Destination
plt.scatter(
    goal[0],
    goal[1],
    color="red",
    marker="*",
    s=300,
    label="Destination"
)

# Draw path
path_x = [p[0] for p in path]
path_y = [p[1] for p in path]

plt.plot(
    path_x,
    path_y,
    linewidth=3,
    label="A* Path"
)

# Robot
robot = plt.scatter(
    start[0],
    start[1],
    color="blue",
    s=180,
    label="Robot"
)

plt.title(
    "Autonomous AI Delivery Robot"
)

plt.xlabel("X Position")
plt.ylabel("Y Position")

plt.grid(True)
plt.legend()

plt.pause(1)


# --------------------------------------------------
# 10. ROBOT NAVIGATION
# --------------------------------------------------

current_position = start

for position in path:

    current_position = position

    robot.set_offsets([
        position
    ])

    print(
        "Robot position:",
        position
    )

    # Check nearby obstacles
    obstacles = detect_obstacles(
        current_position
    )

    if obstacles:

        print(
            "Obstacle detected:",
            obstacles
        )

    plt.pause(0.5)


# --------------------------------------------------
# 11. DELIVERY COMPLETE
# --------------------------------------------------

print()
print(
    "Destination reached!"
)

print(
    "Package delivered successfully."
)

plt.show()