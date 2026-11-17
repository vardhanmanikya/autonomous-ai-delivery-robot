"""Autonomous AI delivery robot — three-scenario simulation."""

import argparse
import csv
import json
import os
import random
import tempfile
import time
from datetime import datetime

import matplotlib

parser = argparse.ArgumentParser(description="Run one delivery scenario")
parser.add_argument(
    "--scenario",
    choices=("random", "none", "one", "multiple"),
    default="random"
)
parser.add_argument("--status-file", default=None)
parser.add_argument("--headless", action="store_true")
args = parser.parse_args()

matplotlib.use("Agg" if args.headless else "TkAgg")
import matplotlib.pyplot as plt

from simulation.environment import (
    create_environment,
    get_start_position,
    get_goal_position
)
from simulation.robot import Robot
from navigation.astar import astar, compare_routes
from perception.ai_detection import detect_obstacles


APP_DIR = os.path.dirname(os.path.abspath(__file__))
STATUS_FILE = (
    os.path.abspath(args.status_file)
    if args.status_file
    else os.path.join(APP_DIR, "status.json")
)

route_comparison = {
    "shortest_route_steps": None,
    "alternative_route_steps": None,
    "extra_steps": None
}

shadow_position = (1, 1)
speed_mode = "NORMAL"
route_alert = "None"
delivery_confirmation = "Not delivered"
dynamic_obstacles = []
detected_objects = []
target_obstacle_count = 0
planning_time_ms = 0.0


def safe_write_status(status, status_file):
    """Write status JSON safely, retrying temporary Windows file locks."""

    directory = os.path.dirname(os.path.abspath(status_file))
    temp_path = None
    fd = None

    try:
        fd, temp_path = tempfile.mkstemp(
            prefix="robot_status_",
            suffix=".tmp",
            dir=directory
        )

        with os.fdopen(fd, "w", encoding="utf-8") as file:
            fd = None
            json.dump(status, file, indent=2)
            file.flush()
            os.fsync(file.fileno())

        delays = (0.05, 0.1, 0.2, 0.35, 0.5, 0.75)

        for attempt, delay in enumerate(delays):
            try:
                os.replace(temp_path, status_file)
                temp_path = None
                return True

            except PermissionError:
                if attempt == len(delays) - 1:
                    raise
                time.sleep(delay)

        return False

    except (OSError, TypeError, ValueError) as error:
        print(
            f"[STATUS WARNING] {error}",
            flush=True
        )
        return False

    finally:
        if fd is not None:
            try:
                os.close(fd)
            except OSError:
                pass

        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass


def timed_astar(grid, start, goal):
    """Run A* and measure planning time."""

    global planning_time_ms

    started = time.perf_counter()
    result = astar(grid, start, goal)

    planning_time_ms += (
        time.perf_counter() - started
    ) * 1000

    return result


def refresh_route_comparison(grid, start, goal):

    result = compare_routes(grid, start, goal)

    shortest = result.get("shortest_path")
    alternative = result.get("alternative_path")

    if not shortest:
        route_comparison.update(
            shortest_route_steps=None,
            alternative_route_steps=None,
            extra_steps=None
        )
        return

    shortest_steps = len(shortest) - 1
    alternative_steps = (
        len(alternative) - 1 if alternative else None
    )

    route_comparison.update(
        shortest_route_steps=shortest_steps,
        alternative_route_steps=alternative_steps,
        extra_steps=(
            alternative_steps - shortest_steps
            if alternative_steps is not None
            else None
        )
    )


def update_status(
    ai_status="READY",
    astar_status="READY",
    robot_status="IDLE",
    replanning_events=0,
    delivery_status="NOT STARTED",
    robot_position=(1, 1),
    path=None,
    obstacle_visible=False
):

    status = {
        "ai_status": ai_status,
        "astar_status": astar_status,
        "robot_status": robot_status,
        "replanning_events": replanning_events,
        "delivery_status": delivery_status,
        "robot_position": list(robot_position),
        "shadow_position": list(shadow_position),
        "speed_mode": speed_mode,
        "route_alert": route_alert,
        "delivery_confirmation": delivery_confirmation,
        "dynamic_obstacles": [
            list(point) for point in dynamic_obstacles
        ],
        "dynamic_obstacle_count": len(dynamic_obstacles),
        "dynamic_obstacle_target": target_obstacle_count,
        "scenario": scenario_name,
        "planning_time_ms": round(planning_time_ms, 4),
        "dynamic_obstacle": (
            list(dynamic_obstacles[0])
            if dynamic_obstacles else None
        ),
        "dynamic_obstacle_visible": bool(dynamic_obstacles),
        "detected_objects": detected_objects,
        "path": [
            list(point) for point in path
        ] if path else [],
        **route_comparison
    }

    safe_write_status(status, STATUS_FILE)


