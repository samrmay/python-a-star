import pygame
import pygame.mouse
import pygame.freetype
import os
import numpy
import math
import time
import datetime
import random


pygame.init()
#Config
margin = .5
width_base = 2
height_base = width_base
pos_base = [0,0]
grid_length = 300
screen_size = 800
start_ID = [0, 0]
end_ID = [grid_length - 1, grid_length - 1]
rest_period = 5
generate_visuals = False
#Clock config
clock = True
font = 'freestylescript'
time_font_size = 60
#Obstacle config
branch_holes = True
obstacle_mode = "random"

#Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (100, 100, 100)
DARK_GREY = (75, 75, 75)
BLUE = (0 ,100, 255)
GREEN = (0, 230, 0)
RED = (230, 0, 0)
PURPLE = (125, 0, 125)
LIGHT_PURPLE = (200, 0, 200)

#Define class "node", which will make up grid
class node:
    def __init__(self, ID, pos, width, height, screen):
        self.screen = screen
        self.pos = pos
        self.width = width
        self.height = height
        self.passable = True
        self.closed = False
        self.color = WHITE
        self.ID = ID
        self.neighbors = []
        self.f_cost = 0
        self.h_cost = 0
        self.g_cost = 0
        self.parent = []
        self.short_check = True
        #define function that will physically draw node
    def draw(self):
        pygame.draw.rect(self.screen, self.color, [self.pos[0], self.pos[1], self.width, self.height])

#Define line class
class line:
    def __init__(self, length, start_node, direction, grid):
        self.length = length
        self.start = start_node
        self.direction = direction
        self.grid = grid
        self.line_nodes = []
        self.line_children = []
    #Function that will draw line
    def draw(self):
        x_index = self.start.ID[0]
        y_index = self.start.ID[1]
        for node in range(self.length):
            try:
                self.grid[x_index][y_index].color = BLACK
                self.grid[x_index][y_index].passable = False
                self.line_nodes.extend([self.grid[x_index][y_index]])
                x_index += self.direction[0]
                y_index += self.direction[1]
                if generate_visuals:
                    update_display(node, self.grid)
            except IndexError:
                break
        update_display(self.line_nodes, self.grid)
        return self.grid

