import pygame
import os
import numpy
import math
import time
import pygame.mouse

pygame.init()
#Config
margin = 2
width_base = 10
height_base = width_base
pos_base = [0,0]
grid_length = 65
screen_size = 800
start_ID = [0, 0]
end_ID = [grid_length - 1, grid_length - 1]
saved_grid = False

#Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (100, 100, 100)
BLUE = (0 ,50, 200)
GREEN = (0, 230, 0)
RED = (230, 0, 0)
PURPLE = (125, 0, 125)

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

#Define draw grid function
def draw_grid(grid_):
    for column in range(len(grid_)):
        for row in range(len(grid_[0])):
            grid_[column][row].draw()

#Define update display function
def update_display(background):
    screen_base.fill(background)
    draw_grid(my_grid)
    pygame.display.update()

#Function for the A* algorithm
def A_star(grid,start,end):
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
        update_display(GREY)
        time.sleep(.001)
    #Horizontal loop
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
                        for tile in shortcut:
                            j = shortcut.index(tile)
                            grid[tile.ID[0]][tile.ID[1]].color = BLUE
                            path[i + j].short_check = False
                            old_path_node = path[i + j]
                            grid[old_path_node.ID[0]][old_path_node.ID[1]].color = WHITE
                            time.sleep(.005)
                            update_display(GREY)
                        grid[node.ID[0]][node.ID[1]].color = BLUE
                        short_found = True
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
                        for tile in shortcut:
                            j = shortcut.index(tile)
                            grid[tile.ID[0]][tile.ID[1]].color = BLUE
                            path[i + j].short_check = False
                            old_path_node = path[i + j]
                            grid[old_path_node.ID[0]][old_path_node.ID[1]].color = WHITE
                            time.sleep(.001)
                            update_display(GREY)
                        grid[node.ID[0]][node.ID[1]].color = BLUE
                        short_found = True
    update_display(GREY)
    return grid

#Define variables before running function
running = True
a_star_ran = False
screen_base = pygame.display.set_mode((screen_size, screen_size))
if not saved_grid:
    my_grid = define_grid(pos_base, width_base, height_base, grid_length, margin, screen_base)
elif saved_grid:
    my_grid = []
my_grid[start_ID[0]][start_ID[1]].color = GREEN
my_grid[end_ID[0]][end_ID[1]].color = RED

#Running function for application
while running:
    #Quit check
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        #Function to draw walls in grid
        if event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed() == (1, 0, 0):
            mouse_chk = True
            while mouse_chk:
                pos = pygame.mouse.get_pos()
                for col in range(len(my_grid)):
                    for row in range(len(my_grid[0])):
                        node = my_grid[col][row]
                        if pos[0] >= node.pos[0] and pos[0] <= (node.pos[0] + node.width):
                            if pos[1] >= node.pos[1] and pos[1] <= (node.pos[1] + node.height):
                                node.color = BLACK
                                node.passable = False
                                break
                for event in pygame.event.get():
                    if event.type == pygame.MOUSEBUTTONUP:
                        mouse_chk = False
                update_display(GREY)
        elif event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed() == (0, 0, 1):
            mouse_chk = True
            while mouse_chk:
                pos = pygame.mouse.get_pos()
                for col in range(len(my_grid)):
                    for row in range(len(my_grid[0])):
                        node = my_grid[col][row]
                        if pos[0] >= node.pos[0] and pos[0] <= (node.pos[0] + node.width):
                            if pos[1] >= node.pos[1] and pos[1] <= (node.pos[1] + node.height):
                                node.color = WHITE
                                node.passable = True
                                break
                for event in pygame.event.get():
                    if event.type == pygame.MOUSEBUTTONUP:
                        mouse_chk = False
                update_display(GREY)
        #Function to execute pathfinding algorithm
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            path = A_star(my_grid, my_grid[start_ID[0]][start_ID[1]], my_grid[end_ID[0]][end_ID[1]])
            my_grid = draw_path(my_grid, path)
    update_display(GREY)