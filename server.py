import logging
import os

# import math

from flask import Flask
from flask import request
import copy as copy

# move classes to class/snake, class/board... 
from logClass import log
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

    # logger = log()
    # logger.message("healthcheck")
    # logger.print()
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
    global games

    logger = log()

    # clock['start'] = time.time()
    data = request.get_json()
    game_id = data['game']['id']

    # initialise board
    theBoard = board(logger)
    # Initialise snakes
    ourSnek = snake(logger)

    allSnakes = {}       # dict of snake() class. id:snake
    
    logger.message("start", data['game']['id'])
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
          sn = snake(logger) 
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
    logger.print(data)
    return "ok" 


@app.post("/move")
def handle_move():
    global games

    # Load game data (support for multi games)
    data = request.get_json()
    logger = log()
          
    # logdata(data)
    
    game_id = data['game']['id']

    # Support for multiple games 
    # TODO:  Move to stateless 
    if game_id in games: 
        try:
          theBoard = games[game_id]['board']
          ourSnek = games[game_id]['us']
          allSnakes = games[game_id]['snakes']
        
        except Exception as e:
          logger.error('exception', 'server::move', str(e)) 
          theBoard = board(logger)
          ourSnek = snake(logger)
          
    else: 
        # Error - Game ID not found 
        logger.error('exception', 'Game not found: ', game_id)
        return 

 
    theBoard.setLogger(logger)
    ourSnek.setLogger(logger)
    
    # Start clock
    turn = data['turn']
    logger.timer('== Start Move ==') 

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
          logger.error('exception','handle_move',str(e))
          sn = snake() 
          sn.setEnemy(alive)
          aliveSnakes[identity] = copy.deepcopy(sn)
    
    allSnakes = aliveSnakes
    
    # Update predict & threat matrix  
    # TODO:  Review hazard logic & routing
    # hazards = data['board']['hazards']
    theBoard.updateBoards(data, ourSnek, allSnakes, theFoods)
    logger.timer('updateChance')
    theBoard.updateChance(allSnakes, theFoods)
    logger.timer('updateMarkov')
    theBoard.updateMarkov(ourSnek, allSnakes, theFoods)
    logger.timer('updateDijkstra')
    theBoard.updateDijkstra(ourSnek)
    logger.timer('updateGradient')
    theBoard.updateGradient(ourSnek.getHead()) 
    theBoard.updateGradientFix(ourSnek.getHead())
    
    # BUGFIX: Prevent snake from "seeing through" themselves in predict matrix in a future turn.  Needs to be applied after updateGradient complete .. 
       
    # Initialisation complete 
    logger.timer('== Init complete ==')
    
    # Iterate future snake
    # youFuture = youHead 
    # while(weight < threshold): 

    # Check strategy interrupts     
    logger.timer('checkInterrupts')
    checkInterrupts(theBoard, ourSnek, allSnakes)
    
    logger.timer('stateMachine')
    # Progress state machine, set route
    stateMachine(theBoard, ourSnek, allSnakes, theFoods)
    
    # Strategy Complete 
    logger.timer('== Strategy complete ==')

    # Translate target to move 
    logger.timer('makeMove')
    move = makeMove(theBoard, ourSnek, allSnakes)    
    move = ourSnek.getMove()
    shout = ourSnek.setShout(turn)
    logger.timer('Path complete')
   
    logger.message("move", move)
    logger.message("shout", shout)

    # Print maps to console 
    ourSnek.showStats()
    theBoard.showMaps()

    # Save game data
    # games[game_id] = [theBoard, ourSnek, allSnakes]
    
    for key in allSnakes:
        snk = allSnakes[key]
        logger.log('snakes', snk.getName(), snk.getHead(), snk.getLength(), snk.getDirection(), snk.getEating())

    logger.timer('== Move complete ==')
    logger.print(data)
    
    return {"move": move, "shout":shout}
    

@app.post("/end")
def end():
    global games
    data = request.get_json()

    logger = log()

    # Delete game data 
    game_id = data['game']['id']
    games.pop(game_id, None)
    
    logger.message('end', data['game']['id'])
    logger.print(data)
    logger.end(data)
    
    return "ok"


if __name__ == "__main__":
    logging.getLogger("werkzeug").setLevel(logging.ERROR)
    # ENV == "development" 
    print("INFO: Starting Battlesnake Server...")
    port = int(os.environ.get("PORT", "8080"))
    app.run(host="0.0.0.0", port=port, debug=True)

