import random as rand

# from typing import Dict
import numpy as np

from operator import add
from collections import OrderedDict
      
import time as time 
import copy as copy 

import functions as fn
# from logClass import log

import constants as CONST

from snakeClass import snake
from boardClass import board

"""
logic.py
===
Core decision making engine for target selection and making moves 
"""


def predictFuture(bo:board, sn:snake, snakes:list, foods:list):
    """
    Play forward (futuremoves) turns 
    Check for enemy moves before calculating route boards  
    ==
    bo:     boardClass as board 
    sn:     snakeClass as snake 
    snakes: list[] of snakes  
    ==
    return: none
    (set board routing)
      board.updateCell()
    """
    
    # Update / modify routes

    # Enemy kills us -- playing forward X turns
    numfuture = CONST.lookAheadPredictFuture

    # Update enemy future paths to depth of N = numfuture
    bo.getEnemyFuture(snakes, numfuture)
  
    # Check for any possible futures where we die 
    (rr, avoid) = checkFutureDeath(bo, sn, snakes, numfuture=numfuture)

    # Update board to avoid these cells
    them = []
    for sid in snakes:
        enemy  = snakes[sid]
        if (enemy.getType() == 'enemy'):
            enemy_head = enemy.getHead()
            them.append(enemy_head)
        else: 
            head = enemy.getHead()
            
    # TODO: Further modify this to capture closer & larger 
    same = True # include squares where we get there same time 
    closest = bo.closestDist(head, them, same=same)
    
    # Update squares to avoid because of head on collisions 
    # Update squares to avoid because of head on deadend(deprecate) 
    if (len(avoid)):
        # If enemy can get to location before us 
        # If enemy kill path found 
        # print(avoid)
        for path in avoid:
            # Set future markov board, where 
            # * length of steps reflects turn, and 
            # * routing logic looks at next markov board 
            
            for step in path:
            
              # print("PREDICT FUTURE DEATH", step)

              for i in range(0, len(path)):
                bo.updateCell(path[i], CONST.routeSolid/2, i, replace=True)
                bo.updateCell(path[i], CONST.routeSolid/2, i+1, replace=True)

              # bo.updateCell(step, CONST.routeSolid/4, len(path)+1, replace=True)

    # Update eating for snakes based on path 
    # Update cells that enemy snakes can get to before us 
    for sid in snakes: 
        # Ignore us -- we have better calculation because we know our route 
        if (snakes[sid].getType() != "us"): 
            # Uses every possible path based on self.predictEnemyMoves
            paths = snakes[sid].getNextSteps()
            length = snakes[sid].getLength()
            # 
            threat = CONST.routeSolid/2
            for path in paths: 
              # Todo: only paint squares in each path based on turn 
              for pt in path:
                # Print out hazard for N = enemy length or width of board
                for turn in range(0, min(length, bo.width)):
                  if not closest[pt[0], pt[1]]:           
                    bo.updateCell(pt, threat, turn)
                    # bo.updateCell(pt, CONST.routeSolid/(turn+1), turn)
                # threat = int(threat / 5)

            food_in_route = 0 

            # Check if there is food one square from them .. 
            try:
                food_path = 0  
                # Check if food is in future moves 
                for path in paths: 
                    pt = path[0]  # truncate to first point only for now 
                    if pt in foods: 
                        food_in_route = 1 
                    # print("DEBUG ENEMY PATH", sid, pt, path, food_path)   # lookAheadPredictFuture

            except:
                pass 

            # Check if snake ate this turn (don't we already accommodate?)
              

            snakes[sid].setEatingFuture(food_in_route)
            # print(sid, food_in_route)
                            
    # Performance monitoring 
    return rr 


def controlSpace(bo:board, us:snake, snakes:list, aggro=False):
    """
    Maximise number of points we have access to on the board 
    Note:  Finds local maximum 
    ==
    bo:     boardClass as board 
    sn:     snakeClass as snake 
    snakes: list[] of snakes  
    ==
    return: target    (points, eg. [1,2])
    """ 
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
    for d in CONST.directions: 
        # maximise board control - stepwise max 
        step = list(map(add, start, CONST.directionMap[d]))
        if (bo.inBounds(step) and bo.isRoutePointv2(step, 0)):
          # Return board control matrix 
          dist = bo.closestDist(step, heads)
          control = np.sum(dist)
          # Save location wtih max control 
          
          if control > control_max:
              control_max = control
              target = step + []   # copy.copy
              # board_dist = copy.copy(dist)

          if not aggro and dist_min < CONST.foodThreat: 
              # If too close to enemy, abandon 
              target = [] 

          # print("CONTROL", step, control, target, dist_min, CONST.foodThreat)


    return copy.copy(target)


# Enemy interrupt / strategy (state machine) based on external influence 
def enemyInterrupts(bo:board, sn:snake, snakes:list):
    """
    Check for events that change enemy strategy
    """
    # Return your snake 
    you = bo.getIdentity()

    strategyinfo =  {}
    interruptlist = []

    us = snakes[you]
    head_us = us.getHead()
    
    # if(largestSnake(bo, sn, snakes, 0)): 
    #   interruptlist.insert(0, ['Kill', 'Collide'])
    #   strategyinfo['killpath'] = head_us
      
    # if(distToWall <= 1 
    #  ['Idle', 'Wall']

    sn.setStrategyInfo(strategyinfo) 
    sn.setInterrupt(interruptlist) 


