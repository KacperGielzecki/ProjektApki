import pygame
import sys
import os

WIDTH = 800
HEIGHT = 600

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def show_victory_screen(image_path=None):
    if image_path is None:
        image_path = resource_path("static/screens/victory.png")

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Zwycięstwo!")
    image = pygame.image.load(image_path)
    image = pygame.transform.scale(image, (WIDTH, HEIGHT))
    screen.blit(image, (0, 0))
    pygame.display.flip()
    wait_for_close()

def show_defeat_screen(image_path=None):
    if image_path is None:
        image_path = resource_path("static/screens/defeat.png")

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Przegrana")
    image = pygame.image.load(image_path)
    image = pygame.transform.scale(image, (WIDTH, HEIGHT))
    screen.blit(image, (0, 0))
    pygame.display.flip()
    wait_for_close()

def wait_for_close():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()
