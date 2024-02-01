import pygame as pg 
from random import randint

class Ant:
    def __init__(self, app, pos, color):
        self.app = app
        self.color = color 
        self.x, self.y = pos
        self.increments = [(1,0),(0,1),(-1,0),(0,-1)]
        
    def run(self):
        
        value = self.app.grid[self.y][self.x]
        self.app.grid[self.y][self.x] = not value

        SIZE = self.app.CELL_SIZE
        rect = self.x * SIZE, self.y * SIZE, SIZE -1, SIZE - 1

        
        pg.draw.rect(self.app.screen, self.color, rect)
        # prevPos = (self.y, self.x)
        

        move = self.increments[randint(0, len(self.increments)-1)]
        dx, dy = move
        self.x = (self.x + dx) % self.app.COLS
        self.y = (self.y + dy) % self.app.ROWS
