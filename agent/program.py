# COMP30024 Artificial Intelligence, Semester 1 2023
# Project Part B: Game Playing Agent

from referee.game import \
    PlayerColor, Action, SpawnAction, SpreadAction, HexPos, HexDir, Board
import random

# This is the entry point for your game playing agent. Currently the agent
# simply spawns a token at the centre of the board if playing as RED, and
# spreads a token at the centre of the board if playing as BLUE. This is
# intended to serve as an example of how to use the referee API -- obviously
# this is not a valid strategy for actually playing the game!


    
currentBoard = Board()

class Agent:

    global currentBoard
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

        #self.availableActions(currentBoard._state[1])
        
        match self._color:
            case PlayerColor.RED:
                a = availableActions(PlayerColor.RED, currentBoard._state)
                return random.choice(a)
            case PlayerColor.BLUE:
                b = availableActions(PlayerColor.BLUE, currentBoard._state)
                # This is going to be invalid... BLUE never spawned!
                # return SpreadAction(HexPos(3, 3), HexDir.Up)
                return random.choice(b)

    def turn(self, color: PlayerColor, action: Action, **referee: dict):
        """
        Update the agent with the last player's action.
        """
        currentBoard.apply_action(action)
        #print("our board: \n")
        #print(currentBoard.render(True, False))
        #print(availableActions(currentBoard._state))
        match action:
            case SpawnAction(cell):
                
                print(f"Testing: {color} SPAWN at {cell}")
                pass
            case SpreadAction(cell, direction):
                print(f"Testing: {color} SPREAD from {cell}, {direction}")
                pass

def availableActions(color: PlayerColor, boardState: dict[HexPos]):
        availableSpawn = []
        availableSpread = []
        direction = [HexDir.DownRight, HexDir.Down, HexDir.DownLeft, HexDir.UpLeft, HexDir.Up, HexDir.UpRight]
        for i in range(7):
            for j in range(7):
                availableSpawn.append(SpawnAction(HexPos(i,j)))
        for key in boardState.keys():
            if boardState[key].player == color:
                for d in direction:
                    availableSpread.append(SpreadAction(key, d))
            if SpawnAction(key) in availableSpawn:
                availableSpawn.remove(SpawnAction(key)) 
        
        #print("Spawn:" )
        #print(availableSpawn)
        #print("Spread:")
        #print(availableSpread)
        return availableSpawn + availableSpread