def valid_cells(grid, start, goal, current):

    rows, cols = grid.shape

    return [
        (r, c)
        for r in range(rows)
        for c in range(cols)
        if grid[r, c] == 0
        and (r, c) not in {
            tuple(start),
            tuple(goal),
            tuple(current)
        }
    ]


def save_experiment_result():

    fields = [
        "timestamp",
        "scenario",
        "obstacle_target",
        "obstacles_spawned",
        "planning_time_ms",
        "replanning_events",
        "delivery_status"
    ]

    file_exists = os.path.isfile(EXPERIMENT_FILE)

    with open(
        EXPERIMENT_FILE,
        "a",
        newline="",
        encoding="utf-8"
    ) as result_file:

        writer = csv.DictWriter(
            result_file,
            fieldnames=fields
        )

        if not file_exists:
            writer.writeheader()

        writer.writerow({
            "timestamp": datetime.now().isoformat(
                timespec="seconds"
            ),
            "scenario": scenario_name,
            "obstacle_target": target_obstacle_count,
            "obstacles_spawned": len(dynamic_obstacles),
            "planning_time_ms": round(planning_time_ms, 4),
            "replanning_events": replanning_events,
            "delivery_status": (
                "SUCCESS" if robot.delivery_completed
                else "FAILED"
            )
        })

# --------------------------------------------------
# INITIALIZE SCENARIO
# --------------------------------------------------

scenario_name = args.scenario

if scenario_name == "random":
    scenario_name = random.choice(
        ("none", "one", "multiple")
    )

EXPERIMENT_FILE = os.path.join(
    APP_DIR,
    f"experiment_results_{scenario_name}.csv"
)

print(
    "\n=============================================="
    "\n     AUTONOMOUS AI DELIVERY ROBOT"
    "\n==============================================",
    flush=True
)

grid = create_environment()

start = tuple(get_start_position())
goal = tuple(get_goal_position())

robot = Robot(start)
shadow_position = start

replanning_events = 0

target_obstacle_count = {
    "none": 0,
    "one": 1,
    "multiple": random.randint(2, 6)
}[scenario_name]

obstacle_visible = False

path = timed_astar(grid, start, goal)

refresh_route_comparison(grid, start, goal)

shadow_path = list(path) if path else [start]

if not path:

    route_alert = (
        f"Help needed: no route from {start} to {goal}."
    )

    update_status(
        astar_status="FAILED",
        robot_status="STOPPED",
        delivery_status="FAILED",
        robot_position=start
    )

    raise SystemExit(1)


# --------------------------------------------------
# YOLO OBJECT DETECTION
# --------------------------------------------------

try:

    raw_detections = detect_obstacles("bus.jpg") or []

    detected_objects = [
        {
            "object": str(
                item.get("object", "Unknown")
            ),
            "confidence": float(
                item.get("confidence", 0.0)
            ),
            "position": list(
                item.get("position", [])
            )
        }
        for item in raw_detections
        if isinstance(item, dict)
    ]

except Exception as error:

    print(
        f"Vision model unavailable for this run: {error}",
        flush=True
    )


# --------------------------------------------------
# MATPLOTLIB DISPLAY
# --------------------------------------------------

if not args.headless:

    plt.ion()

    figure, axis = plt.subplots(
        figsize=(7, 7)
    )


def draw_simulation():

    if args.headless:
        return

    axis.clear()

    axis.imshow(
        grid,
        cmap="gray_r"
    )

    if path:

        axis.plot(
            [p[1] for p in path],
            [p[0] for p in path],
            marker="o",
            linewidth=3,
            label="A* Route"
        )

    for index, obstacle in enumerate(dynamic_obstacles):

        axis.scatter(
            obstacle[1],
            obstacle[0],
            color=(
                "orange" if index == 0
                else "darkorange"
            ),
            marker="X",
            s=250,
            label=f"Dynamic Obstacle {index + 1}"
        )

    axis.scatter(
        robot.position[1],
        robot.position[0],
        color="blue",
        s=180,
        label="Robot"
    )

    axis.scatter(
        goal[1],
        goal[0],
        color="red",
        marker="*",
        s=250,
        label="Destination"
    )

    axis.set_title(
        "Autonomous AI Delivery Robot"
    )

    axis.set_xticks(
        range(grid.shape[1])
    )

    axis.set_yticks(
        range(grid.shape[0])
    )

    axis.grid(True)

    axis.legend(
        loc="upper right"
    )

    figure.canvas.draw()
    figure.canvas.flush_events()


