import random as rand

# from typing import Dict
# import numpy as np
# import pandas as pd
from operator import add

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
    path = sn.getRoute()
    strategylist, strategyinfo = sn.getStrategy() 
    interruptlist = []
    

    # TODO:  Move interrupt to stack (push onto strategy list)..
    # Kill interrupt 
    if (t := killPath(bo, snakes)):
        interruptlist.insert(0, ['Kill', 'Collide'])
        strategyinfo['killpath'] = t

    if(t := enemyEnclosed(bo, snakes)):
        interruptlist.append(['Kill', 'Cutoff'])
        strategyinfo['killcut'] = t

        # PREDICTION 
        # One path - certainty 100% 
        
        # GENERAL 
        # [intent] - moves that reduce # enemy paths
        
        # SURVIVE 
        # [intent] - paths that have most options 
        # pathTree() -> path branches by length

        # TRAPS 
        # Crawl Wall 
        # [10,9],  wall 
        # [0,1] -> [1,w] -> [h, w-1] -> [h-1, 0]
      
        # STALK 
        # Stay within 2 - 8 squares 
        # Find food 
        # Stay within 2... 

    if (largestSnake(bo, snakes) and health > CONST.healthMed):
        interruptlist.append(['Control', ''])
        strategyinfo['default'] = ['Idle', 'Centre']
        
        # WALL OF DOOM 
        # patrol A - B - C ...
        # simple mode 
        # if dist > 2 to body, +1 each turn  

        # Collision & enemy larger
        # elif (pathThreat(bo, start, path, aggro)): 
        #     strategy = ['Idle', 'FindWall']
        #     interrupt = True 

    # Survive interuupt 
    if (numMovesAvailable(bo, sn) < sn.getLength()):
        interruptlist.append(["Taunt", ""])
        
    # No threats, conserve space (Challenge mode) 
    if (health > CONST.healthHigh): 
        # TODO:  Check for threats (ie enemy snakes)
        interruptlist.append(["Idle","FindWall"])
        
    # Health interrupt 
    if (health < CONST.healthLow): 
        interruptlist.append(["Eat",""])
        
    # Attack interrupt 
    if (aggro > CONST.aggroHigh):
        interruptlist.append(["Attack","Stalk"])
        
    # Interrupt triggered
    if (len(interruptlist)):     
        log('interrupt', str(interruptlist))

    sn.setStrategy(strategylist, strategyinfo) 
    sn.setInterrupt(interruptlist) 
    # return (strategy, strategyinfo)


