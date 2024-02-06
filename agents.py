import mesa

class Player(mesa.Agent):
    def __init__(self, unique_id, model, pos, tech=30, gold=100, num_planets=1 ,estelar_points=0, moore=True):
        """
        unique_id: Servira para identificar al agente por un id unico
        model: Se trata del modelo donde habitara el agente
        pos: Se trata de una tupla con los valores de la coordenada x e y del agente (x,y)
        tech: Valor de tecnología que tendrá el agente de manera inicial será 30
        gold: Valor de oro que tendrá el agente de manera inicial será 100
        num_planets: Número de planetas conquistados
        estelar_points: El valor más importante del juego, decidirá quien es el ganador
        moore: Si es True el agente podrá moverse en las 8 direcciones, si no solo podrá arriba, abajo, derecha e izquierda
        """
        super().__init__(unique_id, model)
        self.pos = pos
        self.tech = tech
        self.gold = gold
        self.num_planets = num_planets
        self.estelar_points = estelar_points
        self.moore = moore
    
    def addResources(self, tech, gold):
        self.tech += tech
        self.gold += gold
        self.num_planets += 1

    def getResources(self):
        return self.tech, self.gold
    
    def payTaxes(self, taxes=20):
        taxes = taxes * self.num_planets
        self.gold -= taxes

    def step(self):
        """
        El step representará cada turno del juego. Podrá decidir si moverse, construir o atacar 
        """
        # Tengo que comprobar si tiene alguna fabrica generada o alguna nave para poder moverse
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
        super.__init__(unique_id, model)
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
                player_selected.addResources(self.tech, self.gold)
        

