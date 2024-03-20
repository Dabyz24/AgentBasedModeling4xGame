
class Upgrades():

    def __init__(self):
        """
        Clase que sirve para tener un arbol de tecnologías para poder mejorar atributos de los agentes 
        Si se quieren añadir más upgrades simplemente sería poner una nueva variable booleana y añadirla a la funcion 
        para luego en la clase agente mediante esa variable modificar el funcionamiento deseado

        Atributos:

            damage_upgrade: Permite mejorar la probabilidad a la hora de ganar los combates 
            factories_upgrades: Permite duplicar las ganancias de las fabricas
            list_upgrades: Tendrá guardadas todos las mejoras para poder obtener el numero maximo de upgrades permitidos
            num_upgrades: Llevará la cuenta de las mejoras para saber si se pueden mejorar más o ya ha alcanzado el límite
        """
        self.damage_upgrade = False
        self.factories_upgrade = False
        self.list_upgrades = ["Damage","Factory"]
        self.num_upgrades = 0


    def upgradeDamage(self):
        if not self.damage_upgrade:
            self.damage_upgrade = True
            self.num_upgrades += 1
            self.list_upgrades.remove("Damage")

    def upgradeFactories(self):
        if not self.factories_upgrade:
            self.factories_upgrade = True
            self.num_upgrades += 1
            self.list_upgrades.remove("Factory")

    # getters y setters para los atributos y poder manejarlo para cada agente
    def isDamageUpgraded(self):
        return self.damage_upgrade
    
    def getNumUpgrades(self):
        return self.num_upgrades
    
    def isUpgradeAvailable(self):
        # Añado 1 para que cuando solo quede una mejora disponible se pueda seleccionar
        return self.num_upgrades <= len(self.list_upgrades)+ 1
    
    def getListUpgrades(self):
        return self.list_upgrades
    
    def getUpgrades(self):
        aux_str = ""
        if self.damage_upgrade:
            aux_str += "D ↑ "
        if self.factories_upgrade:
            aux_str += "F ↑ "
        if aux_str == "": return "None"
        return aux_str
        