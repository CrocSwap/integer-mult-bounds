#!/usr/bin/env python3
"""Replay the finite premises and controls of the Eisenstein message bound.

Python 3.10+, standard library. Checks stay active under python -O.
"""

import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import random
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import geometry as geo

SEED = 41


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def source_pins():
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    root = HERE.parent.parent
    for item in manifest["files"]:
        path = (root / item["path"]).resolve()
        geo.require(path.is_relative_to(root), "source path escapes repository")
        geo.require(hashlib.sha256(path.read_bytes()).hexdigest() == item["sha256"], "source hash mismatch: " + item["path"])
    return hashlib.sha256((HERE / "SOURCES.json").read_bytes()).hexdigest()


def check_clique(mask, adjacent):
    geo.require(mask > 0 and mask < 1 << len(adjacent), "invalid clique mask")
    for i in geo.bits(mask):
        geo.require(mask & ~(adjacent[i] | 1 << i) == 0, "clique contains orthogonal lines")


def frame_partition(adjacent):
    """A seeded exact cover by orthogonal four-frames; used only for controls."""
    full = (1 << len(adjacent)) - 1
    orthogonal = tuple(full ^ (1 << i) ^ adjacent[i] for i in range(len(adjacent)))
    frames = list(geo.maximal_cliques(orthogonal))
    geo.require(len(frames) == 40 and {f.bit_count() for f in frames} == {4}, "orthogonal frame census changed")
    random.Random(SEED).shuffle(frames)
    options = [[f for f in frames if f & 1 << i] for i in range(len(adjacent))]

    def search(remaining):
        if not remaining:
            return []
        i = min(geo.bits(remaining), key=lambda i: sum(f & remaining == f for f in options[i]))
        for f in options[i]:
            if f & remaining == f:
                tail = search(remaining ^ f)
                if tail is not None:
                    return [f] + tail
        return None

    result = search(full)
    geo.require(result is not None and sum(result) == full, "no disjoint frame partition")
    return result


def projected_value(values, mask):
    return tuple(values[t] for t in geo.bits(mask))


def exercise_code(widths, messages, side, decoder, transcript_cliques=()):
    """Exhaust the declared finite input product and every listed transcript.

    Each message is (source mask, reader mask, q, encoder). The dependency
    check is semantic: equal source inputs must give equal message values.
    """
    geo.require(len(widths) == 40 and all(isinstance(b, int) and b >= 0 for b in widths), "bad input widths")
    for sources, readers, width, _ in messages:
        geo.require(0 <= sources < 1 << 40 and 0 <= readers < 1 << 40, "bad message support")
        geo.require(isinstance(width, int) and width >= 0, "bad message width")
    active = sum(1 << t for t, b in enumerate(widths) if b)
    nbits = sum(widths)
    geo.require(nbits <= 12, "truth-table control exceeds its stated domain")
    dependencies = [{} for _ in messages]
    projections = sorted({q & active for q in transcript_cliques if q & active})
    transcripts = [{} for _ in projections]
    for packed in range(1 << nbits):
        remaining = packed
        values = []
        for width in widths:
            values.append(remaining & ((1 << width) - 1))
            remaining >>= width
        outputs = []
        for j, (sources, readers, width, encoder) in enumerate(messages):
            value = encoder(values)
            geo.require(0 <= value < 1 << width, "encoded message exceeds declared width")
            key = projected_value(values, sources)
            old = dependencies[j].setdefault(key, value)
            geo.require(old == value, "encoder depends on undeclared source")
            outputs.append(value)
        for t in geo.bits(active):
            received = {j: outputs[j] for j, msg in enumerate(messages) if msg[1] & 1 << t}
            known = {u: values[u] for u in geo.bits(side[t])}
            geo.require(decoder(t, received, known) == values[t], "zero-error decoding failed")
        for k, clique in enumerate(projections):
            outside = projected_value(values, active & ~clique)
            heard = tuple(outputs[j] for j, msg in enumerate(messages) if msg[0] & clique and msg[1] & clique)
            inside = projected_value(values, clique)
            old = transcripts[k].setdefault((outside, heard), inside)
            geo.require(old == inside, "conditional transcript is not injective")
    return {"inputs": 1 << nbits, "clique_projections": len(projections), "conditional_transcripts": sum(len(x) for x in transcripts)}


