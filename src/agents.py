import mesa
from weapons import Weapon
from upgrades import Upgrades
from behaviours import Behaviour, Explorer, Chaser, Farmer, CustomBehaviour
from global_constants import *

class Player(mesa.Agent):
    def __init__(self, unique_id, model, pos, tech=INITIAL_PLAYER_TECH, gold=INITIAL_PLAYER_GOLD, num_planets=0, num_factories=0 ,stellar_points=0, moore=True):
        """
        unique_id: Servira para identificar al agente por un id unico
        model: Se trata del modelo donde habitara el agente
        pos: Se trata de una tupla con los valores de la coordenada x e y del agente (x,y)
        tech: Valor de tecnología que tendrá el agente de manera inicial será 30
        gold: Valor de oro que tendrá el agente de manera inicial será 100
        num_planets: Número de planetas conquistados
        num_factories: Número de fabricas que ha creado cada agente
        stellar_points: El valor más importante del juego, decidirá quien es el ganador
        moore: Si es True el agente podrá moverse en las 8 direcciones, si no solo podrá arriba, abajo, derecha e izquierda
        """
        super().__init__(unique_id, model)
        self.pos = pos
        self.tech = tech
        self.gold = gold
        self.num_planets = num_planets
        self.num_factories = num_factories
        self.stellar_points = stellar_points
        self.moore = moore
        # Lista para tener controlados los planetas habitados por el agente
        self.list_planets = []
        # El color del agente por defecto será negro, pero en la creacion en el modelo se le atribuira otro color
        self.color = "black"
        # Permite saber el arma actual del agente
        self.player_weapon = Weapon()
        self.battles_won = 0
        # Permite saber si he ganado punto en ese turno 
        self.win_factory_point = False
        self.win_planet_point = False
        # Permite saber si se ha creado una nave para permitir moverse o no, inicialmente será False
        self.move = False
        # Permite saber las mejoras que tienen 
        self.agent_upgrades = Upgrades()
        # Permite saber el tipo de comportamiento del agente
        self.behaviour = None
        # Modificaciones de las mejoras
        self.chosen_upgrade = ""
        self.damage_increase = 0
        self.movement_radius = 1
        self.increase_factories_resources = 1
        # Para saber cuantos puntos pierde o gana en el total de rondas que especifique en el modelo
        self.balance = 0

    # Funciones para modificar los planetas del agente 
    def addPlanetResources(self, tech, gold, populated=False, planet=None):
        self.tech += tech
        self.gold += gold
        if not populated and planet:
            self.num_planets += 1
            self.list_planets.append(planet)
    
    def removePlanet(self, planet):
        self.num_planets -= 1
        self.list_planets.remove(planet) 

    # Funciones para modificar las fabricas del agente 
    def createFactory(self):
        self.num_factories += 1

    def addFactoryResources(self):
        self.tech += TECH_FROM_FACTORIES * self.num_factories * self.increase_factories_resources
        self.gold += GOLD_FROM_FACTORIES * self.num_factories * self.increase_factories_resources

    # Funciones para gestionar las luchas entre agentes y las recompensas de los mismos 
    def addBattleResources(self, enemy):
        if enemy.getGold() > 0:
            enemy_tech = round(enemy.getTech() * TECH_BATTLES_PERCENTAGE)
            enemy_gold = round(enemy.getGold() * GOLD_BATTLES_PERCENTAGE)
            self.tech += enemy_tech
            self.gold += enemy_gold
            enemy.takeAgentResources(enemy_tech, enemy_gold)
        else:
            self.tech += TECH_FROM_POOR_ENEMIES
            self.gold += GOLD_FROM_POOR_ENEMIES

    def maybeFight(self):
    # Si hay algún jugador presente lucharé contra el 
        neighbors = self.model.grid.get_neighbors(self.pos, self.moore)
        # Añado a la lista solo los vecinos que sean del tipo player
        list_players = [obj for obj in neighbors if isinstance(obj, Player)]
        if len(list_players) > 0:
            #print("Luchando")
            player_selected = self.random.choice(list_players)
            enemy_weapon = player_selected.getPlayerWeapon()
            if enemy_weapon == "None":
                #print(f"El ganador es el jugador {self.unique_id}")
                self.addPoint()
                self.addBattleWon()
                self.addBattleResources(player_selected)
                player_selected.lossPoint()
                if len(player_selected.list_planets) >= 1:
                    planet_selected = self.random.choice(player_selected.list_planets)
                    planet_selected.resetPlanet()
            else:
                player_value = self.getPlayerWeapon()[1] * self.random.randint(1,20) + self.damage_increase
                enemy_value = enemy_weapon[1] * self.random.randint(1,20) + player_selected.getDamageIncrease()
                #print(player_value, enemy_value)
                # Evita que los dos jugadores tengan el mismo resultado, si tienen el mimo no ocurrira nada
                if player_value != enemy_value:
                    winner = max(player_value, enemy_value)
                    if winner == player_value:
                        #print(f"Punto ganado por {self.unique_id}")
                        self.addPoint()
                        self.addBattleWon()
                        self.addBattleResources(player_selected)
                        player_selected.lossPoint()
                        if len(player_selected.list_planets) >= 1:
                            planet_selected = self.random.choice(player_selected.list_planets)
                            planet_selected.resetPlanet()
                    else:
                        #print(f"Punto ganado por {player_selected.getId()}")
                        player_selected.addPoint()
                        player_selected.addBattleWon()
                        player_selected.addBattleResources(self)
                        self.lossPoint()
                        if len(self.list_planets) >= 1:
                            planet_selected = self.random.choice(self.list_planets)
                            planet_selected.resetPlanet()
                            
    # Funciones para comprobar y restar los recursos de los jugadores
    def enoughResources(self, tech, gold):
        if self.gold >= gold and self.tech >= tech:
            self.tech -= tech
            self.gold -= gold
            return True
        return False
    
    def takeAgentResources(self, tech, gold):
        self.tech -= tech
        self.gold -= gold

    def payTaxes(self, taxes=TAXES_PLANET):
        self.gold -= taxes * self.num_planets

    # Funciones para añadir puntos estelares y para añadir batallas ganadas
    def addPoint(self, number_planets=0):
        if number_planets > 0:
            self.stellar_points += number_planets
            self.balance += number_planets
        else:
            self.stellar_points += 1
            self.balance += 1

    def lossPoint(self):
        self.stellar_points -= 1
        self.balance -= 1

    def addBattleWon(self):
        self.battles_won += 1

    # Getters y setters de los atributos principales del jugador
    def getId(self):
        return str(self.unique_id)
    
    def getAgentPos(self, verbose=False):
        if verbose:
            return f"X: {self.pos[0]} Y:{self.pos[1]}"
        return self.pos

    def getTech(self):
        return self.tech
    
    def setTech(self, new_value):
        self.tech = new_value

    def getGold(self):
        return self.gold
    
    def setGold(self, new_value):
        self.gold = new_value

    def getPlanets(self):
        return self.num_planets

    def getFactories(self):
        return self.num_factories

    def getPlayerWeapon(self):
        return self.player_weapon.getWeapon()
    
    def getNumPlayerWeapon(self):
        return self.player_weapon.getNumUpgrades()

    def getBattlesWon(self):
        return self.battles_won
    
    def isShipCreated(self):
        return self.move

    def getAgentColor(self):
        return self.color
    
    def setAgentColor(self, new_color):
        self.color = new_color

    def setChosenUpgrade(self, new_value):
        self.chosen_upgrade = new_value

    def getDamageIncrease(self):
        return self.damage_increase

    def setDamageIncrease(self, new_value):
        self.damage_increase = new_value

    def resetDamegeIncrease(self):
        if self.agent_upgrades.isDamageUpgraded():
            self.damage_increase = 5
        else:
            self.damage_increase = 0
    
    def increaseDamage(self):
        self.damage_increase = 15

    def doubleMovementRadius(self):
        self.movement_radius = 2
    
    def doubleFactoriesResources(self):
        self.increase_factories_resources = 2

    def getAgentUpgrades(self):
        return self.agent_upgrades
    
    def getStellarPoints(self):
        return self.stellar_points
    
    def getBehaviour(self):
        return self.behaviour.getActualBehaviour()

    def setBehaviour(self, new_behaviour, random_flag=False):
        # random_flag serivra para identificar si el nuevo comportamiento quiere que sea totalmente random
        if random_flag:
            self.behaviour = Behaviour()
            self.behaviour.setBehaviourName(new_behaviour)
        else:
            if new_behaviour in POSSIBLE_BEHAVIOURS:
                if new_behaviour == "Explorer":
                    self.behaviour = Explorer()
                elif new_behaviour == "Chaser":
                    self.behaviour = Chaser()
                elif new_behaviour == "Farmer":
                    self.behaviour = Farmer()
            else:
                self.behaviour = CustomBehaviour(new_behaviour)


    # Metodo para establecer los comportamientos de los agentes
    def setCustomBehaviour(self):
        name_behaviour = input("Choose a name for the behaviour: ").lower()
        name_behaviour = name_behaviour.capitalize()
        if name_behaviour not in POSSIBLE_BEHAVIOURS:
            is_random = input("Do you want a random behaviour?. (y/n): ").lower()
            if is_random == "y":
                self.setBehaviour(name_behaviour, random_flag=True)
            else:
                self.setBehaviour(name_behaviour)
        else:
            self.setBehaviour(name_behaviour)

    def getListPriorities(self):
        return self.behaviour.getPriorities()

    def getAgentPriority(self):
        return self.behaviour.getPriorities()[0]
    
    def getAgentMoveDirection(self):
        return self.behaviour.getPriorities()[1]
    
    def getAgentPossibleUpgrades(self):
        return self.behaviour.getPriorities()[2]
    
    def getStrBehaviour(self):
        return self.behaviour.getPrioritiesStr()

    def getBalance(self):
        return self.balance

    def resetBalance(self):
        self.balance = 0

    def getResources(self):
        return {"Tech": self.tech, "Gold": self.gold, "Planets": self.num_planets, "Factories": self.num_factories}

    def getAgentInfo(self, verbose=False):
        if verbose:
            return "T: " + str(self.tech) + " G: " + str(self.gold) + " P: " +str(self.num_planets) + " F: "+str(self.num_factories) + " <strong>Stellar Points: " + str(self.stellar_points)+"</strong>"
        return [self.pos, self.tech, self.gold, self.num_planets, self.num_factories, self.player_weapon, self.stellar_points]
    
    # Método para poder elegir la acción de la lista de prioridades de su comportamiento
    def selectAction(self):
        action = self.behaviour.act(self.gold, self.tech, self.num_factories, self.player_weapon, self.agent_upgrades, self.move)
        return action

    def do_move(self, action):
        next_moves = self.model.grid.get_neighborhood(self.pos, self.moore, include_center=False, radius=self.movement_radius)
        next_move = next_moves[action]                 
        self.model.grid.move_agent(self, next_move)

    def do_action(self, chosen_action):
        
        if chosen_action >= 0 and chosen_action <= 7:
            # Determinara si ya ha creado una nave espacial para moverse antes o no 
            if self.move:
                self.do_move(chosen_action)
            elif self.enoughResources(SPACE_SHIP_TECH_COST, SPACE_SHIP_GOLD_COST): 
                self.do_move(chosen_action)
                self.move = True

        if chosen_action == 8:
            price_increase = round(INCREASE_FACTOR ** self.getFactories())
            if self.enoughResources(FACTORIES_TECH_COST * price_increase, FACTORIES_GOLD_COST * price_increase):
                self.createFactory()
        
        # Comprobar si el agente tiene mas mejoras disponibles
        if chosen_action == 9 and self.agent_upgrades.isUpgradeAvailable():
            if self.chosen_upgrade == "":
                list_possible_upgrades = self.getAgentPossibleUpgrades()
                if len(list_possible_upgrades) == 0:
                    print(f"El agente {self.unique_id} no puede realizar upgrades porque no tiene ninguna en su comportamiento")
                elif len(list_possible_upgrades) == 1:
                    self.chosen_upgrade == list_possible_upgrades[0]
                else:
                    self.chosen_upgrade = self.random.choice(list_possible_upgrades)

            if self.chosen_upgrade == "Damage" and self.enoughResources(UPGRADE_DAMAGE_TECH_COST, UPGRADE_DAMAGE_GOLD_COST):
                self.agent_upgrades.upgradeDamage()
                self.increaseDamage()            
            elif self.chosen_upgrade == "Factory" and self.enoughResources(UPGRADE_FACTORIES_TECH_COST, UPGRADE_FACTORIES_GOLD_COST):
                self.agent_upgrades.upgradeFactories()
                self.doubleFactoriesResources()
                         
        if chosen_action == 10 and self.enoughResources(WEAPON_TECH_COST, WEAPON_GOLD_COST):
            # las tres primeras veces que se ejecute solo se mejorara el arma
            if self.player_weapon.getNumUpgrades() < 3:
                self.player_weapon.upgradeWeapon()


    # Funcion para representar cada turno del jugador
    def step(self, action):
        """
        El step representará cada turno del juego. Podrá decidir si moverse, construir o atacar 
        """

        self.do_action(action)
        
        if self.num_factories > 0:
            self.addFactoryResources()

        if self.getPlayerWeapon() != "None":
            self.maybeFight()
        self.payTaxes()

    def resetPlayer(self):
        for planet in self.list_planets:
            planet.resetPlanet()
        


