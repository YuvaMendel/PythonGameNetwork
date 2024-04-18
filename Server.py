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

W_RELEASED_OPCODE = b'KUWK'
A_RELEASED_OPCODE = b'KUAK'
S_RELEASED_OPCODE = b'KUSK'
D_RELEASED_OPCODE = b'KUDK'

TIME_BETWEEN_EACH_REFRESH = 0.017

universe_group = pygame.sprite.Group()
universe_group_lock = threading.Lock()
WORLD_SIZE_X = 1000000
WORLD_SIZE_Y = 1000000


class Client(threading.Thread):
    CLIENT_PORT_FOR_RECV_SOC = 8321

    def __init__(self, soc, a):
        super().__init__()

        self.send_soc = soc
        self.recv_soc = socket.socket()
        self.recv_soc.connect((a[0], self.CLIENT_PORT_FOR_RECV_SOC))

        self.player = visibal_objects.Player()
        self.player.add(universe_group)
        self.connected = True

    def send_soc_handle(self):
        last_sent = b''

        while self.connected:
            data = pickle.dumps(universe_group)
            if data != last_sent:
                tcp.send_with_size(self.send_soc, data)
                last_sent = data

    def recv_soc_handle(self):
        while self.connected:
            command = tcp.recv_by_size(self.recv_soc)
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

    def __exit_client(self):
        self.send_soc.close()
        self.recv_soc.close()
        self.player.kill()

    def run(self) -> None:
        send_thread = threading.Thread(target=self.send_soc_handle)
        recv_thread = threading.Thread(target=self.recv_soc_handle)

        send_thread.start()
        recv_thread.start()

        send_thread.join()
        recv_thread.join()
        self.__exit_client()


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
    with universe_group_lock:
        universe_group.update()


def main():
    server_thread = Server()
    server_thread.start()
    t1 = time.time()
    while True:
        t2 = time.time()
        if t2-t1 > TIME_BETWEEN_EACH_REFRESH:
            update_universe_group()
            t1 = time.time()


if __name__ == '__main__':
    main()
