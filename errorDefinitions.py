class InvalidUserException(Exception):
    def __init__(self):
        self.message = "Provided user does not exists"

    def __repr__(self):
        return self.message


class InvalidGameName(Exception):
    def __init__(self):
        self.message = "Game does not exists"

    def __repr__(self):
        return self.message


# Game errors
class InvalidBet(Exception):
    def __init__(self):
        self.message = "Invalid bet"

    def __repr__(self):
        return self.message


class InvalidResponseException(Exception):
    def __init__(self):
        self.message = "Provided response was not valid"

    def __repr__(self):
        return self.message


# Dice errors
class ShooterDpassBet(Exception):
    def __init__(self):
        self.message = "Shooter can't bet for dpass"

    def __repr__(self):
        return self.message

# Poker errors
class NotEnoughRaiseError(Exception):
    def __init__(self):
        self.message = "Raise must be higher than previous raise"

    def __repr__(self):
        return self.message
