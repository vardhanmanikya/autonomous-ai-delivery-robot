import heapq
import numpy as np
import matplotlib.pyplot as plt

from perception.ai_detection import detect_obstacles


# ============================================================
# 1. CREATE GRID
# ============================================================

grid = np.zeros((10, 10))

# Existing static obstacles
grid[3:7, 4] = 1
grid[6, 4:8] = 1

# Robot and destination
start = (1, 1)
goal = (8, 8)


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


def astar(start, goal):

    open_list = []

    heapq.heappush(open_list, (0, start))

    came_from = {}

    g_score = {
        start: 0
    }

    while open_list:

        _, current = heapq.heappop(open_list)

        if current == goal:

            path = []

            while current in came_from:

                path.append(current)
                current = came_from[current]

            path.append(start)
            path.reverse()

            return path

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
                    + heuristic(neighbor, goal)
                )

                heapq.heappush(
                    open_list,
                    (f_score, neighbor)
                )

    return None


# ============================================================
# 3. INITIAL A* PATH
# ============================================================

initial_path = astar(start, goal)

print("\nInitial A* Path")
print("----------------")

for position in initial_path:
    print(position)

print(f"\nInitial path steps: {len(initial_path) - 1}")


# ============================================================
# 4. RUN YOLO
# ============================================================

obstacles = detect_obstacles("bus.jpg")


print("\nYOLO AI Detection")
print("-----------------")

for obstacle in obstacles:

    print(
        f"{obstacle['object']} | "
        f"Confidence: {obstacle['confidence']:.2f} | "
        f"Position: {obstacle['position']}"
    )


# ============================================================
# 5. SIMULATE AI OBSTACLE APPEARING ON CURRENT PATH
# ============================================================

# For this simulation demonstration, we place the
# detected AI obstacle at (4, 8), which is directly
# on the initial A* path.

ai_obstacle = (4, 8)

grid[ai_obstacle[0], ai_obstacle[1]] = 1

print("\nAI Dynamic Obstacle Detected!")
print("-----------------------------")
print(f"Obstacle added at grid cell: {ai_obstacle}")


# ============================================================
# 6. CHECK WHETHER INITIAL PATH IS BLOCKED
# ============================================================

if ai_obstacle in initial_path:

    print("\nWARNING: Initial A* path is blocked!")

    print("Starting automatic re-planning...")

    new_path = astar(start, goal)

else:

    print("\nInitial path is still clear.")

    new_path = initial_path


# ============================================================
# 7. DISPLAY NEW PATH
# ============================================================

if new_path is None:

    print("\nNo alternative path found!")

else:

    print("\nReplanned A* Path")
    print("-----------------")

    for position in new_path:
        print(position)

    print(f"\nReplanned path steps: {len(new_path) - 1}")


# ============================================================
# 8. VISUALIZE RESULT
# ============================================================

plt.figure(figsize=(8, 8))

plt.imshow(
    grid,
    cmap="gray_r"
)


# Initial path
initial_rows = [p[0] for p in initial_path]
initial_cols = [p[1] for p in initial_path]

plt.plot(
    initial_cols,
    initial_rows,
    linestyle="--",
    marker="o",
    linewidth=2,
    label="Initial A* Path"
)


# Replanned path
if new_path is not None:

    new_rows = [p[0] for p in new_path]
    new_cols = [p[1] for p in new_path]

    plt.plot(
        new_cols,
        new_rows,
        marker="o",
        linewidth=3,
        label="Replanned A* Path"
    )


# AI dynamic obstacle
plt.scatter(
    ai_obstacle[1],
    ai_obstacle[0],
    color="orange",
    marker="X",
    s=250,
    label="AI Dynamic Obstacle"
)


# Robot
plt.scatter(
    start[1],
    start[0],
    color="blue",
    s=180,
    label="Robot"
)


# Destination
plt.scatter(
    goal[1],
    goal[0],
    color="red",
    marker="*",
    s=250,
    label="Destination"
)


plt.title(
    "AI-Based Dynamic Obstacle Detection and A* Re-planning"
)

plt.xticks(range(10))
plt.yticks(range(10))

plt.grid(True)

plt.legend()

plt.show()