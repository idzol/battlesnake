"""
Ref - https://docs.python.org/3/library/unittest.html
Shell - python tests.py -v
"""
import unittest
import json 

from functions import getRouteToTarget
# selectDestination, chooseMove, getDirection, comparePoints, chartPath, setPath, initialise_snake, raiseError

# from snakeClass import snake
# from boardClass import board
# from itemClass import item


game_data = """{
   "game":{
      "id":"0549018e-0a9f-4401-97b2-115f1f82e33b",
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
   "turn":1,
   "board":{
      "height":11,
      "width":11,
      "snakes":[
         {
            "id":"gs_JMJSHhdpyWtGSj66Sv3Dt8yD",
            "name":"Test snek 3",
            "latency":"172",
            "health":99,
            "body":[
               {
                  "x":1,
                  "y":4
               },
               {
                  "x":1,
                  "y":5
               },
               {
                  "x":1,
                  "y":5
               }
            ],
            "head":{
               "x":1,
               "y":4
            },
            "length":3,
            "shout":"",
            "squad":""
         },
         {
            "id":"gs_TEST",
            "name":"ENEMY SNEK",
            "latency":"172",
            "health":99,
            "body":[
               {
                  "x":5,
                  "y":4
               },
               {
                  "x":5,
                  "y":5
               },
               {
                  "x":5,
                  "y":6
               }
            ],
            "head":{
               "x":5,
               "y":6
            },
            "length":3,
            "shout":"",
            "squad":""
         }
      ],
      "food":[
         {
            "x":0,
            "y":6
         },
         {
            "x":5,
            "y":5
         }
      ],
      "hazards":[
         
      ]
   },
   "you":{
      "id":"gs_JMJSHhdpyWtGSj66Sv3Dt8yD",
      "name":"Test snek 3",
      "latency":"172",
      "health":99,
      "body":[
         {
            "x":1,
            "y":4
         },
         {
            "x":1,
            "y":5
         },
         {
            "x":1,
            "y":5
         }
      ],
      "head":{
         "x":1,
         "y":4
      },
      "length":3,
      "shout":"",
      "squad":""
   }
}"""

data = json.loads(game_data)
# print(data)


class getRouteToTargetTest(unittest.TestCase):
    def test_route(self):
        # Test inputs 
        ap = {"x":1,"y":2}
        bp = {"x":10,"y":11}

        # Call function
        rt = getRouteToTarget(ap,bp)

        # Check outputs 
        rt_len = len(rt)  
        rt_end = rt[rt_len - 1]

        # eg. """[{'x': 2, 'y': 2}, {'x': 2, 'y': 3}, {'x': 2, 'y': 4}, {'x': 2, 'y': 5}, {'x': 2, 'y': 6}, {'x': 3, 'y': 6}, {'x': 4, 'y': 6}, {'x': 5, 'y': 6}, {'x': 6, 'y': 6}, {'x': 6, 'y': 7}, {'x': 7, 'y': 7}, {'x': 8, 'y': 7}, {'x': 9, 'y': 7}, {'x': 10, 'y': 7}, {'x': 10, 'y': 8}, {'x': 10, 'y': 9}, {'x': 10, 'y': 10}, {'x': 10, 'y': 11}]""")
        # print(rt) 
  
        # Desired outputs 
        self.assertEqual(rt_len, 18)
        self.assertEqual(rt_end, bp)
  

# class boardClassTest(unittest.TestCase):

    # thisBoard = board()

    # b = thisBoard.setDimensions(11, 11)
    # b1 = thisBoard.updateBoardYou(data)
    # b2 = thisBoard.updateBoardSnakes(data)
    # b3 = thisBoard.updateBoardItems(data)

    # print(b1)
    # print(b2)
    # print(b3)

    # b = thisBoard.updateBoards(data)
    # b4 = thisBoard.getSolid()
    # b5 = thisBoard.getCombine()

    # print(b4) 
    # print(b5) 

if __name__ == "__main__":
    unittest.main()
