from ..interface import Adapter
from ..utils import escape_content
from ..interpreter import Context


class StringAdapter(Adapter):
    __slots__ = ("string", "escape_content")

    def __init__(self, string: str, *, escape: bool = False):
        self.string: str = str(string)
        self.escape_content = escape

    def __repr__(self):
        return f"<{type(self).__qualname__} string={repr(self.string)}>"

    def get_value(self, ctx: Context) -> str:
        return self.return_value(self.handle_ctx(ctx))

    def handle_ctx(self, ctx: Context) -> str:
        if ctx.verb.parameter is None:
            return self.string
        try:
            if "+" not in ctx.verb.parameter:
                index = int(ctx.verb.parameter) - 1
                splitter = " " if ctx.verb.payload is None else ctx.verb.payload
                return self.string.split(splitter)[index]
            else:
                index = int(ctx.verb.parameter.replace("+", "")) - 1
                splitter = " " if ctx.verb.payload is None else ctx.verb.payload
                if ctx.verb.parameter.startswith("+"):
                    return splitter.join(self.string.split(splitter)[: index + 1])
                elif ctx.verb.parameter.endswith("+"):
                    return splitter.join(self.string.split(splitter)[index:])
                else:
                    return self.string.split(splitter)[index]
        except:
            return self.string

    def return_value(self, string: str) -> str:
        return escape_content(string) if self.escape_content else string
