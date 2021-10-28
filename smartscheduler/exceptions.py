class CommonError(Exception):

    def __init__(self, message="Unknown error.", flag=None):
        self.message = message
        self.flag = flag
        super().__init__("Error: " + self.message)


class FatalError(Exception):

    def __init__(self, message):
        super().__init__("Fatal Error: " + message + "\nThe program will now exit.")


class CommonDatabaseError(Exception):
    pass
