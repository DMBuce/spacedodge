
import pygame
import random

import game
from game import WHITE
from game import LIGHTGREY
from game import GREY
from game import DARKGREY
from game import BLACK
from game import YELLOW
from game import PINK

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

def cappos(position, maximum=game.SCREEN_VECTOR):
    return pygame.math.Vector2(
        cap(position.x, game.SCREEN_WIDTH, 0, True),
        cap(position.y, game.SCREEN_HEIGHT, 0, True)
    )

class Entity:
    """Interface for all Space Dodge game objects."""

    def update(self):
        raise NotImplementedError(
            "Class %s doesn't implement update()" % self.__class__.__name__
        )

    def draw(self, screen):
        raise NotImplementedError(
            "Class %s doesn't implement draw()" % self.__class__.__name__
        )

    def touches(self, other):
        if self.rect is not None and other.rect is not None:
            return pygame.sprite.collide_rect(self, other)
        else:
            return False

    def interact(self, other):
        raise NotImplementedError(
            "Class %s doesn't implement interact()" % self.__class__.__name__
        )

class Star(Entity):
    COLORS = [WHITE, LIGHTGREY, GREY, DARKGREY, BLACK, WHITE]
    MAX_COUNT = 3000

    def __init__(self):
        self.pos = game.randpos()
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

class Asteroid(Entity):
    def __init__(self, pos, vel):
        self.pos = pygame.math.Vector2(pos)
        self.vel = pygame.math.Vector2(vel)
        self.color = WHITE
        self.radius = random.randint(2, 30)
        self.corners = self._mkcorners()
        self.rect = None
        self.lastcolor = self.color

    def _mkcorners(self):
        num = random.randint(6, 9)
        retval = []
        for i in range(num):
            corner = UNIT_VECTOR.rotate(i * 360.0 / num)
            corner.scale_to_length(self.radius + random.randint(-2, 3))
            retval.append(corner)

        return retval

    def points(self):
        retval = []
        for p in self.corners:
            retval.append(self.pos + p)

        return retval

    def draw(self, screen):
        self.rect = pygame.draw.polygon(screen, self.color, self.points(), 1)

    def update(self):
        # update position
        self.pos += self.vel

        # wrap screen
        self.pos = cappos(self.pos)

    def interact(self, other, recurse=True):
        #self.destroy()
        if other.color != self.lastcolor and other.lastcolor != self.color:
            (self.lastcolor, other.lastcolor) = (self.color, other.color)
            (self.color, other.color) = (other.color, self.color)

        if recurse:
            other.interact(self, False)

class Ship(Entity):
    WIDTH  = 5
    HEIGHT = 7
    MAX_VEL = 1.75
    MIN_VEL = 0.05
    MAX_ACCEL = 0.08
    MAX_ROTVEL = 2.0

    def __init__(self, pos, vel, rot):
        self.pos = pygame.math.Vector2(pos)
        self.vel = pygame.math.Vector2(vel)
        self.rot = rot
        self.accel = 0.0
        self.rotvel = 0.0
        self.color = YELLOW
        self.rect = None
        self.lastcolor = self.color

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
        self.rect = pygame.draw.polygon(screen, self.color, self.points(), 1)

    def accelerate(self, accel):
        self.accel += accel
        self.accel = cap(self.accel, self.MAX_ACCEL)

    def rotate(self, rotvel):
        self.rotvel += rotvel
        self.rotvel = cap(self.rotvel, self.MAX_ROTVEL)

    def update(self):
        # update rotation
        self.rot += self.rotvel
        self.rot = caprot(self.rot)

        # update velocity
        self.vel += self.accel * UNIT_VECTOR.rotate(self.rot)
        if self.vel.length() != 0:
            self.vel = cap(self.vel.length(), self.MAX_VEL) * self.vel.normalize()

        if self.vel.length() < self.MIN_VEL and self.accel == 0:
            self.vel = pygame.math.Vector2(0.0, 0.0)

        # update position
        self.pos += self.vel

        # wrap screen
        self.pos = cappos(self.pos)

    def interact(self, other, recurse=True):
        #self.destroy()
        if other.color != self.lastcolor and other.lastcolor != self.color:
            (self.lastcolor, other.lastcolor) = (self.color, other.color)
            (self.color, other.color) = (other.color, self.color)

        if recurse:
            other.interact(self, False)

class StationaryTarget:
    def __init__(self, pos):
        self.pos = pos

class EnemyShip(Ship):

    def __init__(self, pos, vel, rot):
        super(EnemyShip, self).__init__(pos, vel, rot)
        self.count = 120 # 2 seconds
        self.update = self.cooldown
        self.goal = StationaryTarget(
            (game.SCREEN_WIDTH / 2.0, game.SCREEN_HEIGHT / 2.0)
        )

    def cooldown(self):
        if self.count > 0:
            self.count -= 1
        else:
            self.accel = self.MAX_ACCEL
            self.update = self.seek

        super(EnemyShip, self).update()

    def target(self, goal):
        self.goal = goal

    def seek(self):
        targetheading = self.goal.pos - self.pos
        currentheading = self.vel

        crossproduct = currentheading.cross(targetheading)
        angle = currentheading.angle_to(targetheading)
        if crossproduct >= 0:
            self.rotvel = self.MAX_ROTVEL
        elif crossproduct <= 0:
            self.rotvel = -self.MAX_ROTVEL
        else:
            self.rotvel = 0.0

        super(EnemyShip, self).update()

class PlayerShip(Ship):

    def __init__(self,
        pos=(game.SCREEN_WIDTH / 2.0, game.SCREEN_HEIGHT / 2.0),
        vel=(0.0, 0.0),
        rot=0.0
    ):
        super(PlayerShip, self).__init__(pos, vel, rot)
        self.color = PINK

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

