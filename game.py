#!/usr/bin/python

import pygame
import random

import entity

# TODO: move rand helper functions to entities module

def randpos():
    return (
        random.randint(0, width()),
        random.randint(0, height())
    )

def randangle():
    return random.randint(0, 360)

def width():
    return pygame.display.get_surface().get_width()

def height():
    return pygame.display.get_surface().get_height()


class Game:
    # use width() and height() instead
    #width()  = 1280
    #height() = 720
    PHYS_LIMIT = 20

    def __init__(self):

        #pygame.draw.init()
        #pygame.event.init()
        #pygame.math.init()
        #pygame.time.init()
        pygame.display.init()
        pygame.display.set_caption("SpaceDodge")
        random.seed()

        # TODO: pick dimensions from environment or args
        self.screen = pygame.display.set_mode(
            (1280, 720)
        )

        self.clock = pygame.time.Clock()
        self.entities = []

        # add the player
        self.player = entity.PlayerShip()
        self.entities.append(self.player)

        # add some stars
        for i in range(width() * height() // 700):
            self.entities.append(entity.Star(None, self.player))

    def run(self):
        done = False
        while not done:

            # handle input
            # TODO: split out into input component somehow
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
                elif event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                    self.player.handle(event)

            # GAME LOGIC

            # gather up dead and newborn entities
            # and update all living entities
            grave = []        # indexes to dead entities that need to be reaped
            nursery = []      # new entities that need to be added
            physentities = [] # entities with physics
            for i, thing in enumerate(self.entities):
                nursery += thing.children()
                thing.infanticide()

                if thing.isdead():
                    grave.append(i)
                else:
                    thing.update()

            # check for collisions
            physentities = [ e for e in self.entities if e.isphysical() ]
            for i, thing in enumerate(physentities):
                for j, that in enumerate(physentities[i+1:]):
                    if not that.isdead() and thing.touches(that):
                        thing.interact(that)
                        that.interact(thing)

            # reap dead entities
            for i in reversed(grave):
                self.entities.pop(i)

            # add new entities
            self.entities += nursery

            # prevent asteroids from spawning if we're above PHYS_LIMIT
            # TODO: move this logic into SpaceHole class
            if len(physentities) > self.PHYS_LIMIT:
                entity.SpaceHole.makeboth = False
            else:
                entity.SpaceHole.makeboth = True

            # DRAW SCREEN

            self.screen.fill(entity.BLACK)

            for thing in self.entities:
                thing.draw(self.screen)

            pygame.display.flip()

            self.clock.tick(60)

        print(len(physentities))

    def quit(self):
        pygame.quit()

