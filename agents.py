import mesa

INITIAL_PLAYER_GOLD = 100
INITIAL_PLAYER_TECH = 30
GOLD_FROM_FACTORIES = 20
TECH_FROM_FACTORIES = 5


class Player(mesa.Agent):
    def __init__(self, unique_id, model, pos, tech=INITIAL_PLAYER_TECH, gold=INITIAL_PLAYER_GOLD, num_planets=0, num_factories=0 ,estelar_points=0, moore=True):
        """
        unique_id: Servira para identificar al agente por un id unico
        model: Se trata del modelo donde habitara el agente
        pos: Se trata de una tupla con los valores de la coordenada x e y del agente (x,y)
        tech: Valor de tecnología que tendrá el agente de manera inicial será 30
        gold: Valor de oro que tendrá el agente de manera inicial será 100
        num_planets: Número de planetas conquistados
        num_factories: Número de fabricas que ha creado cada agente
        estelar_points: El valor más importante del juego, decidirá quien es el ganador
        moore: Si es True el agente podrá moverse en las 8 direcciones, si no solo podrá arriba, abajo, derecha e izquierda
        """
        super().__init__(unique_id, model)
        self.pos = pos
        self.tech = tech
        self.gold = gold
        self.num_planets = num_planets
        self.num_factories = num_factories
        self.estelar_points = estelar_points
        self.moore = moore
        # Permite saber si se ha creado una nave para permitir moverse o no, inicialmente será False
        self.move = False
    
    def addPlanetResources(self, tech, gold):
        self.tech += tech
        self.gold += gold
        self.num_planets += 1

    def getResources(self):
        return "Tech: " + str(self.tech) + " Gold: " + str(self.gold)
    
    def createFactory(self):
        self.num_factories += 1

    def addFactoryResources(self):
        self.tech += TECH_FROM_FACTORIES
        self.gold += GOLD_FROM_FACTORIES

    def enoughResources(self, tech, gold):
        if self.gold >= gold and self.tech >= tech:
            self.tech -= tech
            self.gold -= gold
            return True
        return False
             
    def payTaxes(self, taxes=20):
        taxes = taxes * self.num_planets
        self.gold -= taxes

    def step(self):
        """
        El step representará cada turno del juego. Podrá decidir si moverse, construir o atacar 
        """
        # Tengo que comprobar si tiene alguna fabrica generada o alguna nave para poder moverse
        options = ["Factory", "Space_ship", "Weapon"]
        probabilities = [self.model.prob_factory, self.model.prob_space_ship, self.model.prob_weapon]
        choose_action = self.random.choices(options, weights=probabilities, k=1)[0]

        if choose_action == "Factory" and self.enoughResources(5, 30):
            print("Fabrica creada")
            self.createFactory
            

        if choose_action == "Space_ship":
            print("Space_ship")
            # Determinara si ya ha creado una nave espacial para moverse antes o no 
            if self.move: 
                next_moves = self.model.grid.get_neighborhood(self.pos, self.moore, include_center=False)
                next_move = self.random.choice(next_moves)                    
                self.model.grid.move_agent(self, next_move)
            
            elif self.enoughResources(15, 20):
                self.move = True

        if choose_action == "Weapon" and self.enoughResources(20, 40):
            print("Arma creada")


        if self.num_factories > 0:
            self.addFactoryResources()
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

    def isInhabit(self):
        return self.populated

    def step(self):
        """
        El step representará cada turno del juego. Comprobará si es habitado o no, en caso positivo dará sus recursos al agente 
        """
        if not self.populated: 
            # Si hay algún jugador presente, pasará a ser quien habite el planeta, para ello compruebo los vecinos del planeta
            neighbors = self.model.grid.get_cell_list_contents([self.pos])
            # Añado a la lista solo los vecinos que sean del tipo player
            list_players = [obj for obj in neighbors if isinstance(obj, Player)]
            if len(list_players) > 0:
                player_selected = self.random.choice(list_players)
                self.populated = True
                # pasa a ser habitado por el agente seleccionado
                player_selected.addPlanetResources(self.tech, self.gold)
        

