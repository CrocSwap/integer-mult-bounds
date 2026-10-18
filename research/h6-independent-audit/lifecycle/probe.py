#!/usr/bin/env python3
"""Finite arbitrary-dirt and common-frame lifecycle controls on PR606 labels.

No frozen program or scalar replay implementation is imported. NumPy is used
only to obtain the pinned geometry; all frames and scalar matrices are exact.
"""
from fractions import Fraction as Q
from pathlib import Path
import hashlib
import json
import platform
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "research/niemeier-lattices/code/e8_cubed.py"
sys.path.insert(0, str(SOURCE.parent))
import e8_cubed as geometry


def require(ok, message):
    if not ok:
        raise ValueError(message)


def basis(words):
    pivots = {}
    for word in words:
        value = int(word)
        for pivot in sorted(pivots, reverse=True):
            if value >> pivot & 1:
                value ^= pivots[pivot]
        if value:
            pivot = value.bit_length() - 1
            for old in list(pivots):
                if pivots[old] >> pivot & 1:
                    pivots[old] ^= value
            pivots[pivot] = value
    return tuple(pivots[p] for p in sorted(pivots, reverse=True))


def contained(small, large):
    return len(basis(small + large)) == len(large)


def perp(word):
    pivot = (word & -word).bit_length() - 1
    return basis((1 << bit) ^ ((1 << pivot) if word >> bit & 1 else 0)
                 for bit in range(17) if bit != pivot)


REGISTERS = ("s0", "s1", "t0", "t1", "a", "b")
INDEX = {register: i for i, register in enumerate(REGISTERS)}
FULL = basis(1 << bit for bit in range(17))
ZERO = ()


def add(dst, src, coefficient):
    return {"op": "add", "dst": dst, "src": src, "q": str(coefficient)}


def scale(register, coefficient):
    return {"op": "scale", "register": register, "q": str(coefficient)}


def climb(register, frame):
    return {"op": "climb", "register": register, "frame": list(frame)}


def evaluate(events, starts, ends, dual=False):
    registers = tuple(starts)
    index = {register: i for i, register in enumerate(registers)}
    frames = dict(starts)
    paths = {register: [] for register in registers}
    matrix = [[Q(i == j) for j in range(len(registers))] for i in range(len(registers))]
    for step, event in enumerate(events):
        if event["op"] == "climb":
            register, frame = event["register"], tuple(event["frame"])
            require(frame == basis(frame), f"step {step}: noncanonical frame")
            require(contained(frames[register], frame), f"step {step}: forbidden descent")
            increment = len(frame) - len(frames[register])
            if increment:
                paths[register].append(increment)
            frames[register] = frame
        elif event["op"] == "add":
            dst, src, coefficient = event["dst"], event["src"], Q(event["q"])
            require(frames[dst] == frames[src], f"step {step}: operands have different current frames")
            if dual:
                dst, src, coefficient = src, dst, -coefficient
            matrix[index[dst]] = [x + coefficient * y for x, y in zip(matrix[index[dst]], matrix[index[src]])]
        elif event["op"] == "scale":
            coefficient = Q(event["q"])
            require(coefficient != 0, "noninvertible scale")
            if dual:
                coefficient = 1 / coefficient
            row = index[event["register"]]
            matrix[row] = [coefficient * x for x in matrix[row]]
        else:
            raise ValueError("unknown operation")
    require(frames == ends, "wrong endpoint frames")
    return matrix, paths


def serialized(matrix):
    return [[str(value) for value in row] for row in matrix]


def expected(dual=False):
    matrix = [[Q(i == j) for j in range(6)] for i in range(6)]
    shear = ((1, 1), (1, -1))
    for target in range(2):
        for source in range(2):
            if dual:
                matrix[source][target + 2] = -shear[target][source]
            else:
                matrix[target + 2][source] = shear[target][source]
    return matrix


