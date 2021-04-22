import logging
import minesweeper as ms
import random


class BreathFirstSearch(ms.AI):
    """
    To build a new AI, create a new child class of ms.AI
    This class has 3 important methods: reset(), next() and update()
    """

    def __init__(self, startPosition):
        """
        Initialisation of the AI.
        New attributes can be added if needed (e.g. I added the 'positionStack' for DFS).
        """
        self.width = 0
        self.height = 0
        self.exposed_squares = set()
        self._flags = set()
        self.positionQueue = [startPosition]
        self.has_mine = dict()
        self.safe = set()
        self.is_first = True
        self.temp_queue = []

    def getAdjacents(self, position):
        """
        Returns a list of adjacents positions (i.e. neighbours) of the given position.
        """
        x, y = position
        adj = []
        if y < self.height - 1:
            adj.append((x, y + 1))  # top
        if y < self.height - 1 and x < self.width - 1:
            adj.append((x + 1, y + 1))  # top-right
        if x < self.width - 1:
            adj.append((x + 1, y))  # right
        if x < self.width - 1 and y > 0:
            adj.append((x + 1, y - 1))  # bottom-right
        if y > 0:
            adj.append((x, y - 1))  # bottom
        if x > 0 and y > 0:
            adj.append((x - 1, y - 1))  # bottom-left
        if x > 0:
            adj.append((x - 1, y))  # left
        if x > 0 and y < self.height - 1:
            adj.append((x - 1, y + 1))  # top-left

        return adj

    def reset(self, config):
        """
        Method called when the game is reset (e.g. at the beginning, after a game is over)
        """
        self.width = config.width
        self.height = config.height
        self.exposed_squares.clear()

    def next(self):
        """
        This method is called to 'ask' for the position of the next move.
        Do any kind of computation and return a (x, y) tuple for the next cell to reveal.
        """
        while True:
            if len(self.positionQueue):
                currPosition = self.positionQueue.pop(0)
                if currPosition not in self.exposed_squares and currPosition not in self._flags:
                    self.label_mine(currPosition)
                    self.add_safe_nodes(currPosition)
                    return currPosition

            elif len(self.temp_queue):
                currPosition = self.temp_queue.pop(0)
                if currPosition not in self.exposed_squares and currPosition not in self._flags:
                    self.label_mine(currPosition)
                    self.add_safe_nodes(currPosition)
                    return currPosition

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
            print("THE AI WON :D")
        elif result.status == ms.GameStatus.DEFEAT:
            print("THE AI LOST :'(")
        elif result.status == ms.GameStatus.QUIT:
            print("THE AI GAVE UP...")
        elif len(self._flags) == config.num_mines:
            print("THE AI WON :D")

        for square in result.new_squares:
            self.exposed_squares.add((square.x, square.y))
            if square.num_mines == 0:
                adjacent = self.getAdjacents((square.x, square.y))
                for item in adjacent:
                    if item not in self.exposed_squares:
                        self.safe.add(item)
            else:
                self.has_mine[(square.x, square.y)] = square.num_mines
                self.label_mine((square.x, square.y))

    @property
    def flags(self):
        """
        This is just a custom version of the 'flags' getter which returns [] by default
        """
        return self._flags

    def label_mine(self, position):
        adjacent = self.getAdjacents(position)
        num_adjacent = len(adjacent)
        num_mine = self.has_mine.get(position)
        if num_mine == num_adjacent:
            for item in adjacent:
                self._flags.add(item)

    def add_safe_nodes(self, currPosition):
        for x, y in self.getAdjacents(currPosition):
            # print(">>> Visiting (", currPosition[0], ",", currPosition[1], ")'s adjacent (", x, ",", y, ")")
            if (x, y) not in self.exposed_squares:
                if (x, y) in self.safe:
                    self.positionQueue.append((x, y))
                elif (x, y) not in self._flags:
                    self.temp_queue.append((x, y))


# This is just a configuration for the logger
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

print("This will play a single game and then quit.")
print("The minesweeper window needs focus to capture a key press.")
print()

# Number of games to play in a row (useful for testing)
num_games = 100

# Configuration of the game.
# Possible parameters are 'width', 'height', 'num_mines', 'auto_expand_clear_areas'
# To place the mines as you want, see file 'minesweeper/minesweeper.py', method '_place_mines'
config = ms.GameConfig(num_mines=1, auto_expand_clear_areas=False)

# Create an instance of our AI (startPosition has been created by myself, can be random or anything else)
ai = BreathFirstSearch((2, 2))

# Create a game visualizer - use pause=1 to execute a new move every 1 second (or any other number)
# viz = ms.PyGameVisualizer(pause=1, next_game_prompt=True)

# Run the game(s)
result = ms.run_games(config, num_games, ai, None).pop()
print('Game lasted {0} moves'.format(result.num_moves))