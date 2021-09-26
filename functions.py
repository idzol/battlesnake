import random as rand
from typing import Dict
# import numpy as np
# import pandas as pd

from snakeClass import snake
from boardClass import board
from itemClass import item

def selectDestination(bo: board, sn: snake, its: item):  # b = board(), s = strategy 

    target = {} 
    strat = sn.getStrategy()
        
# perf.append({['strat_start']:time.time()})

    if (strat == "random"):
        # Get dimensions of the board 
        # Select a random x/y 
        x = int(bo.width * rand.random()) 
        y = int(bo.height * rand.random()) 
        target = {'x':x, 'y':y}

    elif (strat == "enlarge"): 
        # Get location of food(s)
        a = bo.XYToLoc(sn.getLocation("head"))
        iname = getClosestItem(bo, its, a, "food")
        it = getItemByName(its, iname)
        target = bo.XYToLoc(it.getLocation())
        
        # Find nearest food 
        # getClosestObject
        
        pass 

    elif (strat == "eat"): 
        # same as enlarge but driven by hunger 
        pass

    elif (strat == "attack"): 
        # if opportunity to end game  
        pass

    elif (strat == "defend"): 
        # if opponent acting aggressive 
        pass 

    elif (strat == "stalk"): 
        # stay close to enemy 
        pass 

    else:
        pass 

    # perf.append({['strat_end']:time.time()})

    return target


def chooseMove(data: dict, bo: board, sn: snake) -> str:
    """
    data: https://docs.battlesnake.com/references/api/sample-move-request
    return: "up", "down", "left" or "right"
    """
    
    pHead = data['you']['head']
    pDest = sn.getTarget()
    print("TARGET")
    print(str(bo.XYToLoc(pDest)))

    # get route 
    # lRoute = getRouteToTarget(pHead, pDest)
    
    start = bo.XYToLoc(pHead)
    finish = bo.XYToLoc(pDest)

    lRoute = bo.findBestPath(start, finish) 
    # TODO: Save route to optimise later 
    # eg. Recalculate every X turns .. 
    # sn.saveRoute() 

    if len(lRoute):
      pNext = lRoute.pop(0)

    else: 
      # No next move -- shouldn't happen
      # TODO: insert random walk ... 
      pNext = finish

    # Translate routepoint to direction 
    move = getDirection(start, pNext)
  
    return move

    # Set route search limit 
    # eg. while(time < 400ms)
    

# move = getMove(pHead, route.pop(0)) 
def getDirection(a, b): 
    
    move = ""

    # X - left, right [0][X]
    # Y - up, down.   [Y][0] 

    ay = a[0]
    ax = a[1]
    by = b[0]
    bx = b[1]
    
    if (bx < ax): 
        move = "left"
    if (bx > ax): 
        move = "right"
    if (by < ay): 
        move = "up"
    if (by > ay): 
        move = "down"

    if (move == ""): 
        # Should never happen 
        moves = ["right", "left", "up", "down"]
        move = rand.choice(moves)
    
    return move


def comparePoints(a: Dict[str, int], b: Dict[str, int]): 

    if(a['x'] == b['x'] and a['y'] == b['y']):
        return True
    else:
        return False 


def getClosestItem(bo, its, loc, t):

    lowest = 100 
    name = ""
    
    if (t == "food"):
       for it in its:     
            # print (it)
            
            itp = bo.XYToLoc(it.getLocation())
            d = distanceToPoint(itp, loc)
            if (d < lowest):
                lowest = d 
                name = it.getName()
                # TODO: if two of same dist, returns top left. do we want to change / randomise this? 

    return name


def getItemByName(its, name):

  for it in its: 
      if it.getName() == name:
        return it 

  return {}

def distanceToPoint(a, b):
  
    d = 0
    try:
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        d = dx + dy
    except: 
        d = -1 
        
    return d
    
# def isSamePoint(a: Dict[str, int], b: Dict[str, int])

def chartPath(b, p):    # b = board(), p = point(x,y)
    pass
    
def setPath():
    pass 

## Load game data 
def initialise_snake(data: dict) -> str:
    pass 


def raiseError(e):
    # error_status = True 
    # error_text = e
    print("ERROR: " + str(e))
    return True

