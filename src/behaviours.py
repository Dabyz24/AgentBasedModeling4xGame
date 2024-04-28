
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
        POSSIBLE_BEHAVIOURS = ["Explorer", "Chaser", "Farmer"]
        pass

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
                

# Comportamientos del agente
# if agent.getBehaviour() == "Chaser":
#                             # Se pone a perseguir al enemigo más cercano para luchar con él
#                             list_enemies = self.getAllPlayersPos()
#                             try:
#                                 _ , chosen_move = self.closestTarget(agent.getAgentPos(), list_enemies)
#                                 chosen_ation = chosen_move
#                             except:
#                                 # Si está en la misma posición que el enemigo la accion elegida será o un movimiento o crear una fabrica
#                                 chosen_ation = self.random.choices(POSSIBLE_ACTIONS[0:9])[0]
                            
#                         elif agent.getBehaviour() == "Explorer":    
#                         # Se pone a buscar planetas cercanos sin explorar
#                             list_uninhabited_planets = self.getAllPlanetPos()
#                             # Si la lista de planetas sin habitar es vacia el agente realizara un movmiento o creara una fabrica
#                             if len(list_uninhabited_planets) == 0:
#                                 chosen_ation = self.random.choices(POSSIBLE_ACTIONS[0:9])[0]
#                             else:
#                                 try:
#                                     _ , chosen_move = self.closestTarget(agent.getAgentPos(), list_uninhabited_planets)
#                                     chosen_ation = chosen_move
#                                 except:
#                                     chosen_ation = self.random.choices(POSSIBLE_ACTIONS[0:9])[0]

#                         elif agent.getBehaviour() == "Farmer":
#                             # Creara una fabrica en los turnos pares y en los impares se movera
#                             if self.step_count % 2 == 0:
#                                 chosen_ation = ACTION_SPACE.get("Factory")
#                             else:
#                                 chosen_ation = self.random.choices(POSSIBLE_ACTIONS[0:8])[0]