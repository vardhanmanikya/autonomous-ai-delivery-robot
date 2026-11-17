import csv
import os
import time
import statistics

from simulation.environment import (
    create_environment,
    get_start_position,
    get_goal_position
)

from simulation.robot import Robot

from navigation.astar import astar


# ============================================================
# SETTINGS
# ============================================================

NUMBER_OF_RUNS = 10

RESULT_FILE = "results/repeated_performance_results.csv"

os.makedirs("results", exist_ok=True)


# ============================================================
# RUN ONE SIMULATION
# ============================================================

def run_simulation(dynamic_obstacles):

    grid = create_environment()

    start = get_start_position()
    goal = get_goal_position()

    robot = Robot(start)

    # --------------------------------------------------------
    # Initial A* planning
    # --------------------------------------------------------

    start_time = time.perf_counter()

    path = astar(
        grid,
        start,
        goal
    )

    end_time = time.perf_counter()

    initial_time = (
        end_time - start_time
    ) * 1000

    if path is None:

        return {
            "initial_path": 0,
            "final_path": 0,
            "replans": 0,
            "moves": 0,
            "success": False,
            "planning_time": initial_time
        }

    initial_path_length = len(path) - 1

    current_path = path

    path_index = 0

    replanning_events = 0

    final_path_length = initial_path_length

    obstacle_index = 0

    total_planning_time = initial_time

    # --------------------------------------------------------
    # Navigation
    # --------------------------------------------------------

    while robot.position != goal:

        # Check for dynamic obstacle
        if obstacle_index < len(dynamic_obstacles):

            dynamic_obstacle = dynamic_obstacles[
                obstacle_index
            ]

            remaining_path = current_path[
                path_index + 1:
            ]

            if dynamic_obstacle in remaining_path:

                # Add obstacle
                grid[
                    dynamic_obstacle[0],
                    dynamic_obstacle[1]
                ] = 1

                # Re-plan
                replanning_start = time.perf_counter()

                new_path = astar(
                    grid,
                    robot.position,
                    goal
                )

                replanning_end = time.perf_counter()

                replanning_time = (
                    replanning_end -
                    replanning_start
                ) * 1000

                total_planning_time += replanning_time

                replanning_events += 1

                if new_path is None:

                    return {
                        "initial_path":
                            initial_path_length,
                        "final_path": 0,
                        "replans":
                            replanning_events,
                        "moves":
                            robot.total_moves,
                        "success": False,
                        "planning_time":
                            total_planning_time
                    }

                current_path = new_path

                path_index = 0

                final_path_length = (
                    len(new_path) - 1
                )

                obstacle_index += 1

                continue

        # Move robot
        if path_index + 1 >= len(current_path):

            break

        next_position = current_path[
            path_index + 1
        ]

        robot.move_to(next_position)

        path_index += 1

    # --------------------------------------------------------
    # Delivery
    # --------------------------------------------------------

    success = False

    if robot.position == goal:

        robot.deliver_package()

        success = robot.delivery_completed

    return {
        "initial_path":
            initial_path_length,
        "final_path":
            final_path_length,
        "replans":
            replanning_events,
        "moves":
            robot.total_moves,
        "success":
            success,
        "planning_time":
            total_planning_time
    }


# ============================================================
# SCENARIOS
# ============================================================

scenarios = [

    (
        "No Dynamic Obstacle",
        []
    ),

    (
        "One Dynamic Obstacle",
        [
            (4, 8)
        ]
    ),

    (
        "Multiple Dynamic Obstacles",
        [
            (4, 8),
            (6, 8)
        ]
    )
]


# ============================================================
# STORE RESULTS
# ============================================================

all_results = []


# ============================================================
# RUN 10 TIMES
# ============================================================

for scenario_name, obstacles in scenarios:

    print("\n==============================================")
    print("Scenario:", scenario_name)
    print("Runs:", NUMBER_OF_RUNS)
    print("==============================================")

    run_times = []
    run_paths = []
    run_final_paths = []
    run_replans = []
    run_moves = []
    successful_runs = 0

    for run_number in range(
        1,
        NUMBER_OF_RUNS + 1
    ):

        result = run_simulation(
            obstacles
        )

        run_times.append(
            result["planning_time"]
        )

        run_paths.append(
            result["initial_path"]
        )

        run_final_paths.append(
            result["final_path"]
        )

        run_replans.append(
            result["replans"]
        )

        run_moves.append(
            result["moves"]
        )

        if result["success"]:
            successful_runs += 1

        print(
            f"Run {run_number:02d} | "
            f"Time: "
            f"{result['planning_time']:.3f} ms | "
            f"Replans: "
            f"{result['replans']} | "
            f"Moves: "
            f"{result['moves']} | "
            f"Success: "
            f"{result['success']}"
        )

    # --------------------------------------------------------
    # Calculate averages
    # --------------------------------------------------------

    average_time = statistics.mean(
        run_times
    )

    average_path = statistics.mean(
        run_paths
    )

    average_final_path = statistics.mean(
        run_final_paths
    )

    average_replans = statistics.mean(
        run_replans
    )

    average_moves = statistics.mean(
        run_moves
    )

    success_rate = (
        successful_runs /
        NUMBER_OF_RUNS
    ) * 100

    print("\nAverage Results")

    print(
        "Average planning time:",
        f"{average_time:.3f} ms"
    )

    print(
        "Average initial path:",
        f"{average_path:.2f}"
    )

    print(
        "Average final path:",
        f"{average_final_path:.2f}"
    )

    print(
        "Average re-planning events:",
        f"{average_replans:.2f}"
    )

    print(
        "Average robot moves:",
        f"{average_moves:.2f}"
    )

    print(
        "Success rate:",
        f"{success_rate:.1f}%"
    )

    all_results.append({

        "Scenario":
            scenario_name,

        "Runs":
            NUMBER_OF_RUNS,

        "Average_Initial_Path":
            round(
                average_path,
                2
            ),

        "Average_Final_Path":
            round(
                average_final_path,
                2
            ),

        "Average_Replanning_Events":
            round(
                average_replans,
                2
            ),

        "Average_Robot_Moves":
            round(
                average_moves,
                2
            ),

        "Average_Planning_Time_ms":
            round(
                average_time,
                3
            ),

        "Successful_Runs":
            successful_runs,

        "Success_Rate_Percent":
            round(
                success_rate,
                1
            )
    })


# ============================================================
# SAVE CSV
# ============================================================

fieldnames = [
    "Scenario",
    "Runs",
    "Average_Initial_Path",
    "Average_Final_Path",
    "Average_Replanning_Events",
    "Average_Robot_Moves",
    "Average_Planning_Time_ms",
    "Successful_Runs",
    "Success_Rate_Percent"
]


with open(
    RESULT_FILE,
    "w",
    newline=""
) as file:

    writer = csv.DictWriter(
        file,
        fieldnames=fieldnames
    )

    writer.writeheader()

    writer.writerows(
        all_results
    )


# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n")
print("==============================================")
print("       REPEATED PERFORMANCE EVALUATION")
print("==============================================")

for result in all_results:

    print(
        f"\n{result['Scenario']}"
    )

    print(
        "Average planning time:",
        result[
            "Average_Planning_Time_ms"
        ],
        "ms"
    )

    print(
        "Average re-planning events:",
        result[
            "Average_Replanning_Events"
        ]
    )

    print(
        "Success rate:",
        result[
            "Success_Rate_Percent"
        ],
        "%"
    )


print("\nResults saved to:")

print(RESULT_FILE)

print(
    "\nRepeated evaluation completed successfully."
)