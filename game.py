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

global GAME_OBJECTS
global PHYS_OBJECTS
GAME_OBJECTS = []
PHYS_OBJECTS = []

(x, y) = (0, 1)

def randpos():
    return (
        random.randint(0, SCREEN_WIDTH),
        random.randint(0, SCREEN_HEIGHT)
    )

def randangle():
    return random.randint(0, 360)

def kill(i, objlist, children):
    objlist += children
    objlist.pop(i)

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

    #player.color = PINK

    player = entity.PlayerShip()
    GAME_OBJECTS.append(player)
    PHYS_OBJECTS.append(player)

    enemy = entity.EnemyShip(
        randpos(),
        #entity.UNIT_VECTOR.rotate(randangle()).scale_to_length(random.uniform(0.0, 0.5)),
        0.5 * entity.EnemyShip.MAX_VEL*entity.UNIT_VECTOR.rotate(randangle()),
        randangle()
    )
    enemy.target(player)
    #enemy.player = player
    GAME_OBJECTS.append(enemy)
    PHYS_OBJECTS.append(enemy)

    asteroid = entity.Asteroid(
        randpos(),
        random.uniform(0.01, 0.75*entity.PlayerShip.MAX_VEL) \
            * entity.UNIT_VECTOR.rotate(randangle())
    )
    GAME_OBJECTS.append(asteroid)
    PHYS_OBJECTS.append(asteroid)

    for i in range(SCREEN_WIDTH * SCREEN_HEIGHT // 700):
        GAME_OBJECTS.append(entity.Star())

    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                player.handle(event)

        # GAME LOGIC

        # update each game object
        for i, thing in enumerate(GAME_OBJECTS):
            if thing.isdead:
                kill(i, GAME_OBJECTS, thing.gamechildren + thing.physchildren)
            else:
                thing.update()

        # check for collisions
        for i, thing in enumerate(PHYS_OBJECTS):
            if thing.isdead:
                kill(i, PHYS_OBJECTS, thing.physchildren)
            for j, that in enumerate(PHYS_OBJECTS[i+1:]):
                if that.isdead:
                    kill(i+j+1, PHYS_OBJECTS, thing.physchildren)
                elif thing.touches(that):
                    thing.interact(that)

        # DRAW SCREEN

        screen.fill(BLACK)

        for thing in GAME_OBJECTS:
            thing.draw(screen)

        pygame.display.flip()

        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    sys.exit(main())

