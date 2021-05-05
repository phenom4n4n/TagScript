import random
from typing import Optional

from ..interface import Block
from ..interpreter import Context


class FiftyFiftyBlock(Block):
    """
      50 is used to give a 50% chance of returning the payload given or 50% of returning a null.

      **Usage:**  ``{50:<paylode>}``

      **Aliases:**  ``5050, ?``

      **Payload:**  string

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
