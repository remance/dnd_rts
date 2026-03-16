#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
from copy import deepcopy
from random import random, choice
import pygame
from pygame.locals import *
from math import ceil, floor
from pygame import Vector2
import numpy as np

DEFAULT_WINDOW_WIDTH = 3840
DEFAULT_WINDOW_HEIGHT = 2160
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
DEFAULT_TILE_SIZE = 512
ZOOM_SCALE_VALUE = (1.25, 1, 0.75, 0.5, 0.375, 0.28125, 0.1875, 0.140625)
screen_scale_width = WINDOW_WIDTH / DEFAULT_WINDOW_WIDTH
screen_scale_height = WINDOW_HEIGHT / DEFAULT_WINDOW_HEIGHT
ZOOM_TILE_SIZE_SCALED = [(DEFAULT_TILE_SIZE * value * screen_scale_width, DEFAULT_TILE_SIZE * value * screen_scale_height) for
                         value in ZOOM_SCALE_VALUE]
ZOOM_TILE_HEIGHT_WITH_HEIGHT_SCALED = {True: [item[1] / 10 for item in ZOOM_TILE_SIZE_SCALED],
                                       False: [item[1] / 4 for item in ZOOM_TILE_SIZE_SCALED]}
DEFAULT_ZOOM_LEVEL = int(len(ZOOM_TILE_SIZE_SCALED) / 2)
current_zoom_level = DEFAULT_ZOOM_LEVEL
current_zoom_scale = ZOOM_SCALE_VALUE[current_zoom_level]

GRID_SIZE = 2
max_map_width_scaled = [value[0] * GRID_SIZE for value in ZOOM_TILE_SIZE_SCALED]
max_map_height_scaled = [value[1] * GRID_SIZE for value in ZOOM_TILE_SIZE_SCALED]

max_show_cell_width_scaled = [ceil(WINDOW_WIDTH / item[0]) for item in ZOOM_TILE_SIZE_SCALED]
max_show_cell_height_scaled = {True: [ceil(WINDOW_HEIGHT / (item[1] / 4)) + 3 for item in ZOOM_TILE_SIZE_SCALED],
                               False: [ceil(WINDOW_HEIGHT / (item[1] / 4)) + 5 for item in ZOOM_TILE_SIZE_SCALED]}
print(ZOOM_TILE_SIZE_SCALED)
print(max_show_cell_width_scaled, max_show_cell_height_scaled)
# Set up asset directories
ASSET_DIR = 'images'
FONT_PATH = 'tahoma.ttf'
TERRAIN_TYPES = ['dirt', 'grass', 'rocky', 'urban1', 'urban2', 'water1', 'water2', 'water3']

# Initialize Pygame
pygame.init()
pygame.font.init()
clock = pygame.time.Clock()

# Create the window
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), HWSURFACE | DOUBLEBUF | RESIZABLE)
pygame.display.set_caption("Isometric Terrain")


# Load images initially
highlight_image = pygame.image.load("highlight.png").convert_alpha()
highlight_image = [pygame.transform.scale(
    highlight_image,
    (highlight_image.get_width() * value * screen_scale_width, highlight_image.get_height() * value * screen_scale_height)) for value in ZOOM_SCALE_VALUE]

images = {terrain: pygame.image.load(os.path.join(ASSET_DIR, f'cube_{terrain}.png')).convert_alpha() for
           terrain in TERRAIN_TYPES}
images = [{terrain: pygame.transform.scale(images[terrain], value) for
                  terrain in TERRAIN_TYPES} for value in ZOOM_TILE_SIZE_SCALED]

# Load font
try:
    font = pygame.font.Font(FONT_PATH, 20)
except FileNotFoundError:
    font = pygame.font.SysFont('tahoma', 20)

grid = {}

half_camera_width = DEFAULT_WINDOW_WIDTH / 2
half_camera_height = DEFAULT_WINDOW_HEIGHT / 2
mini_height_mode = False
show_highlight = True
current_camera_rotate = 0
selected_tiles = []


