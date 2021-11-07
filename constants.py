try: 
    f = open("env", "r")
    lines = f.read().splitlines()

    vars = []
    # for line in lines:
    # line.strip('\n')    
    vars = lines[0].split(':')
 
    environment = vars[0]
    snakename = vars[1] 
    

except: 
    environment = 'localhost'
    snakename = 'idzol dev' 

# print("ENV: '%s' '%s'" % (environment, snakename))
logfile_console = "console.log"
logfile_game = "game.log"
logfile_error = "error.log"


# TODO:  Performance testing 
# TODO:  Converge these over time .. 
lookAheadEnemyStrategy = 3  # Enemy prediction (play forward move - logic:enemyStrategy)
lookAheadEnemy = 3          # Enemy prediction (calculate chance depth - boardControl:updateEnemyChance)
lookAheadPath = 20          # Path prediction (Random)
lookAheadPathContinue = 40  # Path continue (Best / Markov / Dijkstra)
lookAheadPathContinueEnemy = 40  # Path continue (Enemy path lookahead)  
maxRecursion = 3000


if (environment == 'prod'):
  # Production 
  logLevel = 4
  logging = {
    'data':True,
    'file':False,
    'silent':False,
    'json':True,
    'console':False  
  }
  # Time variable 
  timeStart = 300
  timeMid = 350
  timeEnd = 400
  timePanic = 400

elif (environment == 'preprod'): 
  # Preprod (cloud run)
  logLevel = 4
  logging = {
    'data':True,
    'file':False,
    'silent':False,
    'json':True,
    'console':False  
  }
  # Time variable 
  timeStart = 300
  timeMid = 350
  timeEnd = 400
  timePanic = 400

else:
  # Dev (localhost) 
  logLevel = 4
  logging = {
    'data':True,
    'file':True,
    'silent':False,
    'json':False,
    'console':True  
  }
  # Time variable 
  timeStart = 3000
  timeMid = 3500
  timeEnd = 4000
  timePanic = 4000

# Routing threshold - collision probability
routeThreshold = 1000   # Ignore if route larger 
pointThreshold = 25   # Ignore if any step larger
minProbability = 1    # Markov probability 

routeSolid = 500
routeHazard = 15
routeCell = 1

# Game phases
lengthMidGame = 10
lengthEndGame = 20 
# lengthEndGame = 30

# Snake variables
healthHigh = 100
healthMed = 75
healthLow = 50
healthCritical = 25

threatHigh = 80
threatMed = 50
threatLow = 20

aggroHigh = 80
aggroMed = 50
aggroLow = 20

# Strategy 
strategyDepth = 100   # max strategies to explore each turn
strategyDepthEnemy = 10    # max enemy strategies to explore each turn
strategyLength = 5   # number of strategies to remember between turns

# Strategy - control board 
controlMinLength = 25
controlLargerBy = 10

# Strategy - kill radius 
killRadius = 2

# Strategy - kill intercept (%) 
interceptMin = 40

# Strategy - eat / grow 
growLength = 25
foodThreat = 3

# Strategy 
# defaultstrategy = ['Eat', '']

# Movement directions 
counterclockwise = "ccw"
clockwise = "cw"

ccwMap = {
  'up':'left',
  'left':'down',
  'down':'right',
  'right':'up'
}

cwMap = {
  'up':'right',
  'right':'down',
  'down':'left',
  'left':'up'
}

directions = ["up","right","down","left"]

directionSides = {
  'up':[[1,0],[0,1],[0,-1]],
  'down':[[-1,0],[0,1],[0,-1]],
  'left':[[0,-1],[1,0],[-1,0]],
  'right':[[0,1],[1,0],[-1,0]],
  'none':[[0,1],[0,-1],[1,0],[-1,0]]
}

up = "up"
down = "down"
left = "left"
right = "right"

moveup = [1, 0]
movedown = [-1, 0]
moveleft = [0, -1]
moveright = [0, 1]

northwest = 0  # "nw"
northeast = 1  # "ne"
southwest = 2  # "sw"
southeast = 3  # "se"

movenw = [1, -1]
movene = [1, 1]
movesw = [-1, -1]
movese = [-1, 1]

north = 0  # "n"
south = 1  # "s"
west = 2  # "e"
east = 3  # "w"

movenorth = moveup
movesouth  = movedown
movewest = moveleft
moveeast = moveright

directionMap = {
  'up':moveup,
  'down':movedown,
  'right':moveright,
  'left':moveleft,

  'north':moveup,
  'south':movedown,
  'east':moveleft,
  'west':moveright,

  'northwest':movenw,
  'northeast':movene,
  'southwest':movesw,
  'southeast':movese
}

# Board legend 
legend = {
    'you-head':20,
    'you-body':21,
    'you-tail':22,
    'enemy-head':30,  # Snake ID * value .. 
    'enemy-body':31,
    'enemy-tail':32,
    'food':-10,       
    'hazard':10,
    'empty':0
}

# Snake attitude 
shoutFrequency = 10

shouts = ['Away, you three-inch fool',
    'Come, come, you froward and unable worms!',
    'Go, prick thy face, and over-red thy fear, Thou lily-liver’d boy',
    'I am sick when I do look on thee',
    'Sell when you can, you are not for all markets',
    'I’ll beat thee, but I would infect my hands',
    'Methinkst thou art a general offence and every man should beat thee',
    'More of your conversation would infect my brain',
    'Go away, rump-fed runion',
    'The rankest compound of villainous smell that ever offended nostril',
    'The tartness of your face sours ripe grapes',
    'There’s no more faith in thee than in a stewed prune',
    'Thine face is not worth sunburning',
    'Thou art a boil, a plague sore',
    'Art thou a flesh-monger, a fool and a coward?',
    'Thou art as fat as butter',
    'Like the toad; ugly and venomous',
    'Thou art unfit for any place but hell',
    'Thou cream faced loon',
    'Thou clay-brained guts, thou knotty-pated fool, thou whoreson obscene greasy tallow-catch',
    'Thou damned and luxurious mountain goat',
    'Thou elvish-mark’d, abortive, rooting hog!',
    'Thou lump of foul deformity',
    'You poisonous bunch-back’d toad!',
    'Thou hast no more brain than I have in mine elbows',
    'Thy tongue outvenoms all the worms of Nile',
    'Would thou wert clean enough to spit upon',
    'Would thou wouldst burst!',
    'You poor, base, rascally, cheating lack-linen mate!',
    'You are as a candle, the better burnt out.',
    'You scullion! You rampallian! You fustilarian! I’ll tickle your catastrophe',
    'Your brain is as dry as the remainder biscuit after voyage',
    'Villain, I have done thy mother',
    'Heaven truly knows that thou art false as hell',
    'Out of my sight! Thou dost infect mine eyes.',
    'You are spherical, like a globe; I could find countries in you']