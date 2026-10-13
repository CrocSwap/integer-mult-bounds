"""Independent integer-matrix checker for the frozen scalar SWAP experiment.

Prepared for ToikY with substantial OpenAI Codex assistance. Apache-2.0.
No compiler import: recognition multiplies actual two-coordinate integer maps;
replacement checking uses dense integer input columns, including arbitrary dirt.
"""

from collections import Counter
from fractions import Fraction


WORK = ("W", 0)


def require(condition, detail):
    if not condition:
        raise ValueError(detail)


def register(value):
    require(isinstance(value, (tuple, list)) and len(value) == 2,
            "invalid register")
    require(isinstance(value[0], str) and type(value[1]) is int,
            "invalid register coordinate")
    return tuple(value)


def recognize(events, start):
    """Return the two swapped coordinates/frame, or None, for four events.

    The class is exactly three unit ADD macros followed by a unit SCALE,
    all at one frame, involving two distinct native coordinates. Recognition
    checks the resulting dense matrix rather than either known literal pattern.
    """
    block = events[start:start + 4]
    if len(block) != 4 or any(event[0] != "scalar" for event in block):
        return None
    if any(event[2] != block[0][2] for event in block):
        return None
    ops = [event[1] for event in block]
    if [op[0] for op in ops] != ["add", "add", "add", "scale"]:
        return None
    coordinates = set()
    coefficients = []
    for op in ops:
        target = register(op[1])
        if target[0] != "L":
            return None
        coordinates.add(target)
        if op[0] == "add":
            source = register(op[2])
            if source[0] != "L" or source == target:
                return None
            coordinates.add(source)
            q = Fraction(op[3], op[4])
        else:
            q = Fraction(op[2], op[3])
        if abs(q) != 1:
            return None
        coefficients.append(int(q))
    if len(coordinates) != 2:
        return None
    a, b = sorted(coordinates)
    positions = {a: 0, b: 1}
    rows = [[1, 0], [0, 1]]
    for op, q in zip(ops, coefficients):
        target = positions[register(op[1])]
        if op[0] == "add":
            source = positions[register(op[2])]
            rows[target] = [x + q * y for x, y in zip(rows[target], rows[source])]
        else:
            rows[target] = [q * x for x in rows[target]]
    if rows != [[0, 1], [1, 0]]:
        return None
    return a, b, block[0][2]


def detect_runs(events):
    """Exhaustively scan; group only adjacent swaps at an identical frame."""
    runs = []
    i = 0
    while i < len(events):
        found = recognize(events, i)
        if found is None:
            i += 1
            continue
        a, b, frame = found
        start = i
        swaps = []
        permutation = {}
        while found is not None and found[2] == frame:
            a, b, _ = found
            swaps.append((a, b))
            permutation.setdefault(a, a)
            permutation.setdefault(b, b)
            permutation[a], permutation[b] = permutation[b], permutation[a]
            i += 4
            found = recognize(events, i)
        runs.append({"start": start, "end": i, "frame": frame,
                     "swaps": tuple(swaps),
                     "permutation": tuple(sorted(permutation.items()))})
    return runs


def check_replacement(run, primitives, work=WORK):
    """Prove complete local COPY/CLEAR map, with arbitrary work on entry.

    Every involved native coordinate and work is a separate input column.
    Replacements may overwrite work between cycles; no implicit clean input,
    free copy, free clear, or source restoration is supplied by this checker.
    """
    work = register(work)
    permutation = dict(run["permutation"])
    coordinates = sorted(permutation)
    require(work not in permutation, "work aliases native coordinate")
    require(set(permutation.values()) == set(coordinates), "not a permutation")
    order = coordinates + [work]
    positions = {r: i for i, r in enumerate(order)}
    width = len(order)
    rows = [[int(i == j) for j in range(width)] for i in range(width)]
    peak = 1
    counts = Counter()
    for primitive in primitives:
        require(isinstance(primitive, (list, tuple)) and primitive,
                "invalid primitive")
        tag = primitive[0]
        require(tag in ("copy", "clear"), "not a COPY/CLEAR replacement")
        require(len(primitive) == (3 if tag == "copy" else 2),
                "invalid primitive arity")
        target = register(primitive[1])
        require(target in positions, "unknown target coordinate")
        if tag == "clear":
            rows[positions[target]] = [0] * width
        else:
            source = register(primitive[2])
            require(source in positions and source != target,
                    "invalid copy source")
            rows[positions[target]] = rows[positions[source]].copy()
        counts[tag] += 1
        peak = max(peak, max(sum(abs(x) for x in row) for row in rows))
    expected = [[int(j == positions[permutation[r]]) for j in range(width)]
                for r in coordinates] + [[0] * width]
    require(rows == expected, "replacement permutation or dirty-work cleanup")
    return {"input_columns": width, "primitives": sum(counts.values()),
            "copies": counts["copy"], "clears": counts["clear"],
            "local_prefix_l1": peak}


