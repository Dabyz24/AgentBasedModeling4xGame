import mesa 

from agents import Player, Planet
from scheduler import RandomActivationByTypeFiltered

# Tendrá en cuenta las diagonales
MOORE_PLAYER = True
MOORE_PLANET = True

class Game(mesa.Model):
    
    width = 20 
    height = 20
    num_players = 3
    num_planets = 10
    prob_factory = 0.3
    prob_weapon = 0.1
    prob_space_ship = 0.6
    tech_planet = 20
    gold_planet = 30
    taxes_planet = 20
    # Posiciones guardadas para solo 3 jugadores y 10 planetas, si se quiere aumentar el número de jugadores se tendrá que aumentar la lista con su posicion
    list_possible_player_pos = [(0,10),(19,10),(10,0)]
    list_possible_planet_pos = [(6,16),(3,18),(18,18),(12,18),(14,12),(10,10),(5,8),(4,4),(14,5),(17,1)]
    
    def __init__(self, width=20, height=20, num_players=3, num_planets=10, prob_factory=0.3, prob_weapon=0.1, 
                 prob_space_ship=0.6, tech_planet=20, gold_planet=30, taxes_planet=20):
        """
        width: Ancho de la matriz donde se encontraran los agentes
        height: Alto de la matriz donde se encontraran los agentes 
        num_players: Se trata del numero de jugadores que queremos en la partida
        num_planets: Se trata del numero de planetas que querremos en la partida
        prob_factory: Probabilidad de construir una fabrica en el turno
        prob_weapon: Probabilidad de construir un arma en el turno
        prob_space_ship: Probabilidad de construir una nave espacial para la exploracion en el turno
        tech_planet: Tecnología que tendrá cada planeta
        gold_planet: Oro que tendrá cada planeta
        taxes_planet: Impuesto que deberán pagar por cada planeta
        """
        super().__init__()
        self.width = width
        self.height = height
        self.num_players = num_players
        self.num_planets = num_planets
        self.prob_factory = prob_factory
        self.prob_weapon = prob_weapon 
        self.prob_space_ship = prob_space_ship
        self.tech_planet = tech_planet
        self.gold_planet = gold_planet
        self.taxes_planet = taxes_planet
        self.list_agents = []
        self.list_agents_colors = ["Aqua","Green","Pink","Gray","Purple","Yellow"]
        # Se moverán uno cada vez, es decir el primer turno se movera primero el agente 1 y el siguiente el agente 2 primero
        self.schedule = RandomActivationByTypeFiltered(self)
        # Creacion de la matriz Torus=True significa que si el agente se encuentra en la izquierda del todo y sigue a la izquierda aparecera en la derecha 
        self.grid = mesa.space.MultiGrid(self.width, self.height, torus=True)
        # Creacion de variables para poder implentar el Q-Learning 
        self.state_space = [i for i in range(self.width*self.height)]
        self.action_space = {"LLD": 0, "L": 1, "ULD": 2, "D": 3, "U": 4, "LRD": 5, "R": 6, "URD": 7, "F": "Factory", "W": "Weapon"}
        """ Las siglas se corresponden con:
                LLD = Lower Left Diagonal, L = Left, ULD = Upper Left Diagonal
                D = Down, U = Up
                LRD = Lower Right Diagonal, R = Right, URD = Upper right diagonal
            y hacen referencia al indice de la lista de posibles movientos de cada agente 
            F = Fabricar una fabrica 
            W = Crear un arma o mejorar una habilidad 
        """
        self.possible_actions = ["LLD", "L", "ULD", "D", "U", "LRD", "R", "URD", "F", "W"]

        # Datos que queremos ver 
        # self.datacollector = mesa.DataCollector(
        #     {
        #         "Number of players": lambda l: l.schedule.get_type_count(Player)
        #     }
        # )
        
        # Creacion de los jugadores evito que haya dos agentes en el mismo espacio con chekspace y creo y añado el agente
        for i in range(self.num_players):
            pos = self.list_possible_player_pos[i]
            player = Player(self.next_id(), self, pos, moore=MOORE_PLAYER)
            # Una vez creado le asigno un color de la lista de colores, cada uno tendrá un color único
            try:
                chosen_color = self.list_agents_colors.pop(self.random.randrange(0, len(self.list_agents_colors)))
            except:
                # Si se añaden más jugadores que colores en la lista el color será negro
                chosen_color = "black"
            player.setAgentColor(chosen_color)
            self.list_agents.append(player)
            self.grid.place_agent(player, pos)
            self.schedule.add(player)
        
        # Creacion de los planetas 
        for i in range(self.num_planets):
            pos = self.list_possible_planet_pos[i]
            planet = Planet(self.next_id(), self, pos ,self.random.randrange(0, tech_planet),
                            self.random.randrange(0, self.gold_planet), self.taxes_planet, moore=MOORE_PLANET)
            self.grid.place_agent(planet, pos)
            self.schedule.add(planet)
        self.running = True
        #self.datacollector.collect(self)

    def propertiesAgents(self):
        summary = {}    
        for i in self.list_agents:
            summary[i] = i.getAgentInfo()
        return summary
            
    def checkAgentsValues(self):
        values = {}
        for i in self.list_agents:
            values[i] = i.getResources()
        return values
    
    def addStellarPoints(self):
        dict_values = self.checkAgentsValues()
        agent_more_factories = ""
        agent_more_planets = ""
        initial_factories = 0
        initial_planets = 0
        check_factories_list = []
        check_planets_list = []
        for player, resources in dict_values.items():
            # Comparar los valores de num fabricas y num de planetas y ver cual es el mas alto 
            for key, value in resources.items():
                if key == "Planets":
                # Si el valor de los planetas es mayor al numero inicial se guarda el jugador y se guarda el valor en la lista
                    if initial_planets < value:
                        agent_more_planets = player
                        initial_planets = value
                        check_planets_list = [value]
                    # Si otro agente tiene el mismo valor se guarda en la lista 
                    elif initial_planets == value:
                        check_planets_list.append(value)
                if key == "Factories":
                    if initial_factories < value:
                        agent_more_factories = player
                        initial_factories = value
                        check_factories_list = [value]
                    elif initial_planets == value:
                        check_factories_list.append(value) 
        # Si solo hay un valor significa que es el que mas planetas tiene por lo que se le recompensará con un punto estelar
        if len(check_planets_list) == 1:
            #print(f"El agente con más planetas es {agent_more_planets.getId()}")
            agent_more_planets.addPoint()
        # El mismo funcionamiento con el numero de fabricas
        if len(check_factories_list) == 1:
            #print(f"El agente con más fabricas es {agent_more_factories.getId()}")
            agent_more_factories.addPoint()

    def step(self):
        self.schedule.step()
        self.addStellarPoints()
        #self.datacollector.collect(self)
    
    def run_model(self):
        done = False
        i = 1 
        while not done:
            print(f"step {i}")
            self.step()
            for agent in self.schedule.agents:
                if type(agent) == Player:
                    print(f"Player {agent.getAgentPos()}")
                    print(f"Resources: {agent.getAgentInfo()}")
                    if agent.getStellarPoints() >= 100:
                        done = True
            i += 1
            print("------")
            # Actualizar la tabla Q de cada agente 
                    

model = Game()
model.run_model()