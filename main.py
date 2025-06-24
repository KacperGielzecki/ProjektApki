import pygame
import sys
from client import client_main
from server import server_main

def main_menu():
    pygame.init()
    screen = pygame.display.set_mode((400, 200))
    pygame.display.set_caption("Statki - Wybierz tryb")
    font = pygame.font.SysFont("arial", 28)
    clock = pygame.time.Clock()

    server_button = pygame.Rect(50, 60, 120, 60)
    client_button = pygame.Rect(230, 60, 120, 60)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if server_button.collidepoint(event.pos):
                    pygame.quit()
                    server_main()
                    return
                elif client_button.collidepoint(event.pos):
                    pygame.quit()
                    client_main()
                    return

        screen.fill((30, 30, 30))
        pygame.draw.rect(screen, (70, 130, 180), server_button)
        pygame.draw.rect(screen, (70, 180, 130), client_button)

        server_text = font.render("Serwer", True, (255, 255, 255))
        client_text = font.render("Klient", True, (255, 255, 255))
        screen.blit(server_text, (server_button.x + 10, server_button.y + 15))
        screen.blit(client_text, (client_button.x + 15, client_button.y + 15))

        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    main_menu()
