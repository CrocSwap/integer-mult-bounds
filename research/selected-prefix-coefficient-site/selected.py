"""Two actual selected source sites, reconstructed from main's pinned inputs.

The selection, label and chart conventions adapt Jose Manuel's PR2234
provider; the retained PR1627 reader supplies rational frame projectors.
"""
from dataclasses import dataclass
from fractions import Fraction
from hashlib import sha256
import importlib.util
import json
from pathlib import Path

from algebra import eye, inverse, multiply, projector, split_basis
from tapes import need


ROOT = Path(__file__).resolve().parents[2]


def reduce_matrix(a, modulus):
    return [[x.numerator * pow(x.denominator, -1, modulus) % modulus for x in row] for row in a]


@dataclass(frozen=True)
class Request:
    record: tuple
    rank: int
    base: tuple
    sigma: tuple
    source_sigma: tuple

    def preparation(self, q, width):
        modulus = q ** width
        base = reduce_matrix(self.base, modulus)
        basis = split_basis(base, self.rank, q, modulus)
        return multiply(reduce_matrix(self.sigma, modulus), basis, modulus)


def requests():
    path = ROOT / "research/pr589-five-helper-hosting/verify.py"
    spec = importlib.util.spec_from_file_location("retained_selected_prefix_source", path)
    old = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(old)
    word, host, geometry = (old.read(p) for p in (old.WORD, old.HOST, old.GEO))
    call = host["calls"][0]
    program = host["local_programs"][call["orientation"]]
    idles = {e["idx"]: e for e in host["schedule"] if e["kind"] == "idle"}
    result = []
    for position, expected_op, expected_role, expected_key in (
        (21816, 2, 472, "c097fc120eea0e30ceaae6f2f6bad489ec86945dfecb852fb50c2d46d64185cd"),
        (18085, 0, 222, "5a7dce9c52ac8c9c23fa89766439abfc412b5242b444945289a83828ffa9ae6d"),
    ):
        event = program[position]
        need(event[:2] == [expected_op, expected_role], "actual selected literal site")
        a, b, rank = event[3:6] if expected_op == 2 else event[2:5]
        pa, ra = old.projection([word["lines"][i] for i in word["frames"][a]])
        pb, rb = old.projection([word["lines"][i] for i in word["frames"][b]])
        low, high = (pa, pb) if ra <= rb else (pb, pa)
        local = old.sub(high, low)
        need(abs(ra-rb) == rank, "selected residual rank")
        key = sha256(json.dumps(["local", rank, [[str(x) for x in row] for row in local]],
                               sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        need(key == expected_key, "exact selected base label")
        base = [[Fraction(0) for _ in range(64)] for _ in range(64)]
        for i in range(8):
            base[i][:8] = local[i]
        family, route = call["owners"][expected_role]
        need(route[0] == "hosted", "chosen actual hosted owner")
        _, child, offset, width = route
        axes = old.pending_axes(idles[child])[offset:offset+width]
        need(len(axes) == 8, "complete selected owner support")
        port = family % 111 if min(axes) < 8 else -1
        source_sigma = [[Fraction(x) for x in row] for row in eye(64)]
        if port >= 0:
            item = geometry["ports"][port]
            for i in range(8):
                source_sigma[i][:8] = [Fraction(item["q"][i], 2)] + list(map(Fraction, item["complement_columns"][i]))
        permutation = list(range(64))
        for i, j in zip(sorted(set(range(8))-set(axes)), sorted(set(axes)-set(range(8)))):
            permutation[i], permutation[j] = j, i
        source_sigma = [[row[permutation[j]] for j in range(64)] for row in source_sigma]
        sigma = [[Fraction(x) for x in row] for row in eye(64)] if expected_op == 2 else source_sigma
        chart = ("identity", -1, -1, ()) if expected_op == 2 else ("host", port, -1, tuple(axes))
        source_chart = ("host", port, -1, tuple(axes)) if expected_op == 2 else None
        record = ("COPY" if expected_op == 2 else "MOVE", 0, position, expected_role,
                  host["live"] if expected_op == 2 else family, a, b, key, rank, chart,
                  "common" if expected_op == 2 else "owner", source_chart)
        result.append(Request(record, rank, tuple(map(tuple, base)), tuple(map(tuple, sigma)),
                              tuple(map(tuple, source_sigma))))
    return tuple(result)


def raw_fixture(request, q, width, high=1, row=None, unit_low=False, bad=False):
    modulus = q ** width
    row = request.rank if row is None else row
    h = eye(64)
    if bad:
        h[0][0], h[0][row], h[row][0], h[row][row] = q, q-1, 1, 1+q*high
    elif unit_low:
        h[0][0], h[0][row], h[row][0], h[row][row] = 1+q*high, 1, 1, 2
    else:
        h[0][row], h[row][0], h[row][row] = 1, q*high, 1+q*high
    raw = multiply(h, inverse(request.preparation(q, width), modulus), modulus)
    low = tuple(tuple(x % q for x in row) for row in raw)
    digits = tuple(x // q for row in raw for x in row)
    return low, digits


def prepare(request, low, digits, q, width):
    modulus = q ** width
    raw = [[low[i][j] + q*digits[64*i+j] for j in range(64)] for i in range(64)]
    h = multiply(raw, request.preparation(q, width), modulus)
    p = projector(h, request.rank, modulus)
    common = multiply(raw, reduce_matrix(request.sigma, modulus), modulus)
    direct = multiply(multiply(common, reduce_matrix(request.base, modulus), modulus),
                      inverse(common, modulus), modulus)
    need(p == direct, "raw selected projector equals prepared projector")
    return p
