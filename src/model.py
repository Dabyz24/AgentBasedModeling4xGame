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
        # Se moverán uno cada vez, es decir el primer turno se movera primero el agente 1 y el siguiente el agente 2 primero
        self.schedule = RandomActivationByTypeFiltered(self)
        # Creacion de la matriz Torus=True significa que si el agente se encuentra en la izquierda del todo y sigue a la izquierda aparecera en la derecha 
        self.grid = mesa.space.MultiGrid(self.width, self.height, torus=True)
        # Tener un control sobre el numero de turnos del modelo
        self.step_count = 0

        # Datos que queremos ver 
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
            self.list_agents.append(player)
            self.grid.place_agent(player, pos)
            self.schedule.add(player)
        
        # Creacion de los planetas 
        for i in range(self.num_planets):
            location_found = False
            while not location_found:
                # Quiero que la distancia entre planetas sea de al menos 3 en cada direccion, para que no aparezcan muy juntos
                location = self.checkSpace(MOORE_PLANET, custom_radius=2)
                location_found = location[0]
            pos = location[1]
            planet = Planet(i, self, pos ,self.random.randrange(0, self.tech_planet),
                            self.random.randrange(10, self.gold_planet), self.taxes_planet, moore=MOORE_PLANET)
            self.list_planets.append(planet)
            self.grid.place_agent(planet, pos)
            self.schedule.add(planet)
        self.running = True
        #self.datacollector.collect(self)
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
    
    # Método para añadir un punto estelar en funcion de si el agente tiene mas planetas o fabricas que el resto
    def addStellarPoints(self):
        dict_values = self.checkAgentsValues()
        #agent_more_factories = ""
        # agent_more_planets = ""
        #initial_factories = 0
        # initial_planets = 0
        # check_factories_list = []
        # check_planets_list = []
        for player, resources in dict_values.items():
            # Comparar los valores de num fabricas y num de planetas y ver cual es el mas alto 
            for key, value in resources.items():
                if key == "Planets":
                    if value > 0: 
                        player.addPoint(value)
                
                # Si el valor de los planetas es mayor al numero inicial se guarda el jugador y se guarda el valor en la lista
                    # if initial_planets < value:
                        # agent_more_planets = player
                        # initial_planets = value
                        # check_planets_list = [value]
                    # Si otro agente tiene el mismo valor se guarda en la lista 
                    # elif initial_planets == value:
                        # check_planets_list.append(value)
                # if key == "Factories":
                #     if initial_factories < value:
                #         agent_more_factories = player
                #         initial_factories = value
                #         check_factories_list = [value]
                #     elif initial_factories == value:
                #         check_factories_list.append(value) 
        # Si solo hay un valor significa que es el que mas planetas tiene por lo que se le recompensará con un punto estelar
        # if len(check_planets_list) == 1:
            #print(f"El agente con más planetas es {agent_more_planets.getId()}")
            # agent_more_planets.addPoint()
        # El mismo funcionamiento con el numero de fabricas
        # if len(check_factories_list) == 1:
            #print(f"El agente con más fabricas es {agent_more_factories.getId()}")
            # agent_more_factories.addPoint()

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

    # Método para obtener contexto del entorno y saber quien es el agente que más puntos tiene, el que peor arma tiene, el que mas planetas tiene y el que mas oro tiene
    # def getContext(self, player):
    #     points_winner = float("-inf")
    #     worst_weapon = float("inf")
    #     most_planets = 0 
    #     most_resources = 0
    #     # most_gold = 0
    #     points_winner_agent: Player = None
    #     worst_weapon_agent: Player = None
    #     agent_more_planets: Player = None
    #     most_resources_agent: Player = None
    #     # most_resources_planet: Planet = None
    #     # Recorro la lista de todos los agentes restantes para poder guardar los agentes destacados
    #     for agent in self.list_agents:
    #         if agent == player:
    #             continue
    #         if agent.getStellarPoints() > points_winner:
    #             points_winner = agent.getStellarPoints()
    #             points_winner_agent = agent
    #         try:
    #             if agent.getPlayerWeapon()[1] < worst_weapon:
    #                 worst_weapon = agent.getPlayerWeapon()[1]
    #                 worst_weapon_agent = agent
    #         except:
    #             # Si entra en el except es porque no tiene ningun arma y está comparando un float con el string None, por lo que es el agente con peor arma
    #             worst_weapon = agent.getPlayerWeapon()[1]
    #             worst_weapon_agent = agent
    #         if agent.getPlanets() > most_planets:
    #             most_planets = agent.getPlanets()
    #             agent_more_planets = agent
    #         if agent.getGold() > most_resources:
    #             most_resources = agent.getGold()
    #             most_resources_agent = agent

    #     # for planet in self.list_planets:
    #     #     if planet.getPlanetGold() > most_gold:
    #     #         most_gold = planet.getPlanetGold()
    #     #         most_resources_planet = planet

    #     return points_winner_agent, worst_weapon_agent, agent_more_planets, most_resources_agent
    

    # def selectBestAction(self, agent: Player):
    #     # Coger información del entorno para ese agente
    #     points_winner_agent, worst_weapon_agent, agent_more_planets, most_resources_agent = self.getContext(agent)
    #     # print(f"Mas puntos: {points_winner_agent.getId()} Peor arma: {worst_weapon_agent.getId()}, Mas planetas: {agent_more_planets}, Mas recursos: {most_resources_agent.getId()}")
    #     # Necesita mejorar balance, para ello necesito ganar puntos estelares, que puede ser con una batalla o conquistando un planeta
    #    # Si el agente tiene un arma entonces perseguirá al agente que peor arma tenga para poder luchar contra el o al agente mas rico para ganar mayor cantidad de dinero
    #     chosen_action = -1
    #     if agent.getNumPlayerWeapon() != 0: 
    #         if agent.getNumPlayerWeapon() >= worst_weapon_agent.getNumPlayerWeapon():
    #             # perseguir al agente con peor arma worst_weapon_agent
    #             list_positions = [worst_weapon_agent.getAgentPos()]
    #             chosen_action = self._moveToTarget(agent, list_positions)
    #         else:
    #             # Si todos los agentes tiene un arma mejor que el agente entonces intentará mejorar su arma 
    #             if agent.getGold() > WEAPON_GOLD_COST and agent.getTech() > WEAPON_TECH_COST and agent.getNumPlayerWeapon() < MAX_NUM_WEAPONS:
    #                 chosen_action = ACTION_SPACE.get("Weapon")
    #             # Si ya no se puede mejorar mas el arma tendré que buscar al agente con mas planetas para quitarle planetas
    #             else:
    #                 # Si hay un agente con un planeta o mas ire a por el 
    #                 if agent_more_planets is not None:
    #                     list_positions = [agent_more_planets.getAgentPos()]
    #                     chosen_action = self._moveToTarget(agent, list_positions)
    #                 # Si no hay ningun jugador con un planeta ire a por el planeta para conquistarlo
    #                 else:
    #                     list_positions = self.getAllPlanetPos()
    #                     chosen_action = self._moveToTarget(agent, list_positions)
    #     else:
    #         list_positions = self.getAllPlanetPos()
    #         chosen_action = self._moveToTarget(agent, list_positions)
    #     # Si el agente tiene una mejora de daño o mejor arma que alguno de la simulación ir a por el 
    #     # Si no buscar un planeta para conquistar
    #     # Si no tiene dinero para mantenerlo tiene que buscar como obtener dinero que puede ser con una pelea o esperando a que las fabricas produzcan recursos para poder tenr un arma 
    #     return chosen_action

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
        if verbose:
            new_behaviour = input("Introduce el comportamiento del agente ")
            player.setBehaviour(new_behaviour)
        else:
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
                # El agente cogera un valor de la lista de posibles acciones del modelo. [0] es porque devolvera una lista y necesito el elemento
                action = "Random"
                chosen_action = self.random.choices(POSSIBLE_ACTIONS)[0]
            else:
                # Si el balance es negativo lo que tiene que hacer es dependiendo de sus recursos (arma, oro...) perseguir a un agente con peor arma o ir a por un planeta con recursos
                # Si no simplemente recorrerá su lista de prioridades y eligirá la acción que pueda hacer
                # if agent.getBalance() < 0:
                #     action = "Best_Action"
                #     chosen_action = self.selectBestAction(agent)
                # else:
                # Elijo la primera accion posible de su lista de prioridades
                action = agent.selectAction()
                # Establezco la accion a realizar por el agente
                chosen_action = self.chooseAction(agent,action)
            # # Tengo que pensar alguna forma para poder moverme y que no se tiren quietos todo el rato, porque es muy poco dinámico y no hay casi exploración 
            print(f"agent: {agent.getId()} elige el movimiento {action, chosen_action}")
            agent.step(chosen_action)
        for planet in self.list_planets:
            planet.step()
        # Al final de cada turno compruebo quien es el agente que mas planetas y fabricas tiene para asignarle los puntos estelares
        self.addStellarPoints()

# Cada X turnos se revisa el número de stellar points que han ganado los agentes y si es infrerior se eliminan y se crea uno nuevo
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
                planet_dict[agent.getPlanetId()] = [agent.getPlanetPos(), agent.getPlanetTech(), agent.getPlanetGold(), agent.getPlayer()]
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

            