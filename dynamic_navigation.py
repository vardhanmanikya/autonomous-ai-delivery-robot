import numpy as np
import matplotlib.pyplot as plt
import heapq


# --------------------------------------------------
# 1. CREATE THE MAP
# --------------------------------------------------

grid = np.zeros((10, 10))

# Fixed obstacles
grid[3:7, 4] = 1
grid[6, 4:8] = 1


# --------------------------------------------------
# 2. START AND DESTINATION
# --------------------------------------------------

start = (1, 1)
goal = (8, 8)


# --------------------------------------------------
# 3. ROBOT MOVEMENTS
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

        # Check neighbors
        for movement in movements:

            new_x = current[0] + movement[0]
            new_y = current[1] + movement[1]

            neighbor = (new_x, new_y)

            # Ignore obstacles
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
# 7. INITIAL PATH
# --------------------------------------------------

path = a_star(start, goal)


# --------------------------------------------------
# 8. CREATE VISUALIZATION
# --------------------------------------------------

plt.figure(figsize=(9, 7))

plt.imshow(grid, cmap="gray_r")

# Destination
plt.scatter(
    goal[0],
    goal[1],
    color="red",
    marker="*",
    s=300,
    label="Destination"
)

# Initial A* path
path_x = [p[0] for p in path]
path_y = [p[1] for p in path]

path_line, = plt.plot(
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

plt.title("Autonomous AI Delivery Robot - Dynamic Obstacle Avoidance")
plt.xlabel("X Position")
plt.ylabel("Y Position")
plt.grid(True)
plt.legend()

plt.pause(1)


# --------------------------------------------------
# 9. ROBOT MOVEMENT
# --------------------------------------------------

current_position = start

replanned = False

for position in path:

    current_position = position

    robot.set_offsets([position])

    print("Robot position:", position)

    # --------------------------------------------------
    # DYNAMIC OBSTACLE APPEARS
    # --------------------------------------------------

    if position == (1, 4) and not replanned:

        print()
        print("!!! Dynamic obstacle detected !!!")

        # Add new obstacle in front of robot
        grid[5, 1] = 1

        print("Obstacle added at:", (1, 5))

        # Recalculate path
        new_path = a_star(current_position, goal)

        if new_path:

            print("New A* path calculated!")

            # Remove old path
            path_line.remove()

            # Draw new path
            new_path_x = [p[0] for p in new_path]
            new_path_y = [p[1] for p in new_path]

            path_line, = plt.plot(
                new_path_x,
                new_path_y,
                linewidth=3,
                label="Replanned Path"
            )

            # Mark dynamic obstacle
            plt.scatter(
                1,
                5,
                color="orange",
                marker="X",
                s=200,
                label="Dynamic Obstacle"
            )

            plt.legend()

            # Follow the new path
            path = new_path

            replanned = True

            break

    plt.pause(0.5)


# --------------------------------------------------
# 10. FOLLOW NEW PATH
# --------------------------------------------------

if replanned:

    # Skip the starting position because
    # the robot is already there

    for position in path[1:]:

        robot.set_offsets([position])

        print("Replanned movement:", position)

        plt.pause(0.5)


# --------------------------------------------------
# 11. DELIVERY COMPLETE
# --------------------------------------------------

print()
print("Destination reached!")
print("Package delivered successfully.")

plt.show()