import logging
import os

import time

from flask import Flask
from flask import request

# move classes to class/snake, class/board... 
from snakeClass import snake
from boardClass import board
from itemClass import item

from functions import selectDestination, chooseMove

app = Flask(__name__)

# Globals 
print("GLOBAL: Define game objects")
theBoard = board()
theItems = []       # array of item() class
ourSnek = snake()
perf = []           # time - list dict

# Register snake 
@app.get("/")
def handle_info():
    print("INFO: Healthcheck - OK")
    return {
        "apiversion": "1",
        "author": "idzol", 
        "color": "#FF00FF",  
        "head": "default",  # TODO: Personalize
        "tail": "default",  # TODO: Personalize
    }


@app.post("/start")
def handle_start():
    data = request.get_json()

    print(f"START {data['game']['id']}")

    # initialise game (theGame)

    # initialise board (theBoard)
    dataBoard = data['board']
    boardWidth = int(dataBoard["width"])
    boardHeight = int(dataBoard["height"])
    theBoard.setDimensions(boardWidth, boardHeight)

    # initialise items (theItems)
    theItems = []

    # initialise our snake (ourSnek)
    ourSnek.__init__()
   
    # initialise other snakes (otherSneks)


    # initalise / reset other vars
    perf = [] 

    return "ok"


@app.post("/move")
def handle_move():
    data = request.get_json()

    # perf.append({['strat_end']:time.time()})

    # update board (theBoard)
    dataBoard = data['board']
    boardWidth = int(dataBoard["width"])
    boardHeight = int(dataBoard["height"])
    theBoard.setDimensions(boardWidth, boardHeight)
    theBoard.updateBoards(data)

    # update items / objects (theItems)
    foods = data['board']['food']
    theItems = []
    for f in foods:
      it = item("food", f) 
      theItems.append(it)

    # update snake (ourSnek) 
    ourSnek.setLocation(data)
    ourSnek.updateStrategy(data) # check strategy 
    
    # TODO: Review state model 
    # if (ourSnek.lastStrategy != ourSnek.strategy): 
    # ourSnek.lastStrategy = ourSnek.strategy
    dest = selectDestination(theBoard, ourSnek, theItems)
    ourSnek.setTarget(dest)

    # decide move 
    move = chooseMove(data, theBoard, ourSnek)
    
    print(f"MOVE: {move}")
    return {"move": move}


@app.post("/end")
def end():
    data = request.get_json()

    print(f"END {data['game']['id']}")
    return "ok"


if __name__ == "__main__":
    logging.getLogger("werkzeug").setLevel(logging.ERROR)
    # ENV == "development" 
    print("INFO: Starting Battlesnake Server...")
    port = int(os.environ.get("PORT", "8080"))
    app.run(host="0.0.0.0", port=port, debug=True)
