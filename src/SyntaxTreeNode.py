class STN:
    def __init__(self, value, children=None, variable_symbol=None):
        self.value = value
        if children is None:
            self.children = []
        else:
            self.children = children

        self.variable_symbol = variable_symbol


    def __repr__(self):
        if self.children:
            return f'STN({self.value}, {self.children})'
        else:
            return f'STN({self.value})'
        
    def __str__(self):
        return str(self.value)