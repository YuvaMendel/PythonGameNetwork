import socket
import pickle
import pygame
import threading
import visibal_objects
import time
import tcp

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

TIME_BETWEEN_EACH_REFRESH = 0.017

universe_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()


universe_group_lock = threading.Lock()

WINDOW_WIDTH = 700
WINDOW_HEIGHT = 500




class Client(threading.Thread):
    CLIENT_PORT_FOR_RECV_SOC = 8321

    def __init__(self, soc, a):
        super().__init__()

        self.send_soc = soc
        self.recv_soc = socket.socket()
        self.recv_soc.connect((a[0], self.CLIENT_PORT_FOR_RECV_SOC))

        self.player = visibal_objects.Player()
        with universe_group_lock:
            self.player.add(universe_group)
            self.player.add(player_group)
        self.connected = True
        print("Client Connected")

    def send_soc_handle(self):
        last_sent = b''

        while self.connected:
            data = pickle.dumps((universe_group, self.player))
            if data != last_sent:
                tcp.send_with_size(self.send_soc, data)
                last_sent = data

    def recv_soc_handle(self):
        while self.connected:
            data = tcp.recv_by_size(self.recv_soc)
            if data == b'':
                self.connected = False
                print("Client Disconnected")
            else:
                data = pickle.loads(data)
                command = data[0]
                with universe_group_lock:
                    if command == QUIT_OPCODE:
                        self.connected = False
                    elif command == W_PRESSED_OPCODE:
                        self.player.walk_up()
                    elif command == A_PRESSED_OPCODE:
                        self.player.walk_left()
                    elif command == S_PRESSED_OPCODE:
                        self.player.walk_down()
                    elif command == D_PRESSED_OPCODE:
                        self.player.walk_right()
                    elif command == W_RELEASED_OPCODE:
                        self.player.walk_down()
                    elif command == A_RELEASED_OPCODE:
                        self.player.walk_right()
                    elif command == S_RELEASED_OPCODE:
                        self.player.walk_up()
                    elif command == D_RELEASED_OPCODE:
                        self.player.walk_left()
                    elif command == MOUSE_PRESSED_OPCODE:
                        target = pygame.math.Vector2(data[1][0] + self.player.position.x - WINDOW_WIDTH/2, data[1][1] + self.player.position.y - WINDOW_HEIGHT/2)
                        blt = self.player.shoot(target)
                        bullet_group.add(blt)
                        universe_group.add(blt)

    def __exit_client(self):
        self.send_soc.close()
        self.recv_soc.close()
        self.player.kill()

    def run(self) -> None:
        print("thread created")
        send_thread = threading.Thread(target=self.send_soc_handle)
        recv_thread = threading.Thread(target=self.recv_soc_handle)

        send_thread.start()
        recv_thread.start()

        send_thread.join()
        recv_thread.join()
        self.__exit_client()
        print("Thread closed")


class Server(threading.Thread):
    SERVER_NETWORK_CARD = '127.0.0.1'
    SERVER_PORT = 3321

    def __init__(self):
        super().__init__()
        self.server = socket.socket()
        self.server.bind((self.SERVER_NETWORK_CARD, self.SERVER_PORT))
        self.server.listen(5)

    def run(self) -> None:
        while True:
            c, a = self.server.accept()
            Client(c, a).start()


def update_universe_group():
    enemy = visibal_objects.createenemy(len(player_group.sprites()))
    with universe_group_lock:
        universe_group.update()
        if enemy is not None:
            enemy.add(universe_group)
            enemy.add(enemy_group)


def update_enemies_target():
    with universe_group_lock:
        for enemy in enemy_group:
            enemy.update_target(player_group)


def bullet_collisions():
    with universe_group_lock:
        for bullet in bullet_group:
            bullet.hit(enemy_group)


def enemy_collisions():
    with universe_group_lock:
        for enemy in enemy_group:
            enemy.attack(player_group)


def main():
    server_thread = Server()
    server_thread.start()
    t1 = time.time()
    while True:
        t2 = time.time()
        if t2-t1 > TIME_BETWEEN_EACH_REFRESH:
            update_enemies_target()
            update_universe_group()
            bullet_collisions()
            enemy_collisions()
            t1 = time.time()


if __name__ == '__main__':
    main()
