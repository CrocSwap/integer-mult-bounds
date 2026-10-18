#!/usr/bin/env python3
"""Independent row-set census of the frozen R439 two-shear chain.

Uses row support sets and intersection cardinalities, not packed columns or
the primary checker. Apache-2.0. Prepared with substantial Codex assistance.
The default verifies the recorded receipt; an explicit --write creates it.
"""

import argparse
from collections import Counter
import gzip
import hashlib
import itertools
import json
from pathlib import Path
import struct
import sys


PARENT = Path("research/r439-bsection-stars-seed01")
SOURCE_SHA256 = {
    "candidate.json.gz": "b452d2c2b0b2a546d1105b1da9769aa78e5c54d6f00e97b30c77e3f54ce445ee",
    "candidate_search.json": "488741d5ad803372b622495972d754ab2998a8afb0b84ef755edc337b20d0af0",
}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, "duplicate JSON key: " + key)
        result[key] = value
    return result


def load_parent(root):
    objects = {}
    for name, expected in SOURCE_SHA256.items():
        raw = (root / PARENT / name).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == expected, "source pin: " + name)
        decoded = gzip.decompress(raw) if name.endswith(".gz") else raw
        objects[name] = json.loads(decoded, object_pairs_hook=unique_object)
    word = objects["candidate.json.gz"]
    search = objects["candidate_search.json"]
    need(type(word["v"]) is int and word["v"] == 111, "source vertex count")
    need(type(word["R"]) is int and word["R"] == 439, "source helper count")
    canonical = json.dumps(word, sort_keys=True, separators=(",", ":")).encode()
    need(hashlib.sha256(canonical).hexdigest() == search["candidate_sha256"],
         "candidate canonical digest")
    need(search["helper_edges"] == 236 and len(search["steps"]) == 236,
         "helper preparation count")
    need(search["target_shears"] == 306 and search["middle_weight"] == 4464,
         "frozen middle metadata")
    return word, search


def gate(gate_value, low, high):
    need(type(gate_value) is list and len(gate_value) == 3, "gate shape")
    frame, destination, sources = gate_value
    need(type(frame) is int and frame == 0, "D frame")
    need(type(destination) is int and low <= destination < high, "gate destination")
    need(type(sources) is list, "gate sources")
    need(all(type(x) is int and low <= x < high for x in sources), "source register")
    need(len(set(sources)) == len(sources) and destination not in sources,
         "repeated/self source")
    return destination, sources


def reconstruct(word, search):
    """Transpose explicit middle row incidence into finite row-support sets."""
    d = word["D"]
    need(len(d) == 2 * 236 + 2 * 306 + 111, "D block length")
    preparations = d[:236]
    target_preparations = d[236:542]
    middle = d[542:653]
    need(d[653:959] == target_preparations[::-1], "inverse target preparation")
    need(d[959:] == preparations[::-1], "reverse helper preparation")
    components = list(range(439))

    def representative(index):
        while components[index] != index:
            components[index] = components[components[index]]
            index = components[index]
        return index

    for operation, step in zip(preparations, search["steps"]):
        destination, sources = gate(operation, 222, 661)
        need(len(sources) == 1, "one-source helper preparation")
        a, b = destination - 222, sources[0] - 222
        need(type(step["a"]) is int and type(step["b"]) is int,
             "helper step index type")
        need((a, b) == (step["a"], step["b"]), "helper preparation provenance")
        ra, rb = representative(a), representative(b)
        if ra != rb:
            components[max(ra, rb)] = min(ra, rb)
    components = [representative(i) for i in range(439)]
    for operation in target_preparations:
        _, sources = gate(operation, 111, 222)
        need(len(sources) == 1, "one-source target preparation")
    rows = [set() for _ in range(439)]
    for index, operation in enumerate(middle):
        need(type(operation) is list and len(operation) == 3, "middle gate shape")
        frame, destination, sources = operation
        need(type(frame) is int and frame == 0, "middle frame")
        need(type(destination) is int and destination == 111 + index, "middle row order")
        need(type(sources) is list and all(type(s) is int and 222 <= s < 661 for s in sources),
             "middle helper sources")
        need(len(sources) == len(set(sources)), "repeated middle source")
        for source in sources:
            rows[source - 222].add(index)
    columns = tuple(frozenset(row) for row in rows)
    need(sum(map(len, columns)) == 4464, "middle incidence count")
    retained = word["ret"]
    need(type(retained) is list and all(type(x) is int and 222 <= x < 661 for x in retained),
         "retained helper register")
    need(len(set(retained)) == len(retained) == 9, "retained helper count")
    eligible = tuple(i for i in range(439) if 222 + i not in retained)
    need(len(eligible) == 430, "eligible helper count")
    return columns, components, eligible


