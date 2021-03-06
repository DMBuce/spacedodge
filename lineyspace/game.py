#!/usr/bin/python

import pygame
import random

import entity

# TODO: move rand helper functions to entities module

def randpos(edge=False):
    randwidth  = random.randint(0, width())
    randheight = random.randint(0, height())
    if not edge:
        print("not edge")
        return (randwidth, randheight)
    else:
        return random.choice( [
            ( randwidth, 0          ),
            ( randwidth, height()   ),
            ( 0,         randheight ),
            ( width(),   randheight )
        ] )

def randangle():
    return random.randint(0, 360)

def width():
    return pygame.display.get_surface().get_width()

def height():
    return pygame.display.get_surface().get_height()


class Game:
    PHYS_LIMIT = 30

    def __init__(self):
        entity.init(self)
        #pygame.draw.init()
        #pygame.event.init()
        #pygame.math.init()
        #pygame.time.init()
        pygame.font.init()
        pygame.display.init()
        pygame.display.set_caption("Liney Space")
        random.seed()

        # TODO: pick dimensions from environment or config or args
        self.screen = pygame.display.set_mode(
            (1280, 720)
        )

        self.clock = pygame.time.Clock()
        self.entities = []

        # add some stars
        for i in range(width() * height() // 700):
            self.entities.append(entity.Star(None))

        # add the player
        self._player = entity.PlayerShip()
        self.entities.append(self._player)

    def player(self, newplayer=None):
        if newplayer is not None:
            self._player = newplayer
            if self._player not in self.entities:
                self.entities.append(self._player)

        return self._player

    def run(self):
        done = False
        while not done:

            # handle input
            # TODO: split out into input component somehow
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
                elif event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                    self._player.handle(event)

            # GAME LOGIC

            # gather up dead and newborn entities
            # and update all living entities
            grave = []        # indexes to dead entities that need to be reaped
            nursery = []      # new entities that need to be added
            physentities = [] # entities with physics
            for i, thing in enumerate(self.entities):
                nursery += thing.poop()

                if thing.isdead():
                    grave.append(i)
                else:
                    thing.update()

            # check for collisions
            physentities = [ e for e in self.entities if e.isphysical() and not e.isdead() ]
            for i, thing in enumerate(physentities):
                for j, that in enumerate(physentities[i+1:]):
                    if thing.touches(that):
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

# vim: set expandtab shiftwidth=4 softtabstop=4:
