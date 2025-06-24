import socket
import threading
import pygame
import sys
from gui import run_game

IP_INPUT_WIDTH = 300
IP_INPUT_HEIGHT = 50

def get_ip_gui():
    pygame.init()
    screen = pygame.display.set_mode((400, 200))
    pygame.display.set_caption("Połącz z serwerem")
    font = pygame.font.SysFont("arial", 28)
    input_box = pygame.Rect(50, 50, IP_INPUT_WIDTH, IP_INPUT_HEIGHT)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    active = False
    text = ''
    done = False

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = True
                else:
                    active = False
                color = color_active if active else color_inactive
            elif event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        done = True
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode

        screen.fill((30, 30, 30))
        txt_surface = font.render(text, True, color)
        screen.blit(txt_surface, (input_box.x+5, input_box.y+5))
        pygame.draw.rect(screen, color, input_box, 2)

        prompt = font.render("Wpisz IP i port [IP:PORT]:", True, pygame.Color("white"))
        screen.blit(prompt, (20, 10))

        pygame.display.flip()

    pygame.quit()

    ip_input = text.strip()
    if ':' in ip_input:
        ip, port = ip_input.split(':')
        port = int(port)
    else:
        ip = ip_input
        port = 5000
    return ip, port

def send(sock, msg):
    sock.sendall(str(msg).encode())

def receive(sock):
    data = sock.recv(1024)
    return eval(data.decode())

def client_main():
    server_ip, port = get_ip_gui()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((server_ip, port))

    lock = threading.Lock()
    buffer = []

    def send_move(move):
        with lock:
            send(sock, move)

    def receive_move():
        with lock:
            if buffer:
                return buffer.pop(0)
        return None

    def listen():
        while True:
            try:
                msg = receive(sock)
                with lock:
                    buffer.append(msg)
            except:
                break

    threading.Thread(target=listen, daemon=True).start()
    run_game(player_id=1, send_move=send_move, receive_move=receive_move)

if __name__ == "__main__":
    client_main()
