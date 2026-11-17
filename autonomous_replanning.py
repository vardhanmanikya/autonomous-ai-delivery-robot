import numpy as np
import matplotlib.pyplot as plt
import heapq

from experience_memory import (
    get_problem_locations,
    record_problem_location,
    record_success,
    record_failure
)


# --------------------------------------------------
# 1. MAP
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
# 4. VALID POSITION
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
# 6. A* ALGORITHM WITH EXPERIENCE
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

    # Load previous robot experience
    problem_locations = {
        tuple(location)
        for location in get_problem_locations()
    }

    if problem_locations:

        print()
        print("Robot Experience Memory:")
        print(
            "Previously problematic locations:",
            problem_locations
        )

    while open_list:

        current_f, current = heapq.heappop(
            open_list
        )

        if current == goal:

            path = []

            while current in came_from:

                path.append(current)
                current = came_from[current]

            path.append(start)
            path.reverse()

            return path

        for movement in movements:

            neighbor = (
                current[0] + movement[0],
                current[1] + movement[1]
            )

            if not is_valid_position(neighbor):
                continue

            # Normal movement cost
            movement_cost = 1

            # Learned problem locations have higher cost
            if neighbor in problem_locations:

                movement_cost = 6

            new_g = (
                g_cost[current]
                + movement_cost
            )

            if (
                neighbor not in g_cost
                or new_g < g_cost[neighbor]
            ):

                g_cost[neighbor] = new_g

                h = heuristic(
                    neighbor,
                    goal
                )

                f = new_g + h

                came_from[neighbor] = current

                heapq.heappush(
                    open_list,
                    (f, neighbor)
                )

    return None


# --------------------------------------------------
# 7. OBSTACLE DETECTION
# --------------------------------------------------

def detect_obstacles(position):

    x, y = position

    nearby = []

    surrounding = [
        (x + 1, y),
        (x - 1, y),
        (x, y + 1),
        (x, y - 1)
    ]

    for px, py in surrounding:

        if 0 <= px < 10 and 0 <= py < 10:

            if grid[py, px] == 1:

                nearby.append(
                    (px, py)
                )

    return nearby


# --------------------------------------------------
# 8. INITIAL PATH
# --------------------------------------------------

current_position = start

path = a_star(
    current_position,
    goal
)

print()
print("Initial path:")
print(path)


# --------------------------------------------------
# 9. DISPLAY
# --------------------------------------------------

plt.figure(figsize=(9, 7))

plt.imshow(
    grid,
    cmap="gray_r"
)

plt.scatter(
    goal[0],
    goal[1],
    color="red",
    marker="*",
    s=300,
    label="Destination"
)

path_x = [p[0] for p in path]
path_y = [p[1] for p in path]

path_line, = plt.plot(
    path_x,
    path_y,
    linewidth=3,
    label="A* Path"
)

robot = plt.scatter(
    current_position[0],
    current_position[1],
    color="blue",
    s=180,
    label="Robot"
)

plt.title(
    "Autonomous Robot - Learning Based Navigation"
)

plt.xlabel("X Position")
plt.ylabel("Y Position")

plt.grid(True)
plt.legend()

plt.pause(1)


# --------------------------------------------------
# 10. ROBOT NAVIGATION
# --------------------------------------------------

replanned = False

step_number = 0

while current_position != goal:

    # Move along current path
    current_index = path.index(
        current_position
    )

    if current_index + 1 >= len(path):
        break

    next_position = path[
        current_index + 1
    ]

    current_position = next_position

    robot.set_offsets([
        current_position
    ])

    step_number += 1

    print(
        "Robot position:",
        current_position
    )


    # --------------------------------------------------
    # 11. CREATE A DYNAMIC OBSTACLE
    # --------------------------------------------------

    if (
        current_position == (1, 4)
        and not replanned
    ):

        dynamic_obstacle = (1, 5)

        print()
        print(
            "!!! DYNAMIC OBSTACLE APPEARED !!!"
        )

        print(
            "Obstacle position:",
            dynamic_obstacle
        )

        # Add obstacle to map
        grid[
            dynamic_obstacle[1],
            dynamic_obstacle[0]
        ] = 1

        # Display dynamic obstacle
        plt.scatter(
            dynamic_obstacle[0],
            dynamic_obstacle[1],
            color="orange",
            marker="X",
            s=220,
            label="Dynamic Obstacle"
        )

        plt.legend()

        # Check whether obstacle affects current route
        if dynamic_obstacle in path:

            print(
                "Current path is blocked."
            )

            # ------------------------------------------
            # NEW: ROBOT LEARNS FROM THE PROBLEM
            # ------------------------------------------

            print(
                "Robot learning problematic location:",
                dynamic_obstacle
            )

            record_problem_location(
                dynamic_obstacle
            )

            print(
                "Location saved to robot memory."
            )

            print(
                "Recalculating A* path..."
            )

            new_path = a_star(
                current_position,
                goal
            )

            if new_path:

                path = new_path

                print(
                    "New path found:"
                )

                print(path)

                # Draw new path
                new_x = [
                    p[0] for p in path
                ]

                new_y = [
                    p[1] for p in path
                ]

                path_line.remove()

                path_line, = plt.plot(
                    new_x,
                    new_y,
                    linewidth=3,
                    label="Replanned Path"
                )

                plt.legend()

                replanned = True

                print(
                    "Robot continuing on new path..."
                )

            else:

                print(
                    "No new path available."
                )

                record_failure()


    plt.pause(0.5)


# --------------------------------------------------
# 12. DELIVERY
# --------------------------------------------------

if current_position == goal:

    print()
    print("Destination reached!")
    print("Package delivered successfully.")

    # Save successful mission
    record_success()

    print(
        "Mission experience saved."
    )

    if replanned:

        print(
            "Dynamic obstacle was successfully avoided."
        )

else:

    print()
    print("Robot could not reach destination.")

    record_failure()


plt.show()