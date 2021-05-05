import random
from typing import Optional

from ..interface import Block
from ..interpreter import Context


class RangeBlock(Block):
    """
    range block is used to return a random number from the given range of numbers in the payload.
    rangef will return a tenths place decimal number

    **Usage:** ``{range(seed):<lowset-highest>}``

    **Aliases:** ``rangef``

    **Payload:** int

    **Parameter:** seed, None

    **Examples:** ::

        The number i pick is {range:10-300}
        # The number i pick is 128

        This time i pick {rangef:5-8}
        # This time i pick 6.9
    """
    def will_accept(self, ctx: Context) -> bool:
        dec = ctx.verb.declaration.lower()
        return any([dec == "rangef", dec == "range"])

    def process(self, ctx: Context) -> Optional[str]:
        try:
            spl = ctx.verb.payload.split("-")
            random.seed(ctx.verb.parameter)
            if ctx.verb.declaration.lower() == "rangef":
                lower = float(spl[0])
                upper = float(spl[1])
                base = random.randint(lower * 10, upper * 10) / 10
                return str(base)
                # base = random.randint(lower, upper)
                # if base == upper:
                #     return str(base)
                # if ctx.verb.parameter != None:
                #     random.seed(ctx.verb.parameter+"float")
                # else:
                #     random.seed(None)
                # return str(str(base)+"."+str(random.randint(1,9)))
            else:
                lower = int(float(spl[0]))
                upper = int(float(spl[1]))
                return str(random.randint(lower, upper))
        except:
            return None
