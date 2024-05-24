import re
import os
import mesa 
import math

from agents import Player, Planet
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
        self.schedule = mesa.time.RandomActivationByType(self)
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
                            self.random.randrange(0, self.gold_planet), self.taxes_planet, moore=MOORE_PLANET)
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
        return minimum_tuple, chosen_move

    # Método para obtener contexto del entorno y saber quien es el agente que más puntos tiene, el que peor arma tiene, el que mas planetas tiene y el que mas oro tiene
    def getContext(self):
        points_winner = float("-inf")
        worst_weapon = float("inf")
        most_planets = 0 
        most_resources = 0
        points_winner_agent: Player = None
        worst_weapon_agent: Player = None
        agent_more_planets: Player = None
        most_resources_agent: Player = None
        # Recorro la lista de todos los agentes para poder guardar los agentes destacados
        for agent in self.list_agents:
            if agent.getStellarPoints() > points_winner:
                points_winner = agent.getStellarPoints()
                points_winner_agent = agent
            try:
                if agent.getPlayerWeapon()[1] < worst_weapon:
                    worst_weapon = agent.getPlayerWeapon()[1]
                    worst_weapon_agent = agent
            except:
                # Si entra en el except es porque no tiene ningun arma y está comparando un float con el string None, por lo que es el agente con peor arma
                worst_weapon = agent.getPlayerWeapon()[1]
                worst_weapon_agent = agent
            if agent.getPlanets() > most_planets:
                most_planets = agent.getPlanets()
                agent_more_planets = agent
            if agent.getGold() > most_resources:
                most_resources = agent.getGold()
                most_resources_agent = agent

        return points_winner_agent, worst_weapon_agent, agent_more_planets, most_resources_agent

    def selectBestAction(self, agent: Player):
        # Coger información del entorno
        points_winner_agent, worst_weapon_agent, agent_more_planets, most_resources_agent = self.getContext()
        # print(f"Mas puntos: {points_winner_agent.getId()} Peor arma: {worst_weapon_agent.getId()}, Mas planetas: {agent_more_planets}, Mas recursos: {most_resources_agent.getId()}")
        # Necesita mejorar balance, para ello necesito ganar puntos estelares, que puede ser con una batalla o conquistando un planeta
        if agent.getPlayerWeapon()[0] != "N": 
            # perseguir al agente con peor arma worst_weapon_agent
            list_positions = [agent.getAgentPos(), worst_weapon_agent.getAgentPos()]
            try:
                _ , chosen_move = self.closestTarget(agent.getAgentPos(), list_positions)
                chosen_action = chosen_move
            except: 
                chosen_action = -1
        else:
            if agent.getGold() <= 0: 
                pass
        # Si el agente tiene una mejora de daño o mejor arma que alguno de la simulación ir a por el 
        # Si no buscar un planeta para conquistar
        # Si no tiene dinero para mantenerlo tiene que buscar como obtener dinero que puede ser con una pelea o esperando a que las fabricas produzcan recursos para poder tenr un arma 
        return chosen_action


    # El step representa cada turno del juego
    def step(self):
        self.step_count += 1
        chosen_action = ""
        for agent in self.list_agents:
            # Si el valor aletorio es menor que EPSILON (0.1) realizará una accion aleatoria, esto permite que no todos los agentes tengan el mismo comportamiento
            if self.random.uniform(0, 1) < EPSILON:
                print(f"Accion random para el agente {agent.getId()}")
                # El agente cogera un valor de la lista de posibles acciones del modelo. [0] es porque devolvera una lista y necesito el elemento
                chosen_action = self.random.choices(POSSIBLE_ACTIONS)[0]
                action = "Random"
            else:
                list_priorities, behaviour_moves, behaviour_upgrades = agent.getListPriorities()
                # Si el balance es negativo lo que tiene que hacer es dependiendo de sus recursos (arma, oro...) perseguir a un agente con peor arma o ir a por un planeta con recursos
                # Si no simplemente recorrerá su lista de prioridades y eligirá la acción que pueda hacer
                # if agent.getBalance() < 0:
                #     action = self.selectBestAction()
                # else:
                    # Recorre toda la lista de prioridades y comprueba si puede hacer la acción 
                action = agent.selectAction()
                if action == "Move":
                    if len(behaviour_moves) == 1:
                        if behaviour_moves[0] == "To_Planet":
                            list_directions = self.getAllPlanetPos()
                            # Si todos los planetas están ocupados, se moveran hacia un agente cercano para luchar y hacer que algun planeta se quede libre
                            if len(list_directions) == 0:
                                list_directions = self.getAllPlayersPos()
                        elif behaviour_moves[0] == "To_Player":
                            list_directions = self.getAllPlayersPos()
                        try:
                            _ , chosen_move = self.closestTarget(agent.getAgentPos(), list_directions)
                            chosen_action = chosen_move
                        except:
                            # Si no se puede mover donde el agente no realizará ninguna acción 
                            chosen_action = -1
                    else:
                        chosen_action = self.random.choices(POSSIBLE_ACTIONS[0:8])[0]

                elif action[0] == "Upgrade":
                    if action[1] == "Factory":
                            agent.setChosenUpgrade("Factory")
                            chosen_action = ACTION_SPACE.get("Upgrade")
                    
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
            # # Tengo que pensar alguna forma para poder moverme y que no se tiren quietos todo el rato, porque es muy poco dinámico y no hay casi exploración 
            # print(f"agent: {agent.getId()} elige el movimiento {action, chosen_action}")
            agent.step(chosen_action)
        for planet in self.list_planets:
            planet.step()
        # Al final de cada turno compruebo quien es el agente que mas planetas y fabricas tiene para asignarle los puntos estelares
        self.addStellarPoints()

