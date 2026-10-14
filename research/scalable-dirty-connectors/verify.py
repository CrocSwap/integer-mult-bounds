#!/usr/bin/env python3
"""Physical-row polynomial replay, rectangular matrix oracle and controls.

No normalized-axis or Gray-path identity is used by the replay interpreter.
All safety/correctness checks remain active under python -O. Apache-2.0.
"""

from collections import Counter, deque
from dataclasses import replace
import hashlib
import json
from math import comb
from pathlib import Path
import random
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from connector import extra_readout_baseline, fixed_port_five, gray_baseline, star
from obstruction import census


def require(condition, message):
    if not condition:
        raise ValueError(message)


def replay(program, *, minimal_sources=False, paired_readouts=True):
    """Root bits are independent dirt; upper bits are formal B_j(x_j).

    For each output m, applying the formal linear map A_m to these bits is
    injective as a *formal expression*. This proves the identity for arbitrary
    maps; no actual A or B needs to be injective, square, or invertible.
    """
    n, k = program.sources, program.roots
    require(type(n) is int and n >= 4, "invalid sources")
    require(type(k) is int and k >= 1, "invalid roots")
    require(paired_readouts or k == 1, "extra-readout contract is one-root only")
    roots = [1 << i for i in range(k)]
    outputs = [0] * (1 << n)
    source_counts, output_counts, tags = Counter(), Counter(), Counter()
    ports = {}
    for operation in program.operations:
        require(type(operation) is tuple and len(operation) == 3, "invalid operation")
        tag, label, port = operation
        require(tag in ("B", "A", "X"), "invalid opcode")
        require(type(label) is int and type(port) is int, "noninteger operand")
        require(0 <= port < k, "invalid port")
        tags[tag] += 1
        if tag == "X":
            require(0 <= label < k and label != port, "invalid transfer")
            roots[label] ^= roots[port]
        elif tag == "B":
            require(0 <= label < n, "invalid source")
            roots[port] ^= 1 << (k + label)
            source_counts[label] += 1
            ports.setdefault(label, set()).add(port)
        else:
            require(1 <= label < (1 << n), "invalid target")
            outputs[label] ^= roots[port]
            output_counts[label] += 1
    require(roots == [1 << i for i in range(k)], "dirty roots or sources not restored")
    require(all(outputs[m] == m << k for m in range(1, 1 << n)), "wrong output polynomial")
    require(all(output_counts[m] >= 2 and output_counts[m] % 2 == 0
                for m in range(1, 1 << n)), "even readout bill")
    if paired_readouts:
        require(all(output_counts[m] == 2 for m in range(1, 1 << n)), "paired readout bill")
    require(all(source_counts[j] >= 2 for j in range(n)), "source bill")
    if minimal_sources:
        require(all(source_counts[j] == 2 for j in range(n)), "nonminimal source calls")
        require(all(len(ports[j]) == 1 for j in range(n)), "source port changed")
        require(all(op[2] == 0 for op in program.operations if op[0] == "A"), "readout port changed")
    encoded = json.dumps(program.operations, separators=(",", ":")).encode()
    return {
        "sources": n, "roots": k, "source_calls": tags["B"],
        "readouts": tags["A"], "transfers": tags["X"],
        "instructions": len(program.operations),
        "source_multiplicities": [source_counts[j] for j in range(n)],
        "source_ports": [sorted(ports[j]) for j in range(n)],
        "readout_multiplicity_histogram": {
            str(count): targets for count, targets in sorted(Counter(output_counts.values()).items())
        },
        "program_sha256": hashlib.sha256(encoded).hexdigest(),
    }


def apply(matrix, vector):
    return sum(((row & vector).bit_count() % 2) << i for i, row in enumerate(matrix))


def check_extra_readout_minima(program):
    """An independent pair-difference BFS checks the compiler's subset DP.

    Any even subset of t observations is t/2 pair differences. Conversely,
    canceling duplicated endpoints in a shortest pair representation yields
    an even subset of no larger size. Thus the two minima coincide.
    """
    points, state = [0], 0
    for tag, label, port in program.operations:
        if tag == "B":
            state ^= 1 << label
            points.append(state)
    differences = sorted({a ^ b for a in points for b in points} - {0})
    distance = {0: 0}
    todo = deque([0])
    while todo:
        mask = todo.popleft()
        for difference in differences:
            target = mask ^ difference
            if target not in distance:
                distance[target] = distance[mask] + 1
                todo.append(target)
    counts = Counter(label for tag, label, port in program.operations if tag == "A")
    require(len(distance) == 1 << program.sources, "pair-difference span")
    require(all(counts[m] == 2 * distance[m] for m in range(1, 1 << program.sources)),
            "subset DP disagrees with shortest pair-difference BFS")


