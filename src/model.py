import re
import mesa 
import math

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
        for i in range(self.num_players):
            location_found = False
            while not location_found:
                location = self.checkSpace(MOORE_PLAYER)
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
                location = self.checkSpace(MOORE_PLANET)
                location_found = location[0]
            pos = location[1]
            planet = Planet(i, self, pos ,self.random.randrange(0, self.tech_planet),
                            self.random.randrange(0, self.gold_planet), self.taxes_planet, moore=MOORE_PLANET)
            self.list_planets.append(planet)
            self.grid.place_agent(planet, pos)
            self.schedule.add(planet)
        self.running = True
        #self.datacollector.collect(self)

    # Método que comprueba que exista un espacio de dos casillas entre los jugadores y los planetas
    def checkSpace(self, moore):
        pos = (self.random.randrange(self.width), self.random.randrange(self.height))
        neighbors = self.grid.get_neighbors(pos, moore, include_center=True, radius=2)
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

    # El step representa cada turno del juego
    def step(self):
        self.step_count += 1
        for agent in self.list_agents:
            # Si el valor aletorio es menor que EPSILON (0.1) realizará una accion aleatoria, esto permite que no todos los agentes tengan el mismo comportamiento
            if self.random.uniform(0, 1) < EPSILON:
                # El agente cogera un valor de la lista de posibles acciones del modelo. [0] es porque devolvera una lista y necesito el elemento
                chosen_ation = self.random.choices(POSSIBLE_ACTIONS)[0]
            else:
                # Si es el primer turno interesa que se mnuevan para poder generar la nave con recursos para poder moverse aunque no tengan recursos
                if self.step_count == 1:
                    # En el primer turno elijo un movimiento aleatorio
                    chosen_ation = self.random.choices(POSSIBLE_ACTIONS[0:8])[0]
                elif agent.getGold() < FACTORIES_GOLD_COST:
                    # Si tiene arma perseguir a algún jugador para luchar y poder ganar recursos del combate
                    if agent.getGold() < 0:
                        try:
                            list_enemies = self.getAllPlayersPos()
                            _ , chosen_move = self.closestTarget(agent.getAgentPos(), list_enemies)
                            chosen_ation = chosen_move
                        except:
                            chosen_ation = self.random.choices(POSSIBLE_ACTIONS)[0]
                                                
                    else:
                        # Buscar un planeta cercano para conquistarlo y poder ganar sus recursos
                        list_uninhabited_planets = self.getAllPlanetPos()
                        try:
                            _ , chosen_move = self.closestTarget(agent.getAgentPos(), list_uninhabited_planets)
                            chosen_ation = chosen_move
                        except:
                            chosen_ation = self.random.choices(POSSIBLE_ACTIONS)[0]
                # Si el agente tiene oro, tecnologia y fabricas sufcientes para subsistir, entonces crear armas o mejorar siempre que se pueda seguir creando nuevas armas y mejoras                    
                elif agent.getGold() > WEAPON_GOLD_COST and agent.getTech() > WEAPON_TECH_COST and agent.getFactories() > 6 and (agent.getNumPlayerWeapon() < 3 or agent.getAgentUpgrades().isUpgradeAvailable()):
                    # Si tengo todas las armas creadas puedo desarrollar las mejoras
                    if agent.getNumPlayerWeapon() == 3:
                    # Tengo que comprobar si puedo hacer mejoras de los recursos de fabricas o la mejora de daño
                        if agent.getAgentUpgrades().isUpgradeAvailable() and (agent.getGold() > UPGRADE_FACTORIES_GOLD_COST and agent.getTech() > UPGRADE_FACTORIES_TECH_COST):
                            # Seleccionar algun valor de la lista de opciones de mejoras y hacer las mejoras
                            chosen_ation = ACTION_SPACE.get("Weapon")
                        else:
                            # Si no tengo recursos sufciente realizo una accion aleatoria quitando la opción de desarrollar un arma/mejora
                            chosen_ation = self.random.choices(POSSIBLE_ACTIONS[0:9])[0]
                    else:
                        # Si todavia no tengo todas las armas las creo
                        chosen_ation = ACTION_SPACE.get("Weapon")     
                
                elif agent.getGold() >= FACTORIES_GOLD_COST and agent.getTech() >= FACTORIES_TECH_COST:
                    if not agent.getAgentUpgrades().isUpgradeAvailable():
                        # Si no tiene mejoras disponibles actuaran en funcion de su comportamiento 
                        if agent.getBehaviour() == "Chaser":
                            # Se pone a perseguir al enemigo más cercano para luchar con él
                            list_enemies = self.getAllPlayersPos()
                            try:
                                _ , chosen_move = self.closestTarget(agent.getAgentPos(), list_enemies)
                                chosen_ation = chosen_move
                            except:
                                # Si está en la misma posición que el enemigo la accion elegida será o un movimiento o crear una fabrica
                                chosen_ation = self.random.choices(POSSIBLE_ACTIONS[0:9])[0]
                            
                        elif agent.getBehaviour() == "Explorer":    
                        # Se pone a buscar planetas cercanos sin explorar
                            list_uninhabited_planets = self.getAllPlanetPos()
                            # Si la lista de planetas sin habitar es vacia el agente realizara un movmiento o creara una fabrica
                            if len(list_uninhabited_planets) == 0:
                                chosen_ation = self.random.choices(POSSIBLE_ACTIONS[0:9])[0]
                            else:
                                try:
                                    _ , chosen_move = self.closestTarget(agent.getAgentPos(), list_uninhabited_planets)
                                    chosen_ation = chosen_move
                                except:
                                    chosen_ation = self.random.choices(POSSIBLE_ACTIONS[0:9])[0]

                        elif agent.getBehaviour() == "Farmer":
                            # Creara una fabrica en los turnos pares y en los impares se movera
                            if self.step_count % 2 == 0:
                                chosen_ation = ACTION_SPACE.get("Factory")
                            else:
                                chosen_ation = self.random.choices(POSSIBLE_ACTIONS[0:8])[0]
                    else:
                        # Si tiene mejoras disponibles crea una fabrica para poder conseguir recursos y sobrevivir
                        chosen_ation = ACTION_SPACE.get("Factory")
                else:
                    chosen_ation = self.random.choices(POSSIBLE_ACTIONS[0:8])[0]
            # Tengo que pensar alguna forma para poder moverme y que no se tiren quietos todo el rato, porque es muy poco dinámico y no hay casi exploración 
            print(f"agent: {agent.getId()} elige el movimiento {chosen_ation}")
            agent.step(chosen_ation)
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
                location = self.checkSpace(MOORE_PLAYER)
                location_found = location[0]
            pos = location[1]
            player = Player(self.next_id(), self, pos, moore=MOORE_PLAYER)
            player.setBehaviour(self.random.choice(POSSIBLE_BEHAVIOURS))
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
                    print(f"Player {agent.getAgentPos(verbose=True)}")
                    print(f"Resources: {agent.getAgentInfo(verbose=True)}")
                    if agent.getStellarPoints() >= 1000:
                        done = True
            i += 1
            print("------")

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
                    
if __name__ == "__main__":
    model = Game()
    model.run_model()