def simulation_pause(seconds):
    """Pause simulation while keeping updates visible."""

    if args.headless:
        time.sleep(seconds)
    else:
        plt.pause(seconds)


# --------------------------------------------------
# START DELIVERY
# --------------------------------------------------

update_status(
    ai_status="ACTIVE",
    astar_status="ACTIVE",
    robot_status="DELIVERING",
    delivery_status="IN PROGRESS",
    robot_position=robot.position,
    path=path
)

draw_simulation()

path_index = 0
moves_since_replan = 0

recent_positions = [
    tuple(robot.position)
]


# --------------------------------------------------
# ROBOT MOVEMENT AND DYNAMIC OBSTACLE HANDLING
# --------------------------------------------------

while robot.position != goal:

    if path_index + 1 >= len(path):
        break

    next_position = tuple(
        path[path_index + 1]
    )

    near_obstacle = any(
        grid[r, c] == 1
        and max(
            abs(r - next_position[0]),
            abs(c - next_position[1])
        ) <= 1
        for r in range(grid.shape[0])
        for c in range(grid.shape[1])
    )

    speed_mode = (
        "CAUTION — SLOW"
        if near_obstacle
        else "NORMAL"
    )

    # Move robot one cell
    robot.move_to(next_position)

    recent_positions.append(
        tuple(robot.position)
    )

    path_index += 1
    moves_since_replan += 1

    shadow_index = min(
        getattr(robot, "total_moves", path_index),
        len(shadow_path) - 1
    )

    shadow_position = tuple(
        shadow_path[shadow_index]
    )

    # Decide whether another obstacle should appear
    spawn_due = (
        len(dynamic_obstacles) < target_obstacle_count
        and (
            not dynamic_obstacles
            or (
                replanning_events >= len(dynamic_obstacles)
                and moves_since_replan >= 2
            )
        )
    )

    if spawn_due:

        candidates = [
            tuple(point)
            for point in path[
                path_index + 2:path_index + 4
            ]
            if tuple(point) in valid_cells(
                grid,
                start,
                goal,
                robot.position
            )
        ]

        if candidates:

            dynamic_obstacle = random.choice(
                candidates
            )

            dynamic_obstacles.append(
                dynamic_obstacle
            )

            obstacle_visible = True

            grid[dynamic_obstacle] = 1

            blocked = (
                dynamic_obstacle
                in [
                    tuple(point)
                    for point in path[path_index + 1:]
                ]
            )

            force_backtrack = (
                blocked and random.random() < 0.30
            )

            update_status(
                ai_status="ACTIVE",
                astar_status="OBSTACLE DETECTED",
                robot_status="WAITING",
                replanning_events=replanning_events,
                delivery_status="IN PROGRESS",
                robot_position=robot.position,
                path=path,
                obstacle_visible=True
            )

            draw_simulation()
            simulation_pause(0.5)

            if blocked:

                replanning_events += 1

                if (
                    force_backtrack
                    and len(recent_positions) > 1
                ):

                    route_alert = (
                        "Route fully blocked. "
                        "Backing up one step to record "
                        "the obstacle and detour."
                    )

                    update_status(
                        ai_status="ACTIVE",
                        astar_status="ROUTE BLOCKED",
                        robot_status="BACKING UP",
                        replanning_events=replanning_events,
                        delivery_status="IN PROGRESS",
                        robot_position=robot.position,
                        path=path,
                        obstacle_visible=True
                    )

                    previous_safe_position = (
                        recent_positions[-2]
                    )

                    robot.move_to(
                        previous_safe_position
                    )

                    recent_positions.pop()

                    draw_simulation()
                    simulation_pause(0.5)

                    route_start = tuple(
                        robot.position
                    )

                else:

                    route_start = tuple(
                        robot.position
                    )

                update_status(
                    ai_status="ACTIVE",
                    astar_status="RE-PLANNING",
                    robot_status="WAITING",
                    replanning_events=replanning_events,
                    delivery_status="IN PROGRESS",
                    robot_position=robot.position,
                    path=path,
                    obstacle_visible=True
                )

                # Calculate a new route
                path = timed_astar(
                    grid,
                    route_start,
                    goal
                )

                refresh_route_comparison(
                    grid,
                    route_start,
                    goal
                )

                # If no route is found, try previous safe positions
                if not path:

                    route_alert = (
                        "No route ahead. Recording obstacle "
                        "and backing up to re-route."
                    )

                    safe_position = None
                    safe_path = None

                    for previous_position in reversed(
                        recent_positions[:-1]
                    ):

                        candidate_path = timed_astar(
                            grid,
                            previous_position,
                            goal
                        )

                        if candidate_path:

                            safe_position = previous_position
                            safe_path = candidate_path
                            break

                    if safe_position is None:

                        route_alert = (
                            f"No safe route found from "
                            f"recorded positions to {goal}."
                        )

                        update_status(
                            ai_status="ACTIVE",
                            astar_status="FAILED",
                            robot_status="STOPPED",
                            replanning_events=replanning_events,
                            delivery_status="FAILED",
                            robot_position=robot.position,
                            path=[],
                            obstacle_visible=True
                        )

                        break

                    update_status(
                        ai_status="ACTIVE",
                        astar_status="BACKTRACKING",
                        robot_status="BACKING UP",
                        replanning_events=replanning_events,
                        delivery_status="IN PROGRESS",
                        robot_position=robot.position,
                        path=path,
                        obstacle_visible=True
                    )

                    while (
                        tuple(robot.position)
                        != tuple(safe_position)
                    ):

                        previous = recent_positions[-2]

                        robot.move_to(previous)

                        recent_positions.pop()

                        update_status(
                            ai_status="ACTIVE",
                            astar_status="BACKTRACKING",
                            robot_status="BACKING UP",
                            replanning_events=replanning_events,
                            delivery_status="IN PROGRESS",
                            robot_position=robot.position,
                            path=path,
                            obstacle_visible=True
                        )

                        draw_simulation()
                        simulation_pause(0.35)

                    path = safe_path

                    refresh_route_comparison(
                        grid,
                        robot.position,
                        goal
                    )

                    route_alert = (
                        "Obstacle recorded. Route recalculated "
                        "from the previous safe position."
                    )

                    recent_positions = [
                        tuple(robot.position)
                    ]

                path_index = 0
                moves_since_replan = 0

    # Update dashboard after each robot movement
    update_status(
        ai_status="ACTIVE",
        astar_status="ACTIVE",
        robot_status="DELIVERING",
        replanning_events=replanning_events,
        delivery_status="IN PROGRESS",
        robot_position=robot.position,
        path=path,
        obstacle_visible=obstacle_visible
    )

    draw_simulation()

    simulation_pause(
        0.9 if near_obstacle else 0.5
    )


