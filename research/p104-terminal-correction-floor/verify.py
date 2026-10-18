#!/usr/bin/env python3
"""Exact terminal-cut certificate; no producer imports or floating acceptance.

Prepared for Adam Gall with substantial OpenAI Codex assistance. Apache-2.0.
The arbitrary-length lower bound is proved in README.md; this checks its finite
premises, a sharp witness in the declared relaxation, and the pricing algebra.
"""
import argparse
from collections import Counter
import copy
from fractions import Fraction as Q
from functools import lru_cache
import gzip
import hashlib
import importlib.util
from itertools import combinations, product
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
NATIVE = ROOT / "research/p104-native-channel"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def authenticate():
    pins = json.loads((HERE / "SOURCES.json").read_text())
    checked = {}
    for record in pins["files"]:
        if record["usage"] != "input":
            continue
        raw = (ROOT / record["path"]).read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        require(digest == record["sha256"], "source authentication: " + record["path"])
        checked[record["path"]] = digest
    return checked


@lru_cache(None)
def span(frame):
    values = {0}
    for vector in frame:
        require(isinstance(vector, int) and 0 < vector < 512, "binary frame vector")
        values |= {value ^ vector for value in tuple(values)}
    require(len(values) == 1 << len(frame), "independent binary frame")
    return frozenset(values)


def roots():
    values = set()
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            row = [0] * 8
            row[i], row[j] = 2, 2 * sign
            values.add(tuple(row))
    for signs in product((-1, 1), repeat=7):
        if signs.count(-1) % 2 == 0:
            values.add((1, *signs))
    require(len(values) == 120, "120 independent E8 lines")
    return sorted(values)


def inner(left, right):
    value = sum(a * b for a, b in zip(left, right))
    require(value % 4 == 0, "integral ordinary Gram entry")
    return value // 4


def initial_state(word):
    return ({name: {name: Q(1)} for name in word["initial_frames"]},
            {name: span(tuple(frame)) for name, frame in word["initial_frames"].items()})


def run(program, state, frames, persistent):
    """Independent framed row induction, preserving every arbitrary dirty input."""
    state = copy.deepcopy(state)
    frames = dict(frames)
    private = set()
    counts = Counter()
    paid = Counter()
    for event in program:
        kind, register = event[:2]
        if kind == "zero":
            require(register not in state and register not in persistent, "private initialization")
            state[register] = {}
            frames[register] = span(tuple(event[2]))
            private.add(register)
        elif kind == "erase":
            require(register in private and frames[register] == span(tuple(event[2])),
                    "owned private discard")
            del state[register], frames[register]
            private.remove(register)
        elif kind == "transport":
            _, _, old, new, rank = event
            a, b = span(tuple(old)), span(tuple(new))
            require(frames[register] == a, "transport entry frame")
            require(a < b or b < a, "strictly nested transport")
            require(rank == abs(len(old) - len(new)) and rank > 0, "paid transport rank")
            frames[register] = b
            paid[rank] += 1
        elif kind == "copy":
            _, _, source, frame = event
            require(register in private and not state[register], "owned zero copy target")
            require(frames[register] == frames[source] == span(tuple(frame)), "copy common chart")
            state[register] = dict(state[source])
        else:
            require(kind == "add", "known event alphabet")
            _, _, source, coefficient, frame = event
            require(register != source, "distinct scalar operands")
            require(frames[register] == frames[source] == span(tuple(frame)), "add common chart")
            coefficient = Q(coefficient)
            for name, value in state[source].items():
                updated = state[register].get(name, Q(0)) + coefficient * value
                if updated:
                    state[register][name] = updated
                else:
                    state[register].pop(name, None)
        counts[kind] += 1
    require(not private and set(state) == set(frames) == set(persistent), "private lifetime closure")
    return state, frames, counts, paid


def check_endpoint(state, frames, word, ports, corrected):
    for name in word["initial_frames"]:
        expected = {name: Q(1)}
        if name.startswith("Y"):
            target = int(name[1:])
            if corrected:
                expected["X" + str(target)] = Q(1)
            else:
                expected.update({"X" + str(source): Q(inner(ports[target], row), 2)
                                 for source, row in enumerate(ports) if inner(ports[target], row)})
        require(state[name] == expected, "arbitrary-input endpoint: " + name)
        require(frames[name] == span(tuple(word["final_frames"][name])), "final frame: " + name)


