from itertools import islice
from typing import Any, Dict, List, Optional, Tuple

from .exceptions import ProcessError, StopError, TagScriptError, WorkloadExceededError
from .interface import Adapter, Block
from .utils import maybe_await
from .verb import Verb

__all__ = (
    "Interpreter",
    "AsyncInterpreter",
    "Context",
    "Response",
    "Node",
    "build_node_tree",
)

AdapterDict = Dict[str, Adapter]


class Node:
    """
    A low-level object representing a bracketed block.

    Attributes
    ----------
    coordinates: Tuple[int, int]
        The start and end position of the bracketed text block.
    verb: Optional[Verb]
        The determined Verb for this node.
    output:
        The `Block` processed output for this node.
    """

    __slots__ = ("output", "verb", "coordinates")

    def __init__(self, coordinates: Tuple[int, int], verb: Optional[Verb] = None):
        self.output: Optional[str] = None
        self.verb = verb
        self.coordinates = coordinates

    def __str__(self):
        return str(self.verb) + " at " + str(self.coordinates)

    def __repr__(self):
        return f"<Node verb={self.verb!r} coordinates={self.coordinates!r} output={self.output!r}>"


def build_node_tree(message: str) -> List[Node]:
    """
    Function that finds all possible nodes in a string.

    Returns
    -------
    List[Node]
        A list of all possible text bracket blocks.
    """
    nodes = []
    previous = r""

    starts = []
    for i, ch in enumerate(message):
        if ch == "{" and previous != r"\\":
            starts.append(i)
        if ch == "}" and previous != r"\\":
            if not starts:
                continue
            coords = (starts.pop(), i)
            n = Node(coords)
            nodes.append(n)

        previous = ch
    return nodes


class Response:
    """
    An object containing information on a completed TagScript process.

    Attributes
    ----------
    body: str
        The cleaned message with all verbs interpreted.
    actions: Dict[str, Any]
        A dictionary that blocks can access and modify to define post-processing actions.
    variables: Dict[str, Adapter]
        A dictionary of variables that blocks such as the `LooseVariableGetterBlock` can access.
    extra_kwargs: Dict[str, Any]
        A dictionary of extra keyword arguments that blocks can use to define their own behavior.
    """

    __slots__ = ("body", "actions", "variables", "extra_kwargs")

    def __init__(self, *, variables: AdapterDict = None, extra_kwargs: Dict[str, Any] = None):
        self.body: str = None
        self.actions: Dict[str, Any] = {}
        self.variables: AdapterDict = variables if variables is not None else {}
        self.extra_kwargs: Dict[str, Any] = extra_kwargs if extra_kwargs is not None else {}

    def __repr__(self):
        return (
            f"<Response body={self.body!r} actions={self.actions!r} variables={self.variables!r}>"
        )


class Context:
    """
    An object containing data on the TagScript block processed by the interpreter.
    This class is passed to adapters and blocks during processing.

    Attributes
    ----------
    verb: Verb
        The Verb object representing a TagScript block.
    original_message: str
        The original message passed to the interpreter.
    interpreter: Interpreter
        The interpreter processing the TagScript.
    """

    __slots__ = ("verb", "original_message", "interpreter", "response")

    def __init__(self, verb: Verb, res: Response, interpreter, og: str):
        self.verb: Verb = verb
        self.original_message: str = og
        self.interpreter = interpreter
        self.response: Response = res

    def __repr__(self):
        return f"<Context verb={self.verb!r}>"


