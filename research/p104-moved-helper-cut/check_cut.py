# SPDX-License-Identifier: Apache-2.0
"""Second cut check: binary elimination and reverse scalar sensitivity.

No imports from verify.py or any predecessor package. The interval-contact
lemma is credited to the PR2996 lineage. Prepared for commdata2338 with
substantial OpenAI Codex assistance; not a formal-kernel proof.
"""
import hashlib
import json
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def check(condition, message):
    if not condition:
        raise ValueError(message)


def reduced(rows):
    pivots = {}
    for value in rows:
        for bit in sorted(pivots, reverse=True):
            if value >> bit & 1:
                value ^= pivots[bit]
        if value:
            bit = value.bit_length() - 1
            for other in list(pivots):
                if pivots[other] >> bit & 1:
                    pivots[other] ^= value
            pivots[bit] = value
    return tuple(pivots[k] for k in sorted(pivots, reverse=True))


def contains(large, small):
    return len(reduced((*large, *small))) == len(large)


def hyperplane(rows, functional):
    odd = [v for v in rows if (v & functional).bit_count() & 1]
    check(odd, "nonconstant hyperplane functional")
    pivot = odd[0]
    return reduced(v ^ pivot if (v & functional).bit_count() & 1 else v
                   for v in rows if v != pivot)


def possible_contact(left, right, dimension):
    a, b = left
    c, d = right
    joined_low = reduced((*a, *c))
    intersection_dimension = len(b) + len(d) - len(reduced((*b, *d)))
    return (len(joined_low) <= dimension <= intersection_dimension
            and contains(b, joined_low) and contains(d, joined_low))


def fits(bounds, frame, dimension):
    low, high = bounds
    return len(frame) == dimension and contains(frame, low) and contains(high, frame)


def load():
    result = {}
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    for record in manifest["files"]:
        if record["usage"] == "input":
            raw = (ROOT / record["path"]).read_bytes()
            check(hashlib.sha256(raw).hexdigest() == record["sha256"], "source digest")
            result[Path(record["path"]).name] = json.loads(raw)
    return result


def target_row(word, target=40):
    """Reverse-mode scalar pullback of one complete logical target row."""
    weights = defaultdict(Fraction, {f"Y{target}": Fraction(1)})
    copies = 0
    for event in reversed(word["program"]):
        op, name = event[:2]
        if op == "add":
            weights[event[2]] += Fraction(event[3]) * weights[name]
        elif op == "copy":
            weights[event[2]] += weights[name]
            weights[name] = Fraction(0)
            copies += 1
        elif op in ("erase", "zero"):
            weights[name] = Fraction(0)
        else:
            check(op == "transport", "known logical opcode")
    check(copies == 8, "all private lifetimes pulled back")
    for name in word["initial_frames"]:
        if not name.startswith("X"):
            check(weights[name] == int(name == f"Y{target}"), "target entrance/dirt response")
    return [Fraction(int(s == target)) - weights[f"X{s}"] for s in range(104)]


def derive(inputs):
    word = inputs["LOWRANK-WITNESS.json"]
    paths = {f"{kind}{i}": [reduced(word["initial_frames"][f"{kind}{i}"])]
             for kind in "XY" for i in range(104)}
    for event in word["program"]:
        if event[0] == "transport" and event[1] in paths:
            chain = paths[event[1]]
            before, after = reduced(event[2]), reduced(event[3])
            check(chain[-1] == before and contains(after, before), "data path continuity")
            chain.append(after)
    for name, chain in paths.items():
        check(chain[-1] == reduced(word["final_frames"][name]), "final data frame")
    forms = inputs["CERTIFICATE.json"]["forms"]
    pairing = inputs["WITNESS.json"]["pairing"]
    check(sorted(pairing) == list(range(208)), "perfect matching")
    previous = inputs["CONTROL.json"]["pairing"]
    reconstructed = list(previous)
    cycle = [13, 203, 191, 63]
    for i, h in enumerate(cycle):
        reconstructed[h] = previous[cycle[(i + 1) % 4]]
    check(pairing == reconstructed, "oriented cycle binding")
    lows = [reduced((*paths[f"X{i}"][0], form)) for i in range(104)
            for form in forms["departure"][i]]
    highs = [hyperplane(paths[f"Y{i}"][-1], form) for i in range(104)
             for form in forms["arrival"][i]]
    check(all(len(a) == 2 for a in lows) and all(len(b) == 7 for b in highs), "endpoint ranks")
    check(all(contains(highs[pairing[h]], lows[h]) for h in range(208)), "endpoint inclusion")

    def interval(h, dimension):
        if dimension == 1:
            fixed = paths[f"X{h // 2}"][0]
            return fixed, fixed
        if dimension == 8:
            fixed = paths[f"Y{pairing[h] // 2}"][-1]
            return fixed, fixed
        return lows[h], highs[pairing[h]]

    contacts, reads, writes = {}, {}, {}
    for h in (13, 17, 83, 91):
        contacts[str(h)], reads[str(h)], writes[str(h)] = [], [], []
        for d in range(1, 9):
            bounds = interval(h, d)
            contacts[str(h)].append([k for k in range(208) if k != h
                                     and possible_contact(bounds, interval(k, d), d)])
            reads[str(h)].append([s for s in range(104)
                                  if any(fits(bounds, f, d) for f in paths[f"X{s}"])])
            writes[str(h)].append([t for t in range(104)
                                   if any(fits(bounds, f, d) for f in paths[f"Y{t}"])])
        check(contacts[str(h)][0] == [h ^ 1], "one source-line partner")
        partner_bounds = interval(h ^ 1, 1)
        partner_reads = [s for s in range(104) if any(fits(partner_bounds, f, 1) for f in paths[f"X{s}"])]
        check(partner_reads == [h // 2], "partner has only the same source")
    writers = [[d, h] for d in range(1, 9) for h in range(208)
               if any(fits(interval(h, d), f, d) for f in paths["Y40"])]
    check(not any(set(paths[f"X{s}"]) & set(paths["Y40"]) for s in range(104)), "no direct read")
    check(pairing[91] == 8, "outgoing arrival boundary")
    for h, vector in ((63, 31), (118, 178), (185, 253)):
        check(contains(lows[h], (vector,)) and not contains(highs[8], (vector,)), "separator")
    row = target_row(word)
    support = {6, 8, 41, 45}
    missing = [s for s in range(104) if row[s] and s not in support]
    check(row[1] == Fraction(1, 2) and len(missing) == 44, "required coefficients")
    return {"complete_contacts_by_dimension": contacts, "local_reads_by_dimension": reads,
            "local_writes_by_dimension": writes, "all_target_writers": writers,
            "required_coefficient": str(row[1]), "missing_required_sources": missing}


def main():
    actual = derive(load())
    cut = json.loads((HERE / "RESULT.json").read_text())["cut"]
    expected = {key: cut[key] for key in actual}
    check(json.dumps(actual, sort_keys=True) == json.dumps(expected, sort_keys=True),
          "independent cut receipt equality")
    print("PASS_P104_MOVED_HELPER_ALGEBRAIC_CUT contacts=independent row=reverse_pullback missing=44")


if __name__ == "__main__":
    main()
