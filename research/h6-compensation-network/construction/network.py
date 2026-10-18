#!/usr/bin/env python3
"""Compressed edge schema and exact bounded all-column lifecycle replay.

The full schema has one ordinary dirty helper for every nonzero I-K entry.
Fixtures explicitly emit all compensation events. The optional K callback is
an interface test, not a gate-level K compiler or proof of supplier admission.
"""
from fractions import Fraction as Q
from pathlib import Path
import hashlib
import json
import platform
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from artifact import write_gzip_json
INPUT = ROOT / "research/niemeier-lattices/code/e8_cubed.py"
sys.path.insert(0, str(INPUT.parent))
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


def subset(small, large):
    return len(basis(small + large)) == len(large)


def perp(word):
    pivot = (word & -word).bit_length() - 1
    return basis((1 << bit) ^ ((1 << pivot) if word >> bit & 1 else 0)
                 for bit in range(17) if bit != pivot)


ZERO = ()
FULL = basis(1 << bit for bit in range(17))


def merge(destination, source, coefficient):
    result = dict(destination)
    for column, value in source.items():
        result[column] = result.get(column, Q(0)) + coefficient * value
        if result[column] == 0:
            del result[column]
    return result


def add(dst, src, q, phase):
    return dict(op="add", dst=dst, src=src, q=str(q), phase=phase)


def climb(register, frame, phase):
    return dict(op="climb", register=register, frame=list(frame), phase=phase)


def edge_records(ports, packed, source_indices, target_indices):
    """Canonical order: ascending supplied target position, then source position.

    Supply range(30960) for both index lists for the complete compressed
    construction. This generator never allocates a full NxN matrix.
    """
    for ti, target in enumerate(target_indices):
        for si, source in enumerate(source_indices):
            numerator = int(ports[source] @ ports[target])
            require(numerator % 4 == 0, "integral pairing")
            pairing = numerator // 4
            coefficient = Q(int(source == target)) - Q(pairing ** 3 - 4 * pairing, 48)
            if coefficient:
                require((int(packed[source]) & int(packed[target])).bit_count() % 2 == 0,
                        "nonzero compensation edge is not binary orthogonal")
                yield dict(source_position=si, target_position=ti, source_port=int(source),
                           target_port=int(target), pairing=pairing, coefficient=str(coefficient),
                           helper=f"h{ti}_{si}")


def event_records(ports, packed, source_indices, target_indices, k_event=None):
    """Deterministic full phase iterator; only one edge record is live at once.

    A complete traversal is huge. This is the compressed definition; bounded
    fixtures use this identical iterator. k_event is an explicitly supplied
    restored interface invocation, never synthesized from scalar identities.
    """
    def edges():
        return edge_records(ports, packed, source_indices, target_indices)
    for edge in edges():
        yield add(f"t{edge['target_position']}", edge["helper"], -Q(edge["coefficient"]), "dirt_prefix")
    for edge in edges():
        source = f"s{edge['source_position']}"
        yield climb(edge["helper"], basis([int(packed[edge["source_port"]])]), "source_line_gather")
        yield add(edge["helper"], source, 1, "source_line_gather")
    for si in range(len(source_indices)):
        yield climb(f"s{si}", FULL, "source_full")
    if k_event is not None:
        yield k_event
    for ti, target in enumerate(target_indices):
        yield climb(f"t{ti}", perp(int(packed[target])), "target_caps")
    for edge in edges():
        target = f"t{edge['target_position']}"
        yield climb(edge["helper"], perp(int(packed[edge["target_port"]])), "target_cap_scatter")
        yield add(target, edge["helper"], Q(edge["coefficient"]), "target_cap_scatter")
    for edge in edges():
        yield climb(edge["helper"], FULL, "helper_full")
    for edge in edges():
        yield add(edge["helper"], f"s{edge['source_position']}", -1, "FULL_cleanup")