#Define chamber class for obstacle building
class chamber:
    def __init__(self, grid, width, length, start_node):
        self.width = width
        self.length = length
        self.children = []
        self.start = start_node
        self.grid = grid
    #Define recursive split function
    def split(self):
        #Pick random points to start walls to split chamber
        vert_start = random.randint(self.start.ID[0] + 1, (self.start.ID[0] + self.width - 2))
        hor_start = random.randint(self.start.ID[1] + 1, (self.start.ID[1] + self.length - 2))
        vert_node = self.grid[vert_start][self.start.ID[1]]
        hor_node = self.grid[self.start.ID[0]][hor_start]
        hor_line = line(self.width, hor_node, [1, 0], self.grid)
        vert_line = line(self.length, vert_node, [0, 1], self.grid)
        hor_line.draw()
        vert_line.draw()
        #Define left/right walls
        for node in hor_line.line_nodes:
            if node.ID[0] == vert_start:
                hor_div = node
                hor_div_index = hor_line.line_nodes.index(node)
        left_wall = hor_line.line_nodes[0 : hor_div_index]
        right_wall = hor_line.line_nodes[hor_div_index + 1 : self.width]
        #Define top/bottom walls
        for node in vert_line.line_nodes:
            if node.ID[1] == hor_start:
                vert_div = node
                vert_div_index = vert_line.line_nodes.index(node)
        top_wall = vert_line.line_nodes[0 : vert_div_index]
        bot_wall = vert_line.line_nodes[vert_div_index + 1 : self.length]
        #Pick random walls within which to place passages
        walls = [left_wall, right_wall, top_wall, bot_wall]
        pass_walls = random.sample(walls, 3)
        for wall in pass_walls:
            passage = random.choice(wall)
            passage.color = WHITE
            passage.passable = True
            update_display(passage, self.grid)
        #Define chamber children
        self.children.extend([
            chamber(self.grid, len(left_wall), len(top_wall), self.start),
            chamber(self.grid, len(right_wall), len(top_wall), self.grid[vert_node.ID[0] + 1][vert_node.ID[1]]),
            chamber(self.grid, len(right_wall), len(bot_wall), self.grid[vert_div.ID[0] + 1][vert_div.ID[1] + 1]),
            chamber(self.grid, len(left_wall), len(bot_wall), self.grid[hor_node.ID[0]][hor_node.ID[1] + 1])
            ])
        for child in self.children:
            if child.length < 3 or child.width < 3:
                pass
            else:
                child.split()
        return self.grid

    #Define squares obstacle function
    def squares(self):
        #Create square around defined chamber
        left_corner = self.grid[self.start.ID[0] - 1][self.start.ID[1] - 1]
        top_line = line(self.width + 2, left_corner, [1, 0], self.grid)
        left_line = line(self.length + 2, left_corner, [0, 1], self.grid)
        right_corner = self.grid[left_corner.ID[0] + self.width + 1][left_corner.ID[1] + self.length + 1]
        bot_line = line(self.width + 2, right_corner, [-1, 0], self.grid)
        right_line = line(self.length + 2, right_corner, [0, -1], self.grid)
        square = [top_line, left_line, right_line, bot_line]
        for side in square:
            side.draw()
        #Block top right and bottom left corner of square
        top_right_corner = self.grid[left_corner.ID[0] + self.width + 1][left_corner.ID[1]]
        bot_left_corner = self.grid[left_corner.ID[0]][left_corner.ID[1] + self.length + 1]
        corner_blockers = [
            self.grid[top_right_corner.ID[0] + 1][top_right_corner.ID[1]],
            self.grid[top_right_corner.ID[0] + 1][top_right_corner.ID[1] - 1],
            self.grid[top_right_corner.ID[0]][top_right_corner.ID[1] - 1],
            self.grid[bot_left_corner.ID[0] - 1][bot_left_corner.ID[1]],
            self.grid[bot_left_corner.ID[0] - 1][bot_left_corner.ID[1] + 1],
            self.grid[bot_left_corner.ID[0]][bot_left_corner.ID[1] + 1]
        ]
        for block in corner_blockers:
            block.color = BLACK
            block.passable = False
        #Put passages in all sides
        pass_sides = random.sample(square, 3)
        for side in pass_sides:
            passage = random.choice(side.line_nodes[2 : len(side.line_nodes) - 2])
            passage.color = WHITE
            passage.passable = True
        #Define smaller chamber inside of this one
        baby_chamber = chamber(self.grid, self.width - 4, self.length - 4, self.grid[self.start.ID[0] + 2][self.start.ID[1] + 2])
        #Call squares function again if chamber is large enough
        if baby_chamber.length < 3 or baby_chamber.width < 3:
            #If chamber is too small, create center of maze
            center = [
                self.grid[baby_chamber.start.ID[0]][baby_chamber.start.ID[1]],
                self.grid[baby_chamber.start.ID[0] + 1][baby_chamber.start.ID[1] + 1],
                self.grid[baby_chamber.start.ID[0]][baby_chamber.start.ID[1] + 1],
                self.grid[baby_chamber.start.ID[0] + 1][baby_chamber.start.ID[1]]
            ]
            for node in center:
                node.color = BLACK
                node.passable = False
        else:
            baby_chamber.squares()
        return self.grid

#Function to get game events
def get_events(cont_find):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        #Function to execute pathfinding algorithm
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            cont_find = not cont_find
    return cont_find

#Define a distance function for A* pathfinding
def distance_fcn(point1, point2):
    x_dis = point2[0] - point1[0]
    y_dis = point2[1] - point1[1]
    return math.sqrt((x_dis**2) + (y_dis**2))

#Function to define grid given parameters
def define_grid(pos, width, height, grid_length, margin, screen):
    grid = []
    pos_x = pos[0]
    pos_y = pos[1]
    pos_x += margin
    pos_y += margin
    pos_start = [pos_x, pos_y]
    #initiate grid
    for x in range(grid_length):
        grid.extend([[]])
        for y in range(grid_length):
            grid[x].extend([y])
    #Define position for each node
    for column in range(grid_length):
        pos_y  = pos_start[1]
        for row in range(grid_length):
            pos = [pos_x,pos_y]
            node_loop = node([column,row], pos, width, height, screen)
            grid[column][row] = node_loop
            pos_y += (height + margin)
        pos_x += (width + margin)
    #Define neighbors for each node
    for column in range(len(grid)):
        for row in range(len(grid[0])):
            loop_node = grid[column][row]
            #Define ranges for which to find neighbors
            if column == 0:
                col_range = range(0, (loop_node.ID[0] + 2))
            elif column == (len(grid) - 1):
                col_range = range((loop_node.ID[0] - 1), len(grid))
            else:
                col_range = range((loop_node.ID[0] - 1), (loop_node.ID[0] + 2))
            for col in col_range:
                if row == 0:
                    row_range = range(0, (loop_node.ID[1] + 2))
                elif row == (len(grid[column]) - 1):
                    row_range = range((loop_node.ID[1] - 1), len(grid[column]))
                else:
                    row_range = range((loop_node.ID[1] - 1), (loop_node.ID[1] + 2))
                for row_ in row_range:
                    if [col,row_] != [column,row]:
                        loop_node.neighbors += [grid[col][row_]]
    return grid

