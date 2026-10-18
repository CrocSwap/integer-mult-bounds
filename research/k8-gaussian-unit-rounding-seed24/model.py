"""Static Gaussian-unit gauges, Hanson Sun with OpenAI Codex, Apache-2.0.

The real macro lowering is Sagar Thakrar's PR696; the local word is the
source-bound PR1094/1042 k8 word. No pending PR implementation is imported.
"""
from collections import Counter, defaultdict
from fractions import Fraction as Q
from functools import lru_cache
import copy
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = "410026dc5513b87db92ae98571d1d5984c69a983"
ARCHIVE1042 = "research/community-frontier1042-audit/selected-replay.tar.gz"
ARCHIVE1094 = "research/community-frontier1094-audit/selected-replay.tar.gz"
LOWER = "research/complex-dyadic-lowering/lower.py"
INPUTS = frozenset((ARCHIVE1042, ARCHIVE1094, LOWER,
    "research/community-frontier1042-audit/RESULT.json",
    "research/community-frontier1094-audit/RESULT.json",
    "research/complex-dyadic-lowering/README.md",
    "docs/research/community-batch1099-review.md"))
MEMBERS = ("CANONICAL-WORD.json.gz", "LOCAL-PROGRAMS.json.gz",
           "INDEPENDENT-LOCAL-REPLAY.json", "LOCAL-CHECKS.json")
ZERO = (Q(0), Q(0))
ONE = (Q(1), Q(0))


