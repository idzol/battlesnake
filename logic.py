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

# === STATE MACHINE ===
# Core decision making engine

    # Eat -- focus on maximising snake size and restoring health
    # Attack -- larger size, full health, stay close to head, intercept food, look for kill
    # Kill -- opportunity to kill (eg. head to head collision)
    # Defend -- smaller snake .. 
    # Survive -- limited moves left 
    # .. 
    
# Changes strategy (state machine) based on external influence 
def checkInterrupts(bo:board, sn:snake, snakes):

    # Return your snake 
    you = bo.getIdentity()
    # sn = snakes[you]
    
    health = sn.getHealth() 
    length = sn.getLength()
    # aggro = sn.getAggro()
    # path = sn.getRoute()
    
    strategylist, strategyinfo = sn.getStrategy() 
    interruptlist = []

    numsnakes = len(snakes)
    minlength = CONST.growLength
    larger = CONST.controlLargerBy
    
    reason = []

    # Kill interrupt -- larger than 
    t = killPath(bo, snakes)
    if (len(t)):
        interruptlist.insert(0, ['Kill', 'Collide'])
        strategyinfo['killpath'] = t
        reason.append('killpath was identified')

    # Kill interrupt -- cut off path 
    t = enemyEnclosed(bo, sn, snakes)
    if (len(t)):
        interruptlist.append(['Kill', 'Cutoff'])
        strategyinfo['killcut'] = t
        reason.append('enclosed enemy was identified')

    # t = foodNearby(bo, sn, snakes)
    # if (len(t)):
    #   interruptlist.insert(0, ['Eat', ''])

    # Critical health interrupt -- get food
    if (health < CONST.healthCritical):
        interruptlist.insert(0, ['Eat', ''])
        reason.append('health was critical')


    # Control interrupt -- control board 
    if (health > CONST.healthLow and largestSnake(bo, snakes, minlength, larger) and numsnakes == 2):
        interruptlist.append(['Control', 'Box'])
        for sndata in snakes: 
          sid = snakes[sndata].getId() 
          if sid != you:
            strategyinfo['enemy'] = snakes[sndata]

        reason.append('duel, '+str(minlength)+' length and larger by '+str(larger))


    if (largestSnake(bo, snakes, minlength, larger) and health > CONST.healthMed):
        interruptlist.append(['Idle', 'Centre'])
        reason.append('largest snake by '+str(minlength)+' length and larger by '+str(larger))

    # Growth interrupt when small
    if (health < CONST.healthHigh and length < CONST.growLength): 
        interruptlist.append(['Eat', ''])
        reason.append('health is less than high and length less than '+str(CONST.growLength))

    # # No threats & high health
    # if (health >= CONST.healthLow): 
    #     interruptlist.append(['Idle', 'Centre'])
    #     reason.append('health is high')

    # Health interrupt general 
    if (health < CONST.healthLow): 
        interruptlist.append(['Eat', ''])
        reason.append('health is less than high')

    # Survive interuupt 
    if (numMovesAvailable(bo, sn) < length):
        interruptlist.append(['Survive', ''])
        reason.append('less than X moves available')

    # Interrupt triggered
    if (len(interruptlist)):     
        log('interrupt', str(interruptlist), str(reason))

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
        #     strategy = ['Idle', 'Wall']
        #     interrupt = True 



