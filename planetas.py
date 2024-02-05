from random import randrange
import pygame as pg

class Planets:
    def __init__(self, app, pos, length ,tech, money, taxes):
        self.app = app
        self.x, self.y = pos
        self.len = length
        self.resources = [tech, money]
        self.tax = taxes

    
    @staticmethod
    def get_color(self):
        if self.resources[0] > self.resources[1]:
            # Más azul si el planeta tiene más tecnología que dinero
            return (0,randrange(0,205),255)
        else:
            # Más amarillo si el planeta tiene más dinero que tecnología
            return (255,255,randrange(0,112))
    
    def draw(self):
        center = self.getPos()
        color = self.get_color(self)
        pg.draw.circle(self.app.screen, color, center, self.len)

    def getPos(self):
        return (self.x, self.y)