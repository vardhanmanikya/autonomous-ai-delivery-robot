import heapq
import time
import numpy as np
import matplotlib.pyplot as plt

from perception.ai_detection import detect_obstacles


# ============================================================
# 1. CREATE SIMULATION GRID
# ============================================================

grid = np.zeros((10, 10))

# Static obstacles
grid[3:7, 4] = 1
grid[6, 4:8] = 1

# Robot and destination
start = (1, 1)
goal = (8, 8)

# Dynamic obstacle will appear later
dynamic_obstacle = (4, 8)


# ============================================================
# 2. A* FUNCTIONS
# ============================================================

def is_valid(position):

    row, col = position

    return (
        0 <= row < 10
        and 0 <= col < 10
        and grid[row, col] == 0
    )


def heuristic(current, goal):

    return abs(current[0] - goal[0]) + abs(current[1] - goal[1])


def astar(start_position, goal_position):

    open_list = []

    heapq.heappush(
        open_list,
        (0, start_position)
    )

    came_from = {}

    g_score = {
        start_position: 0
    }

    while open_list:

        _, current = heapq.heappop(open_list)

        # Goal reached
        if current == goal_position:

            path = []

            while current in came_from:

                path.append(current)
                current = came_from[current]

            path.append(start_position)
            path.reverse()

            return path

        # Four-direction movement
        neighbors = [
            (current[0] - 1, current[1]),
            (current[0] + 1, current[1]),
            (current[0], current[1] - 1),
            (current[0], current[1] + 1)
        ]

        for neighbor in neighbors:

            if not is_valid(neighbor):
                continue

            tentative_g = g_score[current] + 1

            if (
                neighbor not in g_score
                or tentative_g < g_score[neighbor]
            ):

                came_from[neighbor] = current
                g_score[neighbor] = tentative_g

                f_score = (
                    tentative_g
                    + heuristic(neighbor, goal_position)
                )

                heapq.heappush(
                    open_list,
                    (f_score, neighbor)
                )

    return None


# ============================================================
# 3. RUN YOLO AI PERCEPTION
# ============================================================

print("\n========================================")
print(" AUTONOMOUS AI DELIVERY ROBOT")
print("========================================")

print("\nRunning YOLO AI perception...")

obstacles = detect_obstacles("bus.jpg")

print("\nDetected Objects")
print("----------------")

for obstacle in obstacles:

    print(
        f"{obstacle['object']} | "
        f"Confidence: {obstacle['confidence']:.2f} | "
        f"Position: {obstacle['position']}"
    )


# ============================================================
# 4. INITIAL A* PATH
# ============================================================

current_position = start

path = astar(current_position, goal)

if path is None:

    print("\nNo initial path found!")
    exit()


print("\nInitial A* path generated.")
print(f"Initial path length: {len(path) - 1} steps")


# ============================================================
# 5. SET UP VISUALIZATION
# ============================================================

plt.ion()

figure, axis = plt.subplots(figsize=(8, 8))


def draw_environment(current_path, robot_position):

    axis.clear()

    axis.imshow(
        grid,
        cmap="gray_r"
    )

    # Draw current A* path
    if current_path:

        path_rows = [p[0] for p in current_path]
        path_cols = [p[1] for p in current_path]

        axis.plot(
            path_cols,
            path_rows,
            marker="o",
            linewidth=3,
            label="A* Path"
        )

    # Robot
    axis.scatter(
        robot_position[1],
        robot_position[0],
        color="blue",
        s=180,
        label="Robot"
    )

    # Destination
    axis.scatter(
        goal[1],
        goal[0],
        color="red",
        marker="*",
        s=250,
        label="Destination"
    )

    # Dynamic obstacle
    if grid[dynamic_obstacle[0], dynamic_obstacle[1]] == 1:

        axis.scatter(
            dynamic_obstacle[1],
            dynamic_obstacle[0],
            color="orange",
            marker="X",
            s=250,
            label="AI Dynamic Obstacle"
        )

    axis.set_title(
        "Autonomous AI Delivery Robot"
    )

    axis.set_xticks(range(10))
    axis.set_yticks(range(10))

    axis.grid(True)

    axis.legend()

    figure.canvas.draw()
    figure.canvas.flush_events()


# ============================================================
# 6. ROBOT AUTONOMOUS NAVIGATION
# ============================================================

replanning_count = 0
total_moves = 0

print("\nRobot starting navigation...")


path_index = 0

while current_position != goal:

    # --------------------------------------------------------
    # Move robot to next position
    # --------------------------------------------------------

    if path_index + 1 >= len(path):

        break

    next_position = path[path_index + 1]

    current_position = next_position

    path_index += 1
    total_moves += 1

    print(
        f"Robot moved to {current_position}"
    )

    draw_environment(
        path[path_index:],
        current_position
    )

    plt.pause(0.6)

    # --------------------------------------------------------
    # SIMULATE AI DYNAMIC OBSTACLE
    # --------------------------------------------------------

    # When robot reaches (1,4), an AI obstacle event occurs.
    if (
        current_position == (1, 4)
        and grid[dynamic_obstacle[0], dynamic_obstacle[1]] == 0
    ):

        print("\n----------------------------------------")
        print("AI DYNAMIC OBSTACLE DETECTED!")
        print("----------------------------------------")

        print(
            f"AI obstacle mapped to grid cell: "
            f"{dynamic_obstacle}"
        )

        # Add obstacle to simulation grid
        grid[
            dynamic_obstacle[0],
            dynamic_obstacle[1]
        ] = 1

        # Check whether current path is blocked
        remaining_path = path[path_index:]

        if dynamic_obstacle in remaining_path:

            print("Current path is blocked!")
            print("Starting automatic A* re-planning...")

            replanning_count += 1

            # Re-plan from current robot position
            new_path = astar(
                current_position,
                goal
            )

            if new_path is None:

                print("No alternative path found!")

                break

            # Replace current path
            path = new_path
            path_index = 0

            print(
                "New path generated successfully."
            )

            print(
                f"New path length: "
                f"{len(path) - 1} steps"
            )

            draw_environment(
                path,
                current_position
            )

            plt.pause(1.5)


# ============================================================
# 7. DELIVERY COMPLETED
# ============================================================

draw_environment(
    [goal],
    goal
)

plt.pause(1)

print("\n========================================")
print(" DESTINATION REACHED!")
print("========================================")

print("\n📦 Package delivered successfully!")

print("\nPerformance Summary")
print("-------------------")
print(f"Total robot moves: {total_moves}")
print(f"A* re-planning events: {replanning_count}")
print(f"Final robot position: {current_position}")

if current_position == goal:

    print("Delivery status: SUCCESS")

else:

    print("Delivery status: FAILED")


plt.ioff()

plt.show()