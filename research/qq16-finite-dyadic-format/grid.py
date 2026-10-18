"""Independent bounded max-plus audit of the QQ16 dyadic grid depth.

Source authentication belongs to verify.py. This module imports no candidate
arithmetic implementation and performs no file or network operations.
"""

import collections
import copy
import itertools

COUNTS = {
    "clear": 312,
    "add": 2704,
    "line": 336,
    "map": 464,
    "begin": 3,
    "end": 3,
    "checkpoint": 1,
}
COEFFICIENTS = {"1": 1084, "-1": 724, "1/4": 448, "-1/4": 448}
BORROWED = frozenset(f"{p}{i}" for p in "XY" for i in range(112))
OWNED = frozenset(f"{p}{i}" for p in "ZW" for i in range(112))
PRIVATE = frozenset(f"{p}{i}" for p in "FG" for i in range(8))
SCOPES = {"B1_current_query": 8, "future_logger_inverse": 8, "F0_inverse": 16}
FRAMES = frozenset({"current", "identity", "query2", "wide"} | {f"hole{i}" for i in range(112)})
MAX_FRONTIER = 337
MAX_PARAMETER = 16384


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate_word(word):
    """Validate the complete finite external event schema before traversal."""
    require(type(word) is list and len(word) == 3823, "word event capacity")
    lengths = {"clear": 3, "add": 4, "line": 4, "map": 5, "begin": 3, "end": 3, "checkpoint": 2}
    fields = BORROWED | OWNED | PRIVATE
    for event in word:
        require(type(event) is list and event and type(event[0]) is str, "event shape")
        op = event[0]
        require(op in lengths and len(event) == lengths[op], "operation shape")
        require(type(event[1]) is str, "event name")
        if op in ("begin", "end"):
            require(
                event[1] in SCOPES and type(event[2]) is int and event[2] == SCOPES[event[1]],
                "private scope schema",
            )
        elif op == "checkpoint":
            require(event[1] == "original_F0_outputs", "checkpoint schema")
        else:
            require(event[1] in fields, "destination schema")
            if op == "clear":
                require(type(event[2]) is str and event[2] in FRAMES, "CLEAR schema")
            elif op == "add":
                require(
                    type(event[2]) is str
                    and event[2] in fields
                    and type(event[3]) is str
                    and event[3] in COEFFICIENTS,
                    "ADD schema",
                )
            elif op == "line":
                require(
                    type(event[2]) is int
                    and 0 <= event[2] < 112
                    and type(event[3]) is int
                    and event[3] in (-1, 1),
                    "LINE schema",
                )
            else:
                require(
                    type(event[2]) is int
                    and event[2] in (1, 2)
                    and type(event[3]) is int
                    and 0 <= event[3] < 112
                    and type(event[4]) is bool,
                    "MAP schema",
                )
    require(dict(collections.Counter(event[0] for event in word)) == COUNTS, "event invoice")
    require(
        dict(collections.Counter(event[3] for event in word if event[0] == "add")) == COEFFICIENTS,
        "coefficient invoice",
    )


def _frontier(rows):
    """Coordinate domination proves the envelope for every nonnegative k."""
    require(len(rows) <= 2 * MAX_FRONTIER, "frontier input capacity")
    result = {
        row: path
        for row, path in rows.items()
        if not any(other != row and other[0] >= row[0] and other[1] >= row[1] for other in rows)
    }
    require(len(result) <= MAX_FRONTIER, "frontier output capacity")
    return result


def _advance(rows, zero, event, index, charge_lines, charge_quarters):
    op, destination = event[:2]
    if op == "clear":
        rows[destination] = {(0, 0): []}
        zero[destination] = True
        return
    require(destination in rows, "uninitialized destination")
    if op == "add":
        source = event[2]
        require(source in rows, "uninitialized source")
        inc = 2 if charge_quarters and "/" in event[3] else 0
        candidate = dict(rows[destination])
        for (a, b), path in rows[source].items():
            candidate[(a, b + inc)] = path + ([index] if inc else [])
        rows[destination] = _frontier(candidate)
        zero[destination] = zero[destination] and zero[source]
    elif op == "line":
        inc = int(charge_lines)
        rows[destination] = {
            (a + inc, b): path + ([index] if inc else [])
            for (a, b), path in rows[destination].items()
        }
    require(
        all(len(path) <= 1232 for path in rows[destination].values()), "dependency path capacity"
    )


