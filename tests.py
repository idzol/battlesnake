"""
Ref - https://docs.python.org/3/library/unittest.html
Shell - python -m unittest tests.py -v
        # python tests.py -v
"""
import unittest
import json 
import constants

import functions as fn 

import pandas as pd
import numpy as np

# from functions import getRouteToTarget
# selectDestination, chooseMove, getDirection, comparePoints, chartPath, setPath, initialise_snake, raiseError

# from snakeClass import snake
from boardClass import board
# from itemClass import item

# Test arrays 

test_food = np.array(
[[12,31, 0, 0, 0, 0, 0],
 [11,31, 0, 0, 0, 0, 0],
 [10,31, 0, 0, 0, 0, 0],
 [ 0,31, 0, 0, 0, 0, 0],
 [ 0,31, 0, 0, 0, 0, 0],
 [ 0,31, 0, 0, 0, 0, 0],
 [ 0, 0, 0, 0, 0, 0, -30]])

test_foodpath = np.array(
[[ 0, 0, 0, 0, 0, 0, 0],
 [ 1, 0, 0, 0, 0, 0, 0],
 [ 2, 0, 0, 0, 0, 0, 0],
 [ 3, 0, 0, 0, 0, 0, 0],
 [ 4, 0, 0, 0, 0, 0, 0],
 [ 5, 0, 0, 0, 0, 0, 0],
 [ 6, 7, 8, 9,10,11,12]])
    
json_vals = {

    'height':11,
    'width':11,
    'you_body':"[{'x': 1, 'y': 4}, {'x': 1, 'y': 5}, {'x': 1, 'y': 5}]",
    'you_head':"{'x': 1, 'y': 4}",
    'you_len':3,
    'hazard':"[]",
    'food':"[{'x': 0, 'y': 6}, {'x': 5, 'y': 5}]"
    
}

# JSON Template for data 

json_template = """{{'game': 
 {{'id': '0549018e-0a9f-4401-97b2-115f1f82e33b', 'ruleset': 
 {{'name': 'solo', 'version': 'v1.0.22', 'settings': 
 {{'foodSpawnChance': 15, 'minimumFood': 1, 'hazardDamagePerTurn': 0, 'royale': 
 {{'shrinkEveryNTurns': 0}}, 'squad': 
 {{'allowBodyCollisions': False, 'sharedElimination': False, 'sharedHealth': False, 'sharedLength': False}}}}}}, 'timeout': 500}}, 'turn': 1, 
 'board': {{
 'height': $height, 
  'width': $width, 
 'snakes': [{{'id': 'gs_JMJSHhdpyWtGSj66Sv3Dt8yD', 
 'name': 'Test snek', 'latency': '172',  'health': 99, 
 'body': {you_body}, 
 'head': {you_head}, 
 'length': {you_len}, 
 'shout': '', 'squad': ''}}], 
 'food': $food , 
 'hazards': {hazard} }}, 
 'you': {{'id': 'gs_JMJSHhdpyWtGSj66Sv3Dt8yD', 'name': 'Test snek', 'latency': '172', 
 'health': 99, 
 'body': {you_body}, 
 'head': {you_head}, 
 'length': {you_len}, 
 'shout': '', 'squad': ''}}}}
"""

if __name__ == "__main__":
    unittest.main()
    # getRouteToTargetTest()
    # boardClassTest()

