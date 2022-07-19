#!/usr/bin/python3
# pylint: disable=invalid-name, disable=no-name-in-module, disable=no-member, disable=global-statement

""" this is a snake game written in python"""
import json
import pathlib as pl
import random
import sys
import time
from enum import Enum

import pygame as pg
from pygame.locals import K_UP, K_DOWN, K_LEFT, K_RIGHT, K_ESCAPE, K_SPACE


class Direction(Enum):
    """ THIS CLASS DEFINE THE DIRECTIONS """
    UP = 1
    DOWN = 2
    RIGHT = 3
    LEFT = 4


def r_data():
    """ READ THE HIGHSCOREFILE AND RETURN A DICT WITH THE DATA"""
    with open(PA_HS_FILE, "r", encoding='UTF-8') as app_data_file:
        app_data_dict = json.load(app_data_file)
    return app_data_dict


def w_h_score():
    """ WRITE THE NEW HIGHSCORE TO THE .JSON FILE """
    with open(PA_HS_FILE, "w", encoding='UTF-8') as file:
        json.dump(highscore_data, file)


# define constants
PA_HS_FILE = str(pl.Path().absolute()) + "/PycharmProjects/snakepie/h_score.json"
WIN_W, WIN_H = 1080, 720
SCALE = 20

pg.init()
pg.display.set_caption("snakekpie")
win = pg.display.set_mode((WIN_W, WIN_H))
refresh_controller = pg.time.Clock()

speed = 10
level = 1
game_stat = 0
objects = []

snake_pos = [250, 250]
snake_body = [[250, 250],
              [240, 250],
              [230, 250]]

food_pos = [random.randint(20, 1000), random.randint(20, 700)]
input_rect = pg.Rect(200, 200, 140, 32)
user_text = " "
active = False
color_active = pg.Color('green')
color_passive = pg.Color('blue')
color = color_passive

score = 0
FONT60 = pg.font.SysFont("Arial", 60)
FONT40 = pg.font.SysFont("Arial", 40)
FONT16 = pg.font.SysFont("Arial", 16)

highscore_data = r_data()

h_score_str = list(highscore_data.keys())
print(h_score_str)
h_score_int = []

for i, n in enumerate(h_score_str):
    h_score_int.append(int(n))
print(h_score_int)
h_score_int.sort()
print(h_score_int)

h_score_alt = h_score_int[-1]
h_score_neu = h_score_alt
h_score_name = highscore_data[str(h_score_alt)]
print(h_score_alt)
print(h_score_name)


def handle_keys(direction):
    """ handle the key events."""
    global game_stat, active, color, user_text
    new_direction = direction
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
        if event.type == pg.MOUSEBUTTONDOWN:
            if input_rect.collidepoint(event.pos):
                active = True
            else:
                active = False
        if event.type == pg.KEYDOWN:
            if event.key == K_UP and direction != Direction.DOWN:
                new_direction = Direction.UP
            if event.key == K_DOWN and direction != Direction.UP:
                new_direction = Direction.DOWN
            if event.key == K_RIGHT and direction != Direction.LEFT:
                new_direction = Direction.RIGHT
            if event.key == K_LEFT and direction != Direction.RIGHT:
                new_direction = Direction.LEFT
            if event.key == K_ESCAPE:
                game_stat = 0
            if event.key == K_SPACE:
                game_stat = 1
            if event.key == pg.K_BACKSPACE:
                # get text input from 0 to -1 i.e. end.
                user_text = user_text[:-1]
            # Unicode standard is used for string
            # formation
            else:
                user_text += event.unicode
            if active:
                color = color_active
            else:
                color = color_passive

    return new_direction


def move_snake(direction):
    """ change the direction of the snake"""
    if direction == Direction.UP:
        snake_pos[1] -= SCALE
    if direction == Direction.DOWN:
        snake_pos[1] += SCALE
    if direction == Direction.LEFT:
        snake_pos[0] -= SCALE
    if direction == Direction.RIGHT:
        snake_pos[0] += SCALE
    snake_body.insert(0, list(snake_pos))


