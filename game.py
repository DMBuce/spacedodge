#!/usr/bin/python

import pygame
import sys
import math
import random

import entity

# colors
BLACK     = (  0,   0,   0)
DARKGREY  = (191, 191, 191)
GREY      = (127, 127, 127)
LIGHTGREY = ( 63,  63,  63)
WHITE     = (255, 255, 255)
PINK      = (255,  20, 147)
YELLOW    = (255, 255,   0)

#PI          = math.pi

SCREEN_WIDTH  = 1280
SCREEN_HEIGHT = 720
#SCREEN_WIDTH  = 700
#SCREEN_HEIGHT = 500
SCREEN_VECTOR = pygame.math.Vector2(SCREEN_WIDTH, SCREEN_HEIGHT)

GAME_OBJECTS = []

(x, y) = (0, 1)

def main():
    random.seed()

    pygame.display.init()
    #pygame.draw.init()
    #pygame.event.init()
    #pygame.math.init()
    #pygame.time.init()

    winsize = (SCREEN_WIDTH, SCREEN_HEIGHT)
    pygame.display.set_caption("SpaceDodge")
    screen = pygame.display.set_mode(winsize)

    clock = pygame.time.Clock()

    ship = entity.Ship()
    ship.color = PINK

    GAME_OBJECTS.append(ship)

    enemies = []

    for i in range(SCREEN_WIDTH * SCREEN_HEIGHT // 700):
        GAME_OBJECTS.append(entity.Star())

    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                ship.handle(event)

        # GAME LOGIC

        for thing in GAME_OBJECTS:
            thing.update()

        # DRAW SCREEN

        screen.fill(BLACK)

        for thing in GAME_OBJECTS:
            thing.draw(screen)

        pygame.display.flip()

        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    sys.exit(main())

