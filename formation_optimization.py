import random
import math
import numpy as np
# import skimage.draw
import copy


class Individual:
    def __init__(self, disk_order, goal_order):
        self.disk_order = disk_order
        self.goal_order = goal_order
        self.collisions = 99999

    def mutate(self):
        idx = range(len(self.disk_order))
        i1, i2 = random.sample(idx, 2)
        if bool(random.getrandbits(1)):
            self.disk_order[i1], self.disk_order[i2] = self.disk_order[i2], self.disk_order[i1]
        else:
            self.goal_order[i1], self.goal_order[i2] = self.goal_order[i2], self.goal_order[i1]
        self.collisions = 99999

    def __str__(self):
        return "Individual - disk order: " + str(self.disk_order) + ", goal order: " + str(self.goal_order) +\
               ", collisions: " + str(self.collisions)


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
    if len(path) > 1:
        for i in range(len(ext_path.visited_nodes) - 1):
            ext_path.length = ext_path.length + distance(ext_path.visited_nodes[i], ext_path.visited_nodes[i + 1])
    return ext_path


def distance(point1, point2):
    return math.sqrt(((point1[0] - point2[0]) ** 2) + (point1[1] - point2[1]) ** 2)


def a_star(env_map, start, goal, obstacles, disk_radius):
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
            return construct_path(current_node, env_map)
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
                collision = False
                for obstacle in obstacles:
                    if distance(obstacle, successor_position) < disk_radius * 1.999:
                        collision = True
                if collision:
                    continue
                # create new successor node
                new_successor = Node(current_node, successor_position)
                # append new successor node to successors list
                successor_nodes.append(new_successor)

            for successor_node in successor_nodes:
                if len([visited_successor for visited_successor in closed_nodes
                        if visited_successor == successor_node]) > 0:
                    continue
                cost = distance(current_node.position, successor_node.position)
                successor_node.g = current_node.g + cost
                successor_node.h = ((successor_node.position[0] - goal_node.position[0]) ** 2 +
                                    (successor_node.position[1] - goal_node.position[1]) ** 2)
                successor_node.f = successor_node.g + successor_node.h
                if len([i for i in open_nodes if successor_node == i and successor_node.g > i.g]) > 0:
                    continue

                open_nodes.append(successor_node)
    print("astar fail")
    return env_map


def disks_positions(n, disk_radius, area_size):
    coordinates_list = []
    for _ in range(n):
        coordinates_list.append([random.randint(disk_radius, area_size - disk_radius),
                                 random.randint(disk_radius, area_size - disk_radius)])
    overlap = True
    while overlap:
        overlap = False
        for idx, coordinates in enumerate(coordinates_list):
            for coordinates2 in coordinates_list[idx + 1:-1]:
                # print("coordinates>", coordinates, " and ", coordinates2)
                if get_eucl_distance(coordinates, coordinates2) < disk_radius:
                    coordinates_list[idx] = [random.randint(disk_radius, area_size - disk_radius),
                                             random.randint(disk_radius, area_size - disk_radius)]

                    overlap = True
    return coordinates_list


def get_eucl_distance(a, b):
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)


def create_map(disks_coords, formation_coords, area_size, disk_radius):
    state_map = []
    # state_map = np.zeros((area_size, area_size))
    # for disk in disks_coords:
    #     # state_map[disk[0], disk[1]] = 100
    #     rr, cc = skimage.draw.disk(tuple(disk), disk_radius)
    #     state_map[rr, cc] = 100
    # for target in formation_coords:
    #     print(target)
    #     rr, cc, val = skimage.draw.circle_perimeter_aa(target[0], target[1], disk_radius)
    #     state_map[rr, cc] = 50
    return state_map


def check_collision(start, goal, obstacle_list, required_distance):
    collisions_number = 0
    for obstacle in obstacle_list:
        if dist(start[0], start[1], goal[0], goal[1], obstacle[0], obstacle[1]) < required_distance:
            collisions_number += 1
    return collisions_number


def dist(x1, y1, x2, y2, x3, y3):  # x3,y3 is the point
    px = x2-x1
    py = y2-y1

    norm = px*px + py*py

    u = ((x3 - x1) * px + (y3 - y1) * py) / float(norm)

    if u > 1:
        u = 1
    elif u < 0:
        u = 0

    x = x1 + u * px
    y = y1 + u * py

    dx = x - x3
    dy = y - y3
    ed = (dx * dx + dy * dy) ** .5
    return ed


def optimize_formation(start_positions, target_positions, disk_radius):
    targets = range(len(target_positions))
    population_size = 30
    population = []
    for index in range(population_size):
        population.append(Individual(random.sample(targets, len(targets)), random.sample(targets, len(targets))))
    found_solution = False
    individual = None
    generation = -1
    while not found_solution:
        generation += 1
        for idx1, individual in enumerate(population):
            # path_len.append(0)
            obstacle_list = copy.deepcopy(start_positions)
            # print(idx1, " individual: ", individual)
            individual.collisions = 0
            for idx, disk in enumerate(individual.disk_order):
                obstacle_list.remove(start_positions[disk])
                start = start_positions[disk]
                goal = target_positions[individual.goal_order[idx]]
                # print("individual idx1: ", idx1, "start: ", start, "goal: ", goal)
                # path = a_star(map_graph, start, goal, obstacle_list)
                individual.collisions = individual.collisions + check_collision(start, goal, obstacle_list, disk_radius)
                obstacle_list.append(goal)
                # path_len[idx1] = path_len[idx1] + path.length
            if individual.collisions == 0:
                found_solution = True
                print(individual)
                break
            # print(individual)
        # SELECTION
        if not found_solution:
            population.sort(key=lambda x: x.collisions, reverse=False)
            next_generation = population[0:int(population_size / 3)]
            for individual in population[0:int(population_size / 3)]:
                individual.mutate()
                next_generation.append(individual)
                next_generation.append(
                    Individual(random.sample(targets, len(targets)), random.sample(targets, len(targets))))
            population = copy.deepcopy(next_generation)

    return individual.disk_order, individual.goal_order
