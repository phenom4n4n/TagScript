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
      If block is used as a control block. The two payloads are separated by a |.
      If the bool is True then the part before | is the payload. If the bool is False then the part after the | is the payload.

      **Usage:** ``{if(<bool>):[payload]}``

      **Aliases:** ``None``

      **Payload:** string, None

      **Parameter:** Bool

      **Examples:** ::

         #assume you mentioned yourself
         {if({target(id)}=={user(id)}):You mentioned yourself.|You mentioned {target}}
         #You mentioned youeself.

        {if({args}==):You must provide some arguments for this tag.|Hello World!}

    """
    def will_accept(self, ctx: Context) -> bool:
        dec = ctx.verb.declaration.lower()
        return dec == "if"

    def process(self, ctx: Context) -> Optional[str]:
        if ctx.verb.payload is None or ctx.verb.parameter is None:
            return None
        result = helper_parse_if(ctx.verb.parameter)
        return parse_into_output(ctx.verb.payload, result)
