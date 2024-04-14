import re
import mesa 

from agents import Player, Planet
from scheduler import RandomActivationByTypeFiltered
from global_constants import * 


class Game(mesa.Model):
    
    def __init__(self, width=WIDTH, height=HEIGHT, num_players=NUM_PLAYERS, num_planets=NUM_PLANETS, 
                 tech_planet=TECH_PLANETS, gold_planet=GOLD_PLANETS, taxes_planet=TAXES_PLANET):
        """
        width: Ancho de la matriz donde se encontraran los agentes
        height: Alto de la matriz donde se encontraran los agentes 
        num_players: Se trata del numero de jugadores que queremos en la partida
        num_planets: Se trata del numero de planetas que querremos en la partida
        tech_planet: Tecnología que tendrá cada planeta
        gold_planet: Oro que tendrá cada planeta
        taxes_planet: Impuesto que deberán pagar por cada planeta
        """
        super().__init__()
        self.width = width
        self.height = height
        self.num_players = num_players
        self.num_planets = num_planets
        self.tech_planet = tech_planet
        self.gold_planet = gold_planet
        self.taxes_planet = taxes_planet
        self.list_agents = []
        self.list_planets = []
        self.list_agents_colors = ["Aqua","Green","Pink","Gray","Purple","Yellow"]
        # Se moverán uno cada vez, es decir el primer turno se movera primero el agente 1 y el siguiente el agente 2 primero
        self.schedule = RandomActivationByTypeFiltered(self)
        # Creacion de la matriz Torus=True significa que si el agente se encuentra en la izquierda del todo y sigue a la izquierda aparecera en la derecha 
        self.grid = mesa.space.MultiGrid(self.width, self.height, torus=True)
        # Tener un control sobre el numero de turnos del modelo
        self.step_count = 0

        # Datos que queremos ver 
        # self.datacollector = mesa.DataCollector(
        #     {
        #         "Number of players": lambda l: l.schedule.get_type_count(Player)
        #     }
        # )
        
        # Creacion de los jugadores evito que haya dos agentes en el mismo espacio con chekspace y creo y añado el agente
        for _ in range(self.num_players):
            location_found = False
            while not location_found:
                location = self.checkSpace(MOORE_PLAYER)
                location_found = location[0]
            pos = location[1]
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
        for _ in range(self.num_planets):
            location_found = False
            while not location_found:
                location = self.checkSpace(MOORE_PLANET, planet_space=True)
                location_found = location[0]
            pos = location[1]
            planet = Planet(self.next_id(), self, pos ,self.random.randrange(0, self.tech_planet),
                            self.random.randrange(0, self.gold_planet), self.taxes_planet, moore=MOORE_PLANET)
            self.list_planets.append(planet)
            self.grid.place_agent(planet, pos)
            self.schedule.add(planet)
        self.running = True
        #self.datacollector.collect(self)

    def checkSpace(self, moore, planet_space=False):
        pos = (self.random.randrange(self.width), self.random.randrange(self.height))
        if planet_space:
            neighbors = self.grid.get_neighbors(pos, moore, include_center=True, radius=2)
        else:
            neighbors = self.grid.get_neighbors(pos, moore, include_center=True, radius=2)
        # Añado a la lista los vecinos que sean del tipo player o planet para saber si tiene otros planetas o jugadores alrededor 
        list_agents = [obj for obj in neighbors if (isinstance(obj, Player) or isinstance(obj, Planet))]
        if len(list_agents) > 0:
            return False, pos
        return True, pos

    def propertiesAgents(self):
        summary = {}    
        for i in self.list_agents:
            summary[i] = i.getAgentInfo(verbose=True)
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
                    elif initial_factories == value:
                        check_factories_list.append(value) 
        # Si solo hay un valor significa que es el que mas planetas tiene por lo que se le recompensará con un punto estelar
        if len(check_planets_list) == 1:
            #print(f"El agente con más planetas es {agent_more_planets.getId()}")
            agent_more_planets.addPoint()
        # El mismo funcionamiento con el numero de fabricas
        if len(check_factories_list) == 1:
            #print(f"El agente con más fabricas es {agent_more_factories.getId()}")
            agent_more_factories.addPoint()

    # Método para añadir de manera dinámica atributos al modelo o al agente
    def _addAttribute(self, class_name, attribute_name, new_type, value, id=None):
        if new_type == "int":
            value = int(value)
        elif new_type == "float":
            value = float(value)
        elif new_type == "bool":
            if value == "true":
                value = True
            elif value == "false":
                value = False
        if class_name == "m":
            setattr(self, attribute_name, value)
        elif class_name == "a":
            agent_selected = self.list_agents[int(id)]
            setattr(agent_selected, attribute_name, value)
            print(agent_selected.__getattribute__(attribute_name))

    def step(self):
        self.step_count += 1
        for agent in self.list_agents:
            # Tengo que crear una lógica en el modelo para que dependiendo de las habilidades del agente haga una cosa u otra
            # Si el valor aletorio es menor que EPSILON (0.1) realizará una accion aleatoria, esto permite que no todos los agentes tengan el mismo comportamiento
            if self.random.uniform(0, 1) < EPSILON:
                # El agente cogera un valor de la lista de posibles acciones del modelo. [0] es porque devolvera una lista y necesito el elemento
                choose_action = self.random.choices(POSSIBLE_ACTIONS)[0]
            else:
                # Si es el primer turno interesa que se mnuevan para poder generar la nave con recursos para poder moverse aunque no tengan recursos
                if self.step_count == 1:
                    # En el primer turno elijo un movimiento aleatorio
                    choose_action = self.random.choices(POSSIBLE_ACTIONS[0:8])[0]
                elif agent.getGold() < 30:
                    # Si tiene arma perseguir a algún jugador para luchar y poder ganar recursos del combate
                    if agent.getGold() < 0:
                        print("Buscando a un agente para luchar")
                        # Crear lógica para buscar un jugador por ahora se mueve random
                        choose_action = self.random.choices(POSSIBLE_ACTIONS[0:8])[0]
                    else:
                        # Buscar un planeta cercano para conquistarlo y poder ganar sus recursos
                        print("Buscando planeta cercano")
                        # Crear lógica para buscar un planeta que no este conquistado por ahora se mueve random 
                        choose_action = self.random.choices(POSSIBLE_ACTIONS[0:8])[0]
    # Comprobar para que pueda hacer otra cosa y no se quede todo el rato haciendo esta accion una vez se cumplan las demas condiciones
                elif agent.getGold() > 40 and agent.getTech() > 20 and agent.getFactories() > 6 and (agent.getNumPlayerWeapon() < 3 or agent.getAgentUpgrades().isUpgradeAvailable()):
                    # Si tengo suficientes fabricas para poder sobrevivir economicamente tengo que desarrollar armas
                    if agent.getNumPlayerWeapon() == 3:
                    # Tengo que comprobar si puedo hacer mejoras de los recurosos de fabricas o la mejora de daño
                        if agent.getAgentUpgrades().isUpgradeAvailable() and (agent.getGold() > UPGRADE_FACTORIES_GOLD_COST and agent.getTech() > UPGRADE_FACTORIES_TECH_COST):
                            # Seleccionar algun valor de la lista de opciones de mejoras y hacer las mejoras
                            choose_action = ACTION_SPACE.get("Weapon")
                        else:
                            choose_action = self.random.choices(POSSIBLE_ACTIONS[0:8])[0]
                    else:
                        choose_action = ACTION_SPACE.get("Weapon")     
                    
                elif agent.getGold() >= 30 and agent.getTech() >= 5:
                    # Crear una fabrica para poder conseguir recursos y sobrevivir
                    choose_action = ACTION_SPACE.get("Factory")
                else:
                    choose_action = self.random.choices(POSSIBLE_ACTIONS[0:8])[0]
            # Tengo que pensar alguna forma para poder moverme y que no se tiren quietos todo el rato, porque es muy poco dinámico y no hay casi exploración 
            print(f"agent: {agent.getId()} elige el movimiento {choose_action}")
            agent.step(choose_action)
        for planet in self.list_planets:
            planet.step()
        self.addStellarPoints()
