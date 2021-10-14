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

from logic import checkInterrupts, stateMachine, makeMove

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

    log('time', '== Start Move ==', theBoard.getStartTime())
    turn = data['turn']
    
    # Update board (theBoard) and clear counters 
    theBoard.resetCounters()
    
    # Update items and objects (theItems)
    foods = data['board']['food']
    theItems = []
    for f in foods:
      it = item("food", f) 
      theItems.append(it)

    # Refresh enemy snakes. Remove dead sneks
    snakes = data['board']['snakes']

    aliveSnakes = {}
    for alive in snakes:
      identity = alive['id']
      if (identity == ourSnek.getId()):
        # We are alive! 
        ourSnek.setAll(data['you'])
        aliveSnakes[identity] = ourSnek
    
      else:
        try: 
          # Enemy snake alive 
          aliveSnakes[identity] = allSnakes[identity]
          aliveSnakes[identity].setEnemy(alive)
          
        except Exception as e:
          # Create new snake -- shouldn't happen .. 
          log('exception','handle_move',str(e))
          sn = snake() 
          sn.setEnemy(alive)
          aliveSnakes[identity] = copy.deepcopy(sn)
    
    allSnakes = aliveSnakes
  

    # Update predict & threat matrix  
    hazards = data['board']['hazards']
    theBoard.updateBoards(data)
    log('time', 'predictSnakeMoves', theBoard.getStartTime())
    
    theBoard.predictSnakeMoves(allSnakes, theItems)
    
    # Initialise routing gradient 
    log('time', 'updatePredict', theBoard.getStartTime())
    theBoard.updatePredict(allSnakes)
    log('time', 'updateThreat', theBoard.getStartTime())
    theBoard.updateThreat(allSnakes, hazards)
    log('time', 'updateDijkstra', theBoard.getStartTime())
    theBoard.updateDijkstra(ourSnek)
    log('time', 'updateGradient', theBoard.getStartTime())
    theBoard.updateGradient(ourSnek.getHead()) 
    theBoard.updateGradientFix(ourSnek.getHead())
    # BUGFIX: Prevent snake from "seeing through" themselves in predict matrix in a future turn.  Needs to be applied after updateGradient complete .. 
       
    # Initialisation complete 
    log('time', '== Init complete ==', theBoard.getStartTime())
    
    # Iterate future snake
    # youFuture = youHead 
    # while(weight < threshold): 

    # Check strategy interrupts     
    log('time', 'checkInterrupts', theBoard.getStartTime())
    checkInterrupts(theBoard, allSnakes)
    
    log('time', 'stateMachine', theBoard.getStartTime())
    # Progress state machine, set route
    stateMachine(theBoard, ourSnek, theItems)
    
    # Strategy Complete 
    log('time', '== Strategy complete ==', theBoard.getStartTime())

    # Translate target to move 
    log('time', 'makeMove', theBoard.getStartTime())
    move = makeMove(theBoard, ourSnek)    
    move = ourSnek.getMove()
    shout = ourSnek.setShout(turn)
    log('time', 'Path complete', theBoard.getStartTime())
   
    print("SNAKE")
    ourSnek.showStats()
    log("move", move)
    log("shout", shout)

    # Print maps to console 
    theBoard.showMaps()

    # Save game data
    game[game_id] = [theBoard, ourSnek, allSnakes]
    
    # for key in allSnakes:
    #     snk = allSnakes[key]
    #     print("SNAKES", snk.getName(), snk.getHead(), snk.getLength())

    log('time', '== Move complete ==', theBoard.getStartTime())  
    
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