def stateMachine(bo:board, sn: snake, its: list): 
    # Returns target (next move) based on inputs 

    depth = CONST.maxPredictTurns

    strategylist, strategyinfo = sn.getStrategy()
    interruptlist = sn.getInterrupt() 
    defaultstrategy = CONST.defaultstrategy 
    
    start = sn.getHead()
    length = sn.getLength()
    aggro = sn.getAggro()
    tail = sn.getTail()

    # Outputs of state machine 
    target = []
    route = [] 
    
    log('strategy', 'START', str(strategylist), str(strategyinfo))
    
    # Progress state machine
    i = 0
    while not len(route):
      
      # Get next strategy .. 
      if len(interruptlist):
        # interruptlist - delete every turn   
        strategy = interruptlist.pop(0)

      elif len(strategylist):  
        # strategylist - keep persistent 
        strategy = strategylist.pop(0)

      else:
        # strategyinfo - default strategy 
        if 'default' in strategyinfo:
          strategy = strategyinfo['default']
        else:
          strategy = ['Taunt', '']


      if(strategy[0] == "Kill"):
          if (strategy[1] == "Collide"):
            # HEAD ON COLLISION 
            target = strategyinfo['kill']       
            # TODO:  Use prediction route, current direction or random? 
            strategylist.append(defaultstrategy)
            log('strategy-killpath', 'killPath', str(start), start(length), str(target))
            
          # if (strategy[1] == "Cutoff"):
            # Larger / Smaller & +1 ahead of enemy prediction  
            
            
      if(strategy[0]=="Control"):
          if (strategy[1]==''):
            strategy[1]=="Point-A"

          # Patrol A 
          if (strategy[1]=="Point-A"): 

            # If reached target.
            if 'control-a' in strategyinfo:
              if start == strategyinfo['control-a']:
                strategy[1] = "Point-B" 

            if ('control-path' in strategyinfo):
              # retrace previous path 
              target = strategyinfo['control-path'].pop(0)
              route, weight = bo.route(start, target, length)
              
            else: 
              # Get closest cardinal points (n,e,s,w)         
              target = bo.findClosestNESW(start)
              route, weight = bo.route(start, target, length)
              strategyinfo['control-a'] = target
              strategyinfo['enemy-direction'] = bo.findDirectionWith(CONST.legend['enemy-body'])
            
              strategylist.insert(0, ['Control', 'Point-B'])
               
            log('strategy-control', 'A', str(target), '')

          if (strategy[1]=="Point-B"): 

            if 'control-b' in strategyinfo:
              if start == strategyinfo['control-b']:
                strategy[1] = 'Point-C'

            if ('control-path' in strategyinfo):
                # retrace previous path 
                target = strategyinfo['control-path'].pop(-1)
                route = strategyinfo['control-path']
            
            else: 
              target = bo.invertPoint(strategyinfo['control-a'])
              route, weight = bo.route(start, target, length)
              
              strategyinfo['control-b'] = target
              strategyinfo['enemy-direction'] = bo.findDirectionWith
              
              strategyinfo['control-a'] = target
              strategylist.insert(0, ['Control', 'Point-C'])
            
              log('strategy-control', "B", str(target), '')


            if (strategy[1]=="Point-C"): 
              target = strategyinfo['control-a'] 
              # Find food on the way 
              route, weight = bo.route(start, target, length)
              
              # TODO: findFoodInArea
              # TODO: route(a, b, x) to capture food 

              history = sn.getPathHistory()
              cpath = []

              # Write path we took to memory 
              for h in history:
                if h == target:
                  break 
                else:
                  cpath.insert(0, h)

              # Save control path for next patrol 
              strategyinfo['control-path'] = cpath 
              
              log('strategy-control', "C", str(target), cpath)

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
            strategylist.append(defaultstrategy)

          else: 
            # Get closest item 
            itsort = bo.findClosestItem(its, start)
            # Get route to target  
            
            # Iterate through items 
            while (len(itsort)):
                target = itsort.pop(0).getLocation()
                # Get threat map 
                tmap = bo.getThreat()
                # Adjust for future location 
                turn = fn.distanceToPoint(start, target)
                turn = min(turn, depth - 1)
                threat = tmap[turn][target[0], target[1]]
                # Calculate route & weight 
                route, weight = bo.route(start, target, length)
                # Look for item with low threat & low route complexity 
                if weight < CONST.routeThreshold and threat < aggro:
                    break 

            # If no route to target change to default strategy 
            if(not len(route)):
                strategylist.append(defaultstrategy)

            # TODO: Introduce threat level to "allowed" or "gradient" (route)
            # log('strategy-eat', str(a), str(iname), str(it), str(target))
          
      if(strategy[0]=='Idle'):

        # Default
        if(strategy[1]==""):
          strategy[1]=="FindWall"
          

        if(strategy[1]=="Centre"): 
            target = bo.findCentre(start)
            strategylist.insert(0, defaultstrategy)
            log('strategy-findcentre', target)


        # 

        # Find nearest wall 
        if(strategy[1]=="FindWall"):   
            target = bo.findClosestWall(start)
            strategyinfo['next'] = ['Idle', 'TrackWall']
            log('strategy-findwall', target)
            
        # Track wall - clockwise or counterclockwise 
        if(strategy[1]=="TrackWall"): 

            rotation = int(2 * rand.random())
            if (rotation):
                rotation = CONST.clockwise 
            else: 
                rotation = CONST.counterclockwise 

            proximity = 2
            target = trackWall(bo, sn, rotation, proximity)
            strategyinfo['next'] = ['Idle', 'Centre']
            log('strategy-trackwall', target)
            
    
      if(strategy[0]=="Taunt"):
          # Defensive -- Optimum use of space 
          # find dijkstras way out .. 
          # .. otherwise slinky pattern until death
          target = sn.getTail()
          strategyinfo['next'] = ['Eat', '']
          log('strategy-taunt', target)
            

      # Check route.  If no target / no route  -- previous strategy complete or could not be completed).  Find new strategy 
      route, weight = bo.route(start, target, length)
      if(not len(route)): 
          
          # Check if time exceeds limit 
          st = bo.getStartTime()
          diff = 1000 * (time.time() - st)
          if diff > CONST.timePanic: 
              log('timer-hurry')
              bo.hurry = True   
          log('time','Strategy search', st)
          
          # Find new strategy 
          if (len(strategylist) > 1):
              # Try next 
              strategy.pop(0) 
          else:  
              # Default strategy 
              strategy = defaultstrategy 
            
          log('strategy-iterate', str(strategy))


      if (i > CONST.strategyDepth or bo.hurry):
          # Exit loop
          target = []
          route = []
          break
          # log('strategyInsert random walk 
          # target = random ... 
          # interrupt = True 
      
          
      log('strategy', 'Try again: ' + str(i), str(strategy), str(strategyinfo))
      i = i + 1 
    
    sn.setStrategy(strategylist, strategyinfo)   
    sn.setRoute(route)
    sn.setTarget(target)
    
    return (strategy, strategyinfo)