def emit(ports, packed, indices, include_k):
    edges = list(edge_records(ports, packed, indices, indices))
    sources = [f"s{i}" for i in range(len(indices))]
    targets = [f"t{i}" for i in range(len(indices))]
    starts = {s: basis([int(packed[port])]) for s, port in zip(sources, indices)}
    starts.update({t: ZERO for t in targets})
    starts.update({edge["helper"]: ZERO for edge in edges})
    ends = {s: FULL for s in sources}
    ends.update({t: perp(int(packed[port])) for t, port in zip(targets, indices)})
    ends.update({edge["helper"]: FULL for edge in edges})
    k = [[Q((int(ports[si] @ ports[ti]) // 4) ** 3 - 4 * (int(ports[si] @ ports[ti]) // 4), 48)
          for si in indices] for ti in indices]
    k_event = dict(op="K_interface", phase="K_complete_invocation", sources=sources, targets=targets,
                   matrix=[[str(value) for value in row] for row in k]) if include_k else None
    events = list(event_records(ports, packed, indices, indices, k_event))
    return dict(indices=list(map(int, indices)), starts={k: list(v) for k, v in starts.items()},
                ends={k: list(v) for k, v in ends.items()}, edges=edges, events=events, include_k_interface=include_k)


def replay(fixture, dual=False):
    frames = {k: tuple(v) for k, v in fixture["starts"].items()}
    rows = {register: {register: Q(1)} for register in frames}
    paths = {register: [] for register in frames}
    for step, event in enumerate(fixture["events"]):
        if event["op"] == "climb":
            register, frame = event["register"], tuple(event["frame"])
            require(frame == basis(frame), f"step {step}: noncanonical frame")
            require(subset(frames[register], frame), f"step {step}: nonnested ordinary transition")
            increment = len(frame) - len(frames[register])
            if increment:
                paths[register].append(increment)
            frames[register] = frame
        elif event["op"] == "add":
            dst, src, coefficient = event["dst"], event["src"], Q(event["q"])
            require(frames[dst] == frames[src], f"step {step}: unequal current frames")
            if dual:
                dst, src, coefficient = src, dst, -coefficient
            rows[dst] = merge(rows[dst], rows[src], coefficient)
        elif event["op"] == "K_interface":
            sources, targets = event["sources"], event["targets"]
            require(all(frames[s] == FULL for s in sources), "K source entrance FULL")
            require(all(frames[t] == ZERO for t in targets), "K target entrance zero")
            # This macro promises exact restoration of every unrelated helper
            # and source in the forward orientation. It has no source/helper
            # dirt response. It is deliberately not counted as emitted gates.
            for ti, target in enumerate(targets):
                for si, source in enumerate(sources):
                    q = Q(event["matrix"][ti][si])
                    if dual:
                        rows[source] = merge(rows[source], rows[target], -q)
                    else:
                        rows[target] = merge(rows[target], rows[source], q)
        else:
            raise ValueError("unknown event")
    require(frames == {k: tuple(v) for k, v in fixture["ends"].items()}, "wrong endpoint frames")
    return rows, paths


def expected(fixture, dual=False):
    rows = {register: {register: Q(1)} for register in fixture["starts"]}
    if fixture["include_k_interface"]:
        for i in range(len(fixture["indices"])):
            dst, src, q = (f"s{i}", f"t{i}", Q(-1)) if dual else (f"t{i}", f"s{i}", Q(1))
            rows[dst] = merge(rows[dst], rows[src], q)
    else:
        for edge in fixture["edges"]:
            source, target = f"s{edge['source_position']}", f"t{edge['target_position']}"
            dst, src, q = (source, target, -Q(edge["coefficient"])) if dual else (target, source, Q(edge["coefficient"]))
            rows[dst] = merge(rows[dst], rows[src], q)
    return rows


def run_fixture(fixture):
    forward, paths = replay(fixture)
    dual, dual_paths = replay(fixture, True)
    require(forward == expected(fixture), "forward all-basis arbitrary-dirt mismatch")
    require(dual == expected(fixture, True), "inverse-transpose all-basis mismatch")
    require(paths == dual_paths, "orientation frame chronology differs")
    n = len(fixture["indices"])
    r = len(fixture["edges"])
    require(all(paths[f"s{i}"] == [16] and paths[f"t{i}"] == [16] for i in range(n)), "data profile")
    require(all(paths[edge["helper"]] == [1, 15, 1] for edge in fixture["edges"]), "edge helper profile")
    return dict(ports=n, helper_count=r, arbitrary_basis_columns=len(forward),
                event_count=len(fixture["events"]), all_basis_forward="PASS", all_basis_inverse_transpose="PASS",
                same_current_frames_and_nested_paths="PASS", local_rank_mass=32*n+17*r,
                include_k_interface=fixture["include_k_interface"], source_path=[16], target_path=[16], helper_path=[1,15,1])


def controls(fixture, packed):
    result = {}
    for phase, key in (("dirt_prefix", "missing_prefix"), ("target_cap_scatter", "missing_edge"), ("FULL_cleanup", "missing_cleanup")):
        index = next(i for i, event in enumerate(fixture["events"]) if event["phase"] == phase and event["op"] == "add")
        mutant = dict(fixture, events=fixture["events"][:index] + fixture["events"][index+1:])
        rows, _ = replay(mutant)
        require(rows != expected(fixture), f"{key} mutant was not detected")
        affected = sorted(register for register in rows if rows[register] != expected(fixture)[register])
        result[key] = dict(detected=True, affected_registers=affected, removed_event=fixture["events"][index])
    first = fixture["edges"][0]
    source = f"s{first['source_position']}"
    # Every address is odd, so the cap of the identical address never contains
    # the source line. This tests actual orthogonality, not a hand-picked frame.
    source_label = int(packed[fixture["indices"][first["source_position"]]])
    require(source_label.bit_count() % 2 == 1, "odd address witness")
    mutation = climb(first["helper"], perp(source_label), "nonorthogonal_mutant")
    gather_end = next(i for i, event in enumerate(fixture["events"]) if event["phase"] == "source_full")
    try:
        replay(dict(fixture, events=fixture["events"][:gather_end] + [mutation]))
    except ValueError as error:
        require("nonnested" in str(error), "nonorthogonality failed for unrelated reason")
        result["nonorthogonal_edge"] = dict(detected=True, reason=str(error), source_label=source_label)
    else:
        raise ValueError("nonorthogonal edge passed")
    index = next(i for i, event in enumerate(fixture["events"]) if event["phase"] == "source_line_gather" and event["op"] == "climb")
    mutant = dict(fixture, events=fixture["events"][:index] + fixture["events"][index+1:])
    try:
        replay(mutant)
    except ValueError as error:
        require("unequal current frames" in str(error), "wrongframe failed for unrelated reason")
        result["missing_helper_line_join"] = dict(detected=True, reason=str(error))
    else:
        raise ValueError("missing line join passed")
    return result


def main():
    require(hashlib.sha256(INPUT.read_bytes()).hexdigest() == "ce24f397053c0ef5b26881bb7ccfab53fb0a3d762f2de04086fed8f7b41e8234", "pinned geometry changed")
    roots, _, shell, profiles = geometry.construct_shell()
    ports = shell[(profiles & 4) == 0, :16]
    _, packed, fitting = geometry.binary_labels(roots, ports)
    require(len(ports) == 30960 and fitting["dimension"] == 17, "wrong full domain")
    records = []
    fixtures = []
    for n in (8, 32):
        indices = [0, 3, 287, 288]
        for i in range(n):
            candidate = (i * 30959) // (n - 1)
            if candidate not in indices:
                indices.append(candidate)
            if len(indices) == n:
                break
        require(len(indices) == n and len({int(packed[i]) for i in indices}) == n, "varying distinct fixture labels")
        for include_k in (False, True):
            fixture = emit(ports, packed, indices, include_k)
            record = run_fixture(fixture)
            if n == 8:
                record["negative_controls"] = controls(fixture, packed)
            fixture_path = HERE / f"fixture-{n}-{'composed' if include_k else 'compensation'}.json.gz"
            digest = write_gzip_json(fixture_path, fixture)
            record["fixture"] = fixture_path.name
            record["fixture_canonical_sha256"] = digest
            records.append(record)
    receipt = dict(status="PASS_FINITE_FULL_EDGE_SCHEMA_FIXTURES", python=platform.python_version(),
                   generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                   source_sha256=hashlib.sha256(INPUT.read_bytes()).hexdigest(), full_ports=30960,
                   canonical_edge_order="target_position then source_position; omit exactly zero I-K coefficients",
                   full_schema_is_executable_iterator=True, full_events_materialized=False,
                   fixture_results=records,
                   scope="Exact finite scalar and common-frame compensation; composed fixtures use an explicit complete-restored K interface macro. No physical Clifford compiler or all-port emitted stream, K admission, full bank invoice, or new kappa is claimed.")
    prior = ROOT / "research/h6-independent-audit/walsh/results.json"
    previous = json.loads(prior.read_text())
    full_r = previous["compensation_nonzeros"]
    require(full_r == 480337920, "prior exhaustive nonzero receipt changed")
    schema = dict(status="COMPRESSED_FULL_EDGE_CONSTRUCTION", N=30960, h=17, helper_roles=full_r,
                  count_provenance=dict(path=str(prior.relative_to(ROOT)), sha256=hashlib.sha256(prior.read_bytes()).hexdigest(),
                                        note="Prior exhaustive 958521600-entry audit; full count is retained evidence, not rerun here."),
                  source_sha256=hashlib.sha256(INPUT.read_bytes()).hexdigest(),
                  packed_labels_sha256=hashlib.sha256(packed.astype('<u4').tobytes()).hexdigest(),
                  scalar_coefficients={str(t): str(Q(4*t-t**3,48)) for t in (-3,-1,1,3)},
                  edge_iterator="edge_records(ports,packed,range(30960),range(30960))",
                  event_iterator="event_records(ports,packed,range(30960),range(30960),k_event=None)",
                  source_path=[16], target_path=[16], ordinary_helper_path=[1,15,1],
                  source_target_transition_mass=32*30960, helper_transition_mass=17*full_r,
                  compensation_local_rank_mass=32*30960+17*full_r,
                  compensation_event_count=7*full_r+2*30960,
                  scalar_add_count=4*full_r, transition_count=3*full_r+2*30960,
                  private_descent_bill_compensation=0,
                  scope="Compressed all-port scalar/frame definition and proof. Counts do not include K, controller banks, pads, repetitions, adapters, or a physical Clifford compiler.")
    (HERE / "SCHEMA.json").write_text(json.dumps(schema, indent=2, sort_keys=True) + "\n")
    (HERE / "RESULT.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": receipt["status"], "fixtures": records}, sort_keys=True))


if __name__ == "__main__":
    main()