# Changes strategy (state machine) based on external influence 
def checkInterrupts(bo:board, sn:snake, snakes:list, foods:list):
    """
    Check for events that need response in three categories 
    (1) Kill logic 
    (2) Board control logic 
    (3) Survival logic 
    ==
    bo:     boardClass as board 
    sn:     snakeClass as snake 
    snakes: list[] of snakes  
    ==
    return: none
    (set snake variables)
      sn.setStrategy(strategylist, strategyinfo) 
      sn.setInterrupt(interruptlist) 
    """
  
    # Return your snake 
    you = bo.getIdentity()
    
    # Get our stats 
    length = sn.getLength()
    health = sn.getHealth()
    start = sn.getHead()
    
    strategyinfo =  {}
    interruptlist = []
    reason = []

    # Check if duel (two snakes)
    numsnakes = len(snakes)
    if (numsnakes == 2):
        duel = True
    else:
        duel = False 
    
    # Check if ally (idzol)
    ally = None
    for sid in snakes: 
      if snakes[sid].getType() != "us":
        if snakes[sid].getName() in ["Idzol", "Cucumber Cat"]: 
          ally = sid 
          strategyinfo['ally'] = sid
            
    
    # Check if largest snake by one, many 
    larger = largestSnake(bo, sn, snakes, 1)
    largest = largestSnake(bo, sn, snakes) 


    # If just me and ally 
    if (ally and duel): 
        interruptlist.append(['Ally', 'Forfeit'])
        
    # In the sauce - get food, or get out 
    if (start in bo.hazards): 
        interruptlist.append(['Eat', 'Best'])
        interruptlist.append(['Survive', 'Hazard'])
        reason.append('in the sauce')
        # strategyinfo['anylength'] = 1
        strategyinfo['clear'] = 1
        

    # Kill interrupt -- larger than 
    t = killPath(bo, snakes)
    if (len(t)):
        interruptlist.append(['Kill', 'Collide'])
        strategyinfo['killpath'] = t
        reason.append('killpath was identified')
    

    # Kill interrupt -- cut off path 
    t = enemyEnclosed(bo, sn, snakes)
    if (len(t)):
        interruptlist.append(['Kill', 'Cutoff'])
        strategyinfo['killcut'] = t
        reason.append('enclosed enemy was identified')


    # Critical health interrupt -- get food
    if (health <= CONST.healthCritical):
        interruptlist.append(['Eat', 'Any'])
        reason.append('health was low')

    if (ally and duel): 
        interruptlist.append(['Ally', 'Tail'])
    
    # Kill logic 
    if (larger and duel): 
      # Control space 
      interruptlist.append(['Control', 'Space'])
      strategyinfo['attack'] = 1
      
      # Prison logic (if avaialable)
      for sid in snakes:
        if sid != you:
          snek = snakes[sid]
          # Check if snake in prison
          if (prison := bo.enclosedPrison(snek, head=start)):
            strategyinfo['prison'] = []
            # Check weakest prison bar
            for bar in prison: 
              target = bar['point']
              expires = bar['expires']

              try:               
                dist = len(bo.best[str(start)][str(target)]['path'])
              except:
                # Key doesn't exist or no route 
                dist = -1 
              
              # print("DEBUG BAR", target, dist, expires)

              # Route distance equals bar expiry 
              if(expires == dist):
                strategyinfo['prison'].append(target)
                # Only route to first point (otherwise N points in tail)
                interruptlist.append(['Control', 'Prison'])
                reason.append('prison was identified')
                break 

      # print("DEBUG PRISON", prison, bo.best[str(start)][str([8, 9])], strategyinfo['prison'])
    
        

    # t = foodNearby(bo, sn, snakes)
    # if (len(t)):
    #   interruptlist.insert(0, ['Eat', 'Best'])

    # End game - Control space
    if (health > CONST.healthLow and largest and length >= CONST.lengthEndGame and duel):
        interruptlist.append(['Control', 'Box'])
        for sndata in snakes: 
          sid = snakes[sndata].getId() 
          if sid != you:
            strategyinfo['enemy'] = snakes[sndata]

        reason.append('duel and largest. length: '+str(length))

    # Mid game - Idle centre 
    # if (health > CONST.healthMed and length >= CONST.lengthMidGame):
    if (largest and health > CONST.healthMed and length >= CONST.lengthMidGame):
        interruptlist.append(['Idle', 'Centre'])
        reason.append('largest snake. length: '+str(length))
    

    # Early game - Survive & eat 
    # or (health > CONST.healthMed and length < CONST.lengthMidGame
    # if (numMovesAvailable(bo, start) < length):
    #     interruptlist.append(['Survive', 'Weight'])
    #     reason.append('less than X moves available')

    # Interrupt triggered
    if (len(interruptlist)):     
        bo.logger.log('interrupt', str(interruptlist), str(reason))

    # print(reason)
    sn.setStrategyInfo(strategyinfo) 
    sn.setInterrupt(interruptlist) 
   

