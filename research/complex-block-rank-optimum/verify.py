"""Check the source-bound premises of the block moment theorem."""

import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction
import gzip
import hashlib
import itertools
import json
import math
from pathlib import Path


HERE = Path(__file__).resolve().parent
BASES = (592, 600, 608, 624, 632, 640, 648, 656, 672, 680, 688, 696)


def f2_basis(values):
    basis = {}
    for value in values:
        while value:
            pivot = value.bit_length()
            if pivot in basis:
                value ^= basis[pivot]
            else:
                basis[pivot] = value
                break
    return tuple(basis[p] for p in sorted(basis, reverse=True))


def rank(values):
    return len(f2_basis(values))


def contains(frame, sub):
    return rank(frame + sub) == rank(frame)


def qrank(rows):
    rows = [list(map(Fraction, row)) for row in rows]
    if not rows:
        return 0
    pivot = 0
    for column in range(len(rows[0])):
        index = next((i for i in range(pivot, len(rows)) if rows[i][column]), None)
        if index is None:
            continue
        rows[index], rows[pivot] = rows[pivot], rows[index]
        factor = rows[pivot][column]
        rows[pivot] = [x / factor for x in rows[pivot]]
        for i in range(pivot + 1, len(rows)):
            factor = rows[i][column]
            rows[i] = [x - factor * y for x, y in zip(rows[i], rows[pivot])]
        pivot += 1
        if pivot == len(rows):
            break
    return pivot


def require(condition, message):
    if not condition:
        raise ValueError(message)


def scalar(gate, rows):
    if gate[0] == "add":
        _, dst, src, numerator, denominator, _ = gate
        coefficient = Fraction(numerator, denominator)
        rows[dst] = [a + coefficient * b for a, b in zip(rows[dst], rows[src])]
    elif gate[0] == "scale":
        _, dst, numerator, denominator, _ = gate
        rows[dst] = [Fraction(numerator, denominator) * a for a in rows[dst]]
    else:
        raise ValueError(f"Unknown scalar gate: {gate[0]}")


def incident(gate):
    return gate[1:3] if gate[0] == "add" else gate[1:2]


def canonical(word):
    if "frames" in word:
        return word
    frames = []
    keys = {}

    def frame(values):
        key = tuple(values)
        if key not in keys:
            keys[key] = len(frames)
            frames.append(list(values))
        return keys[key]

    count = 2 * len(word["ports"]) + word["report"]["R"]
    start = [frame([p]) for p in word["ports"]] + [frame([])] * (count - len(word["ports"]))
    for r, f in word["start_extra"].items():
        start[int(r)] = frame(f)
    full = frame([1 << i for i in range(9)])
    final = [full] * count
    for j, p in enumerate(word["ports"]):
        final[len(word["ports"]) + j] = frame(f2_basis(x for x in range(512) if (x & p).bit_count() % 2 == 0))
    for r, f in word["helper_final"].items():
        final[int(r)] = frame(f)
    result = {s: [g[:-1] + [frame(g[-1])] for g in word[s]] for s in ("A", "B")}
    result.update(start=start, final=final, frames=frames, ports=word["ports"],
                  cut=word["cut"], precondition=word["precondition"])
    return result


def frame_states(word):
    state = word["start"].copy()
    frames = word["frames"]
    for gate in word["A"]:
        for register in incident(gate):
            require(contains(frames[gate[-1]], frames[state[register]]), "A frame descends")
            state[register] = gate[-1]
    states = []
    for gate in word["B"]:
        states.append(state.copy())
        for register in incident(gate):
            require(contains(frames[gate[-1]], frames[state[register]]), "B frame descends")
            state[register] = gate[-1]
    states.append(state.copy())
    return states


