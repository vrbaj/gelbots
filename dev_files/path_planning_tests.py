import random
import math
from matplotlib import pyplot as plt
import numpy as np
import skimage.draw


# STEP 1. PLACE DISKS AND TARGETS


AREA_SIZE = 1000
REPULSIVE_POTENTIAL = 500.0
ATTRACTIVE_POTENTIAL = 5.0
DISKS_COORDS = []
FORMATION_COORDS = [[500, 500], [500, 560], [560, 500], [560, 560]]
DISKS_N = 10
DISK_RADIUS = 30


class Path:
    def __init__(self, start, goal):
        self.start = start
        self.goal = goal
        self.visited_nodes = []
        self.length = 0


class Node:
    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position
        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.position == other.position


def construct_path(evaluated_node, env_map):
    ext_path = Path(None, None)
    path = []
    map_shape = np.shape(env_map)
    result = [[-1 for i in range(map_shape[1])] for j in range(map_shape[1])]
    actual_node = evaluated_node
    while actual_node is not None:
        path.append(actual_node.position)
        ext_path.visited_nodes.append(list(actual_node.position))
        actual_node = actual_node.parent
    path = path[::-1]
    start_value = 0
    for i in range(len(path)):
        result[path[i][0]][path[i][1]] = 50
        start_value += 1
    return path, ext_path


def distance(point1, point2):
    return math.sqrt(((point1[0] - point2[0]) ** 2) + (point1[1] - point2[1]) ** 2)


def a_star(env_map, start, goal, obstacles):
    # get size of image
    start_node = Node(None, tuple(start))
    start_node.g = start_node.h = start_node.f = 0
    goal_node = Node(None, tuple(goal))
    goal_node.g = goal_node.h = goal_node.f = 0
    env_map_size = np.shape(env_map)
    # possible moves on the image
    possible_moves = [[-1, -1],    # go NW
                      [-1, 0],     # go N
                      [-1, 1],     # NE
                      [0, -1],     # go W
                      [0, 1],      # go E
                      [1, -1],     # go SW
                      [1, 0],      # go S
                      [1, 1]]      # go SE
    # list with open nodes
    open_nodes = []
    # list with already visited nodes
    closed_nodes = []
    # starting node
    # start_node = Node(None, start)
    # goal node
    # goal_node = Node(None, goal)
    # insert starting node into open nodes list
    open_nodes.append(start_node)
    # while there are any open nodes, search
    while len(open_nodes) > 0:
        # expand best node
        current_node = open_nodes[0]
        current_index = 0
        for idx, node in enumerate(open_nodes):
            # find the most promising node from open nodes
            if node.f < current_node.f:
                current_node = node
                current_index = idx
        # remove the most promising node from open nodes list
        open_nodes.pop(current_index)
        # insert the most promising node to visited nodes list
        closed_nodes.append(current_node)
        # if the most promising node is the goal return the path
        if current_node == goal_node:
            print("Goal node: ", goal_node.position)
            return construct_path(node, env_map)
        # else get children of the node
        else:
            # list of successors nodes
            successor_nodes = []
            for position in possible_moves:
                # new possible position
                successor_position = current_node.position[0] + position[0], current_node.position[1] + position[1]
                # check the validity of new position
                if (successor_position[0] > (env_map_size[0] - 1) or
                    successor_position[0] < 0 or
                    successor_position[1] > (env_map_size[1] - 1) or
                        successor_position[1] < 0):
                    print("Invalid position")
                    continue
                # TODO check for obstacle
                collision = False
                for obstacle in obstacles:
                    if distance(obstacle, successor_position) < DISK_RADIUS * 2.05:
                        collision = True
                if collision:
                    continue
                # create new successor node
                new_successor = Node(current_node, successor_position)
                # append new successor node to successors list
                successor_nodes.append(new_successor)

            for successor_node in successor_nodes:
                if len([visited_successor for visited_successor in closed_nodes if visited_successor == successor_node]) > 0:
                    continue
                cost = distance(current_node.position, successor_node.position)
                successor_node.g = current_node.g + cost
                successor_node.h = ((successor_node.position[0] - goal_node.position[0]) ** 2 +
                                    (successor_node.position[1] - goal_node.position[1]) ** 2)
                successor_node.f = successor_node.g + successor_node.h
                if len([i for i in open_nodes if successor_node == i and successor_node.g > i.g]) > 0:
                    continue

                open_nodes.append(successor_node)
    return env_map


