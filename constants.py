# Time variable 
timeLow = 100
timePanic = 300

# Log level 
logFile = "games.log"
logLevelConsole = 5
logLevelPrint = 5

# Snake variables
healthHigh = 100
healthMed = 95
healthLow = 90

threatHigh = 80
threatMed = 50
threatLow = 20

aggroHigh = 80
aggroMed = 50
aggroLow = 20

# Strategy variables 
strategyDepth = 10   # max strategies to explore each turn
strategyLength = 5   # number of strategies to remember between turns
strategyLargerBy = 3 

# Routing variables 
maxSearchDepth = 3
maxOwnPaths = 100
maxPredictTurns = 4
maxRecursion = 2000

# TODO: .. 
routeThreshold = 500   # Ignore route if larger 
pointThreshold = 10   # Ignore point if larger
routeSolid = 500
routeHazard = 15 
routeCell = 1

# Strategy 
defaultstrategy = ['Eat', '']

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