from typing import Optional

from ..interface import verb_required_block
from ..interpreter import Context


class SubstringBlock(verb_required_block(True, parameter=True)):
    ACCEPTED_NAMES = ("substr", "substring")

    def process(self, ctx: Context) -> Optional[str]:
        try:
            if "-" not in ctx.verb.parameter:
                return ctx.verb.payload[int(float(ctx.verb.parameter)) :]

            spl = ctx.verb.parameter.split("-")
            start = int(float(spl[0]))
            end = int(float(spl[1]))
            return ctx.verb.payload[start:end]
        except:
            return