def make_correction(word, ports):
    """A relaxed owned-copy upper witness, not an admitted physical supplier."""
    full = word["final_frames"]["X0"]
    program, blocks = [], []
    for target, row in enumerate(ports):
        coefficients = {source: Q(source == target) - Q(inner(row, other), 2)
                        for source, other in enumerate(ports)}
        coefficients = {source: value for source, value in coefficients.items() if value}
        require(len(coefficients) == 48 and target not in coefficients, "48 nonzero side entries")
        first = min(coefficients)
        frame = word["final_frames"]["Y" + str(target)]
        start = len(program)
        program.extend([["zero", "C", full], ["copy", "C", "X" + str(first), full]])
        for source, value in coefficients.items():
            # The explicit COPY preserves the inherited owned-copy shape. Its
            # coefficient is adjusted by a legal same-chart rational addition.
            program.append(["add", "C", "X" + str(source), str(value - (source == first)), full])
        program.extend([["transport", "C", full, frame, 1],
                        ["add", "Y" + str(target), "C", "1", frame],
                        ["erase", "C", frame]])
        blocks.append([start, len(program)])
    return program, blocks


def native_premises(certificate, word, all_roots, ports, interpreter):
    """Bind actual physical labels and independently check every new drop."""
    N = interpreter
    iso = certificate["label_isometry"]
    pivots = iso["pivot_root_indices"]
    require(len(pivots) == len(set(pivots)) == 9, "nine principal coordinates")
    compressed = [sum(((inner(row, all_roots[j]) + 1) & 1) << k
                      for k, j in enumerate(pivots)) for row in all_roots]
    gram = tuple(compressed[j] for j in pivots)
    require(list(gram) == iso["compressed_gram"], "compressed Gram binding")
    dual = N.inverse(gram)
    require(list(dual) == iso["compressed_dual_gram"], "dual Gram binding")
    dot = lambda a, b: (a & N.mul(dual, b)).bit_count() & 1
    orth = iso["orthonormal_basis_compressed"]
    require(len(orth) == 9 and all(dot(a, b) == (i == j)
            for i, a in enumerate(orth) for j, b in enumerate(orth)), "label isometry")
    convert = lambda value: sum(dot(value, vector) << j for j, vector in enumerate(orth))
    physical = [convert(value) for value in compressed]
    require(physical == iso["physical_root_labels"] and len(set(physical)) == 120,
            "physical root labels")
    for i, a in enumerate(physical):
        for j, b in enumerate(physical):
            require(((a & b).bit_count() & 1) == ((inner(all_roots[i], all_roots[j]) + 1) & 1),
                    "physical pairing")
    labels = dict(zip(all_roots, physical))
    exits = {record["register"]: record for record in certificate["endpoint_adapters"]
             if record["position"] == "exit"}
    circuits = []
    target_spaces = []
    for index, row in enumerate(ports):
        name = "Y" + str(index)
        record = exits[name]
        q, frame = record["normal"], tuple(record["frame"])
        require(q == labels[row] and q.bit_count() % 2 == 1, "odd physical target normal")
        require(span(frame) == span(tuple(convert(v) for v in word["final_frames"][name])),
                "actual target-frame binding")
        require(len(frame) == 8 and all((v & q).bit_count() % 2 == 0 for v in frame),
                "target hyperplane")
        target_spaces.append(span(frame))
        require(record["recipe"]["rank"] == 0, "rank-zero exit adapter")
        adapter = N.recipe(record["recipe"])
        N.equal(adapter, N.adjoint(N.frame(frame, 9)) + (("C", q, -1),) + N.fourier(9),
                "pinned target exit identity")
        # C_q^-1 = X_q C_q. Conjugating C_e0 by the invertible
        # binary basis matrix uses exactly one positive rank-one child.
        matrix = N.transpose(N.extend((q,), 9))
        circuit = (("P", N.inverse(matrix)), ("C", 1, 1), ("P", matrix), ("X", q))
        circuit += N.adjoint(adapter)
        N.equal(circuit, N.adjoint(N.fourier(9)) + N.frame(frame, 9),
                "positive rank-one full-to-target drop")
        require(sum(gate[0] == "C" for gate in circuit) == 1, "one native positive child")
        circuits.append(circuit)
    require(len(set(target_spaces)) == 104, "104 distinct physical target hyperplanes")
    return circuits, target_spaces


