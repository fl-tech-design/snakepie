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

pg.init()
pg.display.set_caption("snakekpie")


class Direction(Enum):
    """ THIS CLASS DEFINE THE DIRECTIONS """
    UP = 1
    DOWN = 2
    RIGHT = 3
    LEFT = 4


class Fon:
    """this class defines the game fonts"""
    fo100 = pg.font.SysFont("Arial", 100)
    fo40 = pg.font.SysFont("Arial", 40)
    fo23 = pg.font.SysFont("Arial", 23)
    fo16 = pg.font.SysFont("Arial", 16)


def quit_game():
    """ quit the game and close the window"""
    pg.quit()
    sys.exit(0)


def r_data():
    """ READ THE HIGH-SCORE-FILE AND RETURN A DICT WITH THE DATA"""
    with open(PA_HS_FILE, "r", encoding='UTF-8') as file:
        data_dict = json.load(file)
    return data_dict


class SnakeGame:
    """ the class snakegame include the whole game"""

    def __init__(self):
        self.direction = Direction.RIGHT
        self.win = pg.display.set_mode((WIN_W, WIN_H))
        self.clock = pg.time.Clock()
        self.speed, self.level = 10, 1
        self.g_stat, self.n_stat = 0, 0
        self.s_pos = [250, 250]
        self.s_body = [[250, 250],
                       [240, 250],
                       [230, 250]]

        self.f_pos = [random.randint(20, 1000), random.randint(20, 700)]

        self.score = 0
        self.hs_stat = False

        self.hs_data = r_data()
        self.hs_int = []
        self.load_hs_list()

        self.hs_old = max(self.hs_int)
        self.hs_new = self.hs_old

        # all things for the input field for high-score name
        self.active = False
        self.i_rect = pg.Rect(WIN_M_W + 25, Y_BOT - 20, 90, 40)

        self.u_text = ""

        self.main_loop()

    def check_hs(self):
        """ check if a new high-score exist"""
        if self.score > self.hs_new:
            self.hs_new = self.score
            self.hs_stat = True
        else:
            self.hs_stat = False

    def entry_name(self):
        """ make a textfield for the high-score name"""
        self.n_stat = 1
        while self.n_stat:
            for event in pg.event.get():
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_RETURN:
                        self.u_text = self.u_text[:]
                        self.n_stat = 0
                    else:
                        self.u_text += event.unicode
                    if event.key == pg.K_BACKSPACE:
                        ut_list = list(self.u_text)
                        ut_list.pop()
                        ut_list.pop()
                        ut_str = "".join(ut_list)
                        self.u_text = ut_str
                        pg.display.flip()

            pg.draw.rect(self.win, BG_G, self.i_rect)
            text_surface = Fon.fo40.render(self.u_text, True, FG_P)
            self.win.blit(text_surface, (self.i_rect.x + 2, self.i_rect.y + 2))
            pg.display.flip()

    def event_control(self):
        """ handle the key events."""
        for event in pg.event.get():
            if event.type == pg.MOUSEBUTTONDOWN:
                if self.i_rect.collidepoint(event.pos):
                    self.active = True
                else:
                    self.active = False
            if event.type == pg.QUIT:
                quit_game()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_UP and self.direction != Direction.DOWN:
                    self.direction = Direction.UP
                if event.key == pg.K_DOWN and self.direction != Direction.UP:
                    self.direction = Direction.DOWN
                if event.key == pg.K_RIGHT and self.direction != Direction.LEFT:
                    self.direction = Direction.RIGHT
                if event.key == pg.K_LEFT and self.direction != Direction.RIGHT:
                    self.direction = Direction.LEFT
                if event.key == pg.K_ESCAPE:
                    quit_game()
                if event.key == pg.K_SPACE:
                    self.g_stat = 1

    def generate_new_food(self):
        """ create a new food in the window"""
        self.f_pos[0] = random.randint(5, ((WIN_W - 2) // SIZE)) * SIZE
        self.f_pos[1] = random.randint(5, ((WIN_H - 2) // SIZE)) * SIZE

    def get_food(self):
        """ check if the snake get the food.
        create a new food if the snake hit the food"""
        if abs(self.s_pos[0] - self.f_pos[0]) < 20 and abs(self.s_pos[1] - self.f_pos[1]) < 20:
            self.score += 10
            self.generate_new_food()
            self.check_hs()
            if self.score % 100 == 0:
                self.speed_up()
        else:
            self.s_body.pop()

    def game_over(self):
        """ Check the game state if the game is over"""
        if self.s_pos[0] < SIZE or self.s_pos[0] > WIN_W - SIZE:
            self.g_stat = 2
        if self.s_pos[1] < SIZE or self.s_pos[1] > WIN_H - SIZE:
            self.g_stat = 2
        for blob in self.s_body[1:]:
            if self.s_pos[0] == blob[0] and self.s_pos[1] == blob[1]:
                self.g_stat = 2

    def move_snake(self):
        """ change the direction of the snake"""
        if self.direction == Direction.UP:
            self.s_pos[1] -= SIZE
        if self.direction == Direction.DOWN:
            self.s_pos[1] += SIZE
        if self.direction == Direction.LEFT:
            self.s_pos[0] -= SIZE
        if self.direction == Direction.RIGHT:
            self.s_pos[0] += SIZE
        self.s_body.insert(0, list(self.s_pos))

    def paint_hud(self):
        """ show the textes in the game"""
        self.show_text(f"Level: {self.level}", FG_P, 30, 0, Fon.fo16)
        self.show_text(f"Score: {self.score}", FG_P, 125, 0, Fon.fo16)
        self.show_text("Zum Beenden ESC-Taste drücken", FG_P, 800, 0, Fon.fo16)
        self.show_text(f"Highscore: {str(self.hs_new)}", FG_P, 300, 0, Fon.fo16)

    def restart_game(self):
        """ this function rest all datas and set the snake on the startpoint"""
        self.score = 0
        self.level = 1
        self.speed = 10
        self.hs_old = self.hs_new
        self.s_pos = [250, 250]
        self.s_body = [[250, 250],
                       [240, 250],
                       [230, 250]]
        self.u_text = ''

    def repaint(self):
        """ repaint the display for moving the snake"""
        self.win.fill(pg.Color(BG_G))
        for body in self.s_body:
            self.win.blit(GamePics.b_pic, (body[0] - (SIZE / 2), body[1] - (SIZE / 2)))
        self.win.blit(GamePics.f_pic, (self.f_pos[0] - (SIZE / 2),
                                       self.f_pos[1] - (SIZE / 2)))

    def show_hs_tab(self):
        """ take the high-score data dict and show it on the display"""
        pos_y_tab = 220
        for i in range(10):
            self.show_text(f"{self.hs_data[str(self.hs_int[i])]}",
                           FG_P, WIN_M_W + 40, pos_y_tab, Fon.fo40)
            self.show_text(f"{self.hs_int[i]}",
                           FG_P, WIN_M_W + 280, pos_y_tab, Fon.fo40)
            pos_y_tab += 40
            pg.display.flip()

    def show_go_message(self):
        """ this message will be shown if the game is over"""
        self.win.fill(BG_G)
        self.win.blit(GamePics.go_logo, (WIN_M_W - 90, Y_TOP))
        self.show_hs_tab()
        if self.hs_stat:
            self.show_text(f"Neuer Highscore: {self.hs_new}",
                           FG_A, WIN_M_W - 20, 140, Fon.fo40)
            self.show_text("Name eingeben:",
                           FG_A, WIN_M_W - 300, Y_BOT - 20, Fon.fo40)
            self.entry_name()
            self.hs_data[f"{self.hs_new}"] = self.u_text
            del self.hs_data[str(min(self.hs_int))]
            self.hs_int.append(self.score)
            self.sort_list()
            self.hs_int.pop()
            self.w_data()
        else:
            self.show_text("High-score leider nicht geschlagen",
                           FG_P, WIN_M_W - 100, Y_BOT - 23, Fon.fo40)
            pg.display.update()
            time.sleep(3)
        self.restart_game()
        self.win.fill(BG_G)
        self.g_stat = 0

    def show_text(self, text, col, p_x, p_y, fo_st):
        """ a small def to create a textfield"""
        act_text = fo_st.render(text, True, pg.Color(col))
        rect_text = act_text.get_rect()
        rect_text.x = p_x
        rect_text.y = p_y
        self.win.blit(act_text, rect_text)

    def show_st_text(self):
        """ show the start window"""
        self.win.blit(GamePics.pg_logo, (5, 669))
        self.win.blit(GamePics.sp_logo, (300, 30))
        self.show_text("Highscores:", FG_P, WIN_M_W + 40, 160, Fon.fo40)
        self.show_text("Start - SPACE-Taste drücken", FG_P, WIN_M_W - 50, Y_BOT + 20, Fon.fo16)
        self.show_text("Beenden - ESC-Taste drücken", FG_P, WIN_M_W + 200, Y_BOT + 20, Fon.fo16)

    def speed_up(self):
        """ raise the speed and the level of the game"""
        self.speed += 2
        self.level += 1

    def load_hs_list(self):
        """ load the high-score data from json file"""
        hs_keys_str = list(self.hs_data.keys())
        for i, n in enumerate(hs_keys_str):
            self.hs_int.append(int(n))
            print(i)
        self.sort_list()

    def sort_list(self):
        self.hs_int.sort()
        self.hs_int.reverse()

    def w_data(self):
        """ WRITE THE NEW HIGH-SCORE TO THE .JSON FILE """
        with open(PA_HS_FILE, "w", encoding='UTF-8') as file:
            json.dump(self.hs_data, file)

    def main_loop(self):
        """ this is the main loop"""
        while True:
            self.event_control()
            if self.g_stat == 0:
                self.start_loop()
            elif self.g_stat == 1:
                self.game_loop()
            elif self.g_stat == 2:
                self.end_loop()
            pg.display.update()
            self.clock.tick(self.speed)

    def start_loop(self):
        """ this loop shows the start-window"""
        self.show_hs_tab()
        self.show_st_text()

    def game_loop(self):
        """ the game loop is the main function"""
        self.move_snake()
        self.get_food()
        self.repaint()
        self.game_over()
        self.paint_hud()

    def end_loop(self):
        """ the end loop shows the high-score list and an entry-field"""
        self.show_hs_tab()
        self.show_go_message()


class GamePics:
    """ define all pics of the game"""
    PA_PG_LOGO = str(pl.Path().absolute()) + "/PycharmProjects/snakepie/pg_logo.png"
    PA_SP_LOGO = str(pl.Path().absolute()) + "/PycharmProjects/snakepie/sp_logo.png"
    PA_GO_LOGO = str(pl.Path().absolute()) + "/PycharmProjects/snakepie/go_logo.png"
    PA_F_PIC = str(pl.Path().absolute()) + "/PycharmProjects/snakepie/py_logo.png"
    PA_BODY = str(pl.Path().absolute()) + "/PycharmProjects/snakepie/body.png"
    pg_logo = pg.image.load(PA_PG_LOGO)
    sp_logo = pg.image.load(PA_SP_LOGO)
    go_logo = pg.image.load(PA_GO_LOGO)
    f_pic = pg.image.load(PA_F_PIC)
    b_pic = pg.image.load(PA_BODY)


WIN_W, WIN_H, SIZE = 1080, 720, 20

WIN_M_W, WIN_M_H = WIN_W / 3, WIN_H / 3
FG_A, FG_P, BG_G = (0, 255, 0), (255, 255, 255), (0, 0, 0)
Y_TOP, Y_BOT = 30, 670
PA_HS_FILE = str(pl.Path().absolute()) + "/PycharmProjects/snakepie/h_score.json"

if __name__ == "__main__":
    SnakeGame()
