import heapq
import numpy as np
import matplotlib.pyplot as plt

from perception.ai_detection import detect_obstacles


# ============================================================
# 1. CREATE SIMULATION GRID
# ============================================================

grid = np.zeros((10, 10))


# Existing static obstacles
grid[3:7, 4] = 1
grid[6, 4:8] = 1


# Robot and destination
start = (1, 1)
goal = (8, 8)


# ============================================================
# 2. RUN YOLO AI DETECTION
# ============================================================

obstacles = detect_obstacles("bus.jpg")


# ============================================================
# 3. CONVERT AI DETECTIONS INTO GRID OBSTACLES
# ============================================================

for obstacle in obstacles:

    confidence = obstacle["confidence"]
    position = obstacle["position"]

    # Ignore low-confidence detections
    if confidence < 0.70:
        continue

    if position == "LEFT":
        row, col = 3, 4

    elif position == "CENTER":
        row, col = 4, 4

    else:
        row, col = 5, 4

    grid[row, col] = 1


print("\nAI Obstacles Added to Grid")
print("--------------------------")

for obstacle in obstacles:

    if obstacle["confidence"] >= 0.70:

        print(
            f"{obstacle['object']} | "
            f"Confidence: {obstacle['confidence']:.2f} | "
            f"Position: {obstacle['position']}"
        )


# ============================================================
# 4. A* HELPER FUNCTIONS
# ============================================================

def is_valid(position):

    row, col = position

    return (
        0 <= row < grid.shape[0]
        and 0 <= col < grid.shape[1]
        and grid[row, col] == 0
    )


def heuristic(current, goal):

    return abs(current[0] - goal[0]) + abs(current[1] - goal[1])


# ============================================================
# 5. A* PATH PLANNING
# ============================================================

def astar(start, goal):

    open_list = []

    heapq.heappush(
        open_list,
        (0, start)
    )

    came_from = {}

    g_score = {
        start: 0
    }

    while open_list:

        _, current = heapq.heappop(open_list)

        # Goal reached
        if current == goal:

            path = []

            while current in came_from:

                path.append(current)
                current = came_from[current]

            path.append(start)

            path.reverse()

            return path

        # Four possible movements
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
# 6. FIND PATH
# ============================================================

path = astar(start, goal)


if path is None:

    print("\nNo path found!")

else:

    print("\nA* Path Generated")
    print("-----------------")

    for position in path:

        print(position)

    print(f"\nTotal steps: {len(path) - 1}")


# ============================================================
# 7. VISUALIZE AI + A* RESULT
# ============================================================

plt.figure(figsize=(8, 8))

plt.imshow(
    grid,
    cmap="gray_r"
)


# Draw A* path
if path is not None:

    path_rows = [position[0] for position in path]
    path_cols = [position[1] for position in path]

    plt.plot(
        path_cols,
        path_rows,
        marker="o",
        linewidth=3,
        label="A* Path"
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


plt.title("AI-Based Obstacle Detection + A* Path Planning")

plt.xticks(range(10))
plt.yticks(range(10))

plt.grid(True)

plt.legend()

plt.show()  