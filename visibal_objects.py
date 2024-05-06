import pygame
import random

TIME_BETWEEN_EACH_GAME_REFRESH = 0.017

WINDOW_WIDTH = 700
WINDOW_HEIGHT = 500

NO_ENEMY_AREA_X = (-50, 50)
NO_ENEMY_AREA_Y = (-50, 50)

MAP_LIMITS = (-100, -100, 100, 100)

SPAWNRATE = 0.01

PINK = (255, 174, 201, 0)


PLAYER_ANIMATION_SPEED = 0.3
PLAYER_SIZE = (40, 50)
player_move_files_prefix = "res\\Full body animated characters\\Char 1\\with hands\\walk_"
PLAYER_WALK_ANIMATION_LENGTH = 8
player_moving_animation = []
for i in range(PLAYER_WALK_ANIMATION_LENGTH):

    temp_img = pygame.image.load(player_move_files_prefix + str(i) + ".png")
    temp_img.set_colorkey(PINK)
    temp_img = pygame.transform.scale(temp_img, PLAYER_SIZE)
    player_moving_animation.append(temp_img)

player_move_files_prefix = "res\\Full body animated characters\\Char 1\\with hands\\idle_"
PLAYER_IDLE_ANIMATION_LENGTH = 6
player_idle_animation = []
for i in range(PLAYER_IDLE_ANIMATION_LENGTH):
    temp_img = pygame.image.load(player_move_files_prefix + str(i) + ".png")
    temp_img.set_colorkey(PINK)
    temp_img = pygame.transform.scale(temp_img, PLAYER_SIZE)
    player_idle_animation.append(temp_img)


ENEMY_ANIMATION_SPEED = 0.2
ENEMY_SIZE = (40, 50)

enemy_idle_files_prefix = "res\\Full body animated characters\\Enemies\\Enemy 1\\idle_"
ENEMY_IDLE_ANIMATION_LENGTH = 6
enemy_idle_animation = []
for i in range(ENEMY_IDLE_ANIMATION_LENGTH):
    temp_img = pygame.image.load(enemy_idle_files_prefix + str(i) + ".png")
    temp_img.set_colorkey(PINK)
    temp_img = pygame.transform.scale(temp_img, PLAYER_SIZE)
    enemy_idle_animation.append(temp_img)

enemy_walk_files_prefix = "res\\Full body animated characters\\Enemies\\Enemy 1\\walk_"
ENEMY_WALK_ANIMATION_LENGTH = 8
enemy_walk_animation = []
for i in range(ENEMY_WALK_ANIMATION_LENGTH):
    temp_img = pygame.image.load(enemy_walk_files_prefix + str(i) + ".png")
    temp_img.set_colorkey(PINK)
    temp_img = pygame.transform.scale(temp_img, PLAYER_SIZE)
    enemy_walk_animation.append(temp_img)


temp_img = None


class VisibleObject(pygame.sprite.Sprite):
    def __init__(self, position):    # position is a tuple: (x, y)
        super().__init__()
        self.position = pygame.math.Vector2(position[0], position[1])
        self.velocityx = 0
        self.velocityy = 0

    def update(self):
        if self.velocityx != 0 or self.velocityy != 0:
            self.position += pygame.math.Vector2(self.velocityx, self.velocityy).normalize()

    def draw(self, surface, perspective):
        pass

    def put_in_border(self):
        if self.position.x < MAP_LIMITS[0]:
            self.position.x = MAP_LIMITS[0]
        if self.position.x > MAP_LIMITS[2]:
            self.position.x = MAP_LIMITS[2]
        if self.position.y < MAP_LIMITS[1]:
            self.position.y = MAP_LIMITS[1]
        if self.position.y > MAP_LIMITS[3]:
            self.position.y = MAP_LIMITS[3]

class Character(VisibleObject):
    MS = 2

    def __init__(self, start_pos):
        super().__init__(start_pos)
        self.animation = 0
        self.facing_left = False
        self.is_moving = False

    def draw(self,  surface, animation_list, perspective=(0, 0)):
        pos = (self.position.x - perspective[0] + WINDOW_WIDTH / 2 - PLAYER_SIZE[0] / 2,
               self.position.y - perspective[1] + WINDOW_HEIGHT / 2 - PLAYER_SIZE[1] / 2)
        if self.animation > len(animation_list) - 1:
            self.animation = 0
        img = animation_list[int(self.animation)].convert().copy()
        if self.facing_left:
            img = pygame.transform.flip(img, True, False)
        surface.blit(img, pos)


class Player(Character):
    MS = 3.5

    def __init__(self):
        super().__init__((0, 0))

    def draw(self, surface, perspective=(0, 0)):
        animation_list = player_idle_animation
        if self.is_moving:
            animation_list = player_moving_animation
        super().draw(surface, animation_list, perspective=perspective)

    def update(self):
        move_vector = pygame.math.Vector2(self.velocityx, self.velocityy)
        if move_vector.length() != 0:    # if the player is moving now
            self.is_moving = True
            self.animation += PLAYER_ANIMATION_SPEED
            if self.animation > PLAYER_WALK_ANIMATION_LENGTH:
                self.animation = 0
            move_vector.scale_to_length(self.MS)
            self.position += move_vector
            self.put_in_border()
            if move_vector.x < 0:
                self.facing_left = True
            elif move_vector.x > 0:
                self.facing_left = False
        elif self.is_moving:    # if the character was moving
            self.animation = 0
            self.is_moving = False
        else:    # the character is idle
            self.animation += PLAYER_ANIMATION_SPEED
            if self.animation > PLAYER_IDLE_ANIMATION_LENGTH:
                self.animation = 0

    def walk_up(self):
        self.velocityy -= self.MS

    def walk_down(self):
        self.velocityy += self.MS

    def walk_left(self):
        self.velocityx -= self.MS

    def walk_right(self):
        self.velocityx += self.MS


class Enemy(Character):
    MS = 2.5

    def __init__(self, start_pos):
        super().__init__(start_pos)
        self.target = None

    def draw(self, surface, perspective=(0, 0)):
        animation_list = enemy_idle_animation
        if self.is_moving:
            animation_list = enemy_walk_animation
        super().draw(surface, animation_list, perspective=perspective)

    def update(self):
        if self.target is not None:

            self.is_moving = True
            move_vector = self.position.move_towards(self.target.position, self.MS) - self.position
            if move_vector.x > 0:
                self.facing_left = False
            if move_vector.x < 0:
                self.facing_left = True
            self.position += move_vector
            self.put_in_border()
            self.animation += ENEMY_ANIMATION_SPEED
            if self.animation > ENEMY_WALK_ANIMATION_LENGTH:
                self.animation = 0
        else:
            self.is_moving = False
            self.animation += ENEMY_ANIMATION_SPEED
            if self.animation > ENEMY_IDLE_ANIMATION_LENGTH:
                self.animation = 0


def CreateEnemy():
    if random.randint(0,int(1/SPAWNRATE)) == 0:
        x_pos = 0
        y_pos = 0

        print("enemy created in: " + str(x_pos) + " " + str(y_pos))
        return Enemy((x_pos, y_pos))
    return None


