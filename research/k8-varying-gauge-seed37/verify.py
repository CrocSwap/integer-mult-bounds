"""Offline finite replay. Sagar Thakrar with substantial OpenAI Codex assistance.

Apache-2.0. Exact scalar semantics follow the retained icekylinx/Jeremy Kothe
lineage. PR1161 by @woklerx introduced the constant helper-gauge comparison.
"""
import argparse
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
ARCHIVE = "research/community-frontier1042-audit/selected-replay.tar.gz"
CURRENT = "research/community-frontier1094-audit/selected-replay.tar.gz"
LOWER = "research/complex-dyadic-lowering/lower.py"
MEMBERS = {"CANONICAL-WORD.json.gz", "LOCAL-PROGRAMS.json.gz",
           "INDEPENDENT-LOCAL-REPLAY.json", "LOCAL-CHECKS.json"}
FILES = {ARCHIVE, CURRENT, LOWER, "research/community-frontier1042-audit/RESULT.json",
         "research/community-frontier1094-audit/RESULT.json",
         "research/community-frontier1094-audit/ASSEMBLY.json",
         "docs/research/community-batch1099-review.md"}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def load(root=ROOT, manifest=None):
    m = manifest if manifest is not None else json.loads((HERE / "SOURCES.json").read_bytes())
    require(m["base"] == "dd6403f774a0891093a006ae9716c02e371b1fdb"
            and m["seed"] == 37, "assignment pin")
    require(set(m["files"]) == FILES and set(m["archive_members"]) == MEMBERS,
            "complete source inventory")
    for path, pin in m["files"].items():
        require(digest((root / path).read_bytes()) == pin, "source pin " + path)
    result = {}
    with tarfile.open(root / ARCHIVE) as old, tarfile.open(root / CURRENT) as new:
        for name in sorted(MEMBERS):
            raw = old.extractfile("slots/local/" + name).read()
            require(digest(raw) == m["archive_members"][name], "archive member " + name)
            actual = new.extractfile("candidate/strict/global8/base/providers/gauge44/" + name).read()
            require(raw == actual, "selected provider alias " + name)
            result[name] = json.loads(gzip.decompress(raw) if name.endswith(".gz") else raw)
    old = json.loads((root / "research/community-frontier1042-audit/RESULT.json").read_bytes())
    new = json.loads((root / "research/community-frontier1094-audit/RESULT.json").read_bytes())
    require(old["status"] == "PASS_COMPLETE_PR1042_COMPOSITION"
            and new["status"] == "PASS_COMPLETE_PR1094_COMPOSITION", "source receipt statuses")
    require(new["baseline_receipt_sha256"] == m["files"]["research/community-frontier1042-audit/RESULT.json"],
            "selected baseline receipt binding")
    assembly = json.loads((root / "research/community-frontier1094-audit/ASSEMBLY.json").read_bytes())
    require(assembly["kappa"] == m["selected_kappa_at_base"], "selected arithmetic binding")
    w = result["CANONICAL-WORD.json.gz"]
    require((w["v"], w["h"], w["R"]) == (112, 9, 480), "source geometry")
    lower = runpy.run_path(str(root / LOWER))["lower"]
    return w, result["LOCAL-PROGRAMS.json.gz"], result, lower


def independent_minimum(terms, domain, lower):
    """Two linear sweeps compute the distance transform; no optimizer costs used."""
    lo, hi = domain
    values = [abs(k) for k in range(lo, hi + 1)]
    for _, q, s in terms:
        for j in range(1, len(values)):
            values[j] = min(values[j], values[j - 1] + 1)
        for j in range(len(values) - 2, -1, -1):
            values[j] = min(values[j], values[j + 1] + 1)
        for j, k in enumerate(range(lo, hi + 1)):
            shifted = q * Q(2) ** (s * k)
            macro = ["add", ["L", 0], ["L", 1], shifted.numerator, shifted.denominator]
            original = ["add", ["L", 0], ["L", 1], q.numerator, q.denominator]
            values[j] += len(lower(macro)) - len(lower(original))
    return min(v + abs(k) for k, v in zip(range(lo, hi + 1), values))


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


def frame_check(events, word, helper):
    frame = word["start"][helper]
    scales = 0
    for e in events:
        if e[0] == "climb" and e[2] == helper:
            require(frame == e[3], "helper climb incidence")
            frame = e[4]
        elif e[0] == "scalar" and ["L", helper] in e[1]:
            require(frame == e[2], "helper scalar frame")
            require(e[1][0] in ("add", "scale"), "helper copy/clear excluded")
            scales += int(e[1][0] == "scale")
        elif e[0] == "residual_adapter":
            require(e[2] != helper, "helper wrapper excluded")
    require(frame == word["final"][helper], "helper final frame")
    return scales


