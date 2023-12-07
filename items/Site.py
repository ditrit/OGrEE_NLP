from Building import Building

class Site :
    def __init__(self, name : str, *buildings : Building) :
        self.name = name
        self.buildings = buildings

    def makeCLI(self) :
        return str(self.name)