def stateMachine(bo:board, sn:snake, snakes:dict, foods:list, enemy=False):
    """
    Set the target and route for the turn
    (0) Check for interrupts (see checkInterrupts)
    (1) Find a target
    (2) Find route to target 
    (3) Find route padding (check safety) 
    (4) Check target, route, route padding 
    (5) Repeat until found  
    (6) If not found - select best route (see makeMove)
    ==
    bo:     boardClass as board 
    sn:     snakeClass as snake 
    snakes: list[] of snakes  
    ==
    return: none
    (set snake variables)
      sn.setRoute()
      sn.setTarget()
      sn.addRoutes()
    """
    
    depth_strategy = CONST.strategyDepth
    depth = CONST.lookAheadPathContinue
    
    # Strategy
    strategy = []
    reason = []

    # Snake 
    start = sn.getHead()
    length = sn.getLength()
    # body = sn.getBody()
    tail = sn.getTail()
    numsnakes = len(snakes)
    if (numsnakes == 2):
        duel = True
    else:
        duel = False 

    # Inputs to state machine 
    interruptlist = sn.getInterrupt() 
    strategyinfo = sn.getStrategyInfo()
    
    # Our strategy 
    if not enemy:
        if not 'clear' in strategyinfo:      
          strategylist_default = [['Eat', 'Best'], ['Control', 'Space'], ['Survive', 'Tail'], ['Survive', 'Rfactor']]
          # strategylist_default = [['Eat', 'Best'], ['Control', 'Space'], ['Survive', 'Rfactor'], ['Survive', 'Tail'], ]
        else: 
          strategylist_default = [] 

    # Enemy strategy 
    else:
        strategylist_default = [['Idle','Wall'], ['Eat', 'Simple']]
        # ['Control', 'Space'], ['Survive', 'Weight']]
        depth_strategy = CONST.strategyDepthEnemy
        depth = min(length, CONST.lookAheadPathContinueEnemy) 
    
    # Add interrupts 
    if len(interruptlist):
      # interruptlist - delete every turn 
      strategylist = interruptlist + strategylist_default
      reason.append('interrupt was triggered')
    
    else:
      strategylist = strategylist_default
    
    foodsort = fn.findClosestItem(foods, start)
    
    # Get available directions 
    dirns_avail = bo.findEmptySpace(start, dirn=False)
    # print("DEBUG DIRNS AVAIL", dirns_avail)

    routepadding_method = 'rfactor'
    keepLooking = False 

    # tail = sn.getTail()
    # alltails = getSnakeTails(snakes)

    # State machine 
    hurry = False
    sauce = False 
    i = 0  

    while 1:

      # Reset every turn 
      found = False 
      ignoreThreat = False 

      lookahead = max(depth, fn.findLargestLength(snakes) + 1)
      
      target = []
      route = []
      route_padded = []
      weight_padding = CONST.routeThreshold
      weight_route = CONST.routeThreshold
        
      if (not len(strategylist)): 
        # Terminate search 
        route = [] 
        target = [] 
        reason = 'last strategy reached'
        break 
    
      strategy = strategylist.pop(0)
      reason = 'next strategy'
        
      target_method = ""
      route_method = "" 
      
      # bo.logger.log('strategy %s reason:%s list:%s info:%s' % (str(strategy), str(reason), str(strategylist), str(strategyinfo)))

      # Test a particular strategy 
      # strategy = ['Eat', 'Best']

      if(strategy[0] == 'Kill'):
          
          if (strategy[1] == 'Collide'):
            # HEAD ON COLLISION 
            target = strategyinfo['killpath']   
            target_method = "killPath" 
            # bo.logger.log('strategy-killpath', 'killPath', str(start), str(length), str(target))
            # Do not repeat strategy 

          if (strategy[1] == 'Cutoff'):
            if len(strategyinfo['killcut']):
              target = strategyinfo['killcut'].pop()
              target_method = "killCut"
              strategylist.insert(0, strategy)
              # If duel, we only need more turns than the enemy to win 
              if duel: 
                lookahead = CONST.lookAheadEnemy

            else: 
              # Repeat until no more paths 
               pass 
             
            # bo.logger.log('strategy-killpath', 'killCut', str(start), str(length), str(target))
            
      # 
      if(strategy[0]=='Ally'):

          # Forfeit, no friendly fire 
          if (strategy[1] == 'Forfeit'):
            
            route_padded = [start * lookahead]
        
          # Tail 
          if (strategy[1] == 'Tail'):

            ally = strategyinfo['ally']
            target = snakes[ally].getTail()
        

      if(strategy[0]=='Control'):

          if (strategy[1] == 'Prison'):
            # Target equals weakest bar 
            target = strategyinfo['prison'].pop(0)
            routepadding_method = 'rfactor' # strategyinfo['padding']

            if(len(strategyinfo['prison'])):
                strategylist.insert(0, strategy)
            
          # target = bo.findClosestNESW(start)  
          if (strategy[1]=='Space'):

            if 'attack' in strategyinfo: 
                aggro = True 
            else: 
                aggro = False 
            
            target = controlSpace(bo, sn, snakes, aggro=aggro)
            
            # print("CONTROL SPACE", target, aggro)
            # target_method = "controlSpace"
            # bo.logger.log('strategy-route', "CONTROL SPACE", str(start), str(target))
 
          
          if (strategy[1]=='Box'):
            
            if not 'control' in strategyinfo: 
              strategyinfo['control'] = 0   # 0-a, 1-b, 2-c  
            
            # try: 
            step = strategyinfo['control']
            them = strategyinfo['enemy']
            
            # Get closest three vertices of enemy snake 
            targets = bo.findSnakeBox(start, them)
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
            # bo.logger.log('strategy-control', str(step), str(target), '')

    
      if(strategy[0]=='Eat'): 

          # No food -- change strategy
          # Sort by closest food
          if(strategy[1] == 'Best'):
            # Look for closest N foods 
            if(len(foodsort) and i <= CONST.foodsToSearch):
              # print("FOODS", foodsort)
              target = findBestFood(foodsort, bo, sn, snakes)
              target_method = "findBestFood"
              # if(not len(target)):
              # Try next food 
              foodsort.pop(0)
              if(len(foodsort)):
                strategylist.insert(0, strategy)
            

          if(strategy[1] == 'Any'):
            if(len(foodsort)):
              target = foodsort.pop(0)
              target_method = "findAnyFood"
              # if(not len(target)):
              # Try next food 
              ignoreThreat = True 
              strategylist.insert(0, strategy)


          if(strategy[1] == 'Simple'):
            if(len(foodsort)):
              target = foodsort.pop(0)
              target_method = "findSimpleFood"
              # if(not len(target)):
              # Try next food 
              strategylist.insert(0, strategy)
          
          # bo.logger.log('strategy-eat', str(target))


      if(strategy[0]=='Idle'):

        # Default
        if(strategy[1]==''):
          strategy[1]=='Centre'
          

        if(strategy[1]=='Centre'): 
            target = bo.findCentre(start)
            target_method = "findCentre"
            if (not(len(target))):
              # If already in centre .. 
              # strategylist.pop(0) 
              strategylist.append(['Idle', 'Centre'])

            else: 
              # TODO:  Very computationally intensive.  Temporary remove from retry ..
              # strategylist.append(strategy)
              pass 

            # bo.logger.log('strategy-findcentre', 'Centre')

        # Find nearest wall 
        if(strategy[1]=='Wall'):   
            target = bo.findClosestWall(start)
            target_method = "findClosestWall"
            if (not len(target)):
              pass 
              # Already on a wall 
              # Do not repeat 
              # strategylist.append(['Idle', 'Centre'])

            else:
              # Repeat until interrupt 
              strategylist.insert(0, strategy)
              
            # bo.logger.log('strategy-findwall', target)
            
    
      if(strategy[0]=='Survive'):
          # Defensive 

          survive_execute = ['Survive', 'Run']
          
          # If hazard board -- increase threat after we have looked for food 
          if(len(bo.hazards) and not sauce):
            # set hazards to solid (except food)
            bo.increaseHazard(foods=foods, multiplier=10)  # .. solid=True) 
            # redo routing (move this up for performance)
            bo.updateBest(start, turn=0, snakes=snakes, foods=foods, reason="1")
            sauce = True

          if(strategy[1]=='Weight'):  
            dirns = dirns_avail + []    # copy.copy
            routepadding_method = "weight"
            strategylist.insert(0, survive_execute)
            
          if(strategy[1]=='Length'):  
            dirns = dirns_avail + []    # copy.copy
            routepadding_method = "length"
            strategylist.insert(0, survive_execute)
            
          if(strategy[1]=='Tail'):  
            dirns = dirns_avail + []    # copy.copy
            routepadding_method = "tail"
            strategylist.insert(0, survive_execute)

          if(strategy[1]=='Rfactor'):  
            dirns = dirns_avail + []    # copy.copy
            routepadding_method = "rfactor"
            strategylist.insert(0, survive_execute)

          if(strategy[1]=='Hazard'):  
            dirns = dirns_avail + []    # copy.copy
            routepadding_method = "rfactor"
            strategylist.insert(0, survive_execute)

          if(strategy[1]=='Random'):  
            dirns = dirns_avail + []    # copy.copy
            routepadding_method = "tail"
            strategylist.insert(0, survive_execute)
            
          if(strategy[1]=='Run'):  
            # Iterate through all directions 
            if(len(dirns)):
                keepLooking = True 
                target = dirns.pop(0) 
                strategylist.insert(0, strategy)
                target_method = "survive"
            else: 
                keepLooking = False 
                # Routes are added to snake routes & decision made in final stage 
                

          # bo.logger.log('strategy-survive', 'Target: %s' % (target))
        

      # (2) Find route to target 
      # Look ahead by lenght of largest snake 
      
      # print("DEBUG TARGET", target)
      if (len(target)):
        # Find route to target 
        if 'numpy' in str(type(target)):
            # Target is an area 
            # bo.logger.log('strategy-target', "TARGET %s %s %s" % (str(strategy), str(target), str(i)))
            route, weight_route = bo.fuzzyRoute(start, target, sn)
            route_method = "fuzzyRoute"

        elif 'list' in str(type(target)) and bo.inBounds(target):
            # Target is a point 
            route, weight_route = bo.route(start, target, sn)
            # bo.logger.log('strategy-target', "TARGET %s %s %s %s %s" % (str(strategy), str(start), str(target), str(route), str(weight_route)))
            route_method = "route"

        # if(len(route)):
        #   while(route[0] == start):
        #     route.pop(0)

        # (3) Find route padding
        if (len(route) and not enemy):
            
            # Pad out route to N moves.  Look ahead by lenght of largest snake 
            # if route[-1] == tail:
            #     # IF tail, assume infinite moves 
            #     route_padded = route + [tail] * lookahead 
            #     weight_padding = 0 

            # # elif killcollide ... 
            #     # route_padded += [tail] * lookahead 
            #     # weight_padding = 0 

            # else:
                route_padded, weight_padding = bo.routePadding(route, snakes, foods, depth=lookahead, method=routepadding_method) 
            
          

      # (4) Check target, route, route padding are safe 
      weight_total = weight_route + weight_padding
      route_length = len(route_padded)
      # print("WEIGHT", weight_padding, weight_route)
      
      # TODO:  Clean up all the blank & routes to start ..       
      if not (route in [[], [start]]):
        sn.addRoutes(route_padded, weight_total, route_length, strategy[0])
      
      bo.logger.log("strategy-add", "STRATEGY ROUTE %s Strategy: %s Target:%s Route: %s Weight: %s, Length: %s %s keeplooking|ignorethreat|enemy: %s %s %s" %
                          (str(i), str(strategy), str(target),
                          route_padded, weight_total, route_length, lookahead,
                          keepLooking, ignoreThreat, enemy))
              
      
      # Check if this is a "good" route for us 
      if ((weight_total <= CONST.pointThreshold and 
            (len(route_padded) >= lookahead)) and 
            not keepLooking):   
          found = True 
          
      # We are desparate.  Ignore length & route threshold except hazard/solid death
      elif (ignoreThreat and weight_total < 2 * CONST.routeThreshold):
          found = True 
          
      # Enemy ignores point threshold 
      elif (enemy):
          found = True 
      
      # Safe path to & away found
      if (found):
          route = route_padded + []   # copy.copy
          # bo.logger.log('strategy-found', 'PATH FOUND')
          
          # Normal exit from loop
          break
      # else:
      #     bo.logger.log('strategy-found', 'PATH NOT FOUND')

      # 5) Next strategy -- keep looking.  Check if time exceeds limit 
      st = bo.logger.getStartTime()
      diff = 1000 * (time.time() - st)
      if diff > CONST.timeEnd: 
          hurry = True   
          


      # Termination of loop 
      # No more strategy
      # Time expired 
      # Max depth (TODO: Remove)
      if (not len(strategylist) or 
            hurry or 
            i > depth_strategy):
          
          bo.logger.log('timer-hurry strategy:%s hurry:%s depth:%s / %s' % (len(strategylist), hurry, i, depth_strategy))
      
      # print("STRATEGY EXIT", len(strategylist), hurry, depth)
      #   Exit loop
          target = []
          route = []
          break
  
      # bo.logger.log('strategy-update','%s not found. Try next strategy. i: %s' % (str(strategy), i))
      bo.logger.timer('Strategy search')

      i = i + 1 
        
    # TODO: Delete -- no longer required for stateless 
    # Remove duplicates from strategy list 
    # stl_unique = []
    # for stl in strategylist: 
    #     if not stl in stl_unique:
    #       stl_unique.append(stl)  
    # strategylist = copy.copy(stl_unique)

    sn.setRoute(route)
    sn.setTarget(target)


