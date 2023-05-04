# COMP30024 Artificial Intelligence, Semester 1 2023
# Project Part B: Game Playing Agent

from referee.game import \
    PlayerColor, Action, SpawnAction, SpreadAction, HexPos, HexDir, Board
import random, math, copy

# This is the entry point for your game playing agent. Currently the agent
# simply spawns a token at the centre of the board if playing as RED, and
# spreads a token at the centre of the board if playing as BLUE. This is
# intended to serve as an example of how to use the referee API -- obviously
# this is not a valid strategy for actually playing the game!

currentBoard: dict[tuple, tuple]
currentBoard = {}
'''board = {
        ...     (5, 6): (PlayerColor.RED, 2),
        ...     (1, 0): (PlayerColor.BLUE, 2),
        ... }
'''
    
#currentBoard = Board()
team_color = PlayerColor.RED
enemy_color = PlayerColor.BLUE
maxDepth = 3
turnCount = 1

class Agent:

    global currentBoard, nextAction, maxDepth, turnCount
    
    def __init__(self, color: PlayerColor, **referee: dict):
        """
        Initialise the agent.
        """
        self._color = color
        match color:
            case PlayerColor.RED:
                print("Testing: I am playing as red")
            case PlayerColor.BLUE:
                print("Testing: I am playing as blue")

    def action(self, **referee: dict) -> Action:
        """
        Return the next action to take.
        """
        global currentBoard
        #print(sumOfPlayerPower(PlayerColor.RED, currentBoard._state))
        
        match self._color:
            case PlayerColor.RED:
                #print("current board sent to minmax: ", currentBoard)
                miniMax(currentBoard, maxDepth, -math.inf, math.inf, True)
                #print (availableActions(team_color, currentBoard)) # no problem here
                return nextAction
            case PlayerColor.BLUE:
                b = availableActions(PlayerColor.BLUE, currentBoard)
                return random.choice(b)

    def turn(self, color: PlayerColor, action: Action, **referee: dict):
        """
        Update the agent with the last player's action.
        """
        global currentBoard, turnCount
        currentBoard = apply_action(currentBoard, action, color)
        turnCount += 1
        #print(currentBoard)
        
        match action:
            case SpawnAction(cell):
                
                print(f"Testing: {color} SPAWN at {cell}")
                pass
            case SpreadAction(cell, direction):
                print(f"Testing: {color} SPREAD from {cell}, {direction}")
                pass
            
nextAction: Action
nextAction = SpawnAction(HexPos(0,0))
def miniMax(board: dict[tuple, tuple], depth, alpha, beta, isMaxPlayer):
    if(depth == 0 | isGameOver(board)):
        return evaluation(board)
    
    global nextAction, maxDepth
    
    if(isMaxPlayer):
        maxEval = -math.inf
        for action in availableActions(team_color, board):
            child_board = apply_action(board, action, team_color)
            eval = miniMax(child_board, depth-1, alpha, beta, False)
            '''
            if(depth == maxDepth): #using this to see if there's strange eval value, now has times where spawn has eval = 2
                print("action ", action, "has eval = ", eval)'''
            #alpha = max(eval, maxEval)
            if(eval > maxEval):
                
                 # select action from depth = max - 1 (recursive so the last should be at that level)
                if(depth == maxDepth):
                    nextAction = action # need check, highly possible be logically incorrect
                    print("depth is", depth," action of this node is", action, " maxEval is ", maxEval)
                alpha = eval
                maxEval = eval

            if(beta <= alpha):
                break
           
        return maxEval
    else:
        minEval = math.inf
        for action in availableActions(enemy_color, board):
            child_board = apply_action(board, action, enemy_color)
            eval = miniMax(child_board, depth-1, alpha, beta, True)
            beta = min(eval, minEval)
            if(eval < minEval):
                #print("depth is", depth," action of this node is", action, " minEval is ", minEval)
                #nextAction = nextAction # to avoid none value warning
                beta = eval
                minEval = eval
                
            if(beta <= alpha):
                break
            
        return minEval

def availableActions(color: PlayerColor, board: dict):
    availableSpawn = []
    availableSpread = []
    direction = [HexDir.DownRight, HexDir.Down, HexDir.DownLeft, HexDir.UpLeft, HexDir.Up, HexDir.UpRight]
    position = HexPos(0,0) #initialize
    
    # appending all position
    for i in range(7):
        for j in range(7):
            availableSpawn.append(SpawnAction(HexPos(i,j)))
    # appending available spreads
    for key in board.keys():
        position = HexPos(key[0], key[1])
        if board[key][0] == color:
            for d in direction:
                availableSpread.append(SpreadAction(position, d))
        # remove taken spots from spawn list
        if SpawnAction(position) in availableSpawn:
            availableSpawn.remove(SpawnAction(position)) 
    
    #print("Spawn:" )
    #print(availableSpawn)
    #print("Spread:")
    #print(availableSpread)
    return availableSpawn + availableSpread
    
def sumOfPlayerPower(color: PlayerColor, board):
    sum = 0
    for key in board.keys():
        if(color == board[key][0]):
            sum += board[key][1]
    return sum

def isGameOver(board):
    global turnCount
    if turnCount< 2: 
            return False

    return any([
        #turn_count >= 343, probably no need cuz referee ends game itself
        sumOfPlayerPower(PlayerColor.RED, board) == 0,
        sumOfPlayerPower(PlayerColor.BLUE, board) == 0,
    ])

def evaluation(board: Board):
    num = sumOfPlayerPower(team_color, board) - sumOfPlayerPower(enemy_color, board)

    # need more function, spread priority > spawn etc..
    
    return num

def apply_action(board, action, color: PlayerColor):
    match action:
        case SpawnAction():
            return spawn(board, (action.cell.r, action.cell.q), color)
        case SpreadAction():
            return spread(board, (action.cell.r, action.cell.q), (action.direction.__getattribute__("r"), action.direction.__getattribute__("q")))

def spread(originBoard, position, direction):
    board = originBoard.copy()
    #print(board.keys())
    color = board[position][0]
    rank = board[position][1]
    #print(color)

    for i in range(1,rank+1):
        spreadX = (position[0]+i*direction[0]+7)%7 #plus an additional 7 to make negative positions positive so that -1 -> 6
        spreadY = (position[1]+i*direction[1]+7)%7
        board[(spreadX, spreadY)] = (color, (board.get((spreadX, spreadY),(0,0))[1] + 1))
    del board[position]

    return board

def spawn(originBoard, position, color: PlayerColor):
    board = originBoard.copy()
    board[position] = (color, 1)
    
    return board