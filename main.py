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


class Direction(Enum):
    """ THIS CLASS DEFINE THE DIRECTIONS """
    UP = 1
    DOWN = 2
    RIGHT = 3
    LEFT = 4


class Col:
    """ define the colors of the game"""
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    PURPLE = (128, 0, 128)


def quit_game():
    """ quit the game and close the window"""
    pg.quit()
    sys.exit(0)


class SnakeGame:
    """ the class snakegame include the whole game"""

    def __init__(self):
        self.direction = Direction.RIGHT
        self.PA_HS_FILE = str(pl.Path().absolute()) + "/PycharmProjects/snakepie/h_score.json"
        pg.init()
        pg.display.set_caption("snakekpie")
        # define constants
        self.win_w, self.win_h = 1080, 720
        self.size = 20
        self.fo60 = pg.font.SysFont("Arial", 60)
        self.fo40 = pg.font.SysFont("Arial", 40)
        self.fo16 = pg.font.SysFont("Arial", 16)

        self.win = pg.display.set_mode((self.win_w, self.win_h))
        self.clock = pg.time.Clock()

        self.speed = 10
        self.level = 1
        self.game_stat = 0
        self.name_stat = 0
        self.s_pos = [250, 250]
        self.s_body = [[250, 250],
                       [240, 250],
                       [230, 250]]

        self.f_pos = [random.randint(20, 1000), random.randint(20, 700)]

        self.score = 0
        self.hs_data = self.r_data()
        self.hs_old = self.take_highscore()
        self.hs_new = self.hs_old

        # all things for the input field for highscore name
        self.active = False
        self.input_rect = pg.Rect(200, 400, 100, 32)
        self.color = (10, 10, 10)

        self.user_text = ""

        self.main_loop()

    def take_highscore(self):
        """ This function take the highscores as string, format to int and sort the list.
        The function returns the highscore as an int"""
        hs_str = list(self.hs_data.keys())
        hs_int = []
        for i, n in enumerate(hs_str):
            hs_int.append(int(n))
            print(i)
        hs_int.sort()
        return hs_int[-1]

    def r_data(self):
        """ READ THE HIGHSCOREFILE AND RETURN A DICT WITH THE DATA"""
        with open(self.PA_HS_FILE, "r", encoding='UTF-8') as file:
            data = json.load(file)
        return data

    def w_data(self):
        """ WRITE THE NEW HIGHSCORE TO THE .JSON FILE """
        with open(self.PA_HS_FILE, "w", encoding='UTF-8') as file:
            json.dump(self.hs_data, file)

    def event_control(self):
        """ handle the key events."""
        for event in pg.event.get():
            if event.type == pg.MOUSEBUTTONDOWN:
                if self.input_rect.collidepoint(event.pos):
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
                    self.game_stat = 1

    def move_snake(self):
        """ change the direction of the snake"""
        if self.direction == Direction.UP:
            self.s_pos[1] -= self.size
        if self.direction == Direction.DOWN:
            self.s_pos[1] += self.size
        if self.direction == Direction.LEFT:
            self.s_pos[0] -= self.size
        if self.direction == Direction.RIGHT:
            self.s_pos[0] += self.size
        self.s_body.insert(0, list(self.s_pos))

    def generate_new_food(self):
        """ create a new food in the window"""
        self.f_pos[0] = random.randint(5, ((self.win_w - 2) // self.size)) * self.size
        self.f_pos[1] = random.randint(5, ((self.win_h - 2) // self.size)) * self.size

    def get_food(self):
        """ check if the snake the snake get the food.
        create a new food if the snake hit the food"""
        if abs(self.s_pos[0] - self.f_pos[0]) < 20 and abs(self.s_pos[1] - self.f_pos[1]) < 20:
            self.score += 10
            self.generate_new_food()
            if self.score % 100 == 0:
                self.speed_up()
        else:
            self.s_body.pop()

    def speed_up(self):
        """ raise the speed and the level of the game"""
        self.speed += 2
        self.level += 1

    def repaint(self):
        """ repaint the display for moving the snake"""
        self.win.fill(pg.Color("black"))
        for body in self.s_body:
            pg.draw.circle(self.win, pg.Color(Col.PURPLE), (body[0], body[1]), int(self.size / 2))
        pg.draw.rect(self.win, pg.Color(255, 0, 0),
                     pg.Rect(self.f_pos[0] - int(self.size / 2),
                             self.f_pos[1] - int(self.size / 2), self.size,
                             self.size))

    def game_over_message(self):
        """ this message will shown if the game is over"""
        self.win.fill(Col.BLACK)
        self.show_text("GAME OVER",
                       Col.WHITE, (int(self.win_w / 2), int(self.win_h / 2) - 100), self.fo40)
        self.show_text(f"Score: {self.score}",
                       Col.WHITE, (int(self.win_w / 2), int(self.win_h / 2)), self.fo40)
        if self.hs_new > self.hs_old:
            self.show_text(f"Neuer Highscore: {self.hs_new}",
                           Col.WHITE, (int(self.win_w / 2), int(self.win_h / 2) + 200), self.fo40)
            self.entry_name()
            time.sleep(0.5)
            self.hs_data[f"{self.hs_new}"] = self.user_text
            self.w_data()
        else:
            self.show_text("Leider Highscore nicht geschlagen",
                           Col.WHITE, (int(self.win_w / 2), int(self.win_h / 2) + 200), self.fo40)
            pg.display.flip()
            time.sleep(2)
        self.restart_game()
        self.win.fill(Col.BLACK)
        pg.display.flip()
        self.game_stat = 0

    def entry_name(self):
        self.name_stat = 1
        while self.name_stat:
            for event in pg.event.get():
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_RETURN:
                        self.user_text = self.user_text[:]
                        self.name_stat = 0
                    else:
                        self.user_text += event.unicode
            pg.draw.rect(self.win, self.color, self.input_rect)
            text_surface = self.fo40.render(self.user_text, True, Col.WHITE)
            self.win.blit(text_surface, (self.input_rect.x + 5, self.input_rect.y + 5))
            pg.display.flip()

    def restart_game(self):
        self.score = 0
        self.level = 1
        self.hs_old = self.hs_new
        self.s_pos = [250, 250]
        self.s_body = [[250, 250],
                       [240, 250],
                       [230, 250]]

    def show_text(self, text, col, pos, fo_st):
        """ a small def to create a textfield"""
        act_text = fo_st.render(text, True, pg.Color(col))
        rect_text = act_text.get_rect()
        rect_text.midtop = pos
        self.win.blit(act_text, rect_text)

    def game_over(self):
        """ Check the game state if it game over"""
        if self.s_pos[0] < 0 or self.s_pos[0] > self.win_w - self.size:
            self.game_stat = 2
        if self.s_pos[1] < 0 or self.s_pos[1] > self.win_w - self.size:
            self.game_stat = 2
        for blob in self.s_body[1:]:
            if self.s_pos[0] == blob[0] and self.s_pos[1] == blob[1]:
                self.game_stat = 2

    def paint_hud(self):
        """ show the textes in the game"""
        self.show_text(f"Level: {self.level}", "white", (30, 0), self.fo16)
        self.show_text(f"Score: {self.score}", "white", (125, 0), self.fo16)
        self.show_text("Zum Beenden ESC-Taste drücken", "white", (900, 0), self.fo16)
        self.show_text(f"Highscore: {str(self.hs_new)}", "white", (300, 0), self.fo16)

    def show_starttext(self):
        """ show the start window"""
        self.show_text("SnakePie", "white", (500, 150), self.fo60)
        self.show_text("Zum starten SPACE-Taste drücken", "white", (500, 300), self.fo40)
        self.show_text(f"Highscore: {str(self.hs_old)}", "white", (500, 500), self.fo40)

    def check_h_score(self):
        """ check if a new highscore exist"""
        if self.score > self.hs_new:
            self.hs_new = self.score

    def main_loop(self):
        """ this is the onlyone mainloop"""
        self.direction = Direction.RIGHT
        while True:
            self.event_control()
            if self.game_stat == 0:
                self.start_loop()
            elif self.game_stat == 1:
                self.game_loop()
            elif self.game_stat == 2:
                self.end_loop()
            pg.display.update()
            self.clock.tick(self.speed)

    def start_loop(self):
        """ this loop shows the startwindow"""
        self.show_starttext()

    def game_loop(self):
        """ the game loop is the main function"""
        self.move_snake()
        self.get_food()
        self.repaint()
        self.game_over()
        self.paint_hud()
        self.check_h_score()

    def end_loop(self):
        self.game_over_message()


if __name__ == "__main__":
    SnakeGame()