def demand_bound(widths, maximal):
    """An integer lower bound, using all maximal cliques for unequal demands."""
    geo.require(len(widths) == 40 and all(isinstance(b, int) and b >= 0 for b in widths), "bad demand widths")
    weighted = (11 * sum(widths) + 19) // 20
    concentrated = max(sum(widths[t] for t in geo.bits(q)) for q in maximal)
    return max(weighted, concentrated)


def controls(spans, adjacent, maximal, maximum, full_hits):
    rejected = []

    def reject(name, action):
        try:
            action()
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError("negative control accepted: " + name)

    partition = frame_partition(adjacent)
    selected = partition[:3]
    active = selected[0] | selected[1] | selected[2]
    widths = [int(bool(active & 1 << t)) for t in range(40)]
    side = [(active & ~(adjacent[t] | 1 << t)) for t in range(40)]
    frame_of = {t: j for j, frame in enumerate(selected) for t in geo.bits(frame)}

    def nonlinear(values):
        z = [sum(values[t] for t in geo.bits(frame)) % 2 for frame in selected]
        return z[0] | z[1] << 1 | (z[2] ^ (z[0] & z[1])) << 2

    def decode(t, received, known):
        y = received[0]
        z = [y & 1, (y >> 1) & 1, ((y >> 2) & 1) ^ ((y & 1) & ((y >> 1) & 1))]
        frame = selected[frame_of[t]]
        return z[frame_of[t]] ^ (sum(known[u] for u in geo.bits(frame & ~(1 << t))) % 2)

    message = (active, active, 3, nonlinear)
    geo.require(all(side[t] & (adjacent[t] | 1 << t) == 0 for t in geo.bits(active)), "illegal side information in nonlinear control")
    cliques = list(maximum) + [1 << t for t in range(40)]
    nonlinear_check = exercise_code(widths, [message], side, decode, cliques)
    support_basis = geo.basis([row for t in geo.bits(active) for row in spans[t]])
    rank = geo.pairing_rank(support_basis, support_basis)
    geo.require(rank == 4, "nonlinear example support rank changed")
    geo.require(3 * rank == 12 and demand_bound(widths, maximal) == 7, "nonlinear example bound changed")
    # A mixed Boolean derivative certifies genuine nonlinearity of the encoder.
    a, b = next(geo.bits(selected[0])), next(geo.bits(selected[1]))
    zero = [0] * 40
    va, vb, vab = zero.copy(), zero.copy(), zero.copy()
    va[a] = vb[b] = vab[a] = vab[b] = 1
    geo.require(nonlinear(zero) ^ nonlinear(va) ^ nonlinear(vb) ^ nonlinear(vab) == 4, "example is not nonlinear")
    reject("message width reduced from three to two", lambda: exercise_code(widths, [(active, active, 2, nonlinear)], side, decode))
    reject("one source omitted from the declared support", lambda: exercise_code(widths, [(active ^ (1 << a), active, 3, nonlinear)], side, decode))
    reject("third message bit dropped", lambda: exercise_code(widths, [(active, active, 3, lambda x: nonlinear(x) & 3)], side, decode))
    reject("message replaced by a constant", lambda: exercise_code(widths, [(active, active, 3, lambda x: 0)], side, decode))
    reject("nonlinear inverse correction omitted", lambda: exercise_code(widths, [message], side, lambda t, received, known: ((received[0] >> frame_of[t]) & 1) ^ (sum(known[u] for u in geo.bits(selected[frame_of[t]] & ~(1 << t))) % 2)))

    # Unequal-width positive control on an orthogonal four-frame: one XOR
    # message per active bit plane, with every plane's source/reader support
    # equal to the ports that actually have that bit.
    first = list(geo.bits(partition[0]))
    heterogeneous = [0] * 40
    for t, width in zip(first, [0, 1, 2, 3]):
        heterogeneous[t] = width
    msgs = []
    for bit in range(3):
        support = sum(1 << t for t in first if heterogeneous[t] > bit)
        def encode_plane(values, bit=bit, support=support):
            return sum((values[t] >> bit) & 1 for t in geo.bits(support)) % 2
        msgs.append((support, support, 1, encode_plane))
    hetero_side = [(partition[0] & ~(1 << t)) if t in first else 0 for t in range(40)]
    geo.require(all(hetero_side[t] & (adjacent[t] | 1 << t) == 0 for t in first), "illegal side information in unequal-width control")
    def decode_heterogeneous(t, received, known):
        value = 0
        for bit in range(heterogeneous[t]):
            value |= (received[bit] ^ (sum((known[u] >> bit) & 1 for u in geo.bits(msgs[bit][0] & ~(1 << t))) % 2)) << bit
        return value
    hetero_check = exercise_code(heterogeneous, msgs, hetero_side, decode_heterogeneous, cliques)
    hetero_cost = sum(geo.pairing_rank(geo.basis([row for t in geo.bits(msg[0]) for row in spans[t]]), geo.basis([row for t in geo.bits(msg[1]) for row in spans[t]])) for msg in msgs)
    geo.require(hetero_cost == 6 and demand_bound(heterogeneous, maximal) == 4, "heterogeneous bound changed")

    # Assumption boundary, intentionally ACCEPTED as a code: extra
    # nonorthogonal side information defeats the claimed clique bound.
    q = maximum[0]
    boundary_widths = [int(bool(q & 1 << t)) for t in range(40)]
    boundary_message = (q, q, 1, lambda x: sum(x[t] for t in geo.bits(q)) % 2)
    extra_side = [q & ~(1 << t) for t in range(40)]
    boundary = exercise_code(boundary_widths, [boundary_message], extra_side, lambda t, heard, known: heard[0] ^ (sum(known.values()) % 2))
    qb = geo.basis([row for t in geo.bits(q) for row in spans[t]])
    geo.require(geo.pairing_rank(qb, qb) == 4 < demand_bound(boundary_widths, maximal) == 7, "side-information boundary changed")
    reject("nonorthogonal side information passed off as legal", lambda: geo.require(all(extra_side[t] & adjacent[t] == 0 for t in geo.bits(q)), "extra side information is not orthogonal"))
    reject("nonlinear message charged once instead of per bit", lambda: geo.require(rank >= demand_bound(widths, maximal), "undercharged three-bit message violates bound"))
    mate = next(i for i in range(1, 40) if not adjacent[0] & 1 << i)
    reject("orthogonal pair admitted as a clique", lambda: check_clique(1 | 1 << mate, adjacent))
    reject("Eisenstein charge not converted to rational units", lambda: geo.require(len(geo.basis(spans[0])) == geo.pairing_rank(spans[0], spans[0]), "missing factor of two"))
    reject("maximum-clique weights rounded upward", lambda: geo.require(24 * 40 + full_hits <= 959 * 4, "full/full primal inequality violated"))
    reject("singleton weights omitted but demand coefficient retained", lambda: geo.require(Fraction(504, 960) == Fraction(11, 20), "missing singleton weight"))
    reject("negative payload width", lambda: demand_bound([-1] + [0] * 39, maximal))
    return {
        "negative_controls": rejected,
        "orthogonal_partition": partition,
        "nonlinear_12_port_code": {**nonlinear_check, "active_mask": active, "message_width": 3, "copy_charge": 12, "demand_bound": 7, "mixed_derivative": 4},
        "heterogeneous_0_1_2_3_code": {**hetero_check, "copy_charge": hetero_cost, "demand_bound": 4},
        "extra_nonorthogonal_side_information_boundary": {**boundary, "clique_mask": q, "copy_charge": 4, "excluded_model_bound": 7},
        "forty_port_product_extension": {"copy_charge": 40, "message_widths": [3] + [1] * 28, "proof": "12-port nonlinear code plus 28 independent uncoded bits; no exhaustive 2^40 claim"},
    }


