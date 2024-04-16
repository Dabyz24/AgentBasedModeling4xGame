# Constantes iniciales para el juego 
WIDTH = 20
HEIGHT = 20
NUM_PLAYERS = 3
NUM_PLANETS = 10
TECH_PLANETS = 20
GOLD_PLANETS = 30
TAXES_PLANET = 50

# Tendrá en cuenta las diagonales
MOORE_PLAYER = True
MOORE_PLANET = True

# Constante para permitir la exploración de acciones aleatorias por parte del agente 
EPSILON = 0.1   # Permite la exploracion del agente si el valor es menor a EPSILON

# Constantes iniciales del jugador
INITIAL_PLAYER_TECH = 30
INITIAL_PLAYER_GOLD = 100
# Constantes para los recursos que gastan por movimiento 
SPACE_SHIP_TECH_COST = 5
SPACE_SHIP_GOLD_COST = 10
# Constantes de las fabricas
TECH_FROM_FACTORIES = 1
GOLD_FROM_FACTORIES = 5
FACTORIES_TECH_COST = 5
FACTORIES_GOLD_COST = 30
# Constantes para el gasto por fabricar armas y las mejoras
WEAPON_TECH_COST = 20
WEAPON_GOLD_COST = 40
UPGRADE_DAMAGE_TECH_COST = 100
UPGRADE_DAMAGE_GOLD_COST = 500
UPGRADE_MOVEMENT_TECH_COST = 200
UPGRADE_MOVEMENT_GOLD_COST = 1000
UPGRADE_FACTORIES_TECH_COST = 300
UPGRADE_FACTORIES_GOLD_COST = 1500
# Constantes para las ganancias de las luchas
TECH_BATTLES_PERCENTAGE = 0.05
GOLD_BATTLES_PERCENTAGE = 0.1

# Conjunto de acciones posibles por el agente
ACTION_SPACE = {(-1,-1): 0 , (-1,0): 1, (-1,1): 2, (0,-1): 3, (0,1): 4, (1,-1): 5, (1,0): 6, (1,1): 7, "Factory": 8, "Weapon":9}
""" 
Las siglas se corresponden con:
        LLD = Lower Left Diagonal, L = Left, ULD = Upper Left Diagonal
        D = Down, U = Up
        LRD = Lower Right Diagonal, R = Right, URD = Upper right diagonal y hacen referencia al indice de la lista de posibles movientos de cada agente 
    F = Fabricar una fabrica 
    W = Crear un arma o mejorar una habilidad 
"""
POSSIBLE_ACTIONS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

# Conjunto de comportamientos posibles en el agente
POSSIBLE_BEHAVIOURS = ["Explorer", "Chaser", "Farmer"]
