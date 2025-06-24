import pygame
import time
import os
import sys
from board import *
from screens import show_victory_screen, show_defeat_screen

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

CELL_SIZE = 40
GRID_SIZE = 10
MARGIN = 40
SPACING = 80
WIDTH = 2 * (GRID_SIZE * CELL_SIZE + MARGIN) + SPACING
HEIGHT = GRID_SIZE * CELL_SIZE + 2 * MARGIN

WHITE = (255, 255, 255)
BLUE = (0, 100, 255)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
DARK_GRAY = (30, 30, 30)
GREEN = (0, 255, 0)
SHADOW_VALID = (0, 180, 0)
SHADOW_INVALID = (150, 150, 150)

SHIP_TYPES = [
    ("Lotniskowiec", 1, 4),
    ("Pancernik", 2, 3),
    ("Krążownik", 3, 2),
    ("Niszczyciel", 4, 1)
]

SHIP_NAME_BY_LENGTH = {
    4: "Lotniskowiec",
    3: "Pancernik",
    2: "Krążownik",
    1: "Niszczyciel"
}

def run_game(player_id, send_move, receive_move):
    pygame.init()
    pygame.mixer.init()
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(f"Statki - Gracz {player_id + 1}")
    font = pygame.font.SysFont("arial", 24, bold=True)

    sounds = {
        "hit": pygame.mixer.Sound(resource_path("static/sounds/hit.wav")),
        "miss": pygame.mixer.Sound(resource_path("static/sounds/miss.wav")),
        "place": pygame.mixer.Sound(resource_path("static/sounds/place.wav")),
        "win": pygame.mixer.Sound(resource_path("static/sounds/win.wav")),
        "lose": pygame.mixer.Sound(resource_path("static/sounds/lose.wav")),
    }

    player_board = create_board()
    enemy_board = create_board()
    ship_positions = []

    place_channel = pygame.mixer.Channel(5)

    game_phase = "setup"
    current_ship_index = 0
    orientation = "H"

    opponent_ready = False
    i_am_ready = False
    sent_start = False
    my_turn = False
    last_shot_result = ""
    game_over = False
    winner = None

    start_time = time.time()

    running = True
    while running:
        win.fill(BLACK)
        player_x = MARGIN
        enemy_x = WIDTH // 2 + SPACING // 2

        draw_grid(win, player_board, player_x, MARGIN, ship_positions)
        draw_grid(win, enemy_board, enemy_x, MARGIN)

        label1 = font.render("Twoja plansza", True, WHITE)
        label2 = font.render("Plansza przeciwnika", True, WHITE)
        win.blit(label1, (player_x + (GRID_SIZE * CELL_SIZE - label1.get_width()) // 2, 5))
        win.blit(label2, (enemy_x + (GRID_SIZE * CELL_SIZE - label2.get_width()) // 2, 5))

        elapsed = int(time.time() - start_time)
        mins, secs = divmod(elapsed, 60)
        timer_label = font.render(f"Czas: {mins:02}:{secs:02}", True, WHITE)
        win.blit(timer_label, (WIDTH // 2 - timer_label.get_width() // 2, 5))

        if game_over:
            pygame.display.flip()
            pygame.time.delay(1000)
            if winner == player_id:
                sounds["win"].play()
                show_victory_screen()
            else:
                sounds["lose"].play()
                show_defeat_screen()
            return

        if game_phase == "setup" and current_ship_index < len(SHIP_TYPES):
            mx, my = pygame.mouse.get_pos()
            col = (mx - player_x) // CELL_SIZE
            row = (my - MARGIN) // CELL_SIZE
            name, qty, length = SHIP_TYPES[current_ship_index]
            cells = get_ship_cells(row, col, length, orientation)
            valid = can_place_ship(player_board, row, col, length, orientation)
            draw_shadow(win, cells, valid, player_x, MARGIN)

        if game_phase == "setup":
            name, qty, _ = SHIP_TYPES[current_ship_index]
            info = font.render(f"Rozstaw: {name} (ilość: {qty})", True, GREEN)
        elif not opponent_ready:
            info = font.render("Czekam na przeciwnika...", True, WHITE)
        elif game_phase == "wait":
            info = font.render("Losowanie kto zaczyna...", True, WHITE)
        else:
            msg = "Twoja tura" if my_turn else f"{last_shot_result} – Tura przeciwnika" if last_shot_result else "Tura przeciwnika"
            info = font.render(msg, True, WHITE)
        win.blit(info, (WIDTH // 2 - info.get_width() // 2, HEIGHT - 30))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and game_phase == "setup":
                if event.key == pygame.K_r:
                    orientation = "V" if orientation == "H" else "H"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                col = (x - player_x) // CELL_SIZE
                row = (y - MARGIN) // CELL_SIZE

                if game_phase == "setup":
                    if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
                        if player_board[row][col] == 1:
                            for i, (r, c, length, orient) in enumerate(ship_positions):
                                if (row, col) in get_ship_cells(r, c, length, orient):
                                    remove_ship(player_board, get_ship_cells(r, c, length, orient))
                                    ship_positions.pop(i)
                                    for j in range(len(SHIP_TYPES)-1, -1, -1):
                                        if SHIP_TYPES[j][2] == length:
                                            SHIP_TYPES[j] = (SHIP_TYPES[j][0], SHIP_TYPES[j][1] + 1, SHIP_TYPES[j][2])
                                            current_ship_index = min(current_ship_index, j)
                                            break
                                    break
                        else:
                            name, qty, length = SHIP_TYPES[current_ship_index]
                            if can_place_ship(player_board, row, col, length, orientation):
                                place_ship(player_board, row, col, length, orientation)
                                ship_positions.append((row, col, length, orientation))
                                place_channel.play(sounds["place"])
                                SHIP_TYPES[current_ship_index] = (name, qty - 1, length)
                                if SHIP_TYPES[current_ship_index][1] == 0:
                                    current_ship_index += 1
                                if current_ship_index == len(SHIP_TYPES):
                                    i_am_ready = True
                                    send_move({"type": "ready"})
                                    game_phase = "wait"

                elif game_phase == "play" and my_turn:
                    col = (x - enemy_x) // CELL_SIZE
                    row = (y - MARGIN) // CELL_SIZE
                    if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE and enemy_board[row][col] == 0:
                        send_move({"type": "shot", "pos": (row, col)})
                        my_turn = False

        try:
            move = receive_move()
            if move:
                if move.get("type") == "shot":
                    r, c = move["pos"]
                    hit = player_board[r][c] == 1
                    player_board[r][c] = 2 if hit else 3
                    send_move({"type": "result", "pos": (r, c), "hit": hit})
                    my_turn = True
                    last_shot_result = ""
                    if check_victory(player_board):
                        send_move({"type": "end"})
                        game_over = True
                        winner = 1 - player_id
                elif move.get("type") == "result":
                        r, c = move["pos"]
                        hit = move["hit"]
                        enemy_board[r][c] = 2 if hit else 3
                        sounds["hit" if hit else "miss"].play()

                        last_shot_result = "Trafienie" if hit else "Pudło"

                elif move.get("type") == "ready":
                    opponent_ready = True
                elif move.get("type") == "start":
                    starter = move["who"]
                    game_phase = "play"
                    my_turn = (player_id == starter)
                elif move.get("type") == "end":
                    game_over = True
                    winner = player_id
        except:
            pass

        if game_phase == "wait" and i_am_ready and opponent_ready and not sent_start:
            if player_id == 0:
                import random
                starter = random.choice([0, 1])
                send_move({"type": "start", "who": starter})
                game_phase = "play"
                my_turn = (player_id == starter)
            sent_start = True

        pygame.display.flip()

    pygame.quit()


def draw_grid(win, board, offset_x, offset_y, ship_positions=None):
    ship_color_by_length = {
        4: (80, 80, 80),        # Lotniskowiec – ciemny szary
        3: (160, 120, 60),      # Pancernik – brązowy
        2: (128, 0, 32),        # Krążownik – bordowy
        1: (85, 107, 47)        # Niszczyciel – oliwkowy
    }

    position_color_map = {}
    if ship_positions:
        for r, c, length, orientation in ship_positions:
            for i in range(length):
                rr = r + i if orientation == "V" else r
                cc = c + i if orientation == "H" else c
                position_color_map[(rr, cc)] = ship_color_by_length.get(length, (0, 100, 255))

    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            val = board[row][col]
            pos = (row, col)

            if val == 2:
                color = RED
            elif val == 3:
                color = GRAY
            elif val == 1 and pos in position_color_map:
                color = position_color_map[pos]
            elif val == 1:
                color = (0, 100, 255)  # default blue
            else:
                color = WHITE

            pygame.draw.rect(
                win,
                color,
                (offset_x + col * CELL_SIZE, offset_y + row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            )
            pygame.draw.rect(
                win,
                DARK_GRAY,
                (offset_x + col * CELL_SIZE, offset_y + row * CELL_SIZE, CELL_SIZE, CELL_SIZE),
                1
            )


def draw_shadow(win, cells, valid, offset_x, offset_y):
    for r, c in cells:
        if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE:
            color = SHADOW_VALID if valid else SHADOW_INVALID
            x = offset_x + c * CELL_SIZE
            y = offset_y + r * CELL_SIZE
            pygame.draw.rect(win, color, (x, y, CELL_SIZE, CELL_SIZE))