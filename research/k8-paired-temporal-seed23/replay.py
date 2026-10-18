"""Selected-provider scalar checks, adapted from Sagar Thakrar's PR1259.

Sagar Thakrar with substantial OpenAI Codex assistance, Apache-2.0.
Retains the icekylinx/Jeremy Kothe supplier and PR696 lowerer semantics.
"""
from collections import Counter
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path
import runpy
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SEARCH = runpy.run_path(str(HERE / "search.py"))
require = SEARCH["require"]
OLD = "research/community-frontier1042-audit/"
NEW = "research/community-frontier1094-audit/"
LOWER = "research/complex-dyadic-lowering/lower.py"
FILES = {OLD + "selected-replay.tar.gz", NEW + "selected-replay.tar.gz",
         OLD + "RESULT.json", NEW + "RESULT.json", LOWER}
MEMBERS = {"CANONICAL-WORD.json.gz", "LOCAL-PROGRAMS.json.gz", "INDEPENDENT-LOCAL-REPLAY.json"}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def load(root=ROOT, manifest=None):
    m = manifest if manifest is not None else json.loads((HERE / "SOURCES.json").read_bytes())
    require(m["base"] == "bce54fb3f895cbe5cd4c0eb477c3afeed100190f" and m["seed"] == 23, "assignment pin")
    require(set(m["files"]) == FILES and set(m["archive_members"]) == MEMBERS, "complete source inventory")
    for path, pin in m["files"].items():
        require(digest((root / path).read_bytes()) == pin, "source pin " + path)
    result = {}
    with tarfile.open(root / (OLD + "selected-replay.tar.gz")) as old, tarfile.open(root / (NEW + "selected-replay.tar.gz")) as new:
        for name in sorted(MEMBERS):
            raw = old.extractfile("slots/local/" + name).read()
            require(digest(raw) == m["archive_members"][name], "archive member " + name)
            actual = new.extractfile("candidate/strict/global8/base/providers/gauge44/" + name).read()
            require(raw == actual, "selected provider alias " + name)
            result[name] = json.loads(gzip.decompress(raw) if name.endswith(".gz") else raw)
    old = json.loads((root / (OLD + "RESULT.json")).read_bytes())
    new = json.loads((root / (NEW + "RESULT.json")).read_bytes())
    require(old["status"] == "PASS_COMPLETE_PR1042_COMPOSITION" and new["status"] == "PASS_COMPLETE_PR1094_COMPOSITION", "receipt status")
    require(new["baseline_receipt_sha256"] == m["files"][OLD + "RESULT.json"], "selected baseline binding")
    word = result["CANONICAL-WORD.json.gz"]
    require((word["v"], word["h"], word["R"]) == (112, 9, 480), "source geometry")
    return word, result["LOCAL-PROGRAMS.json.gz"], result["INDEPENDENT-LOCAL-REPLAY.json"], runpy.run_path(str(root / LOWER))["lower"]


def apply(g, rows):
    tag, t = g[0], tuple(g[1])
    if tag == "clear":
        rows[t] = {}
    elif tag == "copy":
        rows[t] = dict(rows[tuple(g[2])])
    elif tag in ("scale", "double", "halve", "negate"):
        q = Q(g[2], g[3]) if tag == "scale" else {"double": Q(2), "halve": Q(1, 2), "negate": Q(-1)}[tag]
        rows[t] = {i: q * a for i, a in rows[t].items()}
    else:
        require(tag in ("add", "subtract"), "scalar opcode")
        s = tuple(g[2])
        require(s != t, "distinct ADD operands")
        q = Q(g[3], g[4]) if len(g) == 5 else Q(1 if tag == "add" else -1)
        for i, a in rows[s].items():
            v = rows[t].get(i, Q(0)) + q * a
            if v:
                rows[t][i] = v
            else:
                rows[t].pop(i, None)


