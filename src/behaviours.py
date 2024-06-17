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
                        return action, "None"
                
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
        # Si el vecino es un jugador el agente huira de el 
        if len(context_players) > 0:
            # Tengo que huir del player si tiene un arma
            for enemie in context_players:
                if enemie.getNumPlayerWeapon() > 0:
                    self.run_away = True
                    self.addSpecialTarget(enemie.getAgentPos())
                    return
            # Si ninguno de los jugadores tiene un arma del que huir actuo normal 
            self.resetBehaviour()
            return 
        # Si no solo habrá vecinos Planet 
        elif len(context_planets) > 0: 
            # if all(planet.isInhabit() for planet in context_planets):
            #         # Si todos los planetas están habitados 
            #         print("El agente intentará construir una fabrica y luego moverse")
            #         self.list_priorities = ["Factory", "Move", "Weapon", "Upgrade"]
            #         return
            # else:
                    # Si es un planeta actuará como siempre, aunque tendría que dar prioridad al planeta con oro que el jugador pueda mantener 
                    self.resetBehaviour()
                    return 
        else:
            # Si no tiene ningún vecino alrededor, se comportará con el comportamiento estandar
            print("El agente cambia su prioridad para construir una fabrica primero")
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

    # def changeBehaviour(self, player, context_players, context_planets, dict_enemies):
    #     # Reseteo el comportamiento para que vuelva a decidir la acción que hacer
    #     self.resetBehaviour()
    #     # Si el agente tiene algún vecino, ya sea otro jugador o planeta intentará identificar la situación para cambiar su comportamiento 
    #     if len(context_planets) > 0:
    #         # Significa que habrá al menos un vecino Planet y otro vecino Player
    #         if len(context_players) > 0:
    #             # Tengo que huir del player 
    #             self.run_away = True
    #             self.addSpecialTarget(context_players[0])
    #             return 
    #         # Si no solo habrá vecinos Planet 
    #         else:
    #             # Si solo hay un miembro todos tendrán el mismo tipo, por lo que puedo comprobar el tipo del primer elemento de la lista 
    #             if all(planet.isInhabit() for planet in context_planets):
    #                     # Si todos los planetas están habitados 
    #                     print("El agente intentará construir una fabrica y luego moverse")
    #                     self.list_priorities = ["Factory", "Move", "Weapon", "Upgrade"]
    #             else:
    #                     # Si es un planeta actuará como siempre, aunque tendría que dar prioridad al planeta con oro que el jugador pueda mantener 
    #                     self.resetBehaviour()
    #                     return 
    #     # Si no hay ningun planeta solo habrá jugadores alrededor
    #     elif len(context_players) > 0:
    #         # Buscar el que peor arma tenga y compararla con la mia, si tiene peor arma lo que hare será luchar con él, es decir, acercarme
    #         # Si tiene un arma mejor lo que haré será huir como maxima prioridad  
    #         worst_weapon = float("inf")
    #         if player.getNumPlayerWeapon() != 0:
    #             if player.getPlayerWeapon()[1] > dict_enemies["Worst_Weapon"].getPlayerWeapon()[1]:
    #                 if dict_enemies["Worst_Weapon"] in context_players:
    #                     print("Se encuentra aqui el agente con peor arma")
    #                     # Perseguir a el agente con peor arma
    #                     self.addSpecialTarget(dict_enemies["Worst_Weapon"].getAgentPos())
    #                     return 
    #                 else:
    #                     print("No se encuentra el agente con peor arma, buscare si en mi contexto hay uno con peor arma que el mio")
    #             # Si el jugador tiene un arma puedo buscar el que peor arma tenga para decidir si luchar con el o no 
    #                     print("Busco el agente con peor arma")
    #                     for neighbor in context_players:
    #                         try:
    #                             if neighbor.getPlayerWeapon()[1] < worst_weapon:
    #                                 worst_weapon = neighbor.getPlayerWeapon()[1]
    #                         except:
    #                             # Si entra en el except es porque no tiene ningun arma y está comparando un float con el string None, por lo que es el agente con peor arma
    #                             worst_weapon = neighbor.getPlayerWeapon()[1]
    #                     # Si tengo un arma mejor lucharé con el 
    #                     if player.getPlayerWeapon()[1] > worst_weapon:
    #                         # Haré que se mueva hacia el jugador con peor arma
    #                         self.dict_actions["Move"]["To_Planet"] = False
    #                         self.dict_actions["Move"]["To_Player"] = True
    #                         return 
    #             else:
    #                 # Huir
    #                 self.resetBehaviour()
    #                 return   
    #         else:
    #             # Huir hacia otro lado
    #             self.resetBehaviour()
    #             return 
    #     else:
    #         # Si no tiene ningún vecino alrededor, se comportará con el comportamiento estandar
    #         print("El agente cambia su prioridad para construir una fabrica primero")
    #         self.list_priorities = ["Factory", "Move", "Weapon", "Upgrade"]
    #         return 

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
                    print(f"This are the only valid numbers: {self._valid_numbers_priority}")

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

               