def negative_controls():
    """Independent boundary controls, including incoming scratch dirt."""
    a, b = ("L", 0), ("L", 1)
    run = {"permutation": ((a, b), (b, a))}
    good = [("copy", WORK, a), ("copy", a, b),
            ("copy", b, WORK), ("clear", WORK)]
    require(check_replacement(run, good)["local_prefix_l1"] == 1,
            "positive swap control")
    bad = {
        "missing_clear": good[:-1],
        "missing_save": good[1:],
        "premature_clear": good[:2] + [good[-1], good[2]],
        "wrong_copy_direction": [good[0], ("copy", b, a), *good[2:]],
        "unknown_source": [("copy", WORK, ("L", 2)), *good[1:]],
    }
    rejected = []
    for name, word in bad.items():
        try:
            check_replacement(run, word)
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError("accepted negative control: " + name)
    return rejected


def scalar_runs(events):
    """Independently segment maximal adjacent scalar runs at one frame."""
    runs = []
    i = 0
    while i < len(events):
        if events[i][0] != "scalar":
            i += 1
            continue
        start, frame = i, events[i][2]
        while i < len(events) and events[i][0] == "scalar" and events[i][2] == frame:
            i += 1
        runs.append({"start": start, "end": i, "frame": frame})
    return runs


def _macro_count(op):
    """Independent PR696 per-real-component primitive formula."""
    tag = op[0]
    if tag in ("clear", "copy"):
        return 1
    q = Fraction(op[3], op[4]) if tag == "add" else Fraction(op[2], op[3])
    require(q != 0 and q.denominator & (q.denominator - 1) == 0,
            "invalid dyadic macro coefficient")
    a, b = abs(q.numerator), q.denominator
    if tag == "scale":
        require(a & (a - 1) == 0, "invalid scale coefficient")
        return abs(a.bit_length() - b.bit_length()) + int(q < 0)
    require(tag == "add", "unknown macro")
    return 2 if abs(q) == 1 else a.bit_length() + a.bit_count() + b.bit_length()


def _reference(op, work):
    """Literal PR696 trace, reconstructed without importing its lowering."""
    tag, target = op[0], register(op[1])
    if tag == "clear":
        return [("clear", target)]
    if tag == "copy":
        return [("copy", target, register(op[2]))]
    q = Fraction(op[3], op[4]) if tag == "add" else Fraction(op[2], op[3])
    if tag == "scale":
        exponent = abs(q.numerator).bit_length() - q.denominator.bit_length()
        word = [("double" if exponent > 0 else "halve", target)] * abs(exponent)
        return word + ([("negate", target)] if q < 0 else [])
    source = register(op[2])
    sign = "add" if q > 0 else "subtract"
    if abs(q) == 1:
        return [(sign, target, source), ("clear", work)]
    numerator = abs(q.numerator)
    word = [("copy", work, source)]
    for bit in range(numerator.bit_length() - 2, -1, -1):
        word.append(("double", work))
        if numerator & (1 << bit):
            word.append(("add", work, source))
    word += [("halve", work)] * (q.denominator.bit_length() - 1)
    return word + [(sign, target, work), ("clear", work)]


def _step(rows, primitive, width):
    require(isinstance(primitive, (tuple, list)) and primitive, "invalid primitive")
    tag = primitive[0]
    binary = tag in ("add", "subtract", "copy")
    require(tag in ("clear", "copy", "double", "halve", "negate", "add", "subtract"),
            "unknown primitive")
    require(len(primitive) == (3 if binary else 2), "invalid primitive arity")
    target = register(primitive[1])
    require(target in rows, "unknown target coordinate")
    if tag == "clear":
        rows[target] = [0] * width
    elif binary:
        source = register(primitive[2])
        require(source in rows and source != target, "invalid primitive source")
        if tag == "copy":
            rows[target] = rows[source].copy()
        else:
            sign = 1 if tag == "add" else -1
            rows[target] = [x + sign * y for x, y in zip(rows[target], rows[source])]
    else:
        factor = {"double": 2, "halve": Fraction(1, 2), "negate": -1}[tag]
        rows[target] = [factor * x for x in rows[target]]
    return target