def stateMachine(bo:board, sn: snake, snakes: list, foods: list): 
    # Returns target (next move) based on inputs 

    depth = CONST.lookAheadPath
    
    # Inputs to state machine 
    interruptlist = sn.getInterrupt() 
    strategylist, strategyinfo = sn.getStrategy()
    strategylist_default = [['Eat', ''], ['Idle', 'Centre']]
    #  ['Control', 'Space']
    #  ['Idle', 'Wall']
    
    strategy = []
    start = sn.getHead()
    length = sn.getLength()
    foodsort = fn.findClosestItem(foods, start)
    # aggro = sn.getAggro()
    # tail = sn.getTail()
    # alltails = getSnakeTails(snakes)

    # Outputs of state machine 
    route = [] 
    i = 0
    
    found = False
    lastGasp = False

    while not found:
      # Reset every turn 
      target = []
      route = []
      reason = []
    
      # Get next strategy .. 
      if len(interruptlist):
        # interruptlist - delete every turn   
        strategy = interruptlist.pop(0)
        reason.append('interrupt was triggered')

      elif len(strategylist):  
        # strategylist - keep persistent 
        strategy = strategylist.pop(0)
        reason.append('strategy from last turn')

      elif(not lastGasp):
        # strategyinfo - default strategy 
        # if 'default' in strategyinfo:
        #   strategy = strategyinfo['default']
        # else:
        strategylist = copy.copy(strategylist_default)
        strategy = strategylist.pop(0)
        reason.append('default strategy invoked')
        lastGasp = True 
      
      else: 
        # Terminate search 
        route = [] 
        target = [] 
        reason.append('last strategy reached')
        break 

      log('strategy', str(strategy), str(reason), str(strategylist), str(strategyinfo))

      # Test a particular strategy 
      # strategy = ['Eat', '']

      if(strategy[0] == 'Kill'):
          if (strategy[1] == 'Collide'):
            # HEAD ON COLLISION 
            target = strategyinfo['killpath']    
            log('strategy-killpath', 'killPath', str(start), str(length), str(target))
            # Do not repeat strategy 

          if (strategy[1] == 'Cutoff'):
            if len(strategyinfo['killcut']):
              target = strategyinfo['killcut'].pop()
              strategylist.insert(0, strategy)

            else: 
              # Repeat until no more paths 
               pass 
             
            log('strategy-killpath', 'killCut', str(start), str(length), str(target))
            
            
      if(strategy[0]=='Control'):

          # target = bo.findClosestNESW(start)  
          if (strategy[1]=='Space'):

            target = controlSpace(bo, sn, snakes)
            log('strategy-route', "CONTROL SPACE", str(start), str(target))
           
          
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
            
            # TODO:  Repeat next turn but not this turn.  Should just interrupt again .. 
            # strategylist.append(copy.copy(strategy))
            # strategyinfo['norepeat'] = copy.copy(strategy)
            
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


      if(strategy[0]=='Attack'):
          
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

          # No food -- change strategy
          # Sort by closest food
          if(len(foodsort)):
              target = findBestFood(foodsort, bo, sn, snakes)
              if(not len(target)):
                  # Try next food 
                  foodsort.pop(0)
                  strategylist.insert(0, strategy)
              
          
          log('strategy-eat', str(target))
          

      if(strategy[0]=='Idle'):

        # Default
        if(strategy[1]==''):
          strategy[1]=='Centre'
          

        if(strategy[1]=='Centre'): 
            target = bo.findCentre(start)
            if (not(len(target))):
              # If already in centre .. 
              # strategylist.pop(0) 
              strategylist.append(['Idle', 'Centre'])

            else: 
              # TODO:  Very computationally intensive.  Temporary remove from retry ..
              # strategylist.append(strategy)
              pass 

            log('strategy-findcentre', target)

        # Find nearest wall 
        if(strategy[1]=='Wall'):   
            target = bo.findClosestWall(start)
            if (not len(target)):
              pass 
              # Already on a wall 
              # Do not repeat 
              # strategylist.append(['Idle', 'Centre'])

            else:
              # Repeat until interrupt 
              strategylist.insert(0, strategy)
              
            log('strategy-findwall', target)
            
        # Track wall - clockwise or counterclockwise 
        if(strategy[1]=='TrackWall'): 

            if not 'rotation' in strategyinfo: 
              rotation = int(2 * rand.random())
              if (rotation):
                  rotation = CONST.clockwise 
              else: 
                  rotation = CONST.counterclockwise 
            else: 
              rotation = strategyinfo['rotation']

            proximity = 2
            
            target = trackWall(bo, sn, rotation, proximity)
            # Repeat -- until interrupt
            strategylist.insert(0, strategy)
            log('strategy-trackwall', target)
            
    
      if(strategy[0]=='Survive'):
          # Defensive 
          
          if(strategy[1]==''):  
            # Find any way out .. 
            route = bo.findLargestPath([start])
            if len(route) > 1:
              # Remove start point (head)
              route.pop(0) 
              # Target is next point
              target = route.pop(0)
              # strategylist.insert(0, strategy)
            
            else:
              target = []

          if(strategy[1]=='Taunt'):
            # Chase our tail 
            target = sn.getTail()           
            # Repeat -- until interrupt 
            strategylist.insert(0, strategy)

          log('strategy-taunt', target)


      # Check route
      st = bo.getStartTime()
      log('time', 'Strategy::Route', st)
      
      # If no target or no route , try next strategy    
      if 'numpy' in str(type(target)):
          # Target is an area 
          log('strategy-route', "TARGET", str(strategy), str(target))
          route, weight = bo.fuzzyRoute(start, target, length)
          
      elif 'list' in str(type(target)) and bo.inBounds(target):
          # Target is a point -- type == <class 'list'> 
          log('strategy-route', "TARGET", str(strategy), str(target))
          route, weight = bo.route(start, target, length)
          

      st = bo.getStartTime()
      log('time', 'Strategy::RoutePadding', st)

      if (len(route)):
          # Route found -- try to find a safe way out 

          eatingNext = False
          if route[0] in foods:
            # Check if eating next turn to adjust route tables 
            eatingNext = True 

          # Insert start 
          route.insert(0, start)  
          route = copy.copy(fn.getPointsInRoute(route))
          
          # If route valid 
          log('strategy-route', "ROUTE", str(start), str(route))
          
          # Pad out route to N moves 
          fullroute, found = bo.routePadding(route, eatingNext)
          log('strategy-route', "ROUTE PADDING", str(start), str(fullroute))
    
      if(found): 
          # Route found
          route = copy.copy(fullroute)

          log('strategy-update','Path found\nTarget:'+str(target)+'\nRoute:'+str(route)+'\nWeight: '+str(weight))
          break
      

      # Check if time exceeds limit 
      st = bo.getStartTime()
      diff = 1000 * (time.time() - st)
      if diff > CONST.timePanic: 
          log('timer-hurry')
          bo.hurry = True   
      
      log('time','Strategy search', st)
        
      # Exceeded number of attempts 
      if (i > depth or bo.hurry):
          # Exit loop
          target = []
          route = []
          break
  
      log('strategy-update','route from '+str(start)+' to '+str(target)+' not found, try again. i:'+str(i))
      
      i = i + 1 
    
    
    # Remove duplicates from strategy list 
    stl_unique = []
    for stl in strategylist: 
        if not stl in stl_unique:
          stl_unique.append(stl)  
    strategylist = copy.copy(stl_unique)

    # Trim strategies to max strategies 
    while len(strategylist) > CONST.strategyLength: 
      strategylist.pop(-1)
      
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
    route_method = ''

    # 0) Route Found 
    route = sn.getRoute()
    p = []
    if len(route):
      route_method = 'route_stateMachine'
      p = route.pop(0)
      

    # 1) Still no route - Use lookahead (route padding)
    # TODO: Combine lookahead & dijkstra to avoid 
    #   collision with high threat 
    if (not len(p) or not bo.inBounds(p)):
      route_method = 'route_findLargestPath'
      route = bo.findLargestPath([start])
      if len(route) > 1:
        # TODO: Cleanup routes -- some include start, others don't
        # Remove head (if exists)
        if (route[0] == start): 
          route.pop(0)

        try:
          p = route.pop(0)
        except Exception as e:
          log('exception', 'makeMove', str(e))


    # 2) Still no route - Chase a tail
    if (not len(p) or not bo.inBounds(p)):
      route_method = 'route_chaseTail'
      for d in CONST.directions:
        # Check each direction 
        t = list( map(add, start, CONST.directionMap[d]) )
        if (bo.inBounds(t)):
          # Find tail
          # TODO:  if sn.Eating():

          w = bo.trails[t[0],t[1]]
          if w == 1:
            p = copy.copy(t)
            wmin = copy.copy(w) 
    

    # 3) Still no route - Use lowest gradient
    if (not len(p) or not bo.inBounds(p)):
      route_method = 'route_dijkstra'
      wmin = CONST.routeThreshold
      for d in CONST.directions:
        # Check each direction 
        t = list( map(add, start, CONST.directionMap[d]) )
        if (bo.inBounds(t)):
          try: 
            # Find lowest weight
            w = bo.dijkstra[0][t[0],t[1]]
            if w < wmin:
              p = copy.copy(t)
              wmin = copy.copy(w) 

          except Exception as e:
            log('exception','makeMove',str(e))


    # 4) Still no route - Use self.enclosd available moves 
    # if (not len(p) or not bo.inBounds(p)):
    #   route_method = 'route_dijkstra'
    #   for d in CONST.directions:
    #     moves_avail = bo.enclosed[move] 
    #     ..


    # 5) Still no route - Wipe markovs & try again
    # if (not len(p) or not bo.inBounds(p)):
    #   route_method = 'route_findLargest_clear'
    #   bo.resetRouting()
    #   route = bo.findLargestPath([start])
    #   if len(route) > 1:
    #     if (route[0] == start): 
    #       route.pop(0)
    #     try:
    #       p = route.pop(0)
    #     except Exception as e:
    #       log('exception', 'makeMove', str(e))


    #  # Translate move 
    # if(route_failure):
    #   enclosed = bo.enclosed
    #   move = max(enclosed, key=enclosed.get)
    
    # Translate routepoint to direction
    move = fn.translateDirection(start, p)

    log('time', 'After Direction', bo.getStartTime())
    
    log('make-move', str(start), str(finish), str(p), str(move), str(route_method))
        
    sn.setRoute(route)
    sn.setMove(move)    
    # return move
    

