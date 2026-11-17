"""Exact character-ring certificate for the selected real-body factor gauge."""

from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
DIM = 36
STAGES = 17
EVENTS = 4783
SOURCE_HASH = "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc"
CASE = (0, 1, 2, 4, 6, 8, 10, 12, 14, 18, 19, 20, 22, 24, 26, 28, 30, 32, 34, 36)
FILES = (
    "README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json",
    "verify.py", "independent.py", "NOTICE", "inputs/ORIGIN.json",
    "inputs/CALLER.json", "inputs/PR7439-NOTICE",
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def decode(raw):
    require(len(raw) <= 2**20, "caller byte cap")
    require(sha256(raw).hexdigest() == SOURCE_HASH, "caller source hash")
    caller = json.loads(raw)
    require(len(caller["events"]) == EVENTS, "event count")
    a = caller["types"]["A"]
    require(a["roles"] == DIM and a["offset"] == 0, "Type A inventory")
    require(a["alpha2"] == "-1" and a["beta2"] == "0", "Type A phase contract")
    require(len(a["diagonal"]) == DIM, "output diagonal size")
    for row in a["diagonal"]:
        require(len(row) == STAGES + 2 and row[:2] == [-1, 0], "diagonal convention")
        require(all(type(x) is int and x in (0, 1) for x in row[2:]), "body powers")
    return caller


def expand(caller, mutation=""):
    """Project the frozen caller to Type A and expand its literal body contacts."""
    actions = []
    for event in caller["events"]:
        if event[0] == "B":
            continue
        if event[0] == "J":
            _, stage, (a, b, c, d), _ = event
            require(1 <= stage <= STAGES and len({a, b, c, d}) == 4, "host shape")
            actions.extend((("query", b, a, Fraction(1)), ("query", c, d, Fraction(-1))))
            if mutation != "omit-host-8" or stage != 8:
                actions.extend(("body", role, 1 << (stage - 1), Fraction(1))
                               for role in (a, b, c, d))
            continue
        require(event[0] == "A", "unknown event family")
        _, op, dest, *args = event
        if op == "ADD":
            actions.append(("add", dest, args[0], Fraction(args[1])))
        elif op == "QUERY":
            require(args[1] == -1, "query exponent")
            actions.append(("query", dest, args[0], Fraction(1)))
        elif op == "SWAP":
            actions.append(("swap", dest, args[0], Fraction(1)))
        elif op == "SCALE":
            actions.append(("scale", dest, 0, Fraction(args[0])))
        elif op == "IDLE_ONE":
            stages = args[0]
            require(len(set(stages)) == len(stages), "duplicate idle body")
            require(all(1 <= j <= STAGES for j in stages), "idle stage range")
            mask = sum(1 << (j - 1) for j in stages)
            if mutation == "omit-idle-8":
                mask &= ~(1 << 7)
            actions.append(("body", dest, mask, Fraction(1)))
        else:
            require(op == "LAMBDA", "unknown Type A operation")
    require(len(actions) <= 20000, "expanded action cap")
    for kind, dest, source, coefficient in actions:
        require(0 <= dest < DIM, "destination range")
        if kind in ("add", "query", "swap"):
            require(0 <= source < DIM and source != dest, "source range")
        require(coefficient and coefficient.numerator.bit_length() <= 256
                and coefficient.denominator.bit_length() <= 256, "coefficient contract")
    return actions


def plus(a, b, coefficient=1):
    result = a.copy()
    for mask, value in b.items():
        entry = result.get(mask, 0) + coefficient * value
        if entry:
            result[mask] = entry
        else:
            result.pop(mask, None)
    require(len(result) <= 2048, "character capacity")
    return result


def times(a, b):
    result = {}
    for first, x in a.items():
        for second, y in b.items():
            mask = first ^ second
            result[mask] = result.get(mask, 0) + x * y
    result = {mask: value for mask, value in result.items() if value}
    require(len(result) <= 2048, "character product capacity")
    return result


def scalar(poly, coefficient=1, mask=0):
    return {key ^ mask: coefficient * value for key, value in poly.items()}


def identity():
    return [[{0: Fraction(1)} if i == j else {} for j in range(DIM)]
            for i in range(DIM)]


def add_row(matrix, inverse, dest, source, coefficient):
    matrix[dest] = [plus(x, y, coefficient)
                    for x, y in zip(matrix[dest], matrix[source], strict=True)]
    for row in range(DIM):
        inverse[row][source] = plus(inverse[row][source], inverse[row][dest], -coefficient)


def scale_row(matrix, inverse, dest, coefficient=1, mask=0):
    matrix[dest] = [scalar(poly, coefficient, mask) for poly in matrix[dest]]
    for row in range(DIM):
        inverse[row][dest] = scalar(inverse[row][dest], 1 / coefficient, mask)


def build(actions, q):
    matrix, inverse = identity(), identity()
    factors = []
    for kind, dest, source, coefficient in actions:
        if kind == "query":
            image = [inverse[row][dest] for row in range(DIM)]
            covector = [scalar(poly, 2 * coefficient) for poly in matrix[source]]
            nilpotent = {}
            for x, y in zip(image, covector, strict=True):
                nilpotent = plus(nilpotent, times(x, y))
            require(not nilpotent, "relative factor nilpotence")
            factors.append((image, covector))
        if kind in ("add", "query"):
            add_row(matrix, inverse, dest, source, coefficient * (q if kind == "query" else 1))
        elif kind == "swap":
            matrix[dest], matrix[source] = matrix[source], matrix[dest]
            for row in range(DIM):
                inverse[row][dest], inverse[row][source] = inverse[row][source], inverse[row][dest]
        else:
            scale_row(matrix, inverse, dest, coefficient, source if kind == "body" else 0)
    require(len(factors) == 38, "relative factor count")
    return factors, matrix


def endpoint(matrix, caller, q):
    for row in range(DIM):
        powers = caller["types"]["A"]["diagonal"][row][2:]
        mask = sum(value << j for j, value in enumerate(powers))
        for col in range(DIM):
            expected = {mask: Fraction(q)} if row == col else {}
            require(matrix[row][col] == expected, "symbolic endpoint")


def gauge_masks():
    chain = tuple((1 << min(max(j - 1, 0), 8)) - 1 for j in range(18))
    return chain + chain


def reference(factors):
    return [([sum(poly.values()) for poly in image],
             [sum(poly.values()) for poly in covector]) for image, covector in factors]


def certify(factors, unit, masks):
    nonzero = 0
    for index in CASE:
        image, covector = factors[index]
        old_image, old_covector = unit[index]
        for row in range(DIM):
            for col in range(DIM):
                actual = times(image[row], covector[col])
                value = old_image[row] * old_covector[col]
                expected = {masks[row] ^ masks[col]: value} if value else {}
                require(actual == expected, f"factor gauge at {index},{row},{col}")
                nonzero += bool(actual)
    return nonzero


def rejected(operation):
    try:
        operation()
    except ValueError:
        return
    raise ValueError("a negative control was accepted")


def controls(caller, factors, unit, masks, raw):
    for mutation in ("omit-host-8", "omit-idle-8"):
        changed, _ = build(expand(caller, mutation), 1)
        rejected(lambda: certify(changed, unit, masks))
    changed_masks = list(masks)
    changed_masks[9] ^= 1 << 7
    rejected(lambda: certify(factors, unit, changed_masks))
    changed_masks = list(masks)
    changed_masks[17] ^= 1 << 16
    rejected(lambda: certify(factors, unit, changed_masks))
    changed = list(factors)
    image, covector = changed[CASE[0]]
    changed[CASE[0]] = image, [scalar(poly, -1) for poly in covector]
    rejected(lambda: certify(changed, unit, masks))
    rejected(lambda: decode(raw + b" "))
    return 6


def main():
    raw = (HERE / "inputs/CALLER.json").read_bytes()
    caller = decode(raw)
    actions = expand(caller)
    factors, positive = build(actions, 1)
    _, negative = build(actions, -1)
    endpoint(positive, caller, 1)
    endpoint(negative, caller, -1)
    unit, masks = reference(factors), gauge_masks()
    nonzero = certify(factors, unit, masks)
    require(nonzero == 659, "selected displacement support count")
    result = {
        "claim_type": "scoped proof with exact character-ring certificate",
        "body_signs": STAGES, "roles": DIM, "selected_indices": CASE,
        "gauge_masks": masks, "nonzero_displacement_entries": nonzero,
        "zero_displacement_entries": len(CASE) * DIM * DIM - nonzero,
        "negative_controls": controls(caller, factors, unit, masks, raw),
        "source_sha256": SOURCE_HASH,
        "file_sha256": {name: sha256((HERE / name).read_bytes()).hexdigest() for name in FILES},
    }
    print(json.dumps(result, sort_keys=True))
    print("PASS_REAL_BODY_FACTOR_GAUGE selected_factors=20 signs=17 nonzero_entries=659 controls=6")


if __name__ == "__main__":
    main()
