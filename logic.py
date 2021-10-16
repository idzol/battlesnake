import random as rand

# from typing import Dict
import numpy as np

from operator import add
from collections import OrderedDict
      
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

    numsnakes = len(snakes)

    # Kill interrupt -- larger than 
    if (t := killPath(bo, snakes)):
        interruptlist.insert(0, ['Kill', 'Collide'])
        strategyinfo['killpath'] = t

    # Kill interrupt -- cut off path 
    if (t := enemyEnclosed(bo, snakes)):
        interruptlist.append(['Kill', 'Cutoff'])
        strategyinfo['killcut'] = t

    # Critical health interrupt -- get food
    if (health < CONST.healthCritical):
        interruptlist.insert(0, ['Eat', ''])
        
    # Control interrupt -- control board 
    if (health > CONST.healthLow and largestSnake(bo, snakes) and numsnakes == 2):
        interruptlist.append(['Control', 'Box'])
        for sndata in snakes: 
          sid = snakes[sndata].getId() 
          if sid != you:
            strategyinfo['enemy'] = snakes[sndata]
          
    if (largestSnake(bo, snakes) and health > CONST.healthMed):
        interruptlist.append(['Idle', 'Centre'])
        
    # Survive interuupt 
    if (numMovesAvailable(bo, sn) < sn.getLength()):
        interruptlist.append(['Taunt', ''])
    
    # Health interrupt 
    if (health < CONST.healthHigh): 
        interruptlist.append(['Eat', ''])
         
    # No threats & high health
    if (health > CONST.healthHigh): 
        interruptlist.append(['Idle', 'FindCentre'])
        
    # Interrupt triggered
    if (len(interruptlist)):     
        log('interrupt', str(interruptlist))

    sn.setStrategy(strategylist, strategyinfo) 
    sn.setInterrupt(interruptlist) 
    # return (strategy, strategyinfo)


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

        # WALL OF DOOM 
        # patrol A - B - C ...
        # simple mode 
        # if dist > 2 to body, +1 each turn  

        # Collision & enemy larger
        # elif (pathThreat(bo, start, path, aggro)): 
        #     strategy = ['Idle', 'FindWall']
        #     interrupt = True 



