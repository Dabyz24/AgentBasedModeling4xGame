import pygame as pg 
from random import randrange
from agents import Ant
from fabrics import Planets
import time

NUMTECHPLANETS = 3
NUMRICHPLANETS = 3

class Juego:
    def __init__(self, WIDTH=1600, HEIGHT=900, CELL_SIZE=10):
        pg.init()
        self.screen = pg.display.set_mode([WIDTH, HEIGHT]) # Crea una pantalla de 1600 por 900
        self.clock = pg.time.Clock()  # Establece el numero de frames de screen 
        self.CELL_SIZE = CELL_SIZE
        self.ROWS, self.COLS = HEIGHT // CELL_SIZE, WIDTH // CELL_SIZE  # 900/10 serán las filas y 1600/10 serán las columnas
        self.grid = [[0 for _ in range(self.COLS)]for _ in range(self.ROWS)]  # EL tablero será una matriz con el numero de columnas y filas inicializado a 0 
        self.ants = [Ant(self, [2, 45], (128,128,128)) for _ in range(1)]
        # Pensar una manera más sofisticada para crear de una manera equilibrada planetas con más tecnología y otros con más dinero, los que tengan más dinero tendrán más impuestos
        techPlanets = [Planets(self, pos=[randrange(200, WIDTH), randrange(100, HEIGHT)], length=randrange(10,30), tech=randrange(30,100), money=randrange(20,30), taxes=randrange(10,30))for _ in range(NUMTECHPLANETS)]
        richPlanets = [Planets(self, pos=[randrange(200, WIDTH), randrange(100, HEIGHT)], length=randrange(10,30), tech=randrange(0,20), money=randrange(20,200), taxes=randrange(10,50))for _ in range(NUMRICHPLANETS)]
        self.planets = techPlanets + richPlanets
        for planet in self.planets:
            planet.draw()

    def run(self):
        while True:
            [ant.run() for ant in self.ants]
            # # Obtener las coordenadas del ratón
            # mouse_x, mouse_y = pg.mouse.get_pos()
            # print(f"{mouse_x}, {mouse_y}")
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
            time.sleep(0.5)
            pg.display.flip()
            self.clock.tick()