# == HELPERS == 

def largestSnake(bo, snakes, minlength=CONST.growLength, larger=CONST.controlLargerBy):
    # if larger than enemy
    you = bo.getIdentity()
    you_len = snakes[you].getLength() 
    if you_len < minlength:
        return False 

    largest = True 
    for identity in snakes:
      sn = snakes[identity]
      if sn.getType() != "us":
        enemy_len = sn.getLength()
        if you_len >= (enemy_len + larger):
          pass 
        else:
          largest = False 
          
    return largest 


# def pathThreat(board, start, path, maxthreat=CONST.aggroLow): 
#     # TODO:  search whole route (currently first vector only) 

#     if(len(path)):
#       tmap = board.getMarkov()
#       # First vector 
#       p0 = path.pop(0)
#       # Translate to points 
#       points = fn.getPointsInLine(start, p0) 
#       # Iterate points 
#       for pt in points:
#         # Threat exceeds aggro .. 
#         if (tmap[0][pt[0], pt[1]] > maxthreat):
#           return True
    
#     return False


def killPath(bo, snakes, radius=CONST.killRadius):
    # Find smaller snakes within a kill radius 
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

        # If larger & within kill zone 
        if (you_len > enemy_len) and (dist <= radius):
          enemy_dirn = sn.getDirection()
          sn_collide = list( map(add, enemy_head, CONST.directionMap[enemy_dirn]) )
          if (bo.inBounds(sn_collide)):
            return copy.copy(sn_collide)

    return []


