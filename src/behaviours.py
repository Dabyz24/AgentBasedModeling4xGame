import random
import copy
from global_constants import *


class Behaviour():
    # Objeto encargado de generalizar todos los comportamientos y permitir la creacion de nuevos comportamientos de una manera sencilla
    
    def __init__(self):
        # Nombre del comportamiento
        self.actual_behaviour = ""
        # Diccionario con las acciones posibles y direccion de movimiento
        self.dict_actions = {"Move": {"To_Planet": False, "To_Player":False}, "Factory": 0, "Weapon": 0, "Upgrade": {"Damage": False, "Factory":False}}
        # Lista que servirá para tener las prioridades
        self.list_priorities = []
        # Sirve para determinar el objetivo de la dirección
        self.special_target = []
        # Sirve para determinar si el agente huira del objetivo o no 
        self.run_away = False

    # Metodo que recorre la lista de prioridades del agente y decide la acción que realizar en función de sus recursos
    def act(self, agent_gold, agent_tech, agent_factories, agent_weapon, agent_upgrades, is_ship_created):
        for action in self.list_priorities:
            if action == "Move":
                list_move_direction = self.getPriorities()[1]
                if (agent_gold >= SPACE_SHIP_GOLD_COST and agent_tech >= SPACE_SHIP_TECH_COST) or is_ship_created:
                    if len(list_move_direction) == 1:
                        # Si la lista de direccion tiene solo una devolvere la accion y la direccion 
                        return action, list_move_direction[0], self.special_target
                    else:
                        # Si la lista tiene mas de una direccion o ninguna devolvere la accion y "None"
                        return action, "None", self.special_target
                
            elif action == "Factory":
                price_increase = round(INCREASE_FACTOR ** agent_factories)
                if (agent_gold >= (FACTORIES_GOLD_COST * price_increase)  and agent_tech >= (FACTORIES_TECH_COST * price_increase)):
                    return action
            
            elif action == "Weapon":
                if agent_gold > WEAPON_GOLD_COST and agent_tech > WEAPON_TECH_COST and agent_weapon.getNumUpgrades() < MAX_NUM_WEAPONS:
                    return action
            
            elif action == "Upgrade":
                list_special_upgrade = self.getPriorities()[2]
                if agent_upgrades.isUpgradeAvailable() and len(list_special_upgrade) > 0:
                    if "Factory" in list_special_upgrade and not agent_upgrades.isFactoryUpgraded():
                        if (agent_gold > UPGRADE_FACTORIES_GOLD_COST and agent_tech > UPGRADE_FACTORIES_TECH_COST):
                            return action, "Factory"
                    
                    if "Damage" in list_special_upgrade and not agent_upgrades.isDamageUpgraded():
                        if (agent_gold > UPGRADE_DAMAGE_GOLD_COST and agent_tech > UPGRADE_DAMAGE_TECH_COST):
                            return action, "Damage"
        return "Wait"
    
    # Método para cambiar la lista de prioridades en función del entorno 
    # Hacer polimorfismo para cada comportamiento para poder cambiar los comportamientos en funcion de las necesidades
    def changeBehaviour(self, player, context_players, context_planets, dict_enemies):
        pass
    
    # Método que me permite especificar la dirección de movimiento de los agentes, para obligarles a ir a una dirección especifica 
    def addSpecialTarget(self, target):
        if len(self.special_target) == 1:
            self.special_target.pop(0)
        self.special_target.append(target)

    def getRunAway(self):
        return self.run_away

    # Método para presentar de una manera mas visual la lista de prioridades
    def getPrioritiesStr(self):
        aux_str = ""
        for i in range(0, len(self.list_priorities)):
            if i+1 == len(self.list_priorities):
                aux_str += self.list_priorities[i]
            else:
                aux_str += self.list_priorities[i] + " -> "    
        return aux_str
    
    def getPriorities(self):
        # Devuelve la lista de prioridades, la lista de direccion de movimiento y la lista de mejoras
        list_special_move = []
        list_special_upgrade = []
        for action in self.list_priorities:
            if action == "Move":
                dict_action = self.dict_actions[action]
                for key, value in dict_action.items():
                    if value:
                        list_special_move.append(key)
            elif action == "Upgrade":
                dict_action = self.dict_actions[action]
                for key, value in dict_action.items():
                    if value:
                        list_special_upgrade.append(key)
                
        return self.list_priorities, list_special_move, list_special_upgrade
  
    def resetBehaviour(self):
        self.dict_actions = {"Move": {"To_Planet": False, "To_Player":False}, "Factory": 0, "Weapon": 0, "Upgrade": {"Damage": False, "Factory":False}}
        self.list_priorities = []

    def getActualBehaviour(self):
        return self.actual_behaviour
    
    def setBehaviourName(self, new_name):
        self.actual_behaviour = new_name

    # Método para establecer de manera aleatoria la direccion del movimiento y el comportamiento
    def getRandomSpecialActions(self, action):
        for item in self.dict_actions[action]:
            coin = random.randint(0,1)
            if coin == 0:
                self.dict_actions[action][item] = False
            else:
                self.dict_actions[action][item] = True

    def _checkWorstWeaponAgent(self, context_players, player):
        worst_weapon = float("inf")
        for neighbor in context_players:
            try:
                if neighbor.getPlayerWeapon()[1] < worst_weapon:
                    worst_weapon = neighbor.getPlayerWeapon()[1]
                    worst_weapon_agent = neighbor
            except:
                # Si entra en el except es porque no tiene ningun arma y está comparando un float con el string None, por lo que es el agente con peor arma
                worst_weapon = 0
                worst_weapon_agent = neighbor
        return worst_weapon, worst_weapon_agent
    

