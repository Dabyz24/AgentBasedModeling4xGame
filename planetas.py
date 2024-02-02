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
    def get_color():
        channel = lambda: randrange(30,220)
        return channel(), channel(), channel()
    
    def draw(self):
        center = self.getPos()
        color = self.get_color()
        pg.draw.circle(self.app.screen, color, center, self.len)

    def getPos(self):
        return (self.x, self.y)