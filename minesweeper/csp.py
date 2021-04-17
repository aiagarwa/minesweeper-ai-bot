import logging
import minesweeper as ms
import random

from CSPVariable import CSPVariable


class CSP_agent(ms.AI):

    def _check_solvable_csp(self):
        # return (not self.non_mine_variables and not self.mine_variables)
        return not self.non_mine_variables

    """
    To build a new AI, create a new child class of ms.AI
    This class has 3 important methods: reset(), next() and update()
    """

    def __init__(self, config, startPosition):
        """
        Initialisation of the AI.
        New attributes can be added if needed (e.g. I added the 'positionStack' for DFS).
        """
        self.width = config.width
        self.height = config.height
        self.exposed_squares = set()
        self._flags = set()
        self.startPosition = startPosition
        self.all_constraint_equations = list()
        self.non_mine_variables = list()
        self.mine_variables = list()
        self.is_first_step = True
        self.game_stuck = False

        self.all_variables = {}
        for row in range(self.width):
            for column in range(self.height):
                self.all_variables[(row, column)] = CSPVariable(row=row, column=column)

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
        # print("next()....")
        # if is_first_step is true, which means we are in the first step, we just pick the startPosition
        if self.is_first_step:
            self.is_first_step = False
            return self.startPosition

        # if there are non-mine variables remain, which means we still have some positions that we can make sure they
        # are not mines
        if self.non_mine_variables:
            non_mine_variable = self.non_mine_variables.pop(0)
            return [non_mine_variable.row, non_mine_variable.column]

        # try to reduce the constraints and infer new non-mine variables
        self.reduce_constraints()

        if self._check_solvable_csp():
            # click randomly
            return self.click_random_cell_with_heuristic()
        else:
            non_mine_variable = self.non_mine_variables.pop(0)
            return [non_mine_variable.row, non_mine_variable.column]

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

        # print("update()....")

        if result.status == ms.GameStatus.VICTORY:
            print("THE AI WON :D")
            return
        elif result.status == ms.GameStatus.DEFEAT:
            print("THE AI LOST :'(")
            return
        elif result.status == ms.GameStatus.QUIT:
            print("THE AI GAVE UP...")
            return

        # get the cell clicked before
        square = list(result.new_squares)[0]
        # print("(", square.x, ",", square.y, ")") # Just for debug purposes
        self.exposed_squares.add((square.x, square.y))

        # Set constraint_value and value
        variable = self.all_variables[(square.x, square.y)]
        variable.constraint_value = square.num_mines
        variable.value = square.num_mines

        self.build_constraint_equation(variable)
        self.remove_variable_from_other_equations(variable)

        # remove duplicate constraint equations for the csp agent
        self.remove_duplicate_constraints()
        # add flags when find new mines
        self.flag_all_mines()

        # try to find more non-mine and mine variables from equations
        self.find_new_non_mines_and_mines()

    def flag_all_mines(self):
        """
         This method is called when the csg agent want to flag mines
        """
        while self.mine_variables:
            mine_variable = self.mine_variables.pop(0)
            self._flags.add((mine_variable.row, mine_variable.column))

    @property
    def flags(self):
        """
        This is just a custom version of the 'flags' getter which returns [] by default
        """
        return self._flags

    def build_constraint_equation(self, variable):
        """
        Create the constraint equation for the variable
        """

        for x, y in self.getAdjacents((variable.row, variable.column)):
            # If the neighbour is clicked, then there is no need to add it to the constraint equation.
            if (x, y) in self.exposed_squares:
                continue
            # If the neighbour is flagged, then there is no need add it to the equation. at the same time,
            # subtract the constraint value of the current variable, because the flagged mine cant affect the
            # result.
            if (x, y) in self._flags:
                variable.constraint_value -= 1
                continue
            neighbour = self.all_variables[(x, y)]
            variable.add_constraint_equations(neighbour)

        # add the equation in the global equation list
        self.all_constraint_equations.append([variable.constraint_equations, variable.constraint_value])

    def remove_variable_from_other_equations(self, variable, is_mine_variable=False):
        for equation in self.all_constraint_equations:
            if variable in equation[0]:
                equation[0].remove(variable)
                if is_mine_variable and equation[1]:
                    equation[1] -= 1

    def remove_duplicate_constraints(self):
        """
        remove the duplicate elements from global all constraint equations
        """
        unique_list = []
        for item in self.all_constraint_equations:
            if item not in unique_list:
                unique_list.append(item)

        self.all_constraint_equations = unique_list

    def find_new_non_mines_and_mines(self):
        """
        Try to find new non_mines and mines, once we find these cells, we can continue to
        reveal new non_mines cells or flag mines.
        """

        for equation in self.all_constraint_equations.copy():

            # Remove the empty equation
            if len(equation) == 0 or len(equation[0]) == 0:
                self.all_constraint_equations.remove(equation)
                continue

            # Check the constraint value, if the value is 0,
            # which means all variables in that equation are non-mine cells.
            # we append these variables to global non_mine_variables list
            if equation[1] == 0:
                self.all_constraint_equations.remove(equation)
                for variable in equation[0]:
                    if (variable.row, variable.column) not in self.exposed_squares \
                            and variable not in self.non_mine_variables:
                        self.non_mine_variables.append(variable)
                continue

            # Check the constraint value, if the value is the lens of variables in this equation,
            # which means all variables in this equation are mine cells.
            # we append these variables to global mine_variables list
            if len(equation[0]) == equation[1]:
                self.all_constraint_equations.remove(equation)
                for variable in equation[0]:
                    if variable not in self.mine_variables:
                        self.mine_variables.append(variable)

    def reduce_constraints(self):
        """
        Reduce the constraints by inferring clues from constraint equations.
        The main method for inferring is find the subsets from the equations
        """
        # Sort all constraint equations according to their length and in increasing order
        self.all_constraint_equations = sorted(self.all_constraint_equations, key=lambda i: len(i[0]))

        # traverse all the constraint equations
        for equation1 in self.all_constraint_equations:
            for equation2 in self.all_constraint_equations:

                # there is no need to compare same equation
                if equation1 == equation2 or not equation1[0] or not equation2[0] or not equation1[1] or not equation2[1]:
                    continue

                # if the constraint equation is a subset of the other one, simplifies the constraint.
                # e.g equation1 = [(A, B, C), 1] equation2 = [(B, C), 1]
                # we can infer that A is not a mine, we changed equation1 to [(A), 0]

                # equation1 is subset of equation2
                if set(equation1[0]).issubset(set(equation2[0])):
                    equation2[0] = list(set(equation2[0]) - set(equation1[0]))
                    equation2[1] -= equation1[1]
                    continue

                # equation2 is subset of equation1
                if set(equation2[0]).issubset(set(equation1[0])):
                    equation1[0] = list(set(equation1[0]) - set(equation2[0]))
                    equation1[1] -= equation2[1]

        # After reducing constraints, try to get safe cells
        self.find_new_non_mines_and_mines()

    def click_random_cell_with_heuristic(self):

        unrevealed_cells = dict()
        for cell in self.exposed_squares:
            exposed_cell_variable = self.all_variables[cell]

            # get number of flagged mines in neighbors
            number_of_cell_mines_found = 0

            # get all the unrevealed neighbours
            unrevealed_cell_neighbours = list()

            for x, y in self.getAdjacents(cell):
                if (x, y) in self._flags:
                    number_of_cell_mines_found += 1
                if (x, y) not in self.exposed_squares:
                    unrevealed_cell_neighbours.append((x, y))

            # get the risk from a rough calculation
            risk = exposed_cell_variable.value - number_of_cell_mines_found
            # add risk value to each of the neighbours
            for cell_neighbour in unrevealed_cell_neighbours:
                if cell_neighbour not in unrevealed_cells:
                    unrevealed_cells[cell_neighbour] = 0

                unrevealed_cells[cell_neighbour] += risk

        # select the cell with lowest risk.
        random_cell = min(unrevealed_cells, key=unrevealed_cells.get)
        return random_cell

# This is just a configuration for the logger
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

print("This will play a single game and then quit.")
print("The minesweeper window needs focus to capture a key press.")
print()

# Number of games to play in a row (useful for testing)
num_games = 1

# Configuration of the game.
# Possible parameters are 'width', 'height', 'num_mines', 'auto_expand_clear_areas'
# To place the mines as you want, see file 'minesweeper/minesweeper.py', method '_place_mines'
config = ms.GameConfig(width = 16, height = 16, num_mines=10, auto_expand_clear_areas=False)

# Create an instance of our AI (startPosition has been created by myself, can be random or anything else)
ai = CSP_agent(config, (2, 2))

# Create a game visualizer - use pause=1 to execute a new move every 1 second (or any other number)
viz = ms.PyGameVisualizer(pause=1, next_game_prompt=True)

# Run the game(s)
result = ms.run_games(config, num_games, ai, viz).pop()
print('Game lasted {0} moves'.format(result.num_moves))