# TODO:  Consider combining state machine (target) and 

# Check snake target,  return next move 
def makeMove(bo: board, sn: snake, snakes) -> str:
    """
    Translates route to a direction 
    Use primary route, otherwise select "best route" from available 
    ==
    bo:     boardClass as board 
    sn:     snakeClass as snake 
    snakes: list[] of snakes  
    ==
    return: "up", "down", "left" or "right"
    """
    
    # 5) Route Found 
    route = sn.getRoute()
    start = sn.getHead()
    
    route_method = ''
    found = False 
    p = []

    # print("SNAKE PATHS", sn.getRoutes())
    while len(route):
      # Preferred route 
      route_method = 'route_stateMachine'
      p = route.pop(0)
      if p != start:
        found = True 
        break 

    # 6.1) Route not found - select least worst route 
    if (not found): 
        # Add default routes 
        # sn.addRoutes()
        # Get all routes  
        routes = sn.getRoutes() 
        bo.logger.log('route-found %s' % str(routes))
        # Best = Longest length (eg. 25) / lowest weight (50%) 
        rfactor = 0

        if len(routes):
          route = []
          for r in routes:
            # len(r['route'])
            # TODO: Model this ..

            # R20211104 - changed from 10*len to 10*2^len 
            path_length = min(CONST.lookAheadPathContinue, r['length'])
              
            if r['weight'] == 0:
              # rnew = 100 * pow(1.2, r['length'])
              rnew = pow(path_length, 3)
            else:  
              # rnew = 100 * pow(1.2, r['length']) / r['weight'] 
              rnew = pow(path_length, 3) / r['weight']
            # print("DEBUG ROUTE", rnew, r)

            if rnew > rfactor:
              rfactor = rnew 
              route = r['route']
              # sn.setTarget(r['target'])
              # sn.setRoute(r['route'])
              # sn.setTarget
              
          while len(route):
            # Preferred  route 
            route_method = 'route_getRoutes'
            p = route.pop(0)
            if p != start:
              found = True 
              break 

        # print(bo.markovs)
        bo.logger.log('route-last-resort', 'rfactor:%.2f route:%s' % (rfactor, str(p)))
        

    # 7) Translate next point to direction
    move = fn.translateDirection(start, p)
    
    bo.logger.log('make move', str(start), str(p), str(move), str(route_method))
    
    sn.setTarget(p)
    sn.setRoute(route)
    sn.setMove(move)    
    # return move


