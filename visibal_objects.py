import pygame
import random
import math


TIME_BETWEEN_EACH_GAME_REFRESH = 0.017

WINDOW_WIDTH = 700
WINDOW_HEIGHT = 500


MAP_LIMITS = (-1000, -1000, 1000, 1000)

SPAWNRATE = 0.008

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

BULLET_SIZE = (15,15)
BULLET_IMG_FILE_PATH = "res\\Extras\\PowerOre.png"
bullet_img = pygame.image.load(BULLET_IMG_FILE_PATH)
bullet_img = pygame.transform.scale(bullet_img, BULLET_SIZE)
bullet_img.set_colorkey(PINK)
temp_img = None


class VisibleObject(pygame.sprite.Sprite):
    def __init__(self, position, size):    # position is a tuple: (x, y)
        super().__init__()
        self.position = pygame.math.Vector2(position[0], position[1])
        self.velocityx = 0
        self.velocityy = 0
        self.width = size[0]
        self.height = size[1]

    def update(self):
        if self.velocityx != 0 or self.velocityy != 0:
            self.position += pygame.math.Vector2(self.velocityx, self.velocityy).normalize()
            self.put_in_border()

    def draw(self, surface, perspective):
        pass

    def put_in_border(self):
        hit_border = False
        if self.position.x < MAP_LIMITS[0]:
            self.position.x = MAP_LIMITS[0]
            hit_border = True
        if self.position.x + self.width > MAP_LIMITS[2]:
            self.position.x = MAP_LIMITS[2] - self.width
            hit_border = True
        if self.position.y < MAP_LIMITS[1]:
            self.position.y = MAP_LIMITS[1]
            hit_border = True
        if self.position.y + self.height> MAP_LIMITS[3]:
            self.position.y = MAP_LIMITS[3] - self.height
            hit_border = True
        return hit_border

    def check_collision(self, other):
        self_rect = pygame.Rect(self.position.x, self.position.y, self.width, self.height)
        other_rect = pygame.Rect(other.position.x, other.position.y, other.width, other.height)
        return self_rect.colliderect(other_rect)


class Character(VisibleObject):
    MS = 2

    def __init__(self, start_pos, size):
        self.hp = 100
        super().__init__(start_pos, size)
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
    MS = 7

    def __init__(self):
        self.kill_cnt = 0
        super().__init__((0, 0), PLAYER_SIZE)


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

    def shoot(self, target):
        return Bullet(self, target)

    def walk_up(self):
        self.velocityy -= self.MS

    def walk_down(self):
        self.velocityy += self.MS

    def walk_left(self):
        self.velocityx -= self.MS

    def walk_right(self):
        self.velocityx += self.MS


class Enemy(Character):
    MS = 3
    DISTANCE_TO_ACTIVATE = 500
    ATTACK_COOLDOWN_CONST = 0.2
    ENEMY_DAMAGE = 7

    def __init__(self, start_pos):
        super().__init__(start_pos, ENEMY_SIZE)
        self.target = None
        self.attack_cooldown = 1

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
            if self.attack_cooldown < 1:
                self.attack_cooldown += self.ATTACK_COOLDOWN_CONST
        else:
            self.is_moving = False
            self.animation += ENEMY_ANIMATION_SPEED
            if self.animation > ENEMY_IDLE_ANIMATION_LENGTH:
                self.animation = 0

    def update_target(self, players):
        new_target = None
        for player in players:
            if new_target is None or player.position.distance_to(self.position) < new_target.position.distance_to(self.position):
                if player.position.distance_to(self.position) <= self.DISTANCE_TO_ACTIVATE:
                    new_target = player
        self.target = new_target

    def attack(self, players):
        if self.attack_cooldown >= 1:
            for player in players:
                if self.check_collision(player):
                    self.deal_damage(player)

    def deal_damage(self, player):
        player.hp -= self.ENEMY_DAMAGE
        self.attack_cooldown = 0
        if player.hp <= 0:
            player.kill()


class Bullet(VisibleObject):
    MS = 13
    MAX_TRAVEL = 500
    BULLET_DMG = 40

    def __init__(self, owner, target):
        self.owner = owner
        super().__init__((owner.position.x, owner.position.y), BULLET_SIZE)
        if self.position.move_towards(target, self.MS) - self.position == pygame.Vector2(0,0):
            target = pygame.math.Vector2(target.x+1, target.y)
        move_vector = (self.position.move_towards(target, self.MS) - self.position)
        move_vector.scale_to_length(self.MS)
        self.velocityx = move_vector.x
        self.velocityy = move_vector.y
        self.distance_traveled = 0

    def update(self):
        if self.distance_traveled >= self.MAX_TRAVEL:
            self.kill()
        else:
            self.distance_traveled += math.sqrt(self.velocityx**2 + self.velocityy**2)
            self.position += pygame.math.Vector2(self.velocityx, self.velocityy)
            if self.put_in_border():
                self.kill()

    def draw(self,surface, perspective=(0,0)):
        pos = (self.position.x - perspective[0] + WINDOW_WIDTH / 2 - BULLET_SIZE[0] / 2,
               self.position.y - perspective[1] + WINDOW_HEIGHT / 2 - BULLET_SIZE[1] / 2)
        surface.blit(bullet_img, pos)

    def hit(self, enemies):
        for enemy in enemies:
            if self.check_collision(enemy):
                self.deal_damage(enemy)

    def deal_damage(self, enemy):
        self.kill()
        enemy.hp -= self.BULLET_DMG
        if enemy.hp <= 0:
            self.owner.kill_cnt += 1
            enemy.kill()


def createenemy(num_of_players):
    if not num_of_players == 0 and SPAWNRATE != 0:
        if random.randint(0,int(1/(SPAWNRATE*num_of_players))) == 0:
            x_pos = random.randint(MAP_LIMITS[0], MAP_LIMITS[2])
            y_pos = random.randint(MAP_LIMITS[1], MAP_LIMITS[3])
            return Enemy((x_pos, y_pos))
    return None