def dense_case(program, rng, trial):
    n, k = program.sources, program.roots
    root_width = 1 + trial % 7
    input_width = 1 + (trial * 3) % 9
    output_width = 1 + (trial * 5) % 8
    b = [[rng.getrandbits(input_width) for _ in range(root_width)] for _ in range(n)]
    a = [[rng.getrandbits(root_width) for _ in range(output_width)] for _ in range(1 << n)]
    # Include singular/zero maps deliberately; restoration cannot rely on them.
    if trial % 3 == 0:
        b[0] = [0] * root_width
    if trial % 4 == 0:
        a[-1] = [1] * output_width
    x = [rng.getrandbits(input_width) for _ in range(n)]
    roots = [rng.getrandbits(root_width) for _ in range(k)]
    outputs = [rng.getrandbits(output_width) for _ in range(1 << n)]
    old_roots, expected = roots[:], outputs[:]
    responses = [apply(matrix, source) for matrix, source in zip(b, x)]
    for mask in range(1, 1 << n):
        summed = 0
        for j, response in enumerate(responses):
            if mask & (1 << j):
                summed ^= response
        expected[mask] ^= apply(a[mask], summed)
    for tag, label, port in program.operations:
        if tag == "X":
            roots[label] ^= roots[port]
        elif tag == "B":
            roots[port] ^= apply(b[label], x[label])
        else:
            outputs[label] ^= apply(a[label], roots[port])
    require(roots == old_roots and outputs == expected, "matrix oracle mismatch")
    # The additive batch is its own inverse, including all initially dirty rows.
    for tag, label, port in reversed(program.operations):
        if tag == "X":
            roots[label] ^= roots[port]
        elif tag == "B":
            roots[port] ^= apply(b[label], x[label])
        else:
            outputs[label] ^= apply(a[label], roots[port])
    require(roots == old_roots, "inverse root mismatch")
    for mask in range(1, 1 << n):
        summed = 0
        for j, response in enumerate(responses):
            if mask & (1 << j):
                summed ^= response
        require(outputs[mask] == expected[mask] ^ apply(a[mask], summed), "inverse output mismatch")


def failure_controls(program):
    controls = 0
    for tag in ("B", "A", "X"):
        for at, op in enumerate(program.operations):
            if op[0] != tag:
                continue
            edited = program.operations[:at] + program.operations[at + 1 :]
            try:
                replay(replace(program, operations=edited), minimal_sources=True)
            except ValueError:
                controls += 1
            else:
                raise ValueError(f"accepted omitted {tag} at {at}")
    for at, (tag, label, port) in enumerate(program.operations):
        if tag == "X":
            wrong = (tag, port, label)
        else:
            wrong = (tag, label, (port + 1) % program.roots)
        edited = program.operations[:at] + (wrong,) + program.operations[at + 1 :]
        try:
            replay(replace(program, operations=edited), minimal_sources=True)
        except ValueError:
            controls += 1
        else:
            raise ValueError(f"accepted wrong port/direction at {at}")
        if tag in ("B", "A"):
            wrong_label = (label + 1) % program.sources if tag == "B" else label % ((1 << program.sources) - 1) + 1
            wrong = (tag, wrong_label, port)
            edited = program.operations[:at] + (wrong,) + program.operations[at + 1 :]
            try:
                replay(replace(program, operations=edited), minimal_sources=True)
            except ValueError:
                controls += 1
            else:
                raise ValueError(f"accepted wrong label at {at}")
    for wrong in (("B", True, 0), ("A", 0, 0), ("X", 0, 0), ("B", 0.0, 0), ("B", 0, program.roots)):
        try:
            replay(replace(program, operations=program.operations + (wrong,)))
        except ValueError:
            controls += 1
        else:
            raise ValueError("accepted malformed operation")
    return controls


