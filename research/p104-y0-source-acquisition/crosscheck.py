#!/usr/bin/env python3
"""Independent dense integer / binary-elimination replay of the published word.

No imports from build.py, verify.py or predecessor executables.
Prepared for commdata2338, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent


def check(condition, message):
    if not condition:
        raise ValueError(message)


def reduce_vector(v, basis):
    for b in basis:
        v = min(v, v ^ b)
    return v


def echelon(generators):
    pivots = {}
    for v in generators:
        while v:
            bit = v.bit_length() - 1
            if bit in pivots:
                v ^= pivots[bit]
            else:
                pivots[bit] = v
                break
    for bit in sorted(pivots):
        for higher in pivots:
            if higher > bit and (pivots[higher] >> bit) & 1:
                pivots[higher] ^= pivots[bit]
    return tuple(pivots[b] for b in sorted(pivots, reverse=True))


def contained(a, b):
    return all(reduce_vector(v, b) == 0 for v in a)


def roots(fixture):
    lines = set()
    for positions in combinations(range(8), 2):
        for signs in product((-2, 2), repeat=2):
            r = [0] * 8
            for j, v in zip(positions, signs):
                r[j] = v
            if next(v for v in r if v) < 0:
                r = [-v for v in r]
            lines.add(tuple(r))
    for r in product((-1, 1), repeat=8):
        if sum(v < 0 for v in r) % 2 == 0:
            lines.add(r if r[0] > 0 else tuple(-v for v in r))
    data = fixture["section4_explicit_P104"]
    return sorted(lines - {tuple(r) for r in data["F0"] + data["C"]})


def main():
    source = {}
    for pin in json.loads((HERE / "SOURCES.json").read_text())["files"]:
        if pin["usage"] == "input":
            raw = (ROOT / pin["path"]).read_bytes()
            check(sha256(raw).hexdigest() == pin["sha256"], "input hash")
            source[Path(pin["path"]).name] = json.loads(raw)
    word, fixture = source["LOWRANK-WITNESS.json"], source["P104-FIXTURE.json"]
    candidate = json.loads((HERE / "CIRCUIT.json").read_text())
    check([b["completed_cut"] for b in candidate["insertions"]] == [0, 3467], "cut indices")
    events = (candidate["insertions"][0]["events"] + word["program"][:3467]
              + candidate["insertions"][1]["events"] + word["program"][3467:])
    initial = dict(word["initial_frames"], **candidate["initial_frames"])
    names = sorted(initial)
    columns = {r: j for j, r in enumerate(names)}
    rows = {r: [8 * int(j == columns[r]) for j in range(len(names))] for r in names}
    frames = {r: echelon(b) for r, b in initial.items()}
    histories = {r: [frames[r]] for r in names if r.startswith(("X", "Y"))}
    for e in events:
        kind = e[0]
        if kind == "add":
            _, dst, src, c, b = e
            check(frames[dst] == frames[src] == echelon(b), "ADD chart")
            c = Fraction(c)
            products = [c.numerator * v for v in rows[src]]
            check(all(v % c.denominator == 0 for v in products), "denominator-eight invariant")
            rows[dst] = [u + v // c.denominator for u, v in zip(rows[dst], products)]
        elif kind == "transport":
            _, r, before, after, rank = e
            a, b = echelon(before), echelon(after)
            check(frames[r] == a, "transport entrance")
            check(a != b and (contained(a, b) or contained(b, a)), "nested transport")
            check(abs(len(a) - len(b)) == rank, "rank charge")
            frames[r] = b
            if r in histories:
                check(contained(a, b), "data path descent")
                histories[r].append(b)
        elif kind == "zero":
            check(e[1] == "C" and e[1] not in rows, "private allocation")
            rows[e[1]], frames[e[1]] = [0] * len(names), echelon(e[2])
        elif kind == "copy":
            check(not any(rows[e[1]]) and frames[e[1]] == frames[e[2]] == echelon(e[3]), "private copy")
            rows[e[1]] = rows[e[2]][:]
        elif kind == "erase":
            check(e[1] == "C" and frames[e[1]] == echelon(e[2]), "private discard")
            del rows[e[1]], frames[e[1]]
        else:
            raise ValueError("unknown event")
    final = dict(word["final_frames"], **candidate["final_frames"])
    check(frames == {r: echelon(b) for r, b in final.items()}, "final frames")
    ports = roots(fixture)
    check(len(ports) == 104 and len(names) == 328 and len(events) == 4442, "finite dimensions")
    for r in names:
        expected = [8 * int(j == columns[r]) for j in range(len(names))]
        if r.startswith("Y"):
            t = int(r[1:])
            for s in range(104):
                expected[columns[f"X{s}"]] = (8 * int(s == 0) if t == 0 else
                                               sum(x * y for x, y in zip(ports[t], ports[s])))
        check(rows[r] == expected, "dense endpoint " + r)
    h = histories["Y0"][-1]
    support = [s for s in range(104)
               if 8 * int(s == 0) != sum(x * y for x, y in zip(ports[0], ports[s]))]
    lines = set()
    for s in support:
        path = histories[f"X{s}"]
        check(len(path[0]) == 1 and contained(path[0], h), "initial source line")
        check(all(not contained(f, h) for f in path[1:]), "expanded source in H")
        check(path[0] not in histories["Y0"], "direct source access")
        lines.add(path[0])
    check(len(lines) == len(support) == 48, "48 distinct acquisition lines")
    canonical = {r: {names[j]: str(Fraction(v, 8)) for j, v in enumerate(rows[r]) if v}
                 for r in names}
    digest = sha256(json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    check(digest == json.loads((HERE / "RESULT.json").read_text())["full_endpoint_sha256"], "cross-check digest")
    print("PASS_P104_Y0_DENSE_CROSSCHECK events=4442 columns=328 acquisition_lines=48 exact_scale=8")


if __name__ == "__main__":
    main()
