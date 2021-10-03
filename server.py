import logging
import os

from logger import log
# import math

from flask import Flask
from flask import request

# move classes to class/snake, class/board... 
from snakeClass import snake
from boardClass import board
from itemClass import item

from logic import checkInterrupts, stateMachine,translatePath

app = Flask(__name__)

# Globals 
global theBoard 
global theItems 
global ourSnek 
global codeTime

theBoard = board()
theItems = []          # array of item() class
ourSnek = snake()
clock = {}           # time - dict

# Register snake 
@app.get("/")
def handle_info():
    log("healthcheck")
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

    # clock['start'] = time.time()
    data = request.get_json()

    # print(f"START {data['game']['id']}")
    log("start", data['game']['id'])
    
    # initialise game (theGame)
    
    # initialise board (theBoard)
    theBoard = board()
    
    # initialise items (theItems)
    theItems = []

    # (re)initialise our snake (ourSnek)
    ourSnek.__init__()
     
    # initialise other snakes (otherSneks)

    # initalise / reset other vars
    # clock['init'] = time.time()
    
    return "ok" 


@app.post("/move")
def handle_move():
    global theBoard 
    global theItems 
    global ourSnek 
    global codeTime  

    theBoard.setStartTime()

    # Start clock
    data = request.get_json()
    log('time', 'Start Move', theBoard.getStartTime())

    # Update board (theBoard)
    width = int(data['board']['width'])
    height = int(data['board']['height'])
    theBoard.setDimensions(width, height)
    theBoard.updateBoards(data)

    turn = int(data['turn'])
    
    # Update items / objects (theItems)
    foods = data['board']['food']
    theItems = []
    for f in foods:
      it = item("food", f) 
      theItems.append(it)

    # Update snake (ourSnek) 
    ourSnek.setAll(data)

    # Initialisation complete 
    log('time', 'Init complete', theBoard.getStartTime())
    
    # Check interrupts     
    strat, stratinfo = checkInterrupts(theBoard, ourSnek)
    ourSnek.setStrategy(strat, stratinfo) # check 

    # Progress state machine & return target
    move, strat, stratinfo = stateMachine(theBoard, ourSnek, theItems)
    ourSnek.setStrategy(strat, stratinfo) # check   
    # Default strategy if no route found  
    # if (move == []):
    #   try different strategy 
    # 
    ourSnek.setTarget(move)
    log('time', 'Strategy complete', theBoard.getStartTime())

    # Strategy Complete 

    # Translate target to move 
    move = translatePath(theBoard, ourSnek)
    shout = ourSnek.setShout(turn)
    log('time', 'Path complete', theBoard.getStartTime())

    # log("strategy", ourSnek.showStats())
    print("SNAKE")
    ourSnek.showStats()
    log("move", move)
    log("shout", shout)

    log('time', 'Move complete', theBoard.getStartTime())    
    return {"move": move, "shout":shout}


@app.post("/end")
def end():
    global theBoard 
    global theItems 
    global ourSnek 
    global codeTime
  
    data = request.get_json()

    log("end", data['game']['id'])

    return "ok"


if __name__ == "__main__":
    logging.getLogger("werkzeug").setLevel(logging.ERROR)
    # ENV == "development" 
    print("INFO: Starting Battlesnake Server...")
    port = int(os.environ.get("PORT", "8080"))
    app.run(host="0.0.0.0", port=port, debug=True)
