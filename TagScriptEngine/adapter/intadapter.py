from ..interface import Adapter
from ..interpreter import Context


class IntAdapter(Adapter):
    __slots__ = ("integer",)

    def __init__(self, integer: int):
        self.integer: int = int(integer)

    def __repr__(self):
        return f"<{type(self).__qualname__} integer={repr(self.integer)}>"

    def get_value(self, ctx: Context) -> str:
        return str(self.integer)
