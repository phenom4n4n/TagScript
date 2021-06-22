from typing import Optional


class Block:
    """
    The base class for TagScript blocks.

    Implementations must subclass this to create new blocks.
    """

    def __init__(self):
        pass

    def __repr__(self):
        return f"<{type(self).__qualname__} at {hex(id(self))}>"

    def will_accept(self, ctx: "interpreter.Context") -> Optional[bool]:
        """
        Describes whether the block is valid for the given :class:`~TagScriptEngine.interpreter.Context`.

        Subclasses must implement this.

        Parameters
        ----------
        ctx: Context
            The context object containing the TagScript :class:`~TagScriptEngine.verb.Verb`.

        Returns
        -------
        bool
            Whether the block should be processed for this :class:`~TagScriptEngine.interpreter.Context`.

        Raises
        ------
        NotImplementedError
            The subclass did not implement this required method.
        """
        raise NotImplementedError

    def pre_process(self, ctx: "interpreter.Context"):
        return None

    def process(self, ctx: "interpreter.Context") -> Optional[str]:
        """
        Processes the block's actions for a given :class:`~TagScriptEngine.interpreter.Context`.

        Subclasses must implement this.

        Parameters
        ----------
        ctx: Context
            The context object containing the TagScript :class:`~TagScriptEngine.verb.Verb`.

        Returns
        -------
        Optional[str]
            The block's processed value.

        Raises
        ------
        NotImplementedError
            The subclass did not implement this required method.
        """
        raise NotImplementedError

    def post_process(self, ctx: "interpreter.Context"):
        return None