# --------------------------------------------------
# DELIVERY COMPLETION
# --------------------------------------------------

if tuple(robot.position) == tuple(goal):

    robot.deliver_package()

    delivery_confirmation = (
        f"Delivered {datetime.now().strftime('%H:%M:%S')} "
        f"at {robot.position}"
    )

    route_alert = "None"

    update_status(
        ai_status="ACTIVE",
        astar_status="ACTIVE",
        robot_status="COMPLETED",
        replanning_events=replanning_events,
        delivery_status="SUCCESS",
        robot_position=robot.position,
        path=path,
        obstacle_visible=obstacle_visible
    )

else:

    if route_alert == "None":

        route_alert = (
            "Delivery stopped before reaching the destination."
        )

    update_status(
        ai_status="ACTIVE",
        astar_status="FAILED",
        robot_status="STOPPED",
        replanning_events=replanning_events,
        delivery_status="FAILED",
        robot_position=robot.position,
        path=path,
        obstacle_visible=obstacle_visible
    )


# --------------------------------------------------
# SAVE EXPERIMENT RESULTS
# --------------------------------------------------

try:

    save_experiment_result()

except OSError as error:

    print(
        f"[EXPERIMENT WARNING] Could not save results: {error}",
        flush=True
    )


print(
    f"Delivery "
    f"{'SUCCESS' if robot.delivery_completed else 'FAILED'}; "
    f"moves={robot.total_moves}; "
    f"re-plans={replanning_events}",
    flush=True
)

draw_simulation()

if not args.headless:

    plt.ioff()
    plt.show()