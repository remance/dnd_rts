#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
from random import random, choice
import pygame, json
from pygame.locals import *
from math import ceil, floor


DEFAULT_WINDOW_WIDTH = 3840
DEFAULT_WINDOW_HEIGHT = 2160
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
DEFAULT_TILE_SIZE = 128
ZOOM_SCALE_VALUE = (1, 0.75, 0.5, 0.375, 0.28125, 0.1875, 0.140625)
screen_scale = (DEFAULT_WINDOW_WIDTH / WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT / WINDOW_HEIGHT)
ZOOM_TILE_SIZE_SCALED = {index: (DEFAULT_TILE_SIZE * value * screen_scale[0], DEFAULT_TILE_SIZE * value * screen_scale[1]) for
                         index, value in enumerate(ZOOM_SCALE_VALUE)}
DEFAULT_ZOOM_LEVEL = int(len(ZOOM_TILE_SIZE_SCALED) / 2)
current_zoom_scale_value = ZOOM_SCALE_VALUE[DEFAULT_ZOOM_LEVEL]
TILE_WIDTH = ZOOM_TILE_SIZE_SCALED[DEFAULT_ZOOM_LEVEL][0]
TILE_HEIGHT = ZOOM_TILE_SIZE_SCALED[DEFAULT_ZOOM_LEVEL][1]
MAX_TILE_HEIGHT_VISIBILITY = TILE_HEIGHT * 3
GRID_SIZE = 18

current_zoom = DEFAULT_ZOOM_LEVEL

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
images = {terrain: pygame.image.load(os.path.join(ASSET_DIR, f'cube_{terrain}.png')).convert_alpha() for
           terrain in TERRAIN_TYPES}
images = {index: {terrain: pygame.transform.scale(images[terrain], ZOOM_TILE_SIZE_SCALED[index]) for
                  terrain in TERRAIN_TYPES} for index in ZOOM_TILE_SIZE_SCALED}

# Load font
try:
    font = pygame.font.Font(FONT_PATH, 20)
except FileNotFoundError:
    font = pygame.font.SysFont('tahoma', 20)

grid = {}

half_camera_width = WINDOW_WIDTH / 2
half_camera_height = WINDOW_HEIGHT / 2


# Camera Class
class Camera:
    def __init__(self):
        camera_w, camera_h = window.get_rect().size  # get size of camera
        self.camera_w_center = camera_w / 2
        self.camera_h_center = camera_h / 2

        self.base_x = half_camera_width
        self.base_y = half_camera_height

        self.x = self.base_x * ZOOM_SCALE_VALUE[current_zoom]
        self.y = self.base_y * ZOOM_SCALE_VALUE[current_zoom]

        self.topleft_x = self.x - self.camera_w_center
        self.topleft_y = self.y - self.camera_h_center

    def camera_update(self):
        self.x = self.base_x * ZOOM_SCALE_VALUE[current_zoom]
        self.y = self.base_y * ZOOM_SCALE_VALUE[current_zoom]

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
terrain_grid = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

for x in range(GRID_SIZE):
    for y in range(GRID_SIZE):
        pos = {}
        pos_top_left = {}
        for zoom_level in ZOOM_TILE_SIZE_SCALED:
            max_map_width = ZOOM_TILE_SIZE_SCALED[zoom_level][0] * GRID_SIZE
            max_map_height = ZOOM_TILE_SIZE_SCALED[zoom_level][1] * GRID_SIZE
            map_center_x = max_map_width / 2
            map_center_y = max_map_height / 2
            half_tile_width = ZOOM_TILE_SIZE_SCALED[zoom_level][0] / 2
            a_fourth_tile_height = ZOOM_TILE_SIZE_SCALED[zoom_level][1] / 4
            start_x = (half_camera_width * ZOOM_SCALE_VALUE[zoom_level]) - half_tile_width
            start_y = (half_camera_height * ZOOM_SCALE_VALUE[zoom_level]) - (map_center_y / 2)

            pos[zoom_level] = (start_x + ((x - y) * half_tile_width) - half_tile_width,
                               start_y + ((x + y) * a_fourth_tile_height))
            pos_top_left[zoom_level] = (pos[zoom_level][0] + half_tile_width, pos[zoom_level][1])
        terrain_grid[x][y] = {"terrain": choice(TERRAIN_TYPES), "height": int(random() * 2),
                              "topleft": pos_top_left, "center": pos}

