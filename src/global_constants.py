# Constantes iniciales para el juego 
WIDTH = 20
HEIGHT = 20
NUM_PLAYERS = 3
NUM_PLANETS = 10
TECH_PLANETS = 20
GOLD_PLANETS = 50
TAXES_PLANET = 25

# Tendrá en cuenta las diagonales
MOORE_PLAYER = True
MOORE_PLANET = True

# Constante para permitir la exploración de acciones aleatorias por parte del agente 
EPSILON = 0.02   # Permite la exploracion del agente si el valor es menor a EPSILON

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
# Si el enemigo tiene oro negativo ganara una cierta cantidad
TECH_FROM_POOR_ENEMIES = 5
GOLD_FROM_POOR_ENEMIES = 10
# Factor de aumento exponencial para el coste de construccion de fabricas 
INCREASE_FACTOR = 1.2
# Numero máximo de armas disponibles en el juego
MAX_NUM_WEAPONS = 3

# Conjunto de acciones posibles por el agente
ACTION_SPACE = {(-1,-1): 0 , (-1,0): 1, (-1,1): 2, (0,-1): 3, (0,1): 4, (1,-1): 5, (1,0): 6, (1,1): 7, "Factory": 8, "Upgrade":9, "Weapon":10}
""" 
Los números se corresponden con:
    0 => Abajo izquierda
    1 => Izquierda
    2 => Arriba izquierda
    3 => Abajo
    4 => Arriba
    5 => Abajo derecha
    6 => Derecha
    7 => Arriba derecha 
    8 => Factory = Construir una fabrica 
    9 => Upgrade = Crear una mejora de una habilidad
    10 => Weapon = Crear un arma  
"""
POSSIBLE_ACTIONS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# Conjunto de comportamientos posibles en el agente
POSSIBLE_BEHAVIOURS = ["Explorer", "Chaser", "Farmer"]