def determinant(matrix):
    """Use the integer Bareiss identity after row denominator clearing."""
    if not matrix:
        return Fraction(1)
    integers = []
    scale = 1
    for row in matrix:
        denominator = math.lcm(*(Fraction(x).denominator for x in row))
        scale *= denominator
        integers.append([int(Fraction(x) * denominator) for x in row])
    previous = sign = 1
    for k in range(len(integers) - 1):
        pivot = next((i for i in range(k, len(integers)) if integers[i][k]), None)
        if pivot is None:
            return Fraction(0)
        if pivot != k:
            integers[k], integers[pivot] = integers[pivot], integers[k]
            sign = -sign
        value = integers[k][k]
        for i in range(k + 1, len(integers)):
            for j in range(k + 1, len(integers)):
                numerator = integers[i][j] * value - integers[i][k] * integers[k][j]
                require(numerator % previous == 0, "Bareiss division is not exact")
                integers[i][j] = numerator // previous
            integers[i][k] = 0
        previous = value
    return Fraction(sign * integers[-1][-1], scale)


def gram_rank(rows):
    """A rational Gram matrix has the same rank as its row matrix."""
    gram = [[sum(a * b for a, b in zip(x, y)) for y in rows] for x in rows]
    for size in range(len(rows), 0, -1):
        for indices in itertools.combinations(range(len(rows)), size):
            if determinant([[gram[i][j] for j in indices] for i in indices]):
                return size
    return 0


def span_set(values):
    """Enumerate the binary span without a pivot basis."""
    result = {0}
    for value in values:
        result |= {x ^ value for x in result}
    return result


def prefix_witness(word, registers, inputs, first_input, correction):
    """Bind all sixteen boundary values to the actual scalar prefix."""
    count = len(word["start"])
    ports = len(word["ports"])
    targets = set(range(ports, 2 * ports))
    cut = word["cut"]
    require(all(set(incident(g)) <= targets for g in word["precondition"]),
            "The preconditioner changes an original source or helper")
    require(all(g[0] == "add" and g[1] in targets and g[2] not in targets for g in cut),
            "The copied-centre cut is not a shear on the main arrays")
    removed = set(correction)
    prefix = word["A"] + cut + [g for i, g in enumerate(word["B"][:first_input]) if i not in removed]
    for gate in prefix:
        require(gate[0] in ("add", "scale"), "A prefix gate is outside the scalar alphabet")
        require(gate[2 if gate[0] == "scale" else 3] != 0, "A prefix scalar is zero")
        if gate[0] == "add":
            require(gate[1] != gate[2], "A prefix addition has equal source and target")
    variables = registers + inputs
    pulled = [{r: Fraction(1)} for r in variables]
    for gate in reversed(prefix):
        dst = gate[1]
        if gate[0] == "add":
            src, coefficient = gate[2], Fraction(gate[3], gate[4])
            for row in pulled:
                if dst in row:
                    row[src] = row.get(src, Fraction(0)) + coefficient * row[dst]
                    if not row[src]:
                        del row[src]
        else:
            coefficient = Fraction(gate[2], gate[3])
            for row in pulled:
                if dst in row:
                    row[dst] *= coefficient
    dense = [[row.get(i, Fraction(0)) for i in range(count)] for row in pulled]
    reduced = [row.copy() for row in dense]
    columns = []
    for column in range(count):
        pivot = len(columns)
        index = next((i for i in range(pivot, 16) if reduced[i][column]), None)
        if index is None:
            continue
        reduced[pivot], reduced[index] = reduced[index], reduced[pivot]
        value = reduced[pivot][column]
        reduced[pivot] = [x / value for x in reduced[pivot]]
        for i in range(pivot + 1, 16):
            factor = reduced[i][column]
            if factor:
                reduced[i] = [x - factor * y for x, y in zip(reduced[i], reduced[pivot])]
        columns.append(column)
        if len(columns) == 16:
            break
    require(len(columns) == 16, "The sixteen interface values are not independent")
    require(all(c < ports or c in registers for c in columns),
            "The independence witness uses a target or an exterior dirty helper")
    require(sum(c < ports for c in columns) == 8,
            "The witness does not use eight original source columns")
    minor = [[row[j] for j in columns] for row in dense]
    det = determinant(minor)
    require(det != 0, "The interface minor is singular")
    forward = [[Fraction(int(r == c)) for c in columns] for r in range(count)]
    for gate in prefix:
        scalar(gate, forward)
    require([forward[r] for r in variables] == minor, "The forward prefix and pullback minor differ")
    return {"boundary": "before-inputs-with-helper-correction-deferred",
            "registers": variables, "initial_scalar_columns": columns,
            "minor": [[str(x) for x in row] for row in minor], "determinant": str(det),
            "removed_correction_indices": sorted(removed), "scalar_prefix_length": len(prefix)}


