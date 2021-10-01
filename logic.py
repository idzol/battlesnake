import random as rand

# from typing import Dict
# import numpy as np
# import pandas as pd

import functions as fn

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
        # target = {'x':x, 'y':y}
        target = [y, x]

    elif (strat == "enlarge"): 
        # Get location of food(s)
        a = sn.getLocation("head")
        
        iname = getClosestItem(bo, its, a, "food")
        it = getItemByName(its, iname)
        target = it.getLocation()
        
        # Find nearest food 
        # getClosestObject
        
        pass 

    elif (strat == "idle"): 
        # health full.  Follow wall  
        pass

        # find closest wall (dijkstra)
        # target = getClosestWall()


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


def chooseMove(bo: board, sn: snake) -> str:
    """
    data: https://docs.battlesnake.com/references/api/sample-move-request
    return: "up", "down", "left" or "right"
    """
    
    pHead = sn.getLocation("head") 
    pDest = sn.getTarget()
    
    print("TARGET")
    print(str(pDest))

    # get route 
    # lRoute = getRouteToTarget(pHead, pDest)
    
    start = pHead
    finish = pDest

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
    move = fn.getDirection(start, pNext)
  
    return move

    # Set route search limit 
    # eg. while(time < 400ms)
  

# ERROR: can't handle if its[] = it (single item)
def getClosestItem(bo, its, loc, t):

    lowest = 100 
    name = ""
    
    # if (t == "food"):
    for it in its:     
      
        itp = it.getLocation()
        d = fn.distanceToPoint(itp, loc)
        
        # print("ITEM:DIST")
        # print(str(d) + ":" + str(it.getName()))

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
