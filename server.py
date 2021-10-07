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
global allSnakes

theBoard = board()
theItems = []          # array of item() class
allSnakes = []       # array of snake() class
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
    global allSnakes
    global codeTime

    # clock['start'] = time.time()
    data = request.get_json()

    # print(f"START {data['game']['id']}")
    log("start", data['game']['id'])
    
    # Initialise game (theBoard)
    # TODO: Don't reinitliaise board & clear counters,eg. keep win stats 
    theBoard = board()
    
    # initialise items (theItems)
    theItems = []

    # Initialise our snake (ourSnek)
    allSnakes = []

    # TODO: Combine ourSnek.__init with data)
    # ourSnek.reset() -- clear counters, eg. adjust strategy keep win state 
    ourSnek.__init__()
    ourSnek.id = data['you']['id']
    ourSnek.setType("us")
    allSnakes.append(ourSnek)
    
    # initialise other snakes (otherSneks)
    snakes = data['board']['snakes']
    for sndata in snakes: 
        if sndata['id'] != data['you']['id']:
          sn = snake() 
          sn.setType("enemy")
          allSnakes.append(sn)
    
      # TODO: check if this creates a deep copy, or pointer to same snake (multiple enemies represented as one snake)  

    # initalise / reset other vars
    # log("start-complete", data['game']['id'])
    
    return "ok" 


@app.post("/move")
def handle_move():
    global theBoard 
    global theItems 
    global ourSnek 
    global allSnakes
    global codeTime  

    # Start clock
    theBoard.setStartTime()
    data = request.get_json()
    log('time', 'Start Move', theBoard.getStartTime())
    turn = data['turn']
    
    # Update board (theBoard)
    theBoard.resetCounters()
    theBoard.updateBoards(data)
    
    # Update items / objects (theItems)
    foods = data['board']['food']
    theItems = []
    for f in foods:
      it = item("food", f) 
      theItems.append(it)

    # Update snake (ourSnek) 
    ourSnek.setAll(data)

    # Update enemy snakes 
    theBoard.updatePredict(allSnakes)
    theBoard.predictSnakeMoves(allSnakes, theItems)

    # Initialisation complete 
    log('time', 'Init complete', theBoard.getStartTime())
    
    # Check interrupts     
    checkInterrupts(theBoard, ourSnek)
    
    # Progress state machine & return target
    stateMachine(theBoard, ourSnek, theItems)
    
    log('time', 'Strategy complete', theBoard.getStartTime())

    # Strategy Complete 

    # Translate target to move 
    move = translatePath(theBoard, ourSnek)
    
    move = ourSnek.getDirection()
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
