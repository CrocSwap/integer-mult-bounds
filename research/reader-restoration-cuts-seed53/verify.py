#!/usr/bin/env python3
"""Independent literal-column and exhaustive-partition checks. Apache-2.0."""
import argparse
import copy
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import random
import sys

ROOT = Path(__file__).resolve().parent


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def need(ok, message):
    if not ok:
        raise ValueError(message)


def literal(children, prices, cuts, overhead=0):
    """Replay every D/W input column; compare the whole state at each cut."""
    n = len(prices)
    state = [[int(i == j) for j in range(2 * n)] for i in range(2 * n)]
    eager = copy.deepcopy(state)
    start, cost, negative = 0, 0, []
    for i, child in enumerate(children):
        for j, (sign, reader) in enumerate(zip(child["signs"], child["reader"])):
            state[j] = [x + reader * y for x, y in zip(state[j], state[n + j])]
            state[n + j] = [sign * x for x in state[n + j]]
            eager[j] = [x + reader * y for x, y in zip(eager[j], eager[n + j])]
        if i + 1 in cuts:
            negative = []
            for j in range(n):
                sign = 1
                for child_back in reversed(children[start:i + 1]):
                    sign *= child_back["signs"][j]
                if sign == -1:
                    negative.append(j)
                    state[n + j] = [-x for x in state[n + j]]
            cost += sum(prices[j] for j in negative) + (overhead if negative else 0)
            if state != eager:
                return None
            start = i + 1
    need(start == len(children), "literal word has no final checkpoint")
    return cost


def brute(children, prices, required=(), overhead=0):
    r = len(children)
    if not r:
        return (0, 0, ()), 1
    best, count = None, 0
    for mask in range(1 << (r - 1)):
        cuts = tuple(i + 1 for i in range(r - 1) if mask >> i & 1) + (r,)
        if not set(required) <= set(cuts):
            continue
        count += 1
        cost = literal(children, prices, cuts, overhead)
        if cost is not None:
            key = cost, len(cuts), cuts
            if best is None or key < best:
                best = key
    return best, count


def checked_plan(planner, data):
    actual = planner.plan(**data)
    expected, count = brute(**data)
    key = actual["cost"], len(actual["cuts"]), tuple(actual["cuts"])
    need(key == expected, "planner disagrees with independent partition enumeration")
    need(literal(data["children"], data["prices"], actual["cuts"], data.get("overhead", 0)) == actual["cost"],
         "plan failed complete-column replay")
    previous = 0
    for segment in actual["segments"]:
        need(segment["start"] == previous and segment["stop"] > previous, "segment endpoints")
        chunk = data["children"][previous:segment["stop"]]
        negative = [j for j in range(len(data["prices"]))
                    if sum(c["signs"][j] == -1 for c in chunk) % 2]
        need(segment["negate"] == negative, "wrong emitted restoration")
        need(segment["cost"] == sum(data["prices"][j] for j in negative)
             + (data.get("overhead", 0) if negative else 0), "unpaid emitted restoration")
        previous = segment["stop"]
    return actual, count


def source_replay():
    pins = json.loads((ROOT / "SOURCES.json").read_text())
    for path, digest in pins["files"].items():
        need(hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest, "source hash: " + path)
    old = load("retained_pr1155", ROOT / "sources/pr1155/verify.py")
    need(json.loads(json.dumps(old.verify())) == json.loads((ROOT / "sources/pr1155/CERTIFICATE.json").read_text()),
         "retained certificate no longer reproduces")
    children = []
    for b in (1, 1, 1, -1, 1):
        phases = [old.G(-1)]
        child = old.make_child([old.G(b)], [old.G(0)], old.mat_diag(phases),
                               old.mat_diag(phases), lambda v: old.apply_diag(v, [old.G(-1)]),
                               "reader", ("diag", phases))
        children.append(child)
    batch = old.Batch(1, 0)
    apply, _ = old.compose_structured(children)
    probes = [old.G(1), old.G(0, 1), old.G(7, -3)]
    for w in probes:
        de, we, ce = batch.run_eager([w], children)
        dd, wd, cd = batch.run_deferred([w], children, apply)
        need(de[0] == dd[0] == old.G(3) * w and we[0] == wd[0] == w, "retained reader witness")
        need(ce["mults"] == 5 and cd["mults"] == 1, "retained restoration invoice")
    return {"old_certificate": "PASS", "probes": len(probes), "eager_mults": 5, "deferred_mults": 1}


def scalar_invoice(children, result):
    data, workspace = 11, 7
    counts = {"data_reads": 0, "coefficient_reads": 0, "data_writes": 0,
              "multiplies": 0, "adds": 0, "negations": 0, "program_records": 0}
    word = []
    restore = {s["stop"]: s["negate"] for s in result["segments"]}
    for i, child in enumerate(children):
        b, g = child["reader"][0], child["signs"][0]
        data += b * workspace
        workspace *= g
        word.append(("child", b, g))
        counts["data_reads"] += 2
        counts["coefficient_reads"] += 2
        counts["data_writes"] += 1 + (g == -1)
        counts["multiplies"] += 1
        counts["adds"] += 1
        counts["negations"] += g == -1
        counts["program_records"] += 1
        if restore.get(i + 1):
            need(restore[i + 1] == [0], "scalar restore mask")
            workspace = -workspace
            word.append(("restore",))
            counts["data_reads"] += 1
            counts["data_writes"] += 1
            counts["negations"] += 1
            counts["program_records"] += 1
    need((data, workspace) == (32, 7), "literal scalar result")
    for event in reversed(word):
        if event[0] == "restore":
            workspace = -workspace
        else:
            _, b, g = event
            workspace *= g
            data -= b * workspace
    need((data, workspace) == (11, 7), "literal inverse")
    return counts


