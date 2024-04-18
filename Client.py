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

WINDOW_WIDTH = 700
WINDOW_HEIGHT = 500
FPS = 60
pygame.init()
size = (WINDOW_WIDTH, WINDOW_HEIGHT)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Game")
clock = pygame.time.Clock()
finish = False

QUIT_OPCODE = b'QUIT'

W_PRESSED_OPCODE = b'KDWK'
A_PRESSED_OPCODE = b'KDAK'
S_PRESSED_OPCODE = b'KDSK'
D_PRESSED_OPCODE = b'KDDK'

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
        send_soc_serv.bind((NETWORK_CARD, PORT_FOR_SEND_SOC))
        send_soc_serv.listen(1)
        send_soc, a = send_soc_serv.accept()
        if a[0] == SERVER_IP:
            got_second_connection = True
    return recv_soc, send_soc


class ReceiveClient(threading.Thread):
    def __init__(self, recv_soc):
        super().__init__()
        self.soc = recv_soc

    def handle_server_msg(self):
        while not finish:
            on_screen_group = pickle.loads(tcp.recv_by_size(self.soc))
            screen.fill((255, 255, 255, 0))
            for a in on_screen_group:
                a.draw(screen)

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
                tcp.send_with_size(send_soc, QUIT_OPCODE)
                finish = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w and not buttons_pressed[pygame.K_w]:
                    tcp.send_with_size(send_soc, W_PRESSED_OPCODE)
                    buttons_pressed[pygame.K_w] = True
                elif event.key == pygame.K_a and not buttons_pressed[pygame.K_a]:
                    tcp.send_with_size(send_soc, A_PRESSED_OPCODE)
                    buttons_pressed[pygame.K_a] = True
                elif event.key == pygame.K_s and not buttons_pressed[pygame.K_s]:
                    tcp.send_with_size(send_soc, S_PRESSED_OPCODE)
                    buttons_pressed[pygame.K_s] = True
                elif event.key == pygame.K_d and not buttons_pressed[pygame.K_d]:
                    tcp.send_with_size(send_soc, D_PRESSED_OPCODE)
                    buttons_pressed[pygame.K_d] = True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_w and buttons_pressed[pygame.K_w]:
                    tcp.send_with_size(send_soc, W_RELEASED_OPCODE)
                    buttons_pressed[pygame.K_w] = False
                elif event.key == pygame.K_a and buttons_pressed[pygame.K_a]:
                    tcp.send_with_size(send_soc, A_RELEASED_OPCODE)
                    buttons_pressed[pygame.K_a] = False
                elif event.key == pygame.K_s and buttons_pressed[pygame.K_s]:
                    tcp.send_with_size(send_soc, S_RELEASED_OPCODE)
                    buttons_pressed[pygame.K_s] = False
                elif event.key == pygame.K_d and buttons_pressed[pygame.K_d]:
                    tcp.send_with_size(send_soc, D_RELEASED_OPCODE)
                    buttons_pressed[pygame.K_d] = False

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == '__main__':
    main()
