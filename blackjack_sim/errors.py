

# Config files are not in the correct format or missing expected data
class ConfigurationError(ValueError):
    pass

# Tried to do something that violates the rules of the game
class GameplayError(ValueError):
    pass

# Unable to determine the next action the player or dealer should take
class DetermineActionError(LookupError):
    pass
