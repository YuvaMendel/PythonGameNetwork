import pygame


class VisibleObject(pygame.sprite.Sprite):
    def __init__(self, position):    # position is a tuple: (x, y)
        super().__init__()
        self.position = pygame.math.Vector2(position[0], position[1])
        self.velocityx = 0
        self.velocityy = 0

    def update(self):
        self.position += pygame.math.Vector2(self.velocityx, self.velocityy).normalize()

    def draw(self, surface):
        pass


class Player(VisibleObject):
    MS = 10

    def __init__(self):
        super().__init__((0, 0))

    def draw(self, surface):
        pygame.draw.circle(surface, (255, 0, 0), self.position, 10)

    def update(self):
        move_vector = pygame.math.Vector2(self.velocityx, self.velocityy)
        if move_vector.length() != 0:
            move_vector.scale_to_length(self.MS)
            self.position += move_vector
            print(self.position)

    def walk_up(self):
        self.velocityy -= self.MS

    def walk_down(self):
        self.velocityy += self.MS

    def walk_left(self):
        self.velocityx -= self.MS

    def walk_right(self):
        self.velocityx += self.MS