# TODO:  Consider combining state machine (target) and 

# Check snake target,  return next move 
def makeMove(bo: board, sn: snake) -> str:
    """
    data: https://docs.battlesnake.com/references/api/sample-move-request
    return: "up", "down", "left" or "right"
    """
    
    start = sn.getHead()
    finish = sn.getTarget()
    
    
    # if (change to strategy): 
    # path = bo.route(start, finish)   
    path = sn.getRoute()
    p = []
    if len(path):
      p = path.pop(0)

    if (not len(p) or not bo.inBounds(p)):
      # Final check that move is valid  
      # TODO: Report on this condition -- solve through stateMachine  
      # log('move-desparate', bo.dump, sn.dump)

      # Tempoary logic to (a) avoid enclosed spaces and (b) avoid head to head collisions 

      enclosed = copy.copy(bo.enclosed)
      dijkstra = copy.copy(bo.dijkstra[0])

      for d in CONST.directions:
          a = list( map(add, start, CONST.directionMap[d]) )
          if (not bo.inBounds(a) or dijkstra[a[0], a[1] > CONST.routeThreshold / 2]): 
            try: 
              enclosed.pop(d, None)
            except:
              pass 
              
      dirn = max(enclosed, key=enclosed.get)
      p = list( map(add, start, CONST.directionMap[dirn]) )
  
    # Translate routepoint to direction
    move = fn.translateDirection(start, p)
    log('time', 'After Direction', bo.getStartTime())
    
    log('make-move', str(start), str(finish), str(path), str(p), str(move))
        
    sn.setMove(move)    
    # return move
    

# == HELPERS == 

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


def pathThreat(board, start, path, maxthreat=CONST.aggroLow): 
    # TODO:  search whole route (currently first vector only) 

    if(len(path)):
      tmap = board.getThreat()
      # First vector 
      p0 = path.pop(0)
      # Translate to points 
      points = fn.getPointsInLine(start, p0) 
      # Iterate points 
      for pt in points:
        # Threat exceeds aggro .. 
        if (tmap[0][pt[0], pt[1]] > maxthreat):
          return True
    
    return False


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
    
    return False


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


def trackWall2(bo, sn, rotation=CONST.clockwise, proximity=0):
    
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
    # TODO:  Switch from one square collision detect to using route 
    # TODO:  makeMove -- consolidate bo.getEmptyAdjacent(start)  -> trackWall() 
     
    # a = current point 
    # d = direction
    # next corner 
    # if east & up .. 
    #   corner north east 
    # if east & down 
    #   corner south east 
    # .. 
    # target corner - proximity 

        
    # Rotate direction & try again 
    if(r == CONST.counterclockwise): 
        d = CONST.ccwMap[d] 
    else:
        d = CONST.cwMap[d]
  
    # log('strategy-trackwall', str(w), str(h), str(a), str(d), str(r), str(p), str(a1))
    return a

def trackWall(bo, sn, rotation=CONST.clockwise, proximity=0):
    # DEPRECATE:  Replace with route / fuzzyRoute logic which incorporates normal routing engine  

    # TODO:  Update for proximity (ie. X squares away from edge).  
     
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

    
    for i in range(0, 4):
        # Add one point in current direction 
        a1[0] = ay + CONST.directionMap[d][0]
        a1[1] = ax + CONST.directionMap[d][1]
        
        # No collision & in bounds 
        if( 0 <= a1[0] < w and 0 <= a1[1] < h):
            bs = bo.solid[a1[0], a1[1]] 
            bt = bo.threat[0][a1[0], a1[1]] 
            pt = CONST.pointThreshold
            ag = sn.getAggro()

            # Not solid, low threat, not enclosed
            move = fn.translateDirection(a, a1)
            length = sn.getLength()
        
            if (bs < pt and bt < ag and length < bo.enclosed[move]):
              # print("TRACK-SOLID", str(bo.solid[a1[0], a1[1]]))
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
    # return c


def numMovesAvailable(bo, sn):
    enclosed = copy.copy(bo.enclosed)
    max_len = max(enclosed, key=enclosed.get)
    return int(enclosed[max_len])


def enemyEnclosed(bo, snakes): 

    # for s in snakes ... 
    # run enclosed algo 
    # enclosed algo identify choke points?  
    # graph 
    # a -> [b] -> c,d,e,f
    # a -> b,c,d,e,f
    # return b -- if B then 
    #  
    # MovesAvailable(enemy< enemy.getLength()

    return False


# == DEPRECATE / DELETE == 

def getItemByName(its, name):
  # DEPRECATE / DELETE:  belongs in functions?  duplicate in board.  
  for it in its: 
      if it.getName() == name:
        return it 

  return {}
