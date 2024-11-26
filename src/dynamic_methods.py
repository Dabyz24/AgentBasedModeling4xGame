from global_constants import *

# Método para quitar la funcionalidad de evitar las luchas de los Explorer y la construccion de fabricas
def changeBehaviourDummyExplorer(self, player, context_players, context_planets, dict_enemies):
    return 

#------- Método dinámico para modificar el comportamiento de Chaser
def changeBehaviourChaser(self, player, context_players, context_planets, dict_enemies):
    # Buscar el que mas recursos tenga y luchar con el, si tiene peor arma lo que hará será mejorar el arma y si no puede intetará mejorar 
    # Pero siempre perseguira al agente con mas puntos
    self.agent_more_points = dict_enemies["Points_Winner"]
    if player.getNumPlayerWeapon() != 0:
        # Si tengo un arma peor que el agente con mas recursos intentare mejorarla 
        if player.getNumPlayerWeapon() <= self.agent_more_points.getNumPlayerWeapon():
            # Si tiene todas las armas mejoradas, tendrá que buscar upgradear para poder ganar el maximo de duelos al agente con mas recursos
            if player.getNumPlayerWeapon() == MAX_NUM_WEAPONS and not player.getAgentUpgrades().isDamageUpgraded():
                self.list_priorities = ["Upgrade","Weapon","Move","Factory"]

        # Se mueve hacia el jugador con mas recursos
        self.addSpecialTarget(self.agent_more_points.getAgentPos())
        return

    # Si no tiene armas actuará normal para poder generarlas 
    return

#------- Métodos dinámicos para modificar el comportamiento de Farmer -------
def changeBehaviourFarmer(self, player, context_players, context_planets, dict_enemies):
    # Resetea el comportamiento para que vuelva a decidir la acción que hacer
    self.resetBehaviour()
    # Si se encuentra con un enemigo en su contexto
    if len(context_players) > 0:
        worst_weapon = float("inf")
        if player.getNumPlayerWeapon() != 0:
            # Si el jugador tiene un arma busca el que peor arma tenga para decidir si luchar con el o no 
            worst_weapon, worst_weapon_agent = self._checkWorstWeaponAgent(context_players, player)
            # Si tiene mejor arma le persigue para luchar y aprovechar esa ventaja
            if player.getPlayerWeapon()[1] > worst_weapon:
                # Establece como prioridad el movimiento para no perder al agente con peor arma
                self.list_priorities = ["Move", "Factory", "Upgrade", "Weapon"]
                self.dict_actions["Move"]["To_Player"] = True
                self.addSpecialTarget(worst_weapon_agent.getAgentPos())
                return
            # Si tiene peor arma o el otro agente tiene ventaja de daño por tener la mejora. Huye del combate  
            elif (player.getPlayerWeapon()[1] < worst_weapon) or (worst_weapon_agent.getAgentUpgrades().isDamageUpgraded() and not player.getAgentUpgrades().isDamageUpgraded()):
                self.run_away = True
                self.addSpecialTarget(worst_weapon_agent.getAgentPos())
                return
        # En caso de no tener arma huye del primer agente que se encuentre en su contexto 
        else:
            self.run_away = True
            self.addSpecialTarget(context_players[0].getAgentPos())
            self.list_priorities = ["Move", "Factory", "Upgrade", "Weapon"]
            return
                
    # Si no hay rivales busca si hay algún planeta e intenta conquistarlo 
    if len(context_planets) > 0:
        # Si encuentra un planeta establece como prioridad y como objetivo del movimiento ese planeta para conquistarlo
        self.list_priorities = ["Move", "Factory", "Upgrade", "Weapon"] 
        self.dict_actions["Move"]["To_Planet"] = True
        self.addSpecialTarget(context_planets[0].getPlanetPos())
        return
    
    # Si no tiene nada alrededor, comprueba si puede construir fabricas manteniendo sus planetas conquistados
    if self.check_money(player):
        self.list_priorities = ["Factory", "Upgrade", "Weapon", "Move"]
        return
    # Si no puede construir la fabrica y mantener los planetas, actua normal seleccionando como direccion de movimiento los planetas
    self.dict_actions["Move"]["To_Planet"] = True
    return

# Método dinamico para comprobar si se puede construir fabricas y pagar las taxes de los planetas           
def check_money(self, player):
    price_increase = round(INCREASE_FACTOR ** player.getFactories())
    if player.getGold() - (FACTORIES_GOLD_COST * price_increase) > TAXES_PLANET * player.getPlanets():
        return True
    return False
    
# Nuevo resetBerhaviour para poder añadir la opcion de mejora de daño en los Farmer
def resetBehaviourFarmer(self):
    self.run_away = False
    self.dict_actions = {"Move": {"To_Planet": False, "To_Player":False}, "Factory": 0, "Weapon": 0, "Upgrade": {"Damage": True, "Factory":True}}
    self.list_priorities = ["Factory", "Upgrade", "Weapon", "Move"]
    self.special_target = []
