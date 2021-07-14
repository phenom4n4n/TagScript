from typing import Optional

from ..interface import verb_required_block
from ..interpreter import Context


class RedirectBlock(verb_required_block(True, parameter=True)):
    """
    Redirects the tag response to either the given channel, the author's DMs,
    or uses a reply based on what is passed to the parameter.

    **Usage:** ``{redirect(<"dm"|"reply"|channel>)}``

    **Payload:** None

    **Parameter:** "dm", "reply", channel

    **Examples:** ::

        {redirect(dm)}
        {redirect(reply)}
        {redirect(#general)}
        {redirect(626861902521434160)}
    """

    ACCEPTED_NAMES = ("redirect",)

    def process(self, ctx: Context) -> Optional[str]:
        param = ctx.verb.parameter.strip()
        if param.lower() == "dm":
            target = "dm"
        elif param.lower() == "reply":
            target = "reply"
        else:
            target = param
        ctx.response.actions["target"] = target
        return ""
