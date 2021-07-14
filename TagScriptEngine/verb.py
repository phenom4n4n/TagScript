from typing import Optional

__all__ = ("Verb",)


class Verb:
    """
    Represents the passed TagScript block.

    Parameters
    ----------
    verb_string: Optional[str]
        The string to parse into a verb.
    limit: int
        The maximum number of characters to parse.
    dot_parameter: bool
        Whether the parameter should be followed after a "." or use the default of parantheses.

    Attributes
    ----------
    declaration: Optional[str]
        The text used to declare the block.
    parameter: Optional[str]
        The text passed to the block parameter in the parentheses.
    payload: Optional[str]
        The text passed to the block payload after the colon.

    Example
    -------
    Below is a visual representation of a block and its attributes::

        {declaration(parameter):payload}

        # dot_parameter = True
        {declaration.parameter:payload}
    """

    __slots__ = (
        "declaration",
        "parameter",
        "payload",
        "parsed_string",
        "dec_depth",
        "dec_start",
        "skip_next",
        "parsed_length",
        "dot_parameter",
    )

    def __init__(
        self, verb_string: Optional[str] = None, *, limit: int = 2000, dot_parameter: bool = False
    ):
        self.declaration: Optional[str] = None
        self.parameter: Optional[str] = None
        self.payload: Optional[str] = None
        self.dot_parameter = dot_parameter
        if verb_string is None:
            return
        self.__parse(verb_string, limit)

    def __str__(self):
        """This makes Verb compatible with str(x)"""
        response = "{"
        if self.declaration is not None:
            response += self.declaration
        if self.parameter is not None:
            response += f".{self.parameter}" if self.dot_parameter else f"({self.parameter})"
        if self.payload is not None:
            response += ":" + self.payload
        return response + "}"

    def __repr__(self):
        attrs = ("declaration", "parameter", "payload")
        inner = " ".join(f"{attr}={getattr(self, attr)!r}" for attr in attrs)
        return f"<Verb {inner}>"

    def __parse(self, verb_string: str, limit: int):
        self.parsed_string = verb_string[1:-1][:limit]
        self.parsed_length = len(self.parsed_string)
        self.dec_depth = 0
        self.dec_start = 0
        self.skip_next = False

        parse_parameter = (
            self._parse_dot_parameter if self.dot_parameter else self._parse_paranthesis_parameter
        )

        for i, v in enumerate(self.parsed_string):
            if self.skip_next:
                self.skip_next = False
                continue
            elif v == "\\":
                self.skip_next = True
                continue

            if v == ":" and not self.dec_depth:
                # if v == ":" and not dec_depth:
                self.set_payload()
                return
            elif parse_parameter(i, v):
                return
        else:
            self.set_payload()

    def _parse_paranthesis_parameter(self, i: int, v: str) -> bool:
        if v == "(":
            self.open_parameter(i)
        elif v == ")" and self.dec_depth:
            return self.close_parameter(i)
        return False

    def _parse_dot_parameter(self, i: int, v: str) -> bool:
        if v == ".":
            self.open_parameter(i)
        elif (v == ":" or i == self.parsed_length - 1) and self.dec_depth:
            return self.close_parameter(i + 1)
        return False

    def set_payload(self):
        res = self.parsed_string.split(":", 1)
        if len(res) == 2:
            self.payload = res[1]
        self.declaration = res[0]

    def open_parameter(self, i: int):
        self.dec_depth += 1
        if not self.dec_start:
            self.dec_start = i
            self.declaration = self.parsed_string[:i]

    def close_parameter(self, i: int) -> bool:
        self.dec_depth -= 1
        if self.dec_depth == 0:
            self.parameter = self.parsed_string[self.dec_start + 1 : i]
            try:
                if self.parsed_string[i + 1] == ":":
                    self.payload = self.parsed_string[i + 2 :]
            except IndexError:
                pass
            return True
        return False