def literal_chain(columns, source_bits, wrong_order=False, missing_mixed=False,
                  wrong_restoration=False):
    """Execute a three-helper preparation/middle/restoration on one bit input."""
    helpers = list(source_bits)
    a, b, c = columns
    operations = ((1, 2), (0, 1)) if wrong_order else ((0, 1), (1, 2))
    for destination, source in operations:
        helpers[destination] ^= helpers[source]
    compensated = (a, a ^ b, b ^ c if missing_mixed else a ^ b ^ c)
    output = set()
    for value, support in zip(helpers, compensated):
        if value:
            output ^= support
    restoration = operations if wrong_restoration else operations[::-1]
    for destination, source in restoration:
        helpers[destination] ^= helpers[source]
    return tuple(helpers), output


def controls():
    # Both unilateral complete gains are nonpositive, while the ordered chain
    # saves two ADDs. This tests a distinction that a commuting-score model misses.
    columns = (frozenset((0, 1, 2, 3)), frozenset((0, 1, 2, 4, 5, 6)),
               frozenset((3, 4, 5, 6)))
    a, b, c = columns
    need((len(b) - len(a ^ b) - 2, len(c) - len(b ^ c) - 2) == (0, -2),
         "toy unilateral gains")
    need(len(b) + len(c) - len(a ^ b) - len(a ^ b ^ c) - 4 == 2,
         "toy joint gain")
    cases = tuple(itertools.product((0, 1), repeat=3))

    def original(bits):
        support = set()
        for bit, column in zip(bits, columns):
            if bit:
                support ^= column
        return bits, support

    need(all(literal_chain(columns, bits) == original(bits) for bits in cases),
         "all eight chain endpoint columns")
    faults = ("wrong_order", "missing_mixed", "wrong_restoration")
    for fault in faults:
        need(any(literal_chain(columns, bits, **{fault: True}) != original(bits)
                 for bits in cases), "undetected control: " + fault)
    return {"toy_unilateral_gains": [0, -2], "toy_joint_gain": 2,
            "literal_binary_inputs": 8, "detected_faults": list(faults)}


def census(columns, components, eligible):
    """Exhaustive lexicographic scoring using only set cardinalities.

    If D=A symmetric_difference B, then
      |A xor B xor C| = |D| + |C| - 2 |D intersection C|.
    Thus g = |B| - 2|D| + 2|D intersection C| - 4.
    Every admitted record, including nonpositive records, enters the digest.
    """
    weights = tuple(map(len, columns))
    unilateral = [[0] * 439 for _ in range(439)]
    for a in eligible:
        for b in eligible:
            unilateral[a][b] = weights[b] - len(columns[a] ^ columns[b]) - 2
    tails = {
        b: tuple(c for c in eligible if components[b] != components[c]
                 and unilateral[b][c] <= 0)
        for b in eligible
    }
    histogram = {}
    digest = hashlib.sha256()
    pack = struct.Struct("<4i").pack
    maximum = None
    first_maximum = None
    positives = []
    for a in eligible:
        block = bytearray()
        component_a = components[a]
        for b in eligible:
            if component_a == components[b] or unilateral[a][b] > 0:
                continue
            difference = columns[a] ^ columns[b]
            constant = weights[b] - 2 * len(difference) - 4
            for c in tails[b]:
                if component_a == components[c]:
                    continue
                gain = constant + 2 * len(difference.intersection(columns[c]))
                histogram[gain] = histogram.get(gain, 0) + 1
                block.extend(pack(a, b, c, gain))
                if gain > 0:
                    tie = int.from_bytes(hashlib.sha256(pack(17, a, b, c)).digest(), "big")
                    positives.append([a, b, c, gain, tie])
                if maximum is None or gain > maximum:
                    maximum = gain
                    first_maximum = [a, b, c]
        digest.update(block)
    count = sum(histogram.values())
    need(count > 0 and maximum is not None, "empty census")
    sizes = Counter(components[i] for i in eligible)
    n = len(eligible)
    distinct_components = n**3 - 3 * n * sum(s**2 for s in sizes.values()) + 2 * sum(
        s**3 for s in sizes.values())
    positives.sort(key=lambda row: (-row[3], row[4]))
    return {
        "candidate_count": count,
        "ordered_distinct_helpers": n * (n - 1) * (n - 2),
        "distinct_parent_components": distinct_components,
        "gain_histogram": {str(g): histogram[g] for g in sorted(histogram)},
        "positive_count": sum(n for g, n in histogram.items() if g > 0),
        "maximum_gain": maximum,
        "first_lexicographic_maximum": first_maximum,
        "records_sha256": digest.hexdigest(),
        "digest_encoding": "lexicographic helper indices; struct.pack('<4i',a,b,c,gain)",
        "nominees": positives[:32],
    }


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def same(actual, expected, name):
    # Comparing canonical bytes distinguishes booleans from equal-valued ints.
    need(canonical(actual) == canonical(expected), name)