# Forma de modificar los atributos en ejecucion mediante los metodos exec, parecido a poner una condicion y ejecutarlo directamente
#         if self.step_count % 10 == 0: 
#             new_atribute = input("""Introduzca un nuevo atributo, señalando si quieres que sea para el modelo o para un agente determinado. 
# Ejemplo (M  nombre_var tipo_var valor) ó (A id(0-{}) nombre_var tipo_var valor): """.format(len(self.list_agents))).lower()
#             if new_atribute == "":
#                 pass
#             else:
#                 if re.match("^m\s[a-z(0-9)?]+\s(int|bool|float|str)\s[a-z0-9]+" + "|" + "^a\s[0-9]\s[a-z(0-9)?]+\s(int|bool|float|str)\s[a-z0-9]+",
#                             new_atribute):
#                     method_attributes = new_atribute.split()
#                     if len(method_attributes) == 5:
#                         self.addAttribute(class_name=method_attributes[0], attribute_name=method_attributes[2],
#                                         new_type=method_attributes[3], value=method_attributes[4], id=method_attributes[1])
#                     else:
#                         self.addAttribute(class_name=method_attributes[0], attribute_name=method_attributes[1],
#                                         new_type=method_attributes[2], value=method_attributes[3])
#                     print(self.__getattribute__(method_attributes[1]))
#             code = """
# print(self.step_count)
# setattr(self, "allies", False)

# print(dir(self))

# for i in dir(self):
#     if i.startswith("_"):
#         continue
#     elif i == "list_agents":
#         random_agent = self.__getattribute__(i)[0]
#         random_agent.setAgentColor("black")
# """
#             exec(code)
#             self.allies = True
#             print(self.allies)
        #self.datacollector.collect(self)

    # Método para comprobar rápidamente el funcionamiento del juego sin tener que ejecutar el servidor
    def run_model(self):
        done = False
        i = 1 
        while not done:
            print(f"step {i}")
            self.step()
            for agent in self.schedule.agents:
                if type(agent) == Player:
                    print(f"Player {agent.getAgentPos(verbose=True)}")
                    print(f"Resources: {agent.getAgentInfo(verbose=True)}")
                    if agent.getStellarPoints() >= 100:
                        done = True
            i += 1
            print("------")
                    
if __name__ == "__main__":
    model = Game()
    model.run_model()