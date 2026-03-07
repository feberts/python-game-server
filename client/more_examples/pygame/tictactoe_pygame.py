#!/usr/bin/env python3
"""
This is a graphical tic-tac-toe client using Pygame (www.pygame.org). It is
based on an implementation found on GitHub.

The original implementation is a stand-alone program to be used by two human
players on the same machine. It was modified to use the game server API to play
against a remote client. Most of the game logic was removed and replaced with
calls to API functions.

Author of the original implementation: Rockikz
https://github.com/x4nth055/pythoncode-tutorials/tree/master/gui-programming/tictactoe-game
Accessed: 2024-12-12
"""

"""
MIT License

Copyright (c) 2019 Rockikz

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
"""

import os
import pygame
import threading

from game_server_api import GameServerAPI, GameServerError, IllegalMove

game = GameServerAPI(server='127.0.0.1', port=4711, game='TicTacToe', token='mygame', players=2)

pygame.init()
pygame.font.init()

window_size = (450, 500)

screen = pygame.display.set_mode(window_size)
pygame.display.set_caption("Tic Tac Toe")

class TicTacToe():
    def __init__(self, table_size):
        self.my_id = game.join()
        self.state = game.state()

        self.table_size = table_size
        self.cell_size = table_size // 3
        self.table_space = 20

        self.mark = self._load_mark('mark_x.svg'), self._load_mark('mark_o.svg')

        self.background_color = (255, 174, 66)
        self.table_color = (50, 50, 50)
        self.line_color = (0, 175, 0)
        self.instructions_color = (17, 53, 165)
        self.font = pygame.font.SysFont(["Courier New", pygame.font.get_default_font()], 35, True)
        self.FPS = pygame.time.Clock()

    def _load_mark(self, file_name):
        path = os.path.dirname(__file__) + '/'
        img = pygame.image.load(path + file_name)
        return pygame.transform.scale(img, (self.cell_size, self.cell_size))

    # draws table representation
    def _draw_table(self):
        tb_space_point = (self.table_space, self.table_size - self.table_space)
        cell_space_point = (self.cell_size, self.cell_size * 2)
        pygame.draw.line(screen, self.table_color, [tb_space_point[0], cell_space_point[0]], [tb_space_point[1], cell_space_point[0]], 8)
        pygame.draw.line(screen, self.table_color, [cell_space_point[0], tb_space_point[0]], [cell_space_point[0], tb_space_point[1]], 8)
        pygame.draw.line(screen, self.table_color, [tb_space_point[0], cell_space_point[1]], [tb_space_point[1], cell_space_point[1]], 8)
        pygame.draw.line(screen, self.table_color, [cell_space_point[1], tb_space_point[0]], [cell_space_point[1], tb_space_point[1]], 8)

    # processing clicks to move
    def _move(self, pos):
        try:
            x, y = pos[0] // self.cell_size, pos[1] // self.cell_size
            game.move(position=y * 3 + x)
        except IllegalMove as e:
            print(e)
        except GameServerError as e:
            print(e)
        except:
            print("Click inside the table only")

    # draws character of the recent player to the selected table cell
    def _draw_char(self, x, y, player):
        screen.blit(self.mark[player], (x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size))

    # instructions and game-state messages
    def _message(self):
        if self.state['gameover']:
            screen.fill(self.background_color, (135, 445, 188, 35))
            if self.state['winner'] == self.my_id:
                msg = '  You win! '
            elif self.state['winner'] is None:
                msg = 'No winner ...'
            else:
                msg = 'You lose ...'
            msg = self.font.render(msg, True, self.instructions_color,self.background_color)
            screen.blit(msg,(110,445))
            self._strike()
        else:
            screen.fill(self.background_color, (135, 445, 188, 35))

            if self.my_id in self.state['current']:
                instr = 'Your turn!   '
            else:
                instr = 'Opponent ... '
            instructions = self.font.render(instr, True, self.instructions_color,self.background_color)
            screen.blit(instructions,(110,445))

    def _strike(self):
        if self.state['gameover'] and self.state['winner'] is not None:
            b = self.state['board']
            if b[0] == b[1] == b[2] and b[2] != -1:
                self._pattern_strike((0,0),(2,0),"hor")
            elif b[3] == b[4] == b[5] and b[5] != -1:
                self._pattern_strike((0,1),(2,1),"hor")
            elif b[6] == b[7] == b[8] and b[8] != -1:
                self._pattern_strike((0,2),(2,2),"hor")
            elif b[0] == b[3] == b[6] and b[6] != -1:
                self._pattern_strike((0,0),(0,2),"ver")
            elif b[1] == b[4] == b[7] and b[7] != -1:
                self._pattern_strike((1,0),(1,2),"ver")
            elif b[2] == b[5] == b[8] and b[8] != -1:
                self._pattern_strike((2,0),(2,2),"ver")
            elif b[0] == b[4] == b[8] and b[8] != -1:
                self._pattern_strike((0,0),(2,2),"left-diag")
            elif b[2] == b[4] == b[6] and b[6] != -1:
                self._pattern_strike((2,0),(0,2),"right-diag")

    # strikes a line to winning patterns if already has
    def _pattern_strike(self, start_point, end_point, line_type):
        # gets the middle value of the cell
        mid_val = self.cell_size // 2

        # for the vertical winning pattern
        if line_type == "ver":
            start_x, start_y = start_point[0] * self.cell_size + mid_val, self.table_space
            end_x, end_y = end_point[0] * self.cell_size + mid_val, self.table_size - self.table_space

        # for the horizontal winning pattern
        elif line_type == "hor":
            start_x, start_y = self.table_space, start_point[-1] * self.cell_size + mid_val
            end_x, end_y = self.table_size - self.table_space, end_point[-1] * self.cell_size + mid_val

        # for the diagonal winning pattern from top-left to bottom right
        elif line_type == "left-diag":
            start_x, start_y = self.table_space, self.table_space
            end_x, end_y = self.table_size - self.table_space, self.table_size - self.table_space

        # for the diagonal winning pattern from top-right to bottom-left
        elif line_type == "right-diag":
            start_x, start_y = self.table_size - self.table_space, self.table_space
            end_x, end_y = self.table_space, self.table_size - self.table_space

        # draws the line strike
        pygame.draw.line(screen, self.line_color, [start_x, start_y], [end_x, end_y], 16)

    def _draw_marks(self):
        for y in range(3):
            for x in range(3):
                player = self.state['board'][y * 3 + x]
                if player in (0, 1):
                    self._draw_char(x,y,player)

    def _request_state(self):
        while True:
            self.state = game.state()
            self._draw_marks()

            if self.state['gameover']:
                return

    def main(self):
        screen.fill(self.background_color)
        self._draw_table()
        running = True
        threading.Thread(target=self._request_state, args=(), daemon=True).start()

        while running:
            self._message()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    self._move(event.pos)

            pygame.display.flip()
            self.FPS.tick(30)

if __name__ == "__main__":
    g = TicTacToe(window_size[0])
    g.main()
