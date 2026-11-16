"""Independent order, integer-grid and chart audit. Apache-2.0, OpenAI Codex assisted."""
from collections import Counter, defaultdict
from copy import deepcopy
from fractions import Fraction as Q
import gzip
from hashlib import sha256
import importlib.util
import json
from math import gcd, lcm
from pathlib import Path
import sys

INPUTS = Path(__file__).resolve().parent
PKG = INPUTS.parent / "shared-wire-split-composition"
if not __debug__:
    raise RuntimeError("Run without -O; assertions are proof checks.")


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if raw.startswith(b"\x1f\x8b") else raw)


def digest(word):
    return sha256(json.dumps(word, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def touched(e):
    return set(e[1:3] if e[0] in ("ADD", "COPY") else e[1:2])


def build(old, edit):
    seq = old["program"]
    insert, remove, repl, moved = defaultdict(list), set(), {}, set()
    for p in edit["plans"]:
        r = p["role"]
        a, b = (m["index"] for m in p["old_moves"])
        first, last = seq[a], seq[b]
        assert [first, last] == [m["event"] for m in p["old_moves"]]
        assert 0 <= a < b and r < old["public"] and first[3] == last[2]
        assert first[:2] == last[:2] == ["MOVE", r] and not first[4] and not last[4]
        assert {i for i in range(a + 1, b) if r in touched(seq[i])} == {s["index"] for s in p["slides"]}
        repl[a] = ["MOVE", r, first[2], last[3], False]
        remove.add(b)
        for s in p["slides"]:
            i, k, chart = s["index"], s["before_event"], s["new_frame"]
            assert seq[i] == s["event"] and seq[i][0] == "ADD" and seq[i][-1] == first[3]
            assert i not in moved
            assert (k <= a and chart == first[2]) or (k > b and chart == last[3])
            insert[k].append((i, [*seq[i][:-1], chart]))
            moved.add(i)
    tagged = []
    for i in range(len(seq) + 1):
        tagged.extend(sorted(insert[i]))
        if i < len(seq) and i not in remove and i not in moved:
            tagged.append((i, repl.get(i, seq[i])))
    loc = {j: i for i, (j, _) in enumerate(tagged)}
    assert len(loc) == len(tagged) == len(seq) - 5
    crossings, version_checks = Counter(), set(moved)
    for i in moved:
        a, b = seq[i][1:3]
        for j in loc:
            if (i < j) == (loc[i] < loc[j]):
                continue
            other = seq[j]
            crossings["all"] += 1
            if not touched(seq[i]) & touched(other):
                continue
            op = other[0]
            crossings[op] += 1
            if op == "MOVE":
                continue
            # E_ab E_cd = E_cd E_ab = 0 is sufficient for arbitrary values.
            assert op == "ADD" and b != other[1] and other[2] != a, (i, j)
            version_checks.add(j)
    return tagged, crossings, version_checks


def subspace(basis):
    span = {0}
    for v in basis:
        assert v not in span and 0 < v < 512
        span |= {x ^ v for x in span}
    return span


def replay(word, tagged, checked, grid=1125):
    n, m, unit = word["public"], word["owned_fields"], 2**24
    span = [subspace(f) for f in word["frames"]]
    frames = word["initial"] + [None] * m
    rows = [{r: grid * unit} for r in range(n)] + [{} for _ in range(m)]
    live, versions, clear, copy = {}, {}, {}, {}
    lifetimes, owned_moves = [], []
    paid, up, ops, odd = Counter(), Counter(), Counter(), Counter()
    peak, max_mass, odd_lcm, high = 0, grid * unit, 1, 0

    def measure(row):
        nonlocal max_mass, odd_lcm, high
        max_mass = max(max_mass, sum(abs(x) for x in row.values()))
        for value in row.values():
            odd_lcm = lcm(odd_lcm, grid // gcd(grid, value))
            high = max(high, 25 - (abs(value) & -abs(value)).bit_length())

    for origin, e in tagged:
        op, r = e[:2]
        ops[op] += 1
        if op == "INIT":
            assert r >= n and frames[r] is None and r not in live
            live[r] = origin
            frames[r], rows[r] = e[2], {}
            peak = max(peak, len(live))
        elif op == "CLEAR":
            assert r in live and frames[r] == e[2]
            clear[origin] = tuple(sorted(rows[r].items()))
            lifetimes.append((live.pop(r), origin, r))
            frames[r], rows[r] = None, {}
        elif op == "MOVE":
            _, r, a, b, owned = e
            assert frames[r] == a and owned == (r >= n) and (not owned or r in live)
            assert span[a] < span[b] or (owned and span[b] < span[a])
            rank = abs(len(word["frames"][a]) - len(word["frames"][b]))
            paid[rank] += 1
            if owned:
                owned_moves.append((origin, live[r], e))
                if span[a] < span[b]:
                    up[rank] += 1
            frames[r] = b
        else:
            assert op in ("ADD", "COPY", "SCALE")
            s = r if op == "SCALE" else e[2]
            q = Q(e[-2])
            assert frames[r] is not None and frames[r] == frames[s] == e[-1] and q
            assert (r == s) == (op == "SCALE") and abs(q) + 1 < 2**16
            if origin in checked:
                versions[origin] = tuple(sorted(rows[s].items()))
            if q.denominator & (q.denominator - 1):
                odd[op] += 1
            product = {}
            for j, value in rows[s].items():
                z, rem = divmod(value * q.numerator, q.denominator)
                if rem:
                    raise ValueError(("grid", origin, q.denominator))
                if z:
                    product[j] = z
            measure(product)
            if op == "COPY":
                assert r in live and not rows[r]
                copy[origin] = tuple(sorted(product.items()))
            if op == "SCALE":
                rows[r] = product
            else:
                for j, z in product.items():
                    if v := rows[r].get(j, 0) + z:
                        rows[r][j] = v
                    else:
                        rows[r].pop(j, None)
                measure(rows[r])
    assert not live and frames == word["final"] + [None] * m
    assert all(v % grid == 0 for row in rows[:n] for v in row.values())
    return (rows, versions, clear, copy, lifetimes, owned_moves), {
        "opcodes": ops, "paid": paid, "owned_rises": up, "owned_peak": peak,
        "owned_lifetimes": len(lifetimes), "owned_rise_mass": sum(r*n for r,n in up.items()),
        "odd_divisions": odd, "odd_grid_lcm": odd_lcm,
        "dyadic_height": high, "maximum_scaled_mass": str(Q(max_mass, unit)),
    }


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec)
    sys.modules[name] = obj
    spec.loader.exec_module(obj)
    return obj


def lower(word, edit):
    c = module("stop_compiler", PKG / "frozen/clifford_exact.py")
    v = module("stop_interpreter", PKG / "frozen/native_verify.py")
    pairs = sorted({(p["old_moves"][0]["event"][2], p["old_moves"][1]["event"][3])
                    for p in edit["plans"]})
    frames = word["frames"]
    result = []
    for a, b in pairs:
        ca, cb = (c.canonical_frame(9, tuple(frames[i])) for i in (a,b))
        recipe, _ = c.lower_child(ca.adjoint().then(cb))
        expected = v.adjoint(v.frame(frames[a],9)) + v.frame(frames[b],9)
        v.equal(v.recipe(recipe), expected, "absolute phase and signed-Pauli chart")
        assert recipe["rank"] == len(frames[b]) - len(frames[a])
        result.append([a, b, recipe["rank"]])
    wrong = deepcopy(recipe)
    wrong["left"]["phase"] = (wrong["left"]["phase"] + 1) % 4
    try:
        v.equal(v.recipe(wrong), expected, "wrong absolute phase")
    except ValueError:
        pass
    else:
        raise AssertionError("Changed phase accepted")
    return result


def main():
    source = read(PKG / "data/final.json.gz")
    edit = read(INPUTS / "EDITS.json")
    candidate = read(Path(sys.argv[1]))
    assert digest(source) == edit["source_canonical_sha256"] == "91429a6b96729292a8764836e00c87a6f7cd3b76f05159033f4867f69a98d097"
    assert digest(candidate) == "d0de7804e56b2c8fe6db9d323560e53041810fd0377b91680cbed19b5176ebc0"
    tagged, crossings, checked = build(source, edit)
    assert candidate == source | {"program": [e for _, e in tagged]}
    base, a = replay(source, list(enumerate(source["program"])), checked)
    new, b = replay(source, tagged, checked)
    assert base == new, "Source versions, endpoints or owned history changed"
    delta = b["paid"].copy()
    delta.subtract(a["paid"])
    assert +delta == {2:2,5:3} and -delta == {1:7,4:3}
    assert sum(r*n for r,n in delta.items()) == 0
    assert b["owned_rise_mass"] == 56 and sum(b["owned_rises"].values()) == 23
    assert b["owned_peak"] == 43 and b["owned_lifetimes"] == 54 and b["odd_grid_lcm"] == 1125
    assert all(a[k] == b[k] for k in ("dyadic_height", "odd_divisions", "maximum_scaled_mass"))
    missing = {s["index"] for s in edit["plans"][0]["slides"]}
    assert replay(source, [(i,e) for i,e in tagged if i not in missing], checked)[0][0] != new[0]
    try:
        replay(source, tagged, checked, grid=375)
    except ValueError as err:
        rejected_grid = str(err)
    else:
        raise AssertionError("Insufficient odd scale accepted")
    print(json.dumps({
        "source_canonical_sha256": digest(source), "candidate_canonical_sha256": digest(candidate),
        "edits_sha256": sha256((INPUTS/"EDITS.json").read_bytes()).hexdigest(),
        "crossings": crossings, "exact_source_rows_compared": len(checked),
        "exact_output_rows_compared": source["public"], "exact_owned_clear_rows_compared": len(new[2]),
        "owned_move_events_and_lifetimes_identical": True,
        "base": a, "candidate": b, "local_paid_delta": {r:n for r,n in delta.items() if n},
        "complete_paid_delta": {r:18*n for r,n in delta.items() if n},
        "checked_new_chart_pairs": lower(source, edit),
        "controls": ["omitted slide changes endpoint", rejected_grid, "wrong absolute phase rejected"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