def block(word, states, base):
    registers = list(range(base, base + 8))
    regset = set(registers)
    frames = word["frames"]
    gates = word["B"]
    inner = [(i, g) for i, g in enumerate(gates) if g[0] == "add" and g[1] in regset and g[2] in regset]
    all_incoming = [(i, g) for i, g in enumerate(gates) if g[0] == "add" and g[1] in regset and g[2] not in regset]
    incoming = [(i, g) for i, g in all_incoming if rank(frames[g[-1]]) > 1]
    outgoing = [(i, g) for i, g in enumerate(gates) if g[0] == "add" and g[1] not in regset and g[2] in regset]
    require(len(incoming) == 8, "There must be eight input gates")
    require(len({g[1] for _, g in incoming}) == 8, "There must be eight input recipients")
    require(len({g[2] for _, g in incoming}) == 8, "There must be eight distinct input arrays")
    first_input = incoming[0][0]
    last_input = incoming[-1][0]
    require(last_input - first_input == 7, "The input gates must form one segment")
    correction = [(i, g) for i, g in inner if i < first_input]
    require(correction, "The block must have a correction")
    start = correction[0][0]
    require(all(i < start for i, g in all_incoming if (i, g) not in incoming), "An additional input occurs after the module starts")
    early = [(i, g) for i, g in outgoing if i < start]
    late = [(i, g) for i, g in outgoing if i > last_input]
    require(len(early) + len(late) == len(outgoing), "An output lies inside the correction or input segment")
    require(len(late) == 8, "There must be eight late output gates")
    targets = sorted({g[1] for _, g in late})
    require(len(targets) == 4, "There must be four output targets")
    require(all(not (g[0] == "scale" and g[1] in targets) and
                not (g[0] == "add" and g[2] in targets)
                for g in gates[late[0][0]:]), "A late target is scaled or read by the exterior")
    initial = {r: frames[states[start][r]] for r in registers}
    low = [r for r in registers if len(initial[r]) == 1]
    high = [r for r in registers if len(initial[r]) > 1]
    require(len(low) == len(high) == 4, "There must be four low and four high helpers")
    common = initial[high[0]]
    u = rank(common)
    require(u in (4, 5), "The common frame must have rank four or five")
    require(all(contains(common, initial[r]) and contains(initial[r], common) for r in high), "The high frames differ")
    require(all(contains(common, initial[r]) for r in low), "A low frame is outside the common frame")
    require(all(contains(common, frames[g[-1]]) for _, g in correction), "A correction gate is above the common frame")
    require(all(contains(frames[g[-1]], common) for _, g in correction), "A correction gate is below the common frame")
    for i in range(start, first_input):
        if regset.intersection(incident(gates[i])):
            require(set(incident(gates[i])) <= regset, "The correction cannot move past an exterior event")

    input_frames = [frames[g[-1]] for _, g in incoming]
    for (index, gate), frame in zip(incoming, input_frames):
        require(rank(frame) in (5, 6) and contains(frame, common), "An input frame has the wrong rank or common subspace")
        require(contains(frames[states[first_input][gate[2]]], frame), "An external input is not ready at its declared frame")
        require(contains(frame, frames[states[index][gate[2]]]), "An external input has advanced beyond its declared frame")
    require(all(not contains(a, b) and not contains(b, a) for a, b in itertools.combinations(input_frames, 2)), "Two input frames are comparable")
    entry_indices = [next(i for i, g in late if g[1] == t) for t in targets]
    target_entry = [frames[states[i][t]] for i, t in zip(entry_indices, targets)]
    target_caps = [frames[word["final"][t]] for t in targets]
    require(all(rank(f) in (7, 8) for f in target_entry), "A target entry frame does not have rank seven or eight")
    require(all(rank(f) == 8 for f in target_caps), "A target cap does not have rank eight")
    require(all(rank(a + b) == 9 for a, b in itertools.combinations(target_caps, 2)), "Two target caps coincide")
    require(all(rank(f + g) >= 8 for f in input_frames for g in target_entry), "An input can reach a target below rank eight")

    variables = registers + [g[2] for _, g in incoming]
    require(len(set(variables)) == 16, "The sixteen inputs are not distinct arrays")
    rows = {r: [Fraction(int(i == j)) for i in range(16)] for j, r in enumerate(variables)}
    rows.update({t: [Fraction(0)] * 16 for t in targets})
    for i, gate in enumerate(gates):
        if i >= start and regset.intersection(incident(gate)):
            require(set(incident(gate)) <= set(rows), "An undeclared array occurs in the block")
            scalar(gate, rows)
    output = [rows[t] for t in targets]
    high_indices = [registers.index(r) for r in high]
    require(all(row[j] == 0 for row in output for j in high_indices), "A high dirty input reaches a target")
    q = [row[8:] for row in output]
    require(qrank(q) == 4, "The injection output matrix must have rank four")
    require(all(sum(row[j] != 0 for row in q) == 2 for j in range(8)), "An input does not need two distinct output targets")
    require(all(qrank([[v for i, v in enumerate(row) if i != j] for row in q]) == 4 for j in range(8)), "The kernel has a zero coordinate")
    projection_ranks = Counter()
    for size in range(1, 5):
        for selected in itertools.combinations(range(8), size):
            complement = [j for j in range(8) if j not in selected]
            projection_rank = size - 4 + qrank([[row[j] for j in complement] for row in q])
            require(projection_rank >= (3 * size + 3) // 4, "A kernel coordinate projection is too small")
            projection_ranks[(size, projection_rank)] += 1

    spectrum = Counter()
    kernel_frames = {}
    for mask in range(1, 256):
        indices = [j for j in range(8) if mask >> j & 1]
        frame = [v for j in indices for v in input_frames[j]]
        frame_rank = rank(frame)
        restricted = [[row[j] for j in indices] for row in q]
        matrix_rank = qrank(restricted)
        require(gram_rank(restricted) == matrix_rank, "The rational rank methods disagree")
        require(len(span_set(frame)) == 1 << frame_rank, "The binary span methods disagree")
        spectrum[(frame_rank, len(indices), matrix_rank)] += 1
        if frame_rank <= 6:
            require(matrix_rank == len(indices), f"A kernel is present below rank seven: {base}, {mask}")
        if frame_rank == 7 and matrix_rank < len(indices):
            eligible = [j for j, cap in enumerate(target_caps) if contains(cap, frame)]
            require(eligible == [j for j, cap in enumerate(target_caps) if span_set(frame) <= span_set(cap)],
                    "The cap containment methods disagree")
            require(len(eligible) <= 1, "A rank-seven kernel can reach two target caps")
            closure = tuple(j for j, f in enumerate(input_frames) if contains(frame, f))
            require(all(rank(input_frames[j]) == 5 for j in closure), "A rank-six input lies in a rank-seven kernel frame")
            kernel_frames[closure] = {"indices": list(closure), "frame": list(f2_basis(frame)),
                                      "eligible_targets": [targets[j] for j in eligible]}

    profile = Counter()
    current = initial.copy()
    for i, gate in enumerate(gates):
        if i >= start:
            for r in regset.intersection(incident(gate)):
                delta = rank(frames[gate[-1]]) - rank(current[r])
                require(delta >= 0 and contains(frames[gate[-1]], current[r]), "A helper frame descends")
                if delta:
                    profile[delta] += 1
                current[r] = frames[gate[-1]]
    for r in registers:
        require(rank(frames[word["final"][r]]) == 9, "A helper does not end at the full frame")
        delta = 9 - rank(current[r])
        if delta:
            profile[delta] += 1
    expected = Counter({1: 24, 2: 8, 3: 4}) if u == 4 else Counter({1: 32, 4: 4})
    require(profile == expected, f"The selected profile does not attain the proposed floor: {base}, {profile}")
    return {"base": base, "helpers": registers, "low": low, "high": high,
            "common_frame": common, "common_rank": u,
            "first_correction": start, "first_input": first_input,
            "input_gate_indices": [i for i, _ in incoming],
            "output_gate_indices": [i for i, _ in late],
            "output_entry_indices": entry_indices,
            "R": [[str(row[registers.index(r)]) for r in low] for row in output],
            "independence_witness": prefix_witness(word, registers, [g[2] for _, g in incoming],
                                                    first_input, [i for i, _ in correction]),
            "input_arrays": [g[2] for _, g in incoming], "input_frames": input_frames,
            "target_arrays": targets, "target_entry_frames": target_entry,
            "target_caps": target_caps, "Q": [[str(x) for x in row] for row in q],
            "profile": dict(sorted(profile.items())),
            "kernel_projection_ranks": [{"size": k[0], "rank": k[1], "count": v}
                                        for k, v in sorted(projection_ranks.items())],
            "rank_seven_kernel_frames": [v for _, v in sorted(kernel_frames.items())],
            "subset_spectrum": [{"frame_rank": k[0], "size": k[1], "matrix_rank": k[2], "count": v}
                                for k, v in sorted(spectrum.items())]}


def load_payload(entry, data=None):
    if data is None:
        data = (HERE / entry["file"]).read_bytes()
    require(hashlib.sha256(data).hexdigest() == entry["sha256"], "A frozen input hash differs")
    payload = gzip.decompress(data)
    require(hashlib.sha256(payload).hexdigest() == entry["payload_sha256"], "An input payload hash differs")
    return json.loads(payload)


def load_source(entry, data=None):
    return canonical(load_payload(entry, data))


def failure_controls(word, states, first_block, entry):
    controls = []

    def reject(name, operation, message):
        try:
            operation()
        except ValueError as error:
            require(str(error) == message, f"The {name} control failed for another reason: {error}")
            controls.append({"name": name, "rejection": message})
        else:
            raise ValueError(f"The {name} control was accepted")

    changed = deepcopy(word)
    i = first_block["first_correction"]
    changed["B"][i][3] += changed["B"][i][4]
    reject("wrong-helper-correction", lambda: block(changed, states, BASES[0]),
           "A high dirty input reaches a target")
    changed = deepcopy(word)
    i = first_block["first_input"]
    changed["B"][i + 1][2] = changed["B"][i][2]
    reject("duplicate-external-input", lambda: block(changed, states, BASES[0]),
           "There must be eight distinct input arrays")
    changed = deepcopy(word)
    changed["final"][BASES[0]] = changed["final"][first_block["target_arrays"][0]]
    reject("missing-full-helper-end", lambda: block(changed, states, BASES[0]),
           "A helper does not end at the full frame")
    data = bytearray((HERE / entry["file"]).read_bytes())
    data[-1] ^= 1
    reject("changed-frozen-input", lambda: load_source(entry, data), "A frozen input hash differs")
    return controls


def orientation_contract(entry):
    programs = load_payload(entry)
    forward, backward = programs["forward"], programs["backward"]
    climbs = [[e for e in program if e[0] == "climb"] for program in (forward, backward)]
    require(climbs[0] == climbs[1], "The provider orientations have different frame climbs")
    profiles = []
    scalars = []
    for program in (forward, backward):
        profile = Counter()
        operations = []
        phase = None
        for event in program:
            if event[0] == "phase":
                phase = event[1]
            elif event[0] == "climb":
                profile[event[5]] += 1
            elif event[0] == "center":
                profile[event[4]] += 1
            elif event[0] == "scalar" and phase != "centers":
                operations.append(event)
        profiles.append(profile)
        scalars.append(operations)
    require(profiles[0] == profiles[1] == Counter({1:2412, 2:418, 3:432, 4:142, 5:82, 8:8}),
            "The two native orientation profiles differ")
    require(len(scalars[0]) == len(scalars[1]), "The two orientation scalar counts differ")
    for fwd, bwd in zip(*scalars):
        gate = deepcopy(fwd[1])
        if gate[0] == "add":
            gate[1], gate[2] = gate[2], gate[1]
            gate[3] = -gate[3]
        elif gate[0] == "scale":
            gate[2], gate[3] = gate[3], gate[2]
        else:
            raise ValueError("An orientation scalar is outside the dual alphabet")
        require(bwd == ["scalar", gate, fwd[2]], "The backward scalar is not the retained inverse-transpose dual")
    return {"file": entry["file"], "source_sha256": entry["payload_sha256"],
            "contract": "same-order-inverse-transpose-from-one-canonical-word",
            "equal_climb_events": len(climbs[0]), "dual_noncentre_scalars": len(scalars[0]),
            "equal_complete_profile": dict(sorted(profiles[0].items()))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-certificate", action="store_true",
                        help="Write the exact interface certificate after all checks pass.")
    args = parser.parse_args()
    manifest = json.loads((HERE / "INPUTS.json").read_text())
    receipts = []
    expected_totals = ({1: 328, 2: 56, 3: 28, 4: 20},
                       {1: 304, 2: 80, 3: 40, 4: 8},
                       {1: 296, 2: 88, 3: 44, 4: 4})
    require([e["file"] for e in manifest["inputs"]] ==
            ["inputs/selected.json.gz", "inputs/pr1319-base.json.gz", "inputs/pr1319-extra.json.gz"],
            "The source set differs")
    for entry, expected in zip(manifest["inputs"], expected_totals):
        word = load_source(entry)
        states = frame_states(word)
        blocks = [block(word, states, base) for base in BASES]
        profile = Counter()
        for item in blocks:
            profile.update(item["profile"])
        require(dict(profile) == expected, "The total attained moment differs")
        require(any(b["rank_seven_kernel_frames"] for b in blocks),
                "The rank-seven retirement case is no longer exercised")
        receipts.append({"file": entry["file"], "source_sha256": entry["payload_sha256"],
                         "blocks": blocks, "total_profile": dict(sorted(profile.items())),
                         "subsets": 255 * len(blocks),
                         "controls": failure_controls(word, states, blocks[0], entry)})
    certificate = {"schema_version": 1, "status": "PASS_FIXED_BLOCK_MOMENT_PREMISES",
                   "sources": receipts, "source_block_pairs": 36, "subset_checks": 9180,
                   "independence_minors": 36, "failure_controls": 12,
                   "orientation_contract": orientation_contract(manifest["orientation_program"])}
    output = json.dumps(certificate, indent=2, sort_keys=True) + "\n"
    target = HERE / "CERTIFICATE.json"
    if args.write_certificate:
        target.write_text(output)
    else:
        require(json.loads(target.read_text()) == json.loads(output), "The interface certificate differs")
    print("PASS_FIXED_BLOCK_MOMENT_PREMISES blocks=36 subsets=9180 minors=36 controls=12")
    print("The finite checks support PROOF.md; they are not a formal proof of the all-length theorem.")


if __name__ == "__main__":
    main()
