class VariableSymbol:
    def __init__(self, type, name, is_const):
        self.type = type
        self.name = name
        self.is_const = is_const

    def __str__(self):
        return self.name

class FunctionSymbol:
    def __init__(self, return_type, name, arguments, variables):
        self.return_type = return_type
        self.name = name
        self.variables = variables
        self.arguments = arguments

    def __str__(self):
        return self.name