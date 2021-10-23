import logging
import os

from logger import log, logdata
# import math

from flask import Flask
from flask import request
import copy as copy

# move classes to class/snake, class/board... 
from snakeClass import snake
from boardClass import board

from logic import checkInterrupts, stateMachine, makeMove

app = Flask(__name__)

# Globals 
global games
games = {}  


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
    global games

    # clock['start'] = time.time()
    data = request.get_json()
    game_id = data['game']['id']

    # initialise board
    theBoard = board()
    # Initialise snakes
    ourSnek = snake()
    allSnakes = {}       # dict of snake() class. id:snake
    # initialise food 
    theFoods = []

    log("start", data['game']['id'])
    # print(str(data))
    
    # Set our identity 
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

    # TODO:  Reset counters every turn, every game 
    # log("start-complete", data['game']['id'])
    
    # Save game data
    games[game_id] = [theBoard, ourSnek, allSnakes]

    # Initialise game 
    games[game_id] = {
        'board':theBoard,
        'us':ourSnek,
        'snakes':allSnakes
        # 'foods':theFoods
    }

    return "ok" 


@app.post("/move")
def handle_move():
    global games

    # Load game data (support for multi games)
    data = request.get_json()
    logdata(data)
    
    game_id = data['game']['id']
    # Support for multiple games 
    if game_id in games: 
        try:
          theBoard = games[game_id]['board']
          ourSnek = games[game_id]['us']
          allSnakes = games[game_id]['snakes']
        
        except Exception as e:
          log('exception', 'server::move', str(e)) 
          theBoard = board()
          ourSnek = snake()
          
    else: 
        # Error - Game ID not found 
        log('exception', 'Game not found: ', game_id)
        return 
        
    # Start clock
    theBoard.setStartTime()

    turn = data['turn']
    log('move-start', game_id, turn)
    log('time', '== Start Move ==', theBoard.getStartTime())

    # FIX: disappearing identity ..  KeyError: ''
    identity = data['you']['id']
    theBoard.setIdentity(identity)
    

    # Update board (theBoard) and clear counters 
    theBoard.resetCounters()

    # Update food objects 
    foods = data['board']['food']
    # food_lastturn = copy.copy(theFoods)
    theFoods = []
    for f in foods:
      food = [f['y'], f['x']]
      theFoods.append(food)

    # Refresh enemy snakes. Remove dead sneks
    snakes = data['board']['snakes']
    ourSnek.setAll(data['you'])
        
    aliveSnakes = {}
    for alive in snakes:
      identity = alive['id']
      if (identity == ourSnek.getId()):
        # We are alive! 
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
    # TODO:  Review hazard logic & routing
    # hazards = data['board']['hazards']
    theBoard.updateBoards(data, ourSnek, allSnakes, theFoods)
    log('time', 'updateChance', theBoard.getStartTime())
    theBoard.updateChance(allSnakes, theFoods)
    log('time', 'updateMarkov', theBoard.getStartTime())
    theBoard.updateMarkov(ourSnek, allSnakes, theFoods)
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
    checkInterrupts(theBoard, ourSnek, allSnakes)
    
    log('time', 'stateMachine', theBoard.getStartTime())
    # Progress state machine, set route
    stateMachine(theBoard, ourSnek, allSnakes, theFoods)
    
    # Strategy Complete 
    log('time', '== Strategy complete ==', theBoard.getStartTime())

    # Translate target to move 
    log('time', 'makeMove', theBoard.getStartTime())
    move = makeMove(theBoard, ourSnek)    
    move = ourSnek.getMove()
    shout = ourSnek.setShout(turn)
    log('time', 'Path complete', theBoard.getStartTime())
   
    print("SNAKE")
    log("move", move)
    log("shout", shout)

    # Print maps to console 
    ourSnek.showStats()
    theBoard.showMaps()

    # Save game data
    # games[game_id] = [theBoard, ourSnek, allSnakes]
    
    for key in allSnakes:
        snk = allSnakes[key]
        print("SNAKES", snk.getName(), snk.getHead(), snk.getLength(), snk.getDirection(), snk.getEating())

    log('time', '== Move complete ==', theBoard.getStartTime())  
    
    return {"move": move, "shout":shout}
    

@app.post("/end")
def end():
    global games
    data = request.get_json()

    # TODO: Dump game data to log. Record win / loss 
    
    # Delete game data 
    game_id = data['game']['id']
    games.pop(game_id, None)
    
    log("end", data['game']['id'])
    return "ok"


if __name__ == "__main__":
    logging.getLogger("werkzeug").setLevel(logging.ERROR)
    # ENV == "development" 
    print("INFO: Starting Battlesnake Server...")
    port = int(os.environ.get("PORT", "8080"))
    app.run(host="0.0.0.0", port=port, debug=True)

