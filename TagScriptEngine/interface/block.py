from typing import Optional

__all__ = ("Block", "verb_required_block")


class Block:
    """
    The base class for TagScript blocks.

    Implementations must subclass this to create new blocks.

    Attributes
    ----------
    ACCEPTED_NAMES: Tuple[str, ...]
        The accepted names for this block. This ideally should be set as a class attribute.
    """

    ACCEPTED_NAMES = ()

    def __init__(self):
        pass

    def __repr__(self):
        return f"<{type(self).__qualname__} at {hex(id(self))}>"

    @classmethod
    def will_accept(cls, ctx: "interpreter.Context") -> bool:
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
        """
        dec = ctx.verb.declaration.lower()
        return dec in cls.ACCEPTED_NAMES

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


def verb_required_block(
    implicit: bool, *, payload: bool = False, parameter: bool = False
) -> Block:
    """
    Get a Block subclass that requires a verb to implicitly or explicitly have a parameter or payload passed.

    Parameters
    ----------
    implicit: bool
        ...
    payload: bool
        ...
    parameter: bool
        ...
    """
    check = (lambda x: x) if implicit else (lambda x: x is not None)

    class VerbRequiredBlock(Block):
        def will_accept(self, ctx: "interpreter.Context") -> bool:
            verb = ctx.verb
            if payload and not check(verb.payload):
                return False
            if parameter and not check(verb.parameter):
                return False
            return super().will_accept(ctx)

    return VerbRequiredBlock
