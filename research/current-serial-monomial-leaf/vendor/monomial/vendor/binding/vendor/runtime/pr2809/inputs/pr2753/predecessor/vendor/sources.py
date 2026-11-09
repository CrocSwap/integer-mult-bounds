"""Compile fixed selected rational labels and low classes.

This stage depends on q and the fixed selected catalogue, never on the input
width or high digits. Runtime inverses and coefficients come from words.py.
The selection/chart conventions adapt PR2234 and PR2405 with attribution.
"""
from dataclasses import dataclass
from fractions import Fraction as F
from hashlib import sha256
import importlib.util
import json
from pathlib import Path

from words import need


ROOT = Path(__file__).resolve().parents[3]


def identity(n):
    return [[F(i == j) for j in range(n)] for i in range(n)]


def product(a, b):
    out = [[F(0) for _ in b[0]] for _ in a]
    for i, row in enumerate(a):
        for k, x in enumerate(row):
            if x:
                for j, y in enumerate(b[k]):
                    if y:
                        out[i][j] += x*y
    return out


def independent_columns(matrix, q):
    # q is fixed when compiling the finite source vocabulary.
    rows = [[x.numerator*pow(x.denominator, -1, q) % q for x in row] for row in matrix]
    rank, chosen = 0, []
    for j in range(len(matrix[0])):
        pivot = next((i for i in range(rank, len(rows)) if rows[i][j]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        inv = pow(rows[rank][j], -1, q)
        rows[rank] = [x*inv % q for x in rows[rank]]
        for i in range(len(rows)):
            if i != rank and rows[i][j]:
                c = rows[i][j]
                rows[i] = [(x-c*y) % q for x, y in zip(rows[i], rows[rank])]
        chosen.append(j)
        rank += 1
        if rank == len(rows):
            break
    return chosen


@dataclass(frozen=True)
class Template:
    q: int
    rank: int
    record: tuple
    base: tuple
    chart: tuple
    preparation: tuple


@dataclass(frozen=True)
class Specification:
    code: int
    template: Template
    low: tuple
    good: bool


def compile_specification(code, template, low):
    """Compile the finite low-class branch, with no width/high input."""
    import oracle
    q = template.q
    need(len(low) == 64 and all(len(row) == 64 and all(0 <= x < q for x in row) for row in low),
         "fixed raw low class")
    h = oracle.multiply(low, oracle.reduce_rational(template.preparation, q), q)
    inv = oracle.inverse(h, q)
    p = oracle.multiply([row[:template.rank] for row in h], inv[:template.rank], q)
    try:
        oracle.good_pivots(p, template.rank, q)
        good = True
    except ValueError:
        good = False
    return Specification(code, template, tuple(map(tuple, low)), good)


def compile_templates(q=3):
    path = ROOT / "research/pr589-five-helper-hosting/verify.py"
    spec = importlib.util.spec_from_file_location("retained_binary_control_source", path)
    old = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(old)
    word, host, geometry = (old.read(p) for p in (old.WORD, old.HOST, old.GEO))
    call = host["calls"][0]
    program = host["local_programs"][call["orientation"]]
    idles = {event["idx"]: event for event in host["schedule"] if event["kind"] == "idle"}
    templates = []
    for position, op, role, key in (
        (21816, 2, 472, "c097fc120eea0e30ceaae6f2f6bad489ec86945dfecb852fb50c2d46d64185cd"),
        (18085, 0, 222, "5a7dce9c52ac8c9c23fa89766439abfc412b5242b444945289a83828ffa9ae6d"),
    ):
        event = program[position]
        need(event[:2] == [op, role], "exact selected literal")
        a, b, rank = event[3:6] if op == 2 else event[2:5]
        pa, ra = old.projection([word["lines"][i] for i in word["frames"][a]])
        pb, rb = old.projection([word["lines"][i] for i in word["frames"][b]])
        lo, hi = (pa, pb) if ra <= rb else (pb, pa)
        local = old.sub(hi, lo)
        observed = sha256(json.dumps(["local", rank, [[str(x) for x in row] for row in local]],
                                    sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        need(observed == key and abs(ra-rb) == rank, "selected projector identity")
        base = [[F(0) for _ in range(64)] for _ in range(64)]
        for i in range(8):
            base[i][:8] = local[i]
        family, route = call["owners"][role]
        need(route[0] == "hosted", "selected hosted source")
        _, child, offset, width = route
        axes = old.pending_axes(idles[child])[offset:offset+width]
        port = family % 111 if min(axes) < 8 else -1
        chart = identity(64)
        if op != 2:
            if port >= 0:
                entry = geometry["ports"][port]
                for i in range(8):
                    chart[i][:8] = [F(entry["q"][i], 2)] + list(map(F, entry["complement_columns"][i]))
            pi = list(range(64))
            for i, j in zip(sorted(set(range(8))-set(axes)), sorted(set(axes)-set(range(8)))):
                pi[i], pi[j] = j, i
            chart = [[row[pi[j]] for j in range(64)] for row in chart]
        complement = [[F(i == j)-base[i][j] for j in range(64)] for i in range(64)]
        image, kernel = independent_columns(base, q), independent_columns(complement, q)
        need((len(image), len(kernel)) == (rank, 64-rank), "fixed low-field split basis")
        basis = [[base[i][j] for j in image] + [complement[i][j] for j in kernel] for i in range(64)]
        # PB=BE over the rationals, before any input-width modulus exists.
        projected_basis = [[basis[i][j] if j < rank else F(0) for j in range(64)] for i in range(64)]
        need(product(base, basis) == projected_basis and len(independent_columns(basis, q)) == 64,
             "rational split basis with unit determinant modulo fixed q")
        preparation = product(chart, basis)
        record = ("COPY" if op == 2 else "MOVE", 0, position, role,
                  host["live"] if op == 2 else family, a, b, key, rank,
                  "common" if op == 2 else "owner", tuple(axes), port)
        templates.append(Template(q, rank, record, tuple(map(tuple, base)), tuple(map(tuple, chart)),
                                  tuple(map(tuple, preparation))))
    return tuple(templates)
