from ..interface import Block
from ..interpreter import Context


class ReplaceBlock(Block):
    """
    The replace block is used to replace all the charater(s) from the 1st parameter with the charater(s) given in the 2nd parameter.
    The 1st and 2nd parameter should be seperated using ``,``.

    **Usage:** ``{replace(<1st parameter,2nd parameter>):<message>}``

    **Aliases:** ``None``

    **Payload:** message

    **Parameter:** string

    **Examples:** ::

        {replace(o,i):welcome to the server}
        #welcime ti the server

        {replace(1,6):{args}}
        #if {args} = 1637812
        #6637862
    """
    def will_accept(self, ctx: Context):
        dec = ctx.verb.declaration.lower()
        return dec == "replace"

    def process(self, ctx: Context):
        if not ctx.verb.parameter or not ctx.verb.payload:
            return
        try:
            before, after = ctx.verb.parameter.split(",", 1)
        except ValueError:
            return

        return ctx.verb.payload.replace(before, after)


class PythonBlock(Block):
    """
    index is used to return the value of the string form the given list of strings.
    index uses 0 as the starting for the payload and are always counded by the number of spaces.
    if the string is not found in the given list of strings, then the value returned is -1.

    in is used to check if the given string is present in the payload.
    contains is used to check if the sting is present in the payload
    but can only check one sting and will return false is exact match is not found.
    both contains and in always returns a bool value

    **Usage:** ``{index(<string>):<list of strings>}``
               ``{in(<string>):<payload>}``
               ``{contains(<string>):<payload>}``

    **Aliases:** ``None``

    **Payload:** int, bool

    **Parameter:** string

    **Examples:** ::

        {index(food):I love to eat food. everyone does.}
        #4

        {in(apple pie):banana pie apple pie and other pie}
        #true
        {in(mute):How does it feel to be muted?}
        #true

        {contains(mute):How does it feel to be muted?}
        #false  (because it has to be exactly mute and not muted)
    """
    def will_accept(self, ctx: Context):
        dec = ctx.verb.declaration.lower()
        return dec in ("contains", "in", "index")

    def process(self, ctx: Context):
        dec = ctx.verb.declaration.lower()
        if dec == "contains":
            return str(bool(ctx.verb.parameter in ctx.verb.payload.split())).lower()
        elif dec == "in":
            return str(bool(ctx.verb.parameter in ctx.verb.payload)).lower()
        else:
            try:
                return str(ctx.verb.payload.strip().split().index(ctx.verb.parameter))
            except ValueError:
                return "-1"
