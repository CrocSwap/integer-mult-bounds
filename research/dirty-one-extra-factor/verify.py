"""Exact corroboration of the one-extra-factor theorem. Apache-2.0."""
import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAX_LITERAL_N = 17
MAX_HEIGHT = 32


def need(condition, message):
    if not condition:
        raise ValueError(message)


def bound(h):
    need(type(h) is int and 0 <= h <= 10000, "height outside capacity")
    return h*h//2+h+3


def leaves(n):
    need(type(n) is int and 1 <= n <= 2**MAX_HEIGHT+1, "factor capacity")
    p = 1 << (n.bit_length()-1)
    return 3*p*n-2*p*p


def children(node):
    lo, n, x, y, depth, sign = node
    need(n > 1 and sign in (-1, 1), "nonleaf contract")
    a, z = n//2, depth+2
    calls = [(lo, a, x, z, depth+1, 1),
             (lo+a, n-a, z, y, depth+1, 1),
             (lo, a, x, z, depth+1, -1),
             (lo+a, n-a, z, y, depth+1, -1)]
    if sign == -1:
        calls = [(*c[:-1], -c[-1]) for c in reversed(calls)]
    return calls


def emit(n, sign=1):
    need(type(n) is int and 1 <= n <= MAX_LITERAL_N, "literal capacity")
    need(sign in (-1, 1), "orientation")
    stack, events = [(0, n, 0, 1, 0, sign)], []
    for _ in range(2*leaves(n)):
        if not stack:
            return events
        node = stack.pop()
        lo, count, x, y, _, direction = node
        if count == 1:
            events.append((x, y, lo, direction))
        else:
            stack.extend(reversed(children(node)))
    raise ValueError("literal traversal budget exhausted")


def eye(d, polynomial=False):
    if polynomial:
        return [[{(): 1} if i == j else {} for j in range(d)] for i in range(d)]
    return [[int(i == j) for j in range(d)] for i in range(d)]


def formal_step(matrix, event):
    x, y, factor, sign = event
    old = matrix[y]
    out = []
    for left, right in zip(old, matrix[x]):
        value = left.copy()
        for word, c in right.items():
            key = (factor,)+word
            value[key] = value.get(key, 0)+sign*c
            if not value[key]:
                del value[key]
        out.append(value)
    matrix[y] = out


def masses(matrix):
    return [sum(abs(c) for entry in row for c in entry.values()) for row in matrix]


def exhaustive(n):
    """Every nonempty ordered interval, via both chronological orientations."""
    d = (n-1).bit_length()+2
    maximum, tested, witness = 1, 0, None
    for sign in (1, -1):
        events = emit(n, sign)
        for start in range(len(events)):
            matrix = eye(d, True)
            for end in range(start, len(events)):
                formal_step(matrix, events[end])
                values = masses(matrix)
                if max(values) > maximum:
                    maximum = max(values)
                    witness = [sign, start, end+1, values.index(maximum)]
                tested += 1
    h = (n-1).bit_length()-1
    need(maximum == bound(h), "new fixed-length envelope mismatch")
    return {"n": n, "ordered_nonempty_intervals": tested,
            "maximum": maximum, "first_witness": witness}


def scalar_prefix(n, cut, negatives):
    """Skip complete calls; update prefix and inverse by exact shears."""
    need(0 <= cut <= leaves(n), "cut range")
    need(len(negatives) <= MAX_HEIGHT and all(0 <= v < n for v in negatives),
         "negative factor contract")
    d = (n-1).bit_length()+2
    prefix, inverse = eye(d), eye(d)
    stack = [(0, n, 0, 1, 0, 1)]
    budget = 4*((n-1).bit_length()+1)
    for _ in range(budget):
        if cut == 0:
            return prefix, inverse
        need(bool(stack), "missing call")
        node = stack.pop()
        lo, count, x, y, _, sign = node
        length = leaves(count)
        if length <= cut:
            coefficient = sign*(-1)**sum(lo <= j < lo+count for j in negatives)
            prefix[y] = [v+coefficient*w for v, w in zip(prefix[y], prefix[x])]
            for row in inverse:
                row[x] -= coefficient*row[y]
            cut -= length
        else:
            stack.extend(reversed(children(node)))
    raise ValueError("compressed traversal budget exhausted")


