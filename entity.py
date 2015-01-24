
import pygame
import random

import game

# colors
BLACK     = (  0,   0,   0)
DARKGREY  = (191, 191, 191)
GREY      = (127, 127, 127)
LIGHTGREY = ( 63,  63,  63)
WHITE     = (255, 255, 255)
PINK      = (255,  20, 147)
YELLOW    = (255, 255,   0)
CYAN      = (  0, 255, 255)

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

def cappos(position, maximum=None):
    if maximum is None:
        maximum = pygame.math.Vector2( game.width(), game.height() )

    return pygame.math.Vector2(
        cap(position.x, game.width(), 0, True),
        cap(position.y, game.height(), 0, True)
    )

def init(game):
    Entity._game = game

def getgame():
    return Entity._game

# TODO: simplify physics by removing some of: _isphysical, rect, touches(), interact()
class Entity:
    """Interface for all Space Dodge game objects."""

    _isdead = False
    _isphysical = False
    _children = []
    rect = None

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

    def children(self):
        return self._children

    def poop(self):
        retval = self._children
        self._children = []
        return retval

    def isdead(self):
        return self._isdead

    def isphysical(self):
        return self._isphysical

class Star(Entity):
    COLORS = [WHITE, LIGHTGREY, GREY, DARKGREY, BLACK, WHITE]
    MAX_BLINKTIME = 3000 # max length of time before a star changes colors: 50s

    def __init__(self, pos=None, lifetime=-1):
        if pos is None:
            print( game.randpos() )
            self.pos = pygame.math.Vector2(game.randpos())
        else:
            self.pos = pygame.math.Vector2(pos)

        self.index = random.randint(0, len(self.COLORS) - 1)
        self.color = self.COLORS[self.index]
        self.blinktime = random.randint(0, self.MAX_BLINKTIME)
        self.lifetime = lifetime

    def draw(self, screen):
        pygame.draw.line(screen, self.color, self.pos, self.pos)

    def update(self):
        if self.lifetime == -1:
            pass
        elif self.lifetime == 0:
            self._isdead = True
        else:
            self.lifetime -= 1

        if self.blinktime != 0:
            self.blinktime -= 1
        else:
            self.blinktime = random.randint(0, self.MAX_BLINKTIME)

            self.index += random.randint(-1, 1)
            self.index = cap(self.index, len(self.COLORS)-1)
            if self.color != self.COLORS[self.index]:
                self.color = self.COLORS[self.index]
                if self.index == len(self.COLORS) - 1:
                    self._children = [ SpaceHole(self) ]

class ShootingStar(Entity):
    MAX_VEL = 0.5
    WIDTH  = 3
    HEIGHT = 3
    TRAILTIME = 1800 # 5 minutes
    _num = 0

    def __init__(self, color=CYAN):
        ShootingStar._num += 1
        self.color = color
        self.pos = pygame.math.Vector2( game.randpos(edge=True) )
        self.vel = pygame.math.Vector2( game.width()/2, game.height()/2 ) - self.pos
        self.vel.scale_to_length(self.MAX_VEL)
        self.rect = None
        self._isphysical = True

    def update(self):
        self.pos += self.vel

        # poop a trail of stars
        if random.randint(0, 3) == 0:
            dr = self.vel.rotate(90)
            dr.scale_to_length(1)
            dr *= random.uniform(-1, 1) * self.WIDTH
            self._children.append(Star(self.pos + dr, self.TRAILTIME))

        # leave screen
        if self.pos != cappos(self.pos):
            self._isdead = True
            ShootingStar._num -= 1

    def number(self=None):
        return ShootingStar._num

    def points(self):
        retval = []
        for i in [ self.WIDTH/2, -self.WIDTH/2 ]:
            for j in [ i, -i ]:
                retval.append( pygame.math.Vector2(self.pos.x + i, self.pos.y + j) )

        return retval

    def draw(self, screen):
        self.rect = pygame.draw.polygon(screen, self.color, self.points())

    def interact(self, other):
        if isinstance(other, Ship):
            Ship.MAX_SHIELDING += Ship.SHIELD_PER_SHIELDING
            self._isdead = True
            ShootingStar._num -= 1

