"""Bounded constructors for the balanced dirty word and its new attaining cut."""

MAX_G = 9
MAX_N = 2**MAX_G - 1
MAX_LEAVES = 4**MAX_G


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sizes(n):
    require(type(n) is int and 1 <= n <= MAX_N, "unsupported factor count")
    counts = [0, 1] + [0] * (n - 1)
    for k in range(2, n + 1):
        counts[k] = 2 * (counts[k // 2] + counts[k - k // 2])
    return counts


def children(node):
    k, sign, source, target, scratch, base = node
    require(k > 1 and sign in (-1, 1), "not an internal call")
    b = k // 2
    u = (b, 1, source, scratch, scratch + 1, base)
    v = (k - b, 1, scratch, target, scratch + 1, base + b)
    ui = (b, -1, source, scratch, scratch + 1, base)
    vi = (k - b, -1, scratch, target, scratch + 1, base + b)
    if sign == 1:
        return (("U", u), ("V", v), ("U'", ui), ("V'", vi))
    return (("V", v), ("U", u), ("V'", vi), ("U'", ui))


def word(n, sign=1):
    counts = sizes(n)
    require(type(sign) is int and sign in (-1, 1), "invalid sign")
    stack = [(n, sign, 0, 1, 2, 0)]
    events = []
    for _ in range(4 * MAX_LEAVES):
        if not stack:
            require(len(events) == counts[n], "leaf count mismatch")
            return events
        node = stack.pop()
        k, sg, source, target, _, base = node
        if k == 1:
            events.append((source, target, base, sg))
        else:
            stack.extend(child for _, child in reversed(children(node)))
    raise ValueError("word expansion exhausted its node bound")


def locate(n, path):
    """Return the zero-based first leaf and final node of a phase path."""
    counts = sizes(n)
    require(len(path) <= MAX_G, "path too deep")
    node = (n, 1, 0, 1, 2, 0)
    offset = 0
    for name in path:
        found = False
        for candidate, child in children(node):
            if candidate == name:
                node = child
                found = True
                break
            offset += counts[child[0]]
        require(found, "invalid phase name")
    return offset, node


def keeping_path(n, sign):
    """The classical y-keeping chain, used as a credited constituent."""
    sizes(n)
    require(type(sign) is int and sign in (-1, 1), "invalid sign")
    path = []
    for _ in range(MAX_G):
        if n == 1:
            return tuple(path)
        path.append("U'" if sign == 1 else "U")
        n //= 2
        sign = -sign
    raise ValueError("keeping path exhausted its depth bound")


def exit_family(h, sign):
    """2h-1 distinct leaves with h distinct exit monomials at size 2^h-1."""
    require(type(h) is int and 1 <= h < MAX_G, "unsupported exit depth")
    require(type(sign) is int and sign in (-1, 1), "invalid sign")
    paths = []
    prefix = ()
    for level in range(h, 1, -1):
        q = 2 ** (level - 1)
        paths.append(prefix + ("V",) + keeping_path(q, 1))
        paths.append(prefix + ("V'",) + keeping_path(q, -1))
        prefix += ("U'" if sign == 1 else "U",)
        sign = -sign
    paths.append(prefix)
    require(len(paths) == 2 * h - 1, "exit-family size mismatch")
    return tuple(paths)


def witness(g):
    require(type(g) is int and 3 <= g <= MAX_G, "unsupported attaining depth")
    h = g - 1
    n = 2**g - 1
    cut_path = ("V'", "V'", "U") + ("V",) * (h - 2)
    last, leaf = locate(n, cut_path)
    require(leaf[0] == 1, "cut path must end at a completed leaf")
    paths = []
    for name, sign in (("U", 1), ("U'", -1)):
        paths.extend((name,) + p for p in exit_family(h, sign))
    q = 2 ** (h - 1)
    for prefix, sign in ((("V", "U"), 1), (("V", "U'"), -1),
                         (("V'", "U"), 1)):
        paths.append(prefix + keeping_path(q, sign))
    indices = []
    for path in paths:
        index, node = locate(n, path)
        require(node[0] == 1 and index <= last, "injection outside cut")
        indices.append(index)
    require(len(indices) == len(set(indices)) == 4 * g - 3,
            "injections must be distinct")
    return n, last + 1, tuple(sorted(indices))


def readout_formula(g):
    require(type(g) is int and 3 <= g <= MAX_G, "unsupported readout depth")
    h = g - 1
    b = 2**h - 1
    q = 2 ** (h - 1)
    r = 2 ** (h - 2)
    end = b + q + r
    row = {2: {tuple(reversed(range(b, end))): 1},
           3: {tuple(reversed(range(b + q, end))): 1}, 4: {(): 1}}
    for level in range(1, h - 1):
        row[4 + level] = {tuple(reversed(range(end - r // 2**level, end))): 1}
    return row
