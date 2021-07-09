from typing import Optional

from ..interface import Block
from ..interpreter import Context


class StrictVariableGetterBlock(Block):
    """
    The strict variable block represents the adapters for any seeded or defined variables.
    This variable implementation is considered "strict" since it checks whether the variable is
    valid during :meth:`will_accept` and is only processed if the declaration refers to a valid
    variable.

    **Usage:** ``{<variable_name>([parameter]):[payload]}``

    **Aliases:** This block is valid for any variable name in `Response.variables`.

    **Payload:** Depends on the variable's underlying adapter.

    **Parameter:** Depends on the variable's underlying adapter.

    **Examples:** ::

        {=(var):This is my variable.}
        {var}
        # This is my variable.
    """

    def will_accept(self, ctx: Context) -> bool:
        return ctx.verb.declaration in ctx.response.variables

    def process(self, ctx: Context) -> Optional[str]:
        return ctx.response.variables[ctx.verb.declaration].get_value(ctx.verb)
