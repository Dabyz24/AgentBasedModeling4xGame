import mesa

from agents import Player, Planet
from model import Game

def game_portrayal(agent):
    if agent is None:
        return
    
    portrayal = {}

    if type(agent) is Player:
        portrayal["Shape"] = "circle"
        portrayal["r"] = 0.3
        portrayal["Layer"] = 1
        portrayal["Filled"] = "true"
        portrayal["Color"] = "black"
        portrayal["Agent Id"] = agent.getId()

    if type(agent) is Planet:
            portrayal["Shape"] = "circle"
            portrayal["r"] = 1
            portrayal["Layer"] = 0
            # Para el color elegirlo dependiendo de si tiene mas tecnologia o mas dinero
            portrayal["Filled"] = "true"
            if agent.isInhabit(): 
                portrayal["Color"] = "green"
                portrayal["text"] = agent.getPlayer().getId()
            else:
                portrayal["Color"] = "red"
                portrayal["text"] = "None"
            portrayal["text_color"] = "black"

    return portrayal

def overviewAgents(model):
    summary = model.propertiesAgents()
    aux_str = ""
    for i, k in summary.items():
        aux_str += (f"Agent: {i} Resources: {k} <br>")
    return aux_str

canvas_element = mesa.visualization.CanvasGrid(game_portrayal, 20, 20, 500, 500)
chart_elemnt = mesa.visualization.ChartModule(
     [
          {"Label": "Num Estelar Points", "Color": "#AA0000"}
     ]
)

model_params = {
        "title": mesa.visualization.StaticText("Parameters:"),
        "num_players": mesa.visualization.Slider("Number of players", 2, 1, 6),
        "num_planets": mesa.visualization.Slider("Number of planets", 5, 2, 10),
        "prob_factory": mesa.visualization.Slider("Probability of producing Factories", 0.4, 0.0, 1.0, 0.1),
        "prob_weapon": mesa.visualization.Slider("Probability of producing Weapons", 0.1, 0.0, 1.0, 0.1),
        "prob_space_ship": mesa.visualization.Slider("Probability of producing Space Ships", 0.6, 0.0, 1.0, 0.1, description="Space ships allowed the player to move"),
        "taxes_planet": mesa.visualization.Slider("Taxes apply to planets", 20, 10, 100, 10),

}

server = mesa.visualization.ModularServer(Game, [canvas_element, overviewAgents, chart_elemnt], "Agent based modeling 4x Game", model_params)
server.port = 8521