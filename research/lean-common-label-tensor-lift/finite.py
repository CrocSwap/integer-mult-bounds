"""Exact small Gaussian-matrix audit; this file does not run Lean.

Gareth Davidson with OpenAI Codex assistance. Apache-2.0.
"""
from dataclasses import dataclass
from fractions import Fraction as Q
from functools import lru_cache
from itertools import product
import hashlib
import json


def need(ok, message):
    if not ok:
        raise ValueError(message)


@dataclass(frozen=True)
class G:
    re: Q = Q(0)
    im: Q = Q(0)

    def __post_init__(self):
        object.__setattr__(self, "re", Q(self.re))
        object.__setattr__(self, "im", Q(self.im))

    def __add__(self, other):
        other = gaussian(other)
        return G(self.re + other.re, self.im + other.im)

    __radd__ = __add__

    def __neg__(self):
        return G(-self.re, -self.im)

    def __sub__(self, other):
        return self + -gaussian(other)

    def __mul__(self, other):
        other = gaussian(other)
        return G(self.re * other.re - self.im * other.im,
                 self.re * other.im + self.im * other.re)

    __rmul__ = __mul__

    def __truediv__(self, other):
        other = gaussian(other)
        norm = other.re ** 2 + other.im ** 2
        need(norm != 0, "division by zero")
        return self * G(other.re / norm, -other.im / norm)


def gaussian(value):
    return value if isinstance(value, G) else G(value)


Z, O, I = G(), G(1), G(0, 1)


def matrix(rows):
    return tuple(tuple(gaussian(x) for x in row) for row in rows)


def eye(n):
    return matrix([[int(r == s) for s in range(n)] for r in range(n)])


def mm(a, b):
    need(len(a[0]) == len(b), "matrix shape")
    return tuple(tuple(sum((x * y for x, y in zip(row, col)), Z)
                       for col in zip(*b)) for row in a)


def mv(a, v):
    need(len(a[0]) == len(v), "vector shape")
    return tuple(sum((x * y for x, y in zip(row, v)), Z) for row in a)


def inv2(a):
    ((a00, a01), (a10, a11)) = a
    det = a00 * a11 - a01 * a10
    out = matrix([[a11 / det, -a01 / det], [-a10 / det, a00 / det]])
    need(mm(a, out) == eye(2) == mm(out, a), "inverse")
    return out


def kron(a, b):
    return tuple(tuple(x * y for x in row_a for y in row_b)
                 for row_a in a for row_b in b)


@lru_cache(None)
def label(j, name):
    """Heterogeneous noncommuting shears and a genuine unary phase."""
    return {
        "I": eye(2),
        "A": matrix([[1, Q(j + 1, 2)], [0, 1]]),
        "B": matrix([[1, 0], [j + 1, 1]]),
        "P": matrix([[I, 0], [0, I]]),
    }[name]


@lru_cache(None)
def tensor_label(f, name, inverse=False):
    """Endpoint oracle: direct coordinate products, independent of kron()."""
    addresses = list(product(range(2), repeat=f))
    columns = [inv2(label(j, name)) if inverse else label(j, name) for j in range(f)]
    def entry(a, b):
        out = O
        for j in range(f):
            out *= columns[j][a[j]][b[j]]
        return out
    return tuple(tuple(entry(a, b) for b in addresses) for a in addresses)


@lru_cache(None)
def tensor_recipe(f, source, target, fault=None):
    out = ((O,),)
    for j in range(f):
        a, b = label(j, source), label(j, target)
        if fault == "omit_unary_phase":
            a = eye(2) if source == "P" else a
            b = eye(2) if target == "P" else b
        step = mm(inv2(a), b) if fault == "reverse_recipe" else mm(b, inv2(a))
        out = kron(out, step)
    return out


INITIAL = ("I", "A", "B", "P")
WORD = (
    ("clear", 3, "I"), ("copy", 3, 0, "I"),
    ("relabel", 1, "A", "I"), ("add", 1, 3, Q(1, 2)),
    ("scale", 1, Q(-1)), ("relabel", 0, "I", "B"),
    ("relabel", 3, "I", "B"), ("add", 0, 3, Q(-1, 2)),
    ("relabel", 1, "I", "B"), ("add", 1, 0, Q(2)),
    ("relabel", 2, "B", "I"), ("copy", 3, 2, "I"),
    ("relabel", 3, "I", "P"), ("scale", 3, Q(-1)),
    ("relabel", 3, "P", "B"), ("add", 1, 3, Q(1, 2)),
    ("clear", 3, "I"), ("relabel", 0, "B", "P"),
    ("relabel", 1, "B", "A"),
)


def labels_and_shadow(word, initial=INITIAL):
    labels, shadow = list(initial), eye(4)
    for event in word:
        op, r, *args = event
        gate = [list(row) for row in eye(4)]
        if op == "relabel":
            source, target = args
            need(labels[r] == source, "wrong relabel source")
            labels[r] = target
        elif op == "add":
            s, q = args
            need(labels[r] == labels[s], "mismatched ADD labels")
            gate[r][s] += q
        elif op == "scale":
            gate[r][r] = G(args[0])
        elif op == "copy":
            s, name = args
            need(labels[s] == name, "wrong COPY label")
            labels[r] = name
            gate[r] = [G(int(c == s)) for c in range(4)]
        elif op == "clear":
            labels[r] = args[0]
            gate[r] = [Z] * 4
        else:
            raise ValueError("unknown event")
        shadow = mm(tuple(tuple(row) for row in gate), shadow)
    return tuple(labels), shadow