# Cada X turnos se revisa el número de stellar points que han ganado los agentes y si es infrerior se eliminan y se crea uno nuevo
        if self.step_count % 100 == 0:
            
            for agent in self.list_agents:
                print(f"El agente {agent.getId()} tiene un balance de {agent.getBalance()}")
                if agent.getBalance() <= 0:
                    agent.resetPlayer()
                    self.list_agents.remove(agent)
                    self.grid.remove_agent(agent)
                    self.schedule.remove(agent)
                else:
                    agent.resetBalance()

            # Primer boceto para incluir agentes de manera dináminca
            location_found = False
            while not location_found:
                location = self.checkSpace(MOORE_PLAYER, 0)
                location_found = location[0]
            pos = location[1]
            next_id = self.next_id()
            player = Player(next_id, self, pos, moore=MOORE_PLAYER)
            player.setBehaviour("Random"+str(next_id), random_flag=True)
            try:
                chosen_color = self.list_agents_colors.pop(self.random.randrange(0, len(self.list_agents_colors)))
                player.setAgentColor(chosen_color)
            except:
                chosen_color = "#" + "".join([self.random.choice("0123456789ABCDEF") for j in range(6)])
                player.setAgentColor(chosen_color)
            self.list_agents.append(player)
            self.grid.place_agent(player, pos)
            self.schedule.add(player)
    # Por ahora no reseteare los planetas y los comportamientos en el turno 100 solo intertaré eliminar un agente y meter otro 
            # for agent in self.list_agents:
            #     # Resetear el damage increase para que el que sea chaser adquiera los 10 de daño y el anterior los pierda
            #     agent.resetDamegeIncrease()
            #     agent.changeBehaviour()
            #     # Si es chaser y tenia los 5 de daño (tiene la mejora de daño) se le añade 10
            #     if agent.getBehaviour() == "Chaser" and agent.getDamageIncrease() == 5:
            #         agent.setDamageIncrease(10)
            # for planet in self.list_planets:
            #     planet.resetPlanet()
        #     last_score = float("inf")
        #     for agent in self.list_agents:  
        #         if agent.getStellarPoints() < last_score:
        #             last_score = agent.getStellarPoints()
        #             agent.behaviour = "Farmer" 
                
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
                    if agent.getStellarPoints() >= 50000:
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
                players_dict[agent.getId()] = [agent.getAgentPos(), agent.getAgentInfo(), agent.getBattlesWon(), agent.getAgentUpgrades().getUpgrades(), agent.getBehaviour(), agent.getListPriorities()]
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
            my_file.write("Los jugadores son: \n")
            for k, v in players.items():
                my_file.write(f"Agent id {k} {v}\n")    
            my_file.write("Los planetas son: \n")
            for k, v in planets.items():
                my_file.write(f"Planet id {k} {v}\n")

            