from .. import Interpreter, adapter
from ..interface import Block
from . import helper_parse_list_if, helper_parse_if, helper_split
from typing import Optional


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
    def will_accept(self, ctx: Interpreter.Context) -> bool:
        dec = ctx.verb.declaration.lower()
        return any([dec == "any", dec == "or"])

    def process(self, ctx: Interpreter.Context) -> Optional[str]:
        if ctx.verb.payload is None or ctx.verb.parameter is None:
            return None
        result = any(helper_parse_list_if(ctx.verb.parameter) or [])
        return parse_into_output(ctx.verb.payload, result)


class AllBlock(Block):
    def will_accept(self, ctx: Interpreter.Context) -> bool:
        dec = ctx.verb.declaration.lower()
        return any([dec == "all", dec == "and"])

    def process(self, ctx: Interpreter.Context) -> Optional[str]:
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

      **Payload:** ``string, None``

      **Parameter:** ``Bool``

      **Examples:** ::

         #assume you mentioned yourself
         {if({target(id)}=={user(id)}):You mentioned yourself.|You mentioned {target}}
         #You mentioned youeself.

        {if({args}==):You must provide some arguments for this tag.|Hello World!}

    """
    def will_accept(self, ctx: Interpreter.Context) -> bool:
        dec = ctx.verb.declaration.lower()
        return dec == "if"

    def process(self, ctx: Interpreter.Context) -> Optional[str]:
        if ctx.verb.payload is None or ctx.verb.parameter is None:
            return None
        result = helper_parse_if(ctx.verb.parameter)
        return parse_into_output(ctx.verb.payload, result)