def physical(f, word, h, fault=None):
    state = list(h)
    for event in word:
        op, r, *args = event
        if op == "relabel":
            state[r] = mv(tensor_recipe(f, *args, fault), state[r])
        elif op in ("add", "scale"):
            q = args[-1]
            if fault == "tensor_role_coefficient":
                q **= f
            if op == "scale":
                state[r] = tuple(q * x for x in state[r])
            else:
                state[r] = tuple(x + q * y for x, y in zip(state[r], state[args[0]]))
        elif op == "copy":
            state[r] = state[args[0]]
            if fault == "destructive_copy":
                state[args[0]] = (Z,) * (2 ** f)
        elif op == "clear":
            if fault != "omit_clear":
                state[r] = (Z,) * (2 ** f)
        else:
            raise ValueError("unknown event")
    return tuple(state)


def endpoint(f, word, h):
    final, shadow = labels_and_shadow(word)
    canonical = [mv(tensor_label(f, name, True), h[r]) for r, name in enumerate(INITIAL)]
    mixed = [tuple(sum((shadow[r][s] * canonical[s][k] for s in range(4)), Z)
                   for k in range(2 ** f)) for r in range(4)]
    return tuple(mv(tensor_label(f, name), mixed[r]) for r, name in enumerate(final))


def fixture(f, seed):
    # Dense coefficients depend jointly on role and the complete address.
    # In particular this is not generated by multiplying per-column vectors.
    return tuple(tuple(G(Q((r + 2) * (k + 1) + seed, 2 ** (k % 3)),
                         Q((k * k + r + seed) % 7 - 3, 2))
                       for k in range(2 ** f)) for r in range(4))


def packed(h):
    return [[[str(x.re), str(x.im)] for x in row] for row in h]


def replay():
    digest = hashlib.sha256()
    basis_cases = dense_cases = prefix_cases = 0
    for f in range(5):
        n = 2 ** f
        for c in range(4 * n):
            h = tuple(tuple(G(int(r * n + k == c)) for k in range(n)) for r in range(4))
            actual = physical(f, WORD, h)
            need(actual == endpoint(f, WORD, h), "basis endpoint mismatch")
            digest.update(json.dumps(packed(actual), separators=(",", ":")).encode())
            basis_cases += 1
        for seed in range(4):
            h = fixture(f, seed)
            need(physical(f, WORD, h) == endpoint(f, WORD, h), "dense endpoint mismatch")
            dense_cases += 1
        h = fixture(f, 17)
        for stop in range(len(WORD) + 1):
            prefix = WORD[:stop]
            need(physical(f, prefix, h) == endpoint(f, prefix, h), "prefix invariant mismatch")
            prefix_cases += 1
        final, shadow = labels_and_shadow(WORD)
        need(shadow[2] == eye(4)[2], "fixture unit row")
        h = fixture(f, 91)
        unary = mv(tensor_label(f, final[2]), mv(tensor_label(f, INITIAL[2], True), h[2]))
        need(physical(f, WORD, h)[2] == unary, "unit row contaminated by dirty roles")
        need(all(shadow[r][3] == Z for r in range(4)), "private input survives overwrite")
    controls = []
    h = fixture(3, 29)
    expected = endpoint(3, WORD, h)
    for fault in ("tensor_role_coefficient", "omit_unary_phase", "reverse_recipe",
                  "destructive_copy", "omit_clear"):
        need(physical(3, WORD, h, fault) != expected, "undetected fault: " + fault)
        controls.append(fault)
    for name, word in (
        ("ADD_labels", (("add", 0, 1, Q(1)),)),
        ("relabel_source", (("relabel", 0, "B", "A"),)),
        ("COPY_label", (("copy", 3, 0, "A"),)),
    ):
        try:
            labels_and_shadow(word)
        except ValueError:
            controls.append(name)
        else:
            raise ValueError("admitted invalid labels: " + name)
    # This word is well-labelled, yet its one-column identity is insufficient.
    need(2 * Q(1, 2) == 1 and 2 * Q(1, 2) ** 2 == Q(1, 2), "bare endpoint")
    need((-1) ** 2 != -1 and (1 + 1) ** 2 != 1 ** 2 + 1 ** 2, "shortcut witnesses")
    controls += ["bare_endpoint", "role_sign", "tensor_of_sum"]
    return {"schema": "common-label-tensor-finite/1", "widths": list(range(5)),
            "events": len(WORD), "roles": 4, "address_field": "Q(i)",
            "basis_cases": basis_cases, "dense_cases": dense_cases, "prefix_cases": prefix_cases,
            "endpoint_sha256": digest.hexdigest(), "rejected_shortcuts": controls,
            "kernel_checked": False}


if __name__ == "__main__":
    print(json.dumps(replay(), sort_keys=True, indent=2))
