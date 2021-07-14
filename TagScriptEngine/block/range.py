import random
from typing import Optional

from ..interface import verb_required_block
from ..interpreter import Context


class RangeBlock(verb_required_block(True, payload=True)):
    """
    The range block picks a random number from a range of numbers seperated by ``-``.
    The number range is inclusive, so it can pick the starting/ending number as well.
    Using the rangef block will pick a number to the tenth decimal place.

    An optional seed can be provided to the parameter to always choose the same item when using that seed.

    **Usage:** ``{range([seed]):<lowest-highest>}``

    **Aliases:** ``rangef``

    **Payload:** number

    **Parameter:** seed, None

    **Examples:** ::

        Your lucky number is {range:10-30}!
        # Your lucky number is 14!
        # Your lucky number is 25!

        {=(height):{rangef:5-7}}
        I am guessing your height is {height}ft.
        # I am guessing your height is 5.3ft.
    """

    ACCEPTED_NAMES = ("rangef", "range")

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