def defaultRoutes(bo, sn, snakes):
    # TODO: Review & include default route

    start = sn.getHead()
    # finish = sn.getTarget()    
    route_weight = CONST.routeThreshold
    route_method = ''
    
    routes = []

    # 6.2) Still no route - Use lookahead (route padding)
    # TODO: Combine lookahead & dijkstra to avoid 
    #   collision with high threat 
    # if (not len(p) or not bo.inBounds(p)):
    #   route_method = 'route_findLargestPath'
    #   route = bo.findLargestPath([start], snakes)
    #   if len(route) > 1:
    #     # TODO: Cleanup routes -- some include start, others don't
    #     # Remove head (if exists)
    #     if (route[0] == start): 
    #       route.pop(0)
    #     try:
    #       p = route.pop(0)
    #     except Exception as e:
    #       bo.logger.error('exception', 'makeMove', str(e))

    # 6.3) Still no route - Chase any tail
    # if (not found and not sn.getEating()):
    #   route_method = 'route_chaseTail'
    #   for d in CONST.directions:
    #     # Check each direction 
    #     t = list( map(add, start, CONST.directionMap[d]) )
    #     if (bo.inBounds(t)):
    #       # Find tail
          
    #       w = bo.trails[t[0],t[1]]
    #       if w == 1:
    #         p = copy.copy(t)
    #         wmin = copy.copy(w) 
    
    # 6.4) Still no route - Use lowest gradient
    # route_method = 'route_dijkstra'
    # wmin = CONST.routeThreshold
    # for d in CONST.directions:
    #   # Check each direction 
    #   t = list( map(add, start, CONST.directionMap[d]) )
    #   if (bo.inBounds(t)):
    #     try: 
    #       # Find lowest weight
    #       w = bo.dijkstra[0][t[0],t[1]]
    #       if w < wmin:
    #         p = copy.copy(t)
    #         wmin = copy.copy(w) 

    #     except Exception as e:
    #       pass 

      # sn.addRoutes(route_padded, weight_total, route_length, strategy[0]))
    
    # 6.5) Still no route - Use self.enclosd available moves 
    # if (not len(p) or not bo.inBounds(p)):
    #   route_method = 'route_dijkstra'
    #   for d in CONST.directions:
    #     moves_avail = bo.enclosed[move] 
    #     ..


    # 6.6) Still no route - Wipe markovs & try again
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
    