# asd
# self.camera.update(self.shown_camera_pos, self.battle_camera,
#                    out_surfaces=self.realtime_ui_updater)


def draw_grid():
    window.fill((0, 0, 0))  # Clear the screen

    # Get the mouse position
    # mouse_x, mouse_y = pygame.mouse.get_pos()
    hovered_block = None
    # pos = (start_x + ((x - y) * half_tile_size) - half_tile_size,
    #        start_y + ((x + y) * a_fourth_tile_size))
    min_block_x = floor((camera.topleft_x - map_center_x))
    if min_block_x < 0:
        min_block_x = 0
    min_block_y = floor((camera.topleft_y - half_camera_height) / MAX_TILE_HEIGHT_VISIBILITY)
    if min_block_y < 0:
        min_block_y = 0

    max_block_x = ceil((camera.topleft_x + half_camera_width))
    # if max_block_x > GRID_SIZE:
    max_block_x = GRID_SIZE
    # max_block_y = ceil((camera.topleft_y + half_camera_height) * MAX_TILE_VISIBILITY)
    # if max_block_y > GRID_SIZE:
    max_block_y = GRID_SIZE
    # print(camera.x, camera.y, min_block_x, min_block_y, max_block_x, max_block_y)

    for grid_x in range(min_block_x, max_block_x):
        for grid_y in range(min_block_y, max_block_y):
            # Check if the current tile position is within the screen bounds before drawing
            pos = terrain_grid[grid_x][grid_y]["topleft"][current_zoom]
            pos = (pos[0] - camera.topleft_x, pos[1] - camera.topleft_y)
            # pos = (camera.x + pos[0], camera.y - pos[1])

            # Check if the mouse is hovering over this block
            # if mouse_x in range(x, x + int(TILE_SIZE * 0.8)) and mouse_y in range(y, y + int(TILE_SIZE * 0.3)):
            #     hovered_block = block
            #     blit_y -= TILE_SIZE // 3
            window.blit(images[current_zoom][terrain_grid[grid_x][grid_y]["terrain"]], pos)

    # Display camera position
    camera_text = font.render(f"Camera: ({camera.x}, {camera.y})", True, (255, 255, 255))
    window.blit(camera_text, (WINDOW_WIDTH - camera_text.get_width(), camera_text.get_height()))

    # Display the coordinates of the hovered block
    if hovered_block:
        text_surface = font.render(f"Block: ({hovered_block['x']}, {hovered_block['y']})", True, (255, 255, 255))
        window.blit(text_surface, (WINDOW_WIDTH - text_surface.get_width(), 0))


# Main loop
running = True
while running:
    # print(int(clock.get_fps()))
    clock.tick()
    draw_grid()
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
                current_zoom += 1
                if current_zoom > len(ZOOM_SCALE_VALUE) - 1:
                    current_zoom = len(ZOOM_SCALE_VALUE) - 1
                current_zoom_scale_value = ZOOM_SCALE_VALUE[current_zoom]
                camera.camera_update()
            elif event.key == K_EQUALS:
                current_zoom -= 1
                if current_zoom < 0:
                    current_zoom = 0
                current_zoom_scale_value = ZOOM_SCALE_VALUE[current_zoom]
                camera.camera_update()
            elif event.key in [K_UP, K_w]:
                camera.base_y -= 20
                camera.camera_update()
            elif event.key in [K_DOWN, K_s]:
                camera.base_y += 20
                camera.camera_update()
            elif event.key in [K_LEFT, K_a]:
                camera.base_x -= 20
                camera.camera_update()
            elif event.key in [K_RIGHT, K_d]:
                camera.base_x += 20
                camera.camera_update()


pygame.quit()
