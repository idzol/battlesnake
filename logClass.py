import constants as CONST 

import json
import copy as copy 
import numpy as np
import sys

import time as time 
# from time import gmtime, strftime

global messages
messages = {
    # Server 
    'healthcheck':[1,"INFO: Healthcheck - OK"],
    'start':[1,"START: %s"],
    'end':[1,"END: %s"],
    'move':[1,"MOVE: %s"],
    'shout':[1,"SHOUT: %s"],
    
  #   # Time 
  #   'time':[2, "TIME"],
  #   'timer-hurry':[2, "TIME", "Move time reached CONST.timePanic"],
    
  #   # Exceptions 
  #   'exception':[2, "WARN","%s: %s"],

  #   # Snake
  #   'snake-showstats':[3, "SNAKE", """
  # Health: %d
  # Hunger: %d
  # Aggro: %d
  # Head: %s
  # Target: %s
  # Route: %s
  # Strategy: %s
  # Last Move: %s"""],
  
  #   # Routing - Summary 
  #   'make-move':[3,"->MAKE MOVE"," start:%s target:%s next:%s move:%s status:%s"],
  #   'route':[3,"-->ROUTE"," %s r:%s w:%s"],

  #   # Map 
  #   'map':[3, "%s"],
  #   'map-predict':[6, "%s"],
  #   'map-debug':[6, "%s"],

  #   # Strategy 
  #   'interrupt':[4,"->INTERRUPT","\nInterrupts:%s \nReasons:%s"],
  #   'strategy':[4,"->STRATEGY", "\nStrategy:%s \n Reason:%s \n Strategylist: %s,  Strategyinfo:%s"],
  #   'strategy-update':[4,"->STRATEGY", "\n%s"],
  #   'strategy-eat':[4,"-->EAT", " %s"],
  #   'strategy-attack':[4,"-->ATTACK", " %s %s %s %s"],
  #   'strategy-killpath':[4,"-->KILL", "%s head:%s length:%s target:%s"],
  #   'strategy-defend':[4,"-->DEFEND", " %s %s %s %s"],
  #   'strategy-control':[4,"-->CONTROL", " %s %s %s"],
  #   'strategy-survive':[4,"-->SURVIVE", " %s %s %s %s"],
  #   'strategy-route':[4,"-->ROUTE", " %s: %s %s"],
  #   'strategy-taunt':[4,"-->SURVIVE", " %s"],
  #   'strategy-findcentre':[4,"-->FINDCENTRE", " Target %s"],
  #   'strategy-findwall':[4,"-->FINDWALL", " Target %s"],
  #   'strategy-trackwall':[4,"-->TRACKWALL", " w:%s h:%s l:%s d:%s r:%s p:%s - Target %s"],

  #   # Routing - Detail
  #   'route-fromto':[5,"-->FROM TO", " %s %s"],
  #   'route-return':[5,"-->ROUTE RETURN", " %s %s"],
  #   'paths':[5,"-->PATH", " %s"],
  #   'path-target':[5,"-->TARGET", " %s"], 
  #   'route-dijkstra-sum':[5,"-->DSUM"," %s-%s-%s path:%s = %d"],
  #   'route-findclosestwall':[5,"-->WALLPATH"," %s %s"],
  #   'route-leastline-dsum':[5,"-->LDSUM"," %s %s-%s = %d"],
  #   'route-gradient':[5,"-->PATH", " Gradient %s"],
  #   'route-complex-step':[5,"-->ROUTE COMPLEX", "from: %s to: %s"],
  #   'route-complex-path':[5,"-->ROUTE COMPLEX", "path: %s"],

  #   # Board - Misc )
  #   'updateboardsnakes-warn':[6, "WARN", "Enemy snake head not defined. %s"],
  #   'itemclass-typewarning':[6, "WARN","item(t,p) expects location as dict"],

  #   'predict-update':[6, "->INFO", "%s"],
  #   'predict-new':[6,"->PREDICT POINT", "%s: %s: %s"],
  #   'predict-erase':[6,"->PREDICT ERASE", "%s: %s: %s"],
    
  #   'enclosed':[6,"->ENCLOSED", "%s %s"],
  #   'enclosed-sum':[6,"->ENCLOSED SUM", "%s"],

}