def check_block(events, start, end, primitives, work=WORK):
    """Check remapped-run primitives against the original exact macro map.

    Dense Fraction columns include every touched scalar coordinate plus dirty
    coefficient work. Each replacement prefix row must occur somewhere in the
    original PR696 prefix trace. This cross-register equality, stronger than
    comparing row norms, preserves the maximum over registers for arbitrary
    correlated incoming values. Register names may differ during the run.
    """
    work = register(work)
    require(type(start) is int and type(end) is int and 0 <= start < end <= len(events),
            "invalid block interval")
    block = events[start:end]
    require(all(event[0] == "scalar" and event[2] == block[0][2] for event in block),
            "block crosses scalar/frame boundary")
    coordinates = set()
    for event in block:
        op = event[1]
        coordinates.add(register(op[1]))
        if op[0] in ("add", "copy"):
            coordinates.add(register(op[2]))
    require(work not in coordinates, "work aliases native coordinate")
    order = sorted(coordinates) + [work]
    width = len(order)
    identity = {r: [int(i == j) for j in range(width)] for i, r in enumerate(order)}
    expected = {r: row.copy() for r, row in identity.items()}
    reference = {r: row.copy() for r, row in identity.items()}
    seen = {tuple(row) for row in identity.values()}
    old_peak, old_count = 1, 0
    for event in block:
        op = event[1]
        tag, target = op[0], register(op[1])
        count = _macro_count(op)
        word = _reference(op, work)
        require(len(word) == count, "independent reference count")
        old_count += count
        for primitive in word:
            changed = _step(reference, primitive, width)
            row = reference[changed]
            seen.add(tuple(row))
            old_peak = max(old_peak, sum(abs(x) for x in row))
        if tag == "clear":
            expected[target] = [0] * width
        elif tag == "copy":
            expected[target] = expected[register(op[2])].copy()
        elif tag == "scale":
            q = Fraction(op[2], op[3])
            expected[target] = [q * x for x in expected[target]]
        else:
            require(tag == "add", "unknown macro")
            q, source = Fraction(op[3], op[4]), register(op[2])
            require(source != target, "aliased macro addition")
            expected[target] = [x + q * y for x, y in zip(expected[target], expected[source])]
            expected[work] = [0] * width
    require(reference == expected, "reference trace does not implement original macros")
    candidate = {r: row.copy() for r, row in identity.items()}
    peak, counts = 1, Counter()
    for primitive in primitives:
        changed = _step(candidate, primitive, width)
        row = candidate[changed]
        require(tuple(row) in seen, "replacement prefix row absent from original trace")
        peak = max(peak, sum(abs(x) for x in row))
        counts[primitive[0]] += 1
    require(candidate == expected, "replacement block map or dirty-work cleanup")
    return {"input_columns": width, "native_coordinates": len(coordinates),
            "original_PR696_count": old_count,
            "replacement_count": sum(counts.values()),
            "saved": old_count - sum(counts.values()),
            "prefix_l1_original": str(old_peak), "prefix_l1_replacement": str(peak),
            "prefix_containment": "exact cross-register rows",
            "primitive_tags": dict(sorted(counts.items()))}


def block_controls():
    """Synthetic cycle, interleaved-operation, dirt and prefix controls."""
    a, b, c = ("L", 0), ("L", 1), ("L", 2)

    def swap(x, y):
        return [["scalar", ["add", list(x), list(y), 1, 1], 7],
                ["scalar", ["add", list(y), list(x), -1, 1], 7],
                ["scalar", ["add", list(x), list(y), 1, 1], 7],
                ["scalar", ["scale", list(y), -1, 1], 7]]

    cycle = swap(a, b) + swap(a, c)
    word = [("copy", WORK, a), ("copy", a, c), ("copy", c, b),
            ("copy", b, WORK), ("clear", WORK)]
    cycle_receipt = check_block(cycle, 0, len(cycle), word)
    require(cycle_receipt["replacement_count"] == 5, "cycle positive control")
    interleaved = swap(a, b) + [["scalar", ["add", list(a), list(c), 1, 1], 7]] + swap(a, b)
    identity_receipt = check_block(interleaved, 0, len(interleaved),
                                   [("add", b, c), ("clear", WORK)])
    require(identity_receipt["replacement_count"] == 2, "remapped operation control")
    rejected = []
    mutations = {
        "cycle_missing_clear": word[:-1],
        "cycle_missing_save": word[1:],
        "cycle_wrong_order": [word[0], word[2], word[1], *word[3:]],
        "cycle_endpoint_neutral_growth": [("double", a), ("halve", a)] + word,
    }
    for name, candidate in mutations.items():
        try:
            check_block(cycle, 0, len(cycle), candidate)
        except ValueError as error:
            if name == "cycle_endpoint_neutral_growth":
                require(str(error) == "replacement prefix row absent from original trace",
                        "growth control failed for another reason")
            rejected.append(name)
        else:
            raise ValueError("accepted negative control: " + name)
    wrong_frame = [event.copy() for event in cycle]
    wrong_frame[-1][2] = 8
    try:
        check_block(wrong_frame, 0, len(wrong_frame), word)
    except ValueError as error:
        require(str(error) == "block crosses scalar/frame boundary", "frame control")
        rejected.append("cross_frame_block")
    else:
        raise ValueError("accepted cross-frame block")
    return {"cycle": cycle_receipt, "interleaved": identity_receipt,
            "rejected": rejected}
