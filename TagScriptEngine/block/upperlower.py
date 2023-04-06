from ..interface import Block
from ..interpreter import Context

class UpperBlock(Block):
    """Converts the given text to uppercase.

    **Usage:**  ``{upper([text]))}``

    **Aliases:**  ``uppercase, upper``

    **Payload:**  None

    **Parameter:**  text

    **Examples:**  ::

        The text is {lower:ThIs Is A TeXt}!
        # The text is THIS IS A TEXT!

        You have entered {lower:{args}}!
        # You have entered HELLO WORLD!
    """

    ACCEPTED_NAMES = ("upper","uppercase")

    def process(self, ctx: Context) -> str:
        text = str(ctx.verb.parameter).upper()
        return "" if text == "NONE" else text

class LowerBlock(Block):
    """Converts the given text to lowercase.

    **Usage:**  ``{lower([text])}``

    **Aliases:**  ``lowercase, lower``

    **Payload:**  None

    **Parameter:**  text

    **Examples:**  ::

        The text is {lower:ThIs Is A TeXt}!
        # The text is this is a text!

        You have entered {lower:{args}}!
        # You have entered hello world!
    """

    ACCEPTED_NAMES = ("lower","lowercase")

    def process(self, ctx: Context) -> str:
        text = str(ctx.verb.parameter).lower()
        return "" if text == "none" else text