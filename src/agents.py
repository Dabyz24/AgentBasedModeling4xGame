import mesa
from weapons import Weapon

INITIAL_PLAYER_GOLD = 100
INITIAL_PLAYER_TECH = 30
GOLD_FROM_FACTORIES = 5
TECH_FROM_FACTORIES = 1


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
        # Permite saber si se ha creado una nave para permitir moverse o no, inicialmente será False
        self.move = False

    # Funciones para modificar los planetas del agente 
    def addPlanetResources(self, tech, gold, populated=False):
        self.tech += tech
        self.gold += gold
        if not populated:
            self.num_planets += 1
    
    def removePlantet(self):
        self.num_planets -= 1 

    # Funciones para modificar las fabricas del agente 
    def createFactory(self):
        self.num_factories += 1

    def addFactoryResources(self):
        self.tech += TECH_FROM_FACTORIES * self.num_factories
        self.gold += GOLD_FROM_FACTORIES * self.num_factories

    # Funciones para modificar las armas del agente
 
    def maybeFight(self):
    # Si hay algún jugador presente lucharé contra el 
        neighbors = self.model.grid.get_neighbors(self.pos, self.moore)
        # Añado a la lista solo los vecinos que sean del tipo player
        list_players = [obj for obj in neighbors if isinstance(obj, Player)]
        if len(list_players) > 0:
            print("Luchando")
            player_selected = self.random.choice(list_players)
            enemy_weapon = player_selected.getPlayerWeapon()
            if enemy_weapon == "None":
                print(f"El gandor es el jugador {self.unique_id}")
                self.addPoint()
            else:
                player_value = self.getPlayerWeapon()[1] * self.random.randint(1,20)
                enemy_value = enemy_weapon[1] * self.random.randint(1,20)
                print(player_value, enemy_value)
                if player_value != enemy_value:
                    winner = max(player_value, enemy_value)
                    if winner == player_value:
                        print(f"Punto ganado por {self.unique_id}")
                        self.addPoint()
                        self.addBattleWon()
                    else:
                        print(f"Punto ganado por {player_selected.getId()}")
                        player_selected.addPoint()
                        player_selected.addBattleWon()
                            
    # Funciones para comprobar y restar los recursos de los jugadores
    def enoughResources(self, tech, gold):
        if self.gold >= gold and self.tech >= tech:
            self.tech -= tech
            self.gold -= gold
            return True
        return False
             
    def payTaxes(self, taxes=20):
        self.gold -= taxes * self.num_planets

    # Funciones para añadir puntos estelares y para añadir batallas ganadas
    def addPoint(self):
        self.stellar_points += 1

    def addBattleWon(self):
        self.battles_won += 1

    # Getters y setters de los atributos principales del jugador
    def getId(self):
        return str(self.unique_id)

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

    def getResources(self):
        return {"Tech": self.tech, "Gold": self.gold, "Planets": self.num_planets, "Factories": self.num_factories}

    def getAgentInfo(self):
        return "T: " + str(self.tech) + " G: " + str(self.gold) + " P: " +str(self.num_planets) + " F: "+str(self.num_factories) + " Stellar Points: " + str(self.stellar_points)

    # Funcion para representar cada turno del jugador
    def step(self):
        """
        El step representará cada turno del juego. Podrá decidir si moverse, construir o atacar 
        """
        # Tengo que comprobar si ha fabricado la nave para poder moverse
        if self.move:
            next_moves = self.model.grid.get_neighborhood(self.pos, self.moore, include_center=False)
            next_move = self.random.choice(next_moves)                    
            self.model.grid.move_agent(self, next_move)
            options = ["Factory", "Weapon"]
            probabilities = [self.model.prob_factory, self.model.prob_weapon]
            choose_action = self.random.choices(options, weights=probabilities, k=1)[0]
        # Si no ha fabricado la nave tengo que darle las tres opciones
        else:
            options = ["Factory", "Space_ship", "Weapon"]
            probabilities = [self.model.prob_factory, self.model.prob_space_ship, self.model.prob_weapon]
            choose_action = self.random.choices(options, weights=probabilities, k=1)[0]

        if choose_action == "Factory" and self.enoughResources(5, 30):
            self.createFactory()
            
        if choose_action == "Space_ship":
            # Determinara si ya ha creado una nave espacial para moverse antes o no 
            if self.enoughResources(5, 10): 
                next_moves = self.model.grid.get_neighborhood(self.pos, self.moore, include_center=False)
                next_move = self.random.choice(next_moves)                    
                self.model.grid.move_agent(self, next_move)
                self.move = True

        if choose_action == "Weapon" and self.enoughResources(20, 40):
            # las tres primeras veces que se ejecute solo se mejorara el arma
            if self.player_weapon.getNumUpgrades() < 3:
                print("Arma creada")
                self.player_weapon.upgradeWeapon()
            #else:
                # Aumentar el numero de armas para que aumente su probabilidad de sacar un numero mas grande
                

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
            self.player.removePlantet()
            self.player = None
            self.populated = False
        else:
            self.player.addPlanetResources(1, 10, True)
        