def primitive_invoice(events, lower):
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
                env[t] = Q(0)
                depths[t] = 0
            elif tag == "copy":
                env[t] = env[tuple(g[2])]
                depths[t] = depths[tuple(g[2])]
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
            require(env["W", 0] == 0, "paid coefficient-work clear")
    require(peak < 2 ** 192, "local 192-bit magnitude guard")
    return {"complex_primitives": 2 * count, "prefix_l1": str(peak),
            "prefix_bits": peak.numerator.bit_length() - peak.denominator.bit_length() + 1,
            "coefficient_grid_depth_upper": max_depth,
            "paid_profile": {str(k): v for k, v in sorted(paid.items())}}


def lowerer_controls(programs, lower):
    # Check every distinct changed or unchanged coefficient on all three local inputs.
    adds, scales = set(), set()
    for events in programs:
        for e in events:
            if e[0] == "scalar":
                g = e[1]
                if g[0] == "add":
                    adds.add(Q(g[3], g[4]))
                elif g[0] == "scale":
                    scales.add(Q(g[2], g[3]))
    for q in adds:
        g = ["add", ["L", 0], ["L", 1], q.numerator, q.denominator]
        rows = {("L", 0): {0: Q(1)}, ("L", 1): {1: Q(1)}, ("W", 0): {2: Q(1)}}
        for op in lower(g):
            apply(op, rows)
        require(rows == {("L", 0): {0: Q(1), 1: q}, ("L", 1): {1: Q(1)}, ("W", 0): {}},
                "lowered arbitrary-work ADD map")
        require(len(lower(g)) == SEARCH["price"](q), "literal vs formula price")
    for q in scales:
        rows = {("L", 0): {0: Q(1)}}
        for op in lower(["scale", ["L", 0], q.numerator, q.denominator]):
            apply(op, rows)
        require(rows == {("L", 0): {0: q}}, "lowered SCALE map")
    return {"add_coefficients": len(adds), "scale_coefficients": len(scales)}


def compute():
    word, programs, source, lower = load()
    helpers = SEARCH["eligible"](word, programs)
    require(len(helpers) == 237, "eligible helper inventory")
    helpers = helpers[37:53]
    result = {"base": "dd6403f774a0891093a006ae9716c02e371b1fdb", "seed": 37,
              "helpers": helpers, "formal_columns": 712, "orientations": {}}
    all_programs = []
    for orientation in ("forward", "backward"):
        events = programs[orientation]
        census = []
        for h in helpers:
            terms = SEARCH["incident"](events, h)
            row = SEARCH["optimize"](terms)
            independent = independent_minimum(terms, row["domain"], lower)
            require(independent == row["delta_real"], "independent shortest-path minimum")
            census.append({"helper": h, **row})
        winner = min(census, key=lambda r: (r["delta_real"], r["helper"]))
        h = winner["helper"]
        candidate = SEARCH["transform"](events, word, h, winner["schedule"])
        require([e for e in events if e[0] != "scalar"] == [e for e in candidate if e[0] != "scalar"],
                "nonscalar event stream unchanged")
        require(frame_check(candidate, word, h) - frame_check(events, word, h) == winner["scale_macros"],
                "inserted scale count")
        replay(events, orientation)
        replay(candidate, orientation)
        before, after = primitive_invoice(events, lower), primitive_invoice(candidate, lower)
        require(after["complex_primitives"] - before["complex_primitives"] == 2 * winner["delta_real"],
                "whole-word primitive saving")
        require(before["paid_profile"] == after["paid_profile"] == source["INDEPENDENT-LOCAL-REPLAY.json"]["paid_profiles"][orientation],
                "source-bound paid profile")
        require(before["prefix_l1"] == source["INDEPENDENT-LOCAL-REPLAY.json"]["local"][orientation]["prefix_l1_upper"],
                "source-bound prefix envelope")
        result["orientations"][orientation] = {
            "census": [{k: v for k, v in r.items() if k != "schedule"} for r in census],
            "winner": winner, "before": before, "after": after,
            "candidate_sha256": digest(canonical(candidate)), "events": len(candidate)}
        all_programs.extend([events, candidate])
    result["lowerer_checks"] = lowerer_controls(all_programs, lower)
    result["status"] = "PASS_K8_VARYING_GAUGE_16_HELPERS_NO_NEW_KAPPA"
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = compute()
    require(canonical(result) == canonical(json.loads((HERE / "CERTIFICATE.json").read_bytes())),
            "saved certificate mismatch")
    controls = runpy.run_path(str(HERE / "controls.py"))["run"]()
    print(json.dumps(result, indent=2) if args.json else
          result["status"] + " helper=276 saved=344/344 columns=712 orientations=2"
          + " controls=" + str(len(controls["rejected"])))
