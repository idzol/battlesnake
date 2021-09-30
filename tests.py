"""
Ref:  https://docs.python.org/3/library/unittest.html
Shell:  python -m unittest tests.py -v
        python tests.py -v
        echo '{"json":"obj"}' | python -m json.tool
"""
import unittest
import json 
import constants as CONST

import functions as fn 
from logic import selectDestination, chooseMove, getClosestItem, getItemByName

import numpy as np

from snakeClass import snake
from boardClass import board
from itemClass import item

# ============ TEST DATA =================

test_food = np.array(
[[12,31, 0, 0, 0, 0, 0],
 [11,31, 0, 0, 0, 0, 0],
 [10,31, 0, 0, 0, 0, 0],
 [ 0,31, 0, 0, 0, 0, 0],
 [ 0,31, 0, 0, 0, 0, 0],
 [ 0,31, 0, 0, 0, 0, 0],
 [ 0, 0, 0, 0, 0, 0, -30]])

test_sides_empty = [15,18,12,20]
test_quads_empty = [4,9,7,8]

test_sides_food = [0,1,0,1]
test_quads_food = [0,0,0,1]

test_foodname = "food@x0y6"
test_foodtarget = [7,7]
test_foodmove = "down"
test_foodpath = np.array(
[[ 0, 0, 0, 0, 0, 0, 0],
 [ 1, 0, 0, 0, 0, 0, 0],
 [ 2, 0, 0, 0, 0, 0, 0],
 [ 3, 0, 0, 0, 0, 0, 0],
 [ 4, 0, 0, 0, 0, 0, 0],
 [ 5, 0, 0, 0, 0, 0, 0],
 [ 6, 7, 8, 9,10,11,12]])
    
test_food2 = np.array(
[[12,11,10, 0, 0, 0, 0],
 [31,31,31,31,31,31, 0],
 [ 0, 0, 0, 0, 0, 0, 0],
 [ 0, 0, 0, 0, 0, 0, 0],
 [ 0, 0, 0, 0, -30, 0, 0],
 [ 0, 0, 0, 0, 0, 0, 0],
 [ 0, 0, 0, 0, 0, 0, -30]])

test_foodname2 = "food@x4y2"
test_foodtarget2 = [5,5]
test_foodmove2 = "right"
test_foodpath2 = np.array(
[[ 0, 1, 2, 3, 4, 5, 6],
 [ 0, 0, 0, 0, 0, 0, 7],
 [ 0, 0, 0, 0, 0, 0, 8],
 [ 0, 0, 0, 0, 0, 0, 9],
 [ 0, 0, 0, 0,12,11,10],
 [ 0, 0, 0, 0, 0, 0, 0],
 [ 0, 0, 0, 0, 0, 0, 0]])

global json_val
json_val = {    
    '$height':str(3),
    '$width':str(3),
    
    '$foods':json.dumps({'x':0, 'y':0}),
    
    '$you_health':str(100),
    '$you_body':json.dumps({'x':0, 'y':0}),
    '$you_head':json.dumps({'x':0, 'y':0}),
    '$you_length':str(1),

    '$enemy_health':str(100),
    '$enemy_body':json.dumps({'x':2, 'y':2}),
    '$enemy_head':json.dumps({'x':0, 'y':2}),
    '$enemy_length':str(1),
    
    '$hazards':json.dumps([]),
    
}

global json_test
json_test = """
{
   "game":{
      "id":"testgame",
      "ruleset":{
         "name":"solo",
         "version":"v1.0.22",
         "settings":{
            "foodSpawnChance":15,
            "minimumFood":1,
            "hazardDamagePerTurn":0,
            "royale":{
               "shrinkEveryNTurns":0
            },
            "squad":{
               "allowBodyCollisions":false,
               "sharedElimination":false,
               "sharedHealth":false,
               "sharedLength":false
            }
         }
      },
      "timeout":500
   },
   "turn":0,
   "board":{
      "height":$height,
      "width":$width,
      "snakes":[
         {
            "id":"gs_JMJSHhdpyWtGSj66Sv3Dt8yD",
            "name":"idzol",
            "latency":"",
            "health":$you_health,
            "body":$you_body,
            "head":$you_head,
            "length":$you_length,
            "shout":"",
            "squad":""
         },
         {
            "id":"gs_JMJSHhdpyWtGSj66Sv3Dt8yE",
            "name":"crepes",
            "latency":"",
            "health":$enemy_health,
            "body":$enemy_body,
            "head":$enemy_head,
            "length":$enemy_length,
            "shout":"",
            "squad":""
         }
      ],
      "food":$foods,
      "hazards":$hazards
   },
   "you":{
      "id":"gs_JMJSHhdpyWtGSj66Sv3Dt8yD",
      "name":"idzol",
      "latency":"",
      "health":$you_health,
      "body":$you_body,
      "head":$you_head,
      "length":$you_length,
      "shout":"",
      "squad":""
   }
}
"""

if __name__ == "__main__":
    unittest.main()
    # getRouteToTargetTest()
    # boardClassTest()