#Flatten nodes in grid into a list
def define_all_nodes(grid):
    all_nodes = []
    for col in grid:
        for node_loop in col:
            all_nodes.append(node_loop)
    return all_nodes

#Define draw grid function
def draw_grid(nodes, grid):
    if isinstance(nodes, list):
        for node in nodes:
            try:
                grid[node.ID[0]][node.ID[1]].draw()
            except TypeError:
                pass
    else:
        try:
            grid[nodes.ID[0]][nodes.ID[1]].draw()
        except TypeError:
            pass
    
#Define update display function
def update_display(nodes, grid):
    draw_grid(nodes, grid)
    if clock:
        display_time()
    new_cont_find = get_events(cont_find)
    pygame.display.update()
    return new_cont_find

#Function for the A* algorithm
def A_star(grid, start, end):
    open_nodes = [start]
    astar_running = True
    start_pos = start.pos
    end_pos = end.pos
    #Define Hcost, Fcost, and Gcost for each node in the grid
    for col in range(len(grid)):
        for row in range(len(grid[0])):
            loop_node = grid[col][row]
            loop_node.g_cost = math.sqrt(((start_pos[0] - loop_node.pos[0])**2) + ((start_pos[1] - loop_node.pos[1])**2))
            loop_node.h_cost = math.sqrt(((end_pos[0] - loop_node.pos[0])**2) + ((end_pos[1] - loop_node.pos[1])**2))
            loop_node.f_cost = loop_node.g_cost + loop_node.h_cost
    #Start of A* algorithm
    while astar_running:
        #Find open node with the lowest f cost
        lowest_f = open_nodes[0].f_cost
        for node in open_nodes:
            loop_f = node.f_cost
            if loop_f <= lowest_f:
                current = node
                lowest_f = loop_f
        #Remove current node from open, add to closed
        open_nodes.remove(current)
        current.closed = True
        #If current node is end node, then end function
        if current.pos == end.pos:
            astar_running = False
            path = []
            path_running = True
            path_leader = end
            while path_running:
                path.extend([path_leader])
                if path_leader.pos == start.pos:
                    path_running = False
                else:
                    path_leader = path_leader.parent
            path.reverse()
            return path
        #Find open neighbors and add to open
        for neighbor in current.neighbors:
            in_open = False
            if not neighbor.passable or neighbor.closed:
                pass
            else:
                #If current node has a lower g_cost than neighbor's parent, make current neighbor's parent
                if neighbor.parent != []:
                    if neighbor.parent.f_cost > current.f_cost:
                        neighbor.parent = current
                elif neighbor.parent == []:
                    neighbor.parent = current
                for node in open_nodes:
                    if node.pos == neighbor.pos:
                        in_open = True
                    elif node.pos != neighbor.pos:
                        pass
                if not in_open:
                    #Add neighbor to open_nodes and redefine f_cost
                    neighbor.g_cost = neighbor.parent.g_cost + (distance_fcn(neighbor.pos, current.pos))
                    neighbor.f_cost = neighbor.h_cost + neighbor.g_cost
                    open_nodes.extend([neighbor])

