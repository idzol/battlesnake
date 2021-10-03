"""
Ref:  https://docs.python.org/3/library/unittest.html
Shell:  python -m unittest tests.py -v
        python tests.py -v
        echo '{"json":"obj"}' | python -m json.tool
"""
import unittest
import json 
import constants as CONST

# import ast 

import functions as fn 
from logic import checkInterrupts, stateMachine, translatePath, getClosestItem, getItemByName

import numpy as np

from snakeClass import snake
from boardClass import board
from itemClass import item

# ============ TEST DATA =================

## MAP0
test_map0 = np.array(
[[-30, 0, 0, 0, 0, 0, 0],
 [ 0, 0,20, 0, 0, 0, 0],
 [ 0, 0, 0, 0, 0, 0, 0],
 [ 0, 0, 0, 0, 0, 0, 0],
 [ 0, 30, 0, 0, 0, 0, 0],  
 [ 0, 0, 0, 0, 0, 30, 0],
 [ 0, 0, 0, 0, 0, 0, 0]])
 
test_map0_wall_route = [[6,2]]
test_map0_dirn_empty = [20,21,20,21]
test_map0_quad_empty = CONST.northeast
test_map0_dirn_food = CONST.north
test_map0_quad_food = CONST.northwest
test_map0_closestwall = [-1,-1]

## MAP1
test_food = np.array(
[[21,10, 0, 0, 0, 0, 31],
 [21,10, 0, 0, 0, 0, 31],
 [20,10, 0, 0, 0, 0, 30],
 [ 0,10, 0, 0, 0, 0, 0],
 [ 0,10, 0, 0, 0, 0, 0],
 [ 0,10, 0, 0, 0, 0, 0],
 [ 0, 0, 0, 0, 0, 0, -30]])

test_map1_dirn_empty = [12,18,12,17]
test_map1_quad_empty = CONST.southeast
test_map1_dirn_food = CONST.north
test_map1_quad_food = CONST.southeast
test_map1_closestwall = [-1,-1]

test_foodname = "food@x6y0"
test_foodtarget = [0,6]
test_foodmove = "down"
test_foodpath = np.array(
[[ 0, 0, 0, 0, 0, 0, 0],
 [ 1, 0, 0, 0, 0, 0, 0],
 [ 2, 0, 0, 0, 0, 0, 0],
 [ 3, 0, 0, 0, 0, 0, 0],
 [ 4, 0, 0, 0, 0, 0, 0],
 [ 5, 0, 0, 0, 0, 0, 0],
 [ 6, 7, 8, 9,10,11,12]])

## MAP2
test_food2 = np.array(
[[21,21,20, 0, 0, 0, 0],
 [10,10,10,10,10,10, 0],
 [ 0, 0, 0, 0, 0, 0, 0],
 [ 0, 0, 0, 0, 0, 0, 0],
 [ 0, 0, 0, 0,-30, 0, 0],
 [ 0, 0, 0, 0, 0, 0, 0],
 [31,31,30, 0, 0, 0,-30]])

test_map2_dirn_empty = [12,16,12,17]
test_map2_quad_empty = [3,6,7,8]
test_map2_dirn_food = [0,2,0,2]
test_map2_quad_food = [0,0,0,1]
test_map2_closestwall = [-1,-1]

test_foodname2 = "food@x4y2"
test_foodtarget2 = [2,4]
test_foodmove2 = "right"
test_foodpath2 = np.array(
[[ 0, 1, 2, 3, 4, 5, 6],
 [ 0, 0, 0, 0, 0, 0, 7],
 [ 0, 0, 0, 0, 0, 0, 8],
 [ 0, 0, 0, 0, 0, 0, 9],
 [ 0, 0, 0, 0,12,11,10],
 [ 0, 0, 0, 0, 0, 0, 0],
 [ 0, 0, 0, 0, 0, 0, 0]])

## MAP3
test_map3 = np.array(
[[ 0, 0,30, 0, 0, 0, 0],
 [10, 0,20, 0, 0, 0, 0],
 [ 0, 0, 0, 0, 0, 0, 0],
 [ 0, 0, 0, 0, 0, 0, 0],
 [ 0, 0, 0, 0, 0, 0, 0],  
 [ 0, 0, 0, 0, 0, 0, 0],
 [ 0, 0, 0, 0, 0, 0, 0]])
 
test_map3_wall_route = [[5, 3], [5, 4], [5, 5], [5, 6]]