def main():
    require(sys.argv[1:] in ([], ["--write-expected"]), "use --write-expected or no arguments")
    receipt = {"star": [], "gray": [], "extra_readout": [], "fixed_port_five": None}
    rng = random.Random(0x53474152)
    extra_rng = random.Random(0x45585452)
    dense_cases = 0
    for n in range(4, 11):
        candidate, baseline = star(n), gray_baseline(n)
        bill = replay(candidate, minimal_sources=True)
        require(bill["source_calls"] == 2 * n, "star source formula")
        require(bill["readouts"] == 2 * ((1 << n) - 1), "star output formula")
        require(bill["transfers"] == 8 * ((1 << (n - 4)) - 1), "star transfer formula")
        old = replay(baseline)
        require(old["source_calls"] == (1 << (n // 2)) + (1 << (n - n // 2)), "Gray source formula")
        receipt["star"].append(bill)
        receipt["gray"].append(old)
        extra = extra_readout_baseline(n)
        check_extra_readout_minima(extra)
        alternative = replay(extra, minimal_sources=True, paired_readouts=False)
        require(alternative["source_calls"] == 2 * n and alternative["transfers"] == 0,
                "extra-readout source/transfer bill")
        require(alternative["readouts"] <= n * (1 << n), "extra-readout general bound")
        if n in (5, 6, 7, 8):
            require(alternative["readouts"] == {5: 64, 6: 156, 7: 368, 8: 828}[n],
                    "reviewed extra-readout invoice")
        receipt["extra_readout"].append(alternative)
        for program in (candidate, baseline, extra):
            for trial in range(20):
                dense_case(program, extra_rng if program is extra else rng, trial)
                dense_cases += 1
    fixed = fixed_port_five()
    receipt["fixed_port_five"] = replay(fixed, minimal_sources=True)
    for trial in range(40):
        dense_case(fixed, rng, trial)
        dense_cases += 1
    controls = sum(failure_controls(program) for program in (star(6), fixed))
    # With several dirty roots, three distinct injection axes can sum to zero.
    # Thus >=2 is necessary, but an even source-call count is NOT necessary.
    excursion = (
        ("X", 0, 1), ("X", 1, 0), ("X", 0, 1), ("B", 0, 0),
        ("X", 1, 0), ("X", 0, 1), ("B", 0, 0), ("X", 1, 0), ("B", 0, 0),
    )
    positive = star(5)
    odd = replace(positive, operations=excursion + positive.operations)
    receipt["odd_source_positive_control"] = replay(odd)
    require(receipt["odd_source_positive_control"]["source_multiplicities"][0] == 5, "odd source control")
    receipt["dense_cases"] = dense_cases
    receipt["rejected_mutations"] = controls
    # Preserve every existing paired-call control. The additional one-root
    # baseline has separate omission and valid-label controls under its wider
    # even-readout contract, rather than disabling the star's paired checks.
    extra = extra_readout_baseline(6)
    extra_controls = 0
    for at, (tag, label, port) in enumerate(extra.operations):
        wrong_label = (label + 1) % 6 if tag == "B" else label % 63 + 1
        for edited in (
            extra.operations[:at] + extra.operations[at + 1 :],
            extra.operations[:at] + ((tag, wrong_label, port),) + extra.operations[at + 1 :],
        ):
            try:
                replay(replace(extra, operations=edited), minimal_sources=True, paired_readouts=False)
            except ValueError:
                extra_controls += 1
            else:
                raise ValueError("accepted corrupted extra-readout program")
    receipt["extra_readout_rejected_mutations"] = extra_controls
    # Exact finite corroboration of the all-n counting proof in the README.
    # 17^8 < 2*16^8 bounds the binomial volume without floating-point entropy.
    require(17**8 < 2 * 16**8, "binomial volume proof constant")
    for n in range(4, 65):
        volume = sum(comb(2 * n, i) for i in range(n // 8 + 1))
        require(volume < 1 << (n - 1), "low-readout subset volume")
    receipt["readout_bound_controls"] = {"n_min": 4, "n_max": 64, "exact_cases": 61}
    # A repeated pair at one boundary contributes zero, so this equivalent
    # program must pass semantic replay even though its invoice is larger.
    zero_pair = (("A", 1, 0), ("A", 1, 0))
    enlarged = replay(replace(extra, operations=zero_pair + extra.operations),
                      minimal_sources=True, paired_readouts=False)
    require(enlarged["readouts"] == receipt["extra_readout"][2]["readouts"] + 2,
            "neutral extra-readout pair positive control")
    receipt["closed_word_census"] = census()
    path = Path(__file__).with_name("EXPECTED.json")
    if sys.argv[1:]:
        path.write_text(json.dumps(receipt, indent=2) + "\n")
    else:
        # JSON encodings distinguish true/1 and 1.0/1; ordinary Python equality
        # would accept these type corruptions in an otherwise identical bill.
        stored = json.dumps(json.loads(path.read_text()), sort_keys=True, separators=(",", ":"))
        actual = json.dumps(receipt, sort_keys=True, separators=(",", ":"))
        require(stored == actual, "regression receipt mismatch")
    print(f"PASS_SCALABLE_DIRTY_CONNECTORS n=4..10 dense={dense_cases} rejected={controls} "
          f"extra_rejected={extra_controls} fixed_port=8")


if __name__ == "__main__":
    main()
