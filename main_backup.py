import time
import matplotlib.pyplot as plt

from simulation.environment import (
    create_environment,
    get_start_position,
    get_goal_position
)

from simulation.robot import Robot

from navigation.astar import astar

from perception.ai_detection import detect_obstacles


# ============================================================
# PROJECT START
# ============================================================

print("\n==============================================")
print("     AUTONOMOUS AI DELIVERY ROBOT")
print("==============================================")

print("\nStarting system...")


# ============================================================
# 1. CREATE ENVIRONMENT
# ============================================================

grid = create_environment()

start = get_start_position()
goal = get_goal_position()

robot = Robot(start)


print("\nSimulation Environment")
print("----------------------")
print("Grid size:", grid.shape)
print("Robot start:", start)
print("Destination:", goal)


# ============================================================
# 2. AI PERCEPTION
# ============================================================

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
# 3. INITIAL A* PATH
# ============================================================

path = astar(
    grid,
    start,
    goal
)


if path is None:

    print("\nERROR: No path found!")
    exit()


print("\nInitial A* Path")
print("----------------")

print("Path length:", len(path) - 1)


# ============================================================
# 4. VISUALIZATION
# ============================================================

plt.ion()

figure, axis = plt.subplots(
    figsize=(8, 8)
)


def draw_simulation():

    axis.clear()

    # Draw grid
    axis.imshow(
        grid,
        cmap="gray_r"
    )

    # Draw current path
    if path:

        rows = [p[0] for p in path]
        cols = [p[1] for p in path]

        axis.plot(
            cols,
            rows,
            marker="o",
            linewidth=3,
            label="A* Path"
        )

    # Robot
    axis.scatter(
        robot.position[1],
        robot.position[0],
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

    # AI dynamic obstacle
    dynamic_obstacle = (4, 8)

    if grid[
        dynamic_obstacle[0],
        dynamic_obstacle[1]
    ] == 1:

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
# 5. ROBOT NAVIGATION
# ============================================================

print("\nRobot starting navigation...")

path_index = 0
replanning_events = 0

dynamic_obstacle = (4, 8)

while robot.position != goal:

    # --------------------------------------------------------
    # Move to next position
    # --------------------------------------------------------

    if path_index + 1 >= len(path):
        break

    next_position = path[path_index + 1]

    robot.move_to(next_position)

    path_index += 1

    print(
        "Robot moved to",
        robot.position
    )

    draw_simulation()

    plt.pause(0.5)

    # --------------------------------------------------------
    # AI DYNAMIC OBSTACLE EVENT
    # --------------------------------------------------------

    if (
        robot.position == (1, 4)
        and grid[
            dynamic_obstacle[0],
            dynamic_obstacle[1]
        ] == 0
    ):

        print("\n--------------------------------")
        print("AI DYNAMIC OBSTACLE DETECTED!")
        print("--------------------------------")

        print(
            "Obstacle mapped to:",
            dynamic_obstacle
        )

        # Add obstacle
        grid[
            dynamic_obstacle[0],
            dynamic_obstacle[1]
        ] = 1

        # Check remaining path
        remaining_path = path[path_index:]

        if dynamic_obstacle in remaining_path:

            print("Current path is blocked.")

            print(
                "Starting A* re-planning..."
            )

            replanning_events += 1

            # Re-plan from robot's current position
            path = astar(
                grid,
                robot.position,
                goal
            )

            if path is None:

                print(
                    "ERROR: No alternative path!"
                )

                break

            # New path starts at robot's current position
            path_index = 0

            print(
                "New path generated."
            )

            print(
                "New path length:",
                len(path) - 1
            )

            draw_simulation()

            plt.pause(1)


# ============================================================
# 6. DELIVERY
# ============================================================

if robot.position == goal:

    robot.deliver_package()

    draw_simulation()

    plt.pause(1)

    print("\n================================")
    print("      DESTINATION REACHED!")
    print("================================")

    print("\nPackage delivered successfully!")

else:

    print("\nDelivery failed.")


# ============================================================
# 7. FINAL RESULTS
# ============================================================

print("\nPerformance Summary")
print("-------------------")

print(
    "Total robot moves:",
    robot.total_moves
)

print(
    "A* re-planning events:",
    replanning_events
)

print(
    "Final robot position:",
    robot.position
)

print(
    "Delivery status:",
    "SUCCESS"
    if robot.delivery_completed
    else "FAILED"
)


plt.ioff()

plt.show()