# Camera Class
class Camera:
    def __init__(self):
        camera_w, camera_h = window.get_rect().size  # get size of camera
        self.camera_w_center = camera_w / 2
        self.camera_h_center = camera_h / 2

        self.base_x = half_camera_width
        self.base_y = half_camera_height

        self.x = self.base_x * current_zoom_scale * screen_scale_width
        self.y = self.base_y * current_zoom_scale * screen_scale_height

        self.topleft_x = self.x - self.camera_w_center
        self.topleft_y = self.y - self.camera_h_center

    def camera_update(self):
        self.x = self.base_x * current_zoom_scale * screen_scale_width
        self.y = self.base_y * current_zoom_scale * screen_scale_height

        self.topleft_x = self.x - self.camera_w_center
        self.topleft_y = self.y - self.camera_h_center

    def update(self, pos):
        window.fill((0, 0, 0))
        camera_x = pos[0] - self.camera_w_center  # Current camera center x
        camera_y = pos[1] - self.camera_h_center  # Current camera center y
        # for surface in surfaces:  # Blit sprite to camara image
        #     surface_x, surface_y = surface.rect.left, surface.rect.top
        #     surface_w, surface_h = surface.rect.size
        #     if surface_x + surface_w - camera_x > 0 and surface_y + surface_h - camera_y > 0:  # only blit if image in camera
        #         window.blit(surface.image, (surface_x - camera_x, surface_y - camera_y))


camera = Camera()


# Terrain Block Class
def create_grid():
    terrain_grid = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            pos = {}
            pos_center_top = {}
            for zoom_level in range(len(ZOOM_TILE_SIZE_SCALED)):
                half_tile_width = ZOOM_TILE_SIZE_SCALED[zoom_level][0] / 2
                half_tile_height = ZOOM_TILE_SIZE_SCALED[zoom_level][1] / 2
                a_fourth_tile_height = ZOOM_TILE_SIZE_SCALED[zoom_level][1] / 4
                start_x = (half_camera_width * screen_scale_width * ZOOM_SCALE_VALUE[zoom_level]) - half_tile_width
                start_y = (half_camera_height * screen_scale_height * ZOOM_SCALE_VALUE[zoom_level]) - (max_map_height_scaled[zoom_level] / 4)

                pos[zoom_level] = Vector2(start_x + ((x - y) * half_tile_width),
                                          start_y + ((x + y) * a_fourth_tile_height))
                pos_center_top[zoom_level] = Vector2(pos[zoom_level][0] + half_tile_width,
                                                     pos[zoom_level][1] + half_tile_height)

            terrain_grid[x][y] = {"terrain": choice(TERRAIN_TYPES), "height": int(random() * 4) + 1,
                                  "topleft": pos, "center": pos_center_top}

    terrain_grid = np.array(terrain_grid)
    terrain_arrays = [np.rot90(deepcopy(terrain_grid)),
                      np.rot90(np.rot90(deepcopy(terrain_grid))),
                      np.fliplr(deepcopy(terrain_grid).swapaxes(0, 1))]  # rotate the array based on the side
    for array in terrain_arrays:  # recalculate position of block
        for x, x_value in enumerate(array):
            for y, y_value in enumerate(x_value):
                pos = {}
                pos_center_top = {}
                for zoom_level in range(len(ZOOM_TILE_SIZE_SCALED)):
                    half_tile_width = ZOOM_TILE_SIZE_SCALED[zoom_level][0] / 2
                    half_tile_height = ZOOM_TILE_SIZE_SCALED[zoom_level][1] / 2
                    a_fourth_tile_height = ZOOM_TILE_SIZE_SCALED[zoom_level][1] / 4
                    # blit using topleft, so minus by half width to offset to center.
                    start_x = (half_camera_width * screen_scale_width * ZOOM_SCALE_VALUE[zoom_level]) - half_tile_width
                    start_y = (half_camera_height * screen_scale_height * ZOOM_SCALE_VALUE[zoom_level]) - (max_map_height_scaled[zoom_level] / 4)

                    pos[zoom_level] = Vector2(start_x + ((x - y) * half_tile_width),
                                              start_y + ((x + y) * a_fourth_tile_height))
                    pos_center_top[zoom_level] = Vector2(pos[zoom_level][0] + half_tile_width,
                                                         pos[zoom_level][1] + half_tile_height)

                y_value["topleft"] = pos
                y_value["center"] = pos_center_top

    terrain_arrays = [terrain_grid.tolist()] + [item.tolist() for item in terrain_arrays]  # convert back to python list

    return terrain_arrays


terrain_arrays = create_grid()
# self.camera.update(self.shown_camera_pos, self.battle_camera,
#                    out_surfaces=self.realtime_ui_updater)


