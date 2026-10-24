"""R437 arithmetic stock certificates; no physical or Program admission.

Mihir Srivastava, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from dataclasses import dataclass
from functools import lru_cache

FAMILIES, STOCK_MULTIPLE, DIMENSION, MAX_RANK = 28416, 9475, 64, 42


def require(condition, message):
    if not condition:
        raise ValueError(message)


def positive_integer(value, name):
    require(type(value) is int and value > 0, "positive integer " + name)


def depth(n):
    positive_integer(n, "width")
    result = 0
    while n >= DIMENSION:
        n = MAX_RANK * (n // DIMENSION)
        result += 1
    return result


@lru_cache(None, typed=True)
def row_factor(q, w):
    """A = W |GL_64(F_q)| q^(4096(w-1)); prime q is an external premise."""
    positive_integer(q, "field order")
    positive_integer(w, "root precision")
    require(q >= 3 and q % 2 == 1, "odd field parameter")
    order = 1
    for i in range(DIMENSION):
        order *= q**DIMENSION - q**i
    return FAMILIES * order * q ** (DIMENSION**2 * (w - 1))


def stock_divisor(n, q, w):
    """Sharp for the complete rank-ceiling path model; see README proof."""
    d = depth(n)
    return 1 if d == 0 else STOCK_MULTIPLE * row_factor(q, w)**d


@dataclass(frozen=True)
class Node:
    width: int
    rows: int
    q: int
    w: int


def certify_path(root, nodes):
    """Check root anchoring, exact row inheritance and future stock sufficiency.

    A path may stop internally. The caller must separately authenticate the
    original root parameters and bind each node to actual Program events.
    """
    require(isinstance(root, Node), "typed root")
    require(isinstance(nodes, (list, tuple)) and len(nodes) > 0, "nonempty path")
    positive_integer(root.width, "root width")
    positive_integer(root.rows, "root rows")
    factor = row_factor(root.q, root.w)
    require(nodes[0] == root, "path begins at the supplied root")
    divisor = stock_divisor(root.width, root.q, root.w)
    require(root.rows % divisor == 0, "root stock covers every bounded path")
    for i, node in enumerate(nodes):
        require(isinstance(node, Node), "typed descendant")
        positive_integer(node.width, "descendant width")
        positive_integer(node.rows, "descendant rows")
        positive_integer(node.q, "descendant field")
        positive_integer(node.w, "descendant precision")
        require((node.q, node.w) == (root.q, root.w), "unchanged original-root field and precision")
        require(node.rows % stock_divisor(node.width, root.q, root.w) == 0,
                "descendant stock covers its remaining subtree")
        if node.width >= DIMENSION:
            require(node.rows % factor == 0, "complete family/low/high factors")
            require((node.rows // factor) % STOCK_MULTIPLE == 0,
                    "caller unused-row stock factor")
        if i:
            parent = nodes[i - 1]
            require(parent.width >= DIMENSION, "no transition below cutoff")
            require(node.width <= MAX_RANK * (parent.width // DIMENSION), "actual rank ceiling")
            require(parent.rows == factor * node.rows, "exact parent-to-child row quotient")
    return {"depth": depth(root.width), "transitions": len(nodes) - 1,
            "terminal_width": nodes[-1].width, "root_multiplier": root.rows // divisor,
            "scope": "arithmetic stock only; Program/source binding remains external"}
