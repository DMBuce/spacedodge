
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

    isdead = False
    gamechildren = []
    physchildren = []

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
    MAX_COUNT = 3000 # max length of time before a star changes colors: 50s

    def __init__(self, pos=None, player=None):
        if pos is None:
            self.pos = pygame.math.Vector2(game.randpos())
        else:
            self.pos = pygame.math.Vector2(pos)

        if player is None:
            self.goal = self
        else:
            self.goal = player

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
            self.index = cap(self.index, len(self.COLORS)-1)
            if self.color != self.COLORS[self.index]:
                self.color = self.COLORS[self.index]
                if self.index == len(self.COLORS) - 1:
                    self.gamechildren = [ SpaceHole(self) ]

class SpaceHole(Entity):
    MAX_RADIUS = 30
    #MAX_RAYLENGTH = 3
    TRANSITIONS = [ 1.0/3.0, 2.0/3.0, 5.0/6.0 ]
    NUMRAYS = 8
    RADVEL = 1.0 / 3.0
    ROTACC = 0.5
    makeboth = True

    def __init__(self, star):
        self.pos = star.pos
        self.goal = star.goal
        self.child = self._birth()
        self.radius = 0.0
        self.raylength = 0
        self.rot = 0
        self.rotvel = 5
        self.color = WHITE
        print("SpaceHole at %s incoming!" % self.pos)

    def _birth(self):
        enemychance = 0.1 # asteroidchance = 1.0 - enemychance
        diceroll = random.uniform(0.0, 1.0)
        if diceroll < enemychance:
            enemy = EnemyShip(
                self.pos,
                0.5 * EnemyShip.MAX_VEL*UNIT_VECTOR.rotate(game.randangle()),
                game.randangle()
            )
            enemy.target(self.goal)
            return enemy
        elif self.makeboth:
            return Asteroid(
                self.pos,
                random.uniform(0.01, 0.5*PlayerShip.MAX_VEL) \
                    * UNIT_VECTOR.rotate(game.randangle())
            )
        else:
            self.isdead = True

    def _raylonger(self):
        for t in self.TRANSITIONS:
            r = t * self.MAX_RADIUS
            if r < self.radius <= r + self.RADVEL:
                return True

        return False

        #if self.MAX_RADIUS * 2.0/3 + self.RADVEL > self.radius >= self.MAX_RADIUS * 2.0/3:
        #elif self.MAX_RADIUS * 5.0/6 + self.RADVEL > self.radius >= self.MAX_RADIUS * 5.0/6:

    def update(self):
        self.radius += self.RADVEL
        if self._raylonger():
            self.raylength += 1

        #if self.MAX_RADIUS * 2.0/3 + self.RADVEL > self.radius >= self.MAX_RADIUS * 2.0/3:
        ##if self.radius % 3 == 0 and self.raylength < self.MAX_RAYLENGTH:
        #    self.raylength += 1
        #elif self.MAX_RADIUS * 5.0/6 + self.RADVEL > self.radius >= self.MAX_RADIUS * 5.0/6:
        #    self.raylength += 1

        self.rotvel += self.ROTACC
        self.rot += self.rotvel

        if self.radius >= self.MAX_RADIUS:
            self.isdead = True
            self.physchildren = [ self.child ]

    def lines(self):
        retval = []
        for i in range(self.NUMRAYS):
            angle = UNIT_VECTOR.rotate(i * 360 / self.NUMRAYS + self.rot)
            ray = (
                self.pos + (self.radius) * angle,
                self.pos + (self.radius + self.raylength) * angle
            )
            retval.append( ray )

        return retval

    def draw(self, screen):
        for points in self.lines():
            #self.rect =
            pygame.draw.polygon(screen, self.color, points, 1)

class Asteroid(Entity):
    MIN_RADIUS = 6
    def __init__(self, pos, vel, radius=None):
        self.pos = pygame.math.Vector2(pos)
        self.vel = pygame.math.Vector2(vel)
        self.color = WHITE
        if radius == None:
            self.radius = random.randint(self.MIN_RADIUS, 30)
        else:
            self.radius = radius

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
        if isinstance(other, Asteroid):
            return

        self.destroy()
        if recurse:
            other.interact(self, False)

    def destroy(self):
        self.isdead = True
        self.gamechildren = Debris.scrap(self)
        if self.radius >= 2*self.MIN_RADIUS:
            for i in range(2):
                self.physchildren = [ self._birth() for i in range(2) ]

    def _birth(self):
        v = pygame.math.Vector2(self.vel)
        v += 0.1*v.length() * UNIT_VECTOR.rotate(game.randangle())
        return Asteroid(self.pos, v, self.radius // 2)

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
        self.destroy()
        if recurse:
            other.interact(self, False)

    def destroy(self):
        self.isdead = True
        self.gamechildren = Debris.scrap(self)

class Debris(Entity):
    BASE_ROTVEL = 5
    MIN_VEL = 0.5

    def __init__(self, ship, i, vel):
        segments = ship.points()
        j = i+1
        if len(segments) == j:
            j = 0

        segments = [ segments[i], segments[j] ]
        self.pos = ( segments[0] + segments[1] ) / 2.0
        self.ends = [ segment - self.pos for segment in segments ]
        self.vel = vel
        if self.vel.length() == 0:
            self.vel = self.MIN_VEL * UNIT_VECTOR.rotate(game.randangle())
        elif self.vel.length() < self.MIN_VEL:
            self.vel.scale_to_length(self.MIN_VEL)

        self.rotvel = self.BASE_ROTVEL + random.randint(-2, 2)
        self.color = ship.color

        #print("%s %s %s" % (self.pos, ship.pos, self.points()) )

    # factory method for making a pile of debris from an object
    def scrap(entity):
        retval = []
        for i in range(len(entity.points())):
            vel = pygame.math.Vector2(entity.vel)
            vel += 0.3*vel.length() * UNIT_VECTOR.rotate(game.randangle())
            retval.append( Debris(entity, i, vel) )

        # drop no more than 3 pieces of debris
        while len(retval) > 3:
            retval.pop( random.randint(0, len(retval) - 1) )

        return retval

    def update(self):
        # update rotation
        self.ends = [ end.rotate(self.rotvel) for end in self.ends ]

        # update position
        self.pos += self.vel

        # wrap screen
        if self.pos != cappos(self.pos):
            self.isdead = True

    def points(self):
        return [ self.pos + end for end in self.ends ]

    def draw(self, screen):
        self.rect = pygame.draw.polygon(screen, self.color, self.points(), 1)

class EnemyShip(Ship):

    def __init__(self, pos, vel, rot):
        super(EnemyShip, self).__init__(pos, vel, rot)
        self.count = 120 # 2 seconds
        self.update = self.cooldown
        self.goal = self

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

    def destroy(self):
        super().destroy()
        self.pos = pygame.math.Vector2(game.SCREEN_WIDTH / 2.0, game.SCREEN_HEIGHT / 2.0)

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