def draw_grid():
    window.fill((0, 0, 0))  # Clear the screen

    # Get the mouse position
    mouse_pos = pygame.mouse.get_pos()

    # print(base_mouse_pos, mouse_pos)
    hovered_block = None

    # Check for tile position within the screen bounds before drawing
    # pos = (start_x + ((x - y) * half_tile_size) - half_tile_size,
    #        start_y + ((x + y) * a_fourth_tile_size))
    half_map_width = max_map_width_scaled[current_zoom_level] / 2
    half_map_height = max_map_height_scaled[current_zoom_level] / 2

    half_tile_width = ZOOM_TILE_SIZE_SCALED[current_zoom_level][0] / 2
    start_x = (half_camera_width * screen_scale_width * ZOOM_SCALE_VALUE[current_zoom_level]) - half_tile_width
    start_y = (half_camera_height * screen_scale_height * ZOOM_SCALE_VALUE[current_zoom_level]) - (
                max_map_height_scaled[current_zoom_level] / 4)

    min_block_y = floor((camera.topleft_x - start_x + half_map_width) / ZOOM_TILE_SIZE_SCALED[current_zoom_level][0])
    # print(min_block_y)
    # if min_block_y < 0:
    min_block_y = 0
    # min_block_x = ceil((camera.topleft_x - half_map_width))
    # print(min_block_x)
    # if min_block_x < 0:
    min_block_x = GRID_SIZE

    max_block_y = floor((camera.topleft_x + half_map_width) / ZOOM_TILE_SIZE_SCALED[current_zoom_level][0])
    # if max_block_y > GRID_SIZE:
    max_block_y = 0
    # max_block_x = ceil((camera.topleft_y - max_map_height_scaled[current_zoom_level] / 2) / MAX_TILE_HEIGHT_VISIBILITY[mini_height_mode])
    # if max_block_x > GRID_SIZE:
    max_block_x = GRID_SIZE

    min_to_check = range(min_block_y, min_block_x)
    max_to_check = range(max_block_y, max_block_x)
    # print(min_to_check, max_to_check)

    # use x,y coordinate of 45 degree grid cell system here
    for grid_y in max_to_check:
        for grid_x in min_to_check:
            pos = terrain_arrays[current_camera_rotate][grid_x][grid_y]["topleft"][current_zoom_level]
            pos = Vector2(pos[0] - camera.topleft_x, pos[1] - camera.topleft_y)

            for height in range(terrain_arrays[current_camera_rotate][grid_x][grid_y]["height"]):
                pos_y_with_height = pos[1] - (
                        ZOOM_TILE_HEIGHT_WITH_HEIGHT_SCALED[mini_height_mode][current_zoom_level] * height)
                # print(pos)
                window.blit(images[current_zoom_level][terrain_arrays[current_camera_rotate][grid_x][grid_y]["terrain"]],
                            (pos[0], pos_y_with_height))
            if (grid_x, grid_y) in selected_tiles and show_highlight:
                window.blit(highlight_image[current_zoom_level], (pos[0], pos_y_with_height))
            # center_pos = terrain_arrays[current_camera_rotate][grid_x][grid_y]["center"][current_zoom_level]
            # center_pos = Vector2(center_pos[0] - camera.topleft_x, center_pos[1] - camera.topleft_y - ZOOM_TILE_HEIGHT_WITH_HEIGHT_SCALED[False][current_zoom_level] - (
            #         ZOOM_TILE_HEIGHT_WITH_HEIGHT_SCALED[mini_height_mode][current_zoom_level] * (terrain_arrays[current_camera_rotate][grid_x][grid_y]["height"] - 1)))
            # pygame.draw.circle(window, (220,220,220), center_pos, 10, 5)
            # pygame.draw.circle(window, (220,50,50), pos, 10, 5)

    found_hover = False
    for grid_y in reversed(max_to_check):
        for grid_x in reversed(min_to_check):
            # Check if the mouse is hovering over block
            terrain_height = terrain_arrays[current_camera_rotate][grid_x][grid_y]["height"]
            center_pos = terrain_arrays[current_camera_rotate][grid_x][grid_y]["center"][current_zoom_level]
            center_pos = Vector2(center_pos[0] - camera.topleft_x, center_pos[1] - camera.topleft_y - ZOOM_TILE_HEIGHT_WITH_HEIGHT_SCALED[False][current_zoom_level] - (
                    ZOOM_TILE_HEIGHT_WITH_HEIGHT_SCALED[mini_height_mode][current_zoom_level] * (terrain_arrays[current_camera_rotate][grid_x][grid_y]["height"] - 1)))
            x = mouse_pos[0]
            y = mouse_pos[1]
            x_diff = abs(center_pos[0] - x)
            y_diff = abs(center_pos[1] - y)
            if x_diff < ZOOM_TILE_SIZE_SCALED[current_zoom_level][0] / 2:
                if y_diff < ZOOM_TILE_SIZE_SCALED[current_zoom_level][1] * 0.2 and x_diff + y_diff <= ZOOM_TILE_SIZE_SCALED[current_zoom_level][0] / 2.5:
                    # print(abs(center_pos[0] - mouse_pos[0]), abs(center_pos[1] - mouse_pos[1]), center_pos.distance_to(mouse_pos))
                    hovered_block = (grid_x, grid_y)
                    pos = terrain_arrays[current_camera_rotate][grid_x][grid_y]["topleft"][current_zoom_level]
                    pos = Vector2(pos[0] - camera.topleft_x, pos[1] - camera.topleft_y)
                    pos_y_with_height = pos[1]
                    if terrain_height:
                        pos_y_with_height -= (ZOOM_TILE_HEIGHT_WITH_HEIGHT_SCALED[mini_height_mode][current_zoom_level] *
                                              (terrain_height - 1))
                    found_hover = True
                    break

                elif mouse_pos[1] > center_pos[1]:
                    # cursor within body of high height tile, very likely blocked cursor view from above but lower tile
                    # break the loop since cursor should not consider hidden tile
                    found_hover = True
                    break
        if found_hover:
            break


    # Display camera position
    camera_text = font.render(f"Camera: ({camera.x}, {camera.y})", True, (255, 255, 255))
    window.blit(camera_text, (WINDOW_WIDTH - camera_text.get_width(), camera_text.get_height()))

    # Display the coordinates of the hovered block
    if hovered_block:
        text_surface = font.render(f"Block: ({hovered_block[0]}, {hovered_block[1]})", True, (255, 255, 255))
        window.blit(text_surface, (WINDOW_WIDTH - text_surface.get_width(), 0))

    return hovered_block