#Function to draw path and fix diagonals
def draw_path(grid, path):
    for node in path:
        grid[node.ID[0]][node.ID[1]].color = BLUE
        update_display(node, grid)
        time.sleep(.0001)
    #Shortcut loop
    for node in path:
        if node.short_check:
            i = path.index(node)
            future_path = path[i + 1:]
            shortcut = []
            short_found  = False
            for member in future_path:
                #Block if it is a horizontal shortcut
                if node.pos[1] == member.pos[1] and not short_found:
                    short_open = True
                    start_short = node.ID[0] + 1
                    end_short = member.ID[0] + 1
                    if start_short < end_short:
                        range_short = range(start_short, end_short)
                    else:
                        range_short = range(end_short, start_short)
                    #Loop to find proposed shortcut along row across columns
                    for column in range_short:
                        tile = grid[column][node.ID[1]]
                        shortcut.extend([tile])
                    #Check if shortcut is passable
                    for tile in shortcut:
                        if not tile.passable or tile.color == BLACK:
                            short_open = False
                    #If shortcut is passable, mark original path as defunct, color white, and color shortcut as Blue
                    if short_open and len(shortcut) != 0:
                        old_path = []
                        for tile in shortcut:
                            j = shortcut.index(tile)
                            grid[tile.ID[0]][tile.ID[1]].color = BLUE
                            path[i + j].short_check = False
                            old_path_node = path[i + j]
                            old_path.append(old_path_node)
                            grid[old_path_node.ID[0]][old_path_node.ID[1]].color = WHITE
                            if generate_visuals:
                                time.sleep(.001)
                                update_display(tile, grid)
                        grid[node.ID[0]][node.ID[1]].color = BLUE
                        shortcut.append(node)
                        short_found = True
                #Verticle block
                elif node.pos[0] == member.pos[0] and not short_found:
                    short_open = True
                    start_short = node.ID[1] + 1
                    end_short = member.ID[1] + 1
                    if start_short < end_short:
                        range_short = range(start_short, end_short)
                    else:
                        range_short = range(end_short, start_short)
                    #Loop to find proposed shortcut along column across rows
                    for row in range_short:
                        tile = grid[node.ID[0]][row]
                        shortcut.extend([tile])
                    #Check if shortcut is passable
                    for tile in shortcut:
                        if not tile.passable or tile.color == BLACK:
                            short_open = False
                    #If shortcut is passable, mark original path as defunct, color white, and color shortcut as Blue
                    if short_open and len(shortcut) != 0:
                        old_path = []
                        for tile in shortcut:
                            j = shortcut.index(tile)
                            grid[tile.ID[0]][tile.ID[1]].color = BLUE
                            path[i + j].short_check = False
                            old_path_node = path[i + j]
                            old_path.append(old_path_node)
                            grid[old_path_node.ID[0]][old_path_node.ID[1]].color = WHITE
                            if generate_visuals:
                                time.sleep(.001)
                                update_display(tile, grid)
                        grid[node.ID[0]][node.ID[1]].color = BLUE
                        short_found = True
    update_display(all_nodes, grid)
    return grid

#Define function to convert to integer
def integer(input):
    return int(round(input))

#Recursive function to draw branch-like obstacle set
def obstacle_branch(grid, seed_line):
    last_node = seed_line.start
    #Define children for seed line
    for node in seed_line.line_nodes:
        if random.random() > 0.70 and abs(seed_line.line_nodes.index(node) - seed_line.line_nodes.index(last_node)) > 3:
            x = random.choice([1, -1])
            child_direction = [x*seed_line.direction[1], x*seed_line.direction[0]]
            child_length = random.randint(integer(seed_line.length/5), integer(seed_line.length/2))
            child = line(child_length, node, child_direction, grid)
            seed_line.line_children.extend([child])
            last_node = node
    #Draw children and restart recursive function for children
    for child in seed_line.line_children:
        child.draw()
        if child.length > 2 and branch_holes:
            hole = random.choice(child.line_nodes)
            hole.color = WHITE
            hole.passable = True
        if child.length < 2:
            return grid
        else:
            obstacle_branch(grid, child)

#Function to define reverse path obstacle method
def rev_path(grid, start, end, scatter):
    for col in grid:
        for row in col:
            row.color = BLACK
            row.passable = False
    update_display(all_nodes, grid)
    current = end
    start_found = False
    open_set = []
    time_out = 0
    while not start_found:
        current.color = WHITE
        current.passable = True
        update_display(current, grid)
        open_set.append(current)
        options = []
        time_out += 1
        if current.ID == start.ID:
            start_found = True
        for option in current.neighbors:
            op_neighbor_cnt = 0
            if (option.ID[0] == current.ID[0] or option.ID[1] == current.ID[1]) and not option.passable:
                for op_neighbor in option.neighbors:
                    if op_neighbor.passable:
                        op_neighbor_cnt += 1
                if op_neighbor_cnt < scatter:
                    options.append(option)
        if options:
            current = random.choice(options)
            time_out = 0
        else:
            current = open_set[open_set.index(current) - 1]
        if time_out > len(open_set)/16:
            break
    print(len(open_set))
    return grid

