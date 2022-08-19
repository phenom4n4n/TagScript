from ..interface import Adapter
from ..utils import escape_content
from ..interpreter import Context, log


class StringAdapter(Adapter):
    __slots__ = ("string", "escape_content")

    def __init__(self, string: str, *, escape: bool = False):
        self.string: str = str(string)
        self.escape_content = escape
        self._methods = {
            "lower": str.lower,
            "upper": str.upper,
            "title": str.title,
            "capitalize": str.capitalize,
            "swapcase": str.swapcase,
            "strip": str.strip,
        }

    def __repr__(self):
        return f"<{type(self).__qualname__} string={repr(self.string)}>"

    def get_value(self, ctx: Context) -> str:
        return self.return_value(self.handle_ctx(ctx))

    def handle_ctx(self, ctx: Context) -> str:
        if ctx.verb.parameter is None:
            return self.string
        try:
            if "+" not in ctx.verb.parameter and ctx.verb.parameter.isdigit():
                index = int(ctx.verb.parameter) - 1
                splitter = " " if ctx.verb.payload is None else ctx.verb.payload
                return self.string.split(splitter)[index]
            elif "+" in ctx.verb.parameter and ctx.verb.parameter.replace("+", "").isdigit():
                index = int(ctx.verb.parameter.replace("+", "")) - 1
                splitter = " " if ctx.verb.payload is None else ctx.verb.payload
                if ctx.verb.parameter.startswith("+"):
                    return splitter.join(self.string.split(splitter)[: index + 1])
                elif ctx.verb.parameter.endswith("+"):
                    return splitter.join(self.string.split(splitter)[index:])
                else:
                    return self.string.split(splitter)[index]
                
            elif ctx.verb.parameter == "split":
                if ctx.verb.payload is None:
                    return self.string
                
                else:
                    return " ".join(self.string.split(ctx.verb.payload))
                
            else:
                return self._methods[ctx.verb.parameter](self.string)
                
                
        except Exception as e:
            log.exception("Error in string", exc_info=e)
            return self.string

    def return_value(self, string: str) -> str:
        return escape_content(string) if self.escape_content else string
