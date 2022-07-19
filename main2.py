#!/usr/bin/python3
import json
import pathlib as pl
import random
import time
from enum import Enum

import pygame


class Direction(Enum):
    UP = 1
    DOWN = 2
    RIGHT = 3
    LEFT = 4


def r_data():
    with open(path_h_score_file, "r") as app_data_file:
        app_data_dict = json.load(app_data_file)
    return app_data_dict


def w_h_score():
    with open(path_h_score_file, "w") as file:
        json.dump(highscore_data, file)


path_h_score_file = str(pl.Path().absolute()) + "/PycharmProjects/snakepie/h_score.json"
speed = 10
level = 1
gamestat = 0
objects = []

win_width = 1080
win_height = 720

pygame.init()
pygame.display.set_caption("snakekpie")
win = pygame.display.set_mode((win_width, win_height))

refresh_controller = pygame.time.Clock()
font = pygame.font.SysFont('Arial', 20)

snake_position = [250, 250]
snake_body = [[250, 250],
              [240, 250],
              [230, 250]]

food_position = [random.randint(20, 1000), random.randint(20, 700)]
scale = 20

score = 0
fo60 = pygame.font.SysFont('Arial', 60)
fo40 = pygame.font.SysFont('Arial', 40)
fo16 = pygame.font.SysFont("Arial", 16)

highscore_data = r_data()

h_score_str = list(highscore_data.keys())
print(h_score_str)
h_score_int = []

for i in range(len(h_score_str)):
    h_score_int.append(int(h_score_str[i]))
print(h_score_int)
h_score_int.sort()
print(h_score_int)

h_score_alt = h_score_int[-1]
h_score_neu = h_score_alt
h_score_name = highscore_data[str(h_score_alt)]
print(h_score_alt)
print(h_score_name)


def handle_keys(direction):
    global gamestat
    new_direction = direction
    for event in [e for e in pygame.event.get() if e.type == pygame.KEYDOWN]:
        if event.key == pygame.K_UP and direction != Direction.DOWN:
            new_direction = Direction.UP
        if event.key == pygame.K_DOWN and direction != Direction.UP:
            new_direction = Direction.DOWN
        if event.key == pygame.K_RIGHT and direction != Direction.LEFT:
            new_direction = Direction.RIGHT
        if event.key == pygame.K_LEFT and direction != Direction.RIGHT:
            new_direction = Direction.LEFT
        if event.key == pygame.K_ESCAPE:
            gamestat = 0
        if event.key == pygame.K_SPACE:
            gamestat = 1

    return new_direction


def move_snake(direction):
    if direction == Direction.UP:
        snake_position[1] -= scale
    if direction == Direction.DOWN:
        snake_position[1] += scale
    if direction == Direction.LEFT:
        snake_position[0] -= scale
    if direction == Direction.RIGHT:
        snake_position[0] += scale
    snake_body.insert(0, list(snake_position))


def generate_new_food():
    food_position[0] = random.randint(5, ((win_width - 2) // scale)) * scale
    food_position[1] = random.randint(5, ((win_height - 2) // scale)) * scale


def get_food():
    global score
    if abs(snake_position[0] - food_position[0]) < 20 and abs(snake_position[1] - food_position[1]) < 20:
        score += 10
        generate_new_food()
        if score % 100 == 0:
            speed_up()
    else:
        snake_body.pop()


def speed_up():
    global speed, level
    speed += 2
    level += 1


def repaint():
    win.fill(pygame.Color("black"))
    for body in snake_body:
        pygame.draw.circle(win, pygame.Color("purple"), (body[0], body[1]), int(scale / 2))
    pygame.draw.rect(win, pygame.Color("red"),
                     pygame.Rect(food_position[0] - int(scale / 2), food_position[1] - int(scale / 2), scale, scale))


def game_over_message():
    global gamestat
    show_text(f"GAME OVER", "grey", (int(win_width / 2), int(win_height / 2) - 100), fo40)
    show_text(f"Score: {score}", "white", (int(win_width / 2), int(win_height / 2)), fo40)
    if h_score_neu > h_score_alt:
        show_text(f"Neuer Highscore: {h_score_neu}", "grey", (int(win_width / 2), int(win_height / 2) + 200), fo40)
        highscore_data[f"{h_score_neu}"] = "___"
        w_h_score()
    else:
        show_text(f"Leider Highscore nicht geschlagen", "grey", (int(win_width / 2), int(win_height / 2) + 200), fo40)

    pygame.display.flip()
    time.sleep(5)
    gamestat = 0


def show_text(text, col, pos, fo):
    act_text = fo.render(text, True, pygame.Color(col))
    rect_text = act_text.get_rect()
    rect_text.midtop = pos
    win.blit(act_text, rect_text)


def game_over():
    if snake_position[0] < 0 or snake_position[0] > win_width - scale:
        game_over_message()
    if snake_position[1] < 0 or snake_position[1] > win_height - scale:
        game_over_message()
    for blob in snake_body[1:]:
        if snake_position[0] == blob[0] and snake_position[1] == blob[1]:
            game_over_message()


def paint_hud():
    show_text(f"Score: {score}", "white", (125, 0), fo16)
    show_text(f"Level: {level}", "white", (30, 0), fo16)
    show_text(f"Zum Beenden ESC-Taste drücken", "white", (900, 0), fo16)
    show_text(f"Highscore: {str(h_score_neu)}", "white", (300, 0), fo16)

    pygame.display.flip()


def show_starttext():
    show_text(f"SnakePie", "white", (500, 150), fo60)
    show_text(f"Zum starten SPACE-Taste drücken", "white", (500, 300), fo40)
    show_text(f"Highscore: {str(h_score_alt)}", "white", (500, 500), fo40)
    pygame.display.flip()


def game_loop():
    direction = Direction.RIGHT
    while not gamestat:
        direction = handle_keys(direction)
        show_starttext()

    while gamestat:
        global h_score_neu
        direction = handle_keys(direction)
        move_snake(direction)
        get_food()
        repaint()
        game_over()
        paint_hud()
        pygame.display.update()
        refresh_controller.tick(speed)
        if score > h_score_neu:
            h_score_neu = score


if __name__ == "__main__":
    game_loop()
    pygame.quit()
    exit(0)