#Function to decide obstacle set and draw obstacles
def draw_obstacles(grid, start, end):
    #Pick which obstacle will be built
    if obstacle_mode == 'random':
        obstacle_set = random.randint(1, 4)
    elif obstacle_mode == 'chamber':
        obstacle_set = 1
    elif obstacle_mode == 'branch':
        obstacle_set = 0
    elif obstacle_mode == 'squares':
        obstacle_set = 2
    elif obstacle_mode == 'reverse':
        obstacle_set = 3
    elif obstacle_mode == 'reverse_scatter':
        obstacle_set = 4
    else:
        obstacle_set = random.randint(0, 4)
    #Start obstacle building block depending on setting
    if obstacle_set == 0:
        #Define initial trunk of branch obstacle
        seed_length = random.randint(integer(3*len(grid)/4), len(grid) - 1)
        seed_dir = random.choice([[0, 1], [1, 0]])
        if seed_dir == [0, 1]:
            seed_y = random.choice([0, len(grid[0]) - 1])
            if seed_y != 0:
                seed_dir = [0, -1]
            seed_x = random.randint(integer(len(grid)/3), integer((2*len(grid))/3))
            seed_start = grid[seed_x][seed_y]
            seed_line = line(seed_length, seed_start, seed_dir, grid)
        else:
            seed_x = random.choice([0, len(grid) - 1])
            if seed_x != 0:
                seed_dir = [-1, 0]
            seed_y = random.randint(integer(len(grid[0])/3), integer((2*len(grid))/3))
            seed_start = grid[seed_x][seed_y]
            seed_line = line(seed_length, seed_start, seed_dir, grid)
        grid = seed_line.draw()
        grid = obstacle_branch(grid, seed_line)
    elif obstacle_set == 1:
        main_chamber = chamber(grid, len(grid), len(grid[0]), grid[0][0])
        grid = main_chamber.split()
    elif obstacle_set == 2:
        main_chamber = chamber(grid, len(grid) - 4, len(grid[0]) - 4, grid[2][2])
        grid = main_chamber.squares()
    elif obstacle_set == 3:
        grid = rev_path(grid, start, end, 3)
    elif obstacle_set == 4:
        grid = rev_path(grid, start, end, 5)
    start.color = GREEN
    start.passable = True
    end.color = RED
    end.passable = True
    update_display(all_nodes, grid)
    return
#Function to display time
def display_time():
    time_font = pygame.font.SysFont(font, 50)
    time_second = datetime.datetime.now().second
    time_minute = datetime.datetime.now().minute
    time_hour = datetime.datetime.now().hour
    if time_second < 10:
        time_second = f"0{time_second}"
    if time_minute < 10:
        time_minute = f"0{time_minute}"
    if time_hour < 12:
        mer = "am"
    elif time_hour > 11:
        time_hour -= 12
        mer = "pm"
    current_time = f" {time_hour}:{time_minute}:{time_second} {mer} "
    time_surface = time_font.render(current_time, False, WHITE, DARK_GREY)
    screen_base.blit(time_surface, (20, 20))

#Define variables before running function
pygame.display.set_caption('Pathfinder Program')
a_star_ran = False
screen_base = pygame.display.set_mode((screen_size, screen_size))
screen_base.fill(GREY)
my_grid = define_grid(pos_base, width_base, height_base, grid_length, margin, screen_base)
my_grid[start_ID[0]][start_ID[1]].color = GREEN
my_grid[end_ID[0]][end_ID[1]].color = RED
all_nodes = define_all_nodes(my_grid)
cont_find = False
update_display(all_nodes, my_grid)
#Running function for application
while True:
    #Check if continue finding parameter is met
    if cont_find:
        draw_obstacles(my_grid, my_grid[start_ID[0]][start_ID[1]], my_grid[end_ID[0]][end_ID[1]])
        try:
            path = A_star(my_grid, my_grid[start_ID[0]][start_ID[1]], my_grid[end_ID[0]][end_ID[1]])
            my_grid = draw_path(my_grid, path)
            for eighth_sec in range(rest_period*7):
                time.sleep(0.125)
                update_display([], my_grid)
        except IndexError:
            print('pass')
            pass
        my_grid = define_grid(pos_base, width_base, height_base, grid_length, margin, screen_base)
        update_display(all_nodes, my_grid)
        my_grid[start_ID[0]][start_ID[1]].color = GREEN
        my_grid[end_ID[0]][end_ID[1]].color = RED
    cont_find = update_display([], my_grid)