class Explorer(Behaviour):

    def __init__(self):
        super().__init__()
        self.setBehaviourName(self.__class__.__name__)
        self.dict_actions["Move"]["To_Planet"] = True
        self.list_priorities = ["Move", "Factory", "Weapon", "Upgrade"]

    # El explorer evitará las peleas, será como una especie de pacifista que solo se centrará en conquistar planetas 
    def changeBehaviour(self, player, context_players, context_planets, dict_enemies):
        # Reseteo el comportamiento para que vuelva a decidir la acción que hacer
        self.resetBehaviour()
        # Si el agente tiene algún vecino, ya sea otro jugador o planeta intentará identificar la situación para cambiar su comportamiento 
        if len(context_players) > 0:
            # Si el vecino es un jugador el agente huira de el si tiene un arma 
            for enemie in context_players:
                if enemie.getNumPlayerWeapon() > 0:
                    self.run_away = True
                    self.addSpecialTarget(enemie.getAgentPos())
                    return
            # Si ninguno de los jugadores tiene un arma del que huir actuo normal 
            return 
        # Si no tiene vecinos jugadores solo habrá vecinos Planet 
        elif len(context_planets) > 0: 
            # Si es un planeta actuará como siempre
            return 
        else:
            # Si no tiene ningún vecino alrededor, priorizará la construcción de fabricas para poder subsistir
            self.list_priorities = ["Factory", "Move", "Weapon", "Upgrade"]
            return 
                        
    def resetBehaviour(self):
        self.run_away = False
        self.dict_actions = {"Move": {"To_Planet": True, "To_Player":False}, "Factory": 0, "Weapon": 0, "Upgrade": {"Damage": False, "Factory":False}}
        self.list_priorities = ["Move", "Factory", "Weapon", "Upgrade"]
        self.special_target = []

