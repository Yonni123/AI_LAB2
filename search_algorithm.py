import numpy as np
import math
import heapq

# Priority Queue based on heapq
class PriorityQueue:
    def __init__(self):
        self.elements = []
    def isEmpty(self):
        return len(self.elements) == 0
    def add(self, item, priority):
        heapq.heappush(self.elements,(priority,item))
    def remove(self):
        return heapq.heappop(self.elements)[1]


class cell:
    def __init__(self, x, y, parent):
        self.x = x
        self.y = y
        self.parent = parent
        self.g = 0

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __lt__(self, other):
        return self.g < other.g

    def __gt__(self, other):
        return self.g > other.g


# An example of search algorithm, feel free to modify and implement the missing part
def get_neighbors(map, current_cell, goal=-3):
    neighbors = []

    # get the cell above the current cell (if it exists and is not an obstacle or already visited)
    if current_cell.y - 1 >= 0:
        if map[current_cell.y - 1][current_cell.x] == 0 or map[current_cell.y - 1][current_cell.x] == goal:
            neighbors.append(cell(current_cell.x, current_cell.y - 1, current_cell))

    # get the cell below the current cell (if it exists and is not an obstacle or already visited)
    if current_cell.y + 1 < map.shape[0]:
        if map[current_cell.y + 1][current_cell.x] == 0 or map[current_cell.y + 1][current_cell.x] == goal:
            neighbors.append(cell(current_cell.x, current_cell.y + 1, current_cell))

    # get the cell to the left of the current cell (if it exists and is not an obstacle or already visited)
    if current_cell.x - 1 >= 0:
        if map[current_cell.y][current_cell.x - 1] == 0 or map[current_cell.y][current_cell.x - 1] == goal:
            neighbors.append(cell(current_cell.x - 1, current_cell.y, current_cell))

    # get the cell to the right of the current cell (if it exists and is not an obstacle or already visited)
    if current_cell.x + 1 < map.shape[1]:
        if map[current_cell.y][current_cell.x + 1] == 0 or map[current_cell.y][current_cell.x + 1] == goal:
            neighbors.append(cell(current_cell.x + 1, current_cell.y, current_cell))

    return neighbors


def cost_function(algorithm, current_cell, next):
    if algorithm == "BFS":
        return current_cell.g + 1
    elif algorithm == "DFS":
        return current_cell.g - 1
    elif algorithm == "Random":
        return np.random.randint(100)

    return current_cell.g + 1


def start_cost(algorithm):
    if algorithm == "BFS":
        return 0
    elif algorithm == "DFS":
        return 100000
    elif algorithm == "Random":
        return np.random.randint(100)
    pass


def search(map_, start_value, goal, algorithm='BFS'):
    # Make a copy of the map
    map = np.copy(map_)

    coord = np.where(map == start_value)
    start = cell(coord[1][0], coord[0][0], None)    # start cell

    # cost moving to another cell
    moving_cost = 1

    # New priority queue
    frontier = PriorityQueue()
    priority = start_cost(algorithm)
    frontier.add(start, priority)  # add the start cell to the frontier

    # path taken
    came_from = {}

    # expanded list with cost value for each cell
    cost = {}

    # init. starting node
    start.parent = None
    start.g = priority

    # if there is still nodes to open
    while not frontier.isEmpty():
        current_cell = frontier.remove()
        current = map[current_cell.y][current_cell.x]

        # check if the goal is reached
        if current == goal:
            break

        # for each neighbour of the current cell
        # Implement get_neighbors function (return nodes to expand next)
        # (make sure you avoid repetitions!)
        a = get_neighbors(map, current_cell)
        for next in get_neighbors(map, current_cell, goal):

            # compute cost to reach next cell
            # Implement cost function
            cost = cost_function(algorithm, current_cell, next)
            next.g = cost

            # update the cell value in the map
            if map[next.y][next.x] != goal:
                map[next.y][next.x] = cost

            # add next cell to open list
            frontier.add(next, cost)
            
            # add to path
            came_from[next.x, next.y] = [current_cell.x, current_cell.y]

    # Figure out the path
    coord = np.where(map == goal)
    goal = cell(coord[1][0], coord[0][0], None)    # start cell
    path = []
    current = [goal.x, goal.y]
    while current != [start.x, start.y]:
        path.append(current)
        current = came_from[current[0], current[1]]
    path.append([start.x, start.y])

    # Convert path to numpy array
    path = np.array(path)

    # Fix the map values, so they range from 1 to max
    if algorithm == "DFS":
        # find min value that's above 0
        min_val = np.min(map[map > 0])
        map[map > 0] -= min_val - 1

    return path, cost, map
