import logging
import os

from logger import log
# import math

from flask import Flask
from flask import request
import copy as copy

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


game = {}  
theBoard = board()
theItems = []          # array of item() class
allSnakes = {}       # dict of snake() class. id:snake
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
    game_id = data['game']['id']
    
    # TODO:  Move to logger (6)
    # log('game-data')
    # 'game-data':[6, "GAME"]
    # print(str(data))
    # return
    
    # print(f"START {data['game']['id']}")
    log("start", data['game']['id'])
    
    # Initialise game (theBoard)
    # TODO: Don't reinitliaise board & clear counters,eg. keep win stats 
    theBoard = board()
    
    # initialise items (theItems)
    theItems = []

    # Initialise our snake (ourSnek)
    allSnakes = {}

    # TODO: Combine ourSnek.__init with data & use reset instead . 
    # ourSnek.reset() -- clear counters, eg. adjust strategy keep win state 
    ourSnek.__init__()
    identity = data['you']['id']
    theBoard.setIdentity(identity)
    ourSnek.setId(identity)
    ourSnek.setType("us")
    allSnakes[copy.copy(identity)] = ourSnek

    # initialise other snakes (otherSneks)
    snakes = data['board']['snakes']
    for sndata in snakes: 
        if sndata['id'] != ourSnek.getId():
          sn = snake() 
          identity = sndata['id']
          sn.setId(identity)
          sn.setType("enemy")
          sn.setEnemy(sndata)
          allSnakes[copy.copy(identity)] = copy.deepcopy(sn)

      # TODO: check if this creates a deep copy, or pointer to same snake (multiple enemies represented as one snake)  

    # initalise / reset other vars
    # log("start-complete", data['game']['id'])
    
    # Save game data
    game[game_id] = [theBoard, ourSnek, allSnakes]

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

    # Load game data (support for multi games)
    data = request.get_json()
    # print(str(data))
    
    game_id = data['game']['id']
    if game_id in game: 
        theBoard = game[game_id][0]
        ourSnek = game[game_id][1]
        allSnakes = game[game_id][2]
    else: 
        # TODO: confirm this works 
        pass 

    log('time', 'Start Move', theBoard.getStartTime())
    turn = data['turn']
    
    # Update board (theBoard) and clear counters 
    theBoard.resetCounters()
    
    # Update items and objects (theItems)
    foods = data['board']['food']
    theItems = []
    for f in foods:
      it = item("food", f) 
      theItems.append(it)

    # Update snake (ourSnek) and save last path 
    ourSnek.setAll(data['you'])
    
    # Update enemy snakes 
    snakes = data['board']['snakes']
    for sndata in snakes: 
        identity = sndata['id']
        if identity != ourSnek.getId():
          allSnakes[identity].setEnemy(sndata)
          # print (str(allSnakes[identity].showStats()))

    # Update predict & threat matrix  
    hazards = data['board']['hazards']
    theBoard.updateBoards(data)
    # TODO:  predictMoves requires updateDijkstra, and vice versa (recursive).  Currently running with blank matrix from updateBoards
    theBoard.predictSnakeMoves(allSnakes, theItems)
    theBoard.updatePredict(allSnakes)
    theBoard.updateThreat(allSnakes, hazards)
    theBoard.updateDijkstra(ourSnek.getHead())

    # Initialisation complete 
    log('time', 'Init complete', theBoard.getStartTime())
    
    # Iterate future snake
    # youFuture = youHead 
    # while(weight < threshold): 

    # Check strategy interrupts     
    checkInterrupts(theBoard, allSnakes)
    
    # Progress state machine, set route
    stateMachine(theBoard, ourSnek, theItems)
    
    # Strategy Complete 
    log('time', 'Strategy complete', theBoard.getStartTime())

    # Translate target to move 
    move = translatePath(theBoard, ourSnek)    
    move = ourSnek.getMove()
    shout = ourSnek.setShout(turn)
    log('time', 'Path complete', theBoard.getStartTime())
    # log('snake-showstats', 'SNAKE', str(ourSnek.showStats()))
    print("SNAKE")
    ourSnek.showStats()
    log("move", move)
    log("shout", shout)

    # Save game data
    game[game_id] = [theBoard, ourSnek, allSnakes]

    log('time', 'Move complete', theBoard.getStartTime())    
    return {"move": move, "shout":shout}
    

@app.post("/end")
def end():
    global theBoard 
    global theItems 
    global ourSnek 
    global codeTime
  
    data = request.get_json()
    
    # Delete game data (TODO:  Dump to log)
    game_id = data['game']['id']
    game[game_id] = None
    
    # print(str(data))
    # if 
    # data['you']['health'] = 0 
    # data['you']['head'] = out of bounds ..  
    # else win ? 
    
    log("end", data['game']['id'])

    return "ok"


if __name__ == "__main__":
    logging.getLogger("werkzeug").setLevel(logging.ERROR)
    # ENV == "development" 
    print("INFO: Starting Battlesnake Server...")
    port = int(os.environ.get("PORT", "8080"))
    app.run(host="0.0.0.0", port=port, debug=True)
