import socket
import pickle
import pygame
import threading
import visibal_objects
import tcp


SERVER_IP = '127.0.0.1'
SERVER_PORT = 3321
NETWORK_CARD = '127.0.0.1'
PORT_FOR_SEND_SOC = 8321
MAP_LIMITS = (-1000, -1000, 1000, 1000)
WINDOW_WIDTH = 700
WINDOW_HEIGHT = 500
FPS = 60
PLAYER_SIZE = (40, 50)


pygame.init()
size = (WINDOW_WIDTH, WINDOW_HEIGHT)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Game")
clock = pygame.time.Clock()
finish = False
PATH_FOR_BACKGROUND = "res\\background.jpg"
background_image = pygame.image.load(PATH_FOR_BACKGROUND)
background_image = pygame.transform.scale(background_image, (MAP_LIMITS[2] - MAP_LIMITS[0], MAP_LIMITS[3] - MAP_LIMITS[1]))

screen_lock = threading.Lock()
QUIT_OPCODE = b'QUIT'

W_PRESSED_OPCODE = b'KDWK'
A_PRESSED_OPCODE = b'KDAK'
S_PRESSED_OPCODE = b'KDSK'
D_PRESSED_OPCODE = b'KDDK'
MOUSE_PRESSED_OPCODE = b'MPOP'

W_RELEASED_OPCODE = b'KUWK'
A_RELEASED_OPCODE = b'KUAK'
S_RELEASED_OPCODE = b'KUSK'
D_RELEASED_OPCODE = b'KUDK'


def create_connection():
    recv_soc = socket.socket()
    recv_soc.connect((SERVER_IP, SERVER_PORT))
    got_second_connection = False
    while not got_second_connection:
        send_soc_serv = socket.socket()
        send_soc_serv.bind((NETWORK_CARD, 0))
        tcp.send_with_size(recv_soc, str(send_soc_serv.getsockname()[1]))
        print(str(send_soc_serv.getsockname()[1]))
        send_soc_serv.listen(1)
        send_soc, a = send_soc_serv.accept()
        if a[0] == SERVER_IP:
            got_second_connection = True
            print("Connection process complete")
    return recv_soc, send_soc


class ReceiveClient(threading.Thread):
    def __init__(self, recv_soc):
        super().__init__()
        self.soc = recv_soc

    def handle_server_msg(self):
        global finish
        while not finish:
            data = tcp.recv_by_size(self.soc)
            if data == b'':
                finish = True
                print("Seems server disconnected")
            else:
                on_screen_group, player = pickle.loads(data)
                screen_pos = (-((MAP_LIMITS[2] - MAP_LIMITS[0])/2) - player.position.x + WINDOW_WIDTH/2 - PLAYER_SIZE[0]/2,
                              -((MAP_LIMITS[3] - MAP_LIMITS[1])/2) - player.position.y + WINDOW_HEIGHT/2 - PLAYER_SIZE[1]/2)
                with screen_lock:
                    screen .fill((255,255,255,0))
                    screen.blit(background_image, screen_pos)

                    for a in on_screen_group:
                        a.draw(screen, (player.position.x, player.position.y))

    def run(self) -> None:
        self.handle_server_msg()
        self.soc.close()


def main():
    global finish
    recv_soc, send_soc = create_connection()
    ReceiveClient(recv_soc).start()
    buttons_pressed = {pygame.K_w: False, pygame.K_a: False, pygame.K_s: False, pygame.K_d: False,}
    while not finish:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                tcp.send_with_size(send_soc, pickle.dumps(QUIT_OPCODE,))
                finish = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w and not buttons_pressed[pygame.K_w]:
                    tcp.send_with_size(send_soc, pickle.dumps((W_PRESSED_OPCODE,)))
                    buttons_pressed[pygame.K_w] = True
                elif event.key == pygame.K_a and not buttons_pressed[pygame.K_a]:
                    tcp.send_with_size(send_soc, pickle.dumps((A_PRESSED_OPCODE,)))
                    buttons_pressed[pygame.K_a] = True
                elif event.key == pygame.K_s and not buttons_pressed[pygame.K_s]:
                    tcp.send_with_size(send_soc, pickle.dumps((S_PRESSED_OPCODE,)))
                    buttons_pressed[pygame.K_s] = True
                elif event.key == pygame.K_d and not buttons_pressed[pygame.K_d]:
                    tcp.send_with_size(send_soc, pickle.dumps((D_PRESSED_OPCODE,)))
                    buttons_pressed[pygame.K_d] = True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_w and buttons_pressed[pygame.K_w]:
                    tcp.send_with_size(send_soc, pickle.dumps((W_RELEASED_OPCODE,)))
                    buttons_pressed[pygame.K_w] = False
                elif event.key == pygame.K_a and buttons_pressed[pygame.K_a]:
                    tcp.send_with_size(send_soc, pickle.dumps((A_RELEASED_OPCODE,)))
                    buttons_pressed[pygame.K_a] = False
                elif event.key == pygame.K_s and buttons_pressed[pygame.K_s]:
                    tcp.send_with_size(send_soc, pickle.dumps((S_RELEASED_OPCODE,)))
                    buttons_pressed[pygame.K_s] = False
                elif event.key == pygame.K_d and buttons_pressed[pygame.K_d]:
                    tcp.send_with_size(send_soc, pickle.dumps((D_RELEASED_OPCODE,)))
                    buttons_pressed[pygame.K_d] = False
            elif event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                tcp.send_with_size(send_soc, pickle.dumps((MOUSE_PRESSED_OPCODE, pos)))
        with screen_lock:
            pygame.display.flip()
        clock.tick(FPS)


if __name__ == '__main__':
    main()
