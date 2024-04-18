import pygame

TIME_BETWEEN_EACH_GAME_REFRESH = 0.017
PLAYER_ANIMATION_SPEED = 0.3
PLAYER_SIZE = (40, 50)
WINDOW_WIDTH = 700
WINDOW_HEIGHT = 500

PINK = (255, 174, 201, 0)
character_move_files_prefix = "res\\Full body animated characters\\Char 1\\with hands\\walk_"
PLAYER_WALK_ANIMATION_LENGTH = 8
moving_animation = []
for i in range(PLAYER_WALK_ANIMATION_LENGTH):

    img = pygame.image.load(character_move_files_prefix + str(i) + ".png")
    img.set_colorkey(PINK)
    img = pygame.transform.scale(img, PLAYER_SIZE)
    moving_animation.append(img)

character_move_files_prefix = "res\\Full body animated characters\\Char 1\\with hands\\idle_"
PLAYER_IDLE_ANIMATION_LENGTH = 6
idle_animation = []
for i in range(PLAYER_IDLE_ANIMATION_LENGTH):
    img = pygame.image.load(character_move_files_prefix + str(i) + ".png")
    img.set_colorkey(PINK)
    img = pygame.transform.scale(img, PLAYER_SIZE)
    idle_animation.append(img)
img = ''


class VisibleObject(pygame.sprite.Sprite):
    def __init__(self, position):    # position is a tuple: (x, y)
        super().__init__()
        self.position = pygame.math.Vector2(position[0], position[1])
        self.velocityx = 0
        self.velocityy = 0

    def update(self):
        self.position += pygame.math.Vector2(self.velocityx, self.velocityy).normalize()

    def draw(self, surface, perspective):
        pass


class Player(VisibleObject):
    MS = 3.5

    def __init__(self):
        super().__init__((0, 0))
        self.is_moving = False
        self.animation = 0
        self.facing_left = False

    def draw(self, surface, perspective=(0, 0)):
        # make camera follow the position of the player
        pos = (self.position.x - perspective[0] + WINDOW_WIDTH/2 - PLAYER_SIZE[0]/2,
               self.position.y - perspective[1] + WINDOW_HEIGHT/2 - PLAYER_SIZE[1]/2)
        if self.is_moving:
            if self.animation > PLAYER_WALK_ANIMATION_LENGTH:
                self.animation = 0
            walk_img = moving_animation[int(self.animation)].convert().copy()
            if self.facing_left:
                walk_img = pygame.transform.flip(walk_img, True, False)
            surface.blit(walk_img, pos)
        else:
            if self.animation > PLAYER_IDLE_ANIMATION_LENGTH:
                self.animation = 0
            idle_img = idle_animation[int(self.animation)].convert().copy()
            if self.facing_left:
                idle_img = pygame.transform.flip(idle_img, True, False)
            surface.blit(idle_img, pos)

    def update(self):
        move_vector = pygame.math.Vector2(self.velocityx, self.velocityy)
        if move_vector.length() != 0:    # if the player is moving now
            self.is_moving = True
            self.animation += PLAYER_ANIMATION_SPEED
            if self.animation > PLAYER_WALK_ANIMATION_LENGTH:
                self.animation = 0
            move_vector.scale_to_length(self.MS)
            self.position += move_vector

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

