import numpy as np
import heapq
from timeit import default_timer as timer


# Priority Queue based on heapq
class PriorityQueue:
    def __init__(self):
        self.elements = []

    def isEmpty(self):
        return len(self.elements) == 0

    def add(self, item, priority):
        heapq.heappush(self.elements, (priority, item))

    def remove(self):
        return heapq.heappop(self.elements)[1]

    def remove_random(self):
        # remove a random element from the queue
        element = self.elements.pop(np.random.randint(0, len(self.elements)))
        return element[1]


class cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
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
            neighbors.append(cell(current_cell.x, current_cell.y - 1))

    # get the cell below the current cell (if it exists and is not an obstacle or already visited)
    if current_cell.y + 1 < map.shape[0]:
        if map[current_cell.y + 1][current_cell.x] == 0 or map[current_cell.y + 1][current_cell.x] == goal:
            neighbors.append(cell(current_cell.x, current_cell.y + 1))

    # get the cell to the left of the current cell (if it exists and is not an obstacle or already visited)
    if current_cell.x - 1 >= 0:
        if map[current_cell.y][current_cell.x - 1] == 0 or map[current_cell.y][current_cell.x - 1] == goal:
            neighbors.append(cell(current_cell.x - 1, current_cell.y))

    # get the cell to the right of the current cell (if it exists and is not an obstacle or already visited)
    if current_cell.x + 1 < map.shape[1]:
        if map[current_cell.y][current_cell.x + 1] == 0 or map[current_cell.y][current_cell.x + 1] == goal:
            neighbors.append(cell(current_cell.x + 1, current_cell.y))

    return neighbors


def manhattan_distance(cell1, cell2):
    return abs(cell1.x - cell2.x) + abs(cell1.y - cell2.y)


def euclidean_distance(cell1, cell2):
    return np.sqrt((cell1.x - cell2.x) ** 2 + (cell1.y - cell2.y) ** 2)


def cost_function(algorithm, current_cell, next, start, goal):
    if algorithm == "BFS":
        return current_cell.g + 1
    elif algorithm == "DFS":
        return current_cell.g - 1
    elif algorithm == "Random":
        return current_cell.g + 1
    elif algorithm == "Greedy_Manhattan":
        return manhattan_distance(next, goal)
    elif algorithm == "Greedy_Euclidean":
        return euclidean_distance(next, goal)
    elif algorithm == "AStar_Manhattan":
        g = (current_cell.g - manhattan_distance(current_cell, goal))  # g(n) = g(n-1) - h(n-1)
        return g + 1 + manhattan_distance(next, goal)
    elif algorithm == "AStar_Euclidean":
        g = (current_cell.g - euclidean_distance(current_cell, goal))  # g(n) = g(n-1) - h(n-1)
        return g + 1 + euclidean_distance(next, goal)

    return current_cell.g + 1


def start_cost(algorithm, start, goal):
    if algorithm == "BFS":
        return 0
    elif algorithm == "DFS":
        return np.iinfo(np.int32).max-1
    elif algorithm == "Random":
        return 0
    elif algorithm == "Greedy_Manhattan":
        return 0
    elif algorithm == "Greedy_Euclidean":
        return 0
    elif algorithm == "AStar_Manhattan":
        return manhattan_distance(start, goal)
    elif algorithm == "AStar_Euclidean":
        return euclidean_distance(start, goal)
    pass


def update_map_value(map, current_cell, next, goal, cost, algorithm):
    if algorithm == "AStar_Manhattan":
        g = (current_cell.g - manhattan_distance(current_cell, goal))  # g(n) = g(n-1) - h(n-1)
        map[next.y][next.x] = g + 1
    elif algorithm == "AStar_Euclidean":
        g = (current_cell.g - euclidean_distance(current_cell, goal))  # g(n) = g(n-1) - h(n-1)
        map[next.y][next.x] = g + 1
    else:
        map[next.y][next.x] = cost


def search(map_, start_value, goal_value, algorithm='BFS'):
    # Make a copy of the map
    map = np.copy(map_)

    coord = np.where(map == start_value)
    start = cell(coord[1][0], coord[0][0])  # start cell
    coord = np.where(map == goal_value)
    goal = cell(coord[1][0], coord[0][0])  # goal cell

    # New priority queue
    frontier = PriorityQueue()
    priority = start_cost(algorithm, start, goal)
    frontier.add(start, priority)  # add the start cell to the frontier

    # path taken
    came_from = {}

    # init. starting node
    start.g = priority
    nodes_expaned = 0

    # Start the timer
    start_time = timer()

    # if there is still nodes to open
    while not frontier.isEmpty():
        if algorithm != "Random":
            current_cell = frontier.remove()
        else:
            current_cell = frontier.remove_random()

        current = map[current_cell.y][current_cell.x]

        # check if the goal is reached
        if current == goal_value:
            break

        nodes_expaned += 1
        # for each neighbour of the current cell
        # Implement get_neighbors function (return nodes to expand next)
        # (make sure you avoid repetitions!)
        for next in get_neighbors(map, current_cell, goal_value):

            # compute cost to reach next cell
            # Implement cost function
            cost = cost_function(algorithm, current_cell, next, start, goal)
            next.g = cost

            # update the cell value in the map (for visualization purposes)
            if map[next.y][next.x] != goal_value:
                update_map_value(map, current_cell, next, goal, cost, algorithm)

            # add next cell to open list
            frontier.add(next, cost)

            # add to path
            came_from[next.x, next.y] = [current_cell.x, current_cell.y]

    # Stop the timer
    end_time = timer()

    # Figure out the path (backtracking)
    coord = np.where(map == goal_value)
    goal_value = cell(coord[1][0], coord[0][0])  # start cell
    path = []
    current = [goal_value.x, goal_value.y]
    while current != [start.x, start.y]:
        path.append(current)
        current = came_from[current[0], current[1]]
    path.append([start.x, start.y])

    # Convert path to numpy array
    path = np.array(path)

    # Fix the map values, so they range from 1 to max (for visualization purposes)
    if algorithm == "DFS":
        # find min value that's above 0
        min_val = np.min(map[map > 0])
        map[map > 0] *= -1
        map[map > 0] -= min_val - 1
        map[map < -3] += np.iinfo(np.int32).max
    elif algorithm == "Greedy_Manhattan" or algorithm == "Greedy_Euclidean":
        max_val = np.max(map)
        map[map > 0] += 3
        map[map > 0] *= -1
        map[map < -3] += max_val + 4


    cost = path.shape[0]

    return path, cost, map, nodes_expaned, (end_time - start_time) * 1000
