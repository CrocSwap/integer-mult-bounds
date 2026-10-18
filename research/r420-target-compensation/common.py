"""Finite R420 compensation construction; Apache-2.0, substantial Codex assistance."""

import copy
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = "research/e8-bit-r420/data/bitE8mut-r420.json.gz"
V, R, N = 120, 420, 660


class Reject(ValueError):
    pass


def need(condition, message):
    if not condition:
        raise Reject(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def read_word():
    return json.loads(gzip.decompress((ROOT / WORD).read_bytes()))


def rows_of(word):
    need((word["v"], word["R"]) == (V, R), "wrong dimensions")
    rows = [0] * V
    for frame, destination, sources in word["D"]:
        need(frame == 0 and V <= destination < 2 * V, "original D shape")
        need(len(sources) == len(set(sources)), "duplicate helper")
        for source in sources:
            need(2 * V <= source < N, "original D must read helpers")
            rows[destination - V] ^= 1 << (source - 2 * V)
    return rows


def make_word(original, operations):
    """Emit E, the literal helper injection E K, then E inverse over F2."""
    rows = rows_of(original)
    basis = []
    for pair in operations:
        need(isinstance(pair, list) and len(pair) == 2, "bad basis pair")
        a, b = pair
        need(type(a) is int and type(b) is int and 0 <= a < V and 0 <= b < V and a != b,
             "invalid basis transvection")
        rows[a] ^= rows[b]
        basis.append([0, V + a, [V + b]])
    injection = [[0, V + a, [2 * V + b for b in range(R) if row >> b & 1]]
                 for a, row in enumerate(rows) if row]
    word = copy.deepcopy(original)
    word["D"] = basis + injection + list(reversed(basis))
    return word, rows


def scalar_stream(word):
    """ADD / COPY / CLEAR, keeping the inherited one-copy-at-a-time lifecycle."""
    stream = []
    for section in ("D", "A", "scatter", "B", "C"):
        if section == "scatter":
            for k, source in enumerate(word["ret"]):
                stream.append(("copy", N, source))
                for t, row in enumerate(word["scatter"]):
                    if k in row:
                        stream.append(("add", V + t, N))
                stream.append(("clear", N, source))
        else:
            for _, destination, sources in word[section]:
                stream.extend(("add", destination, source) for source in sources)
    return stream


def norm_replay(stream, reverse=False, initial=None):
    values = [1] * N + [0] if initial is None else list(initial)
    maximum = max(values)
    opened = None
    for kind, destination, source in (reversed(stream) if reverse else stream):
        if reverse:
            kind = {"copy": "clear", "clear": "copy"}.get(kind, kind)
        if kind == "add":
            need(destination != N and (source != N or opened is not None), "bad copy access")
            need(opened != destination, "copied original was changed")
            values[destination] += values[source]
            maximum = max(maximum, values[destination])
        elif kind == "copy":
            need(opened is None and destination == N, "bad copy opening")
            values[N] = values[source]
            opened = source
        else:
            need(kind == "clear" and opened == source and destination == N, "bad copy closure")
            values[N] = 0
            opened = None
    need(opened is None and values[N] == 0, "unclosed copy")
    return maximum, values


def bill(word):
    stream = scalar_stream(word)
    forward, _ = norm_replay(stream)
    reverse, _ = norm_replay(stream, reverse=True)
    five = 64 * forward ** 3 * reverse ** 2
    nine = (1 << 18) * forward ** 5 * reverse ** 4
    return {
        "D_adds": sum(len(g[2]) for g in word["D"]),
        "total_adds": sum(k == "add" for k, _, _ in stream),
        "forward": forward,
        "reverse": reverse,
        "five_stage_prefix": str(five),
        "five_stage_bits": five.bit_length(),
        "nine_stage_prefix": str(nine),
        "nine_stage_bits": nine.bit_length(),
        "charged_nine_stage_bits": 64 * ((nine.bit_length() + 63) // 64),
    }


def search_context(original):
    """Bounds just outside D, derived by literal execution of the fixed exterior."""
    need(not any(V <= source < 2 * V for section in ("A", "B", "C")
                 for _, _, sources in original[section] for source in sources),
         "the search formula assumes no target reads outside D")
    empty = dict(original, D=[])
    stream = scalar_stream(empty)
    initial = [1] * N + [0]
    initial[V:2 * V] = [0] * V
    exterior_peak, forward = norm_replay(stream, initial=initial)
    reverse_peak, reverse = norm_replay(stream, reverse=True)
    return exterior_peak, forward[V:2 * V], reverse_peak, reverse


def fourth_root(n):
    lo, hi = 0, 1 << ((n.bit_length() + 3) // 4)
    while hi - lo > 1:
        middle = (hi + lo) // 2
        if middle ** 4 <= n:
            lo = middle
        else:
            hi = middle
    need(lo ** 4 <= n < (lo + 1) ** 4, "fourth-root bracket")
    return lo