class SpaceHole(Entity):
    MAX_RADIUS = 30
    TRANSITIONS = [ 1.0/3.0, 2.0/3.0, 5.0/6.0 ]
    NUMRAYS = 8
    RADVEL = 1.0 / 3.0
    ROTACC = 0.5
    makeboth = True

    def __init__(self, star):
        self.pos = star.pos
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

            # mutate enemies
            if diceroll <= 0.005:
                enemy.MAX_VEL += random.uniform(0.0, 1.0)
            elif 0.005 < diceroll <= 0.010:
                enemy.MAX_ROTVEL += random.uniform(0.0, 1.0)
            elif 0.010 < diceroll <= 0.015:
                enemy.shielding += 1

            return enemy
        elif self.makeboth:
            return Asteroid(
                self.pos,
                random.uniform(0.01, 0.5*PlayerShip.MAX_VEL) \
                    * UNIT_VECTOR.rotate(game.randangle())
            )
        else:
            self._isdead = True

    def _raylonger(self):
        for t in self.TRANSITIONS:
            r = t * self.MAX_RADIUS
            if r < self.radius <= r + self.RADVEL:
                return True

        return False

    def update(self):
        self.radius += self.RADVEL
        if self._raylonger():
            self.raylength += 1

        self.rotvel += self.ROTACC
        self.rot += self.rotvel

        if self.radius >= self.MAX_RADIUS:
            self._isdead = True
            self._children = [ self.child ]

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
            pygame.draw.polygon(screen, self.color, points, 1)

