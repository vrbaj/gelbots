import math

import matplotlib.pyplot as plt

show_animation = False


class AStarPlanner:

    def __init__(self, area_x, area_y, obstacle_list, resolution, rr):

        self.resolution = resolution
        self.rr = rr
        self.min_x = area_x[0]
        self.min_y = area_y[0]
        self.max_x = area_x[1]
        self.max_y = area_y[1]
        self.obstacle_map = None
        self.x_width, self.y_width = 0, 0
        self.motion = self.get_motion_model()
        self.calc_obstacle_map(obstacle_list)

    class Node:
        def __init__(self, x, y, cost, parent_index):
            self.cost = cost
            self.x = x  # index of grid
            self.y = y  # index of grid
            self.parent_index = parent_index

    def planning(self, start, goal):
        start_node = self.Node(self.calc_xy_index(start[0], self.min_x),
                               self.calc_xy_index(start[1], self.min_y), 0.0, -1)
        goal_node = self.Node(self.calc_xy_index(goal[0], self.min_x),
                              self.calc_xy_index(goal[1], self.min_y), 0.0, -1)

        open_set, closed_set = dict(), dict()
        open_set[self.calc_grid_index(start_node)] = start_node

        while 1:
            if not open_set:
                print("Open set is empty and no goal was found")
                return None

            c_id = min(
                open_set,
                key=lambda o: open_set[o].cost + self.calc_heuristic(goal_node,
                                                                     open_set[o]))
            current = open_set[c_id]

            # show graph
            if show_animation:  # pragma: no cover
                plt.plot(self.calc_grid_position(current.x, self.min_x),
                         self.calc_grid_position(current.y, self.min_y), "xc")
                if len(closed_set.keys()) % 10 == 0:
                    plt.pause(0.001)

            if current.x == goal_node.x and current.y == goal_node.y:
                goal_node.parent_index = current.parent_index
                goal_node.cost = current.cost
                print("The goal was found with cost: ", goal_node.cost * self.resolution)
                break

            # Remove the item from the open set
            del open_set[c_id]

            # Add it to the closed set
            closed_set[c_id] = current

            # expand_grid search grid based on motion model
            for i, _ in enumerate(self.motion):
                node = self.Node(current.x + self.motion[i][0],
                                 current.y + self.motion[i][1],
                                 current.cost + self.motion[i][2], c_id)
                n_id = self.calc_grid_index(node)

                # If the node is not safe, do nothing
                if not self.verify_node(node):
                    continue

                if n_id in closed_set:
                    continue

                if n_id not in open_set:
                    open_set[n_id] = node  # discovered a new node
                else:
                    if open_set[n_id].cost > node.cost:
                        # This path is the best until now. record it
                        open_set[n_id] = node

        path = self.calc_final_path(goal_node, closed_set, start, goal)

        return path

    def calc_final_path(self, goal_node, closed_set, start, goal):
        # generate final course
        path = [[self.calc_grid_position(goal_node.x, self.min_x),
                 self.calc_grid_position(goal_node.y, self.min_y)]]
        path.insert(0, goal)
        parent_index = goal_node.parent_index
        while parent_index != -1:
            n = closed_set[parent_index]
            path.append([self.calc_grid_position(n.x, self.min_x), self.calc_grid_position(n.y, self.min_y)])
            parent_index = n.parent_index

        path.append(start)
        return path

    @staticmethod
    def calc_heuristic(n1, n2):
        w = 1.0  # weight of heuristic
        d = w * math.hypot(n1.x - n2.x, n1.y - n2.y)
        return d

    def calc_grid_position(self, index, min_position):
        # calculates position in the workspace from the index on the grid
        pos = index * self.resolution + min_position
        return pos

    def calc_xy_index(self, position, min_pos):
        # calculates position in the grid from the workspace position without grid
        return round((position - min_pos) / self.resolution)

    def calc_grid_index(self, node):
        # calculates unique index for each node in the grid
        return (node.y - self.min_y) * self.x_width + (node.x - self.min_x)

    def verify_node(self, node):
        px = self.calc_grid_position(node.x, self.min_x)
        py = self.calc_grid_position(node.y, self.min_y)

        if px < self.min_x:
            return False
        elif py < self.min_y:
            return False
        elif px >= self.max_x:
            return False
        elif py >= self.max_y:
            return False

        # collision check
        if self.obstacle_map[node.x][node.y]:
            return False

        return True

    def boundary(self):
        ox, oy = [], []
        for i in range(self.min_x, self.max_x):
            ox.append(i)
            oy.append(self.min_y)
        for i in range(self.min_y, self.max_y):
            ox.append(self.max_x)
            oy.append(i)
        for i in range(self.min_x, self.max_x):
            ox.append(i)
            oy.append(self.max_y)
        for i in range(self.min_y, self.max_y):
            ox.append(self.min_x)
            oy.append(i)
        if show_animation:
            plt.plot(ox, oy, ".k")

        return ox, oy

    def calc_obstacle_map(self, obstacle_list):

        ox, oy = self.boundary()

        self.x_width = round((self.max_x - self.min_x) / self.resolution)
        self.y_width = round((self.max_y - self.min_y) / self.resolution)

        self.obstacle_map = [[False for _ in range(self.y_width)]
                             for _ in range(self.x_width)]

        for ix in range(self.x_width):
            x = self.calc_grid_position(ix, self.min_x)
            for iy in range(self.y_width):
                y = self.calc_grid_position(iy, self.min_y)
                for iox, ioy in zip(ox, oy):
                    d = math.hypot(iox - x, ioy - y)
                    # condition for boundary
                    if d <= self.rr:
                        self.obstacle_map[ix][iy] = True
                        # lt.plot(x, y, "xr")
                        break
                for iox, ioy in obstacle_list:
                    d = math.hypot(iox - x, ioy - y)
                    # condition for obstacles
                    if d <= 2 * self.rr:
                        self.obstacle_map[ix][iy] = True
                        # plt.plot(x, y, "xr")
                        break

    @staticmethod
    def get_motion_model():
        # dx, dy, cost
        motion = [[1, 0, 1],
                  [0, 1, 1],
                  [-1, 0, 1],
                  [0, -1, 1],
                  [-1, -1, math.sqrt(2)],
                  [-1, 1, math.sqrt(2)],
                  [1, -1, math.sqrt(2)],
                  [1, 1, math.sqrt(2)]]
        return motion