# Logger
class log():

    def __init__(self, override=False):

        logging = CONST.logging

        self.override = override 
        self.silent = logging['silent']  
        self.info = {} 
        self.error = []
        self.console = []
        
        self.time = []
        self.startTime = time.time()


    def dump(self, data):
        
        logging = CONST.logging
        stdout_print = sys.stdout        
        
        if(self.silent or self.override):
            return 

        if(not len(data)):
            return

        logfile = CONST.logfile_game
        # gid = data['game']['id'] 
        # turn = data['turn']

        if (logging['data']):
            if (logging['file']):
                f = open(logfile, "a")
                f.write(str(data) + "\n")
                f.close()

            else:
                stdout_print.write("%s\n" % data)

        # if (logging['console']):
        #   stdout_print = sys.stdout
        #   stdout_print.write("%s\n" % str(data))


    def print(self, data={}):
      
        logging = CONST.logging
           
        if(self.silent or self.override):
            return 

        stdout_print = sys.stdout        
        logfile = CONST.logfile_console
        
        try: 

          game = self.gameinfo(data)
          players = self.players(data) 
          gid = data['game']['id'] 
          turn = data['turn']

          output = {
              'game': game,
              'players':players,
              'id': gid,
              'turn': turn,
              'info': self.info,
              'console': self.console,
              'error': self.error
          }

        except: 

          output = {
              'info': self.info,
              'console': self.console,
              'error': self.error
          }

        if(logging['json']):
            json_output = json.dumps(output)
            stdout_print.write("%s\n" % json_output)

        if(logging['file']):
            f = open(logfile, "a")
            if (logging['json']):
                f.write(json_output+"\n")
            f.close()


    def players(self, data):

        try: 
          names = []
          snakes = data['board']['snakes']
          for snake in snakes: 
            # sn = snakes[sid]
            names.append(snake['name'])
        except: 
          names = ''

        return copy.copy(names)
  

    def gameinfo(self, data):

        try: 
          name = data['game']['ruleset']['name'] 
          foodSpawn = data['game']['ruleset']['settings']['foodSpawnChance']
          minimumFood = data['game']['ruleset']['settings']['minimumFood']
          hazardDamage = data['game']['ruleset']['settings']['hazardDamagePerTurn']
          shrinkTurns = data['game']['ruleset']['settings']['royale']['shrinkEveryNTurns']
          timeout = data['game']['timeout']

          if (name == 'solo' and foodSpawn == 15 and minimumFood == 1 and hazardDamage == 0 and shrinkTurns == 0 and timeout == 500): 
            mode = 'arena'

          else: 
            mode = 'other'
        
        except: 
          mode = ''

        # self.mode = copy.copy(mode) 
        return copy.copy(mode) 


    def log(self, key, *values): 

        global messages
        
        logging = CONST.logging

        if(self.silent or self.override):
            return 

        value = str(values)
        # if std == 'error': 
        # else:  # 'info' 'stdout'
        
        if not(key in self.info):
            # Check if existing loginfo 
            self.info[key] = []

        if isinstance(self.info[key], list):
            # Check if list 
            self.info[key].append(value) 

        else:  
            # Not list -- shouldn't happen 
            self.info[key] = [value] 

        if logging['console']:
            stdout_print = sys.stdout
            stdout_print.write("%s: %s\n" % (key, value))

  
    def message(self, msg, *vars):
        global message 

        logging = CONST.logging
        if(self.silent or self.override):
            return 

        stdout_print = sys.stdout
        llo = CONST.logLevel

        if not msg in messages:
            return 

        message = messages[msg]

        if (llo < int(message[0])):
            return 

        self.console.append(message[1])
        stdout_print.write("%s: %s\n" % (message[1], str(vars)))


    def winloss(self, data):
        name = CONST.snakename
        result = "LOSS"

        snakes = data['board']['snakes']
        for snake in snakes: 
            # sn = snakes[sid]
            if snake['name'] == name:
              result = "WIN"

        return copy.copy(result)


    def end(self, data): 
        stderr_print = sys.stderr
        stdout_print = sys.stdout

        result = self.winloss(data)
    
        gid = data['game']['id']
        turn = data['turn']

        if result == 'WIN':
            stdout_print.write("%s: %s:%s \n" % (result, gid, turn))
            
        else:
            stderr_print.write("%s: %s:%s \n" % (result, gid, turn))


    def error(self, warn, callback='', detail=''):

        logging = CONST.logging
        logfile = CONST.logfile_error

        error_text = "%s: %s: %s" % (warn, callback, detail)
        error = self.log('error', error_text)

        if (logging['file']):
            f = open(logfile, "a")
            f.write(error_text + "\n")
            f.close()

        # if (logging['console']):
        stderr_print = sys.stderr
        stderr_print.write(error_text + "\n")


    def timer(self, marker):
        
        logging = CONST.logging 

        if(self.silent or self.override):
            return 

        # t = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        
        time.time()
        diff = 1000 * (time.time() - self.startTime) 
        timediff = "{:.2f} ms".format(diff)
        self.log('time','%s: %s' % (timediff, marker))

    # Get start time of move -- used for logging
    def getStartTime(self):
        return copy.copy(self.startTime)


    def maps(self, name, data): 

          logging = CONST.logging 
          if(self.silent or self.override):
            return 


          m = copy.copy(data) 
          h = len(m)
          w = len(m[0])

          md = np.zeros([h,w],np.intc)
          for y in range(0, h):
            for x in range(0, w): 
              md[h-y-1,x] = m[y,x]
                
          output = str(md)
          
          if logging['console']:
            stdout_print = sys.stdout
            stdout_print.write("%s\n %s\n" % (name, output))

          else:
            self.log(name, output)

