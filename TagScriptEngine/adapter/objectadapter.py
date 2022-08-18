from inspect import ismethod

from ..interface import Adapter
from ..interpreter import Context


class SafeObjectAdapter(Adapter):
    __slots__ = ("object",)

    def __init__(self, base):
        self.object = base

    def __repr__(self):
        return f"<{type(self).__qualname__} object={repr(self.object)}>"

    def get_value(self, ctx: Context) -> str:
        if ctx.verb.parameter is None:
            return str(self.object)
        if ctx.verb.parameter.startswith("_") or "." in ctx.verb.parameter:
            return
        try:
            attribute = getattr(self.object, ctx.verb.parameter)
        except AttributeError:
            return
        if ismethod(attribute):
            return
        if isinstance(attribute, float):
            attribute = int(attribute)
        return str(attribute)
