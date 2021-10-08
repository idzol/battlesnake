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
def checkInterrupts(bo:board, snakes):

    # Return your snake 
    you = bo.getIdentity()
    sn = snakes[you]
    health = sn.getHealth() 
    aggro = sn.getAggro()
    threat = sn.getThreat()
    strategy, strategyinfo = sn.getStrategy() 
    interrupt = False

    # Kill interrupt 
    if (killPath(bo, snakes)):     
        strategy = ['Kill', 'Collide']
        interrupt = True 

    elif (largestSnake(bo, snakes) and health > CONST.healthMed):
        strategy = ['Control', 'Centre']
        strategyinfo['default'] = ['Idle', 'Centre']

    # Collision & enemy alrger
    elif (threatPath(bo,sn)): 
        strategy = ["Survive",""]
        interrupt = True 

    # Survive interuupt 
    elif (numMovesAvailable(bo, sn) < sn.getLength()):
        strategy =["Survive", ""]
        interrupt = True 
      
    # No threats, conserve space (Challenge mode) 
    elif (health > CONST.healthHigh): 
        # TODO:  Check for threats (ie enemy snakes)
        strategy = ["Idle","FindWall"]
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

    sn.setStrategy(strategy, strategyinfo) 
    # return (strategy, strategyinfo)


# Returns target (next move) based on inputs 
def stateMachine(bo:board, sn: snake, its: list): 

    strategy, strategyinfo = sn.getStrategy()
    start = sn.getHead()
    if 'default' in strategyinfo:
      defaultstrategy = strategyinfo['default']
    else:
      defaultstrategy = ['Idle', '']
  
    # Progress state machine
    target = []
    route = [] 
    
    # log('state-machine-start', str(strategy), str(strategyinfo))
    
    i = 0
    while not len(target):
      # ConserveMoves 
      # start = copy.copy(sn.getHead())
      
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

      if(strategy[0]=="Control"):
          pass 
          if (strategy[1]=="Centre"): 
            pass 
            # patrol('top') 
            # if reacehd bottom or weight > threshold
            
            # patrol('bottom')
            # if reacehd bottom or weight > threshold
            # strategy-info('control-line') = path (last w moves) 

            # patrol ('loop')
            # loop back to top via food 

            # OTHER: sync with other snake, stay two moves ahead.. 
          
          # def patrol('top'):
          #   find enemy snake 
          #   push in enemy snake direction (eg. right) 
          #.  check if safe to do so 
          #.  loop around to lef 
          #    push (right)
          #    one square for each len > w 

          # if not front line 
          #  find food (eg. left
          #  loop back to start (eg. top to bottom)

          # if area control lost 
          #  snake crosses area control line 
          #  strategy = defaultstrategy 


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
            strategy = defaultstrategy
          
          else: 
            # TODO: Can also eliminate food here.  Boolean allowed (board & items).  Further note -- routing better as it accomodates future path 

            # Get closest item 
            it = bo.getClosestItem(its, start, "food")
            # Get route to target  
            target = it.getLocation()

            print("FINISH", str(target))
            route = bo.route(start, target)

            # If no route to target ..
            if(not len(route)):
            # .. then default strategy 
              strategy = defaultstrategy

            # TODO: Introduce threat level to "allowed" or "gradient" (route)

          # log('strategy-eat', str(a), str(iname), str(it), str(target))
        
      if(strategy[0]=="Idle"):

        # Default
        if(strategy[1]==""):
          strategy[1]=="FindWall"
          

        if(strategy[1]=="FindCentre"): 
            pass 
        #     target = bo.findCentre(start)
        #     log('strategy-findcentre', target)

        # Find nearest wall 
        if(strategy[1]=="FindWall"):   
            target = bo.findClosestWall(start)
            route = bo.route(start, target)
            log('strategy-findwall', target)

        # Track wall - clockwise or counterclockwise 
        if(strategy[1]=="CrawlWall"): 
            r = strategyinfo['rotation']
            p = strategyinfo['proximity']
            target = trackWall(bo, sn, r, p)
            route = bo.route(start, target)

      # Optimum use of space 
      if(strategy[0]=="Survive"):   
          # find dijkstras way out .. 
          # .. otherwise slinky pattern until death
          pass 
      
      # NO TARGET -- previous strategy complete (or could not be completed)
      if(len(target) == 0): 
          print("NO PATH")
          
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
            strategy = ["Idle","FindWall"]

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
    
    # TODO: Tell debug where the target came from
    # TODO: Tell debug which routing strategy was used 
    sn.setStrategy(strategy, strategyinfo)   
    sn.setRoute(route)
    sn.setTarget(target)
    
    return (strategy, strategyinfo)


