class InvalidInputError(Exception):
    """Raised when user input fails Regex validation."""
    pass

class APIRequestError(Exception):
    """Raised when an external API fails."""
    pass

class CountryNotFoundError(Exception):
    """Raised when a country is not found."""
    pass