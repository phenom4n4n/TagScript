from typing import Optional

from ..interface import Block, verb_required_block
from ..interpreter import Context


class CommandBlock(verb_required_block(True, payload=True)):
    """
    Run a command as if the tag invoker had ran it. Only 3 command
    blocks can be used in a tag.

    **Usage:** ``{command:<command>}``

    **Aliases:** ``c, com, command``

    **Payload:** command

    **Parameter:** None

    **Examples:** ::

        {c:ping}
        # invokes ping command

        {c:kick {target(id)} Chatflood/spam}
        # invokes ban command on the pinged user with the reason as "Chatflood/spam"
    """

    ACCEPTED_NAMES = ("c", "com", "command")

    def __init__(self, limit: int = 3):
        self.limit = limit
        super().__init__()

    def process(self, ctx: Context) -> Optional[str]:
        command = ctx.verb.payload.strip()
        actions = ctx.response.actions.get("commands")
        if actions:
            if len(actions) >= self.limit:
                return f"`COMMAND LIMIT REACHED ({self.limit})`"
        else:
            ctx.response.actions["commands"] = []
        ctx.response.actions["commands"].append(command)
        return ""


class OverrideBlock(Block):
    """
    Override a command's permission requirements. This can override
    mod, admin, or general user permission requirements when running commands
    with the :ref:`Command Block`. Passing no parameter will default to overriding
    all permissions.

    In order to add a tag with the override block, the tag author must have ``Manage
    Server`` permissions.

    This will not override bot owner commands or command checks.

    **Usage:** ``{override(["admin"|"mod"|"permissions"]):[command]}``

    **Payload:** command

    **Parameter:** "admin", "mod", "permissions"

    **Examples:** ::

        {override}
        # overrides all commands and permissions

        {override(admin)}
        # overrides commands that require the admin role

        {override(permissions)}
        {override(mod)}
        # overrides commands that require the mod role or have user permission requirements
    """

    ACCEPTED_NAMES = ("override",)

    def process(self, ctx: Context) -> Optional[str]:
        param = ctx.verb.parameter
        if not param:
            ctx.response.actions["overrides"] = {"admin": True, "mod": True, "permissions": True}
            return ""

        param = param.strip().lower()
        if param not in ("admin", "mod", "permissions"):
            return None
        overrides = ctx.response.actions.get(
            "overrides", {"admin": False, "mod": False, "permissions": False}
        )
        overrides[param] = True
        ctx.response.actions["overrides"] = overrides
        return ""