# Main loop
running = True
while running:
    # print(int(clock.get_fps()))
    clock.tick()
    hovered_block = draw_grid()
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            sys.exit()

        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running = False
                pygame.quit()
                sys.exit()
            elif event.key == K_MINUS:
                current_zoom_level += 1
                if current_zoom_level > len(ZOOM_SCALE_VALUE) - 1:
                    current_zoom_level = len(ZOOM_SCALE_VALUE) - 1
                current_zoom_scale = ZOOM_SCALE_VALUE[current_zoom_level]
                camera.camera_update()
            elif event.key == K_EQUALS:
                current_zoom_level -= 1
                if current_zoom_level < 0:
                    current_zoom_level = 0
                current_zoom_scale = ZOOM_SCALE_VALUE[current_zoom_level]
                camera.camera_update()
            elif event.key in [K_UP, K_w]:
                camera.base_y -= 1500
                camera.camera_update()
            elif event.key in [K_DOWN, K_s]:
                camera.base_y += 1500
                camera.camera_update()
            elif event.key in [K_LEFT, K_a]:
                camera.base_x -= 1500
                camera.camera_update()
            elif event.key in [K_RIGHT, K_d]:
                camera.base_x += 1500
                camera.camera_update()
            elif event.key in [K_v]:
                if mini_height_mode:
                    mini_height_mode = False
                else:
                    mini_height_mode = True
            elif event.key in [K_c]:
                if show_highlight:
                    show_highlight = False
                else:
                    show_highlight = True
            elif event.key in [K_q, K_e]:
                if event.key == K_q:
                    current_camera_rotate -= 1
                else:
                    current_camera_rotate += 1
                if current_camera_rotate < 0:
                    current_camera_rotate = 3
                elif current_camera_rotate > 3:
                    current_camera_rotate = 0
            elif event.key in [K_z]:
                terrain_arrays = create_grid()
        elif event.type == MOUSEBUTTONUP:
            if event.button == 1 and hovered_block:
                if hovered_block not in selected_tiles:
                    selected_tiles.append(hovered_block)
                else:
                    selected_tiles.remove(hovered_block)
            elif event.button == 3:
                selected_tiles = []

pygame.quit()