def stateMachine(bo:board, sn: snake, its: list): 
    # Returns target (next move) based on inputs 

    depth = CONST.maxPredictTurns

    # Inputs to state machine 
    interruptlist = sn.getInterrupt() 
    strategylist, strategyinfo = sn.getStrategy()
    strategylist_default = [['Eat', ''], ['Find', 'Centre'], ['Taunt', '']] 
    # CONST.defaultstrategy = [['Eat', ''], ['Taunt', '']]
    strategy = []
   
    start = sn.getHead()
    length = sn.getLength()
    aggro = sn.getAggro()
    tail = sn.getTail()

    # Closest item(s) 
    itsort = bo.findClosestItem(its, start) 
    # snakes .. 
    # threat .. 
    # etc.. 

    # Outputs of state machine 
    target = []
    route = [] 
  
    # Progress state machine
    i = 0
    
    while not len(route):

      log('strategy', str(strategy), str(interruptlist), str(strategylist), str(strategyinfo))
      
      # Get next strategy .. 
      if len(interruptlist):
        # interruptlist - delete every turn   
        strategy = interruptlist.pop(0)

      elif len(strategylist):  
        # strategylist - keep persistent 
        strategy = strategylist.pop(0)

      else:
        # strategyinfo - default strategy 
        # if 'default' in strategyinfo:
        #   strategy = strategyinfo['default']
        # else:
        strategylist = copy.copy(strategylist_default)
        strategy = strategylist.pop(0)

      
      if(strategy[0] == "Kill"):
          if (strategy[1] == "Collide"):
            # HEAD ON COLLISION 
            target = strategyinfo['killpath']    
            log('strategy-killpath', 'killPath', str(start), start(length), str(target))
            # Do not repeat strategy 

          # if (strategy[1] == "Cutoff"):
            # Larger / Smaller & +1 ahead of enemy prediction  
            
            
      if(strategy[0]=='Control'):
          # target = bo.findClosestNESW(start)

          if (strategy[1]=='Box'):
            
            if not 'control' in strategyinfo: 
              strategyinfo['control'] = 0   # 0-a, 1-b, 2-c  
            
            # try: 
            step = strategyinfo['control']
            enemy = strategyinfo['enemy']
            
            # Get closest three vertices of enemy snake 
            targets = bo.findSnakeBox(start, enemy)
            for i in range(0, 3):
              # Convert each vertex box to points
              tpts = np.nonzero(targets[i] > 0)

            # If we are already at vertex
            if start in tpts[step]: 
              # Select the next vertex (out of 3)
              step = (step + 1) % 3
            
            # Target corresponds to current step 
            target = targets[step]

            # Update step 
            strategyinfo['control'] = step

            # Repeat (back of strategy)
            strategylist.append(strategy)
            
            log('strategy-control', str(step), str(target), '')

            # except Exception as e: 
            #   log('exception', 'stateMachine::control-box',str(e))
            
            # TODO: sync with other snake, stay two moves ahead.. 
            # def patrol('top'):
            #   find enemy snake 
            #   push in enemy snake direction (eg. right) 
            #.  check if safe to do so 
            #.  loop around to lef 
            #    push (right)
            #    one square for each len > w 

            # if not front line ('a', 'b' -> 'c'?) 
            #  find food (eg. left)
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

      if(strategy[0]=='Eat'): 

          print ("STRAT-EAT1", str(itsort))
            
          # No food -- change strategy
          if(not len(itsort)):
            # strategylist.append(['Taunt', ''])
            # remove strategy 
            # add strategy (top priority)
            # add strategy (low priority)
            pass 
            
          else: 
            # Repeat -- ie. if no route, try again to next item
            strategylist.insert(0, ['Eat',''])
            # Get route to target  
            itemclose = itsort.pop(0)
            target = itemclose.getLocation()
            print ("STRAT-EAT2", str(start), str(target), str(fn.distanceToPoint(start, target)))

            # One square away, we are eating next turn 
            # if (fn.distanceToPoint(start, target) == 1):
            sn.setEating(True)

            # Continue to eat until interrupted
            # strategylist.insert(0, ['Eat', ''])
            log('strategy-eat', str(target))
          
      if(strategy[0]=='Idle'):

        # Default
        if(strategy[1]==""):
          strategy[1]=="FindWall"
          

        if(strategy[1]=="Centre"): 
            target = bo.findCentre(start)
            if (not(len(target))):
              # strategylist.pop(0) 
              strategylist.append(['Idle', 'FindWall'])

            else: 
              strategylist.insert(0, ['Idle', 'Centre'])
            
            log('strategy-findcentre', target)

        # Find nearest wall 
        if(strategy[1]=="FindWall"):   
            target = bo.findClosestWall(start)
            if (not len(target)):
              # strategylist.pop(0) 
              strategylist.append(['Idle', 'TrackWall'])
            else:
              strategylist.insert(0, ['Idle', 'FindWall'])
              
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
            # strategylist.insert(0, ['Idle', 'Centre'])
            log('strategy-trackwall', target)
            
    
      if(strategy[0]=='Taunt'):
          # Defensive -- Optimum use of space 
          # find dijkstras way out .. 
          # .. otherwise slinky pattern until death
          target = sn.getTail()
          log('strategy-taunt', target)
          print("TAUNT", str(target))

          # Taunt until interrupt or X turns 
          # strategyinfo.insert(counter) = counter + 1
          # if strategyinfo.counter > X 
          # strategylist.insert(0,['Taunt', ''])
            

      # Check route.  If no target or no route , try next strategy    
      if 'numpy' in str(type(target)):
          # Target is an area -- <class 'numpy.ndarray'> 
          route, weight = bo.fuzzyRoute(start, target, length)

      else:
          # Target is a point -- <class 'list'> 
          route, weight = bo.route(start, target, length)

      # No route found 
      if(not len(route)): 
    
          # Check if time exceeds limit 
          st = bo.getStartTime()
          diff = 1000 * (time.time() - st)
          if diff > CONST.timePanic: 
              log('timer-hurry')
              bo.hurry = True   
          log('time','Strategy search', st)
         
      else:
          # # Secondary factors (eg. aggro, threat, health)  
          # tmap = bo.getThreat()
          # # Adjust for future location 
          # turn = fn.distanceToPoint(start, target)
          # turn = min(turn, depth - 1)
          # threat = tmap[turn][target[0], target[1]]
          # if threat < aggro: 
          #   break      
          break
      
      # Exceeded number of attempts 
      if (i > CONST.strategyDepth or bo.hurry):
          # Exit loop
          target = []
          route = []
          break

      # Trim strategies to max strategies 
      while len(strategylist) > CONST.strategyLength: 
        strategylist.pop(-1)
        
      i = i + 1 
    
    
    # Remove duplicates from strategy list 
    stl_unique = []
    for stl in strategylist: 
        if not stl in stl_unique:
          stl_unique.append(stl)  
    strategylist = copy.copy(stl_unique)

    # Save strategy 
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
      
      # log('move-desparate', bo.dump, sn.dump)
      wmin = CONST.routeThreshold
      for d in CONST.directions:
        # Check each direction 
        l = sn.getLength()
        t = list( map(add, start, CONST.directionMap[d]) )
        if (bo.inBounds(t)):
          try: 
            # Find lowest route
            r, w = bo.route(start, t, l)
            if w < wmin:
                p = r.pop(0)
            
          except Exception as e:
            log('exception','makeMove',str(e))
    
    # FINAL CHECK - todod
    route_failure = '' 
    if (not len(p)):
      route_failure = 'no path'  
    elif(not bo.inBounds(p)):
      route_failure = 'path - not in bounds'  
    elif(p in sn.getBody()):
      route_failure = 'path - body collision'

     # Translate move 
    if(route_failure):
      enclosed = bo.enclosed
      move = max(enclosed, key=enclosed.get)
    
    else: 
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
 
    # TODO:  Change from radius to shape 
    for identity in snakes:
      sn = snakes[identity]
      if sn.getType() != "us":
        enemy_len = sn.getLength()
        enemy_head = sn.getHead()
        dist = fn.distanceToPoint(you_head, enemy_head)
        if (you_len > enemy_len) and (dist < killRadius):
          enemy_dirn = sn.getDirection()
          sn_collide = list( map(add, enemy_head, CONST.directionMap[enemy_dirn]) )
          return sn_collid

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
