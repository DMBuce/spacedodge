#!/usr/bin/python2

import pygame
import sys
import math

# colors
BLACK  = (  0,   0,   0)
WHITE  = (255, 255, 255)
GREEN  = (  0, 255,   0)
RED    = (255,   0,   0)
PINK   = (255,  20, 147)
YELLOW = (255, 255,   0)
PI     = math.pi

SCREEN_WIDTH  = 700
SCREEN_HEIGHT = 500

(x, y) = (0, 1)

class Ship:
    class BadDimensionError:
        pass

    WIDTH  = 5
    HEIGHT = 7
    MAX_VEL = 3
    MAX_ACC = 0.1

    def __init__(self, coords=[SCREEN_WIDTH / 2.0, SCREEN_HEIGHT / 2.0]):
        self.pos = coords
        self.vel = [0.0, 0.0]
        self.acc = [0.0, 0.0]
        self.color = YELLOW

    def points(self):
        return [
            [self.pos[x],                    self.pos[y] - self.HEIGHT / 2.0],
            [self.pos[x] - self.WIDTH / 2.0, self.pos[y] + self.HEIGHT / 2.0],
            [self.pos[x] + self.WIDTH / 2.0, self.pos[y] + self.HEIGHT / 2.0],
        ]

    def update(self):
        self.vel = [ self.vel[x] + self.acc[x], self.vel[y] + self.acc[y] ]
        for i in (x, y):
            if self.vel[i] > self.MAX_VEL:
                self.vel[i] = self.MAX_VEL
            elif self.vel[i] < -self.MAX_VEL:
                self.vel[i] = -self.MAX_VEL

        self.pos = [ self.pos[x] + self.vel[x], self.pos[y] + self.vel[y] ]
        if self.pos[x] > SCREEN_WIDTH:
            self.pos[x] = self.pos[x] - SCREEN_WIDTH
        elif self.pos[x] < 0:
            self.pos[x] = self.pos[x] + SCREEN_WIDTH
        if self.pos[y] > SCREEN_HEIGHT:
            self.pos[y] = self.pos[y] - SCREEN_HEIGHT
        elif self.pos[y] < 0:
            self.pos[y] = self.pos[y] + SCREEN_HEIGHT

    def accel(self, acceleration, dimension):
        if dimension != x and dimension != y:
            raise self.BadDimensionError()

        self.acc[dimension] += acceleration
        if self.acc[dimension] > self.MAX_ACC:
            self.acc[dimension] = self.MAX_ACC
        elif self.acc[dimension] < -self.MAX_ACC:
            self.acc[dimension] = -self.MAX_ACC

def main():
    pygame.init()

    winsize = (SCREEN_WIDTH, SCREEN_HEIGHT)
    pygame.display.set_caption("Awesome Game")
    screen = pygame.display.set_mode(winsize)

    clock = pygame.time.Clock()

    ship = Ship()
    ship.color = PINK
    enemies = []

    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    ship.accel(ship.MAX_ACC, x)
                elif event.key == pygame.K_LEFT:
                    ship.accel(-ship.MAX_ACC, x)
                elif event.key == pygame.K_UP:
                    ship.accel(-ship.MAX_ACC, y)
                elif event.key == pygame.K_DOWN:
                    ship.accel(ship.MAX_ACC, y)
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_RIGHT:
                    ship.accel(-ship.MAX_ACC, x)
                elif event.key == pygame.K_LEFT:
                    ship.accel(ship.MAX_ACC, x)
                elif event.key == pygame.K_UP:
                    ship.accel(ship.MAX_ACC, y)
                elif event.key == pygame.K_DOWN:
                    ship.accel(-ship.MAX_ACC, y)

        # GAME LOGIC

        ship.update()


        # DRAW SCREEN

        screen.fill(BLACK)

        pygame.draw.polygon(screen, ship.color, ship.points(), 1)

        pygame.display.flip()

        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    sys.exit(main())