class functionsTest(unittest.TestCase):

  def test_getDirection(self): 
      
      a = [1,1]
      bn = [[1,2],[1,0],[2,1],[0,1]]
      cn = ['right','left','down','up']
      # X - left, right [0][X]
      # Y - up, down.   [Y][0] 

      # QA: consider [1,1], better error handling  etc.. 
      i = 0
      for b in bn: 
        c = cn.pop(0)
        result = fn.getDirection(a, b)
        self.assertEqual(result, c)


  def test_comparePoints(self):

      a = {'x':5, 'y': 6}
      b = {'y':6, 'x': 5}

      result = fn.comparePoints(a, b)
      self.assertEqual(result, True)
      
      b = {'y':6, 'x': 7}

      result = fn.comparePoints(a, b)
      self.assertEqual(result, False)
      

  def test_distanceToPoint(self):
  
      an = [[0,0],[10,10],[5,10],[0,5],[1,1],[1,1],[1,1],[1,1],[1,1]]
      bn = [[10,10],[0,0],[0,5],[10,5],[1,2],[1,0],[0,1],[2,1],[1,1]]
      cn = [20,20,10,10,1,1,1,1,0]
      t = "array"       

      for c in cn: 
        a = an.pop(0)
        b = bn.pop(0)
        result = fn.distanceToPoint(a, b, t)
        self.assertEqual(result, c)

      an = [{'x':0,'y':0},{'x':5,'y':10},{'x':1,'y':1},{'x':1,'y':1}]
      bn = [{'x':10,'y':10},{'x':0,'y':0},{'x':1,'y':2},{'x':1,'y':1}]
      cn = [20,15,1,0]
      t = "point"   
     
      for c in cn: 
        a = an.pop(0)
        b = bn.pop(0)
        result = fn.distanceToPoint(a, b, t)
        self.assertEqual(result, c)
  

  def test_getPointsInLine(self):
      
      an = [[0,0],[0,1],[5,10],[5,10],[1,1],[1,1]]
      bn = [[0,2],[2,1],[0,10],[5,5],[1,1],[2,2]]
      cn = [[[0,1],[0,2]],
            [[1,1],[2,1]],
            [[4,10],[3,10],[2,10],[1,10],[0,10]],
            [[5,9],[5,8],[5,7],[5,6],[5,5]],
            [],
            []]
            
      for c in cn: 
        a = an.pop(0)
        b = bn.pop(0)
        result = fn.getPointsInLine(a, b)
        self.assertEqual(result, c)


  def test_printMap(self):
      # Iterate through map array backwards 
      m = [[1,2],
          [3,4]]
      
      md = [[3,4],
          [1,2]]
    
      result = fn.printMap(m)
      self.assertEqual(result, md)


class boardClassTest(unittest.TestCase):

    # def __init__():

    def test_boardClassInit(self):
      pass 

    def test_setGetDimensions(self):
      
      b = board()

      wn = [1,2,3,4,5,6,7,8,9,10] 
      hn = [10,9,8,7,6,5,4,3,2,1] 

      for w in wn:
        h = hn.pop(0)
        result = b.setDimensions(w, h)
        
        hc = b.height
        wc = b.width 
        self.assertEqual(result, True)
        self.assertEqual(wc, w)
        self.assertEqual(hc, h)

        result = b.getDimensions()        
        self.assertEqual(result, [w, h])
    
      # def test_updateBoards()
      #   b = board(5,5)
      #   b.updateBoards(data)
      #   b.updateBoardYou(data)
      #   b.updateBoardSnakes(data)
      #   b.updateBoardItems(data)
      #   b.getSolid()
      #   b.getCombine()

      def test_XYToLoc(self):
      
        b = board(5,5)
        
        an = [[0,0],[5,10],[1,1]]
        cn = [{'x':0,'y':0},{'x':5,'y':10},{'x':1,'y':1}]

        for a in an:
          c = cn.pop(0)
          self.assertEqual(a, c)


      def test_bestPath(self):
        pass 

        # self.loadTestData(test_food)
        # c = self.loadTestPath(test_foodpath)

        # get head
        # get food location 
        # get path 
        
        # self.assertEqual(result, c)


      def loadTestPath(test_map):

        width = len(test_map[-1])
        height = len(test_map)

        y = height 
        x = 0
        
        correct_path = [0] * np.amax(test_map)
        # print(len(correct_path))
        
        for row in test_map:
            y = y - 1
            for cell in row:
              x = x + 1
              if(cell != 0):
                correct_path[cell] = [x, y]

        print(str(correct_path))
        return correct_path


      def loadTestData(test_map):

        width = len(test_map[-1])
        height = len(test_map)

        # Co-ordinates are reversed (y axis)
        y = height 
        x = 0
        you_head = "" 
        you_body = []
        enemy_head = "" 
        enemy_body = []
        hazard = []
        food = []
        
        for row in test_map:
            y = y - 1
            for cell in row:
              x = x + 1
              xy = {'x':x, 'y':y}
              if (cell=='you-head'):
                you_head = xy
              elif(cell=='you-body'):
                you_body.append(xy)
              elif(cell=='you-tail'):
                you_body.append(xy)
                # may be inserted out of order ..
              elif(cell=='enemy-head'):
                you_head = xy
              elif(cell=='enemy-body'):
                you_body.append(xy)
              elif(cell=='enemy-tail'):
                you_body.append(xy)
              elif(cell=='food'): 
                food.append(xy)    
              elif(cell=='hazard'):
                hazard.append(xy)

        json_vals = {

          'height':height,
          'width':width,
          'you_head':str(you_head),
          'you_body':str(you_body),
          'you_len':len(you_body),
          'hazard':str(hazard),
          'food':str(food) 
        }
                
        json_template.format(**json_vals)
        data = json.loads(json_template)
        print(str(data))
        return data