def verify():
    retained = source_replay()
    planner = load("restoration_cut_planner", ROOT / "planner.py")
    fixture = json.loads((ROOT / "fixture.json").read_text())
    chosen, _ = checked_plan(planner, fixture)
    need(chosen["cost"] == 1 and chosen["cuts"] == [5], "five-child construction")
    forced = dict(fixture, required=[2])
    observed, _ = checked_plan(planner, forced)
    need(observed["cost"] == 5, "observation boundary must remove saving")
    eager = planner.plan(fixture["children"], [1], required=[1, 2, 3, 4, 5])
    invoice = {"eager": scalar_invoice(fixture["children"], eager),
               "deferred": scalar_invoice(fixture["children"], chosen),
               "input_D": 11, "input_W": 7, "output_D": 32, "output_W": 7,
               "common_sufficient_signed_bits": 7}

    batches = partitions = 0
    alphabet = [{"reader": [b], "signs": [g]} for g in (-1, 1) for b in (-1, 0, 1)]
    for r in range(5):
        for word in itertools.product(alphabet, repeat=r):
            _, count = checked_plan(planner, {"children": list(word), "prices": [1]})
            batches += 1
            partitions += count
    scalar = {"batches": batches, "partitions": partitions, "max_children": 4}

    alphabet2 = [{"reader": list(b), "signs": list(g)}
                 for g in itertools.product((-1, 1), repeat=2)
                 for b in itertools.product((-1, 0, 1), repeat=2)]
    batches = partitions = 0
    for word in itertools.product(alphabet2, repeat=2):
        _, count = checked_plan(planner, {"children": list(word), "prices": [2, 5], "overhead": 3})
        batches += 1
        partitions += count
    two_coordinate = {"batches": batches, "partitions": partitions}

    rng = random.Random(53)
    partitions = 0
    for trial in range(160):
        n, r = 1 + trial % 3, 5 + trial % 4
        data = {"children": [{"signs": [rng.choice((-1, 1)) for _ in range(n)],
                               "reader": [rng.randrange(-3, 4) for _ in range(n)]} for _ in range(r)],
                "prices": [rng.randrange(1, 10) for _ in range(n)],
                "required": [i for i in range(1, r + 1) if rng.randrange(5) == 0],
                "overhead": rng.randrange(4)}
        _, count = checked_plan(planner, data)
        partitions += count

    controls = []
    changed = copy.deepcopy(fixture)
    changed["children"][3]["reader"] = [1]
    changed_plan, _ = checked_plan(planner, changed)
    need(changed_plan["cost"] == 5, "broken cancellation must cost five")
    controls += ["changed reader destroys cancellation", "checkpoint after child two destroys saving"]
    need(literal(fixture["children"], [1], [2, 5]) is None, "unchecked intermediate cut accepted")
    controls.append("final equality does not authorize an intermediate cut")
    read_first = [{"reader": [1], "signs": [-1]}, {"reader": [0], "signs": [-1]}]
    read_last = [{"reader": [0], "signs": [-1]}, {"reader": [1], "signs": [-1]}]
    need(planner.plan(read_first, [1])["cost"] == 0 and planner.plan(read_last, [1])["cost"] == 2,
         "reader order boundary")
    controls.append("same children in a different order lose cancellation")
    mutations = [dict(fixture, prices=[0]), dict(fixture, prices=[True]),
                 dict(fixture, required=[0]), dict(fixture, required=[6]),
                 dict(fixture, required=[2, 2]), dict(fixture, overhead=-1),
                 dict(fixture, children=[{"signs": [0], "reader": [1]}]),
                 dict(fixture, children=[{"signs": [-1], "reader": [1, 2]}]),
                 dict(fixture, children=[{"signs": [-1], "reader": [1.0]}])]
    for bad in mutations:
        try:
            planner.plan(**bad)
        except ValueError:
            continue
        raise ValueError("invalid input accepted")
    return {"status": "PASS_READER_RESTORATION_CUTS", "base": "1b59b624d21924f8e3537cdc1ac52d3be6eda2fe",
            "seed": 53, "fixture": chosen, "forced_cut_2": observed,
            "scalar_instruction_invoice": invoice,
            "retained_pr1155": retained, "scalar_exhaustion": scalar,
            "two_coordinate_exhaustion": two_coordinate,
            "seeded_longer": {"batches": 160, "partitions": partitions, "max_children": 8, "max_dimension": 3},
            "mathematical_controls": controls, "invalid_input_controls": len(mutations),
            "scope": "exact diagonal readers and signs; every chosen cut matches eager data and workspace; no new kappa"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print recomputed certificate without comparing saved certificate")
    args = parser.parse_args()
    try:
        result = verify()
        if args.json:
            print(json.dumps(result, indent=2, sort_keys=True))
        else:
            need(result == json.loads((ROOT / "CERTIFICATE.json").read_text()), "saved certificate mismatch")
            print("PASS_READER_RESTORATION_CUTS restoration=5->1 forced_cut=5 exhaustive=2851 seeded=160")
    except (OSError, ValueError, TypeError, KeyError) as exc:
        parser.exit(1, "FAIL_READER_RESTORATION_CUTS: " + str(exc) + "\n")


if __name__ == "__main__":
    main()
