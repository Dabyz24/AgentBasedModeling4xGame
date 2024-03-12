
'''
1. Crear una clase que permita incluir mejoras a los atributos o las habilidades de los agentes utilizando su tecnología
Tengo que tener en cuenta que los atributos se podrán cambiar en ejecución por lo que tengo que programar las cosas para que se puedan modificar facilmente
Puedo hacer una clase así con booleanos para que el codigo lo pueda cambiar mas facil desde una única clase y no tenga qeu buscar por todos los archivos

Pensar en una lógica para poder cambiar los valores sabiendo que tengo las mejoras, se me ocurre un if pero pensar una manera más elaborada
Ideas:
    Podrían mejorar la probabilidad de las armas, para así poder ganar más combates, si tiene esa mejora hace que se añada 5 al valor
    Pueden ampliar el rango de movimiento para que se puedan mover dos posiciones en un mismo turno (radius en get_neigborhood)

Manera de implementar algo dinamico en ejecucion mediante exec()

name = "David"
age = 12
code = f"""def greet():
        print("Name: {name}")
        print("Age: {age}")
        """
exec(code)
greet()
'''
class Upgrades():

    def __init__(self):
        """
        damage_upgrade: Permite mejorar la probabilidad a la hora de ganar los combates 
        movement_upgrade: Permite moverse dos posiciones en un turno

        num_upgrades: Llevará la cuenta de las mejoras para saber si se pueden mejorar más o ya ha alcanzado el límite
        """
        self.damage_upgrade = False
        self.movement_upgrade = False
        self.num_upgrades = 0

    def upgradeDamage(self):
        self.damage_upgrade = True

    def upgradeMovement(self):
        self.movement_upgrade = True
    
    def getNumUpgrades(self):
        return self.num_upgrades

