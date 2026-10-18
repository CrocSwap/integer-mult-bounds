#!/usr/bin/env python3
"""Independent finite five-wire splice checks; no synthesis code is imported.

Prepared for Ross with substantial OpenAI Codex assistance. Apache-2.0.
All 32 Boolean inputs are evaluated directly for each nominated local map.
The nonnegative transfer is separately evaluated on the five unit columns.
"""
import copy
import hashlib
import json


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def same(left, right, message):
    # JSON byte equality distinguishes Boolean values from integer indices.
    need(canonical(left) == canonical(right), message)


def evaluate(operations, values, positive=False):
    result = list(values)
    for destination, source in operations:
        if positive:
            result[destination] += result[source]
        else:
            result[destination] ^= result[source]
    return result


def equal_maps(old, new, width):
    for bits in range(1 << width):
        inputs = [(bits >> i) & 1 for i in range(width)]
        need(evaluate(old, inputs) == evaluate(new, inputs), "local Boolean map changed")


def positive_image(operations, width):
    return [evaluate(operations, [int(i == j) for i in range(width)], True)
            for j in range(width)]


def positive_guard(old, new, width):
    for direction in ("forward", "reverse"):
        before = old if direction == "forward" else list(reversed(old))
        after = new if direction == "forward" else list(reversed(new))
        a, b = positive_image(before, width), positive_image(after, width)
        need(all(y <= x for ac, bc in zip(a, b) for x, y in zip(ac, bc)),
             direction + " positive domination")


def flat(word, section):
    return [[frame, destination, [source]]
            for frame, destination, sources in word[section] for source in sources]


def cleanup(word):
    v = word["v"]
    full = [i for i, labels in enumerate(word["frames"])
            if sorted(labels) == list(range(v))]
    need(len(full) == 1, "unique full frame required")
    result = []
    for section in ("B", "A"):
        for _, destination, sources in reversed(word[section]):
            if not v <= destination < 2 * v:
                # Reverse individual source operands, independently of the builder.
                for source in reversed(sources):
                    result.append([full[0], destination, [source]])
    return result


def check_rewrites(baseline, candidate, certificate):
    need(certificate.get("format") == "r439-five-wire/1", "certificate format")
    need(type(certificate.get("seed")) is int and certificate["seed"] == 10, "seed")
    need(certificate.get("baseline_sha256") == digest(baseline), "baseline content hash")
    need(certificate.get("candidate_sha256") == digest(candidate), "candidate content hash")
    need(type(certificate.get("selected")) is list, "selected list")
    v, helper_count = baseline["v"], baseline["R"]
    need(type(v) is int and v > 0 and type(helper_count) is int and helper_count >= 0,
         "source register bounds")
    nregs = 2 * v + helper_count
    original = flat(baseline, "A")
    selected = certificate["selected"]
    previous, saved = 0, 0
    for item in selected:
        need(type(item) is dict and item.get("section") == "A", "only phase A permitted")
        for field in ("start", "stop", "frame", "saving"):
            need(type(item.get(field)) is int, "integer " + field)
        start, stop, frame = item["start"], item["stop"], item["frame"]
        need(previous <= start < stop <= len(original), "overlapping/out-of-range window")
        need(0 <= frame < len(baseline["frames"]), "frame out of range")
        previous = stop
        registers = item.get("registers")
        need(type(registers) is list and len(registers) == 5 and
             all(type(r) is int and 0 <= r < nregs and not v <= r < 2 * v for r in registers),
             "five physical z registers required")
        need(registers == sorted(set(registers)), "register order/uniqueness")
        old, new = item.get("old"), item.get("new")
        need(type(old) is list and type(new) is list, "operation lists")
        need(3 <= len(old) <= 12 and len(new) <= 6, "window/search length bounds")
        for ops in (old, new):
            need(all(type(op) is list and len(op) == 2 and
                     all(type(i) is int and 0 <= i < 5 for i in op) and op[0] != op[1]
                     for op in ops), "invalid transvection")
            need({r for op in ops for r in op} == set(range(5)), "participant set changed")
        decoded = [[frame, registers[d], [registers[s]]] for d, s in old]
        same(decoded, original[start:stop], "source window changed")
        need(len(new) < len(old) and item["saving"] == len(old) - len(new), "unpaid saving")
        equal_maps(old, new, 5)
        positive_guard(old, new, 5)
        saved += item["saving"]
    for field, value in (("saved_A", saved), ("saved_with_cleanup", 2 * saved)):
        need(type(certificate.get(field)) is int and certificate[field] == value,
             "incorrect " + field)

    expected = copy.deepcopy(baseline)
    replacement = copy.deepcopy(original)
    for item in reversed(selected):
        replacement[item["start"]:item["stop"]] = [
            [item["frame"], item["registers"][d], [item["registers"][s]]]
            for d, s in item["new"]]
    expected["A"] = replacement
    expected["C"] = cleanup(expected)
    same(expected, candidate, "candidate is not exact A splice plus literal C")
    return {"rewrites": len(selected), "inputs_per_rewrite": 32,
            "Boolean_inputs_checked": 32 * len(selected),
            "positive_columns_checked": 10 * len(selected),
            "saved_A": saved, "saved_with_cleanup": 2 * saved,
            "preserved_fields": sorted(k for k in baseline if k not in ("A", "C"))}


