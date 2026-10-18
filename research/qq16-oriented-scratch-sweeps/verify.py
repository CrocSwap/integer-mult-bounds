#!/usr/bin/env python3
"""Exact orientation optimum for pinned QQ16 scratch sweeps. Apache-2.0.

David Sanders, with substantial OpenAI Codex assistance. No predecessor code
is imported. The dirty bridge and source word are credited to PR2722/2709.
"""

import gzip
import hashlib
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE_SHA = "5854aae388d1f11d201b8a02db92dd9b688827dc24280f753c3dc5db069704c5"
SOURCE_BLOB = "90cd824dbb7cd3d37e519fc1e188e3c944c41119"
WINDOWS = ((633, 1066, "L2"), (1172, 2125, "F0_inverse"))


def require(value, message):
    if not value:
        raise ValueError(message)


def load_word():
    archive = HERE / "source-word.json.gz"
    require(archive.stat().st_size <= 256_000, "compressed source bound")
    with gzip.open(archive, "rb") as stream:
        raw = stream.read(256_001)
    require(len(raw) == 202_523, "source length")
    require(hashlib.sha256(raw).hexdigest() == SOURCE_SHA, "source SHA256")
    header = b"blob " + str(len(raw)).encode() + b"\0"
    require(hashlib.sha1(header + raw).hexdigest() == SOURCE_BLOB, "source Git blob")
    word = json.loads(raw)
    require(type(word) is list and len(word) == 2415, "source word extent")
    return word


def roles(event):
    if event["op"] == "clear":
        return (event["field"],)
    require(event["op"] == "add", "pointwise scalar event")
    require(event["src"] != event["dst"], "nonaliasing ADD")
    require(event["coefficient"] in ("1", "-1", "1/4", "-1/4"), "dyadic ADD")
    return (event["src"], event["dst"])


def location(role):
    require(type(role) is str and 2 <= len(role) <= 4, "field name")
    require(role[0] in "ZW" and role[1:].isdigit(), "owned Z/W field")
    bank = int(role[1:])
    require(0 <= bank < 112 and role == role[0] + str(bank), "canonical bank")
    return "ZW".index(role[0]), bank


def extract(word, start, end, name):
    begin, finish = word[start], word[end]
    require(begin["op"] == "output_slices_begin", "begin marker")
    require(finish["op"] == "output_slices_end", "end marker")
    require(begin["name"] == finish["name"] == name, "window name")
    fields = [f"W{i}" for i in range(1 if name == "L2" else 16)]
    require(begin["fields"] == finish["fields"] == fields, "slice contract")
    body = word[start + 1:end]
    for event in body:
        for role in roles(event):
            tape, _ = location(role)
            require(tape != 1 or role in fields, "active scratch bank")
    return body


def bridge(body):
    """Apply PR2722's credited four-ADD dirty bridge; no new scalar identity."""
    result, count = [], 0
    for event in body:
        rr = roles(event)
        if len(rr) == 2 and rr[0][0] == rr[1][0]:
            src, dst = rr
            require(src[0] == "W" and event["coefficient"] == "-1", "W subtraction")
            require((int(dst[1:]), int(src[1:])) == (count, count + 8), "bridge order")
            for a, b, c in ((src, "Z0", "1"), ("Z0", dst, "-1"),
                            (src, "Z0", "-1"), ("Z0", dst, "1")):
                result.append({"op": "add", "src": a, "dst": b, "coefficient": c})
            count += 1
        else:
            result.append(dict(event))
    for event in result:
        rr = roles(event)
        require(len({r[0] for r in rr}) == len(rr), "one bank per tape per event")
    return result, count


def optimize(body, sites=2):
    """Bellman recurrence on the two previous sweep endpoints (four states)."""
    require(type(sites) is int and sites >= 1, "positive integer sites")
    banks = [0, 0]
    states = {(0, 0): (0, "")}
    digest = hashlib.sha256()
    for event in body:
        touched = [location(role) for role in roles(event)]
        require(len({t for t, _ in touched}) == len(touched), "cross-tape sweep")
        following = {}
        for state, (cost, path) in sorted(states.items()):
            for start in (0, 1):
                endpoint, extra = list(state), 0
                for tape, bank in touched:
                    gap = (bank - banks[tape]) * sites
                    gap += (start - state[tape]) * (sites - 1)
                    extra += abs(gap) + sites - 1
                    endpoint[tape] = 1 - start
                key, candidate = tuple(endpoint), (cost + extra, path + str(start))
                if key not in following or candidate < following[key]:
                    following[key] = candidate
        states = following
        require(1 <= len(states) <= 4, "four endpoint states")
        for tape, bank in touched:
            banks[tape] = bank
        layer = [[list(s), c] for s, (c, _) in sorted(states.items())]
        digest.update(json.dumps(layer, separators=(",", ":")).encode() + b"\n")
    endings = []
    for state, (cost, path) in states.items():
        home = sum(bank * sites + bit * (sites - 1) for bank, bit in zip(banks, state))
        endings.append((cost + home, path))
    cost, path = min(endings)
    return cost, path, digest.hexdigest()