def construct(parent, columns, triple):
    a, b, c = triple
    adjusted = list(columns)
    adjusted[b] = columns[b] ^ columns[a]
    adjusted[c] = columns[c] ^ columns[b] ^ columns[a]
    middle = [[0, 111 + i, [222 + j for j in range(439) if i in adjusted[j]]]
              for i in range(111)]
    preparation = [[0, 222 + a, [222 + b]], [0, 222 + b, [222 + c]]]
    trial = dict(parent)
    d = parent["D"]
    trial["D"] = (d[:236] + preparation + d[236:542] + middle + d[653:959]
                  + preparation[::-1] + d[959:])
    return trial


def lower(word):
    """Lower every scalar ADD and the nine scatter COPY/ERASE lifetimes."""
    instructions = []
    for section in ("D", "A"):
        for _, destination, sources in word[section]:
            instructions.extend(("add", destination, source) for source in sources)
    for index, source in enumerate(word["ret"]):
        instructions.append(("copy", 661, source))
        for row, slots in enumerate(word["scatter"]):
            if index in slots:
                instructions.append(("add", 111 + row, 661))
        instructions.append(("erase", 661, source))
    for section in ("B", "C"):
        for _, destination, sources in word[section]:
            instructions.extend(("add", destination, source) for source in sources)
    return instructions


def literal(instructions, reverse=False):
    # Each set records the original dirty input basis vectors present in a row.
    rows = [{i} for i in range(661)] + [set()]
    sequence = reversed(instructions) if reverse else instructions
    for operation, destination, source in sequence:
        if reverse:
            operation = {"copy": "erase", "erase": "copy", "add": "add"}[operation]
        if operation == "add":
            rows[destination].symmetric_difference_update(rows[source])
        elif operation == "copy":
            need(not rows[destination], "COPY into live temporary")
            rows[destination] = set(rows[source])
        else:
            need(rows[destination] == rows[source], "ERASE changed temporary")
            rows[destination].clear()
    need(not rows[661], "unrestored COPY temporary")
    return rows[:661]


def peak(instructions, reverse):
    values = [1] * 661 + [0]
    maximum = 1
    for operation, destination, source in (reversed(instructions) if reverse else instructions):
        if reverse:
            operation = {"copy": "erase", "erase": "copy", "add": "add"}[operation]
        if operation == "add":
            values[destination] += values[source]
        elif operation == "copy":
            values[destination] = values[source]
        else:
            values[destination] = 0
        maximum = max(maximum, values[destination])
    return maximum


def invoice(word, instructions):
    f, b = peak(instructions, False), peak(instructions, True)
    local = 64 * f**3 * b**2
    nine = (1 << 18) * f**5 * b**4
    kinds = Counter(operation for operation, _, _ in instructions)
    return {
        "ADDs": kinds["add"], "COPYs": kinds["copy"], "ERASEs": kinds["erase"],
        "D_ADDs": sum(len(operation[2]) for operation in word["D"]),
        "helpers": word["R"], "F": f, "B": b,
        "local_bound": str(local), "nine_stage_bound": str(nine),
        "local_bits": local.bit_length(), "nine_stage_bits": nine.bit_length(),
        "admitted": local < 1 << 104 and nine < 1 << 192,
    }


def frame_paths(word):
    frames = [frozenset(frame) for frame in word["frames"]]
    paths = [[index] for index in word["start"]]
    need(len(paths) == 661 and len(word["final"]) == 661, "frame register count")
    for section in ("D", "A", "B", "C"):
        for frame, destination, sources in word[section]:
            for register in (destination, *sources):
                previous = paths[register][-1]
                if previous != frame:
                    need(frames[previous] < frames[frame], "illegal frame path")
                    paths[register].append(frame)
    for register, frame in enumerate(word["final"]):
        previous = paths[register][-1]
        if previous != frame:
            need(frames[previous] < frames[frame], "illegal terminal frame path")
            paths[register].append(frame)
    return paths


