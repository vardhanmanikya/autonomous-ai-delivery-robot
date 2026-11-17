import csv
import os
import time

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

RESULT_FILE = "results/performance_results.csv"

os.makedirs("results", exist_ok=True)


# ============================================================
# RUN ONE EXPERIMENT
# ============================================================

def run_experiment(test_id, scenario, dynamic_obstacles):

    print("\n==============================================")
    print("Test:", test_id)
    print("Scenario:", scenario)
    print("==============================================")

    # --------------------------------------------------------
    # Create a fresh environment
    # --------------------------------------------------------

    grid = create_environment()

    start = get_start_position()
    goal = get_goal_position()

    robot = Robot(start)

    print("Start:", start)
    print("Goal:", goal)

    # --------------------------------------------------------
    # INITIAL A* PLANNING
    # --------------------------------------------------------

    start_time = time.perf_counter()

    path = astar(
        grid,
        start,
        goal
    )

    end_time = time.perf_counter()

    initial_planning_time = (
        end_time - start_time
    ) * 1000

    if path is None:

        print("ERROR: No initial path found.")

        return {
            "Test_ID": test_id,
            "Scenario": scenario,
            "Initial_Path_Length": 0,
            "Final_Path_Length": 0,
            "Replanning_Events": 0,
            "Total_Robot_Moves": 0,
            "Delivery_Status": "FAILED",
            "Planning_Time_ms": round(
                initial_planning_time,
                3
            )
        }

    initial_path_length = len(path) - 1

    print(
        "Initial path length:",
        initial_path_length
    )

    print(
        "Initial A* planning time:",
        round(initial_planning_time, 3),
        "ms"
    )

    # --------------------------------------------------------
    # NAVIGATION
    # --------------------------------------------------------

    current_path = path
    path_index = 0

    replanning_events = 0
    final_path_length = initial_path_length

    obstacle_index = 0

    while robot.position != goal:

        # ----------------------------------------------------
        # Check whether the next dynamic obstacle should appear
        # ----------------------------------------------------

        if obstacle_index < len(dynamic_obstacles):

            dynamic_obstacle = dynamic_obstacles[
                obstacle_index
            ]

            remaining_path = current_path[
                path_index + 1:
            ]

            if dynamic_obstacle in remaining_path:

                print(
                    "\nDynamic obstacle detected at:",
                    dynamic_obstacle
                )

                # Add obstacle to grid
                grid[
                    dynamic_obstacle[0],
                    dynamic_obstacle[1]
                ] = 1

                # ------------------------------------------------
                # Re-plan
                # ------------------------------------------------

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

                replanning_events += 1

                if new_path is None:

                    print(
                        "No alternative path found."
                    )

                    return {
                        "Test_ID": test_id,
                        "Scenario": scenario,
                        "Initial_Path_Length":
                            initial_path_length,
                        "Final_Path_Length":
                            0,
                        "Replanning_Events":
                            replanning_events,
                        "Total_Robot_Moves":
                            robot.total_moves,
                        "Delivery_Status":
                            "FAILED",
                        "Planning_Time_ms":
                            round(
                                initial_planning_time +
                                replanning_time,
                                3
                            )
                    }

                current_path = new_path
                path_index = 0

                final_path_length = (
                    len(new_path) - 1
                )

                print(
                    "Re-planning completed."
                )

                print(
                    "New path length:",
                    final_path_length
                )

                print(
                    "Re-planning time:",
                    round(
                        replanning_time,
                        3
                    ),
                    "ms"
                )

                obstacle_index += 1

                continue

        # ----------------------------------------------------
        # Move robot
        # ----------------------------------------------------

        if path_index + 1 >= len(current_path):

            break

        next_position = current_path[
            path_index + 1
        ]

        robot.move_to(next_position)

        path_index += 1

    # --------------------------------------------------------
    # DELIVERY
    # --------------------------------------------------------

    if robot.position == goal:

        robot.deliver_package()

        delivery_status = "SUCCESS"

    else:

        delivery_status = "FAILED"

    # --------------------------------------------------------
    # RESULTS
    # --------------------------------------------------------

    print("\nFinal position:", robot.position)

    print(
        "Total robot moves:",
        robot.total_moves
    )

    print(
        "Re-planning events:",
        replanning_events
    )

    print(
        "Delivery:",
        delivery_status
    )

    return {
        "Test_ID": test_id,
        "Scenario": scenario,
        "Initial_Path_Length":
            initial_path_length,
        "Final_Path_Length":
            final_path_length,
        "Replanning_Events":
            replanning_events,
        "Total_Robot_Moves":
            robot.total_moves,
        "Delivery_Status":
            delivery_status,
        "Planning_Time_ms":
            round(
                initial_planning_time,
                3
            )
    }


# ============================================================
# RUN ALL EXPERIMENTS
# ============================================================

results = []


# Test 1
results.append(
    run_experiment(
        1,
        "No Dynamic Obstacle",
        []
    )
)


# Test 2
results.append(
    run_experiment(
        2,
        "One Dynamic Obstacle",
        [
            (4, 8)
        ]
    )
)


# Test 3
results.append(
    run_experiment(
        3,
        "Multiple Dynamic Obstacles",
        [
            (4, 8),
            (6, 8)
        ]
    )
)


# ============================================================
# SAVE RESULTS
# ============================================================

fieldnames = [
    "Test_ID",
    "Scenario",
    "Initial_Path_Length",
    "Final_Path_Length",
    "Replanning_Events",
    "Total_Robot_Moves",
    "Delivery_Status",
    "Planning_Time_ms"
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

    writer.writerows(results)


# ============================================================
# DISPLAY FINAL RESULTS
# ============================================================

print("\n")
print("==============================================")
print("       FINAL PERFORMANCE RESULTS")
print("==============================================")

print()

for result in results:

    print(
        result["Test_ID"],
        "|",
        result["Scenario"],
        "| Initial:",
        result["Initial_Path_Length"],
        "| Final:",
        result["Final_Path_Length"],
        "| Replans:",
        result["Replanning_Events"],
        "| Moves:",
        result["Total_Robot_Moves"],
        "| Status:",
        result["Delivery_Status"],
        "| Time:",
        result["Planning_Time_ms"],
        "ms"
    )


print("\nResults saved to:")
print(RESULT_FILE)

print("\nPerformance measurement completed.")