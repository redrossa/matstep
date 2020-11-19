cmd = {
    "left":     r"\left",
    "right":    r"\right",
    "begin":    r"\begin",
    "end":      r"\end",
    "frac":     r"\frac",
    "xr_arrow": r"\xrightarrow",
    "xl_arrow": r"\xleftarrow",
}


sym = {
    "[":        cmd["left"]  + "[",
    "]":        cmd["right"] + "]",
    "{":        cmd["left"]  + "{",
    "}":        cmd["right"] + "}",
    "(":        cmd["left"]  + "(",
    ")":        cmd["right"] + ")",
    "r_arrow":  r"\rightarrow",
    "l_arrow":  r"\leftarrow",
    "lr_arrow": r"\leftrightarrow",
}


def environment(type, content, *args):
    """
    Returns a LaTeX representation of an environment of the given type whose content
    is the given string. Additional arguments for the specific environment type are
    given as variable arguments.

    :param type: the type of the environment
    :param content: the string content inside the environment
    :param args: any additional arguments for the given type
    :return: a LaTeX representation of an environment of the given type whose content
             is the given string
    """
    s_type = "{" + type + "}"
    s_args = "{" + "}{".join(arg for arg in args) + "}" if len(args) > 0 else ""
    return cmd["begin"] + s_type + s_args + "\n" + \
           content + "\n" + \
           cmd["end"] + s_type


def align(*lines, eq=False):
    """
    Returns a LaTeX representation of an "align*" type environment whose content
    is the given variable arguments. The variable arguments are a list of strings
    representing one line in the environment containing 0 or 1 equality operators.
    If the boolean argument eq is False, the lines are left-aligned, otherwise
    they are aligned by the three equality operators "=", "<", ">" if True.

    :param lines: a list of string variable arguments representing individual lines
           in the environment
    :param eq: if False, lines are left-aligned, otherwise they are aligned by the
           three equality operators "=", "<", ">" if True
    :return: a LaTeX representation of an "align*" type environment whose content
             is lines of the given variable arguments aligned either left or by
             equality operators
    """
    content = "&\n" + " \\\\\n&\n".join(lines) if not eq \
        else " \\\\\n".join(lines).replace("=", "&=").replace("<", "&<").replace(">", "&>")
    return environment("align*", content)


def center(*lines):
    """
    Returns a LaTeX representation of a "gather*" type environment whose content
    is the given variable arguments. The variable arguments are a list of strings
    representing one line in the environment. The lines are center-aligned.

    :param lines: a list of string variable arguments representing individual lines
           in the environment
    :return: a LaTeX representation of an "gather*" type environment whose content
             is lines of the given variable arguments aligned center
    """
    content = " \\\\\n".join(lines)
    return environment("gather*", content)


def matrix(list2D, format=""):
    """
    Returns a LaTeX representation of an "array" type environment whose content correspond
    to the list elements inside the the given 2-D list, surrounded by an opening and a closing
    brackets. The 2-D list is in the same format as that passed to a sympy.Matrix constructor.
    Therefore each elements in the 2-D list represents a row in the array type environment.
    The matrix representation can be in augmented format if e.g. the given format == "ccc|c"
    or non-augmented format if the given format is e.g. "ccc" or just not provided. Of course
    the number of "c"s (although it can be any other letter), must correspond to at least the
    largest row in the given 2-D list.

    :param list2D: a list representing the matrix to be formatted. The 2-D list is in the
           same list format as that passed to a sympy.Matrix constructor
    :param format: the format of the laTeX matrix, specifying either augmented or not
    :return: a LaTeX representation of an "array" type environment whose content correspond
             to the list elements inside the the given 2-D list, surrounded by an opening and a closing
             brackets
    """
    format = "c" * len(max(list2D, key=len))
    content = " \\\\\n".join(str(" & ".join(str(e) for e in row)) for row in list2D)
    return sym["["] + "\n" + \
           environment("array", content, format) + "\n" + \
           sym["]"]


def annotated_arrow(type: str, bot="", top=""):
    """
    Returns a LaTeX representation of an annotated arrow, which can either be pointing towards
    the left or right direction and whose annotation string can be placed on the bottom and/or
    on top the arrow.

    :param type: the type of the arrow; string "l" or "left" all case-insensitive is a left arrow,
           string "r" or "right" all case-insensitive is a right arrow
    :param bot: the string annotation to be placed on the bottom of the arrow
    :param top: the string annotation to be placed on top of the arrow
    :return: a LaTeX representation of an annotated arrow
    :except ValueError: if the given type of arrow is invalid
    """
    if type.lower() != "l" and type.lower() != "left" and type.lower() != "r" and type.lower() != "right":
        raise ValueError("Invalid arrow type '" + type + "'")
    arrow = cmd["x" + type[0] + "_arrow"]
    s_bot = "[" + bot + "]"
    s_top = "{" + top + "}"
    return arrow + s_bot + s_top

