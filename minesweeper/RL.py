import logging
import minesweeper as ms
import random
import pdb

class Reinforcement(ms.AI):
    """
    To build a new AI, create a new child class of ms.AI
    This class has 3 important methods: reset(), next() and update()
    """

    def __init__(self, config, startPosition):
        """
        Initialisation of the AI.
        New attributes can be added if needed (e.g. I added the 'positionStack' for DFS).
        """
        self.width = 0
        self.height = 0
        self.exposed_squares = set()
        self.exposed_square_num = {}
        self._flags = set()
        self.positionStack = [startPosition]
        self.values = {}
        self.alpha = 0.2
        self.curr_Position = set()
        self.config = config

    def getQValue(self, state):
        """
          Returns Q(state,action)
          Should return 0.0 if we have never seen a state
          or the Q node value otherwise
        """
        "*** YOUR CODE HERE ***"
        if state in self.values:
          return self.values[(state)]
        else:
          return 0.0
        util.raiseNotDefined()

    def getAdjacents(self, position):
        """
        Returns a list of adjacents positions (i.e. neighbours) of the given position.
        """
        x, y = position
        adj = []
        if y < self.height - 1:
            adj.append((x, y+1)) # top
        if y < self.height - 1 and x < self.width - 1:
            adj.append((x+1, y+1)) # top-right
        if x < self.width - 1:
            adj.append((x+1, y)) # right
        if x < self.width - 1 and y > 0:
            adj.append((x+1, y-1)) # bottom-right
        if y > 0:
            adj.append((x, y-1)) # bottom
        if x > 0 and y > 0:
            adj.append((x-1, y-1)) # bottom-left
        if x > 0:
            adj.append((x-1, y)) # left
        if x > 0 and y < self.height - 1:
            adj.append((x-1, y+1)) # top-left

        return adj

    def getReward(self, position):
        # reward for exposed state
        reward = 0
        count = 0
        for x, y in self.getAdjacents(position):
            if (x, y) in self.exposed_squares:
                if self.exposed_square_num[(x,y)] >=1:
                    reward+= self.exposed_square_num[(x,y)]*(-10)
                    count+=1
                else:
                    reward += 10
            else:
                reward +=0
        if count == len(self.getAdjacents(position)):
            reward+=-50
        return reward

    def reset(self, config):
        """
        Method called when the game is reset (e.g. at the beginning, after a game is over)
        """
        self.width = config.width
        self.height = config.height
        self.exposed_squares.clear()

    def computeQvaluesAndGetNextAction(self):
        """
        Method to compute the qvalues for all the positions in not exposed state next to current position  and get the best position
        Flag the tile if (all-1)  adjacent tiles are exposed and indicates number of mines. 
        """
        # print("Exposed:",self.exposed_squares)
        states_dict = {}
        # For the next position check if all the adjacent tiles are exposed and indicating the position has mine.
        for x, y in self.getAdjacents(self.curr_Position):
            state = (x,y)
            count_exp=0
            count_num = 0
            for x2, y2 in self.getAdjacents(state):
                if (x2, y2) in self.exposed_squares:
                    count_exp+=1
                    if self.exposed_square_num[(x2,y2)] >=1:
                        count_num+=1
            
            # Calculate the q values
            if state not in self.exposed_squares and state not in self._flags:
                current_state_value = self.getQValue(state)
                self.values[(state)]=((1-self.alpha)*current_state_value)+self.alpha*(self.getReward(state))
                states_dict[state]= self.values[(state)]

        if states_dict:
            max_val = max(states_dict.values())
            worst_position = min(states_dict, key= lambda x: states_dict[x]) # Get the state with least reward to check if it is mine 
        else:
            max_val = 0
            worst_position = "None"
        # print(not states_dict)
        # Get the position with maximum q value
        if states_dict and max_val>(0):
            best_position = max(states_dict, key= lambda x: states_dict[x])
            # print(states_dict)
            # print("Best = ",best_position)
            self.positionStack.append(best_position)
            # print(self.positionStack)
        else:
            # Flag the tile which is assumed to have mine
            if worst_position!="None" and count_num >= len(self.getAdjacents(worst_position))-1 and len(self._flags)!=self.config.num_mines:
                self._flags.add(worst_position)

            # If all the adjacent tiles are exposed, get the position of any random tile.
            states_dict_random={}
            safe_squares = (self.config.height*self.config.width)-len(self._flags)
            count = 0
            visited_cell = set()
            while count != safe_squares - len(self.exposed_square_num):
                x = random.randint(0, self.width - 1)
                y = random.randint(0, self.height - 1)
                state = (x,y)
                # Calculate the q value for all cells that are not exposed and click the one with maximum reward
                if (x, y) not in self.exposed_squares and (x, y) not in self._flags and (x,y) not in visited_cell:
                    current_state_value = self.getQValue(state)
                    self.values[(state)]=((1-self.alpha)*current_state_value)+self.alpha*(self.getReward(state))
                    states_dict_random[state]= self.values[(state)]
                    count+=1
                visited_cell.add(state)
            best_position = max(states_dict_random, key= lambda x: states_dict_random[x])
            # print(states_dict_random)
            # print("Best = ",best_position)
            self.positionStack.append(best_position)


    def next(self):
        """
        This method is called to 'ask' for the position of the next move.
        Do any kind of computation and return a (x, y) tuple for the next cell to reveal.
        """
        if len(self.positionStack):
            currPosition = self.positionStack.pop()
            self.curr_Position = currPosition
            return currPosition
        else:
            print("stack Empty")

        # If you need to set a flag, use this method
        # self._flags.add((x, y))

    def update(self, result):
        """
        This method is called right after a cell has been clicked.
        The 'result' parameter contains information resulting of the click.
        => result.new_squares contains a list of Square (objects) that have been revealed
            -> A Square contains attributes 'x', 'y', and 'num_mines'
            -> The list contains only 1 Square if auto_expand_clear_areas=False
        => result.status contains the status of the game
            -> ms.GameStatus.PLAYING, ms.GameStatus.VICTORY, ms.GameStatus.DEFEAT, ms.GameStatus.QUIT
        """
        if result.status == ms.GameStatus.VICTORY:
            print("THE RL WON :D")
            return
        elif result.status == ms.GameStatus.DEFEAT:
            print("THE RL LOST :'(")
            return
        elif result.status == ms.GameStatus.QUIT:
            print("THE RL GAVE UP...")
            return

        for square in result.new_squares:
            # print("(", square.x, ",", square.y, ")") # Just for debug purposes
            self.exposed_squares.add((square.x, square.y))
            self.exposed_square_num[(square.x, square.y)] = square.num_mines
            self.computeQvaluesAndGetNextAction()
    
    @property
    def flags(self):
        """
        This is just a custom version of the 'flags' getter which returns [] by default
        """
        return self._flags


# # This is just a configuration for the logger
# logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
#
# print("This will play a single game and then quit.")
# print("The minesweeper window needs focus to capture a key press.")
# print()
#
# # Number of games to play in a row (useful for testing)
# num_games = 1
#
# # Configuration of the game.
# # Possible parameters are 'width', 'height', 'num_mines', 'auto_expand_clear_areas'
# # To place the mines as you want, see file 'minesweeper/minesweeper.py', method '_place_mines'
# config = ms.GameConfig(num_mines=3, auto_expand_clear_areas=False)
#
# # Create an instance of our AI (startPosition has been created by myself, can be random or anything else)
# ai = Reinforcement((0,0))
#
# # Create a game visualizer - use pause=1 to execute a new move every 1 second (or any other number)
# viz = ms.PyGameVisualizer(pause='key', next_game_prompt=True)
#
# # Run the game(s)
# result = ms.run_games(config, num_games, ai, viz).pop()
# print('Game lasted {0} moves'.format(result.num_moves))
