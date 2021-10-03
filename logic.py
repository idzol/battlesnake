import random as rand

# from typing import Dict
# import numpy as np
# import pandas as pd

import functions as fn
from logger import log

import constants as CONST

from snakeClass import snake
from boardClass import board
from itemClass import item


# === STATE MACHINE ===
# Core decision making engine

    # Eat -- focus on maximising snake size and restoring health
    # Attack -- larger size, full health, stay close to head, intercept food, look for kill
    # Kill -- opportunity to kill (eg. head to head collision)
    # Defend -- smaller snake .. 
    # Survive -- limited moves left 
    # .. 
    
# Changes strategy (state machine) based on external influence 
def checkInterrupts(bo:board, sn: snake):

    # global strategy
    health = sn.getHealth() 
    aggro = sn.getAggro()
    threat = sn.getThreat()
    strategy, strategyinfo = sn.getStrategy() 
    interrupt = False

    # Kill interrupt 
    if (killPath(bo, sn)): 
        strategy = ["Kill","Collide"]
        interrupt = True 

    # Survive interuupt 
    elif (numMovesAvailable(bo, sn) < sn.getLength()):
        strategy =["Survive", ""]
        interrupt = True 
        
    # Health interrupt 
    elif (health < CONST.healthLow): 
        strategy = ["Eat",""]
        interrupt = True 
        
    # Attack interrupt 
    elif (aggro > CONST.aggroHigh):
        strategy = ["Attack","Stalk"]
        interrupt = True 
        
    elif (threat > CONST.threatHigh):
        strategy = ["Defend",""] 
        interrupt = True 
        
    if (interrupt):
        log('interrupt', str(strategy))

    return (strategy, strategyinfo)


# Returns target (next move) based on inputs 
def stateMachine(bo:board, sn: snake, its: list): 

    strategy, strategyinfo = sn.getStrategy()
    start = sn.getHead()

    # Progress state machine
    target = []
    
    # print("STATE MACHINE", str(strategy), str(strategyinfo))
    # Wait 
    if(strategy[0]=="Idle"):

        if(strategy[1]==""):
          strategy[1]=="FindWall"
          # target = [0, 0]
          
        # Find nearest wall 
        if(strategy[1]=="FindWall"):
            

            target = bo.findClosestWall(start)
            
            # State transition - Move to crawl wall 
            if(len(target) == 0):
                strategy[1]= "CrawlWall"
                
                direction = int(2 * rand.random())
                if (direction):
                    direction = CONST.clockwise 
                else: 
                    direction = CONST.counterclockwise 

                strategyinfo['direction'] = direction
                strategyinfo['proximity'] = 2
        

        # Track wall clockwise or counterclockwise 
        if(strategy[1]=="CrawlWall"):
        
            d = strategyinfo['direction']
            p = strategyinfo['proximity']
        
            target = trackWall(d, p)
    
    
    # Optimum use of space 
    if(strategy[0]=="Survive"):
        
        # find dijkstras way out .. 
        # .. otherwise slinky pattern until death
        pass 
    
    # ConserveMoves 
    if(strategy[0]=="Kill"):

        if (strategy[1] == "Collide"):
            target = headOnCollision(bo, sn) 
            
            # No kill path no longer exists 
            if(not len(target)): 
                strategy = ["Attack","Stalk"]
            
#         if(numMovesAvailable(enemy) < enemy.getLength()):
#             strategy[1] = "Block"
#             move = blockPath()
#             pass 
             

    if(strategy[0]=="Defend"):
        # d = bo.findDirectionWith(CONST.empty)
        # target = CONST.directionMap['d']
        pass 

    if(strategy[0]=="Attack"):
        
        if(strategy[1]=="Stalk"):
            # find enemy head square
            # stay X squares ahead 
            # wait for kill 
            pass 
        
        
        if(strategy[1]=="Spiral"):
            # find central point of map
            # spiral of death 
            pass 
        
        # Spiral  

    if(strategy[0]=="Eat"): 

        a = sn.getLocation("head")
        iname = getClosestItem(bo, its, a, "food")
        it = getItemByName(its, iname)
        target = it.getLocation()

        # print("EAT")
        # print(str(a), str(iname), str(it), str(target))
        # ** Introduce threat level
       

    # If error with strategy 
    if(len(target) == 0): 
        
        # Reset strategy  
        # Insert random walk 
        strategy = ["Eat","x"]
        # target = random ... 
        # strategy = ["Idle","x"]
        # interrupt = True 
        
    return (target, strategy, strategyinfo)


# TODO:  Consider combining state machine (target) and 

# Check snake target,  return next move 
def translatePath(bo: board, sn: snake) -> str:
    """
    data: https://docs.battlesnake.com/references/api/sample-move-request
    return: "up", "down", "left" or "right"
    """

    start = sn.getHead() 
    finish = sn.getTarget()
    
    log("path-target", str(finish))

    # TODO: Save route to optimise later 
    # eg. Only recalculate every X turns .. 
    # eg. while(time < 400ms)  

    # sn.saveRoute() 
    log('time', 'Before Route', bo.getStartTime())
    path = bo.route(start, finish) 
    if len(path):
      p = path.pop(0)
    else: 
      # No next move - cant route to destination
      # TODO: Change strategy 
      p = finish

    log('time', 'After Route', bo.getStartTime())
    
    # Translate routepoint to direction
    print("DIRN", p) 
    move = fn.getDirection(start, p)
    return move
    log('time', 'After Direction', bo.getStartTime())


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



# STUBS -- strategy functions to be built 

def killPath(bo, sn):
    # if larger than enemy 
    # & dijkstra predict enemy == distance to enemy head
    return False


def headOnCollision(bo, sn):
    # snake predict enemy head 
    # for each enemy head range(0,turns)
    # get distance to prediction 
    # if (distance == futureturns)
    # return killpath 
    return []



def blockPath(bo, sn):
    # find move that will reduce enemy available squares 
    return []


def checkOpenPath(bo, a, b): 
  # route = getPointsInLine(a,b)
  # self.solid dijkstra(route, 100)  
  return True 


def trackWall(bo, sn, rotation=CONST.clockwise, proximity=0):
    
    # bo.board 
    # l = sn.getHead()
    # d = direction  # left, right, up, down
    # r = rotation    # cw, ccw
    # p = proximity  # 0, 1, 2..
  
    # check path in current direction 

    # i = 4 
    # pathNotFound = false 
    # while (pathNotFound and i): 
    #   pt = l + d * (p + 1) 
    #   if (openPath(l, pt)): 
    #     move = d 
    #   i = i - 1
    # else:
    #   d = rotateMove(d, r)
    #   if (openPath(l, pt)): 
    # 
    #  # else (openPath(l, .. if blocked, CONST.up
    # try CONST.up, if blocked CONST.right
    # try CONST.right if blocked CONST.down
    # try CONST.down if blocked CONST left
    
    # if (r = CONST.counterclockwise) 
    # try CONST.left, if blocked, CONST.up
    # try CONST.up, if blocked CONST.right
    # try CONST.right if blocked CONST.down
    # try CONST.down if blocked CONST left

    return []

def numMovesAvailable(bo, sn):
    # while sn.getHead()
    #   markAdjacent() 
    #   total + 1 
    #   recursive   
    return 100
