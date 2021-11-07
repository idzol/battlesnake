import logging
import os
import signal
# import psutil
        
# import math

from flask import Flask
from flask import request
import copy as copy

# move classes to class/snake, class/board... 
from logClass import log
from snakeClass import snake
from boardClass import board


from logic import checkEnemy, enemyInterrupts, checkInterrupts, stateMachine, makeMove

app = Flask(__name__)


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

    logger = log()

    # clock['start'] = time.time()
    data = request.get_json()
    game_id = data['game']['id']

    players = []
    # print(data)
    for snake in data['board']['snakes']:
        player = snake['name']
        players.append(player)

    if len(players) == 2:
        mode = 'duel'
    else:
        mode = 'arena'

    # Print game ID, players & mode
    logger.message("start", game_id)
    logger.message("start-players", players)
    logger.message("start-mode", mode)

    logger.print(data)

    return "ok" 


@app.post("/move")
def handle_move(testData="", testOverride=False):

    if testData:
        data = copy.copy(testData)
        debug = True
    else:
        data = request.get_json()
        debug = False 
    
    logger = log(testOverride)
          
    # logdata(data)
    
    game_id = data['game']['id']
       
    theBoard = board(logger)
    ourSnek = snake(logger)
    
    # Start clock
    turn = data['turn']
    logger.timer('== Start Move ==') 

    identity = data['you']['id']
    theBoard.setIdentity(identity)

    # Set food objects 
    theFoods = []
    foods = data['board']['food']
    for f in foods:
      food = [f['y'], f['x']]
      theFoods.append(food)

    theHazards = []
    hazards = data['board']['hazards']
    for h in hazards:
      hazard = [f['y'], f['x']]
      theHazards.append(hazard)

    # Set our snake 
    ourSnek.setAll(data['you'])
    ourSnek.setId(identity)
    ourSnek.setType("us")
        
    # Set all snakes
    allSnakes = {} 
    snakes = data['board']['snakes']
    
    for alive in snakes:
      identity = alive['id']
      if (identity == ourSnek.getId()):
        # We are alive! 
        allSnakes[identity] = ourSnek

      else:
        # Enemy snake alive 
        allSnakes[identity] = snake(logger)
        allSnakes[identity].setId(identity)
        allSnakes[identity].setType("enemy")
        allSnakes[identity].setEnemy(alive)

    # Update routing boards
    theBoard.updateBoards(data, ourSnek, allSnakes, theFoods, theHazards)
    logger.timer('updateChance')

    # == DEPRECATE | CONFLICTS with statemachine == 
    # checkEnemy(theBoard, ourSnek, allSnakes)

    # if ('speed' in game_type):
    # else:

    # Apply state machine to all enemy snakes 
    logger.timer('stateMachineEnemy')
    for sid in allSnakes:
        snek = allSnakes[sid]
        if (snek != ourSnek):
            logger.timer('updateEnemyBest')
            theBoard.updateBest(snek.getHead())
            
            silent = copy.copy(logger.silent) 
            logger.silent = True        # Supress enemy updates
            logger.timer('updateEnemyInterrupts')
            enemyInterrupts(theBoard, snek, allSnakes)
            # AllSnakes updated with setRoute()
            logger.timer('updatesEnemyStateMachine')
            stateMachine(theBoard, snek, allSnakes, theFoods, enemy=True)
            # print("ENEMY ROUTE", snek.getRoute())
            logger.silent = silent 

    # Adjust boards for enemy moves 
    logger.timer('updateBoardsEnemy')
    theBoard.updateBoardsEnemyMoves(allSnakes)

    # Chance board -- handled in updateBoards
    # logger.timer('updateChance')
    # theBoard.updateChance(allSnakes, theFoods)

    # Update our routing board  
    logger.timer('updateBest')
    theBoard.updateBest(ourSnek.getHead())

    # Check strategy interrupts     
    logger.timer('checkInterrupts')
    checkInterrupts(theBoard, ourSnek, allSnakes)
    
    logger.timer('stateMachineEnemyUs')
    # Progress state machine for our snake
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

    # Save game data
    # games[game_id] = [theBoard, ourSnek, allSnakes]
    
    # Fork reporting (non blocking to server response )
    newpid = os.fork()
    if newpid == 0:
        # p = psutil.Process(newpid.getpid())
        # p.set_nice(10)
        reporting(logger, theBoard, ourSnek, allSnakes, data)

    logger.timer('== Move complete ==')    
    return {"move": move, "shout":shout}
    

@app.post("/end")
def end():

    data = request.get_json()

    logger = log()

    game_id = data['game']['id']
    logger.message('end', game_id)
    
    # Print log info
    logger.print(data)

    # Print win/loss       
    # TODO:  Align CONST.snakename to URL (play.battlesnake.com).  Include as variable in deployment string 
    # idzol         .. prod URL
    # idzol cloud   .. cloud run URL1 
    # idzol cloud   .. cloud run URL2  
    # idzol dev     .. Replit URL
    # etc..

    logger.end(data)
    
    return "ok"


def reporting(logger, board, us, snakes, data):
    # Reporting thread
    # Print log info
    us.showStats()
    board.showMaps()
    board.showMapsFuture(snakes)

    for key in snakes:
        snk = snakes[key]
        logger.log('snakes', snk.getName(), snk.getHead(), snk.getLength(), snk.getDirection(), snk.getEating())
    logger.print(data)
    logger.dump(data)
    # print('MOVE: Reporting complete')

    # Kill PID 
    # my_pid = os.getpid()
    # os.kill(my_pid, signal.SIGINT)
    os._exit(0)  


if __name__ == "__main__":
    logging.getLogger("werkzeug").setLevel(logging.ERROR)
    # ENV == "development" 
    print("INFO: Starting Battlesnake Server...")
    port = int(os.environ.get("PORT", "8080"))
    app.run(host="0.0.0.0", port=port, debug=True)