class Planet(mesa.Agent):
    def __init__(self, unique_id, model, pos, tech, gold, taxes=20, populated=False, moore=True):
        """
        unique_id: Servira para identificar al agente por un id unico
        model: Se trata del modelo donde habitara el agente
        pos: Se trata de una tupla con los valores de la coordenada x e y del agente (x,y)
        tech: Valor de tecnología que tendrá el agente de manera inicial será 30
        gold: Valor de oro que tendrá el agente de manera inicial será 100
        populated: Bool que dirá si el planeta es habitado o no 
        taxes: Será el impuesto por cada planeta que se colonice
        moore: Si es True el agente podrá moverse en las 8 direcciones, si no solo podrá arriba, abajo, derecha e izquierda
        """
        super().__init__(unique_id, model)
        self.pos = pos
        self.tech = tech
        self.gold = gold
        self.taxes = taxes
        self.populated = populated
        self.moore = moore
        # Sirve para saber que agente es el dueño del planeta 
        self.player = None

    def isInhabit(self):
        # Dira si el planeta está habitado o no 
        return self.populated

    def getPlayer(self):
        # Devuelve el agente que habita el planeta 
        return self.player
    
    # Getters de los atributos básicos del planeta
    def getPlanetId(self, verbose=False):
        if verbose:
            return f"P {self.unique_id}"
        else:
            return self.unique_id
        
    def getPlanetPos(self, verbose=False):
        if verbose:
            return f"X: {self.pos[0]} Y:{self.pos[1]}"
        else:
            return self.pos
    
    def getPlanetTech(self):
        return self.tech

    def getPlanetGold(self):
        return self.gold
    
    def getResources(self):
        return f"Tech: {self.tech} Gold: {self.gold}" 
    
    def getPlanetInfo(self):
        return [self.pos, self.tech, self.gold, self.populated]

    def resetPlanet(self):
        if self.populated:
            self.player.removePlanet(self)
            self.player = None
            self.populated = False
    
    # Funcion para representar cada turno de los planetas
    def step(self):
        """
        El step representará cada turno del juego. Comprobará si es habitado o no, en caso positivo dará sus recursos al agente 
        """
        if not self.populated: 
            # Si hay algún jugador presente, pasará a ser quien habite el planeta, para ello compruebo los vecinos del planeta
            neighbors = self.model.grid.get_neighbors(self.pos, self.moore)
            # Añado a la lista solo los vecinos que sean del tipo player
            list_players = [obj for obj in neighbors if isinstance(obj, Player)]
            if len(list_players) > 0:
                player_selected = self.random.choice(list_players)
                self.populated = True
                # pasa a ser habitado por el agente seleccionado
                self.player = player_selected
                player_selected.addPlanetResources(self.tech, self.gold, False, self)
        # Si el jugador elegido para controlar el planeta se queda sin dinero se borrara el planeta al jugador y el propio jugador del planeta pasando a no estar habitado
        elif self.player.getGold() <= 0:
            self.resetPlanet()
        else:
            # Para solucionar un bug que salia cuando eliminaba un agente que tenia planetas, a veces no se resetaba bien.
            # Si el agente no esta en la lista de jugadores del modelo se resetea el planeta 
            if self.player not in self.model.list_agents:
                self.resetPlanet()
            else:
                self.player.addPlanetResources(1, 10, True)
        