def scalar_family(h):
    need(1 <= h <= MAX_HEIGHT, "family height")
    n = 2**h+1
    negatives = tuple(2**h-2**j-1 for j in range(h-1))
    a, b = 3*4**(h-1)//5, (4**h+5)//3
    _, inverse = scalar_prefix(n, a, negatives)
    prefix, _ = scalar_prefix(n, b, negatives)
    row = [sum(v*inverse[j][k] for j, v in enumerate(prefix[1]))
           for k in range(len(inverse))]
    expected = [(-1)**(h-1)*(1+h//2), 1]
    expected += [j*(-1)**(h+j) for j in range(1, h+1)]+[1]
    need(row == expected, "attaining row identity")
    need(sum(map(abs, row)) == bound(h), "attaining norm")
    if n <= MAX_LITERAL_N:
        matrix = eye(len(row), True)
        for event in emit(n)[a:b]:
            formal_step(matrix, event)
        literal = [sum(c*(-1)**sum(j in negatives for j in word)
                       for word, c in entry.items()) for entry in matrix[1]]
        need(literal == row, "literal/compressed attaining row")
    return {"h": h, "n": n, "cuts": [a, b], "row": row, "norm": bound(h)}


def controls():
    rejected = 0
    for operation in (lambda: bound(-1), lambda: leaves(0),
                      lambda: emit(MAX_LITERAL_N+1), lambda: emit(3, 0),
                      lambda: scalar_prefix(5, leaves(5)+1, ()),
                      lambda: scalar_prefix(5, 1, (5,))):
        try:
            operation()
        except ValueError:
            rejected += 1
        else:
            raise ValueError("invalid contract accepted")
    row = scalar_family(4)["row"]
    need(sum(map(abs, row)) > bound(4)-1, "understated-bound control")
    positive, _ = scalar_prefix(17, 87, ())
    _, inverse = scalar_prefix(17, 38, ())
    changed = [sum(v*inverse[j][k] for j, v in enumerate(positive[1]))
               for k in range(len(inverse))]
    need(changed != row, "factor-sign control")
    events = emit(5)
    need(emit(5, -1) == [(x, y, f, -s) for x, y, f, s in reversed(events)],
         "literal inverse order")
    return {"rejected_contracts": rejected, "mathematical_controls": 3}


def source_checks():
    external = json.loads((HERE/"PREDECESSOR.json").read_text())
    for name, digest in external["files"].items():
        need(hashlib.sha256((HERE/"prior"/name).read_bytes()).hexdigest() == digest,
             "retained predecessor bytes")
    manifest = json.loads((HERE/"SOURCES.json").read_text())
    root = HERE.parent.parent
    for entry in manifest["files"]:
        if entry["usage"] == "input":
            need(hashlib.sha256((root/entry["path"]).read_bytes()).hexdigest()
                 == entry["sha256"], "main source binding")


def calculate():
    source_checks()
    for h in range(1, 10001):
        left = h*h//2+h+3
        right = (h+1)*(h+1)//2+2
        repeated = bound(h-1)+1
        need(left == bound(h) and right <= bound(h) and repeated <= bound(h),
             "phase arithmetic")
    return {"status": "PASS_DIRTY_ONE_EXTRA_FACTOR",
            "claim_type": "scoped proof with finite corroboration",
            "phase_arithmetic_heights": [1, 10000],
            "exhaustive": [exhaustive(17)],
            "attaining_family": [scalar_family(h) for h in range(1, MAX_HEIGHT+1)],
            "controls": controls()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", type=Path)
    args = parser.parse_args()
    result = calculate()
    if args.write:
        args.write.write_text(json.dumps(result, indent=2)+"\n")
    else:
        need(result == json.loads((HERE/"RESULT.json").read_text()), "receipt mismatch")
    files = sorted(p for p in HERE.rglob("*") if p.is_file())
    digests = {str(p.relative_to(HERE)): hashlib.sha256(p.read_bytes()).hexdigest()
               for p in files if "__pycache__" not in p.parts}
    print(json.dumps({"status": result["status"], "file_sha256": digests,
                      "exhaustive": result["exhaustive"],
                      "family_heights": [1, MAX_HEIGHT],
                      "controls": result["controls"]}, sort_keys=True))


if __name__ == "__main__":
    main()
