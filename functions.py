
# import random as rand
# import constants as CONST 
# from typing import Dict
# import pandas as pd

import numpy as np
import copy as copy 

from logger import log


def translateDirection(a, b): 
    
    # X - left, right [0][X]
    # Y - up, down.   [Y][0] 
    move = 'none'
    
    try: 
      if (not len(a) or not len(b)): 
        return move

      ay = a[0]
      ax = a[1]
      by = b[0]
      bx = b[1]
      
      if (bx < ax): 
          move = 'left'
      if (bx > ax): 
          move = 'right'
      if (by < ay): 
          move = 'down'
      if (by > ay): 
          move = 'up' 

    except Exception as e:
        log('exception', 'translateDirection' + str(a) + ':' + str(b), str(e)) 
          
        move = ""
        #     # Should never happen 
        #     moves = ["right", "left", "up", "down"]
        #     move = rand.choice(moves)
    
    return move

  
def comparePoints(a, b, t="array"): 
    # DEPRECATE:  all points standardised as array / list 
    if(a['x'] == b['x'] and a['y'] == b['y']):
        return True
    else:
        return False 


def distanceToPoint(a, b):
    if(isinstance(a,dict) or isinstance(b,dict)):
      print("ERROR: distanceToPoint(a,b) expecting array list, received dict)")
      return -1 

    try:

      ax = a[1]
      bx = b[1]
      ay = a[0]
      by = b[0]
    
      dx = abs(ax - bx)
      dy = abs(ay - by)
      d = dx + dy
      return d

    except Exception as e:
      log('exception', distanceToPoint, str(e))  
      return -1


# def distanceToPointComplex(a, b):
    # if objects in the way .. 
    

def getPointsInLine(a, b):
    # a = [0, 0], b = [2, 0]
    # a = [2, 0], b = [2, 2]
    ax = a[0]
    ay = a[1]
    bx = b[0]
    by = b[1]
    line = []

    # Point (not a line)
    if (ax == bx) & (ay == by): 
        return [] 
    
    # Line along Y 
    elif (ax == bx):
        # Decide up or down 
        if (ay > by):
            inc = -1
        else:
            inc = 1
        
        ayd = ay
        while (ayd != by):
            ayd = ayd + inc
            line.append([ax, ayd])

    # Line along X
    elif (ay == by):
        # Decide up or down 
        if ax > bx: 
            inc = -1
        else:
            inc = 1
        
        axd = ax    
        while (axd != bx):
            axd = axd + inc
            line.append([axd, ay])
            
    # Not a perpendicular line 
    else:
        return []

    # line.append(b)
    # print("LINE")
    # print(str(line))
    return line


def getPointsInRoute(route, a=[]):

    # TODO: Check is of form of route is always [a, b, c] and not [b, c].  optional to provide a, as separate variable until resolved, eg. if len(a) 
    rt = copy.copy(route)
    # If point, return point 
    if (len(rt) < 2): 
      return rt

    # Translate vectors into points 
    pts = [] 
    va = []
    
    for vb in rt:
    # Skip first point (need two points for line)  
    
        if (len(va)):
            # Add points in line 
            # print(str(va)+str(vb))
            pts = pts + getPointsInLine(va, vb)

        va = vb 

    pts.insert(0, rt[0])
    # print("GETPOINTS", pts, rt)
    
    return pts


def printMap(m):
    # Invert coordinate system 
    # Iterate through map array backwards
    try: 
      h = len(m)
      w = len(m[0])

      md = np.zeros([h,w],np.intc)

      for y in range(0, h):
        for x in range(0, w): 
          md[h-y-1,x] = m[y,x]

      print(md)
    
    except Exception as e:
      log('exception', 'printMap', str(e))


def XYToLoc(pt):

    if(isinstance(pt, dict)):
      px = pt['x']
      py = pt['y']
      return [py, px]
      
    elif(isinstance(pt, list)):
      return pt

    else:
      return [-1,-1]


def raiseError(e):
    # error_status = True 
    # error_text = e
    print("ERROR: " + str(e))
    return True


def findClosestItem(foods, start):
  # Return sorted list of items (foods) closest to point (start)

  # print("FIND CLOSEST ITEM")
  # print(str(start), str(foods))

  fooddict = {}
  for food in foods:
      dist = distanceToPoint(start, food)
      fooddict[str(food)] = dist
          
  foodsort = dict(sorted(fooddict.items(), key=lambda item: item[1]))
  
  foodlist = []
  for fs in foodsort:
      try: 
          y, x = fs.strip('][').split(', ')
          y = int(y)
          x = int(x)
          foodlist.append([y, x])
      except Exception as e:
          log('exception', 'findClosestItem', str(e))

  # print(str(foodlist))
  
  return copy.copy(foodlist)


def isClosest(a, b, others):
    # Return true if you are closest point 

    closest = []
    us_dist = distanceToPoint(a, b)

    for o in others:
      them_dist = distanceToPoint(o, b)
      if (them_dist < us_dist):
          closest = o

    if (a == closest):
      return True 

    else: 
      return False 

# == DEPRECATE / DELETE == 
