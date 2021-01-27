import random, math
from matplotlib import pyplot as plt
import numpy as np
import skimage.draw


# STEP 1. PLACE DISKS AND TARGETS


AREA_SIZE = 1000
REPULSIVE_POTENTIAL = 500.0
ATTRACTIVE_POTENTIAL = 5.0
DISKS_COORDS = []
FORMATION_COORDS = [[500, 500], [500, 560], [560, 500], [560, 560]]
DISKS_N = 4
DISK_RADIUS = 30


class Node:
    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position
        self.g = 0
        self.h = 0
        self.f = 0


def a_star(env_map, start, goal):
    open_nodes = []
    closed_nodes = []
    start_node = Node(None, start)
    goal_node = Node(None, goal)
    open_nodes.append(start_node)
    while len(open_nodes) > 0:
        # expand best node
        current_node = open_nodes[0]
        for idx, node in enumerate(open_nodes):
            if node.f < current_node.f:
                current_node = node
                current_index = idx
        open_nodes.pop(idx)
        closed_nodes.append(current_node)

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
                if get_eucl_distance(coordinates, coordinates2) < DISK_RADIUS:
                    coordinates_list[idx] = random.randint(DISK_RADIUS, AREA_SIZE - DISK_RADIUS)
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
        rr, cc, val = skimage.draw.circle_perimeter_aa(target[0],target[1], DISK_RADIUS)
        state_map[rr, cc] = 50
    return state_map


DISKS_COORDS = disks_positions(DISKS_N)
map_graph = create_map(DISKS_COORDS, FORMATION_COORDS, AREA_SIZE)
fig = plt.figure()
ax = fig.add_subplot(111)
ax.pcolor(map_graph, vmax=100.0, cmap=plt.cm.hot)
ax.set_aspect(1)
plt.show()

# Evolution Strategy
POPULATION_SIZE = 9
population = []
targets = range(len(FORMATION_COORDS))
print(targets)

# STEP 1: GENERATE POPULATION
population = [[random.sample(targets, len(targets)),
               random.sample(targets, len(targets))] for _ in range(POPULATION_SIZE)]
print(population)

# STEP 4. COMPUTE DISTANCE FOR FIRST DISK

# STEP 5. UPDATE DISK POSITIONS

# STEP 6. COMPUTE DISTANCE FOR NEXT DIST and repreat

# STEP 7. SUM ALL DISTANCES

# STEP 8. SELECT 1/3 BEST SOLUTIONS, CREATE RANDOMLY 1/3 SOLUTIONS AND MUTATE 1/3 BEST SOLUTIONS
# GO TO STEP 4. AND REPEAT UNTIL OPTIMIZED

