
import random as rand
import numpy as np

# from typing import Dict
# import pandas as pd

import constants as CONST 

# move = getMove(pHead, route.pop(0)) 
def getDirection(a, b): 
    
    move = ""

    # X - left, right [0][X]
    # Y - up, down.   [Y][0] 
    try: 
      ay = a[0]
      ax = a[1]
      by = b[0]
      bx = b[1]
      
      if (bx < ax): 
          move = "left"
      if (bx > ax): 
          move = "right"
      if (by < ay): 
          move = "down"
      if (by > ay): 
          move = "up" 

    except: 
      pass 
            
    if (move == ""): 
        # Should never happen 
        moves = ["right", "left", "up", "down"]
        move = rand.choice(moves)
    
    return move

  
def comparePoints(a, b, t="array"): 

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

    except: 
      return -1


# def distanceToPointComplex(a, b):
    # if objects in the way .. 
    

def getPointsInLine(a, b):
    # a = [0, 0], b = [2, 0]
    # a = [2, 0], b = [2, 2]
    
    # print("LINE POINTS")
    # print(str(a) + str(b))
    
    # TODO:  
    # Confirm a & b are list [a, b]
    # Confirm ax, bx are int
    # Paths inverted somewhere .. 
  
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


def getPointsInRoute(rt, a=[]):

    # TODO: Check is of form of route is always [a, b, c] and not [b, c].  optional to provide a, as separate variable until resolved, eg. if len(a) 

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

    return pts


# Invert coordinate system 
def printMap(m):
    # Iterate through map array backwards
    try: 
      h = len(m)
      w = len(m[0])

      md = np.zeros([h,w],np.intc)

      for y in range(0, h):
        for x in range(0, w): 
          md[h-y-1,x] = m[y,x]

      print(md)
    
    except: 
      print("ERROR: Could not print map")

def raiseError(e):
    # error_status = True 
    # error_text = e
    print("ERROR: " + str(e))
    return True

# == DEPRECATE == 

# Rotate a direction
# def rotateMove(a, d=CONST.clockwise): 

#   if (CONST.counterclockwise):
#     if (CONST.up):
#         move = CONST.left
#     elif (CONST.left):
#         move = CONST.down
#     elif (CONST.down):
#         move = CONST.right
#     else: # CONST.right
#         move = CONST.up

#   else: # CONST.clockwise:  
#     if (CONST.up):
#         move = CONST.right
#     elif (CONST.right):
#         move = CONST.down
#     elif (CONST.down):
#         move = CONST.left
#     else: # CONST.left
#         move = CONST.up

#   return move

