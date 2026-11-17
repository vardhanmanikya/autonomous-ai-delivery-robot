import heapq
import time
import numpy as np


# ============================================================
# A* PATH PLANNING
# ============================================================

def heuristic(current, goal):
    return abs(current[0] - goal[0]) + abs(current[1] - goal[1])


def astar(grid, start, goal):

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

            row, col = neighbor

            if not (
                0 <= row < 10
                and 0 <= col < 10
            ):
                continue

            if grid[row, col] == 1:
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
# CREATE BASE ENVIRONMENT
# ============================================================

def create_grid():

    grid = np.zeros((10, 10))

    # Static obstacles
    grid[3:7, 4] = 1
    grid[6, 4:8] = 1

    return grid


# ============================================================
# RUN TEST
# ============================================================

def run_test(test_name, dynamic_obstacles):

    grid = create_grid()

    start = (1, 1)
    goal = (8, 8)

    # --------------------------------------------
    # Initial A* planning
    # --------------------------------------------

    planning_start = time.perf_counter()

    initial_path = astar(
        grid,
        start,
        goal
    )

    initial_time = (
        time.perf_counter()
        - planning_start
    )

    if initial_path is None:

        return {
            "test": test_name,
            "initial_path": 0,
            "final_path": 0,
            "replans": 0,
            "success": False,
            "planning_time": initial_time
        }

    initial_length = len(initial_path) - 1

    # --------------------------------------------
    # Add dynamic obstacles
    # --------------------------------------------

    replans = 0

    current_position = start

    current_path = initial_path

    for obstacle in dynamic_obstacles:

        grid[obstacle[0], obstacle[1]] = 1

        # Check whether obstacle blocks current path
        if obstacle in current_path:

            replans += 1

            replanning_start = time.perf_counter()

            new_path = astar(
                grid,
                current_position,
                goal
            )

            initial_time += (
                time.perf_counter()
                - replanning_start
            )

            if new_path is None:

                return {
                    "test": test_name,
                    "initial_path": initial_length,
                    "final_path": 0,
                    "replans": replans,
                    "success": False,
                    "planning_time": initial_time
                }

            current_path = new_path

    # --------------------------------------------
    # Final result
    # --------------------------------------------

    final_length = len(current_path) - 1

    success = (
        current_path[-1] == goal
    )

    return {
        "test": test_name,
        "initial_path": initial_length,
        "final_path": final_length,
        "replans": replans,
        "success": success,
        "planning_time": initial_time
    }


# ============================================================
# RUN EXPERIMENTS
# ============================================================

tests = [

    (
        "Test 1 - No Dynamic Obstacle",
        []
    ),

    (
        "Test 2 - One Dynamic Obstacle",
        [(4, 8)]
    ),

    (
        "Test 3 - Multiple Dynamic Obstacles",
        [(4, 8), (5, 8)]
    )
]


results = []


print("\n==============================================")
print(" AUTONOMOUS AI DELIVERY ROBOT")
print(" PERFORMANCE EVALUATION")
print("==============================================\n")


for test_name, obstacles in tests:

    result = run_test(
        test_name,
        obstacles
    )

    results.append(result)


# ============================================================
# DISPLAY RESULTS
# ============================================================

print(
    f"{'Test':<35}"
    f"{'Initial':<12}"
    f"{'Final':<12}"
    f"{'Replans':<10}"
    f"{'Success':<10}"
    f"{'Time (ms)':<12}"
)

print("-" * 91)


for result in results:

    print(
        f"{result['test']:<35}"
        f"{result['initial_path']:<12}"
        f"{result['final_path']:<12}"
        f"{result['replans']:<10}"
        f"{str(result['success']):<10}"
        f"{result['planning_time'] * 1000:<12.3f}"
    )


print("\nEvaluation completed successfully.")   