# TODO:  Consider combining state machine (target) and 

# Check snake target,  return next move 
def translatePath(bo: board, sn: snake) -> str:
    """
    data: https://docs.battlesnake.com/references/api/sample-move-request
    return: "up", "down", "left" or "right"
    """
    
    start = sn.getHead()
    finish = sn.getTarget()
    
    
    # if (change to strategy): 
    # path = bo.route(start, finish)   
    path = sn.getRoute()
    if len(path):
      p = path.pop(0)

    else: 
      # No next move - cant route to destination
      # TODO: Random point
      p = bo.getEmptySpace(start) 
    
    # Translate routepoint to direction
    move = fn.getDirection(start, p)
    log('time', 'After Direction', bo.getStartTime())
    
    print("ROUTE OUTPUT")
    print(str(start), str(finish), str(path), str(p), str(move))
    
    sn.setDirection(move)    
    # return move
    

def getItemByName(its, name):

  for it in its: 
      if it.getName() == name:
        return it 

  return {}


# STUBS -- strategy functions to be built 


def largestSnake(bo, snakes):
    # if larger than enemy
    you = bo.getIdentity()
    you_len = snakes[you].getLength() 

    largest = True 
    for identity in snakes:
      sn = snakes[identity]
      if sn.getType() != "us":
        enemy_len = sn.getLength()
        if you_len >= (enemy_len + CONST.strategyLargerBy):
          pass 
        else:
          largest = False 
          
    return largest 


def killPath(bo, snakes):

    killRadius = 2

    you = bo.getIdentity()
    you_len = snakes[you].getLength() 
    you_head = snakes[you].getHead() 
 
    for identity in snakes:
      sn = snakes[identity]
      if sn.getType() != "us":
        enemy_len = sn.getLength()
        enemy_head = sn.getHead()
        dist = fn.distanceToPoint(you_head, enemy_head)
        if (you_len > enemy_len) and dist < killRadius:
          return sn
          # log('strategy-trigger', "killPath", you_len, enemy_len, dist)

    # if larger than enemy
    # if range to enemy head < 3 
    # & dijkstra predict enemy == distance to enemy head
    # find path based on snake predic matrix (eg. 1, 2, 3 length)
    return None

def threatPath(bo, sn, dist=2):
    # if enemy larger 
    # distance to enemy head < dist 
    # try to increase dist (eg.)
      # if cannot do safely ...
    return False


def headOnCollision(bo, sn):
    # snake predict enemy head 
    # for each enemy head range(0,turns)
    # get distance to prediction 
    # if (distance == futureturns)
    # return killpath 
    return []


def boardControl(bo, sn):
    # stay n ahead & in same direction 
    # move n-1 squares in & connect to wall 
    # loop back to tail path 

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
            if (bo.solid[a1[0], a1[1]] < CONST.routeThreshold):
              print("TRACK-SOLID", str(bo.solid[a1[0], a1[1]]))
              break
        
        # Rotate direction & try again 
        if(r == CONST.counterclockwise): 
            d = CONST.ccwMap[d] 
        else:
            d = CONST.cwMap[d]
     
    log('strategy-trackwall', str(w), str(h), str(a), str(d), str(r), str(p), str(a1))
    return a1
  
def findCentre(bo, sn, proximity=2):
    w = bo.getWidth()
    h = bo.getHeight()

    cx = int((w + 1)/2)
    cy = int((h + 1)/2)
    c = [cx, cy]

    # if centre occupied 
    return []

    # if within proximity of centre 
    return c


    return 


def numMovesAvailable(bo, sn):
    # while sn.getHead()
    #   markAdjacent() 
    #   total + 1 
    #   recursive   
    return 100

# TODO:  predict boardcontrol, ie. snake doing loop
#   if len > enemy,  target enemy head .. 