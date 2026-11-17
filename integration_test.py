from simulation.environment import (
    create_environment,
    get_start_position,
    get_goal_position
)

from simulation.robot import Robot

from navigation.astar import astar


# Create environment
grid = create_environment()

# Get start and destination
start = get_start_position()
goal = get_goal_position()

# Create robot
robot = Robot(start)

# Calculate path
path = astar(
    grid,
    start,
    goal
)


print("\n================================")
print(" ROBOT NAVIGATION INTEGRATION")
print("================================")

print("\nStart:", start)
print("Destination:", goal)


if path is None:

    print("\nNo path found!")

else:

    print("\nA* path found.")
    print("Path length:", len(path) - 1)

    print("\nRobot navigation:")

    # Skip the first position because
    # the robot is already there.
    for position in path[1:]:

        robot.move_to(position)

        print(
            f"Robot moved to {robot.position}"
        )

    # Check destination
    if robot.position == goal:

        robot.deliver_package()

        print("\nDESTINATION REACHED!")
        print("Package delivered successfully.")

    else:

        print("\nDestination not reached.")


print("\nFinal Robot Status")
print("------------------")
print(robot.get_status())