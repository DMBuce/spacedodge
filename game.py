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
PHYS_LIMIT = 20

(x, y) = (0, 1)

def randpos():
    return (
        random.randint(0, SCREEN_WIDTH),
        random.randint(0, SCREEN_HEIGHT)
    )

def randangle():
    return random.randint(0, 360)

def main():
    global GAME_OBJECTS
    global PHYS_OBJECTS

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

    # add the player
    player = entity.PlayerShip()
    GAME_OBJECTS.append(player)
    PHYS_OBJECTS.append(player)

    # add some stars
    for i in range(SCREEN_WIDTH * SCREEN_HEIGHT // 700):
        GAME_OBJECTS.append(entity.Star(None, player))

    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                player.handle(event)

        # GAME LOGIC

        # update each game object
        gamegrave = []
        gamenursery = []
        physnursery = []
        for i, thing in enumerate(GAME_OBJECTS):
            gamenursery += thing.gamechildren
            physnursery += thing.physchildren
            thing.gamechildren = []
            thing.physchildren = []

            if thing.isdead:
                gamegrave.append(i)
            else:
                thing.update()

        # check for collisions
        physgrave = []
        for i, thing in enumerate(PHYS_OBJECTS):
            if thing.isdead:
                physgrave.append(i)
            for j, that in enumerate(PHYS_OBJECTS[i+1:]):
                if not that.isdead and thing.touches(that):
                    thing.interact(that)

        # reap dead objects
        for i in reversed(gamegrave):
            GAME_OBJECTS.pop(i)

        for i in reversed(physgrave):
            PHYS_OBJECTS.pop(i)

        # add new objects
        GAME_OBJECTS += physnursery + gamenursery
        PHYS_OBJECTS += physnursery

        # prevent asteroids from spawning if we're above PHYS_LIMIT
        if len(PHYS_OBJECTS) > PHYS_LIMIT:
            entity.SpaceHole.makeboth = False
        else:
            entity.SpaceHole.makeboth = True

        # DRAW SCREEN

        screen.fill(BLACK)

        for thing in GAME_OBJECTS:
            thing.draw(screen)

        pygame.display.flip()

        clock.tick(60)

    print(len(PHYS_OBJECTS))
    pygame.quit()

if __name__ == "__main__":
    sys.exit(main())