class Chaser(Behaviour):

    def __init__(self):
        super().__init__()
        self.setBehaviourName(self.__class__.__name__)
        self.dict_actions["Move"]["To_Player"] = True
        self.dict_actions["Upgrade"]["Damage"] = True
        self.list_priorities = ["Weapon", "Upgrade", "Move", "Factory"]

    def changeBehaviour(self, player, context_players, context_planets, dict_enemies):
        # Reseteo el comportamiento para que vuelva a decidir la acción que hacer
        self.resetBehaviour()
        # Si el agente tiene algún vecino, ya sea otro jugador o planeta intentará identificar la situación para cambiar su comportamiento 
        if len(context_players) > 0:
        # Si se encuentra con un vecino jugador comprueba si el agente tiene arma o no 
            if player.getNumPlayerWeapon() != 0:
                # Si el jugador tiene un arma puedo buscar el que peor arma tenga para decidir si luchar con el o no 
                worst_weapon, worst_weapon_agent = self._checkWorstWeaponAgent(context_players, player)
                # Si el jugador tiena la misma arma o peor que el que vecino con peor arma
                if player.getPlayerWeapon()[1] <= worst_weapon:
                    # Si tiene todas las armas mejoradas, tendrá que buscar a otro rival con peor arma, porque no le interesará luchar con alguien con el mismo arma
                    if player.getNumPlayerWeapon() == MAX_NUM_WEAPONS and not player.getAgentUpgrades().isDamageUpgraded():
                        self.addSpecialTarget(dict_enemies["Worst_Weapon"].getAgentPos())
                    else:
                        # Centrarse en hacer mejora, construir arma o obtener la mejora o generar fabricas 
                        self.list_priorities = ["Upgrade","Weapon","Factory","Move"]
                    return
                # Si tiene mejor arma que el simplemente le perseguira
                else:
                    # Haré que se mueva hacia el jugador con peor arma
                    self.addSpecialTarget(worst_weapon_agent.getAgentPos())
                # Si no tiene armas se centrará en crearlas, actuando normal
                return
        # Si solo tiene vecinos planetas
        elif len(context_planets) > 0:
            for planet in context_planets:
                if planet.getPlanetGold() >= 25:
                    # Si el planeta no está habitado y tiene mas de 25 de oro, el chaser irá hacía el 
                    self.list_priorities = ["Move", "Weapon", "Upgrade", "Factory"]
                    self.addSpecialTarget(planet.getPlanetPos())
                    return 
        # Si no tiene nada alrededor o solo tiene planetas actuará normal
        return 

    def resetBehaviour(self):
        self.run_away = False
        self.dict_actions = {"Move": {"To_Planet": False, "To_Player":True}, "Factory": 0, "Weapon": 0, "Upgrade": {"Damage": True, "Factory":False}}
        self.list_priorities = ["Weapon", "Upgrade", "Move", "Factory"]
        self.special_target = []

class Farmer(Behaviour):

    def __init__(self):
        super().__init__()
        self.setBehaviourName(self.__class__.__name__)
        self.dict_actions["Upgrade"]["Factory"] = True
        self.list_priorities = ["Factory", "Upgrade", "Weapon", "Move"]


    def changeBehaviour(self, player, context_players, context_planets, dict_enemies):
        # Reseteo el comportamiento para que vuelva a decidir la acción que hacer
        self.resetBehaviour()
        # Si se encuentra con un enemigo en su contexto
        if len(context_players) > 0:
            worst_weapon = float("inf")
            if player.getNumPlayerWeapon() != 0:
                # Si el jugador tiene un arma puedo buscar el que peor arma tenga para decidir si luchar con el o no 
                worst_weapon, worst_weapon_agent = self._checkWorstWeaponAgent(context_players, player)

                if player.getPlayerWeapon()[1] > worst_weapon:
                    # Perseguirá al rival con peor arma
                    self.list_priorities = ["Move", "Factory", "Upgrade", "Weapon"]
                    self.dict_actions["Move"]["To_Player"] = True
                    self.addSpecialTarget(worst_weapon_agent.getAgentPos())
                    return
                    
        # Si no hay rivales o tienen mejor arma que el jugador tendrá que buscar si hay algún planeta he intentar conquistarlo 
        if len(context_planets) > 0:
            # Si tiene peor arma o igual que el rival intentará ir hacía el planeta más cercano y si no tiene un enemigo también buscara el planeta más cercano
            self.list_priorities = ["Move", "Factory", "Upgrade", "Weapon"]
            # Buscaré el primer planeta y iré hacia el 
            self.dict_actions["Move"]["To_Planet"] = True
            self.addSpecialTarget(context_planets[0].getPlanetPos())
            return
        
        # Si no tiene nada alrededor actuará normal
        return 
            

    def resetBehaviour(self):
        self.run_away = False
        self.dict_actions = {"Move": {"To_Planet": False, "To_Player":False}, "Factory": 0, "Weapon": 0, "Upgrade": {"Damage": False, "Factory":True}}
        self.list_priorities = ["Factory", "Upgrade", "Weapon", "Move"]
        self.special_target = []

