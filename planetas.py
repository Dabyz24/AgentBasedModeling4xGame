from random import randrange
import pygame as pg

class Planetas:
    def __init__(self, app, pos, length ,tecnologia, dinero, impuesto):
        self.app = app
        self.x, self.y = pos
        self.len = length
        self.recursos = [tecnologia, dinero]
        self.tax = impuesto

    
    @staticmethod
    def get_color(self):
        if self.recursos[0] > self.recursos[1]:
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