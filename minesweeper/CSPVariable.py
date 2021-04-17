class CSPVariable():

    def __init__(self, value=None, row=None,column=None, constraint_value=None):
        self.value = value
        self.row = row
        self.column = column
        self.constraint_equations = list()
        self.constraint_value = constraint_value

    def __str__(self):
            return str(self.__dict__)

    def __eq__(self, other):
            return self.row == other.row and self.column == other.column

    def __ne__(self, other):
            return self.row != other.row and self.column != other.column

    def __hash__(self):
            return hash((self.row, self.column))

    def add_constraint_equations(self, variable):
            self.constraint_equations.append(variable)