def walk(body, directions, sites, literal=True, close=True):
    """Separate physical interpreter: visit actual scalar addresses in order."""
    require(type(sites) is int and sites >= 1, "walk site count")
    require(not literal or sites <= 64, "literal walk bound")
    require(len(directions) == len(body) and set(directions) <= {"0", "1"}, "directions")
    heads, distance = [0, 0], 0
    for event, direction in zip(body, directions):
        indices = range(sites) if direction == "0" else range(sites - 1, -1, -1)
        touched = [location(role) for role in roles(event)]
        if literal:
            for site in indices:
                for tape, bank in touched:
                    address = bank * sites + site
                    distance += abs(address - heads[tape])
                    heads[tape] = address
        else:
            first, last = (0, sites - 1) if direction == "0" else (sites - 1, 0)
            for tape, bank in touched:
                distance += abs(bank * sites + first - heads[tape]) + sites - 1
                heads[tape] = bank * sites + last
    return distance + (sum(heads) if close else 0)


def execute(body, directions, sites, wrong_site=False):
    require(1 <= sites <= 5, "semantic fixture bound")
    rows = {f"{t}{b}": [Fraction((b + 3) ** 2 * (s + 1) + offset, 8)
                          for s in range(sites)]
            for t, offset in (("Z", 0), ("W", 10001)) for b in range(112)}
    for event, direction in zip(body, directions):
        indices = range(sites) if direction == "0" else range(sites - 1, -1, -1)
        for site in indices:
            if event["op"] == "clear":
                rows[event["field"]][site] = Fraction(0)
            else:
                source_site = (site + 1) % sites if wrong_site else site
                rows[event["dst"]][site] += (Fraction(event["coefficient"])
                                            * rows[event["src"]][source_site])
    return rows


def certify(word):
    receipt = {"schema_version": 1, "source_sha256": SOURCE_SHA, "windows": {}}
    counts = Counter(str(abs(Fraction(e["coefficient"])))
                     for e in word if e["op"] == "add")
    clears = sum(e["op"] == "clear" for e in word)
    require(counts == {"1": 840, "1/4": 832} and clears == 288,
            "inherited complete scalar invoice")
    for start, end, name in WINDOWS:
        original = extract(word, start, end, name)
        body, count = bridge(original)
        require(count == (0 if name == "L2" else 8), "eight inherited bridges")
        base = walk(body, "0" * len(body), 1)
        best, directions, layers = optimize(body)
        slope, constant = best - base, 2 * base - best
        expected = (3518, -850) if name == "L2" else (8222, -1864)
        require((slope, constant) == expected, "orientation optimum")
        forward2 = walk(body, "0" * len(body), 2)
        forward = [forward2 - base, 2 * base - forward2]
        require(forward == ([3564, -896] if name == "L2" else [8302, -1944]),
                "independent fixed-forward tariff replay")
        for sites in (*range(1, 17), 32, 64):
            require(walk(body, directions, sites) == slope * sites + constant,
                    "literal orientation witness")
            require(optimize(body, sites)[0] == slope * sites + constant,
                    "DP agrees at varied site counts")
        huge = 10 ** 30
        require(walk(body, directions, huge, literal=False) == slope * huge + constant,
                "large exact endpoint arithmetic")
        for sites in (2, 3, 5):
            reference = execute(original, "0" * len(original), sites)
            require(execute(body, directions, sites) == reference, "all dirty cells agree")
        require(walk(body, directions, 3, close=False) < slope * 3 + constant,
                "missing head return changes bill")
        require(execute(body, directions, 3, wrong_site=True)
                != execute(original, "0" * len(original), 3), "wrong-site reads detected")
        receipt["windows"][name] = {
            "instructions": len(body), "bridges_inherited": count,
            "optimal_travel": [slope, constant], "fixed_forward_travel": forward,
            "directions": directions, "bellman_n2_layer_sha256": layers,
        }
    receipt["total_optimal_travel"] = [11740, -2714]
    receipt["total_forward_travel"] = [11866, -2840]
    receipt["saving"] = "126*(N-1)"
    receipt["unchanged_complete_scalar_counts"] = {
        "unit_adds": counts["1"] + 24, "quarter_adds": counts["1/4"], "clears": clears}
    # Inherited QQ16 scalar prices; no bit-level arithmetic implementation claim.
    receipt["unchanged_complete_scalar_allowance"] = (
        8 * (counts["1"] + 24) + 12 * counts["1/4"] + 2 * clears)
    return receipt


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def main():
    result = certify(load_word())
    expected = json.loads((HERE / "RESULT.json").read_text())
    require(canonical(result) == canonical(expected), "committed receipt differs")
    print("PASS_QQ16_ORIENTED_SCRATCH_SWEEPS travel=11740*N-2714 "
          "saving=126*(N-1) orientation_only no_new_kappa")


if __name__ == "__main__":
    main()
