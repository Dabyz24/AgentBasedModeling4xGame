import mesa 

from agents import Player, Planet
from scheduler import RandomActivationByTypeFiltered

class Game(mesa.Model):
    
    width = 20 
    height = 20
    num_players = 2
    num_planets = 5
    prob_factory = 0.4
    prob_weapon = 0.1
    prob_space_ship = 0.6
    tech_planet = 20
    gold_planet = 30
    taxes_planet = 20


    def __init__(self, width=20, height=20, num_players=2, num_planets=5, prob_factory=0.4, prob_weapon=0.1, 
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
        self.listAgents = []
        # Se moverán uno cada vez, es decir el primer turno se movera primero el agente 1 y el siguiente el agente 2 primero
        self.schedule = RandomActivationByTypeFiltered(self)
        # Creacion de la matriz Torus=True significa que si el agente se encuentra en la izquierda del todo y sigue a la izquierda aparecera en la derecha 
        self.grid = mesa.space.MultiGrid(self.width, self.height, torus=True)
        # Datos que queremos ver 
        self.datacollector = mesa.DataCollector(
            {
                "Number of players": lambda l: l.schedule.get_type_count(Player)
            }
        )
        
        # Creacion de los jugadores
        for _ in range(self.num_players):
            pos = (self.random.randrange(self.width), self.random.randrange(self.height))
            player = Player(self.next_id(), self, pos)
            self.listAgents.append(player)
            self.grid.place_agent(player, pos)
            self.schedule.add(player)
        
        # Creacion de los planetas 
        for _ in range(self.num_planets):
            pos = (self.random.randrange(self.width), self.random.randrange(self.height))
            planet = Planet(self.next_id(), self, pos, self.tech_planet, self.gold_planet, self.taxes_planet)
            self.grid.place_agent(planet, pos)
            self.schedule.add(planet)

        self.running = True
        self.datacollector.collect(self)


    def propertiesAgents(self):
        summary = {}    
        for i in self.listAgents:
            summary[i.getId()] = i.getResources()
        return summary
            
    def step(self):
        self.schedule.step()
        self.datacollector.collect(self)
    
    def run_model(self, n):
        for i in range(n):
            self.step()