def trial_checks(parent, columns, enumerated, certificate, package):
    expected_census = certificate["census"]
    names = {
        "candidate_count": "unilateral_nonpositive", "positive_count": "positive_joint",
        "maximum_gain": "maximum_joint_gain", "records_sha256": "records_sha256",
        "gain_histogram": "gain_histogram", "nominees": "nominees",
        "ordered_distinct_helpers": "ordered_distinct_helpers",
        "distinct_parent_components": "distinct_parent_components",
    }
    for actual_name, expected_name in names.items():
        same(enumerated[actual_name], expected_census[expected_name], "primary census: " + actual_name)
    parent_instructions = lower(parent)
    same(invoice(parent, parent_instructions), certificate["baseline"], "primary baseline invoice")
    endpoints = [literal(parent_instructions, reverse) for reverse in (False, True)]
    paths = frame_paths(parent)
    source_access = Counter(source for operation, _, source in parent_instructions
                            if operation == "add" and source < 111)
    copy_sources = [source for operation, _, source in parent_instructions if operation == "copy"]
    trials = []
    winner = None
    winning_word = None
    need(len(certificate["trials"]) == len(enumerated["nominees"]) == 32, "trial coverage")
    for nominee, expected_trial in zip(enumerated["nominees"], certificate["trials"]):
        a, b, c, gain, tie = nominee
        trial = construct(parent, columns, (a, b, c))
        operations = lower(trial)
        billed = invoice(trial, operations)
        result = {"triple": [a, b, c], "gain": gain, "tie": str(tie), "invoice": billed}
        same(result, expected_trial, "primary full trial invoice")
        need(billed["ADDs"] == 11500 - gain and billed["D_ADDs"] == 5548 - gain,
             "complete wrapper ADD charge")
        same(frame_paths(trial), paths, "inherited frame paths")
        need(Counter(source for operation, _, source in operations
                     if operation == "add" and source < 111) == source_access,
             "changed input source access")
        need([source for operation, _, source in operations if operation == "copy"] == copy_sources,
             "changed copied helpers")
        for reverse in (False, True):
            need(literal(operations, reverse) == endpoints[reverse], "full dirty endpoint mismatch")
        if winner is None and billed["admitted"]:
            winner, winning_word = result, trial
        trials.append(result)
    need(winner is not None, "no admitted nominee")
    same(winner, certificate["winner"], "primary selected winner")
    candidate = json.loads(gzip.decompress((package / "CANDIDATE.json.gz").read_bytes()),
                           object_pairs_hook=unique_object)
    same(winning_word, candidate, "complete winning candidate payload")
    winning_digest = hashlib.sha256(canonical(winning_word)).hexdigest()
    same(winning_digest, certificate["full_word_sha256"], "winning word digest")
    # Exercise lifetime rejection separately from endpoint compensation tests.
    first_copy = next(i for i, operation in enumerate(parent_instructions) if operation[0] == "copy")
    bad_copy = parent_instructions[:first_copy + 1] + [parent_instructions[first_copy]] + parent_instructions[first_copy + 1:]
    bad_erase = (parent_instructions[:first_copy + 1] + [("add", 661, 0)]
                 + parent_instructions[first_copy + 1:])
    lifetime_controls = []
    for name, bad in (("copy-live-temporary", bad_copy), ("erase-changed-temporary", bad_erase)):
        try:
            literal(bad)
        except ValueError:
            lifetime_controls.append(name)
        else:
            raise ValueError("undetected lifetime control: " + name)
    return {
        "trials": trials, "winner": winner, "winning_word_sha256": winning_digest,
        "dirty_registers": 661, "trial_endpoint_directions": 64,
        "inherited_frame_paths_sha256": hashlib.sha256(canonical(paths)).hexdigest(),
        "copied_helpers": copy_sources, "source_access_equal": True,
        "lifetime_controls": lifetime_controls,
    }


def run(root, package):
    word, search = load_parent(root)
    columns, components, eligible = reconstruct(word, search)
    enumerated = census(columns, components, eligible)
    certificate = json.loads((package / "CERTIFICATE.json").read_text(), object_pairs_hook=unique_object)
    return {
        "format": "r439-neutral-helper-chain-independent/2",
        "seed": 17,
        "method": "explicit row-support sets, symmetric differences and intersection cardinalities",
        "source_sha256": SOURCE_SHA256,
        "middle_weight": sum(map(len, columns)),
        "helper_components": len(set(components)),
        "eligible_helpers": len(eligible),
        "controls": controls(),
        **enumerated,
        "complete_word_checks": trial_checks(word, columns, enumerated, certificate, package),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--write", type=Path, help="explicitly write the generated JSON receipt")
    arguments = parser.parse_args()
    try:
        package = Path(__file__).resolve().parent
        receipt_path = package / "INDEPENDENT.json"
        expected = None
        if arguments.write is None:
            expected = json.loads(receipt_path.read_text(), object_pairs_hook=unique_object)
        receipt = run(arguments.source_root, package)
        encoded = json.dumps(receipt, sort_keys=True, indent=2) + "\n"
        if arguments.write is not None:
            arguments.write.write_text(encoded)
        else:
            same(receipt, expected, "independent receipt mismatch")
        print("PASS_INDEPENDENT_HELPER_CHAIN triples=%d positive=%d trials=32 dirty=661 directions=64 digest=%s no_new_kappa" % (
            receipt["candidate_count"], receipt["positive_count"], receipt["records_sha256"]))
    except (OSError, ValueError, KeyError, TypeError) as error:
        print("FAIL_INDEPENDENT_HELPER_CHAIN " + str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
