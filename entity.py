
import pygame
import random

import game
from game import WHITE
from game import LIGHTGREY
from game import GREY
from game import DARKGREY
from game import BLACK
from game import YELLOW

#from game import game.SCREEN_WIDTH
#from game import game.SCREEN_HEIGHT

UNIT_VECTOR = pygame.math.Vector2(0, -1)

def cap(quantity, maximum, minimum=None, rollover=False):
    if minimum is None:
        minimum = -maximum

    if not rollover:
        return min(max(quantity, -maximum), maximum)
    elif quantity > maximum:
        return quantity - maximum + minimum
    elif quantity < minimum:
        return quantity + maximum - minimum
    else:
        return quantity

def caprot(rotation, maximum=360, minimum=0):
    return cap(rotation, maximum, minimum, True)
    #if rotation > maximum:
    #    return rotation - maximum
    #elif rotation < 0:
    #    return rotation + maximum

    #return rotation

def cappos(position, maximum=game.SCREEN_VECTOR):
    return pygame.math.Vector2(
        cap(position.x, game.SCREEN_WIDTH, 0, True),
        cap(position.y, game.SCREEN_HEIGHT, 0, True)
    )

    #if position.x > maximum.x:
    #    position.x -= maximum.x
    #elif position.x < 0:
    #    position.x += maximum.x
    #if position.y > maximum.y:
    #    position.y -= maximum.y
    #elif position.y < 0:
    #    position.y += maximum.y

    #return position

class Star:
    #COLORS = [WHITE, WHITE, LIGHTGREY, BLACK]
    COLORS = [WHITE, LIGHTGREY, GREY, DARKGREY, BLACK, WHITE]
    MAX_COUNT = 3000

    def __init__(self):
        self.pos = (
            random.randint(0, game.SCREEN_WIDTH),
            random.randint(0, game.SCREEN_HEIGHT)
        )
        self.index = random.randint(0, len(self.COLORS) - 1)
        self.color = self.COLORS[self.index]
        self.count = random.randint(0, self.MAX_COUNT)

    def draw(self, screen):
        pygame.draw.line(screen, self.color, self.pos, self.pos)

    def update(self):
        if self.count != 0:
            self.count -= 1
        else:
            self.count = random.randint(0, self.MAX_COUNT)

            self.index += random.randint(-1, 1)
            self.index = cap(self.index, 1)
            self.color = self.COLORS[self.index]

class Ship:

    WIDTH  = 5
    HEIGHT = 7
    MAX_VEL = 1.75
    MIN_VEL = 0.05
    MAX_ACCEL = 0.08
    MAX_ROTVEL = 2.0

    def __init__(self, pos=(game.SCREEN_WIDTH / 2.0, game.SCREEN_HEIGHT / 2.0) ):
        self.pos = pygame.math.Vector2(pos)
        self.vel = pygame.math.Vector2(0.0, 0.0)
        self.accel = 0.0
        self.rot = 0.0
        self.rotvel = 0.0
        self.color = YELLOW

    def points(self):
        return [
            self.pos + pygame.math.Vector2(
                0, -self.HEIGHT / 2.0
            ).rotate(self.rot),

            self.pos + pygame.math.Vector2(
                self.WIDTH / 2.0, self.HEIGHT / 2.0
            ).rotate(self.rot),

            self.pos + pygame.math.Vector2(
                -self.WIDTH / 2.0, self.HEIGHT / 2.0
            ).rotate(self.rot)
        ]

    def draw(self, screen):
        pygame.draw.polygon(screen, self.color, self.points(), 1)

    def update(self):
        # debugging
        #print( "{} {}".format(self.rot, self.rotvel) )

        # update rotation
        self.rot += self.rotvel
        self.rot = caprot(self.rot)

        ## scale the velocity
        multiplier = 1.0
        ## scale acceleration so that it's more effective in the direction we're
        ## moving and less effective going against the direction we're moving
        #rotation = UNIT_VECTOR.rotate(self.rot)
        #multiplier = rotation.dot(self.vel)
        #if multiplier != 0:
        #    multiplier /= ( rotation.length() * self.vel.length() )

        #multiplier = multiplier * 0.4 + 0.6 # between 0.2 and 1.0
        #if multiplier > 0.8:
        #    multiplier = 1.0

        # update velocity
        self.vel += multiplier*self.accel * UNIT_VECTOR.rotate(self.rot)
        if self.vel.length() != 0:
            self.vel = cap(self.vel.length(), self.MAX_VEL) * self.vel.normalize()

        if self.vel.length() < self.MIN_VEL and self.accel == 0:
            self.vel = pygame.math.Vector2(0.0, 0.0)

        # update position
        self.pos += self.vel

        # wrap screen
        self.pos = cappos(self.pos)

    def accelerate(self, accel):
        self.accel += accel
        self.accel = cap(self.accel, self.MAX_ACCEL)

    def rotate(self, rotvel):
        self.rotvel += rotvel
        self.rotvel = cap(self.rotvel, self.MAX_ROTVEL)

    def handle(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                self.rotate(self.MAX_ROTVEL)
            elif event.key == pygame.K_LEFT:
                self.rotate(-self.MAX_ROTVEL)
            elif event.key == pygame.K_UP:
                self.accelerate(self.MAX_ACCEL)
            elif event.key == pygame.K_DOWN:
                self.accelerate(-self.MAX_ACCEL)
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_RIGHT:
                self.rotate(-self.MAX_ROTVEL)
            elif event.key == pygame.K_LEFT:
                self.rotate(self.MAX_ROTVEL)
            elif event.key == pygame.K_UP:
                self.accelerate(-self.MAX_ACCEL)
            elif event.key == pygame.K_DOWN:
                self.accelerate(self.MAX_ACCEL)

