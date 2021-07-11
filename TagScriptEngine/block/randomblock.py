import random
from typing import Optional

from ..interface import verb_required_block
from ..interpreter import Context


class RandomBlock(verb_required_block(True, payload=True)):
    """
    Pick a random item from a list of strings, split by either ``~``
    or ``,``. An optional seed can be provided to the parameter to
    always choose the same item when using that seed.

    **Usage:** ``{random([seed]):<list>}``

    **Aliases:** ``#, rand``

    **Payload:** list

    **Parameter:** seed, None

    **Examples:** ::

        {random:Carl,Harold,Josh} attempts to pick the lock!
        # Possible Outputs:
        # Josh attempts to pick the lock!
        # Carl attempts to pick the lock!
        # Harold attempts to pick the lock!

        {=(insults):You're so ugly that you went to the salon and it took 3 hours just to get an estimate.~I'll never forget the first time we met, although I'll keep trying.~You look like a before picture.}
        {=(insult):{#:{insults}}}
        {insult}
        # Assigns a random insult to the insult variable
    """

    ACCEPTED_NAMES = ("random", "#", "rand")

    def process(self, ctx: Context) -> Optional[str]:
        spl = []
        if "~" in ctx.verb.payload:
            spl = ctx.verb.payload.split("~")
        else:
            spl = ctx.verb.payload.split(",")
        random.seed(ctx.verb.parameter)

        return random.choice(spl)