# == HELPERS == 

def largestSnake(bo, us, snakes, larger=CONST.controlLargerBy):
    # if larger than enemy
    
    you_len = us.getLength() 
    largest = True 
    for identity in snakes:
      sn = snakes[identity]
      if sn != us:
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
    collide_target = []

    # Check each snake 
    for identity in snakes:
      sn = snakes[identity]
      if sn.getType() != "us":
        enemy_len = sn.getLength()
        enemy_head = sn.getHead()
        dist = fn.distanceToPoint(you_head, enemy_head)

        dirn_avail = bo.findEmptySpace(enemy_head, dirn=False)

        # print("KILL COLLIDE", you_len, enemy_len, dist, radius, dirn_avail)
        # Only trigger killpath if (a) larger (b) close and (c) enemy has one direction available 
        if (you_len > enemy_len) and (dist <= radius) and len(dirn_avail) == 1:
          
          collide_target = dirn_avail[0]

    # print("DEBUG COLLIDE", collide_target)
    return collide_target      
    

def numMovesAvailable(bo, start):
    """
    Return maximum number of moves in any direction   
    (expensive)
    ===
    start:   location (eg. [7, 3])
    === 
    int       maximum length in any direction  

    """
    en = bo.enclosedSpacev2(start)
    enclosed = copy.copy(bo.enclosed)
    max_len = max(enclosed, key=enclosed.get)
    return int(enclosed[max_len])


def enemyEnclosed(bo:board, us:snake, snakes:list): 
    """
    Returns a list of targets we can enclose the enemy 
    (1) Find squares we can get to first 
    (2) Calcualte enemy chance board, looking for 100% 
    (3) Find intercept of 100% and squares we can get to 
    ==
    bo:         boardClass as board 
    us:         snakeClass as snake
    snakes:     list of snakes 
    ==
    return: targets (list of targets to enclose enemy)
    """ 
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
        targets = findInterceptPath(head, bo, board_closest, board_chance)

        # print(str(board_closest))
        # print(str(board_chance))
        
        # TODO: move these tables to setEnemy ... 
        # Set / get enemy boards  
        # sn.setClosest(board_closest)
        # sn.setChance(board_chance)
      

    return copy.copy(targets)


def findInterceptPath(start, bo:board, board_dist, board_chance, chance=CONST.interceptMin):
    """
    Returns a sorted list of intercept paths that 
    (a) enemy snake will route through (%chance)
    (b) we can get to before the enemy 
    ==
    start:      our location 
    bo:         boardClass as board 
    board_dist: ..
    board_chance: .. 
    chance:     ..
    ==
    return: intlist (list of intersection points)
    """ 

    target = start 
    if not board_chance is None:
      intercepts = np.nonzero(board_chance > chance)
    else:
      return []
    
    intdict = {} 
        
    # TODO:  Better way to sort a list with function (eg list->dict-list)?
    for i in range(0, len(intercepts[0])):
        try:
            target = [intercepts[0][i], intercepts[1][i]]
            dist = fn.distanceToPoint(start, target)
            intdict[str(target)] = dist
        except Exception as e:
            # TODO: Look at these errors 
            bo.logger.error('exception', 'findInterceptPath#1', str(e)) 
            
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
            bo.logger.error('exception', 'findInterceptPath#1', str(e)) 
        
    return intlist


