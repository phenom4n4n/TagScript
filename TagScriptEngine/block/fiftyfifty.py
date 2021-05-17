import random
from typing import Optional

from ..interface import Block
from ..interpreter import Context


class FiftyFiftyBlock(Block):
    """
    The fifty-fifty block has a 50% change of returning the payload, and 50% chance of returning null.

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
        return dec in ("5050", "50", "?")

    def process(self, ctx: Context) -> Optional[str]:
        if ctx.verb.payload is None:
            return
        return random.choice(["", ctx.verb.payload])
