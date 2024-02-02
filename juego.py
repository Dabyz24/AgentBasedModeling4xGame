import pygame as pg 
from random import randrange
from agente import Ant
from planetas import Planetas
import time

class Juego:
    def __init__(self, WIDTH=1600, HEIGHT=900, CELL_SIZE=10):
        pg.init()
        self.screen = pg.display.set_mode([WIDTH, HEIGHT]) # Crea una pantalla de 1600 por 900
        self.clock = pg.time.Clock()  # Establece el numero de frames de screen 

        self.CELL_SIZE = CELL_SIZE
        self.ROWS, self.COLS = HEIGHT // CELL_SIZE, WIDTH // CELL_SIZE  # 900/12 serán las filas y 1600/12 serán las columnas
        self.grid = [[0 for _ in range(self.COLS)]for _ in range(self.ROWS)]  # EL tablero será una matriz con el numero de columnas y filas inicializado a 0 
        self.ants = [Ant(self, [2, 45], self.get_color()) for _ in range(1)]


        self.planetas = [Planetas(self, pos=[randrange(200, WIDTH), randrange(100, HEIGHT)], length=randrange(10,30), tecnologia=randrange(0,50), dinero=randrange(20,200), impuesto=randrange(10,50))for _ in range(6)]
        for planeta in self.planetas:
            print(planeta.getPos())
            planeta.draw()

    @staticmethod
    def get_color():
        channel = lambda: randrange(30,220)
        return channel(), channel(), channel()

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