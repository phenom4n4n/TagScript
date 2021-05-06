from itertools import islice
from typing import Any, Dict, List, Optional, Tuple

from .exceptions import ProcessError, TagScriptError, WorkloadExceededError
from .interface import Block, Adapter
from .verb import Verb

__all__ = (
    "Interpreter",
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
    """

    def __init__(self, *, variables: AdapterDict = None):
        self.body: str = None
        self.actions: Dict[str, Any] = {}
        self.variables: AdapterDict = variables if variables is not None else {}

    def __repr__(self):
        return f"<Response body={self.body!r} actions={self.actions!r} variables={self.variables!r}>"


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

    def __init__(self, verb: Verb, res: Response, interpreter, og: str):
        self.verb: Verb = verb
        self.original_message: str = og
        self.interpreter = interpreter
        self.response: Response = res

    def __repr__(self):
        return "<Context verb={0.verb!r}>".format(self)


class Interpreter:
    """
    The TagScript interpreter.

    Attributes
    ----------
    blocks: List[Block]
        A list of blocks to be used for TagScript processing.
    """

    def __init__(self, blocks: List[Block]):
        self.blocks: List[Block] = blocks

    def __repr__(self):
        return "<Interpreter blocks={0.blocks!r}>".format(self)

    def _get_acceptors(self, ctx: Context, node: Node):
        acceptors: List[Block] = [b for b in self.blocks if b.will_accept(ctx)]
        for b in acceptors:
            value = b.process(ctx)
            if value is not None:  # Value found? We're done here.
                node.output = value
                break

    def _solve(
        self, message: str, node_ordered_list: List[Node], response: Response, *, charlimit: int, verb_limit: int = 2000
    ):
        final = message
        total_work = 0

        for i, node in enumerate(node_ordered_list):
            # Get the updated verb string from coordinates and make the context
            node.verb = Verb(
                final[node.coordinates[0] : node.coordinates[1] + 1], limit=verb_limit
            )
            ctx = Context(node.verb, response, self, message)

            # Get all blocks that will attempt to take this
            self._get_acceptors(ctx, node)
            if node.output is None:
                continue  # If there was no value output, no need to text deform.

            if charlimit:
                total_work = total_work + len(
                    node.output
                )  # Record how much we've done so far, for the rate limit
                if total_work > charlimit:
                    raise WorkloadExceededError(
                        "The TSE interpreter had its workload exceeded. The total characters "
                        f"attempted were {total_work}/{charlimit}"
                    )

            start, end = node.coordinates
            message_slice_len = (end + 1) - start
            replacement_len = len(node.output)
            differential = (
                replacement_len - message_slice_len
            )  # The change in size of `final` after the change is applied
            if "TSE_STOP" in response.actions:
                return final[:start] + node.output
            final = final[:start] + node.output + final[end + 1 :]

            # if each coordinate is later than `start` then it needs the diff applied.
            for future_n in islice(node_ordered_list, i + 1, None):
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

        return final

    def process(
        self, message: str, seed_variables: AdapterDict = None, charlimit: Optional[int] = None
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
        response = Response(variables=seed_variables)

        node_ordered_list = build_node_tree(message)

        try:
            output = self._solve(message, node_ordered_list, response, charlimit=charlimit)
        except TagScriptError:
            raise
        except Exception as error:
            raise ProcessError(error) from error

        # Dont override an overridden response.
        if response.body is None:
            response.body = output.strip("\n ")
        else:
            response.body = response.body.strip("\n ")
        return response
