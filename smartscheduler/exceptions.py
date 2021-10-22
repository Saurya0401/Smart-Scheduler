class CommonError(Exception):

    def __init__(self, message, instr=None):
        self.message = message
        self.instr = instr
        super().__init__("Error: " + self.message)


class FatalError(Exception):

    def __init__(self, message):
        super().__init__("Fatal Error: " + message + "\nThe program will now exit.")


class CommonDatabaseError(Exception):
    pass