class CustomBehaviour(Behaviour):

    def __init__(self, behaviour_name):
        super().__init__()
        self.setBehaviourName(behaviour_name)
        # Servira para comprobar que al establecer una nueva prioridad se pongan los numeros correctos
        self._valid_numbers_priority = ["1","2","3","4"]
        self.setPriorities()
        self.copy_dict_actions = copy.deepcopy(self.dict_actions)
        self.copy_list_priorities = self.list_priorities.copy()

    def setPriorities(self):
        # Método para establecer de una manera personalizada la lista de prioridad, la direccion de movimiento y las mejoras disponibles 
        different_priorities = self.inputPriorities()
        str_special_moves = input("Type the letter if you want to chase an Agent (A) a Planet (P) or None (N). ").upper()
        if str_special_moves == "A":
            self.dict_actions["Move"]["To_Player"] = True
        elif str_special_moves == "P":
            self.dict_actions["Move"]["To_Planet"] = True
        else:
            print("The agent will do random moves")
        
        str_special_upgrades = input("Type the letter if you want to upgrade Damage (D) Factories (F) both (B) or None (N). ").upper()
        if str_special_upgrades == "D":
            self.dict_actions["Upgrade"]["Damage"] = True
        elif str_special_upgrades == "F":
            self.dict_actions["Upgrade"]["Factory"] = True
        elif str_special_upgrades == "B":
            self.dict_actions["Upgrade"]["Damage"] = True
            self.dict_actions["Upgrade"]["Factory"] = True
        else:
            print("No upgrades for your agent")
        # Se crea una lista para poder acceder de manera más simple a las claves del diccionario
        list_actions = list(self.dict_actions.keys())
        for priority in different_priorities:
            # Se resta uno en la priority para que coincida con el indice de dict_actions
            self.list_priorities.append(list_actions[int(priority)-1])

    def inputPriorities(self):
        # Mientras no cumpla la condicion para establecer la lista de prioridades se repetirá el input 
        while True:  
                str_priority = input("Select from highest to lowest priority (1 = Move, 2 = Factory, 3 = Weapon, 4 = Upgrade) using comma as separator. Ex: 1,2,3,4\n")
                different_priorities = str_priority.split(",")
                # Si todos los numeros introducidos estan dentro de la lista de numeros validos 
                if all(number in self._valid_numbers_priority for number in different_priorities) and len(set(different_priorities)) == len(self.dict_actions) == len(different_priorities):
                        return different_priorities
                else:
                    print(f"These are the only valid numbers: {self._valid_numbers_priority}")

    def setFirstPriorityAction(self, action):
        # Primero busco el indice de la accion
        index = self.list_priorities.index(action)
        # Si no es el primer elemento lo ordeno para que asi sea 
        if index != 0:
            self.list_priorities.pop(index)
            self.list_priorities.insert(0, action)
        # Si ya es el primero actuo normal
        return self.list_priorities

    # Pensar una manera de incorporar la mejor accion posible si se encuentra con un planeta con un agente o con ambos, si no se encuentra con nada actuar normal
    def changeBehaviour(self, player, context_players, context_planets, dict_enemies):
        self.resetBehaviour()
        # Si hay algún planeta en su entorno mirara sus recursos y en función de si puede mantener el planeta eligira conquistarlo o no 
        if len(context_planets) > 0:
            # taxes_to_pay hace referencia a los gastos que tendra el agente para poder compararlo con su oro y ver si es rentable o no 
            taxes_to_pay = TAXES_PLANET 
            if player.getPlanets() > 1: 
                # El +1 es para saber si puede mantener los planetas que tiene mas el que conquiste 
                taxes_to_pay = TAXES_PLANET * (player.getPlanets() + 1)  
            # Si tengo más oro que lo que tengo que pagar por taxes conquisto el planeta 
            if player.getGold() > taxes_to_pay:
                # Cambio su prioridad para conquistar el planeta
                self.list_priorities = self.setFirstPriorityAction("Move")
                self.dict_actions["Move"]["To_Planet"] = True 
                self.dict_actions["Move"]["To_Player"] = False
                return
            # Si no tiene suficiente oro intentara luchar con algun enemigo o construir fabricas

        # Si me encuentro con enemigos
        if len(context_players) > 0 and player.getNumPlayerWeapon() != 0:    
            # Comprobar si los vecinos tienen peor arma 
            worst_weapon, worst_weapon_agent = self._checkWorstWeaponAgent(context_players, player)
            # Si tiene peor arma que el que peor arma tiene no luchará 
            if player.getPlayerWeapon()[1] < worst_weapon:
                # Huir de ese agente 
                self.run_away = True
                self.addSpecialTarget(worst_weapon_agent.getAgentPos())
                self.setFirstPriorityAction("Move")
                return 
            # Si es mayor le perseguire
            elif player.getPlayerWeapon()[1] > worst_weapon:
                self.addSpecialTarget(worst_weapon_agent.getAgentPos())
                self.setFirstPriorityAction("Move")
                return
            
        # Si he llegado aqui es porque no tienen recursos para pagar las taxes de los planetas y los enemigos tienen armas iguales a la mia o no hay enemigos
        if len(context_planets) > 0:    
            # Si no tiene arma o rivales pongo como primer elemento de su prioridad construir fabricas
            self.list_priorities = self.setFirstPriorityAction("Factory")
        # Si no hay planetas actuo normal
        if len(context_players) > 0:
            self.list_priorities = self.setFirstPriorityAction("Weapon")
        return 
    

    def resetBehaviour(self):
        self.run_away = False
        self.dict_actions = copy.deepcopy(self.copy_dict_actions)
        self.list_priorities = self.copy_list_priorities.copy()
        self.special_target = []

