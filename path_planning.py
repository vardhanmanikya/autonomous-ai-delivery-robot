import numpy as np
import heapq


# --------------------------------------------------
# 1. CREATE THE VIRTUAL MAP
# --------------------------------------------------

grid = np.zeros((10, 10))

# Add obstacles
grid[3:7, 4] = 1
grid[6, 4:8] = 1


# --------------------------------------------------
# 2. START AND DESTINATION
# --------------------------------------------------

start = (1, 1)
goal = (8, 8)


# --------------------------------------------------
# 3. POSSIBLE ROBOT MOVEMENTS
# --------------------------------------------------

movements = [
    (1, 0),    # Right
    (-1, 0),   # Left
    (0, 1),    # Down
    (0, -1)    # Up
]


# --------------------------------------------------
# 4. CHECK WHETHER A POSITION IS VALID
# --------------------------------------------------

def is_valid_position(position):

    x, y = position

    # Check map boundaries
    if x < 0 or x >= 10 or y < 0 or y >= 10:
        return False

    # Check obstacle
    if grid[y, x] == 1:
        return False

    return True


# --------------------------------------------------
# 5. HEURISTIC FUNCTION
# --------------------------------------------------

def heuristic(position, goal):

    distance_x = abs(position[0] - goal[0])
    distance_y = abs(position[1] - goal[1])

    return distance_x + distance_y


# --------------------------------------------------
# 6. A* PATH PLANNING
# --------------------------------------------------

def a_star(start, goal):

    # Priority queue
    open_list = []

    # Add starting position
    heapq.heappush(open_list, (0, start))

    # Store the previous position
    came_from = {}

    # Distance travelled so far
    g_cost = {start: 0}

    while open_list:

        # Get the position with the lowest cost
        current_f, current = heapq.heappop(open_list)

        # Check if destination reached
        if current == goal:

            path = []

            while current in came_from:

                path.append(current)
                current = came_from[current]

            path.append(start)

            path.reverse()

            return path

        # Check neighboring cells
        for movement in movements:

            new_x = current[0] + movement[0]
            new_y = current[1] + movement[1]

            neighbor = (new_x, new_y)

            # Skip invalid positions
            if not is_valid_position(neighbor):
                continue

            # Cost of moving to neighbor
            new_g_cost = g_cost[current] + 1

            # If this is a better route
            if neighbor not in g_cost or new_g_cost < g_cost[neighbor]:

                g_cost[neighbor] = new_g_cost

                h_cost = heuristic(neighbor, goal)

                f_cost = new_g_cost + h_cost

                # Save previous position
                came_from[neighbor] = current

                # Add to priority queue
                heapq.heappush(
                    open_list,
                    (f_cost, neighbor)
                )

    # No path found
    return None


# --------------------------------------------------
# 7. FIND THE PATH
# --------------------------------------------------

path = a_star(start, goal)


# --------------------------------------------------
# 8. DISPLAY THE RESULT
# --------------------------------------------------

print("Start:", start)
print("Goal:", goal)

if path:

    print()
    print("A* Path Found!")
    print("Path:")

    for position in path:
        print(position)

    print()
    print("Total steps:", len(path) - 1)

else:

    print("No path found.")