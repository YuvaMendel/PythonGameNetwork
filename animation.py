import pygame
prefix = "res\\Full body animated characters\\Char 1\\with hands\\"
WINDOW_WIDTH = 700
WINDOW_HEIGHT = 500
FPS = 10
pygame.init()
size = (WINDOW_WIDTH, WINDOW_HEIGHT)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Game")
clock = pygame.time.Clock()

finish = False
WALK_LENGTH = 8

PINK = (255, 174, 201, 0)

i = 0

while not finish:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            finish = True
    img = pygame.image.load(prefix + "walk_" + str(i) + ".png").convert().copy()
    img.set_colorkey(PINK)
    size = (100, 120)
    img = pygame.transform.scale(img, size)
    i += 1
    i %= WALK_LENGTH
    screen.fill((255, 255, 255, 0))
    screen.blit(img, (10, 30))
    pygame.display.flip()
    clock.tick(FPS)

