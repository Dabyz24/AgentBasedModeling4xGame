import mesa

from agents import Player, Planets
from model import Game

def game_portrayal(agent):
    if agent is None:
        return
    
    portrayal = {}

    if type(agent) is Player:
        portrayal["Shape"] = "rect"
        portrayal["scale"] = 0.9
        portrayal["Layer"] = 1
        portrayal["Text"] = agent.getResources()
        portrayal["Text_color"] = "Black"

    if type(agent) is Planets:
            portrayal["Shape"] = "circle"
            portrayal["scale"] = 0.9
            portrayal["Layer"] = 1
            portrayal["Text"] = agent.isInhabit()
            portrayal["Text_color"] = "Black"

    return portrayal

# Añadir canvas element y revisar la creacion del portrayal