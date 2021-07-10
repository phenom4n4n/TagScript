from discord.ext.commands import Cooldown

__all__ = (
    "TagScriptError",
    "WorkloadExceededError",
    "ProcessError",
    "EmbedParseError",
    "BadColourArgument",
    "StopError",
    "CooldownExceeded",
)


class TagScriptError(Exception):
    """Base class for all module errors."""


class WorkloadExceededError(TagScriptError):
    """Raised when the interpreter goes over its passed character limit."""


class ProcessError(TagScriptError):
    """
    Raised when an exception occurs during interpreter processing.

    Attributes
    ----------
    original: Exception
        The original exception that occurred during processing.
    response: Response
        The incomplete response that was being processed when the exception occurred.
    interpreter: Interpreter
        The interpreter used for processing.
    """

    def __init__(self, error: Exception, response, interpreter):
        self.original = error
        self.response = response
        self.interpreter = interpreter
        super().__init__(error)


class EmbedParseError(TagScriptError):
    """Raised if an exception occurs while attempting to parse an embed."""


class BadColourArgument(EmbedParseError):
    """
    Raised when the passed input fails to convert to `discord.Colour`.

    Attributes
    ----------
    argument: str
        The invalid input.
    """

    def __init__(self, argument: str):
        self.argument = argument
        super().__init__(f'Colour "{argument}" is invalid.')


class StopError(TagScriptError):
    """
    Raised by the StopBlock to stop processing.

    Attributes
    ----------
    message: str
        The stop error message.
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class CooldownExceeded(StopError):
    """
    Raised by the cooldown block when a cooldown is exceeded.

    Attributes
    ----------
    message: str
        The cooldown error message.
    cooldown: discord.ext.commands.Cooldown
        The cooldown bucket with information on the cooldown.
    key: str
        The cooldown key that reached its cooldown.
    retry_after: float
        The seconds left til the cooldown ends.
    """

    def __init__(self, message: str, cooldown: Cooldown, key: str, retry_after: float):
        self.cooldown = cooldown
        self.key = key
        self.retry_after = retry_after
        super().__init__(message)