global json_template
json_template = """
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
  global json_template
  json_t = json_template

  width = len(test_map[-1])
  height = len(test_map)

  # Co-ordinates are reversed (y axis)
  y = width
  x = 0
  you_head = "" 
  you_body = []
  enemy_head = "" 
  enemy_body = []
  hazards = []
  foods = []
  
  for row in test_map:
      y = y - 1
      x = 0
      for cell in row:
        xy = {'x':x, 'y':y}
        if (cell==CONST.legend['you-head']):
          you_head = xy
        elif(cell==CONST.legend['you-body']):
          you_body.append(xy)
        elif(cell==CONST.legend['you-tail']):
          you_body.append(xy)
          # may be inserted out of order ..
        elif(cell==CONST.legend['enemy-head']):
          enemy_head = xy
        elif(cell==CONST.legend['enemy-body']):
          enemy_body.append(xy)
        elif(cell==CONST.legend['enemy-tail']):
          you_body.append(xy)
        elif(cell==CONST.legend['food']): 
          foods.append(xy)    
        elif(cell==CONST.legend['hazard']):
          hazards.append(xy)
        x = x + 1
        
  json_v = { 
      '$height':str(height),
      '$width':str(width),
      
      '$foods':json.dumps(foods),
      
      '$you_health':str(100),
      '$you_body':json.dumps(you_body),
      '$you_head':json.dumps(you_head),
      '$you_length':str(len(you_body)),

      '$enemy_health':str(100),
      '$enemy_body':json.dumps(enemy_body),
      '$enemy_head':json.dumps(enemy_head),
      '$enemy_length':str(1),
      
      '$hazards':json.dumps(hazards)
      
  }

  # nonlocal json_test
  for key in json_v:
      json_t = json_t.replace(key,json_v[key])
      # print(str(json_t))
  try:
      d = json.loads(json_t)
  except:
      print("ERROR: Incorrect JSON format.  Check variable in json_template, and keys in json_vals")
  
  return d


# =========================================
class functionsTest(unittest.TestCase):

  def test_getDirection(self): 
      
      a = [1,1]
      bn = [[1,2],[1,0],[2,1],[0,1]]
      cn = ['right','left','up','down']
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

      for c in cn: 
        a = an.pop(0)
        b = bn.pop(0)
        result = fn.distanceToPoint(a, b)
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
      
      an = [{'x':0,'y':0},{'x':5,'y':10},{'x':1,'y':1}]
      cn = [[0,0],[10,5],[1,1]]
      
      i = 0 
      for a in an:
        result = b.XYToLoc(a)
        self.assertEqual(result, cn[i])
        i = i + 1
        
    def test_bestPath(self):
      pass 

      # self.loadTestData(test_food)
      # c = self.loadTestPath(test_foodpath)

      # get head
      # get food location 
      # get path 
      
      # self.assertEqual(result, c)
    def test_findClosestWall(self):
    
      bo = board()
      sn = snake()
  
      data = loadTestData(test_map0)
      w = data['board']['width']
      h = data['board']['height']
      bo.setDimensions(w, h)
      bo.updateBoards(data)
      sn.setLocation(data)
      
      c = test_map0_wall_route
      result = bo.findClosestWall(sn)
      print(str(result))
      self.assertEqual(result, c)


      data = loadTestData(test_map3)
      w = data['board']['width']
      h = data['board']['height']
      bo.setDimensions(w, h)
      bo.updateBoards(data)
      sn.setLocation(data)
      
      c = test_map3_wall_route
      result = bo.findClosestWall(sn)
      print(str(result))
      self.assertEqual(result, c)


    def test_findDirectionWith(self):

      bo = board()

      data = loadTestData(test_map0)
      w = data['board']['width']
      h = data['board']['height']
      bo.setDimensions(w, h)
      bo.updateBoards(data)
      
      c = test_map0_dirn_empty
      result = bo.findDirectionWith(CONST.legend['empty'])
      self.assertEqual(result, c)

      c = test_map0_dirn_food
      result = bo.findDirectionWith(CONST.legend['food'])
      self.assertEqual(result, c)


      data = loadTestData(test_food)
      w = data['board']['width']
      h = data['board']['height']
      bo.setDimensions(w, h)
      bo.updateBoards(data)

      c = test_map1_dirn_empty
      result = bo.findDirectionWith(CONST.legend['empty'])
      self.assertEqual(result, c)

      c = test_map1_dirn_food
      result = bo.findDirectionWith(CONST.legend['food'])
      self.assertEqual(result, c)


      data = loadTestData(test_food2)
      w = data['board']['width']
      h = data['board']['height']
      bo.setDimensions(w, h)
      bo.updateBoards(data)

      c = test_map2_dirn_empty
      result = bo.findDirectionWith(CONST.legend['empty'])
      self.assertEqual(result, c)

      c = test_map2_dirn_food
      result = bo.findDirectionWith(CONST.legend['food'])
      self.assertEqual(result, c)


    def test_findQuadrantWith(self):

      bo = board()
      data = loadTestData(test_map0)
      w = data['board']['width']
      h = data['board']['height']
      bo.setDimensions(w, h)
      bo.updateBoards(data)

      c = test_map0_quad_empty
      result = bo.findQuadrantWith(CONST.legend['empty'])
      self.assertEqual(result, c)

      c = test_map0_quad_food
      result = bo.findQuadrantWith(CONST.legend['food'])
      self.assertEqual(result, c)     


      bo = board()
      data = loadTestData(test_food)
      w = data['board']['width']
      h = data['board']['height']
      bo.setDimensions(w, h)
      bo.updateBoards(data)
      
      c = test_map1_quad_empty
      result = bo.findQuadrantWith(CONST.legend['empty'])
      self.assertEqual(result, c)

      c = test_map1_quad_food
      result = bo.findQuadrantWith(CONST.legend['food'])
      self.assertEqual(result, c)


      data = loadTestData(test_food)
      w = data['board']['width']
      h = data['board']['height']
      bo.setDimensions(w, h)
      bo.updateBoards(data)
      
      c = test_map2_quad_empty
      result = bo.findQuadrantWith(CONST.legend['empty'])
      self.assertEqual(result, c)
 
      c = test_map2_quad_food
      result = bo.findQuadrantWith(CONST.legend['food'])
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

      # print(str(correct_path))
      return correct_path


# ======================================
class logicTest(unittest.TestCase):
  
  def test_selectDestChooseMove(self):
        
    # bo.setDimensions(data)

    data = loadTestData(test_food)
    
    sn = snake()
    
    w = data['board']['width']
    h = data['board']['height']
    bo = board()
    bo.setDimensions(w, h)

    foods = data['board']['food']
    # print(str(foods))
    theItems = []
    for f in foods:
      it = item("food", f) 
      theItems.append(it)  
      # print(str(f))

    c = test_foodtarget
    result = stateMachine(bo, sn, theItems)
    # self.assertEqual(result, c)

    bo.updateBoards(data)
    sn.setLocation(data)
    sn.setTarget(result)
    # sn.setTarget([0,6])
    
    result = translatePath(bo, sn)

    c = test_foodmove
    self.assertEqual(result, c)

    data = loadTestData(test_food2)
    
    bo.updateBoards(data)
    sn.setLocation(data)
    sn.setTarget(result)

    foods = data['board']['food']
    items = []
    for f in foods:
      it = item("food", f) 
      items.append(it)
    
    result = stateMachine(bo, sn, items)
    c = test_foodtarget2
    self.assertEqual(result, c)

    result = translatePath(bo, sn)
    c = test_foodmove2
    self.assertEqual(result, c)


  def test_getClosestItem(self):
    
    # Test food 1 
    bo = board()
    items = []
    
    data = loadTestData(test_food)
    foods = data['board']['food']

    for f in foods:
      it = item("food", f) 
      items.append(it)
            
    # Find distance from head to food 
    loc = bo.XYToLoc(data['you']['head'])
    result = getClosestItem(bo, items, loc, "food")
    
    # Check result 
    c = test_foodname
    c = self.assertEqual(result, c)

    # Test food 2  
    bo = board()
    items = []
    
    data = loadTestData(test_food2)
    foods = data['board']['food']
    
    for f in foods:
      it = item("food", f) 
      items.append(it)
  
    loc = bo.XYToLoc(data['you']['head'])
    result = getClosestItem(bo, items, loc, "food")

    c = test_foodname2  
    c = self.assertEqual(result, c)


  def test_getItemByName(self):
    
    data = loadTestData(test_food)
    foods = data['board']['food']
    items = []
    for f in foods:
      it = item("food", f) 
      items.append(it)

    name = test_foodname
    it = getItemByName(items, name)
    result = it.getLocation()

    c = test_foodtarget
    self.assertEqual(result, c)

    data = loadTestData(test_food2)
    foods = data['board']['food']
    items = []
    for f in foods:
      it = item("food", f) 
      items.append(it)

    name = test_foodname2
    it = getItemByName(items, name)
    result = it.getLocation()
    
    c = test_foodtarget2
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
