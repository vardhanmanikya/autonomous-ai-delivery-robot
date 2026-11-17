import heapq
from experience_memory import get_problem_locations


def heuristic(current, goal):
    """
    Manhattan distance between two grid cells.
    """
    return abs(current[0] - goal[0]) + abs(current[1] - goal[1])


def is_valid(grid, position):
    """
    Check whether a grid position is inside the map
    and is not an obstacle.
    """

    row, col = position

    return (
        0 <= row < grid.shape[0]
        and 0 <= col < grid.shape[1]
        and grid[row, col] == 0
    )


def astar(grid, start, goal, use_memory=True):
    """
    Find a path from start to goal using A*.

    The robot can use previous experience.
    Locations that caused problems in previous
    missions receive a higher navigation cost.

    Returns:
        A list of grid positions representing the path,
        or None if no path exists.
    """

    open_list = []

    heapq.heappush(
        open_list,
        (0, start)
    )

    # Load locations remembered from previous missions
    problem_locations = set()

    if use_memory:
        problem_locations = {
            tuple(location)
            for location in get_problem_locations()
        }

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

        # Four-direction movement
        neighbors = [
            (current[0] - 1, current[1]),
            (current[0] + 1, current[1]),
            (current[0], current[1] - 1),
            (current[0], current[1] + 1)
        ]

        for neighbor in neighbors:

            if not is_valid(grid, neighbor):
                continue

            # Normal movement cost
            movement_cost = 1

            # Learned locations receive a higher cost
            if neighbor in problem_locations:
                movement_cost += 5

            tentative_g = (
                g_score[current]
                + movement_cost
            )

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


def compare_routes(grid, start, goal):
    """
    Compare the shortest route with an alternative route.

    Returns a dictionary containing both paths.
    The grid is restored after testing each alternative.
    """

    # Calculate the shortest route without experience penalties
    shortest_path = astar(
        grid,
        start,
        goal,
        use_memory=False
    )

    if shortest_path is None:
        return {
            "shortest_path": None,
            "alternative_path": None
        }

    alternative_path = None

    # Try blocking each intermediate cell in the shortest route.
    # This encourages A* to find a different valid route.
    for position in shortest_path[1:-1]:

        row, col = position

        original_value = grid[row, col]

        try:
            grid[row, col] = 1

            candidate_path = astar(
                grid,
                start,
                goal,
                use_memory=False
            )

        finally:
            # Always restore the original grid cell.
            grid[row, col] = original_value

        if candidate_path is None:
            continue

        if candidate_path == shortest_path:
            continue

        if (
            alternative_path is None
            or len(candidate_path) < len(alternative_path)
        ):
            alternative_path = candidate_path

    return {
        "shortest_path": shortest_path,
        "alternative_path": alternative_path
    }