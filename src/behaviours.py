import random

# Objeto encargado de generalizar todos los comportamientos y permitir la creacion de nuevos comportamientos de una manera sencilla

class Behaviour():
    """
    Diferentes comportamientos que están preestablecidos:
    --> Chaser: Su objetivo será perseguir al agente y luchar contra el 
    --> Explorer: Su objetivo será buscar los plaentas que no estén habitados y conquistarlos
    --> Farmer: Su objetivo será construir fábricas para obtener más recursos

    Tendrá que tener más comportamietos se pueden añadir aleatorios o estableciendo la funcionalidad que se quiera,
    
    ****como por ejemplo un CIENTIFICO (tendrá menos coste al efectuar mejoras y tendrá nuevas opciones como moverse más de una casilla)
    ****Otro puede ser el PACIFISTA que evite el uso de armas y huya del combate siempre que pueda

    """
    def __init__(self):
        self.actual_behaviour = ""
        self.initial_behaviours = ["Explorer", "Chaser", "Farmer"]
        self.dict_actions = {"Move": {"To_Planet": False, "To_Player":False}, "Factory": 0, "Weapon": 0, "Upgrade": {"Damage": False, "Factory":False}}
        self.list_priorities = []
        # Servira para comprobar que al establecer una nueva prioridad se pongan los numeros correctos
        self._valid_numbers_priority = ["1","2","3","4"]
    
    def setPriorities(self, behaviour, random_flag=False):
        if behaviour in self.initial_behaviours:
            if behaviour == "Explorer":
                self.dict_actions["Move"]["To_Planet"] = True
                self.list_priorities = ["Move", "Factory", "Upgrade", "Weapon"]
            if behaviour == "Chaser":
                self.dict_actions["Move"]["To_Player"] = True
                self.dict_actions["Upgrade"]["Damage"] = True
                self.list_priorities = ["Weapon", "Move", "Upgrade", "Factory"]
            if behaviour == "Farmer":
                self.dict_actions["Upgrade"]["Factory"] = True
                self.list_priorities = ["Factory", "Upgrade", "Move", "Weapon"]

        elif random_flag:
            list_actions = list(self.dict_actions.keys())
            random.shuffle(list_actions)
            for action in list_actions:
                if action == "Move":
                    self.getRandomSpecialActions(action)
                elif action == "Upgrade":
                    self.getRandomSpecialActions(action)
                self.list_priorities.append(action)
        else:
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

            list_actions = list(self.dict_actions.keys())
            for priority in different_priorities:
                # Se resta uno en la priority para que coincida con el indice de dict_actions
                self.list_priorities.append(list_actions[int(priority)-1])

    def inputPriorities(self):
        while True:  
                str_priority = input("Select from highest to lowest priority (1 = Move, 2 = Factory, 3 = Weapon, 4 = Upgrade) using comma as separator. Ex: 1,2,3,4\n")
                different_priorities = str_priority.split(",")
                if all(number in self._valid_numbers_priority for number in different_priorities) and len(different_priorities) == len(self.dict_actions):
                        return different_priorities
                else:
                    print(f"This are the only valid numbers: {self._valid_numbers_priority}")


    def getPrioritiesStr(self):
        aux_str = ""
        for i in range(0, len(self.list_priorities)):
            if i+1 == len(self.list_priorities):
                aux_str += self.list_priorities[i]
            else:
                aux_str += self.list_priorities[i] + " -> "    
        return aux_str
    
    def getPriorities(self):
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
    
    def newBehaviour(self, new, flag=False):
        """
        Crear un nuevo comportamiento  
        """
        self.list_priorities = []
        self.resetDictActions()
        self.actual_behaviour = new
        if flag:
            self.setPriorities(new, random_flag=True)
        else:
            self.setPriorities(new)

    def resetDictActions(self):
        self.dict_actions = {"Move": {"To_Planet": False, "To_Player":False}, "Factory": 0, "Weapon": 0, "Upgrade": {"Damage": False, "Factory":False}}

    def getRandomSpecialActions(self, action):
        if action == "Move" or action == "Upgrade":
            for item in self.dict_actions[action]:
                coin = random.randint(0,1)
                if coin == 0:
                    self.dict_actions[action][item] = False
                else:
                    self.dict_actions[action][item] = True

    def getActualBehaviour(self):
        return self.actual_behaviour
    

# Para poder comprobar el funcionamiento de la clase 
if __name__ == "__main__":
    comportamiento = Behaviour()
    comportamiento.newBehaviour("Explorer")
    print(comportamiento.actual_behaviour)
    print(comportamiento.getPrioritiesStr())
    print(comportamiento.getPriorities())
    comportamiento.newBehaviour("Chaser")
    print(comportamiento.actual_behaviour)
    print(comportamiento.getPrioritiesStr())
    print(comportamiento.getPriorities())
    comportamiento.newBehaviour("Farmer")
    print(comportamiento.actual_behaviour)
    print(comportamiento.getPrioritiesStr())
    print(comportamiento.getPriorities())
    comportamiento.newBehaviour("random", flag=True)
    print(comportamiento.actual_behaviour)
    print(comportamiento.getPrioritiesStr())
    comportamiento.newBehaviour("new2")
    print(comportamiento.actual_behaviour)
    print(comportamiento.getPrioritiesStr())
               