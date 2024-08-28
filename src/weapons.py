
class Weapon():
    
    def __init__(self):
        """
        Clase que sirve para tener unas mejoras de armas para poder combatir con otros agentes 

        Atributos:
            actual_weapon: Arma actual del agente, empezará sin arma
            num_upgrades: Numero de mejoras que se han hecho al arma como maximo se podrán 3
            value_weapons: Diccionario con el daño asociado a cada arma
            list_weapons: lista de armas del juego
        """
        self.actual_weapon = ""
        self.num_upgrades = 0
        self.value_weapons = {
            "Lasers": 2,
            "Plasma Cannon": 3,
            "Guided missil" : 5
        }
        self.list_weapons = list(self.value_weapons.keys())


    def upgradeWeapon(self):
        try:
            # Si el arma actual se encuentra entre las armas del juego, miramos la siguiente arma en la lista y asignamos su valor a actual_weapon 
            index = self.list_weapons.index(self.actual_weapon)
            # Podremos incrementar el arma porque el indice es menor a la longitud de la lista 
            if index + 1 < len(self.list_weapons):
                self.actual_weapon = self.list_weapons[index+1]
            self.num_upgrades += 1
        except:
            # Si no tiene arma creamos una
            self.actual_weapon = self.list_weapons[0]
            self.num_upgrades += 1


    def getWeapon(self):
        if self.actual_weapon == "":
            return "None"
        return self.actual_weapon, self.value_weapons[self.actual_weapon]
    
    def getNumUpgrades(self):
        return self.num_upgrades
    
    def __str__(self):
        return self.actual_weapon
