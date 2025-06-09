import socket
import threading
import pygame
import sys
from gui import run_game

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def show_waiting_screen(ip_address):
    pygame.init()
    screen = pygame.display.set_mode((400, 200))
    pygame.display.set_caption("Serwer gry - Statki")
    font = pygame.font.SysFont("arial", 28)
    clock = pygame.time.Clock()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.fill((30, 30, 30))
        text = font.render("Oczekiwanie na gracza...", True, pygame.Color("white"))
        screen.blit(text, (50, 50))

        ip_text = font.render(f"IP serwera: {ip_address}", True, pygame.Color("gray"))
        screen.blit(ip_text, (50, 100))

        pygame.display.flip()
        clock.tick(30)

        if hasattr(show_waiting_screen, "client_connected") and show_waiting_screen.client_connected:
            waiting = False

    pygame.quit()

def start_server_socket():
    host = '0.0.0.0'
    port = 5000
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, port))
    sock.listen(1)
    conn, addr = sock.accept()
    show_waiting_screen.client_connected = True
    return conn

def send(sock, msg):
    sock.sendall(str(msg).encode())

def receive(sock):
    data = sock.recv(1024)
    return eval(data.decode())

def server_main():
    ip_address = get_local_ip()

    host = '0.0.0.0'
    port = 5000
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, port))
    sock.listen(1)

    pygame.init()
    screen = pygame.display.set_mode((400, 200))
    pygame.display.set_caption("Serwer gry - Statki")
    font = pygame.font.SysFont("arial", 28)
    clock = pygame.time.Clock()

    conn = None
    while conn is None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.fill((30, 30, 30))
        text = font.render("Oczekiwanie na gracza...", True, pygame.Color("white"))
        screen.blit(text, (50, 50))
        ip_text = font.render(f"IP serwera: {ip_address}", True, pygame.Color("gray"))
        screen.blit(ip_text, (50, 100))
        pygame.display.flip()
        clock.tick(30)

        try:
            sock.settimeout(0.1)
            conn, addr = sock.accept()
        except:
            pass

    pygame.quit()

    lock = threading.Lock()
    buffer = []

    def send_move(move):
        with lock:
            send(conn, move)

    def receive_move():
        with lock:
            if buffer:
                return buffer.pop(0)
        return None

    def listen():
        while True:
            try:
                msg = receive(conn)
                with lock:
                    buffer.append(msg)
            except:
                break

    threading.Thread(target=listen, daemon=True).start()
    run_game(player_id=0, send_move=send_move, receive_move=receive_move)


if __name__ == "__main__":
    server_main()