def _audit(word, charge_lines=True, charge_quarters=True):
    rows = {name: {(0, 0): []} for name in BORROWED}
    zero = {name: False for name in BORROWED}
    scope, scratch, cuts, total, first_peak = None, set(), [], {(0, 0): []}, None
    for index, event in enumerate(word):
        op = event[0]
        if op == "begin":
            require(scope is None, "nested private scope")
            scope = event[1:]
            scratch = {f"F{i}" for i in range(8)}
            if event[2] == 16:
                scratch |= {f"G{i}" for i in range(8)}
            require(not scratch.intersection(rows), "private field reuse")
            continue
        if op == "end":
            require(scope == event[1:], "private scope end")
            require(all(name in rows and zero[name] for name in scratch), "private cleanup")
            for name in scratch:
                del rows[name]
                del zero[name]
            scope, scratch = None, set()
            continue
        if op == "checkpoint":
            continue
        destination = event[1]
        require(destination in OWNED | scratch, "borrowed or unavailable destination")
        _advance(rows, zero, event, index, charge_lines, charge_quarters)
        require(len(rows) <= 464, "live field capacity")
        total = _frontier(total | rows[destination])
        cuts.append((index, destination, tuple(sorted(rows[destination]))))
        if first_peak is None and (3, 6) in rows[destination]:
            first_peak = (index, destination, rows[destination][(3, 6)])
    require(scope is None and len(cuts) == 3816, "cut/scope inventory")
    return total, first_peak, cuts


def audit(word):
    """Return (global frontier, first (3,6) occurrence, every changed cut)."""
    validate_word(word)
    return _audit(word)


def numeric(word, q0, k):
    """Independent scalar recurrence, without affine/frontier operations."""
    validate_word(word)
    require(
        type(q0) is int and 0 <= q0 <= MAX_PARAMETER and type(k) is int and 0 <= k <= MAX_PARAMETER,
        "numeric parameter capacity",
    )
    q = {name: q0 for name in BORROWED}
    cuts = []
    for index, event in enumerate(word):
        op = event[0]
        if op == "clear":
            q[event[1]] = q0
        elif op == "add":
            q[event[1]] = max(q[event[1]], q[event[2]] + (2 if "/" in event[3] else 0))
        elif op == "line":
            q[event[1]] += k
        elif op == "end":
            for name in tuple(q):
                if name[:1] in "FG":
                    del q[name]
        if op in ("clear", "add", "line", "map"):
            cuts.append((index, q[event[1]]))
    require(len(cuts) == 3816, "numeric cut count")
    return cuts


def _numeric_checks(word, cuts):
    cases = 0
    for q0, b, h, depth in itertools.product((0, 1, 9), (0, 1, 64), (1, 2, 3, 8), (1, 2, 3)):
        s = (depth - 1).bit_length() + h * depth // 2
        k = b + 22 + s
        values = numeric(word, q0, k)
        for (index, value), (affine_index, _, rows) in zip(values, cuts, strict=True):
            require(
                index == affine_index and value == q0 + max(a * k + c for a, c in rows),
                "numeric/affine cut disagreement",
            )
        require(max(value for _, value in values) == q0 + 3 * k + 6, "numeric peak")
        cases += 1
    require(cases == 108, "numeric case count")
    return cases


def _rejection_controls(word):
    controls = []
    for kind in ("omitted line", "omitted quarter", "borrowed CLEAR", "dirty scratch read"):
        mutant = copy.deepcopy(word)
        if kind == "omitted line":
            del mutant[4]
        elif kind == "omitted quarter":
            del mutant[3711]
        elif kind == "borrowed CLEAR":
            mutant[0][1] = "X0"
        else:
            mutant[1][2] = "F0"
        try:
            audit(mutant)
        except ValueError:
            controls.append(kind)
        else:
            raise ValueError(f"ineffective control: {kind}")
    variants = ((False, True, "unpriced line"), (True, False, "unpriced quarter"))
    for lines, quarters, label in variants:
        changed, _, _ = _audit(word, charge_lines=lines, charge_quarters=quarters)
        require(set(changed) != {(3, 6)}, f"ineffective control: {label}")
        controls.append(label)
    return controls


def run_checks(word):
    """Return a deterministic receipt containing all source-derived cut rows."""
    total, peak, cuts = audit(word)
    require(
        set(total) == {(3, 6)} and peak is not None and peak[:2] == (3711, "Z0"),
        "declared affine bound",
    )
    require(all(len(rows) == 1 for _, _, rows in cuts), "unexpected affine branch")
    cases = _numeric_checks(word, cuts)
    controls = _rejection_controls(word)
    path = peak[2]
    require(
        sum(word[i][0] == "line" for i in path) == 3
        and sum(word[i][0] == "add" and "/" in word[i][3] for i in path) == 3,
        "peak path invoice",
    )
    return {
        "events": len(word),
        "changed_cuts": len(cuts),
        "grid_bound": "Q0+3*k+6",
        "first_peak": list(peak[:2]),
        "parameter_domain": "Q0>=0, k>=0; rounded caller uses k>=22",
        "cut_rows": [[index, field, list(rows[0])] for index, field, rows in cuts],
        "peak_path": [{"index": i, "event": word[i]} for i in path],
        "numeric_parameter_cases": cases,
        "numeric_cut_comparisons": cases * len(cuts),
        "controls": controls,
        "claim_limit": "Exact recurrence envelope; no actual exponent or precision minimum.",
    }
