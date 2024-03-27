import mesa

from agents import Player, Planet
from model import Game
from global_constants import TAXES_PLANET

def game_portrayal(agent):
    if agent is None:
        return
    
    portrayal = {}

    if type(agent) is Player:
        portrayal["Shape"] = "circle"
        portrayal["r"] = 0.3
        portrayal["Layer"] = 1
        portrayal["Filled"] = "true"
        portrayal["Color"] = agent.getAgentColor()
        portrayal["stroke_color"] = "black"
        portrayal["Agent Id"] = agent.getId()
        portrayal["Position"] = agent.getAgentPos(verbose=True)

    if type(agent) is Planet:
            portrayal["Shape"] = "circle"
            portrayal["r"] = 1
            portrayal["Layer"] = 1
            # Para el color elegirlo dependiendo de si tiene mas tecnologia o mas dinero
            portrayal["Filled"] = "true"
            if agent.isInhabit(): 
                portrayal["Color"] = agent.getPlayer().getAgentColor()
                portrayal["text"] = "A "+agent.getPlayer().getId()
                portrayal["Planet Id"] = agent.getPlanetId()
                
            else:
                portrayal["Color"] = "red"
                portrayal["text"] = agent.getPlanetId()
            portrayal["Position"] = agent.getPlanetPos()
            portrayal["Resources"] = agent.getResources()
            portrayal["text_color"] = "black"

    return portrayal

def overviewAgents(model):
    summary = model.propertiesAgents()
    aux_str = ""
    for i, k in summary.items():
        aux_str += (f"""
                    <span style="display: inline-block; width:10px; height:10px; background-color:{i.getAgentColor()};border-style:solid;border-width:1px;"></span>
                    <strong>Agent: {i.getId()} </strong> Resources: {k} <br>
                    Agent Weapon: <strong>{i.getPlayerWeapon()[0]} </strong> Battles Won: {i.getBattlesWon()} 
                    Upgrades: <strong>{i.getAgentUpgrades().getUpgrades()} </strong>
                    <br> <hr>""")
    return aux_str

canvas_element = mesa.visualization.CanvasGrid(game_portrayal, 20, 20, 500, 500)

# chart_elemnt = mesa.visualization.ChartModule(
#      [
#           {"Label": "Num Estelar Points", "Color": "#AA0000"}
#      ]
# )

model_params = {
        "title": mesa.visualization.StaticText("Parameters:"),
        # "num_players": mesa.visualization.Slider("Number of players", Game.num_players, 1, 6),
        # "num_planets": mesa.visualization.Slider("Number of planets", Game.num_planets, 2, 20),
        "taxes_planet": mesa.visualization.Slider("Taxes apply to planets", TAXES_PLANET, 10, 100, 10),

}

server = mesa.visualization.ModularServer(Game, [canvas_element, overviewAgents], "Agent based modeling 4x Game", model_params)
server.port = 8521