class Interpreter:
    """
    The TagScript interpreter.

    Attributes
    ----------
    blocks: List[Block]
        A list of blocks to be used for TagScript processing.
    """

    __slots__ = ("blocks",)

    def __init__(self, blocks: List[Block]):
        self.blocks: List[Block] = blocks

    def __repr__(self):
        return f"<{type(self).__name__} blocks={self.blocks!r}>"

    def _get_context(
        self,
        node: Node,
        final: str,
        *,
        response: Response,
        original_message: str,
        verb_limit: int,
        dot_parameter: bool,
    ) -> Context:
        # Get the updated verb string from coordinates and make the context
        start, end = node.coordinates
        node.verb = Verb(final[start : end + 1], limit=verb_limit, dot_parameter=dot_parameter)
        return Context(node.verb, response, self, original_message)

    def _get_acceptors(self, ctx: Context) -> List[Block]:
        return [b for b in self.blocks if b.will_accept(ctx)]

    def _process_blocks(self, ctx: Context, node: Node) -> Optional[str]:
        acceptors = self._get_acceptors(ctx)
        for b in acceptors:
            value = b.process(ctx)
            if value is not None:  # Value found? We're done here.
                value = str(value)
                node.output = value
                return value

    @staticmethod
    def _check_workload(charlimit: int, total_work: int, output: str) -> Optional[int]:
        if not charlimit:
            return
        total_work += len(output)
        if total_work > charlimit:
            raise WorkloadExceededError(
                "The TSE interpreter had its workload exceeded. The total characters "
                f"attempted were {total_work}/{charlimit}"
            )
        return total_work

    @staticmethod
    def _text_deform(start: int, end: int, final: str, output: str) -> Tuple[str, int]:
        message_slice_len = (end + 1) - start
        replacement_len = len(output)
        differential = (
            replacement_len - message_slice_len
        )  # The change in size of `final` after the change is applied
        final = final[:start] + output + final[end + 1 :]
        return final, differential

    @staticmethod
    def _translate_nodes(node_ordered_list: List[Node], index: int, start: int, differential: int):
        for future_n in islice(node_ordered_list, index + 1, None):
            new_start = None
            new_end = None
            if future_n.coordinates[0] > start:
                new_start = future_n.coordinates[0] + differential
            else:
                new_start = future_n.coordinates[0]

            if future_n.coordinates[1] > start:
                new_end = future_n.coordinates[1] + differential
            else:
                new_end = future_n.coordinates[1]
            future_n.coordinates = (new_start, new_end)

    def _solve(
        self,
        message: str,
        node_ordered_list: List[Node],
        response: Response,
        *,
        charlimit: int,
        verb_limit: int = 2000,
        dot_parameter: bool,
    ):
        final = message
        total_work = 0

        for index, node in enumerate(node_ordered_list):
            start, end = node.coordinates
            ctx = self._get_context(
                node,
                final,
                response=response,
                original_message=message,
                verb_limit=verb_limit,
                dot_parameter=dot_parameter,
            )
            try:
                output = self._process_blocks(ctx, node)
            except StopError as exc:
                return final[:start] + exc.message
            if output is None:
                continue  # If there was no value output, no need to text deform.

            total_work = self._check_workload(charlimit, total_work, output)
            final, differential = self._text_deform(start, end, final, output)
            self._translate_nodes(node_ordered_list, index, start, differential)
        return final

    @staticmethod
    def _return_response(response: Response, output: str) -> Response:
        if response.body is None:
            response.body = output.strip()
        else:
            # Dont override an overridden response.
            response.body = response.body.strip()
        return response

    def process(
        self,
        message: str,
        seed_variables: AdapterDict = None,
        *,
        charlimit: Optional[int] = None,
        dot_parameter: bool = False,
        **kwargs,
    ) -> Response:
        """
        Processes a given TagScript string.

        Parameters
        ----------
        message: str
            A TagScript string to be processed.
        seed_variables: Dict[str, Adapter]
            A dictionary containing strings to adapters to provide context variables for processing.
        charlimit: int
            The maximum characters to process.
        dot_parameter: bool
            Whether the parameter should be followed after a "." or use the default of parantheses.
        kwargs: Dict[str, Any]
            Additional keyword arguments that may be used by blocks during processing.

        Returns
        -------
        Response
            A response object containing the processed body, actions and variables.

        Raises
        ------
        TagScriptError
            A block intentionally raised an exception, most likely due to invalid user input.
        WorkloadExceededError
            Signifies the interpreter reached the character limit, if one was provided.
        ProcessError
            An unexpected error occurred while processing blocks.
        """
        response = Response(variables=seed_variables, extra_kwargs=kwargs)
        node_ordered_list = build_node_tree(message)
        try:
            output = self._solve(
                message,
                node_ordered_list,
                response,
                charlimit=charlimit,
                dot_parameter=dot_parameter,
            )
        except TagScriptError:
            raise
        except Exception as error:
            raise ProcessError(error, response, self) from error
        return self._return_response(response, output)


class AsyncInterpreter(Interpreter):
    """
    An asynchronous subclass of `Interpreter` that allows blocks to implement asynchronous methods.
    Synchronous blocks are still supported.

    This subclass has no additional attributes from the `Interpreter` class.
    See `Interpreter` for full documentation.
    """

    async def _get_acceptors(self, ctx: Context) -> List[Block]:
        return [b for b in self.blocks if await maybe_await(b.will_accept, ctx)]

    async def _process_blocks(self, ctx: Context, node: Node) -> Optional[str]:
        acceptors = await self._get_acceptors(ctx)
        for b in acceptors:
            value = await maybe_await(b.process, ctx)
            if value is not None:  # Value found? We're done here.
                value = str(value)
                node.output = value
                return value

    async def _solve(
        self,
        message: str,
        node_ordered_list: List[Node],
        response: Response,
        *,
        charlimit: int,
        verb_limit: int = 2000,
        dot_parameter: bool,
    ):
        final = message
        total_work = 0

        for index, node in enumerate(node_ordered_list):
            start, end = node.coordinates
            ctx = self._get_context(
                node,
                final,
                response=response,
                original_message=message,
                verb_limit=verb_limit,
                dot_parameter=dot_parameter,
            )
            try:
                output = await self._process_blocks(ctx, node)
            except StopError as exc:
                return final[:start] + exc.message
            if output is None:
                continue  # If there was no value output, no need to text deform.

            total_work = self._check_workload(charlimit, total_work, output)
            final, differential = self._text_deform(start, end, final, output)
            self._translate_nodes(node_ordered_list, index, start, differential)
        return final

    async def process(
        self,
        message: str,
        seed_variables: AdapterDict = None,
        *,
        charlimit: Optional[int] = None,
        dot_parameter: bool = False,
        **kwargs,
    ) -> Response:
        """
        Asynchronously process a given TagScript string.

        This method has no additional attributes from the `Interpreter` class.
        See `Interpreter.process` for full documentation.
        """
        response = Response(variables=seed_variables, extra_kwargs=kwargs)
        node_ordered_list = build_node_tree(message)
        try:
            output = await self._solve(
                message,
                node_ordered_list,
                response,
                charlimit=charlimit,
                dot_parameter=dot_parameter,
            )
        except TagScriptError:
            raise
        except Exception as error:
            raise ProcessError(error, response, self) from error
        return self._return_response(response, output)