class RandomBehaviour(Behaviour):
    def __init__(self, behaviour_name):
        super().__init__()
        self.setBehaviourName(behaviour_name)
        # Inicializaré una clase de comportamiento con todo aleatorio
        self.setRandomPriorities()
        self.copy_dict_actions = copy.deepcopy(self.dict_actions)
        self.copy_list_priorities = self.list_priorities.copy()

    # Metodo para establecer las prioridades aleatorias del comportamiento
    def setRandomPriorities(self):
        # Paso a una lista todas las claves del diccionario de acciones para poder recorrerla
        list_actions = list(self.dict_actions.keys())
        # Los ordeno de forma aleatoria para tener una lista aleatoria con los comportamientos
        random.shuffle(list_actions)
        # Recorro la lista para determinar una direccion al movimiento y las mejoras que tendrá
        for action in list_actions:
            if isinstance(self.dict_actions.get(action), dict): 
                self.getRandomSpecialActions(action)
            # Por último guardo la lista de prioridad en la variable correspondiente
            self.list_priorities.append(action)

    # def changeBehaviour(self, context=[]):
    #     # Modifica el orden de la lista de forma aleatoria 
    #     random.shuffle(self.list_priorities)
    #     for action in list(self.dict_actions.keys()):
    #         if isinstance(self.dict_actions.get(action), dict): 
    #             self.getRandomSpecialActions(action)

    def resetBehaviour(self):
        self.run_away = False
        self.dict_actions = copy.deepcopy(self.copy_dict_actions)
        self.list_priorities = self.copy_list_priorities.copy()
        self.special_target = []