def controls():
    """Mathematical rejection controls independent of whichever windows are found."""
    rejected = []

    def reject(name, action, reason):
        try:
            action()
        except ValueError as error:
            need(reason in str(error), "wrong rejection for " + name + ": " + str(error))
            rejected.append(name)
        else:
            raise ValueError("control accepted: " + name)

    # Repeated CNOTs cancel over F2 but increase the positive transfer.
    equal_maps([], [[0, 1], [0, 1]], 2)
    reject("F2 cancellation hides positive growth",
           lambda: positive_guard([], [[0, 1], [0, 1]], 2), "forward positive")
    # Forward domination alone is insufficient even for a strictly shorter map.
    old = [[0, 1], [0, 1], [0, 1], [2, 0]]
    new = [[2, 0], [0, 1], [2, 1]]
    equal_maps(old, new, 3)
    need(all(y <= x for ac, bc in zip(positive_image(old, 3), positive_image(new, 3))
             for x, y in zip(ac, bc)), "reverse-only control premise")
    reject("forward-safe circuit grows reverse transfer",
           lambda: positive_guard(old, new, 3), "reverse positive")

    registers = [0, 2, 3, 4, 5]  # one source, one excluded target, four dirty helpers
    old = [[0, 1], [0, 1], [0, 1], [1, 2], [2, 3], [3, 4]]
    new = old[2:]
    decode = lambda ops: [[1, registers[d], [registers[s]]] for d, s in ops]
    baseline = {"v": 1, "R": 4, "frames": [[], [0]], "A": decode(old), "B": [],
                "D": [], "scatter": [[]], "stats": {"sentinel": 1}}
    baseline["C"] = cleanup(baseline)
    candidate = copy.deepcopy(baseline)
    candidate["A"] = decode(new)
    candidate["C"] = cleanup(candidate)
    certificate = {"format": "r439-five-wire/1", "seed": 10,
                   "baseline_sha256": digest(baseline), "candidate_sha256": digest(candidate),
                   "saved_A": 2, "saved_with_cleanup": 4,
                   "selected": [{"section": "A", "start": 0, "stop": 6, "frame": 1,
                                 "registers": registers, "old": old, "new": new, "saving": 2}]}
    check_rewrites(baseline, candidate, certificate)

    def mutate(name, edit, reason):
        changed = copy.deepcopy(certificate)
        edit(changed)
        reject(name, lambda: check_rewrites(baseline, candidate, changed), reason)

    mutate("wrong local Boolean map", lambda x: x["selected"][0]["new"].reverse(), "Boolean map")
    mutate("wrong frame", lambda x: x["selected"][0].__setitem__("frame", 0), "source window")
    mutate("target participant", lambda x: x["selected"][0]["registers"].__setitem__(0, 1), "physical z")
    mutate("self addition", lambda x: x["selected"][0]["new"][0].__setitem__(1, 0), "transvection")
    mutate("Boolean wire index", lambda x: x["selected"][0]["new"][0].__setitem__(0, False), "transvection")
    mutate("Boolean window index", lambda x: x["selected"][0].__setitem__("start", False), "integer start")
    mutate("unpaid saving", lambda x: x["selected"][0].__setitem__("saving", 3), "unpaid saving")
    mutate("missing participant", lambda x: x["selected"][0]["new"].pop(), "participant set")
    mutate("overlapping windows", lambda x: x["selected"].append(copy.deepcopy(x["selected"][0])), "overlapping")
    mutate("incorrect paired bill", lambda x: x.__setitem__("saved_with_cleanup", 2), "saved_with_cleanup")

    for name, edit in (
            ("unpaired stale literal cleanup", lambda x: x.__setitem__("C", baseline["C"])),
            ("unrelated edit with recomputed hash", lambda x: x["stats"].__setitem__("sentinel", 2))):
        changed = copy.deepcopy(candidate)
        edit(changed)
        altered = copy.deepcopy(certificate)
        altered["candidate_sha256"] = digest(changed)
        reject(name, lambda: check_rewrites(baseline, changed, altered), "exact A splice")
    reject("Boolean receipt equality", lambda: same({"x": 1}, {"x": True}, "receipt mismatch"), "receipt")
    return rejected


if __name__ == "__main__":
    result = controls()
    print("PASS_INDEPENDENT_FIVE_WIRE_CONTROLS:", len(result), "rejected")
