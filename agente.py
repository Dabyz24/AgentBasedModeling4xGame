import pygame as pg 
from collections import deque


class Ant:
    def __init__(self, app, pos, color):
        self.app = app
        self.color = color 
        self.x, self.y = pos
        self.increments = deque([(1,0),(0,1),(-1,0),(0,-1)])
        
    def run(self):
        
        value = self.app.grid[self.y][self.x]
        self.app.grid[self.y][self.x] = not value
        
        SIZE = self.app.CELL_SIZE
        rect = self.x * SIZE, self.y * SIZE, SIZE -1, SIZE - 1

        if value:
            pg.draw.rect(self.app.screen, pg.Color("Black"), rect)
        else:
            pg.draw.rect(self.app.screen, self.color, rect)

        self.increments.rotate(1) if value else self.increments.rotate(-1)
        dx, dy = self.increments[0]
        # self.x = (self.x + dx) % self.app.COLS
        # self.y = (self.y + dy) % self.app.ROWS