def generate_new_food():
    """ create a new food in the window"""
    food_pos[0] = random.randint(5, ((WIN_W - 2) // SCALE)) * SCALE
    food_pos[1] = random.randint(5, ((WIN_H - 2) // SCALE)) * SCALE


def get_food():
    """ check if the snake the snake get the food. create a new food if the snake hit the food"""
    global score
    if abs(snake_pos[0] - food_pos[0]) < 20 and abs(snake_pos[1] - food_pos[1]) < 20:
        score += 10
        generate_new_food()
        if score % 100 == 0:
            speed_up()
    else:
        snake_body.pop()


def speed_up():
    """ raise the speed and the level of the game"""
    global speed, level
    speed += 2
    level += 1


def repaint():
    """ repaint the display for moving the snake"""
    win.fill(pg.Color("black"))
    for body in snake_body:
        pg.draw.circle(win, pg.Color("purple"), (body[0], body[1]), int(SCALE / 2))
    pg.draw.rect(win, pg.Color("red"), pg.Rect(food_pos[0] - int(SCALE / 2),
                                               food_pos[1] - int(SCALE / 2), SCALE, SCALE))


def game_over_message():
    """ this message will shown if the game is over"""
    show_text("GAME OVER", "grey", (int(WIN_W / 2), int(WIN_H / 2) - 100), FONT40)
    show_text(f"Score: {score}", "white", (int(WIN_W / 2), int(WIN_H / 2)), FONT40)
    if h_score_neu > h_score_alt:
        show_text(f"Neuer Highscore: {h_score_neu}", "grey", (int(WIN_W / 2),
                                                              int(WIN_H / 2) + 200), FONT40)
        highscore_data[f"{h_score_neu}"] = "___"

        w_h_score()
    else:
        show_text("Leider Highscore nicht geschlagen", "grey", (int(WIN_W / 2),
                                                                int(WIN_H / 2) + 200), FONT40)
    pg.draw.rect(win, color, input_rect)
    text_surface = FONT16.render(user_text, True, (255, 255, 255))
    win.blit(text_surface, (input_rect.x + 5, input_rect.y + 5))
    input_rect.w = max(100, text_surface.get_width() + 10)
    pg.display.flip()
    time.sleep(5)
    sys.exit(0)


def show_text(text, col, pos, fo_st):
    """ a small def to create a textfield"""
    act_text = fo_st.render(text, True, pg.Color(col))
    rect_text = act_text.get_rect()
    rect_text.midtop = pos
    win.blit(act_text, rect_text)


def game_over():
    """ Check the game state if it game over"""
    if snake_pos[0] < 0 or snake_pos[0] > WIN_W - SCALE:
        game_over_message()
    if snake_pos[1] < 0 or snake_pos[1] > WIN_H - SCALE:
        game_over_message()
    for blob in snake_body[1:]:
        if snake_pos[0] == blob[0] and snake_pos[1] == blob[1]:
            game_over_message()


def paint_hud():
    """ show the textes in the game"""
    show_text(f"Level: {level}", "white", (30, 0), FONT16)
    show_text(f"Score: {score}", "white", (125, 0), FONT16)
    show_text("Zum Beenden ESC-Taste drücken", "white", (900, 0), FONT16)
    show_text(f"Highscore: {str(h_score_neu)}", "white", (300, 0), FONT16)
    pg.draw.rect(win, color, input_rect)
    text_surface = FONT16.render(user_text, True, (255, 255, 255))
    win.blit(text_surface, (input_rect.x + 5, input_rect.y + 5))
    input_rect.w = max(100, text_surface.get_width() + 10)
    pg.display.flip()


def show_starttext():
    """ show the start window"""
    show_text("SnakePie", "white", (500, 150), FONT60)
    show_text("Zum starten SPACE-Taste drücken", "white", (500, 300), FONT40)
    show_text(f"Highscore: {str(h_score_alt)}", "white", (500, 500), FONT40)
    pg.display.flip()


def check_h_score():
    """ check if a new highscore exist"""
    global h_score_neu
    if score > h_score_neu:
        h_score_neu = score


def game_loop():
    """ the game loop is the main function"""
    direction = Direction.RIGHT
    while not game_stat:
        direction = handle_keys(direction)
        show_starttext()

    while game_stat:
        direction = handle_keys(direction)
        move_snake(direction)
        get_food()
        repaint()
        game_over()
        paint_hud()
        pg.display.update()
        refresh_controller.tick(speed)
        check_h_score()


if __name__ == "__main__":
    game_loop()
