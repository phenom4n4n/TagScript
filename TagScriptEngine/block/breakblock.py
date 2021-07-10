from typing import Optional

from ..interface import Block
from ..interpreter import Context
from . import helper_parse_if


class BreakBlock(Block):
    """
    The break block will force the tag output to only be the payload of this block, if the passed
    expresssion evaluates true.
    If no message is provided to the payload, the tag output will be empty.

    This differs from the `StopBlock` as the stop block stops all tagscript processing and returns
    its message while the break block continues to process blocks. If command blocks exist after
    the break block, they will still execute.

    **Usage:** ``{break(<expression>):[message]}``

    **Aliases:** ``short, shortcircuit``

    **Payload:**  message

    **Parameter:**  expression

    **Examples:** ::

        {break({args}==):You did not provide any input.}
    """

    ACCEPTED_NAMES = ("break", "shortcircuit", "short")

    def process(self, ctx: Context) -> Optional[str]:
        if helper_parse_if(ctx.verb.parameter):
            ctx.response.body = ctx.verb.payload if ctx.verb.payload != None else ""
        return ""