def pricing(ports=104, pairs=4, banks=0, correction_mass=104):
    require(pairs >= 1 and banks >= 0, "nonnegative paired-chain parameters")
    stages = 2 * pairs + 1
    dimension = 16 * pairs + 9
    live = 2 * pairs * ports
    base_boundary = 2 * ports * 8 + 72 * 9
    idle = (dimension - 1) * live - stages * base_boundary
    require(idle >= 0, "local boundary does not fit retained no-bank windows")
    local_mass = base_boundary + 56 + correction_mass
    mass = stages * local_mass + idle + dimension * banks
    capacity = dimension * (live + banks)
    return {"pairs": pairs, "stages": stages, "dimension": dimension,
            "base_live_families": live, "fully_paid_banks": banks,
            "boundary_mass_per_call": base_boundary, "copy_mass_per_call": 56,
            "terminal_mass_floor_per_call": correction_mass,
            "unchanged_idle_mass": idle, "local_mass_per_call": local_mass,
            "total_mass_floor": mass, "capacity": capacity,
            "deficit_upper_bound": capacity - mass, "moment_zero_lower_bound": str(Q(mass, capacity))}


def replay():
    hashes = authenticate()  # No external code executes before its bytes authenticate.
    spec = importlib.util.spec_from_file_location("p104_floor_gaussian", NATIVE / "vendor/native_verify.py")
    native = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(native)
    word = json.loads((NATIVE / "inputs/LOWRANK-WITNESS.json").read_text())
    fixture = json.loads((NATIVE / "inputs/P104-FIXTURE.json").read_text())["section4_explicit_P104"]
    certificate = json.loads(gzip.decompress((NATIVE / "NATIVE-RECIPES.json.gz").read_bytes()))
    all_roots = roots()
    removed = {tuple(row) for row in fixture["F0"] + fixture["C"]}
    ports = [row for row in all_roots if row not in removed]
    require(len(removed) == 16 and len(ports) == 104, "P104 port set")
    state, frames = initial_state(word)
    persistent = set(state)
    require(len(persistent) == 280, "280 arbitrary persistent input columns")
    terminal, terminal_frames, channel_counts, channel_paid = run(word["program"], state, frames, persistent)
    check_endpoint(terminal, terminal_frames, word, ports, False)
    require(dict(channel_paid) == {1: 1074, 2: 58, 3: 86, 4: 104, 5: 48, 6: 24, 7: 8, 8: 8},
            "native channel profile")
    target_names = {"Y" + str(index) for index in range(104)}
    require(all(len(terminal_frames[name]) == (256 if name in target_names else 512)
                for name in persistent), "actual terminal frame occupancy")
    require(len({terminal_frames[name] for name in target_names}) == 104,
            "one isolated original row at each target chart")
    circuits, spaces = native_premises(certificate, word, all_roots, ports, native)
    correction, blocks = make_correction(word, ports)
    final, final_frames, extra_counts, extra_paid = run(correction, terminal, terminal_frames, persistent)
    check_endpoint(final, final_frames, word, ports, True)
    require(dict(extra_paid) == {1: 104}, "sharp relaxed correction profile")
    require(sum(rank * count for rank, count in channel_paid.items()) == 2368, "channel mass")

    # Finite premises of the written incidence proof: every correction row is
    # nonzero, and no nested transport can have two distinct target charts as
    # endpoints. A rank is at least one, so each incident chart can be charged.
    require(all(not (a < b or b < a) for a, b in combinations(spaces, 2)),
            "target hyperplane antichain")
    boundary = sum(len(word["final_frames"][name]) - len(word["initial_frames"][name])
                   for name in persistent)
    require(boundary == 2312 and 2368 - boundary == 56, "net-progress versus private-copy mass")
    require(all(final_frames[name] == terminal_frames[name] for name in persistent),
            "terminal correction has zero persistent net progress")
    budget = pricing()
    require(budget["moment_zero_lower_bound"] == "1917/1898" and budget["deficit_upper_bound"] == -608,
            "exact completed nine-stage budget")
    require(pricing(banks=1)["deficit_upper_bound"] == -608, "fully paid banks do not repair deficit")

    controls = {}
    def rejects(label, action, expected_fragment):
        try:
            action()
        except ValueError as error:
            require(expected_fragment in str(error), "control failed for an unintended reason: " + label)
            controls[label] = str(error)
        else:
            raise ValueError("accepted semantic fault: " + label)

    def check_bad(program):
        rows, charts, _, _ = run(program, terminal, terminal_frames, persistent)
        check_endpoint(rows, charts, word, ports, True)

    start, stop = blocks[0]
    rejects("omitted_target_correction", lambda: check_bad(correction[stop:]), "arbitrary-input endpoint")
    bad = copy.deepcopy(correction)
    bad[2][3] = str(Q(bad[2][3]) + 1)
    rejects("wrong_side_coefficient", lambda: check_bad(bad), "arbitrary-input endpoint")
    bad = copy.deepcopy(correction)
    bad[1][2] = next(name for name in persistent if not name.startswith(("X", "Y")))
    rejects("dirty_copy_contamination", lambda: check_bad(bad), "arbitrary-input endpoint")
    bad = copy.deepcopy(correction)
    del bad[stop - 3]
    rejects("omitted_frame_descent", lambda: check_bad(bad), "add common chart")
    bad = copy.deepcopy(correction)
    bad[stop - 1][1] = "Y0"
    rejects("discarding_persistent_target", lambda: check_bad(bad), "owned private discard")
    bad = copy.deepcopy(correction)
    full = word["final_frames"]["X0"]
    bad.append(["add", "X0", "X1", "1", full])
    rejects("source_not_restored", lambda: check_bad(bad), "arbitrary-input endpoint")
    rejects("wrong_native_global_phase", lambda: native.equal(circuits[0] + (("phase", 1),),
            circuits[0], "native global phase"), "native global phase")

    wrong_mass = budget["total_mass_floor"] - 104 * budget["stages"]
    def validate_invoice(mass):
        require(mass == budget["stages"] * budget["local_mass_per_call"]
                + budget["unchanged_idle_mass"], "terminal ranks cannot be debited from old idle coverage")
    rejects("double_spent_idle_credit", lambda: validate_invoice(wrong_mass), "old idle coverage")
    require(Q(wrong_mass, budget["capacity"]) < 1, "invoice fault reverses zero-saving decision")

    return {"status": "PASS_P104_TERMINAL_CORRECTION_FLOOR", "source_sha256": hashes,
            "ports": 104, "arbitrary_input_columns": 280, "isolated_target_hyperplanes": 104,
            "physical_pairing_checks": 14400, "native_rank_one_drop_identities": len(circuits),
            "native_circuits_canonical_sha256": hashlib.sha256(canonical(circuits)).hexdigest(),
            "channel_events": len(word["program"]), "channel_event_counts": dict(sorted(channel_counts.items())),
            "channel_paid_profile": dict(sorted(channel_paid.items())), "channel_rank_mass": 2368,
            "persistent_boundary_mass": boundary, "private_copy_mass": 56,
            "correction_rank_mass_lower_bound": 104, "no_allocation_rank_mass_lower_bound": 208,
            "relaxed_witness_events": len(correction), "relaxed_witness_event_counts": dict(sorted(extra_counts.items())),
            "relaxed_witness_paid_profile": {1: 104},
            "relaxed_witness_canonical_sha256": hashlib.sha256(canonical(correction)).hexdigest(),
            "completed_local_profile": dict(sorted((channel_paid + extra_paid).items())),
            "nine_stage_optimistic_bill": budget,
            "invalid_idle_reuse_moment_zero": str(Q(wrong_mass, budget["capacity"])),
            "all_odd_stage_deficit_polynomial": "104*(s-1)-160*s = -56*s-104",
            "controls": controls,
            "scope": "Sharp common-chart terminal-cut floor in an owned-copy relaxation; exact finite native drop operators and arbitrary-input rows, not a physically admitted copy/erase supplier. Pricing is conditional on the retained one-unpaid-coordinate paired-chain law and fully paid banks. No earlier-cut exclusion, all-size proof, new kappa, or selected source changes."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="regenerate the canonical result receipt")
    args = parser.parse_args()
    result = replay()
    encoded = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if args.write:
        (HERE / "RESULT.json").write_text(encoded)
    else:
        require(json.loads((HERE / "RESULT.json").read_text()) == json.loads(encoded),
                "complete regenerated result comparison")
    print(encoded, end="")


if __name__ == "__main__":
    main()
