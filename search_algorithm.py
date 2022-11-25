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
        self.parent = None

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


def my_heuristic(next, goal):
    pass


def get_priority(algorithm, current_cell, next, goal):
    if algorithm == "BFS":
        return current_cell.g + 1
    elif algorithm == "DFS":
        return -current_cell.g - 1
    elif algorithm == "Random":
        return 0    # This value doesn't matter for random
    elif algorithm == "Greedy_Manhattan":
        return manhattan_distance(next, goal)
    elif algorithm == "Greedy_Euclidean":
        return euclidean_distance(next, goal)
    elif algorithm == "AStar_Manhattan":
        return current_cell.g + manhattan_distance(next, goal)
    elif algorithm == "AStar_Euclidean":
        return current_cell.g + euclidean_distance(next, goal)
    elif algorithm == "AStar_MyHeuristic":
        return current_cell.g + euclidean_distance(next, goal)

    else:
        print("Invalid algorithm")
        return -1


goals = []*2
current_goal = 0
def search(map_, start_value, goal_value, algorithm='BFS', info=None):
    global goals, current_goal

    # Make a copy of the map
    map = np.copy(map_)

    coord = np.where(map == start_value)
    start = cell(coord[1][0], coord[0][0])  # start cell
    coord = np.where(map == goal_value)
    goal = cell(coord[1][0], coord[0][0])  # goal cell

    if algorithm == "AStar_MyHeuristic":
        if start.y <= map_.shape[0] / 2:
            x, y = 5, info[1]
            while(map[y][x] != 0):
                y -= 1
            goals.append(cell(x, y))  # go up
        else:
            x, y = 5, info[0]
            while (map[y][x] != 0):
                y += 1
            goals.append(cell(x, y))  # go down
        goals.append(goal)
        goal = goals[current_goal]

    # New priority queue
    frontier = PriorityQueue()
    frontier.add(start, 0)  # add the start cell to the frontier

    # init. starting node
    start.g = 0
    nodes_expaned = 0

    # Start the timer
    start_time = timer()

    # if there is still nodes to open
    while not frontier.isEmpty():
        if algorithm != "Random":
            current_cell = frontier.remove()
        else:
            current_cell = frontier.remove_random()

        # check if the goal is reached
        if current_cell.x == goal.x and current_cell.y == goal.y:
            if algorithm == "AStar_MyHeuristic":
                if current_goal == 0:
                    current_goal = 1
                    goal = goals[current_goal]
                    frontier = PriorityQueue()
                    frontier.add(current_cell, 0)
                    continue
            break

        nodes_expaned += 1
        # for each neighbour of the current cell
        for next in get_neighbors(map, current_cell, goal_value):
            # compute priority for next cell
            priority = get_priority(algorithm, current_cell, next, goal)
            next.g = current_cell.g + 1 # This is the cost

            # update the cell value in the map (for visualization purposes)
            if map[next.y][next.x] != goal_value:
                map[next.y][next.x] = next.g

            # add next cell to open list
            frontier.add(next, priority)

            # add to path
            next.parent = current_cell

    # Stop the timer
    end_time = timer()

    # Figure out the path (backtracking)
    path = []
    while current_cell.parent is not None:
        path.append([current_cell.x, current_cell.y])
        current_cell = current_cell.parent
    path.append([start.x, start.y])

    # Convert path to numpy array
    path = np.array(path)
    cost = path.shape[0]

    return path, cost, map, nodes_expaned, (end_time - start_time) * 1000
