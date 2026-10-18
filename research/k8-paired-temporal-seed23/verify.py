"""Exact bounded paired-gauge census and complete finite scalar replay.

Sagar Thakrar with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from copy import deepcopy
from fractions import Fraction as Q
from itertools import product
import json
from pathlib import Path
import runpy

HERE = Path(__file__).resolve().parent
R = runpy.run_path(str(HERE / "replay.py"))
S = R["SEARCH"]
require = R["require"]


def dense_oracle(blocks, lower):
    """Explicit 81-by-81 edges and literal macro prices; no L1 sweeps or tight-edge DAG."""
    states = list(product(range(-4, 5), repeat=2))
    lengths = [[abs(a - x) + abs(b - y) for x, y in states] for a, b in states]
    boundary = [abs(a) + abs(b) for a, b in states]
    cache = {}

    def price(q):
        if q not in cache:
            cache[q] = len(lower(["add", ["L", 0], ["L", 1], q.numerator, q.denominator]))
        return cache[q]

    joint_total, tied_total, independent_total, edges = 0, 0, 0, 0
    for block in blocks:
        joint = boundary[:]
        lex = [(d, d) for d in boundary]
        for _, q, (s, t) in block:
            joint_new, lex_new = [], []
            base = price(q)
            for n, (a, b) in enumerate(states):
                distances = lengths[n]
                c = price(q * Q(2) ** (a * s + b * t)) - base
                separate = price(q * Q(2) ** (a * s)) + price(q * Q(2) ** (b * t)) - 2 * base
                joint_new.append(min(v + d for v, d in zip(joint, distances)) + c)
                v = min((x + d, y + d) for (x, y), d in zip(lex, distances))
                lex_new.append((v[0] + separate, v[1] + c))
            joint, lex = joint_new, lex_new
            edges += len(states) ** 2
        joint_total += min(v + d for v, d in zip(joint, boundary))
        v = min((a + d, b + d) for (a, b), d in zip(lex, boundary))
        independent_total += v[0]
        tied_total += v[1]
    return joint_total, tied_total, independent_total, edges


def check_transform(original, candidate, word, pair):
    """Read the actual candidate stream and verify the diagonal invariant at every event."""
    exponent = dict.fromkeys(pair, 0)
    frames = {h: word["start"][h] for h in pair}
    j, inserted, scale_cost, add_delta, changed = 0, 0, 0, 0, 0
    for e in original:
        incident = e[0] == "scalar" and e[1][0] == "add" and any(["L", h] in e[1][1:3] for h in pair)
        if incident or e[0] != "scalar":
            while j < len(candidate) and candidate[j][0] == "scalar" and candidate[j][1][0] == "scale":
                g = candidate[j][1]
                require(g[1][0] == "L" and g[1][1] in pair, "inserted scale helper")
                h, q = g[1][1], Q(g[2], g[3])
                require(q > 0 and q.numerator & (q.numerator - 1) == 0 and q.denominator & (q.denominator - 1) == 0,
                        "inserted positive power of two")
                k = q.numerator.bit_length() - q.denominator.bit_length()
                require(k != 0 and candidate[j][2] == frames[h], "inserted scale frame/nonidentity")
                exponent[h] += k
                require(-4 <= exponent[h] <= 4, "actual exponent domain")
                scale_cost += abs(k)
                inserted += 1
                j += 1
        require(j < len(candidate), "candidate contains original event")
        actual = candidate[j]
        if incident:
            require(actual[:1] == e[:1] and actual[2:] == e[2:] and actual[1][:3] == e[1][:3], "ADD topology/frame")
            target, source = e[1][1:3]
            a = exponent.get(target[1], 0) if target[0] == "L" else 0
            b = exponent.get(source[1], 0) if source[0] == "L" else 0
            q, v = Q(e[1][3], e[1][4]), Q(actual[1][3], actual[1][4])
            require(v == q * Q(2) ** (a - b), "actual conjugated coefficient")
            add_delta += S["price"](v) - S["price"](q)
            changed += int(q != v)
        else:
            require(actual == e, "original event unchanged")
        if e[0] != "scalar":
            require(not any(exponent.values()), "zero at every nonscalar boundary")
        if e[0] == "climb" and e[2] in pair:
            require(frames[e[2]] == e[3], "original frame chain")
            frames[e[2]] = e[4]
        j += 1
    require(j == len(candidate) and not any(exponent.values()), "restored exit and no extra events")
    return {"inserted_scales": inserted, "scale_primitives_real": scale_cost,
            "changed_adds": changed, "add_delta_real": add_delta, "delta_real": scale_cost + add_delta}


def coupling_block(blocks, lower):
    """Small 9-by-9 witness for the only block with a strict gap in pair225/350."""
    block = next(b for b in blocks if b[0][0] == 18338)
    shared = [i for i, (_, _, signs) in enumerate(block) if all(signs)]
    require(len(shared) == 1, "one shared ADD in coupling block")
    at = shared[0]
    values = range(-4, 5)

    def charge(q):
        return len(lower(["add", ["L", 0], ["L", 1], q.numerator, q.denominator]))

    profiles = []
    for axis in range(2):
        row = {0: 0}
        for _, q, signs in block[:at + 1]:
            row = {k: min(v + abs(k - j) for j, v in row.items())
                   + charge(q * Q(2) ** (signs[axis] * k)) - charge(q) for k in values}
        tail = {k: abs(k) for k in values}
        for _, q, signs in reversed(block[at + 1:]):
            tail = {j: min(abs(k - j) + charge(q * Q(2) ** (signs[axis] * k)) - charge(q) + tail[k]
                           for k in values) for j in values}
        profiles.append([row[k] + tail[k] for k in values])
    event, q, signs = block[at]
    table = []
    for a, b in product(values, repeat=2):
        correction = charge(q * Q(2) ** (a * signs[0] + b * signs[1])) - charge(q * Q(2) ** (a * signs[0]))
        correction += charge(q) - charge(q * Q(2) ** (b * signs[1]))
        table.append([profiles[0][a + 4] + profiles[1][b + 4] + correction, a, b])
    joint = min(x[0] for x in table)
    singles = [[k for k in values if profiles[axis][k + 4] == min(profiles[axis])] for axis in range(2)]
    tied = min(c for c, a, b in table if a in singles[0] and b in singles[1])
    require(joint == -56 and tied == -53, "small coupling witness")
    return {"first_incident_event": block[0][0], "last_incident_event": block[-1][0], "incident_adds": len(block),
            "shared_event": event, "shared_coefficient": str(q), "signs": signs, "exponents": list(values),
            "conditional_single_deltas_real": profiles, "single_optimal_exponents": singles,
            "joint_minimizers": [x[1:] for x in table if x[0] == joint],
            "joint_delta_real": joint, "best_tied_single_delta_real": tied}


def controls(word, programs, pair, schedules):
    rejected = []

    def reject(name, fn):
        try:
            fn()
        except (ValueError, KeyError, IndexError):
            rejected.append(name)
        else:
            raise ValueError("control accepted: " + name)

    for orientation in ("forward", "backward"):
        original = programs[orientation]
        candidate, _ = S["transform"](original, word, pair, schedules[orientation])
        inserted = next(i for i in range(len(candidate)) if candidate[i] != original[i])
        require(candidate[inserted][1][0] == "scale", "control insertion located")
        bad = deepcopy(candidate)
        del bad[inserted]
        reject(orientation + ": omitted transition", lambda: check_transform(original, bad, word, pair))
        reject(orientation + ": omitted transition changes map", lambda: R["replay"](bad, orientation))
        bad = deepcopy(candidate)
        bad[inserted][2] = -1
        reject(orientation + ": wrong scale frame", lambda: check_transform(original, bad, word, pair))
        bad_schedule = deepcopy(schedules[orientation])
        bad_schedule[0][1] = 5
        reject(orientation + ": exponent out of domain", lambda: S["transform"](original, word, pair, bad_schedule))
        reject(orientation + ": missing ADD schedule", lambda: S["transform"](original, word, pair, schedules[orientation][1:]))
        blocks = S["segments"](original, pair)
        zeros = [[i, 0, 0] for block in blocks for i, _, _ in block]
        unchanged, count = S["transform"](original, word, pair, zeros)
        require(unchanged == original and count == 0, "zero schedule positive control")
    # Exhaust all 9^3 paths in a small interacting fixture, including tied single optima.
    tiny = [[(0, Q(1, 2), (1, 0)), (1, Q(2), (-1, 1)), (2, Q(1), (0, -1))]]
    states = list(product(range(-1, 2), repeat=2))
    records = []
    for path in product(states, repeat=3):
        schedule = [[i, *k] for i, k in enumerate(path)]
        joint = S["schedule_cost"](tiny, schedule)
        separate = sum(S["schedule_cost"](tiny, [[i, k[0] if axis == 0 else 0, k[1] if axis == 1 else 0]
                                                for i, k in enumerate(path)]) for axis in range(2))
        records.append((separate, joint))
    require(S["optimize"](tiny, ((-1, 1), (-1, 1)))["delta_real"] == min(x[1] for x in records), "exhaustive tiny joint optimum")
    require(S["tied_single_minimum"](tiny, bound=1) == min(records)[1], "exhaustive tiny tied optimum")
    manifest = json.loads((HERE / "SOURCES.json").read_bytes())
    bad = deepcopy(manifest)
    bad["files"][R["LOWER"]] = "0" * 64
    reject("source corruption", lambda: R["load"](manifest=bad))
    bad = deepcopy(manifest)
    del bad["archive_members"]["LOCAL-PROGRAMS.json.gz"]
    reject("source inventory omission", lambda: R["load"](manifest=bad))
    return {"rejected": rejected, "tiny_paths": len(records), "zero_schedule_orientations": 2}


def compute():
    word, programs, source, lower = R["load"]()
    helpers = S["eligible"](word, programs)
    all_pairs = S["pairs"](programs, helpers)
    require(len(helpers) == 237 and len(all_pairs) == 2414, "eligible interaction inventory")
    pairs = all_pairs[23:39]
    result = {"base": "bce54fb3f895cbe5cd4c0eb477c3afeed100190f", "seed": 23,
              "domain": [-4, 4], "pairs": pairs, "orientations": {}, "formal_columns": 712}
    all_programs, schedules, witnesses = [], {}, []
    for orientation in ("forward", "backward"):
        events = programs[orientation]
        census = []
        for pair in pairs:
            blocks = S["segments"](events, pair)
            joint = S["optimize"](blocks)
            tied = S["tied_single_minimum"](blocks)
            a = S["optimize"](blocks, ((-4, 4), (0, 0)))
            b = S["optimize"](blocks, ((0, 0), (-4, 4)))
            oracle, oracle_tied, oracle_separate, edges = dense_oracle(blocks, lower)
            require(joint["delta_real"] == oracle and tied == oracle_tied, "independent dense oracle")
            require(a["delta_real"] + b["delta_real"] == oracle_separate, "independent separate optimum")
            require(S["schedule_cost"](blocks, joint["schedule"]) == oracle, "attaining schedule")
            census.append({"pair": pair, "delta_real": oracle, "best_tied_single_delta_real": tied,
                           "single_deltas_real": [a["delta_real"], b["delta_real"]],
                           "strict_gap_real": tied - oracle, "blocks": len(blocks),
                           "incident_adds": sum(map(len, blocks)), "dense_edges": edges})
        winner = min(census, key=lambda x: (-x["strict_gap_real"], x["pair"]))
        pair = winner["pair"]
        require(pair == (225, 350) and winner["strict_gap_real"] == 3, "largest strict coupling gap")
        schedule = S["optimize"](S["segments"](events, pair))["schedule"]
        candidate, inserted = S["transform"](events, word, pair, schedule)
        invariant = check_transform(events, candidate, word, pair)
        require(invariant["inserted_scales"] == inserted and invariant["delta_real"] == winner["delta_real"], "literal invariant invoice")
        R["frame_check"](candidate, word, pair)
        R["replay"](events, orientation)
        R["replay"](candidate, orientation)
        before, after = R["invoice"](events, lower), R["invoice"](candidate, lower)
        require(after["complex_primitives"] - before["complex_primitives"] == 2 * winner["delta_real"], "full scalar invoice")
        require(before["paid_profile"] == after["paid_profile"] == source["paid_profiles"][orientation], "paid profile unchanged")
        require(before["prefix_l1"] == source["local"][orientation]["prefix_l1_upper"], "baseline prefix receipt")
        result["orientations"][orientation] = {"census": census, "winner": winner, "schedule": schedule,
            "coupling_block": coupling_block(S["segments"](events, pair), lower),
            "invariant": invariant, "before": before, "after": after, "candidate_sha256": R["digest"](R["canonical"](candidate))}
        schedules[orientation] = schedule
        witnesses.append(pair)
        all_programs.extend([events, candidate])
    require(witnesses[0] == witnesses[1], "one pair in both orientations")
    result["lowerer_checks"] = R["lowerer_checks"](all_programs, lower)
    result["controls"] = controls(word, programs, witnesses[0], schedules)
    result["status"] = "PASS_K8_PAIRED_TEMPORAL_NO_NEW_KAPPA"
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="print the reproducible certificate without comparing a saved copy")
    args = parser.parse_args()
    result = compute()
    if args.emit:
        print(json.dumps(result, indent=2))
    else:
        require(R["canonical"](result) == R["canonical"](json.loads((HERE / "CERTIFICATE.json").read_bytes())), "saved certificate mismatch")
        print(result["status"] + " pair=225,350 saved=474/474 strict_coupling_gain=6/6 pairs=16 orientations=2 columns=712")