def loadTestData(test_map):
  global json_val
  global json_test

  width = len(test_map[-1])
  height = len(test_map)

  # Co-ordinates are reversed (y axis)
  y = 0 
  x = 0
  you_head = "" 
  you_body = []
  enemy_head = "" 
  enemy_body = []
  hazards = []
  foods = []
  
  for row in test_map:
      y = y + 1
      x = 0
      for cell in row:
        x = x + 1
        xy = {'x':x, 'y':y}
        if (cell==CONST.legend['you-head']):
          you_head = xy
        elif(cell==CONST.legend['you-body']):
          you_body.append(xy)
        elif(cell==CONST.legend['you-tail']):
          you_body.append(xy)
          # may be inserted out of order ..
        elif(cell==CONST.legend['enemy-head']):
          you_head = xy
        elif(cell==CONST.legend['enemy-body']):
          you_body.append(xy)
        elif(cell==CONST.legend['enemy-tail']):
          you_body.append(xy)
        elif(cell==CONST.legend['food']): 
          foods.append(xy)    
        elif(cell==CONST.legend['hazard']):
          hazards.append(xy)

  json_val = { 
      '$height':str(height),
      '$width':str(width),
      
      '$foods':json.dumps(foods),
      
      '$you_health':str(100),
      '$you_body':json.dumps(you_body),
      '$you_head':json.dumps(you_head),
      '$you_length':str(len(you_body)),

      '$enemy_health':str(100),
      '$enemy_body':json.dumps({'x':2, 'y':2}),
      '$enemy_head':json.dumps({'x':0, 'y':2}),
      '$enemy_length':str(1),
      
      '$hazards':json.dumps(hazards),
      
  }

  # nonlocal json_test
  for key in json_val:
      json_test = json_test.replace(key,json_val[key])

  try:
      d = json.loads(json_test)
  except:
      print("ERROR: Incorrect JSON format.  Check variable in json_template, and keys in json_vals")
  # print(str(foods))
  return d


# =========================================
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


# test
#    Function testcases 
#    itemClass 
#        def getDistances(self, things) 
#        def getDistance(self, thing)

#    boardClass 
#       def assignIndices(self, sn, it)
#       def calculateDistances(self, snakes, items) 
#       def predictEnemyMoves(self, sn, its)
#       def predictMatrix 

#    functions
#       def printMap(m)

#    snakeClass
#       def shouts(self)

#    logic 
#       Separated functions to avoid recursion



# ======================================

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

      def test_findDirectionWith(self):


        bo = board()

        data = loadTestData(test_food)
        bo.loadTestData(data)
        
        c = test_sides_empty
        result = bo.findDirectionWith(CONST.legend['empty'])
        self.assertEqual(result, c)

        c = test_sides_food        
        result = bo.findDirectionWith(CONST.legend['food'])
        self.assertEqual(result, c)


      def test_findQuadrantWith(self):
        
        bo = board()
        data = loadTestData(test_food)
        bo.loadTestData(data)

        c = test_quads_empty
        bo.findQuadrantWith(CONST.legend['empty'])
        self.assertEqual(result, c)

        c = test_quads_food
        bo.findQuadrantWith(CONST.legend['food'])
        self.assertEqual(result, c)

            
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


# ======================================
class logicTest(unittest.TestCase):
  
  def test_selectDestChooseMove(self):
        
    # bo.setDimensions(data)

    data = loadTestData(test_food)
    
    sn = snake()
    strat = "enlarge"
    sn.setStrategy(strat)

    bo = board(data)

    foods = data['board']['food']
    print(str(foods))
    theItems = []
    for f in foods:
      it = item("food", f) 
      theItems.append(it)  
      print(str(f))

    c = test_foodtarget
    result = selectDestination(bo, sn, theItems)
    self.assertEqual(result, c)

    c = test_foodmove
    result = chooseMove(data, bo, sn)
    self.assertEqual(result, c)

    data = loadTestData(test_food2)
    foods = data['board']['food']
    theItems = []
    for f in foods:
      it = item("food", f) 
      theItems.append(it)
    
    c = test_foodtarget2
    result = selectDestination(bo, sn, it)
    self.assertEqual(result, c)

    c = test_foodmove2
    result = chooseMove(data, bo, sn)
    self.assertEqual(result, c)


  def test_getClosestItem(self):
    
    bo = board()
    
    data = loadTestData(test_food)
    items = []
    foods = data['board']['food']
    for f in foods:
      it = item("food", f) 
      items.append(it)

    loc = data['you']['head']
    c = test_foodname
    result = getClosestItem(bo, items, loc, "food")
    c = self.assertEqual(result, c)

    data = loadTestData(test_food2)
    items = []
    foods = data['board']['food']
    for f in foods:
      it = item("food", f) 
      items.append(it)

    print(str(foods))
    loc = data['you']['head']
    print(str(loc))
    c = test_foodname2
    print(str(c))
    result = getClosestItem(bo, items, loc, "food")
    print(str(items))
    c = self.assertEqual(result, c)


  def test_getItemByName(self):
    
    data = loadTestData(test_food)
    foods = data['board']['food']
    items = []
    for f in foods:
      it = item("food", f) 
      items.append(it)

    name = test_foodname
    c = test_foodtarget
    result = getItemByName(items, name)
    self.assertEqual(result, c)

    data = loadTestData(test_food2)
    foods = data['board']['food']
    items = []
    for f in foods:
      it = item("food", f) 
      items.append(it)

    name = test_foodname2
    c = test_foodtarget2
    result = getItemByName(items, name)
    self.assertEqual(result, c)
    

# ======================================

class itemClassTest(unittest.TestCase):
  
  def test_getDistances(self):
    pass 
    # getDistances(self):

  def test_getDistance(self):
    pass 
    # getDistance(self, thing):


# ======================================
# 
#    boardClass 
#       def assignIndices(self, sn, it)
#       def calculateDistances(self, snakes, items) 
#       def predictEnemyMoves(self, sn, its)
#       def predictMatrix 

#    functions
#       def printMap(m)

#    snakeClass
#       def shouts(self)

#    logic 
#       Separated functions to avoid recursion
