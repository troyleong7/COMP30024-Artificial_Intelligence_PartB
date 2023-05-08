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
    
team_color : PlayerColor
enemy_color : PlayerColor
maxDepth = 3
turnCount: int
turnCount = 0

class Agent:

    global currentBoard, nextAction, maxDepth
    
    def __init__(self, color: PlayerColor, **referee: dict):
        """
        Initialise the agent.
        """
        global team_color, enemy_color
        self._color = color
        match color:
            case PlayerColor.RED:
                team_color = PlayerColor.RED
                enemy_color = PlayerColor.BLUE
                print("Testing: I am playing as red")
            case PlayerColor.BLUE:
                team_color = PlayerColor.BLUE
                enemy_color = PlayerColor.RED
                print("Testing: I am playing as blue")
                
    def action(self, **referee: dict) -> Action:
        """
        Return the next action to take.
        """
        global currentBoard, turnCount, maxDepth
        eval = evaluation(currentBoard)
        
        # to stop wasting time when we're just closing the game
        if(eval>20):
            depth = 2
            maxDepth = 2
        else:
            depth = 3
            maxDepth = 3
            
        match self._color:
            case PlayerColor.RED:
                turnCount += 1
                miniMax(currentBoard, depth, -math.inf, math.inf, True)
                return nextAction
            
            case PlayerColor.BLUE:
                turnCount += 1
                miniMax(currentBoard, depth, -math.inf, math.inf, True)
                return nextAction

    def turn(self, color: PlayerColor, action: Action, **referee: dict):
        """
        Update the agent with the last player's action.
        """
        global currentBoard
        currentBoard = apply_action(currentBoard, action, color)
        
        
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
    global nextAction, maxDepth, turnCount, team_color
    
    
    if(isGameOver(board, turnCount + maxDepth - depth)):
        if(isMaxPlayer):
            return -1000 #avoid game losing move
        if(sumOfPlayer_and_Power(team_color, board)[0]==0):
            return -1000 # avoid suicide
        return 1000 #always choose the game winning move
    
    if(depth == 0):
        return evaluation(board)
    
    if(isMaxPlayer):
        maxEval = -math.inf
        for action in availableActions(team_color, board):
            child_board = apply_action(board, action, team_color)
            eval = miniMax(child_board, depth-1, alpha, beta, False)
            
            '''if(depth == maxDepth or depth == maxDepth-1): #using this to see if there's strange eval value, now has times where spawn has eval = 2
                print("depth = ",depth, "action ", action, "has eval = ", eval, " has TD = ", token_distribution(team_color, child_board))'''
                

            if(eval > maxEval):
                
                 # select action from depth = max - 1 (recursive so the last should be at that level)
                if(depth == maxDepth):
                    nextAction = action
                    #print("depth is", depth," action of this node is", action," eval is ",eval, " maxEval is ", maxEval)
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
            
            '''if(depth == maxDepth-1): #using this to see if there's strange eval value, now has times where spawn has eval = 2
                print("depth = ",depth, "action ", action, "has eval = ", eval)'''
            
            if(eval < minEval):
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
    if (sumOfPlayer_and_Power(PlayerColor.RED, board)[1] + sumOfPlayer_and_Power(PlayerColor.BLUE, board)[1]) < 49:
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

    return availableSpawn + availableSpread 
    
def sumOfPlayer_and_Power(color: PlayerColor, board):
    power_sum = 0
    player_sum = 0
    for key in board.keys():
        if(color == board[key][0]):
            power_sum += board[key][1]
            player_sum += 1
    return [player_sum, power_sum]

# sum of smallest distance of a team token to another
def token_distribution(color: PlayerColor, board):
    closest_distance_sum = 0
    closest_distance: int
    distance: int
    for position1 in board.keys():
        if(color == board[position1][0]):
            # see closest distance to an ally for each team token
            closest_distance = -1
            isFirst = 1 #boolean for first assign to closest distance
            for position2 in board.keys():
                if(color == board[position2][0]):
                    distance = findDistance(position1, position2)
                    if(distance == 0):
                        # avoid self to self distance
                        continue
                    if(distance < closest_distance or closest_distance == -1):
                        closest_distance = distance
                    if(closest_distance == 1):
                        break
            # could be -1 if there's no ally
            if(closest_distance != -1):
                closest_distance_sum += closest_distance
    return closest_distance_sum
    

def isGameOver(board, modified_turnCount):
    # not game over when it's the first two turns
    if modified_turnCount < 2: 
            return False
    return sumOfPlayer_and_Power(PlayerColor.RED, board)[0] == 0 or sumOfPlayer_and_Power(PlayerColor.BLUE, board)[0] == 0
    

def evaluation(board: Board):
    team_sumInfo = sumOfPlayer_and_Power(team_color, board)
    enemy_sumInfo = sumOfPlayer_and_Power(enemy_color, board)
    
    # 0.2*TD because max TD = 4, try to make it under 1 so it will choose eat enemy with power 1 than spawning at distance = 4
    global turnCount
    if(turnCount < 10):
        num = team_sumInfo[1] - 1.4*enemy_sumInfo[1] - 0.2*token_distribution(team_color, board)
    else:
        num = team_sumInfo[1] - 1.4*enemy_sumInfo[1] + 0.2*token_distribution(team_color, board)

    return num

def apply_action(board, action, color: PlayerColor):
    match action:
        case SpawnAction():
            return spawn(board, (action.cell.r, action.cell.q), color)
        case SpreadAction():
            return spread(board, (action.cell.r, action.cell.q), (action.direction.__getattribute__("r"), action.direction.__getattribute__("q")))

def spread(originBoard, position, direction):
    board = originBoard.copy()
    color = board[position][0]
    rank = board[position][1]

    for i in range(1,rank+1):
        spreadX = (position[0]+i*direction[0]+7)%7 #plus an additional 7 to make negative positions positive so that -1 -> 6
        spreadY = (position[1]+i*direction[1]+7)%7
        power = (board.get((spreadX, spreadY),(0,0))[1] + 1)
        board[(spreadX, spreadY)] = (color, power)
        if(power == 7):
            del board[(spreadX, spreadY)]
    del board[position]

    return board

def spawn(originBoard, position, color: PlayerColor):
    board = originBoard.copy()
    board[position] = (color, 1)
    
    return board

def findDistance(position1, position2):
    distance = 0
    dx = position1[0]-position2[0]
    dy = position1[1]-position2[1]
    if(abs(dx)>3):
        if(dx>0):
            dx -= 7
        else:
            dx += 7
    if(abs(dy)>3):
        if(dy>0):
            dy -= 7
        else:
            dy += 7

    if(dx>0):
        if(dy>0):
            distance = dx+dy
        else:
            distance = max(abs(dx), abs(dy))
    else: # dx<=0
        if(dy<0):
            distance = -dx-dy
        else:
            distance = max(abs(dx), abs(dy))
    
    if(distance > 4):
        return 4 # max distance is 4, return 4 for situations like (-3,-2)
    else:
        return distance