def main():
    print('Commencing')
    area_x = [0, 60]
    area_y = [0, 60]
    # start and goal position
    start = [10, 10]
    goal = [50, 50]
    grid_size = 1.0
    robot_radius = 5.0

    # circle obstacles with centers

    obstacle_list = [
        (30, 20),
        (30, 40),
        (10, 50),
    ]

    polomer = int(robot_radius)
    circle_x = []
    circle_y = []
    for x, y in obstacle_list:
        for r in range(-polomer, polomer + 1):
            d = round(math.sqrt(polomer * polomer - r * r))
            left = x - d
            right = x + d
            top = y - d
            bottom = y + d
            circle_x.extend([left, right, x + r, x + r])
            circle_y.extend([y + r, y + r, top, bottom])

    if show_animation:  # pragma: no cover
        plt.plot(circle_x, circle_y, ".k")
        plt.plot(start[0], start[1], "og")
        plt.plot(goal[0], goal[1], "xb")
        plt.grid(True)
        plt.axis("equal")

    a_star = AStarPlanner(area_x, area_y, obstacle_list, grid_size, robot_radius)
    path = a_star.planning(start, goal)

    if path:
        # path.insert(0, goal)
        # path.append(start)
        if show_animation:  # pragma: no cover
            plt.plot([x for (x, y) in path], [y for (x, y) in path], "-r")
            plt.show()
    if show_animation:
        plt.show()


if __name__ == '__main__':
    main()