class Agressive(Chaser):
    """
    Tipo de chaser que se centrará en atacar a los agentes con mayores recursos
    """
    def __init__(self):
        super().__init__()
        self.setBehaviourName(self.__class__.__name__)  
    
    def changeBehaviour(self, player, context_players, context_planets, dict_enemies):
        # Buscar el que mas recursos tenga y luchar con el, si tiene peor arma lo que hare será mejorar el arma y si no puede intetará mejorar 
        # Pero siempre perseguira al agente con mas oro
        agent_more_gold = dict_enemies["More_Resources"] 
        if player.getNumPlayerWeapon() != 0:
            # Si tengo un arma peor que el agente con mas recursos intentare mejorarla 
            if player.getNumPlayerWeapon() <= agent_more_gold.getNumPlayerWeapon():
                # Si tiene todas las armas mejoradas, tendrá que buscar upgradear para poder ganar el maximo de duelos al agente con mas recursos
                if player.getNumPlayerWeapon() == MAX_NUM_WEAPONS and not player.getAgentUpgrades().isDamageUpgraded():
                    self.list_priorities = ["Upgrade","Weapon","Move","Factory"]

            # Se mueve hacia el jugador con mas recursos
            self.addSpecialTarget(agent_more_gold.getAgentPos())
            return

        # Si no tiene armas actuará normal para poder generarlas 
        return

class Friendly(Behaviour):
    """
    Agente que ha desarrollado la habilidad para cooperar con los demas ayudando a los mas necesitados
    """
    def __init__(self):
        super().__init__()
        self.setBehaviourName(self.__class__.__name__)
        self.dict_actions["Move"]["To_Planet"] = True
        self.dict_actions["Upgrade"]["Factory"] = True
        # Este agente no tendrá acceso a las armas, por lo que no podrá atacar a nadie
        self.list_priorities = ["Factory", "Upgrade", "Move"]

    def changeBehaviour(self, player, context_players, context_planets, dict_enemies):
        # Como el agente no puede atacar primero se tiene que centrar en construir fábricas para poder tener cierta economia
        if len(context_planets) > 0:
            # Si se encuentra con algun planeta reseteo el comportamiento para que se olvide de seguir al que menos oro tiene
            self.resetBehaviour()
            # Si me encuentro uno o mas planetas me dirijo a ellos
            self.list_priorities = ["Move", "Factory", "Upgrade"]
            
        
        else:
            # Buscará a el agente que menos oro tenga en la simulación
            agent_less_resources = dict_enemies["Less_Resources"]
            self.addSpecialTarget(agent_less_resources.getAgentPos())
            # Si está en su campo de vision le doy los recursos como si hubiese ganado la pelea y reseteo el comportamiento 
            if agent_less_resources in context_players:
                print(f"Regalo el 10% de riquezas a {agent_less_resources.getId()}")
                agent_less_resources.addBattleResources(player)
                self.resetBehaviour()

        # Si no tiene nada alrededor actuará normal construyendo fabricas
        return 

    def resetBehaviour(self):
        self.run_away = False
        self.dict_actions = {"Move": {"To_Planet": True, "To_Player":False}, "Factory": 0, "Weapon": 0, "Upgrade": {"Damage": False, "Factory":True}}
        self.list_priorities = ["Factory", "Upgrade", "Move"]
        self.special_target = []    

# Para poder comprobar el funcionamiento de la clase 
if __name__ == "__main__":
    comportamiento = RandomBehaviour("Random")
    explorador = Explorer()
    perseguidor = Chaser()
    granjero = Farmer()
    custom = CustomBehaviour("nombre")
    # for i in range(100):
    #     print(RandomBehaviour(str(i)).getPriorities())

    print(f"nombre de comporamiento de Clase RandomBehaviour -> {comportamiento.actual_behaviour}")
    print(f"nombre de comporamiento de Clase Explorer -> {explorador.actual_behaviour}")
    print(f"nombre de comporamiento de Clase Chaser -> {perseguidor.actual_behaviour}")
    print(f"nombre de comporamiento de Clase Farmer -> {granjero.actual_behaviour}")
    print(f"nombre de comporamiento de Clase Personalizada -> {custom.actual_behaviour}")
    print("Clase RandomBehaviour")
    print(comportamiento.getPrioritiesStr())
    print(comportamiento.getPriorities())
    for i in range(0,10):
        comportamiento.changeBehaviour()
        print(comportamiento.getPriorities())
        print("comportamiento resetado")
        comportamiento.resetBehaviour()
        print(comportamiento.getPriorities())
    print("Clase Explorador")
    print(explorador.getPrioritiesStr())
    print(explorador.getPriorities())
    print("Clase Personalizada")
    print(custom.getPrioritiesStr())
    print(custom.getPriorities())

               