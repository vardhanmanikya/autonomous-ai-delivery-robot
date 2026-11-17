import numpy as np


def create_environment():
    """
    Create the 10x10 indoor simulation grid.

    0 = free space
    1 = obstacle
    """

    grid = np.zeros((10, 10))

    # Static obstacles
    grid[3:7, 4] = 1
    grid[6, 4:8] = 1

    return grid


def get_start_position():
    """Return the robot's starting position."""

    return (1, 1)


def get_goal_position():
    """Return the delivery destination."""

    return (8, 8)