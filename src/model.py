import os
import mesa 
import math

from agents import Player, Planet
from global_constants import * 
from scheduler import RandomActivationByTypeFiltered


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
        self.schedule = RandomActivationByTypeFiltered(self)
        # Creacion de la matriz Torus=True significa que si el agente se encuentra en la izquierda del todo y sigue a la izquierda aparecera en la derecha 
        self.grid = mesa.space.MultiGrid(self.width, self.height, torus=True)
        # Tener un control sobre el numero de turnos del modelo de una manera simple 
        self.step_count = 0

        # Datos que queremos observar rapidamente 
        self.datacollector = mesa.DataCollector(
            {
                "Explorers": lambda l: l.schedule.get_type_count(Player, lambda agent: agent.getBehaviour() == "Explorer"),
                "Chasers": lambda l: l.schedule.get_type_count(Player, lambda agent: agent.getBehaviour() == "Chaser"),
                "Farmers": lambda l: l.schedule.get_type_count(Player, lambda agent: agent.getBehaviour() == "Farmer"),
                "Specials": lambda l: l.schedule.get_type_count(Player, lambda agent: agent.getBehaviour() not in POSSIBLE_BEHAVIOURS)
            }
        )
        
        # Creacion de los jugadores evito que haya dos agentes en el mismo espacio con chekspace y creo y añado el agente
        for i in range(self.num_players):
            location_found = False
            while not location_found:
                location = self.checkSpace(moore=False)
                location_found = location[0]
            pos = location[1]
            player = Player(self.next_id(), self, pos, moore=MOORE_PLAYER)
            # Una vez creado le asigno un color de la lista de colores, cada uno tendrá un color único
            chosen_color = self.list_agents_colors.pop(self.random.randrange(0, len(self.list_agents_colors)))
            player.setAgentColor(chosen_color)
            # Asigno un comportamiento diferente a cada agente
            player.setBehaviour(POSSIBLE_BEHAVIOURS[(0+i)%len(POSSIBLE_BEHAVIOURS)])
            # Añado el agente a la simulacion, añadiendolo a la lista de agentes al terreno de juego y añadiendolo al schedule
            self.list_agents.append(player)
            self.grid.place_agent(player, pos)
            self.schedule.add(player)
        
        # Creacion de los planetas 
        for i in range(self.num_planets):
            location_found = False
            while not location_found:
                # Quiero que la distancia entre planetas sea de al menos 2 en cada direccion, para que no aparezcan muy juntos
                location = self.checkSpace(MOORE_PLANET, custom_radius=2)
                location_found = location[0]
            pos = location[1]
            planet = Planet(i, self, pos ,self.random.randrange(0, self.tech_planet),
                            self.random.randrange(10, self.gold_planet), self.taxes_planet, moore=MOORE_PLANET)
            self.list_planets.append(planet)
            self.grid.place_agent(planet, pos)
            self.schedule.add(planet)
        self.running = True
        self.datacollector.collect(self)
        # Confirmacion para saber si quieres los comportamientos estandar o quieres establecer comportamientos personalizados
        random_behaviours = input("Do you want standard behaviours? (y/n): ").lower()
        if random_behaviours != "y":
            for agent in self.list_agents:
                agent.setCustomBehaviour()

    # Método que comprueba que exista un espacio de dos casillas entre los jugadores y los planetas
    def checkSpace(self, moore, custom_radius=1):
        pos = (self.random.randrange(self.width), self.random.randrange(self.height))
        neighbors = self.grid.get_neighbors(pos, moore, include_center=True, radius=custom_radius)
        # Añado a la lista los vecinos que sean del tipo player o planet para saber si tiene otros planetas o jugadores alrededor 
        list_agents = [obj for obj in neighbors if (isinstance(obj, Player) or isinstance(obj, Planet))]
        if len(list_agents) > 0:
            return False, pos
        return True, pos

    # Método para poder tener la informcaion agrupada del agente para poder representarla en el servidor
    def propertiesAgents(self):
        summary = {}    
        for i in self.list_agents:
            summary[i] = i.getAgentInfo(verbose=True)
        return summary
    
    # Metodo para poder obtener todos los recursos del agente en un diccionario para poder comprobar el numero de planetas o fabricas
    def checkAgentsValues(self):
        values = {}
        for i in self.list_agents:
            values[i] = i.getResources()
        return values
    
    # Método para añadir un punto estelar en funcion del numero de planetas que tenga el agente
    def addStellarPoints(self):
        dict_values = self.checkAgentsValues()
        for player, resources in dict_values.items():
            # Recorro el diccionario de recursos para comprobar el valor de la key Planets
            for key, value in resources.items():
                if key == "Planets":
                    if value > 0: 
                        player.addPoint(value)

    # Devuelve una lista con las tuplas de posiciones de los jugadores
    def getAllPlayersPos(self):
        aux_list = []
        for i in self.list_agents:
            aux_list.append(i.getAgentPos())
        return aux_list     
    
    # Devuelve una lista con las tuplas de posiciones de todos los planetas sin habitar
    def getAllPlanetPos(self):
        aux_list = []
        for i in self.list_planets:
            if not i.isInhabit():
                aux_list.append(i.getPlanetPos())
        return aux_list     # [(1,2), (13, 4), ...]

    # Método privado que obtiene la distancia entre dos puntos 
    def _distance(self, my_position, target_position):
        #print(f"Posicion del agente actual es {my_position}, y la posicion target es {target_position}")
        return math.sqrt((int(target_position[0]) - int(my_position[0]))**2 + (int(target_position[1]) - int(my_position[1]))**2) 

    # Método para calcular la distancia mas cercana a un punto especifico
    def closestTarget(self, my_position, list_positions):
        minimun_distance = float("inf")
        minimum_tuple = None

        for target_position in list_positions:
            if target_position == my_position:
                continue
            dist = self._distance(my_position, target_position)
            # Si se encuentra en la casilla del al lado que haga una acción aleatoria para evitar que se superponga en todas las situaciones
            if dist == 1:
                minimum_tuple = target_position
                chosen_move = self.random.choices(POSSIBLE_ACTIONS[0:9])[0]
                return minimum_tuple, chosen_move 
            # Si la distancia es menor que el valor anterior se guarda la distancia y la tupla 
            if dist < minimun_distance:
                minimun_distance = dist
                minimum_tuple = target_position
        # Calculo la diferencia en el eje x y en el y para poder calcular el movimiento necesario para acercarse
        difference_x = minimum_tuple[0] - my_position[0]
        difference_y = minimum_tuple[1] - my_position[1]
        move_x =  int(difference_x / abs(difference_x)) if difference_x != 0 else 0
        move_y = int(difference_y / abs(difference_y)) if difference_y != 0 else 0
        # Creo la tupla con el movmiento necesario y se lo paso al diccionario para saber la accion que realizar
        move = (move_x, move_y)
        chosen_move = ACTION_SPACE.get(move)
        return move, chosen_move

    # Método privado para evitar repetir el codigo para elegir el movimiento a realizar por el agente
    def _moveToTarget(self, agent, list_positions):
        chosen_action = -1
        try:
            move , chosen_move = self.closestTarget(agent.getAgentPos(), list_positions)
            # Si el agente tiene activo el run_away, entonces se movera en la dirección contraria para huir
            if agent.getCompleteBehaviour().getRunAway() and (move[0] in [0, 1, -1] and move[1] in [0, 1, -1]) and not move == (0,0):
                new_move = (move[0]*-1, move[1]*-1)
                chosen_action = ACTION_SPACE.get(new_move)
            else:
                chosen_action = chosen_move
        except Exception as ex:
            pass
            # print("An exception occurred:", type(ex).__name__, "-", ex)

        return chosen_action

    # Método para realizar la acción y establecer la accion elegida 
    def chooseAction(self, agent, action):
        if action[0] == "Move":
            if action[1] == "None":
                chosen_action = self.random.choices(POSSIBLE_ACTIONS[0:8])[0]
                return chosen_action
            # Si tiene una dirección definida se moverá hacia el 
            if len(action[2]) == 1:
                chosen_action = self._moveToTarget(agent, action[2])
            else:
                if action[1] == "To_Planet":
                    list_directions = self.getAllPlanetPos()
                    # Si todos los planetas están ocupados, se moveran hacia un agente cercano para luchar y hacer que algun planeta se quede libre
                    if len(list_directions) == 0:
                        list_directions = self.getAllPlayersPos()
                
                elif action[1] == "To_Player":
                    list_directions = self.getAllPlayersPos()
                chosen_action = self._moveToTarget(agent, list_directions)

        elif action[0] == "Upgrade":
            if action[1] == "Factory":
                    agent.setChosenUpgrade(action[1])
                    chosen_action = ACTION_SPACE.get(action[0])
            
            if action[1] == "Damage":
                    agent.setChosenUpgrade(action[1])
                    chosen_action = ACTION_SPACE.get(action[0])
        # Por si los agentes no pueden realizar ninguna acción             
        elif action == "Wait":
            # Si no consigue realizar ninguna acción por alguna mala inversión y se da el caso de que no se puede mover, tendrá que esperar
            chosen_action = -1
        # En el caso que la accion sea weapon o fabrica simplemente elijira esa accion
        else:
            chosen_action = ACTION_SPACE.get(action)

        return chosen_action

    # Si algún agente baja del balance se eliminara de la simulación, si no se resetearán los balances
    def maybeRemoveAgent(self):
        agent_removed = False
        for agent in self.list_agents:
            print(f"El agente {agent.getId()} tiene un balance de {agent.getBalance()}")
            if agent.getBalance() <= 0 and not agent_removed:
                print(f"Agente {agent.getId()} eliminado de la simulacion")
                # Reseteo todos los planetas que tuviera el agente para evitar que sigan habitado por un agente no existente
                agent.resetPlayer()
                # Elimino a el agente de la simulación
                self.list_agents.remove(agent)
                self.grid.remove_agent(agent)
                self.schedule.remove(agent)
                agent_removed = True
            else:
                agent.resetBalance()

    # Añadira un agente a la simulación 
    def addAgent(self, verbose=False):
        pos = (self.random.randrange(self.width), self.random.randrange(self.height))
        next_id = self.next_id()
        player = Player(next_id, self, pos, moore=MOORE_PLAYER)
        # Si tiene verbose en True se preguntara para añadir un agente indicando el nombre, si el nombre es conocido se le asignara ese comportamiento
        if verbose:
            new_behaviour = input("Introduce el comportamiento del agente ").lower().capitalize()
            player.setBehaviour(new_behaviour)
        else:
            # Si no añade a la simulacion un agente Explorer, Chaser, Farmer o Random de manera aleatoria
            list_behaviours = POSSIBLE_BEHAVIOURS + ["Random"]
            behaviour = self.random.choice(list_behaviours)
            if behaviour == "Random":
                player.setBehaviour(behaviour+str(next_id), random_flag=True)
            else:
                player.setBehaviour(behaviour)
        try:
            chosen_color = self.list_agents_colors.pop(self.random.randrange(0, len(self.list_agents_colors)))
            player.setAgentColor(chosen_color)
        except:
            chosen_color = "#" + "".join([self.random.choice("0123456789ABCDEF") for j in range(6)])
            player.setAgentColor(chosen_color)
        self.list_agents.append(player)
        self.grid.place_agent(player, pos)
        self.schedule.add(player)

    # El step representa cada turno del juego
    def step(self):
        self.step_count += 1
        chosen_action = ""
        for agent in self.list_agents:
            # Si el valor aletorio es menor que EPSILON (0.02) realizará una accion aleatoria, esto permite que no todos los agentes tengan el mismo comportamiento
            if self.random.uniform(0, 1) < EPSILON:
                action = "Random"
                # El agente cogera un valor de la lista de posibles acciones del modelo. [0] es porque devolvera una lista y necesito el elemento
                chosen_action = self.random.choices(POSSIBLE_ACTIONS)[0]
            else:
                # Elijo la primera accion posible de su lista de prioridades
                action = agent.selectAction()
                # Establezco la accion a realizar por el agente
                chosen_action = self.chooseAction(agent,action)
            print(f"agent: {agent.getId()} elige el movimiento {action, chosen_action}")
            agent.step(chosen_action)
        for planet in self.list_planets:
            planet.step()
        # Al final de cada turno compruebo que agentes tienen planetas para asignarles sus puntos correspondientes 
        self.addStellarPoints()