def replay(events, orientation):
    rows = {("L", i): {i: Q(1)} for i in range(704)}
    rows.update({("C", i): {704 + i: Q(1)} for i in range(8)})
    for e in events:
        if e[0] == "scalar":
            apply(e[1], rows)
    for i in range(704):
        expected = {i: Q(1)}
        if orientation == "forward" and 112 <= i < 224:
            expected[i - 112] = Q(1)
        if orientation == "backward" and i < 112:
            expected[i + 112] = Q(-1)
        require(rows["L", i] == expected, "all-column endpoint " + str((orientation, i)))
    require(all(not rows["C", i] for i in range(8)), "private centers cleared")


def frame_check(events, word, pair):
    frames = {h: word["start"][h] for h in pair}
    for e in events:
        if e[0] == "climb" and e[2] in pair:
            require(frames[e[2]] == e[3], "helper climb incidence")
            frames[e[2]] = e[4]
        elif e[0] == "scalar":
            for h in pair:
                if ["L", h] in e[1]:
                    require(frames[h] == e[2], "helper scalar frame")
                    require(e[1][0] in ("add", "scale"), "helper COPY/CLEAR excluded")
        elif e[0] == "residual_adapter":
            require(e[2] not in pair, "helper wrapper excluded")
    require(all(frames[h] == word["final"][h] for h in pair), "helper final frame")


def invoice(events, lower):
    env = {("L", i): Q(1) for i in range(704)}
    env.update({("C", i): Q(1) for i in range(8)})
    env["W", 0] = Q(1)
    depths = {r: 0 for r in env}
    peak, max_depth, count = Q(1), 0, 0
    paid = Counter()
    for e in events:
        if e[0] == "climb":
            paid[e[5]] += 1
        if e[0] == "center":
            paid[e[4]] += 1
        if e[0] != "scalar":
            continue
        for g in lower(e[1]):
            count += 1
            tag, t = g[0], tuple(g[1])
            if tag == "clear":
                env[t], depths[t] = Q(0), 0
            elif tag == "copy":
                env[t], depths[t] = env[tuple(g[2])], depths[tuple(g[2])]
            elif tag == "double":
                env[t] *= 2
                depths[t] = max(0, depths[t] - 1)
            elif tag == "halve":
                env[t] /= 2
                depths[t] += 1
            elif tag in ("add", "subtract"):
                env[t] += env[tuple(g[2])]
                depths[t] = max(depths[t], depths[tuple(g[2])])
            else:
                require(tag == "negate", "primitive opcode")
            peak = max(peak, env[t])
            max_depth = max(max_depth, depths[t])
        if e[1][0] == "add":
            require(env["W", 0] == 0, "coefficient work cleared")
    bits = peak.numerator.bit_length() - peak.denominator.bit_length() + 1
    require(bits + max_depth < 192, "local signed fixed-point payload guard")
    return {"complex_primitives": 2 * count, "prefix_l1": str(peak), "prefix_bits": bits,
            "grid_depth_upper": max_depth, "paid_profile": {str(k): v for k, v in sorted(paid.items())}}


def lowerer_checks(programs, lower):
    adds, scales = set(), set()
    for events in programs:
        for e in events:
            if e[0] == "scalar" and e[1][0] == "add":
                adds.add(Q(e[1][3], e[1][4]))
            elif e[0] == "scalar" and e[1][0] == "scale":
                scales.add(Q(e[1][2], e[1][3]))
    for q in adds:
        g = ["add", ["L", 0], ["L", 1], q.numerator, q.denominator]
        rows = {("L", 0): {0: Q(1)}, ("L", 1): {1: Q(1)}, ("W", 0): {2: Q(1)}}
        for op in lower(g):
            apply(op, rows)
        require(rows == {("L", 0): {0: Q(1), 1: q}, ("L", 1): {1: Q(1)}, ("W", 0): {}}, "arbitrary-work ADD map")
        require(len(lower(g)) == SEARCH["price"](q), "literal/formula price")
    for q in scales:
        rows = {("L", 0): {0: Q(1)}}
        for op in lower(["scale", ["L", 0], q.numerator, q.denominator]):
            apply(op, rows)
        require(rows == {("L", 0): {0: q}}, "lowered SCALE map")
    return {"adds": len(adds), "scales": len(scales)}
