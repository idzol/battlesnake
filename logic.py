import random as rand

# from typing import Dict
# import numpy as np
# import pandas as pd
import time as time 
import copy as copy 

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
    
    # Progress state machine
    target = []
    
    # print("STATE MACHINE", str(strategy), str(strategyinfo))
    i = 0
    while not len(target):
      # ConserveMoves 
      start = copy.copy(sn.getHead())
      print("H1",str(sn.getHead()))
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

          # No food -- change strategy
          if(not len(its)):
            strategy = ["Idle","FindWall"]
          
          else: 
            a = sn.getLocation("head")
            iname = getClosestItem(bo, its, a, "food")
            it = getItemByName(its, iname)
            target = it.getLocation()
            # TODO: Introduce threat level or and dead end prediction .. 

          # log('strategy-eat', str(a), str(iname), str(it), str(target))
        
      if(strategy[0]=="Idle"):

        # Default
        if(strategy[1]==""):
          strategy[1]=="FindWall"
          
        # Find nearest wall 
        if(strategy[1]=="FindWall"):   
            target = bo.findClosestWall(start)
            log('strategy-findwall', target)

        # Track wall - clockwise or counterclockwise 
        if(strategy[1]=="CrawlWall"): 
            r = strategyinfo['rotation']
            p = strategyinfo['proximity']
            target = trackWall(bo, sn, r, p)
    
        print("H2",str(sn.getHead()))
          
      # Optimum use of space 
      if(strategy[0]=="Survive"):   
          # find dijkstras way out .. 
          # .. otherwise slinky pattern until death
          pass 
      
      # NO TARGET -- previous strategy complete (or could not be completed)
      if(len(target) == 0): 
          print("H3",str(sn.getHead()))
          # State transition - Move to crawl wall 
          if (strategy[1] == "FindWall"): 
            strategy[1] = "CrawlWall"                
            # TODO: Move to high/low threat based on aggro

            rotation = int(2 * rand.random())
            if (rotation):
                rotation = CONST.clockwise 
            else: 
                rotation = CONST.counterclockwise 

            strategyinfo['rotation'] = rotation
            strategyinfo['proximity'] = 2
          
          else:
            strategy = ["Eat","x"]

          # Check if time exceeds limit 
          st = bo.getStartTime()
          diff = 1000 * (time.time() - st)
          if diff > CONST.timePanic: 
              log('timer-hurry')
              bo.hurry = True

          log('time','Strategy updated', st)
          log('strategy-iterate', str(strategy))

  
      if (i > CONST.strategyDepth or bo.hurry):
          # Exit loop
          target = [0, 0]
          break
          # log('strategyInsert random walk 
          # target = random ... 
          # interrupt = True 
    
      i = i + 1 

    print("H4",str(sn.getHead()))    
    return (target, strategy, strategyinfo)


# TODO:  Consider combining state machine (target) and 

# Check snake target,  return next move 
def translatePath(bo: board, sn: snake) -> str:
    """
    data: https://docs.battlesnake.com/references/api/sample-move-request
    return: "up", "down", "left" or "right"
    """
    
    start = copy.copy(sn.getHead())
    finish = copy.copy(sn.getTarget())
    
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
    
    w = bo.getWidth()
    h = bo.getHeight()
    a = sn.getHead() # [0,0] 
    d = sn.getDirection()  # left, right, up, down
    
    # Coordinates - start [ay, ax]
    ax = a[1]
    ay = a[0]
    a1 = [0] * 2

    r = rotation    # cw, ccw
    p = proximity   # 0, 1, 2..

    
    # TODO:  Update for proximity (ie. X squares away from)
    # Check path in current direction
    
    for i in range(0, 4):
        # Add one point in current direction 
        a1[0] = ay + CONST.directionMap[d][0]
        a1[1] = ax + CONST.directionMap[d][1]
        
        # No collision & in bounds 
        print("TRACK-DIRN", str(a), str(a1), d)
        if( 0 <= a1[0] < w and 0 <= a1[1] < h):
            if (bo.solid[a1[0], a1[1]] == 0):
              print("TRACK-SOLID", str(bo.solid[a1[0], a1[1]]))
              break
        
        # Rotate direction & try again 
        if(r == CONST.counterclockwise): 
            d = CONST.ccwMap[d] 
        else:
            d = CONST.cwMap[d]

#     else:
#       d = rotateMove(d, r)
#       if (openPath(l, pt)): 
    
    log('strategy-trackwall', str(w), str(h), str(a), str(d), str(r), str(p), str(a1))
    return a1
  

def numMovesAvailable(bo, sn):
    # while sn.getHead()
    #   markAdjacent() 
    #   total + 1 
    #   recursive   
    return 100