def main():
    roots, _, shell, profiles = geometry.construct_shell()
    ports = shell[(profiles & 4) == 0, :16]
    _, labels, fitting = geometry.binary_labels(roots, ports)
    require(len(ports) == 30960 and fitting["dimension"] == 17, "wrong geometry")
    source_indices = [0, next(i for i, label in enumerate(labels) if int(label) != int(labels[0]))]
    source_labels = [int(labels[i]) for i in source_indices]
    frame = basis(source_labels)
    require(len(frame) == 2, "rank two source span")
    targets = []
    for index, label in enumerate(labels):
        word = int(label)
        if all((word & source).bit_count() % 2 == 0 for source in source_labels):
            if not targets or word != int(labels[targets[0]]):
                targets.append(index)
                if len(targets) == 2:
                    break
    require(len(targets) == 2, "two target caps")
    target_labels = [int(labels[i]) for i in targets]
    caps = [perp(word) for word in target_labels]
    require(all(len(cap) == 16 and contained(frame, cap) for cap in caps), "legal target cap incidence")
    incidences = []
    for si in source_indices:
        for ti in targets:
            dot = int(ports[si] @ ports[ti])
            require(dot % 4 == 0 and (dot // 4) % 2 == 1, "actual odd lattice pairing")
            incidences.append({"source": si, "target": ti, "lattice_pairing": dot // 4,
                               "binary_dot": (int(labels[si]) & int(labels[ti])).bit_count() % 2})
    starts = dict(zip(REGISTERS, (basis([source_labels[0]]), basis([source_labels[1]]), ZERO, ZERO, ZERO, ZERO)))
    ends = dict(zip(REGISTERS, (FULL, FULL, caps[0], caps[1], FULL, FULL)))

    # Ordinary dirt a0 and b0 are precompensated while all targets/helpers
    # are at zero. No source may participate at this frame.
    compensation = [add("t0", "a", -1), add("t0", "b", -1),
                    add("t1", "a", -1), add("t1", "b", 1)]
    joins = [climb(register, frame) for register in REGISTERS]
    gather = [add("a", "s0", 1), add("b", "s1", 1)]
    walsh = [add("a", "b", 1), add("b", "a", "-1/2"), scale("b", -2)]
    scatter = [add("t0", "a", 1), add("t1", "b", 1)]
    terminal = [climb(register, FULL) for register in ("s0", "s1", "a", "b")]
    cleanup = [scale("b", "-1/2"), add("b", "a", "1/2"), add("a", "b", -1),
               add("b", "s1", -1), add("a", "s0", -1)]
    target_finish = [climb("t0", caps[0]), climb("t1", caps[1])]
    events = compensation + joins + gather + walsh + scatter + terminal + cleanup + target_finish
    forward, paths = evaluate(events, starts, ends)
    dual, dual_paths = evaluate(events, starts, ends, dual=True)
    require(forward == expected(), "forward arbitrary-dirt shear")
    require(dual == expected(True), "inverse-transpose arbitrary-dirt shear")
    require(paths == dual_paths, "orientation paths")

    # Here the actual selected I-K submatrix is [-1,1;1,-1]/16. Its
    # rank-one factorization gives a literal compensation subword with one
    # ordinary dirty helper. The four actual pairings above determine it.
    coefficient_matrix = [[Q(4 * int(ports[si] @ ports[ti] // 4) - int(ports[si] @ ports[ti] // 4) ** 3, 48)
                           for si in source_indices] for ti in targets]
    require(coefficient_matrix == [[Q(-1, 16), Q(1, 16)], [Q(1, 16), Q(-1, 16)]],
            "actual compensation submatrix")
    small_starts = {k: v for k, v in starts.items() if k != "b"}
    small_ends = {k: v for k, v in ends.items() if k != "b"}
    actual_events = [add("t0", "a", "1/16"), add("t1", "a", "-1/16")]
    actual_events += [climb(register, frame) for register in small_starts]
    actual_events += [add("a", "s0", 1), add("a", "s1", -1),
                     add("t0", "a", "-1/16"), add("t1", "a", "1/16")]
    actual_events += [climb(register, FULL) for register in ("s0", "s1", "a")]
    actual_events += [add("a", "s0", -1), add("a", "s1", 1)] + target_finish
    actual_forward, actual_paths = evaluate(actual_events, small_starts, small_ends)
    actual_dual, _ = evaluate(actual_events, small_starts, small_ends, dual=True)
    actual_expected = [[Q(i == j) for j in range(5)] for i in range(5)]
    actual_expected_dual = [[Q(i == j) for j in range(5)] for i in range(5)]
    for ti in range(2):
        for si in range(2):
            actual_expected[ti + 2][si] = coefficient_matrix[ti][si]
            actual_expected_dual[si][ti + 2] = -coefficient_matrix[ti][si]
    require(actual_forward == actual_expected and actual_dual == actual_expected_dual,
            "actual compensation arbitrary-dirt forward/dual identities")
    actual_uncompensated, _ = evaluate(actual_events[2:], small_starts, small_ends)
    require(actual_uncompensated[2][4] == Q(-1, 16) and actual_uncompensated[3][4] == Q(1, 16),
            "actual submatrix dirt leakage control")

    # Mutants use the identical independent replay, retaining all endpoint
    # checks. They test mathematical implications, not random samples.
    no_cleanup, _ = evaluate(compensation + joins + gather + walsh + scatter + terminal + target_finish, starts, ends)
    require(no_cleanup != expected(), "dropped cleanup must fail")
    missing_b_compensation = [event for i, event in enumerate(events) if i not in (1, 3)]
    leaked, _ = evaluate(missing_b_compensation, starts, ends)
    require(leaked[INDEX["t0"]][INDEX["b"]] == 1 and leaked[INDEX["t1"]][INDEX["b"]] == -1,
            "independent b dirt leaks despite cleanup")
    # After a has reached FULL, another gather from a source still at F
    # cannot be called scratch reuse. It is a different-label scalar add.
    illegal = compensation + joins + gather + walsh + scatter + [climb("a", FULL), add("a", "s0", 1)]
    try:
        evaluate(illegal, starts, ends)
    except ValueError as error:
        require("different current frames" in str(error), "reuse rejection reason")
        illegal_reason = str(error)
    else:
        raise ValueError("illegal FULL scratch reuse unexpectedly passed")
    try:
        evaluate(compensation + joins + [climb("a", ZERO)], starts, ends)
    except ValueError as error:
        require("forbidden descent" in str(error), "descent rejection reason")
        descent_reason = str(error)
    else:
        raise ValueError("ordinary descent unexpectedly passed")
    try:
        evaluate([add("a", "s0", 1)], starts, ends)
    except ValueError as error:
        require("different current frames" in str(error), "zero accumulator rejection reason")
        zero_load_reason = str(error)
    else:
        raise ValueError("source-frame injection into zero accumulator unexpectedly passed")

    result = {"status": "PASS_FINITE_DIRTY_WALSH_LIFECYCLE", "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              "python": platform.python_version(), "generator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "ports": [{"role": role, "index": i, "packed_label": int(labels[i]), "vector": ports[i].tolist()}
                        for role, i in zip(("s0", "s1", "t0", "t1"), source_indices + targets)],
              "incidences": incidences, "common_frame": list(frame), "common_frame_dimension": 2,
              "initial_frames": {k: list(v) for k, v in starts.items()},
              "final_frames": {k: list(v) for k, v in ends.items()},
              "events": events, "forward_scalar_matrix": serialized(forward), "inverse_transpose_scalar_matrix": serialized(dual),
              "path_increments": paths, "private_copy_descent_bill": 0,
              "total_local_rank_mass": sum(map(sum, paths.values())),
              "ordinary_helper_roles": 2,
              "actual_compensation_submatrix": {
                  "scope": "Literal I-K submatrix at the four recorded incidences, not an all-port word.",
                  "register_order": list(small_starts), "coefficient_matrix": serialized(coefficient_matrix),
                  "ordinary_helper_roles": 1, "events": actual_events,
                  "forward_scalar_matrix": serialized(actual_forward),
                  "inverse_transpose_scalar_matrix": serialized(actual_dual),
                  "omit_dirt_precompensation_control": serialized(actual_uncompensated),
                  "path_increments": actual_paths, "private_copy_descent_bill": 0,
                  "total_local_rank_mass": sum(map(sum, actual_paths.values()))},
              "negative_controls": {"drop_cleanup": serialized(no_cleanup), "omit_independent_b_dirt_compensation": serialized(leaked),
                                    "reuse_after_FULL": illegal_reason, "ordinary_descent_to_zero": descent_reason,
                                    "load_source_into_zero_accumulator": zero_load_reason},
              "scope": "Four pinned port labels; two arbitrary dirty helpers; one rank-two Walsh shear supported on actual orthogonal incidences. This is a scalar/common-frame lifecycle certificate, not a priced all-port compensation word, physical Clifford compiler replay, helper-bank admission, or new kappa."}
    destination = Path(__file__).with_name("RESULT.json")
    destination.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": result["status"], "indices": source_indices + targets,
                      "rank_mass": result["total_local_rank_mass"], "helper_paths": [paths["a"], paths["b"]],
                      "actual_compensation_submatrix_rank_mass": sum(map(sum, actual_paths.values()))}, sort_keys=True))


if __name__ == "__main__":
    main()