def findBestFood(foodsort:list, bo:board, us:snake, snakes:list): 
    """
    Food strategy.  Target food if 
    (a) safe to do so and 
    (b) enemy is not closer
    ==
    foodsort:   food list sorted by distance (closest)
    bo:         boardClass as board 
    sn:         snakeClass as snake 
    snakes:     list[] of snakes  
    ==
    return:     target    (points, eg. [1,2])
    """ 
    # Preserve objects 
    foods = foodsort + []   # copy.copy

    # How many moves until we believe a target
    targetConfidence = 3
    # Check if food under threat (ie. snake enroute) 
    foodthreat = {}
    # Init dict - empty => null 
    reason = []

    for food in foods: 
        foodthreat[str(food)] = []

    start = us.getHead()
    length = us.getLength()

    # Check which sneks are targeting which food  
    for snid in snakes:
        # Get snake
        sn = snakes[snid] 
        if sn.getType() != 'us': 
            # Reset target
            sn.setTarget([])
            # Check each food 
            for food in foods:
              # Get snake body + head (ie. path history)
              history = sn.getHistory()
              
              # history.insert(0, sn.getHead())
              a = []
              # If last three paths to food are descending
              if (len(history) >= targetConfidence): 
                for i in range(0, targetConfidence):
                  a.append(fn.distanceToPoint(food, history[i]))

              # Check ascending - ie. recent locations are closser 
              dist_sort = a + []   # copy.copy
              dist_sort.sort() 
                  
              # Compare sorted list to original to see if the same 
              # print("FOOD SORT", history, a, dist_sort)
              if (a == dist_sort):
                  # Check if closer than existing target 
                  target_last = sn.getTarget()
                  dist_last = bo.height + bo.width
                  if (len(target_last)):
                    dist_last = fn.distanceToPoint(history[0], target_last)

                  # Check new target is closer 
                  if a[0] < dist_last or not len(target_last):
                    dist_enemy = a[0]   # copy.copy
                    len_enemy = sn.getLength()
                    foodthreat[str(food)].append({'length':len_enemy, 'dist':dist_enemy})
                    sn.setTarget(food)
                    # bo.logger.log("food target", sn.getId(), sn.getTarget())
                    

    # Check foods for the closest without threat 
    target = []
    for food in foods: 
        # Route exists   
        r, w = bo.route(start, food, us)
        if (len(r)): 

            reason.append('route exists')
            dist = len(fn.getPointsInRoute(r))
        
            # Threat, enemy closer & smaller - pursue??
            # Threat, enemy closer 
            abandon = False 
            if str(food) in foodthreat:
                # t = [len_enemy, dist_enemy]
                threats = foodthreat[str(food)]
                for t in threats:
                    # bo.logger.log("food", food, t)

                    len_enemy = t['length']
                    dist_enemy = t['dist']
                    # print("FOOD THREAT", start, food, t, r, dist, length)
                    # Check other snakes targeting food 
                    if (len(t)):
                        if dist_enemy < dist:
                            abandon = True
                            reason.append('abandon - enemy closer')
                            
                        elif len_enemy >= length and dist_enemy <= dist:
                            abandon = True
                            reason.append('abandon - enemy larger & same dist')

            if not (abandon):
                # Exit search (ie. for food in foods)
                target = food 
                break
                
        else:
            reason.append('no route')
        
        
        break 
        # print(reason)  
        # return copy.copy(target)

    bo.logger.log("stratey eat", food, reason)      
    return copy.copy(target)


def checkFutureDeath(bo:board, us:snake, snakes:list, numfuture=CONST.lookAheadPredictFuture): 
    """
    Play forward the next (future) moves for us and enemies 
    Ignore routes if (a) Head on collision, or (b) No routes 
    TODO: replace enemy play forard with a more generic implementation
      eg. if enclosedSpace ..
          if certainDeath (N=length steps) 
    ==
    bo:     boardClass as board 
    sn:     snakeClass as snake 
    snakes: list[] of snakes  
    ==
    return: dirn_avoid    (points, eg. [1,2])
    """
    # (1) select possible paths for enemy
    dirn_avoid = []
    
    # O(dirs * future * snakes)
    sid_us = bo.getIdentity()
    us = snakes[sid_us]
    length_us = us.getLength()
    steps_us = us.getNextSteps()
    head_us = us.getHead()
    rr = 0

    if not len(steps_us):
        return rr, [] 
        
    for sid in snakes:
        if sid != sid_us:     
            snake = snakes[sid]
            head_enemy = snake.getHead()
            # Ignore snakes too far away to create collision or block route  
            # print("DEBUG DIST", numfuture, head_us, head_enemy, fn.distanceToPoint(head_us, head_enemy))
            if fn.distanceToPoint(head_us, head_enemy) < (2 * numfuture + 1):
             
              length_enemy = snake.getLength()
              steps_enemy = snake.getNextSteps()
              # print("PREDICT ENEMY", steps_enemy)
              # print("CHECK", len(steps_us), len(steps_enemy))
              # print("us", steps_us)
              # print(snake, steps_enemy)

              for step_us in steps_us:
              # Iterate through our steps 
                  conflict = []

                  for step_enemy in steps_enemy:
                      rr += 1
                      # Check against enemy steps 
                      safe = True
                      reason = []
                          
                      if len(step_enemy) == len(step_us):
                      # Look for same turn (same length)
                          
                          # print(step, ourstep, head_us, ourstep[-1])
                          # Exclude circular (U) loops    
                          if (len(step_us) == 1 or 
                                len(step_us) > 1 and 
                                (abs(head_us[0] - step_us[-1][0]) + 
                                abs(head_us[1] - step_us[-1][1])) > 1):
                              
                              if step_enemy[-1] == step_us[-1]:
                                  if (length_enemy > length_us): 
                                    
                                      # Check for collision (same square and we are same / smaller) 
                                      # conflict = step
                                      safe = False 
                                      reason.append("head on collision")

                              else: 
                                  # Combine all the occupied squares  
                                  turn = len(step_enemy)
                                  start = step_us[-1]
                                  future = step_us + step_enemy 

                                  # Minus current position 
                                  future.remove(start)

                                  # Check if we have moves available (I will never die)
                                  found = bo.findEmptySpace(start, future, turn)
              
                                  # No paths
                                  if (not found):
                                      # AND exclude U loops (dumb) 
                                      # conflict = step
                                      safe = False 
                                      reason.append("no path for us")
                                      

                      # print("STEPS us:%s them:%s" % (ourstep, step)) 
                      # if [6, 2] in step_enemy and not safe:
                      #   print("DEBUG - FINAL PATHS ourstep: (%s) conflict:(%s) safe:(%s)" \
                      #       % (step_us, step_enemy, safe)) # steps_enemy
                      
                  
                      if (not safe):
                      # One of the enemy steps is not safe for our step
                      
                          collision = False 
                          for i in range(0, len(step_enemy)-1):
                            if step_enemy[i] == step_us[i]:
                              collision = True 
                          
                          if not collision:
                            ignore=False 
                            # Check whether enemy went through a kill point
                            # Enemy two squares away
                            if fn.distanceToPoint(head_us, head_enemy) == 2:
                              # Smaller 
                              if length_us > length_enemy:
                                # Calculate midpoint
                                collisions = []
                                if head_us[0] != head_enemy[0] and head_us[1] != head_enemy[1]: 
                                    collisions = [[head_us[0], head_enemy[1]], [head_enemy[0], head_us[1]]]
                                else: 
                                    collisions = [[int((head_us[0] + head_enemy[0])/2), int((head_us[1] + head_enemy[1])/2)]]
                                
                                # Went through collision point  
                                if step_enemy[0] in collisions:
                                  ignore = True 

                            if not ignore: 
                                dirn_avoid.append(step_enemy)
                            
                            # print("DEBUG - FINAL PATHS ourstep: (%s) conflict:(%s)" % (ourstep, step)) # steps_enemy
                      
    # Update possible steps (if used)     
    snakes[sid_us].setNextSteps(steps_us)
    
    # return directions to avoid (mark as not reachable)
    # print("CHECK FUTURE", rr)
    return rr, dirn_avoid