def require(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def check_sources(manifest=None, reader=None):
    manifest = manifest or json.loads((HERE / "SOURCES.json").read_bytes())
    reader = reader or (lambda p: (ROOT / p).read_bytes())
    require(manifest["base_commit"] == BASE, "base commit")
    rows = [r for r in manifest["files"] if r["usage"] == "input"]
    require(len(rows) == len(INPUTS) and {r["path"] for r in rows} == INPUTS,
            "source inventory")
    for r in rows:
        data = reader(r["path"])
        require(sha(data) == r["sha256"], "source SHA256: " + r["path"])
        blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        require(blob == r["git_blob"], "source Git blob: " + r["path"])
    return manifest


def load():
    check_sources()
    raw = {}
    with tarfile.open(ROOT / ARCHIVE1042) as archive:
        for name in MEMBERS:
            raw[name] = archive.extractfile("slots/local/" + name).read()
    with tarfile.open(ROOT / ARCHIVE1094) as archive:
        for name in MEMBERS:
            actual = archive.extractfile(
                "candidate/strict/global8/base/providers/gauge44/" + name).read()
            require(actual == raw[name], "selected provider alias: " + name)
    objects = {n: json.loads(gzip.decompress(b) if n.endswith(".gz") else b)
               for n, b in raw.items()}
    word, programs, replay, checks = (objects[n] for n in MEMBERS)
    old = (ROOT / "research/community-frontier1042-audit/RESULT.json").read_bytes()
    current = json.loads((ROOT / "research/community-frontier1094-audit/RESULT.json").read_bytes())
    require(current["baseline_receipt_sha256"] == sha(old), "baseline receipt binding")
    require(json.loads(old)["status"] == "PASS_COMPLETE_PR1042_COMPOSITION" and
            current["status"] == "PASS_COMPLETE_PR1094_COMPOSITION", "retained receipt status")
    require(replay["canonical_word_sha256"] == sha(raw[MEMBERS[0]]) and
            replay["local_programs_sha256"] == sha(raw[MEMBERS[1]]), "native receipt binding")
    require((word["v"], word["h"], word["R"]) == (112, 9, 480), "source geometry")
    require(set(programs) == {"forward", "backward"}, "orientations")
    bindings = {n: {"archive_member_sha256": sha(b),
                   "payload_sha256": sha(gzip.decompress(b) if n.endswith(".gz") else b)}
                for n, b in raw.items()}
    return word, programs, bindings, replay, checks


def domain(word, programs):
    excluded = set(word["centers"])
    for events in programs.values():
        for event in events:
            if event[0] == "residual_adapter":
                excluded.add(event[2])
            if event[0] == "scalar" and event[1][0] in ("copy", "clear"):
                excluded.update(r[1] for r in event[1][1:]
                                if isinstance(r, list) and r[0] == "L")
    return [h for h in range(224, 704) if h not in excluded
            and word["start"][h] == 0 and word["final"][h] == 1]


def power(e):
    return Q(2 ** e) if e >= 0 else Q(1, 2 ** -e)


def parts(q):
    q = Q(q)
    p = abs(q.numerator)
    require(p > 0 and q.denominator & (q.denominator - 1) == 0, "nonzero dyadic")
    twos = (p & -p).bit_length() - 1
    return p >> twos, twos - (q.denominator.bit_length() - 1)


def c_parts(p, e):
    require(p > 0 and p % 2 == 1, "positive odd numerator")
    return 2 + p.bit_length() - 1 + p.bit_count() + abs(e) - int(p == 1 and e == 0)


def c(q):
    return c_parts(*parts(q))


def mul(x, y):
    return x[0] * y[0] - x[1] * y[1], x[0] * y[1] + x[1] * y[0]


def inv(x):
    d = x[0] ** 2 + x[1] ** 2
    require(d != 0, "nonzero Gaussian factor")
    return x[0] / d, -x[1] / d


def gauge(a, odd, phase=0):
    require(odd in (0, 1) and phase in range(4), "Gaussian-unit parameters")
    return mul((power(a), power(a) if odd else Q(0)),
               (ONE, (Q(0), Q(1)), (Q(-1), Q(0)), (Q(0), Q(-1)))[phase])


def gaussian_add_cost(z):
    if z[0] == 0 or z[1] == 0:
        return 2 * c(z[0] or z[1])
    require(abs(z[0]) == abs(z[1]), "axis or diagonal Gaussian coefficient")
    return 2 * c(z[0]) + 2


def unit_coordinates(z):
    """Normal form for units of Z[1/2,i]; rejects nonunits."""
    require(z != ZERO, "nonzero Gaussian unit")
    if z[0] == 0 or z[1] == 0:
        p, a = parts(z[0] or z[1])
        require(p == 1, "Gaussian dyadic unit norm")
        phase = (0 if z[0] > 0 else 2) if z[1] == 0 else (1 if z[1] > 0 else 3)
        return a, 0, phase
    require(abs(z[0]) == abs(z[1]), "Gaussian dyadic unit diagonal")
    p, a = parts(z[0])
    require(p == 1, "Gaussian dyadic unit norm")
    phase = {(True, True): 0, (False, True): 1,
             (False, False): 2, (True, False): 3}[z[0] > 0, z[1] > 0]
    return a, 1, phase


def terms_by_helper(events):
    terms = defaultdict(list)
    for event in events:
        if event[0] == "scalar" and event[1][0] == "add":
            g = event[1]
            require(g[1] != g[2], "distinct ADD operands")
            p, e = parts(Q(g[3], g[4]))
            for r, sign in ((g[1], 1), (g[2], -1)):
                if r[0] == "L":
                    terms[r[1]].append((p, e, sign))
    return terms


def real_delta(terms, k):
    return 4 * abs(k) + 2 * sum(c_parts(p, e + s * k) - c_parts(p, e)
                              for p, e, s in terms)


def odd_delta(terms, a):
    # The two-register boundary minimum is attained by boundary_word below.
    return 2 * abs(2 * a + 1) + 4 + sum(
        2 * c_parts(p, e + s * a - int(s < 0)) + 2 - 2 * c_parts(p, e)
        for p, e, s in terms)


def census(events, helpers):
    by_helper = terms_by_helper(events)
    rows = []
    for helper in helpers:
        terms = by_helper[helper]
        real_points = sorted({0} | {-s * e for p, e, s in terms})
        odd_points = sorted({-1, 0} | {-s * e - int(s < 0) for p, e, s in terms})
        real = [[k, real_delta(terms, k)] for k in real_points]
        odd = [[a, odd_delta(terms, a)] for a in odd_points]
        rows.append({"helper": helper, "incident_adds": len(terms),
                     "real_candidates": real, "odd_candidates": odd,
                     "real_best": min(real, key=lambda x: (x[1], abs(x[0]), x[0])),
                     "odd_best": min(odd, key=lambda x: (x[1], abs(x[0]), x[0])),
                     "outward_tail_slope": 4 + 2 * len(terms)})
    return rows


def boundary_word(a, odd, target=("X",)):
    """Exact minimum for phase-zero gauge and its inverse; no work register."""
    x, y = tuple(target) + (0,), tuple(target) + (1,)
    if not odd:
        e = a
        result = []
    elif a >= 0:
        e = a
        result = [("add", y, x), ("double", x), ("subtract", x, y)]
    else:
        e = a + 1
        result = [("subtract", x, y), ("halve", x), ("add", y, x)]
    scales = [("double" if e > 0 else "halve", r)
              for r in (x, y) for _ in range(abs(e))]
    forward = scales + result
    inverse_tag = {"add": "subtract", "subtract": "add", "double": "halve", "halve": "double"}
    backward = [(inverse_tag[g[0]], *g[1:]) for g in reversed(forward)]
    expected = 2 * abs(2 * a + 1) + 4 if odd else 4 * abs(a)
    require(len(forward) + len(backward) == expected, "boundary determinant/shear lower bound")
    return forward, backward


@lru_cache(maxsize=1)
def real_lowerer():
    spec = importlib.util.spec_from_file_location("pinned_pr696_lower", ROOT / LOWER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.lower


def lower_gaussian(z, target=("T",), source=("S",)):
    """Share each source-channel product across both targets, then clear work.

    Uses exactly the two existing real coefficient-work registers. Each may be
    arbitrarily dirty on entry. Target/source complex registers must be distinct.
    """
    require(tuple(target) != tuple(source), "distinct complex operands")
    require(z != ZERO, "nonzero Gaussian ADD")
    require(z[0] == 0 or z[1] == 0 or abs(z[0]) == abs(z[1]), "Gaussian support")
    out = []
    for channel, coefficients in enumerate(((z[0], z[1]), (-z[1], z[0]))):
        src = tuple(source) + (channel,)
        work = ("W", channel)
        entries = [(tuple(target) + (i,), q) for i, q in enumerate(coefficients) if q]
        dst, q = entries[0]
        word = real_lowerer()(["add", dst, src, q.numerator, q.denominator], work=work)
        if len(entries) == 2:
            other, coefficient = entries[1]
            require(abs(coefficient) == abs(q), "shared product magnitude")
            operand = src if abs(q) == 1 else work
            word.insert(len(word) - 1,
                        ("add" if coefficient > 0 else "subtract", other, operand))
        out.extend(word)
    require(len(out) == gaussian_add_cost(z), "Gaussian primitive invoice")
    return out


def transformed(events, gauges):
    """Return scalar Gaussian macros; non-scalar events remain unchanged."""
    factors = {("L", h): gauge(a, odd) for h, (a, odd) in gauges.items()}
    stream = []
    for event in events:
        if event[0] != "scalar":
            stream.append(copy.deepcopy(event))
            continue
        g = event[1]
        tag, target = g[0], tuple(g[1])
        if tag == "add":
            source = tuple(g[2])
            z = mul((Q(g[3], g[4]), Q(0)),
                    mul(factors.get(target, ONE), inv(factors.get(source, ONE))))
            op = [tag, list(target), list(source), [z[0].numerator, z[0].denominator],
                  [z[1].numerator, z[1].denominator]]
        elif tag == "scale":
            op = [tag, list(target), [g[2], g[3]], [0, 1]]
        else:
            require(tag in ("clear", "copy"), "scalar opcode")
            require(not any(tuple(r) in factors for r in g[1:] if isinstance(r, list)),
                    "no gauge on copy/clear carrier")
            op = copy.deepcopy(g)
        stream.append(["scalar", op, *event[2:]])
    return stream


def replay(stream, gauges, orientation):
    """Exact complex-linear maps: 712 complex columns = 1424 real columns."""
    rows = {("L", i): {i: ONE} for i in range(704)}
    rows.update({("C", i): {704 + i: ONE} for i in range(8)})

    def scale(target, z):
        rows[target] = {i: mul(v, z) for i, v in rows[target].items()}

    for helper, (a, odd) in gauges.items():
        scale(("L", helper), gauge(a, odd))
    for event in stream:
        if event[0] != "scalar":
            continue
        g = event[1]
        tag, target = g[0], tuple(g[1])
        if tag == "clear":
            rows[target] = {}
        elif tag == "copy":
            rows[target] = dict(rows[tuple(g[2])])
        elif tag == "scale":
            scale(target, (Q(*g[2]), Q(*g[3])))
        elif tag == "add":
            source = tuple(g[2])
            require(source != target, "distinct replay operands")
            z = Q(*g[3]), Q(*g[4])
            for i, value in rows[source].items():
                delta = mul(value, z)
                old = rows[target].get(i, ZERO)
                new = old[0] + delta[0], old[1] + delta[1]
                if new == ZERO:
                    rows[target].pop(i, None)
                else:
                    rows[target][i] = new
        else:
            raise ValueError("Gaussian scalar opcode")
    for helper, (a, odd) in gauges.items():
        scale(("L", helper), inv(gauge(a, odd)))
    for i in range(704):
        expected = {i: ONE}
        if orientation == "forward" and 112 <= i < 224:
            expected[i - 112] = ONE
        if orientation == "backward" and i < 112:
            expected[i + 112] = (Q(-1), Q(0))
        require(rows["L", i] == expected, "all-column endpoint " + str((orientation, i)))
    require(all(not rows["C", i] for i in range(8)), "private centres cleared")
    return {"complex_input_columns": 712, "equivalent_real_input_columns": 1424,
            "dirty_helper_columns": 480, "all_helpers_restored": True,
            "private_centres_cleared": True}


def primitive_stream(stream, gauges):
    for h, (a, odd) in sorted(gauges.items()):
        yield from boundary_word(a, odd, ("L", h))[0]
    for event in stream:
        if event[0] != "scalar":
            continue
        g = event[1]
        if g[0] == "add":
            yield from lower_gaussian((Q(*g[3]), Q(*g[4])), tuple(g[1]), tuple(g[2]))
        else:
            for channel in range(2):
                target = tuple(g[1]) + (channel,)
                if g[0] == "scale":
                    require(g[3] == [0, 1], "real original SCALE")
                    op = ["scale", target, *g[2]]
                elif g[0] == "copy":
                    op = ["copy", target, tuple(g[2]) + (channel,)]
                else:
                    require(g[0] == "clear", "primitive opcode")
                    op = ["clear", target]
                yield from real_lowerer()(op, work=("W", channel))
    for h, (a, odd) in reversed(sorted(gauges.items())):
        yield from boundary_word(a, odd, ("L", h))[1]


def invoice(stream, gauges):
    env = {("L", i, channel): Q(1) for i in range(704) for channel in range(2)}
    env.update({("C", i, channel): Q(1) for i in range(8) for channel in range(2)})
    env.update({("W", channel): Q(1) for channel in range(2)})
    peak, count = Q(1), 0
    digest = hashlib.sha256()
    for g in primitive_stream(stream, gauges):
        count += 1
        digest.update(canonical(g) + b"\n")
        tag, target = g[:2]
        if tag in ("add", "subtract"):
            env[target] += env[g[2]]
        elif tag == "copy":
            env[target] = env[g[2]]
        elif tag == "clear":
            env[target] = Q(0)
        elif tag == "double":
            env[target] *= 2
        elif tag == "halve":
            env[target] /= 2
        else:
            require(tag == "negate", "invoice primitive")
        peak = max(peak, env[target])
    require(env["W", 0] == env["W", 1] == 0, "coefficient work cleared")
    require(peak < 2 ** 192, "inherited 192-bit local envelope")
    paid = Counter()
    for e in stream:
        if e[0] == "climb":
            paid[e[5]] += 1
        elif e[0] == "center":
            paid[e[4]] += 1
    return {"complex_scalar_primitives": count, "primitive_stream_sha256": digest.hexdigest(),
            "positive_prefix_l1": str(peak),
            "positive_prefix_bits": peak.numerator.bit_length() - peak.denominator.bit_length() + 1,
            "inherited_charged_bits": 192, "paid_profile": dict(sorted(paid.items()))}