def build_receipt():
    pins = source_pins()
    roots, rotation4, planes, reps, spans, orbits, adjacent = geo.make_geometry()
    maximal = geo.maximal_cliques(adjacent)
    for clique in maximal:
        check_clique(clique, adjacent)
    maximum = tuple(q for q in maximal if q.bit_count() == 7)
    geo.require(Counter(q.bit_count() for q in maximal) == {4: 90, 7: 2880}, "maximal-clique census changed")
    incidence = [sum(bool(q & 1 << t) for q in maximum) for t in range(40)]
    geo.require(set(incidence) == {504}, "demand coefficient is not uniform")
    geo.require(Fraction(1, 40) + Fraction(504, 960) == Fraction(11, 20), "wrong per-port demand weight")
    flat_list = geo.flats(spans)
    expected = {(0, 0): 1, (1, 1): 40, (2, 2): 240, (2, 4): 90, (3, 5): 360, (3, 12): 40, (4, 40): 1}
    geo.require(Counter((f[0], f[1].bit_count()) for f in flat_list) == expected, "flat census changed")
    spans_set = {f[2] for f in flat_list}
    for f in flat_list:
        for line in spans:
            geo.require(geo.basis(f[2] + line) in spans_set, "flat extension omitted")
    hit_masks = [sum(1 << k for k, q in enumerate(maximum) if q & f[1]) for f in flat_list]
    histogram, tight = Counter(), 0
    for i, f in enumerate(flat_list):
        for j in range(i, len(flat_list)):
            other = flat_list[j]
            hits = (hit_masks[i] & hit_masks[j]).bit_count()
            common = (f[1] & other[1]).bit_count()
            charge = geo.pairing_rank(f[2], other[2])
            geo.require(24 * common + hits <= 960 * charge, "weighted geometric inequality failed")
            histogram[(charge, common, hits)] += 1
            tight += int(24 * common + hits == 960 * charge)
    geo.require(sum(histogram.values()) == 298378, "flat-pair coverage changed")
    control_results = controls(spans, adjacent, maximal, maximum, len(maximum))
    geo.require(len(control_results["negative_controls"]) == 12, "negative-control count changed")
    return {
        "format": "eisenstein-fixed-support-message-bound-v1",
        "base_commit": "66849e1475c930fd7732b1a0067ffee7e1e95f60",
        "assignment_seed": SEED,
        "source_manifest_sha256": pins,
        "model": "fixed-support deterministic zero-error messages; independent bits; orthogonal side information; additive width times pairing rank",
        "bound": {"per_port_weight": "11/20", "equal_width_floor": "22b", "unequal_width_floor": "max(ceil(11*sum(b_t)/20), max_clique sum(b_t))", "rational_equal_width_floor": "44b"},
        "geometry": {"rotation4": rotation4, "a2_planes": planes, "representatives": reps, "root_orbits_sha256": digest(orbits), "roots_sha256": digest(roots), "nonorthogonal_neighbors": adjacent},
        "certificate": {"singleton_weight": "1/40", "seven_clique_weight": "1/960", "clique_incidence_per_port": incidence, "maximal_cliques": maximal, "flats": [{"rank": f[0], "mask": f[1], "generators": f[3]} for f in flat_list]},
        "coverage": {"flats": len(flat_list), "unordered_flat_pairs": sum(histogram.values()), "tight_pairs": tight, "one_line_extensions": len(flat_list) * 40, "pair_histogram": [[*key, value] for key, value in sorted(histogram.items())], "maximal_cliques": len(maximal), "seven_cliques": len(maximum)},
        "controls": control_results,
        "accounting": {"conditional_optimistic_deficit": "D/T <= b*(36*s-80)", "three_stage_upper_deficit": "28b (positive; no exclusion)", "cost_40b_example_deficit": "-80b"},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="write a verified receipt to a NEW path after all checks pass")
    args = parser.parse_args()
    receipt = build_receipt()
    expected = json.loads((HERE / "certificate.json").read_text())
    geo.require(canonical(receipt) == canonical(expected), "committed certificate differs from replay")
    if args.output:
        with args.output.open("x") as stream:
            json.dump(receipt, stream, indent=2, sort_keys=True)
            stream.write("\n")
    print("PASS_EISENSTEIN_MESSAGE_BOUND: 22b; unequal demands 11/20 plus clique bounds; 298378 flat pairs; 12 rejection controls; no new kappa")


if __name__ == "__main__":
    main()