# Cada 100 turnos se revisa el número de stellar points que han ganado los agentes y el primero que es infrerior a 0 se elimina y se crea uno nuevo
        if self.step_count % 100 == 0:
            # Elimino al agente mas antiguo con balance negativo
            self.maybeRemoveAgent()
            self.addAgent()

        # En el turno 20 se introducirá los agentes que se quieran llevar a experimento
        if self.step_count == 20:
            self.addAgent(verbose=True)

        self.datacollector.collect(self)

    # Método para comprobar rápidamente el funcionamiento del juego sin tener que ejecutar el servidor
    def run_model(self):
        done = False
        i = 1 
        while not done:
            print(f"step {i}")
            self.step()
            for agent in self.schedule.agents:
                if type(agent) == Player:
                    if agent.getStellarPoints() >= 25000:
                        done = True
            i += 1
            print("--------------------")
        if done: 
            print("Final de la ejecución")
            for agent in self.schedule.agents:
                if type(agent) == Player:
                    print(f"-> Player con id : {agent.getId()} en la pos {agent.getAgentPos(verbose=True)} comportandose como {agent.getBehaviour()} {agent.getListPriorities()}")
                    print(f"\tResources: {agent.getAgentInfo(verbose=True)}")
            print("--------------------")

    def getAllAgentsInfo(self):
        players_dict = {}
        planet_dict = {}
        for agent in self.schedule.agents:
            if type(agent) == Player:
                players_dict[agent.getId()] = [agent.getAgentInfo(), agent.getBattlesWon(), agent.getAgentUpgrades().getUpgrades(), agent.getBehaviour(), agent.getListPriorities()]
            elif type(agent) == Planet:
                if not agent.getPlayer():
                    planet_agent = "None"
                else:
                    planet_agent = "Planeta conquistado por el agente: " + str(agent.getPlayer().getId())
                planet_dict[agent.getPlanetId()] = [agent.getPlanetPos(), agent.getPlanetTech(), agent.getPlanetGold(), planet_agent]

        return players_dict, planet_dict
    
    def getListPlayers(self):
        return self.list_agents

if __name__ == "__main__":
    for i in range(0,10):
        model = Game()
        model.run_model()
        players, planets = model.getAllAgentsInfo()
        dir_name = os.getcwd()
        path = os.path.join(dir_name, "saves")
        # Trato de crear el directorio para las saves
        try: 
            os.mkdir(path)
        except:
            # Si el directorio ya existe no hago nada 
            pass
        file_name = f"run_{i}.txt"
        path = os.path.join(dir_name, "saves", file_name)
        with open(path, "w+", encoding="utf-8") as my_file:
            my_file.write(f"Ejecución terminada en {model.step_count} steps \n")
            my_file.write("Los jugadores son: \n")
            for k, v in players.items():
                my_file.write(f"Agent id {k} {v}\n")    
            my_file.write("Los planetas son: \n")
            for k, v in planets.items():
                my_file.write(f"Planet id {k} {v}\n")

            