# == DEPRECATE / DELETE == 


# def threatPath(bo, sn, dist=2):
#     # if enemy larger 
#     # distance to enemy head < dist 
#     # try to increase dist (eg.)
#       # if cannot do safely ...
#     return False


# def boardControl(bo, sn):
#     # stay n ahead & in same direction 
#     # move n-1 squares in & connect to wall 
#     # loop back to tail path 

#     return []


# def blockPath(bo, sn):
#     # find move that will reduce enemy available squares 
#     return []


# def checkOpenPath(bo, a, b): 
#   # route = getPointsInLine(a,b)
#   # self.solid dijkstra(route, 100)  
#   return True 


# def trackWall(bo, sn, rotation=CONST.clockwise, proximity=0):
    
#     w = bo.getWidth()
#     h = bo.getHeight()
#     a = sn.getHead()       # [0,0] 
#     d = sn.getDirection()  # left, right, up, down
    
#     a1 = []

#     r = rotation    # cw, ccw
#     p = proximity   # 0, 1, 2..

#     # TODO:  Update for proximity (ie. X squares away from)
#     for i in range(0, 4):
#         # Add one point in current direction 
#         a1 = list(map(add, a, CONST.directionMap[d]))
#         # In bounds 
#         if bo.inBounds(a1) :
#             # All other logic in routing engine .. 
#             break 

#         # Rotate direction & try again 
#         if(r == CONST.counterclockwise): 
#             d = CONST.ccwMap[d] 
#         else:
#             d = CONST.cwMap[d]
    
#     # log('strategy-trackwall', str(w), str(h), str(a), str(d), str(r), str(p), str(a1))
#     return a1


# def trackWall2(bo, sn, rotation=CONST.clockwise, proximity=0):
#     # DEPRECATE:  Replace with route / fuzzyRoute logic which incorporates normal routing engine  

#     # TODO:  Update for proximity (ie. X squares away from edge).  
#     w = bo.getWidth()
#     h = bo.getHeight()
#     a = sn.getHead() # [0,0] 
#     d = sn.getDirection()  # left, right, up, down
    
#     # Coordinates - start [ay, ax]
#     ax = a[1]
#     ay = a[0]
#     a1 = [0] * 2

#     r = rotation    # cw, ccw
#     p = proximity   # 0, 1, 2..

    
#     for i in range(0, 4):
#         # Add one point in current direction 
#         a1[0] = ay + CONST.directionMap[d][0]
#         a1[1] = ax + CONST.directionMap[d][1]
        
#         # No collision & in bounds 
#         if( 0 <= a1[0] < w and 0 <= a1[1] < h):
#             bs = bo.solid[a1[0], a1[1]] 
#             bt = bo.threat[0][a1[0], a1[1]] 
#             pt = CONST.pointThreshold
#             ag = sn.getAggro()

#             # Not solid, low threat, not enclosed
#             move = fn.translateDirection(a, a1)
#             length = sn.getLength()
        
#             if (bs < pt and bt < ag and length < bo.enclosed[move]):
#               # print("TRACK-SOLID", str(bo.solid[a1[0], a1[1]]))
#               break
        
#         # Rotate direction & try again 
#         if(r == CONST.counterclockwise): 
#             d = CONST.ccwMap[d] 
#         else:
#             d = CONST.cwMap[d]
     
#     bo.logger.log('strategy-trackwall', str(w), str(h), str(a), str(d), str(r), str(p), str(a1))
#     return a1


# def getSnakeTails(snakes): 
#     # Returns coordinates of all snake tails in list 
#     tails = []
#     for snid in snakes:
#       sn = snakes[snid]
#       tails.append(sn.getTail())

#     return copy.copy(tails)