def threatPath(bo, sn, dist=2):
    # if enemy larger 
    # distance to enemy head < dist 
    # try to increase dist (eg.)
      # if cannot do safely ...
    return False


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
    a = sn.getHead()       # [0,0] 
    d = sn.getDirection()  # left, right, up, down
    
    a1 = []

    r = rotation    # cw, ccw
    p = proximity   # 0, 1, 2..

    # TODO:  Update for proximity (ie. X squares away from)
    for i in range(0, 4):
        # Add one point in current direction 
        a1 = list(map(add, a, CONST.directionMap[d]))
        # In bounds 
        if bo.inBounds(a1) :
            # All other logic in routing engine .. 
            break 

        # Rotate direction & try again 
        if(r == CONST.counterclockwise): 
            d = CONST.ccwMap[d] 
        else:
            d = CONST.cwMap[d]
    
    # log('strategy-trackwall', str(w), str(h), str(a), str(d), str(r), str(p), str(a1))
    return a1


def trackWall2(bo, sn, rotation=CONST.clockwise, proximity=0):
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


def getSnakeTails(snakes): 
    # Returns coordinates of all snake tails in list 
    tails = []
    for snid in snakes:
      sn = snakes[snid]
      tails.append(sn.getTail())

    return copy.copy(tails)


def numMovesAvailable(bo, sn):
    # Return maximum number of moves in any direction   
    enclosed = copy.copy(bo.enclosed)
    max_len = max(enclosed, key=enclosed.get)
    return int(enclosed[max_len])


def enemyEnclosed(bo, us, snakes): 
    
    head = us.getHead()
    
    targets = [] 
    # Iterate through snakes 
    for snid in snakes:
      sn = snakes[snid]

      if (sn.getType() == 'enemy'):
        
        enemy_head = sn.getHead()
        # Calculate which squares we can get to 
        board_closest = bo.closestDist(head, [enemy_head])
        # Assess enemy path 
        board_chance = sn.getChance()
        # print("BOARD CHANCE", board_chance)
                    # bo.pathProbability(enemy_head)
        
        # Find interecept between closest point & snake chance
        targets = findInterceptPath(head, board_closest, board_chance)

        # print(str(board_closest))
        # print(str(board_chance))
        
        # TODO: move these tables to setEnemy ... 
        # Set / get enemy boards  
        # sn.setClosest(board_closest)
        # sn.setChance(board_chance)
      

    return copy.copy(targets)


def findInterceptPath(start, board_dist, board_chance, chance=CONST.interceptMin):
    # Returns a sorted list of intercept paths that 
    # a) enemy snake will route through (%chance)
    # b) we can get to before the enemy 
    
