import random
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

    # Metodo que determinará el comportamiento de la clase Behaviour
    def act(self, agent_gold, agent_tech, agent_factories, agent_weapon, agent_upgrades, is_ship_created):
        for action in self.list_priorities:
            if action == "Move":
                list_move_direction = self.getPriorities()[1]
                if (agent_gold >= SPACE_SHIP_GOLD_COST and agent_tech >= SPACE_SHIP_TECH_COST) or is_ship_created:
                    if len(list_move_direction) == 1:
                        # Si la lista de direccion tiene solo una devolvere la accion y la direccion 
                        return action, list_move_direction[0]
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
    

class Explorer(Behaviour):

    def __init__(self):
        super().__init__()
        self.setBehaviourName(self.__class__.__name__)
        self.dict_actions["Move"]["To_Planet"] = True
        self.list_priorities = ["Move", "Factory", "Upgrade", "Weapon"]

    # def act():
    #     pass

class Chaser(Behaviour):

    def __init__(self):
        super().__init__()
        self.setBehaviourName(self.__class__.__name__)
        self.dict_actions["Move"]["To_Player"] = True
        self.dict_actions["Upgrade"]["Damage"] = True
        self.list_priorities = ["Weapon", "Upgrade", "Move", "Factory"]


class Farmer(Behaviour):

    def __init__(self):
        super().__init__()
        self.setBehaviourName(self.__class__.__name__)
        self.dict_actions["Upgrade"]["Factory"] = True
        self.list_priorities = ["Factory", "Upgrade", "Move", "Weapon"]

class CustomBehaviour(Behaviour):

    def __init__(self, behaviour_name):
        super().__init__()
        self.setBehaviourName(behaviour_name)
        # Servira para comprobar que al establecer una nueva prioridad se pongan los numeros correctos
        self._valid_numbers_priority = ["1","2","3","4"]
        self.setPriorities()
        
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


class RandomBehaviour(Behaviour):
    def __init__(self, behaviour_name):
        super().__init__()
        self.setBehaviourName(behaviour_name)
        # Inicializaré una clase de comportamiento con todo aleatorio
        self.setRandomPriorities()

    # Metodo para establecer las prioridades aleatorias del comportamiento
    def setRandomPriorities(self):
        # Paso a una lista todas las claves del diccionario de acciones para poder recorrerla
        list_actions = list(self.dict_actions.keys())
        # Los ordeno de forma aleatoria para tener una lista aleatoria con los comportamientos
        random.shuffle(list_actions)
        # Recorro la lista para determinar una direccion al movimiento y las mejoras que tendrá
        for action in list_actions:
            if action == "Move":
                self.getRandomSpecialActions(action)
            elif action == "Upgrade":
                self.getRandomSpecialActions(action)
            # Por último guardo la lista de prioridad en la variable correspondiente
            self.list_priorities.append(action)

    # Método para establecer de manera aleatoria la direccion del movimiento y el comportamiento
    def getRandomSpecialActions(self, action):
        for item in self.dict_actions[action]:
            coin = random.randint(0,1)
            if coin == 0:
                self.dict_actions[action][item] = False
            else:
                self.dict_actions[action][item] = True


# Para poder comprobar el funcionamiento de la clase 
if __name__ == "__main__":
    comportamiento = RandomBehaviour("Random")
    explorador = Explorer()
    perseguidor = Chaser()
    granjero = Farmer()
    custom = CustomBehaviour("nombre")
    
    print(f"nombre de comporamiento de Clase RandomBehaviour -> {comportamiento.actual_behaviour}")
    print(f"nombre de comporamiento de Clase Explorer -> {explorador.actual_behaviour}")
    print(f"nombre de comporamiento de Clase Chaser -> {perseguidor.actual_behaviour}")
    print(f"nombre de comporamiento de Clase Farmer -> {granjero.actual_behaviour}")
    print(f"nombre de comporamiento de Clase Personalizada -> {custom.actual_behaviour}")
    print("Clase RandomBehaviour")
    print(comportamiento.getPrioritiesStr())
    print(comportamiento.getPriorities())
    print("Clase Explorador")
    print(explorador.getPrioritiesStr())
    print(explorador.getPriorities())
    print("Clase Personalizada")
    print(custom.getPrioritiesStr())
    print(custom.getPriorities())

               