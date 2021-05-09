from typing import Optional

from ..interface import Block
from ..interpreter import Context
from . import helper_parse_if, helper_parse_list_if, helper_split


def parse_into_output(payload, result):
    if result is None:
        return None
    try:
        output = helper_split(payload, False)
        if output != None and len(output) == 2:
            if result:
                return output[0]
            else:
                return output[1]
        else:
            if result:
                return payload
            else:
                return ""
    except:
        return None


class AnyBlock(Block):
    """
    any block will return True is any of the given bool is True. If all the given bool is False, then the second part of the payload is returned.
    The bools are separated by |

    **Usage:** ``{any(<bool1|bool2|etc>):[payload]}``

    **Aliases:** ``or``

    **Payload:** string, None

    **Parameter:** Bool

    **Examples:** ::

        {any({args}==hi|{args}==hello|{args}==heyy):Hello {user}|bye}
        #assume {args} = hi
        Hello sravan
        #assume {args} = something
        bye
    """
    def will_accept(self, ctx: Context) -> bool:
        dec = ctx.verb.declaration.lower()
        return any([dec == "any", dec == "or"])

    def process(self, ctx: Context) -> Optional[str]:
        if ctx.verb.payload is None or ctx.verb.parameter is None:
            return None
        result = any(helper_parse_list_if(ctx.verb.parameter) or [])
        return parse_into_output(ctx.verb.payload, result)


class AllBlock(Block):
    """
    all block will return True is all of the given bool is True. If any the given bool is False, then the second part of the payload is returned.
    The bools are separated by |

    **Usage:** ``{all(<bool1|bool2|etc>):[payload]}``

    **Aliases:** ``and``

    **Payload:** string, None

    **Parameter:** Bool

    **Examples:** ::

        {all({args}>=100|{args}<=1000):You picked {args}|Provide a number between 100 and 1000}
        #assume {args} = 52
        Provide a number between 100 and 1000
        #assume {args} = 282
        You picked 282
    """
    def will_accept(self, ctx: Context) -> bool:
        dec = ctx.verb.declaration.lower()
        return any([dec == "all", dec == "and"])

    def process(self, ctx: Context) -> Optional[str]:
        if ctx.verb.payload is None or ctx.verb.parameter is None:
            return None
        result = all(helper_parse_list_if(ctx.verb.parameter) or [])
        return parse_into_output(ctx.verb.payload, result)


class IfBlock(Block):
    """
    The If block returns a message based on the passed expression to the parameter.
    An expression is represented by two values compared with an operator.

    The payload is a required message that must be split by ``|``.
    If the expression evaluates true, then the message before the ``|`` is returned, else the message after is returned.

    **Expression Operators:**

    +----------+--------------------------+---------+---------------------------------------------+
    | Operator | Check                    | Example | Description                                 |
    +==========+==========================+=========+=============================================+
    | ``==``   | equality                 | a==a    | value 1 is equal to value 2                 |
    +----------+--------------------------+---------+---------------------------------------------+
    | ``!=``   | inequality               | a!=b    | value 1 is not equal to value 2             |
    +----------+--------------------------+---------+---------------------------------------------+
    | ``>``    | greater than             | 5>3     | value 1 is greater than value 2             |
    +----------+--------------------------+---------+---------------------------------------------+
    | ``<``    | less than                | 4<8     | value 1 is less than value 2                |
    +----------+--------------------------+---------+---------------------------------------------+
    | ``>=``   | greater than or equality | 10>=10  | value 1 is greater than or equal to value 2 |
    +----------+--------------------------+---------+---------------------------------------------+
    | ``<=``   | less than or equality    | 5<=6    | value 1 is less than or equal to value 2    |
    +----------+--------------------------+---------+---------------------------------------------+

    **Usage:** ``{if(<expression>):<message>]}``

    **Payload:** message

    **Parameter:** expression

    **Examples:** ::

        {if({args}==63):You guessed it! The number I was thinking of was 63!|Too {if({args}<63):low|high}, try again.}
        # if args is 63
        # You guessed it! The number I was thinking of was 63!

        # if args is 73
        # Too low, try again.

        # if args is 14
        # Too high, try again.
    """
    def will_accept(self, ctx: Context) -> bool:
        dec = ctx.verb.declaration.lower()
        return dec == "if"

    def process(self, ctx: Context) -> Optional[str]:
        if ctx.verb.payload is None or ctx.verb.parameter is None:
            return None
        result = helper_parse_if(ctx.verb.parameter)
        return parse_into_output(ctx.verb.payload, result)