#     global board_dist
#     global board_chance

    target = start 
    intercepts = np.nonzero(board_chance > chance)
    intdict = {} 
        
    # TODO:  Better way to sort a list with function (eg list->dict-list)?
    for i in range(0, len(intercepts[0])):
        try:
            target = [intercepts[0][i], intercepts[1][i]]
            dist = fn.distanceToPoint(start, target)
            intdict[str(target)] = dist
        except Exception as e:
            # TODO: Look at these errors 
            log('exception', 'findInterceptPath#1', str(e)) 
            
    intsort = dict(sorted(intdict.items(), key=lambda item: item[1]))
    intlist = []
    
    for il in intsort:
        try: 
            y, x = il.strip('][').split(', ')
            y = int(y)
            x = int(x)
            if (board_dist[y, x]):
                intlist.append([y, x])
            
        except Exception as e:
            log('exception', 'findInterceptPath#1', str(e)) 
        
    return intlist

def findBestFood(foods, bo, us, snakes): 
    # Check if bigger snakes are closer to the food 
    #  # REWRITE .. 
    #  Eat strategy
    #     Closest 
    #     # Work out how many food we can get to before enemy 
    #     Faster than enemies  
    #     Multiples 
    #        Most items 
    #     Safest 
    #        Big snakes 
    #        Corners 
    #     Waiting 
    #        Least threat quadrant 
    #     etc..


    start = us.getHead()
    length = us.getLength()

    foodsort = copy.copy(foods)
    target = []
   
    f = foodsort[0] 
    target = copy.copy(f) 
    print("EAT STRATEGY", f, foods) 
    return f 

    # 1) Closest food 
    # Abandon closest if enemy snakes are closer & larger 
    while not len(target) and len(foodsort): 

      # Gen next food  
      f = foodsort.pop(0) 
      target = copy.copy(f) 
      
      # Check we can route to location 
      r, w = bo.route(start, f)
      if (len(r)): 
        # Route exists 
        reason = 'route exists'
        usdist = len(fn.getPointsInRoute(r))

        # Check each snake to see if larger / closer snake  
        # Find furthest food from other snakes 
        for sid in snakes:
          fsnake = snakes[sid]
          ftype = fsnake.getType()
          flen = fsnake.getLength()   
          if (ftype == 'enemy'):
            fhead = fsnake.getHead()
            # Append to heads -- used later if no path found 
            fdist = fn.distanceToPoint(fhead, f)

            # Enemy is same / larger and equal / closer 
            if (fdist < CONST.foodThreat and fdist <= usdist and flen > length):
              # Ignore , live to fight another day 
              reason = 'enemy larger & very close'
              target = []

            # Enemy is closer 
            elif(fdist < usdist):  
              reason = 'enemy is closer'
              # Ignore , enemy will beat us there 
              target = []

      else:
        reason = 'no route'

    # 2) Uncontested food 
    # Find food furthest from enemy snakes 
    # TODO: Check if covered by above

    # 3) Empty space -- Maximise control and wait for next food spawn.  See ['Control', 'Space']
 
    # print("EAT AVOID")
    # print(str(fsnake), str(ftype), str(flen), str(fdist))
    print("EAT STRATEGY", target, reason) 
    return copy.copy(target)

 
def controlSpace(bo, us, snakes):
 
    start = us.getHead()
    target = [] 

    # Find all enemy heads 
    heads = []
    # Find distance to closest head 
    dist_min = bo.width * bo.height

    for sid in snakes:
      fsnake = snakes[sid]
      ftype = fsnake.getType()   
      if (ftype == 'enemy'):
        fhead = fsnake.getHead()
        heads.append(fhead)
        distance = fn.distanceToPoint(fhead, start)
        dist_min = min(dist_min, distance)

    # Look for each location 
    control_max = 0
    dist_final = []
    for d in CONST.directions: 
        # maximise board control - stepwise max 
        step = list(map(add, start, CONST.directionMap[d]))
        if (bo.inBounds(step)):
          # Return board control matrix 
          dist = bo.closestDist(step, heads)
          control = np.sum(dist)

          # Save location wtih max control 
          if control > control_max:
              control_max = control
              target = copy.copy(step) 
              dist_final = copy.copy(dist)
              # board_dist = copy.copy(dist)

          if dist_min < CONST.foodThreat: 
              # If too close to enemy, abandon 
              target = [] 


    # Board max - brute force search   
    # control_max = 0
    # for h in range(0, height):
    #     for w in range(0, width):
    #       start = [h, w]
    #       dist = bo.closestDist(start, heads)
    #       control = np.sum(dist)
    #       # Save location wtih max control 
    #       if control > control_max:
    #           control_max = control
    #           target = copy.copy(start) 
    #           # board_dist = copy.copy(dist) 

    return copy.copy(target)


# == DEPRECATE / DELETE == 

