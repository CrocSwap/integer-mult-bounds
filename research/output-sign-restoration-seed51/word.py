"""Exact words for fixed linear readers that negate their source port.

Sagar Thakrar, with substantial OpenAI Codex assistance. Apache-2.0.
"""


def check_tree(tree, width, outputs):
    if type(width) is not int or type(outputs) is not int or min(width, outputs) < 1:
        raise ValueError("positive integer register widths required")
    if not isinstance(tree, dict):
        raise ValueError("a reader is a matrix leaf or a nonempty child list")
    if set(tree) == {"matrix"}:
        matrix = tree["matrix"]
        if not isinstance(matrix, (list, tuple)) or len(matrix) != outputs:
            raise ValueError("matrix output width mismatch")
        for row in matrix:
            if not isinstance(row, (list, tuple)) or len(row) != width:
                raise ValueError("matrix source width mismatch")
            if any(type(c) is not int or c not in (-1, 0, 1) for c in row):
                raise ValueError("leaf coefficients must be -1, 0 or 1")
        return 0
    if set(tree) != {"children"} or not isinstance(tree["children"], (list, tuple)) or not tree["children"]:
        raise ValueError("a reader is a matrix leaf or a nonempty child list")
    return 1 + max(check_tree(child, width, outputs) for child in tree["children"])


def inverse(word):
    return [("add", op[1], op[2], -op[3]) if op[0] == "add" else op
            for op in reversed(word)]


def compile_word(tree, width, outputs, *, eager=False, reader=False):
    """Return a frozen ADD/NEG word and its number of scalar registers.

Registers are D, X, then one arbitrary dirty width-sized block per tree level.
An echo preserves X; a reader additionally negates X on return.
"""
    depth = check_tree(tree, width, outputs)
    if type(eager) is not bool or type(reader) is not bool:
        raise ValueError("eager and reader must be booleans")
    if not reader and "children" not in tree:
        raise ValueError("an echo requires at least one child")

    def negate(start, size):
        return [("neg", start + j) for j in range(size)]

    def child_word(node, level):
        source = outputs + level * width
        if "matrix" in node:
            word = [("add", i, source + j, c)
                    for i, row in enumerate(node["matrix"])
                    for j, c in enumerate(row) if c]
        else:
            word = echo_word(node, level)
        return word + negate(source, width)

    def echo_word(node, level):
        source = outputs + level * width
        scratch = source + width
        batch = []
        children = node["children"]
        use_workspace = eager or width <= outputs
        for i, child in enumerate(children):
            if not use_workspace and i:
                batch += negate(0, outputs)
            batch += child_word(child, level + 1)
            if use_workspace:
                batch += negate(scratch, width)
        if not use_workspace:
            batch += negate(scratch, width) if len(children) % 2 else negate(0, outputs)
        copy = [("add", scratch + j, source + j, 1) for j in range(width)]
        return copy + batch + inverse(copy) + inverse(batch)

    word = child_word(tree, 0) if reader else echo_word(tree, 0)
    return word, outputs + (depth + 1) * width