class Asteroid(Entity):
    MIN_RADIUS = 6
    _isphysical = True
    def __init__(self, pos, vel, radius=None):
        self.pos = pygame.math.Vector2(pos)
        self.vel = pygame.math.Vector2(vel)
        self.color = WHITE
        if radius is None:
            self.radius = random.randint(self.MIN_RADIUS, 30)
        else:
            self.radius = radius

        self.corners = self._mkcorners()
        self.rect = None

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

    def interact(self, other):
        if isinstance(other, Ship):
            self.destroy()

    def destroy(self):
        self._isdead = True
        self._children = Debris.scrap(self)
        if self.radius >= 2*self.MIN_RADIUS:
            dv = random.uniform(0.0, 1.0) * UNIT_VECTOR.rotate(game.randangle())
            self._children += [ self._birth(i*dv) for i in [-1, 1] ]

    def _birth(self, dv):
        v = pygame.math.Vector2(self.vel)
        v += 0.3*v.length() * UNIT_VECTOR.rotate(game.randangle())
        v += dv
        return Asteroid(self.pos, v, self.radius // 2)

class Ship(Entity):
    WIDTH  = 5
    HEIGHT = 7
    MAX_VEL = 1.75
    MIN_VEL = 0.05
    MAX_ACCEL = 0.08
    MAX_ROTVEL = 2.0
    SHIELDCORNERS = 12
    MIN_SHIELDRADIUS = 7
    MAX_SHIELDING = 1
    SHIELD_PER_SHIELDING = 4
    _isphysical = True

    def __init__(self, pos, vel, rot):
        self.pos = pygame.math.Vector2(pos)
        self.vel = pygame.math.Vector2(vel)
        self.rot = rot
        self.accel = 0.0
        self.rotvel = 0.0
        self.color = YELLOW
        self.rect = None
        self.shielding = 0

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

    def shieldpoints(self, n):
        num = self.SHIELDCORNERS
        retval = []
        for i in range(num):
            corner = UNIT_VECTOR.rotate(22.5 + i * 360.0 / num)
            corner.scale_to_length(self.MIN_SHIELDRADIUS + 4.5*n/self.SHIELD_PER_SHIELDING)
            retval.append(self.pos + corner)

        return retval

    def draw(self, screen):
        self.rect = pygame.draw.polygon(screen, self.color, self.points(), 1)
        for i in range(self.shielding):
            if i % self.SHIELD_PER_SHIELDING == (self.shielding - 1) % self.SHIELD_PER_SHIELDING:
                self.rect = pygame.draw.polygon(screen, self.color, self.shieldpoints(i), 1)

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

    def interact(self, other):
        if isinstance(other, Debris):
            self.shielding = cap(self.shielding + 1, self.MAX_SHIELDING, 0)
        elif isinstance(other, ShootingStar):
            pass
        elif self.shielding:
            #self.shielding = cap(self.shielding - 3, self.MAX_SHIELDING, 0)
            self.shielding -= self.SHIELD_PER_SHIELDING
            if self.shielding < 0:
                self.shielding = 0
        else:
            self.destroy()

    def destroy(self):
        self._isdead = True
        self._children = Debris.scrap(self)

class Debris(Entity):
    BASE_ROTVEL = 5
    MIN_VEL = 0.5

    def __init__(self, ship, i, vel):
        self._isphysical = True
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

        # leave screen
        if self.pos != cappos(self.pos):
            self._isdead = True

    def points(self):
        return [ self.pos + end for end in self.ends ]

    def draw(self, screen):
        self.rect = pygame.draw.polygon(screen, self.color, self.points(), 1)

    def interact(self, other):
        if isinstance(other, Ship):
            self._isdead = True

class EnemyShip(Ship):

    def __init__(self, pos, vel, rot):
        super(EnemyShip, self).__init__(pos, vel, rot)
        self.count = 120 # 2 seconds
        self.update = self.cooldown

    def cooldown(self):
        if self.count > 0:
            self.count -= 1
        else:
            self.accel = self.MAX_ACCEL
            self.update = self.seek

        super(EnemyShip, self).update()

    def seek(self):
        targetheading = getgame().player().pos - self.pos
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
        pos=None,
        vel=(0.0, 0.0),
        rot=0.0
    ):
        if pos is None:
            pos = (game.width() / 2.0, game.height() / 2.0)

        super(PlayerShip, self).__init__(pos, vel, rot)
        self.lastshielding = self.shielding
        self.color = PINK

    def update(self):
        super().update()
        if self.lastshielding != self.MAX_SHIELDING \
        and self.shielding == self.MAX_SHIELDING \
        and ShootingStar.number() == 0:
            self._children.append(ShootingStar())

        self.lastshielding = self.shielding

    def destroy(self):
        super().destroy()
        self.pos = pygame.math.Vector2(game.width() / 2.0, game.height() / 2.0)
        self._children.append( RestartText(self) )

    def reset(self):
        self.__init__()
        self._isdead = False
        Ship.MAX_SHIELDING = 1
        getgame().player(self)

    def handle(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                self.rotate(self.MAX_ROTVEL)
            elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                self.rotate(-self.MAX_ROTVEL)
            elif event.key == pygame.K_UP or event.key == pygame.K_w:
                self.accelerate(self.MAX_ACCEL)
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.accelerate(-self.MAX_ACCEL)
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                self.rotate(-self.MAX_ROTVEL)
            elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                self.rotate(self.MAX_ROTVEL)
            elif event.key == pygame.K_UP or event.key == pygame.K_w:
                self.accelerate(-self.MAX_ACCEL)
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.accelerate(self.MAX_ACCEL)
            elif event.key == pygame.K_SPACE and self.isdead():
                self.reset()

class RestartText(Entity):
    def __init__(self, ship):
        self.ship = ship
        self.pos = ship.pos
        self.drawn = False
        self.image = pygame.image.load("continue.png")
        self.imagerect = self.image.get_rect()
        self.imagerect.center = self.pos

    def update(self):
        if not self.ship.isdead():
            self._isdead = True

    def draw(self, screen):
        #text = self.font.render("Space to restart", True, ship.color)
        screen.blit( self.image, self.imagerect )
        self.drawn = True

# vim: set expandtab shiftwidth=4 softtabstop=4:
