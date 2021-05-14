import random
from typing import Optional

from ..interface import Block
from ..interpreter import Context


class FiftyFiftyBlock(Block):
    """
    The FiftyFifty block is give 50% chance for the given message to be the payload.
    If the given message is not picked, then the payload is null.

    **Usage:**  ``{50:<message>}``

    **Aliases:**  ``5050, ?``

    **Payload:**  message

    **Parameter:**  None

    **Examples:**  ::

        I pick {if({5050:.}!=):heads|tails}
        # I pick heads
    """
    def will_accept(self, ctx: Context) -> bool:
        dec = ctx.verb.declaration.lower()
        return any([dec == "5050", dec == "50", dec == "?"])

    def process(self, ctx: Context) -> Optional[str]:
        if ctx.verb.payload is None:
            return None
        return random.choice(["", ctx.verb.payload])