def disks_positions(n):
    coordinates_list = []
    for _ in range(n):
        coordinates_list.append([random.randint(DISK_RADIUS, AREA_SIZE - DISK_RADIUS),
                                 random.randint(DISK_RADIUS, AREA_SIZE - DISK_RADIUS)])
    overlap = True
    while overlap:
        overlap = False
        for idx, coordinates in enumerate(coordinates_list):
            for coordinates2 in coordinates_list[idx + 1:-1]:
                print("coordinates>", coordinates, " and ", coordinates2)
                if get_eucl_distance(coordinates, coordinates2) < DISK_RADIUS:
                    coordinates_list[idx] = [random.randint(DISK_RADIUS, AREA_SIZE - DISK_RADIUS),
                                             random.randint(DISK_RADIUS, AREA_SIZE - DISK_RADIUS)]

                    overlap = True

    return coordinates_list


def get_eucl_distance(a, b):
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)


def create_map(disks_coords, formation_coords, area_size):
    state_map = np.zeros((area_size, area_size))
    for disk in disks_coords:
        # state_map[disk[0], disk[1]] = 100
        rr, cc = skimage.draw.disk(tuple(disk), DISK_RADIUS)
        state_map[rr, cc] = 100
    for target in formation_coords:
        print(target)
        rr, cc, val = skimage.draw.circle_perimeter_aa(target[0], target[1], DISK_RADIUS)
        state_map[rr, cc] = 50
    return state_map


DISKS_COORDS = disks_positions(DISKS_N)
DISKS_COORDS = [[100, 100], [150, 150], [200, 300], [380, 400], [200, 220]]
map_graph = create_map(DISKS_COORDS, FORMATION_COORDS, AREA_SIZE)
fig = plt.figure()
ax = fig.add_subplot(111)
ax.pcolor(map_graph, vmax=100.0, cmap=plt.cm.hot)
ax.set_aspect(1)


# Evolution Strategy
POPULATION_SIZE = 9
population = []
targets = range(len(FORMATION_COORDS))
print(targets)

# STEP 1: GENERATE POPULATION
population = [[random.sample(targets, len(targets)),
               random.sample(targets, len(targets))] for _ in range(POPULATION_SIZE)]
print(population)

# maze = [[0,1,0,0,0,0],
#         [0,0,0,0,0,0],
#         [0,1,0,1,0,0],
#         [0,1,0,0,1,0],
#         [0,0,0,0,1,0]]
# start = [0, 0]
# end = [4, 5]
maze = map_graph
start = DISKS_COORDS[0]
end = FORMATION_COORDS[0]


path, ext_path = a_star(maze, start, end, DISKS_COORDS[1:])

# print(path)
fig = plt.figure(2)
ax = fig.add_subplot(111)
ax.pcolor(path)
ax.set_aspect(1)

fig = plt.figure(3)
ax = fig.add_subplot(111)
ax.pcolor(path + map_graph, cmap=plt.cm.hot)
ax.set_aspect(1)

for node in ext_path.visited_nodes:
    map_graph[node[0]][node[1]] = 100

for i in range(len(ext_path.visited_nodes) - 1):
    ext_path.length = ext_path.length + distance(ext_path.visited_nodes[i], ext_path.visited_nodes[i+1])


fig = plt.figure(4)
ax = fig.add_subplot(111)
ax.pcolor(map_graph, vmax=100.0, cmap=plt.cm.hot)
ax.set_aspect(1)
plt.show()

print("path length: ", ext_path.length)

# STEP 4. COMPUTE DISTANCE FOR FIRST DISK

# STEP 5. UPDATE DISK POSITIONS

# STEP 6. COMPUTE DISTANCE FOR NEXT DIST and repreat

# STEP 7. SUM ALL DISTANCES

# STEP 8. SELECT 1/3 BEST SOLUTIONS, CREATE RANDOMLY 1/3 SOLUTIONS AND MUTATE 1/3 BEST SOLUTIONS
# GO TO STEP 4. AND REPEAT UNTIL OPTIMIZED
