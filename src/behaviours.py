import random

# Objeto encargado de generalizar todos los comportamientos y permitir la creacion de nuevos comportamientos de una manera sencilla

"""
Esta puede ser la clase padre de la que hereden todos los demas comportamientos, asi solo tendré que especificar atributos y jerarquia
Si hago esto esta clase tendrá todos los demas metodos que solo cambiaran para cada uno por los atributos y las definciones de las clasess
"""
class Behaviour():
    """
    Diferentes comportamientos que están preestablecidos:
    --> Chaser: Su objetivo será perseguir al agente y luchar contra el 
    --> Explorer: Su objetivo será buscar los plaentas que no estén habitados y conquistarlos
    --> Farmer: Su objetivo será construir fábricas para obtener más recursos

    Tendrá que tener más comportamietos,
    como por ejemplo un CIENTIFICO (tendrá menos coste al efectuar mejoras y tendrá nuevas opciones como moverse más de una casilla)
    Otro puede ser el PACIFISTA que evite el uso de armas y huya del combate siempre que pueda
    Tengo que contemplar la posibilidad de crear nuevos comportamientos con ciertos atributos y estableciendo las cosas que lo hacen especial

    """
    def __init__(self):
        self.actual_behaviour = ""
        self.initial_behaviours = ["Explorer", "Chaser", "Farmer"]
        self.list_actions = ["Move", "Factory", "Weapon", "Upgrade"]
        self.list_priorities = []
        # Servira para comprobar que al establecer una nueva prioridad se pongan los numeros correctos
        self._valid_numbers_priority = ["1","2","3","4"]
    
    def setPriorities(self, behaviour, random_flag=False):
        if behaviour in self.initial_behaviours:
            if behaviour == "Explorer":
                self.list_priorities = ["Move", "Factory", "Upgrade", "Weapon"]
            if behaviour == "Chaser":
                self.list_priorities = ["Weapon", "Move", "Upgrade", "Factory"]
            if behaviour == "Farmer":
                self.list_priorities = ["Factory", "Upgrade", "Move", "Weapon"]

        elif random_flag:
            random.shuffle(self.list_actions)
            for action in self.list_actions:
                self.list_priorities.append(action)
        else:
            different_priorities = self.checker_priorities()
            
            for priority in different_priorities:
                # Se resta uno en la priority para que coincida con el indice de list_actions
                self.list_priorities.append(self.list_actions[int(priority)-1])

    def checker_priorities(self):
        while True:  
                str_priority = input("Select from highest to lowest priority (1 = Move, 2 = Factory, 3 = Weapon, 4 = Upgrade) using comma as separator. Ex: 1,2,3,4\n")
                different_priorities = str_priority.split(",")
                if all(number in self._valid_numbers_priority for number in different_priorities) and len(different_priorities) == len(self.list_actions):
                        return different_priorities
                else:
                    print(f"This are the only valid numbers: {self._valid_numbers_priority}")


    def getListPriorities(self):
        aux_str = ""
        for i in range(0, len(self.list_priorities)):
            if i+1 == len(self.list_priorities):
                aux_str += self.list_priorities[i]
            else:
                aux_str += self.list_priorities[i] + " -> "    
        return aux_str
    

    def new_behaviour(self, new, flag=False):
        """
        Crear un nuevo comportamiento  
        """
        self.list_priorities = []
        self.actual_behaviour = new
        if flag:
            self.setPriorities(new, random_flag=True)
        else:
            self.setPriorities(new)

# Para poder comprobar el funcionamiento de la clase 
if __name__ == "__main__":
    comportamiento = Behaviour()
    comportamiento.new_behaviour("Chaser")
    print(comportamiento.actual_behaviour)
    print(comportamiento.getListPriorities())
    comportamiento.new_behaviour("new2")
    print(comportamiento.actual_behaviour)
    print(comportamiento.getListPriorities())
    comportamiento.new_behaviour("random", flag=True)
    print(comportamiento.actual_behaviour)
    print(comportamiento.getListPriorities())


    # Tengo que abstraer todo lo que hace importante a un comportamiento 
    """
    Dependiendo del comportamiento tendra una lista de prioridades que realizar que en funcion de si puede o no realizara
    Osea tendria que tener un metodo para establecer prioridades, pero claro en ejecucion esto sería muy complicado, porque lo tendría que hardcodear yo todo el rato
    Pero los nuevos comportamientos pueden tener una lista de prioridades aleatoria y que comprueben si es mejor que las anteriores o no
    Osea puedo crear new_Behavior cuyo nombre será new y le ire añadiendo un id y que cada uno decida aleatorio a que le va a dar mas prioridad, si a las mejoras, a los movcimientos o a los combates
    Pero tengo que poder saber la lista de prioridades que tiene cada agente, quizas lo puedo imprimir en la informacion del agente, que ponga comportamiento y sea una lista de numeros que sepa su significado (1. Moverse, 2. Luchar y por ultimo farmear)

    Tengo que añadir a los comportamientos la opcion de crear las upgrades, osea que iran dentro de esta clase en funcion del orden que elijan
    Ahora bien necesito crear las prioridades que no se muy bien como hacerlo porque siempore harán lo primero, a no ser que les ponga ciertas restricciones, como que no puedan repetir la misma accion dos veces seguidas
    Una mejora puede ser la opcion de moverse siempre y luego realizar una accion para estar siempre huyendo 
    
    """ 
                