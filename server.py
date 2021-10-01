import logging
import os

import time
# import math

from flask import Flask
from flask import request

# move classes to class/snake, class/board... 
from snakeClass import snake
from boardClass import board
from itemClass import item

from logic import selectDestination, chooseMove

app = Flask(__name__)

# Globals 
# TODO:  Understand scope of these items..
print("GLOBAL: Define game objects")

global theBoard 
global theItems 
global ourSnek 
global codeTime

# theBoard = board()
theItems = []          # array of item() class
ourSnek = snake()
codeTime = {}           # time - dict

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
    global theBoard 
    global theItems 
    global ourSnek 
    global codeTime

    # perf['start'] = time.time()
    data = request.get_json()

    print(f"START {data['game']['id']}")

    # initialise game (theGame)
    
    # initialise board (theBoard)
    theBoard = board()
    
    # initialise items (theItems)
    theItems = []

    # (re)initialise our snake (ourSnek)
    ourSnek.__init__()
   
    # initialise other snakes (otherSneks)

    # initalise / reset other vars
    # perf['init'] = time.time()
    
    return "ok"


@app.post("/move")
def handle_move():
    global theBoard 
    global theItems 
    global ourSnek 
    global codeTime  

    # perf['move'] = time.time()
    data = request.get_json()

    # perf.append({['strat_end']:time.time()})

    # update board (theBoard)
    dataBoard = data['board']
    boardWidth = int(dataBoard['width'])
    boardHeight = int(dataBoard['height'])
    theBoard.setDimensions(boardWidth, boardHeight)
    theBoard.updateBoards(data)

    turn = int(data['turn'])
    
    # update items / objects (theItems)
    foods = data['board']['food']
    theItems = []
  
    for f in foods:
      it = item("food", f) 
      theItems.append(it)

    # perf['move_init'] = time.time()
  
    # update snake (ourSnek) 
    ourSnek.setLocation(data)
    ourSnek.updateStrategy(data) # check strategy 
    
    # TODO: Review state model 
    # if (ourSnek.lastStrategy != ourSnek.strategy): 
    # ourSnek.lastStrategy = ourSnek.strategy
    dest = selectDestination(theBoard, ourSnek, theItems)
    ourSnek.setTarget(dest)

    # decide move 
    move = chooseMove(theBoard, ourSnek)
    
    # perf['move_choose'] = time.time()
    
    shout = ourSnek.setShout(turn)

    print(f"MOVE: {move}")
    print(f"SHOUT: {shout}")
    
    return {"move": move,"shout":shout}
    # return {'move': move, 'shout': shout}
  

@app.post("/end")
def end():
    global theBoard 
    global theItems 
    global ourSnek 
    global codeTime
  
    data = request.get_json()

    print(f"END {data['game']['id']}")
    return "ok"


if __name__ == "__main__":
    logging.getLogger("werkzeug").setLevel(logging.ERROR)
    # ENV == "development" 
    print("INFO: Starting Battlesnake Server...")
    port = int(os.environ.get("PORT", "8080"))
    app.run(host="0.0.0.0", port=port, debug=True)
