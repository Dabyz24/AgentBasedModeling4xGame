import mesa
from weapons import Weapon
from upgrades import Upgrades
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
        # Modificaciones de las mejoras
        self.upgrade_options = self.agent_upgrades.getListUpgrades()
        self.damage_increase = 0
        self.movement_radius = 1
        self.increase_factories_resources = 1

    # Funciones para modificar los planetas del agente 
    def addPlanetResources(self, tech, gold, populated=False):
        self.tech += tech
        self.gold += gold
        if not populated:
            self.num_planets += 1
    
    def removePlanet(self):
        self.num_planets -= 1 

    # Funciones para modificar las fabricas del agente 
    def createFactory(self):
        self.num_factories += 1

    def addFactoryResources(self):
        self.tech += TECH_FROM_FACTORIES * self.num_factories * self.increase_factories_resources
        self.gold += GOLD_FROM_FACTORIES * self.num_factories * self.increase_factories_resources

    # Funciones para gestionar las luchas entre agentes y las recompensas de los mismos 
    def addBattleResources(self, enemy):
        enemy_tech = round(enemy.getTech() * TECH_BATTLES_PERCENTAGE)
        enemy_gold = round(enemy.getGold() * GOLD_BATTLES_PERCENTAGE)
        self.tech += enemy_tech
        self.gold += enemy_gold
        enemy.takeAgentResources(enemy_tech, enemy_gold)

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
                    else:
                        #print(f"Punto ganado por {player_selected.getId()}")
                        player_selected.addPoint()
                        player_selected.addBattleWon()
                        player_selected.addBattleResources(self)
                            
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

    def payTaxes(self, taxes=20):
        self.gold -= taxes * self.num_planets

    # Funciones para añadir puntos estelares y para añadir batallas ganadas
    def addPoint(self, point_factory=False, point_planet=False):
        if point_factory:
            self.win_factory_point = True
        if point_planet:
            self.win_planet_point = True
        self.stellar_points += 1

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

    def getGold(self):
        return self.gold

    def getPlanets(self):
        return self.num_planets

    def getFactories(self):
        return self.num_factories

    def getPlayerWeapon(self):
        return self.player_weapon.getWeapon()
    
    def getBattlesWon(self):
        return self.battles_won
    
    def getAgentColor(self):
        return self.color
    
    def setAgentColor(self, new_color):
        self.color = new_color

    def getDamageIncrease(self):
        return self.damage_increase

    def increaseDamage(self):
        self.damage_increase = 5

    def doubleMovementRadius(self):
        self.movement_radius = 2
    
    def doubleFactoriesResources(self):
        self.increase_factories_resources = 2

    def getAgentUpgrades(self):
        return self.agent_upgrades
    
    def getStellarPoints(self):
        return self.stellar_points
    
    def getResources(self):
        return {"Tech": self.tech, "Gold": self.gold, "Planets": self.num_planets, "Factories": self.num_factories}

    def getAgentInfo(self, verbose=False):
        if verbose:
            return "T: " + str(self.tech) + " G: " + str(self.gold) + " P: " +str(self.num_planets) + " F: "+str(self.num_factories) + " <strong>Stellar Points: " + str(self.stellar_points)+"</strong>"
        return [self.tech, self.gold, self.num_planets, self.num_factories, self.player_weapon, self.stellar_points]
    
    def do_move(self, action):
        next_moves = self.model.grid.get_neighborhood(self.pos, self.moore, include_center=False, radius=self.movement_radius)
        next_move = next_moves[action]                 
        self.model.grid.move_agent(self, next_move)

    def do_action(self, choose_action):
        
        if choose_action >= 0 and choose_action <= 7:
            # Determinara si ya ha creado una nave espacial para moverse antes o no 
            if self.move:
                self.do_move(choose_action)
            elif self.enoughResources(SPACE_SHIP_TECH_COST, SPACE_SHIP_GOLD_COST): 
                self.do_move(choose_action)
                self.move = True

        if choose_action == 8 and self.enoughResources(FACTORIES_TECH_COST, FACTORIES_GOLD_COST):
            self.createFactory()
        
        if choose_action == 9 and self.enoughResources(WEAPON_TECH_COST, WEAPON_GOLD_COST):
            # las tres primeras veces que se ejecute solo se mejorara el arma
            if self.player_weapon.getNumUpgrades() < 3:
                self.player_weapon.upgradeWeapon()
            # Comprobar si el agente tiene mas mejoras disponibles
            elif self.agent_upgrades.isUpgradeAvailable():
                if len(self.upgrade_options) == 1:
                    random_choice = 0
                else:
                    random_choice = self.random.randint(0,len(self.upgrade_options)-1)
                choose_upgrade = self.upgrade_options[random_choice]
                if choose_upgrade == "Damage" and self.enoughResources(UPGRADE_DAMAGE_TECH_COST, UPGRADE_DAMAGE_GOLD_COST):
                    self.agent_upgrades.upgradeDamage()
                    self.increaseDamage()               
                elif choose_upgrade == "Factory" and self.enoughResources(UPGRADE_FACTORIES_TECH_COST, UPGRADE_FACTORIES_GOLD_COST):
                    self.agent_upgrades.upgradeFactories()
                    self.doubleFactoriesResources()

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
    def getPlanetId(self):
        return f"P {self.unique_id}"
    
    def getPlanetPos(self):
        return f"X: {self.pos[0]} Y:{self.pos[1]}"
    
    def getPlanetTech(self):
        return self.tech

    def getPlanetGold(self):
        return self.gold
    
    def getResources(self):
        return f"Tech: {self.tech} Gold: {self.gold}" 
    
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
                player_selected.addPlanetResources(self.tech, self.gold)
        # Si el jugador elegido para controlar el planeta se queda sin dinero se borrara el planeta al jugador y el propio jugador del planeta pasando a no estar habitado
        elif self.player.getGold() <= 0:
            self.player.removePlanet()
            self.player = None
            self.populated = False
        else:
            self.player.addPlanetResources(1, 10, True)
        

