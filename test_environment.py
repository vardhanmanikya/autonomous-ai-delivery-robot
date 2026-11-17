from simulation.environment import (
    create_environment,
    get_start_position,
    get_goal_position
)


grid = create_environment()

start = get_start_position()
goal = get_goal_position()


print("Simulation Environment Test")
print("---------------------------")

print("Grid size:", grid.shape)

print("Robot start:", start)

print("Destination:", goal)

print("Number of obstacles:", int(grid.sum()))