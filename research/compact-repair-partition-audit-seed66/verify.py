#!/usr/bin/env python3
"""Source-bound partition-repair audit; finite checks support PROOF.md.

Apache-2.0. @CubeJerry, with substantial OpenAI Codex assistance.
"""
import argparse
from collections import Counter
from fractions import Fraction
from hashlib import sha1, sha256
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def authenticate(root=HERE):
    manifest = json.loads((root / "SOURCES.json").read_text())
    for entry in manifest["vendored"]:
        data = (root / entry["path"]).read_bytes()
        need(sha256(data).hexdigest() == entry["sha256"], "source SHA256: " + entry["path"])
        blob = sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        need(blob == entry["git_blob"], "source Git blob: " + entry["path"])
    return len(manifest["vendored"])


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def load_sources():
    streams = load_module("streams", HERE / "sources/streams.py")
    compact = load_module("compact_source_s66", HERE / "sources/compact.py")
    oracle = load_module("repair_oracle_s66", HERE / "oracle.py")
    return streams, compact, oracle


def layout_for(compact, K, G, record_bits=1):
    return compact.Layout((("u", G), ("t", G), ("x", 2*K),
                           ("y", 2*K), ("b", G)), record_bits)


def repair_formula(y, t, z, K, G, rho):
    active = z == 1 and t == (1 << G)-1 and not ((y >> rho) & 1)
    return (y - ((1 << (rho+G+1)) if active else 0)) % (1 << (2*K))


def invariant(mapping, labels):
    return all(labels[i] == labels[d] for i, d in enumerate(mapping))


def tariff(records, bad, A, R):
    need(type(records) is int and type(bad) is int and 0 <= bad <= records,
         "integer record counts")
    need(type(A) is int and type(R) is int and A > 0 and R > 0, "positive tariff shape")
    return records*R + records*A**3 + bad*A*(R+A)


def address_checks(compact, oracle):
    rows, comparisons = [], 0
    # Full target ranges, every dirty digit and both source bits. These fixed
    # fixtures all have a nonempty original sufficient good set.
    for G in range(1, 5):
        K, rho = G+4, 66 % (G+4)
        layout = layout_for(compact, K, G)
        word = compact.Compact(1, K, G, rho, "x", "y")
        word.validate(layout)
        M, B = 1 << (2*K), 1 << G
        for z in (0, 1):
            for t in range(B):
                forward = []
                for y in range(M):
                    state = dict(u=(t+1) % B, t=t, x=z << rho, y=y, b=B-1-t)
                    actual = word.execute(state, layout)
                    oy, ot = oracle.raw_scalar(y, t, z, K, G, rho)
                    need(actual == dict(state, y=oy, t=ot), "literal raw/scalar mismatch")
                    need(ot == t, "one-digit dirty value not restored")
                    forward.append(actual["y"])
                inverse = oracle.inverse_table(forward)
                for y, original in enumerate(inverse):
                    need(original ^ (z << rho) == repair_formula(y, t, z, K, G, rho),
                         "closed repair formula")
                    comparisons += 1
        rows.append({"G": G, "K": K, "rho": rho, "target_states": M,
                     "dirty_states": B, "source_bits": 2, "comparisons": 2*B*M})
    return rows, comparisons


def primary_orbits(compact, oracle):
    G, K, rho = 4, 8, 2
    M, h = 1 << (2*K), 1 << (rho+G+1)
    layout = layout_for(compact, K, G)
    word = compact.Compact(1, K, G, rho, "x", "y")
    state = dict(u=3, t=15, x=4, y=0, b=11)
    old = word.execute(state, layout, True)
    destination = word.ideal(old)
    need(old["y"] == 65412 and destination["y"] == 65408, "source crossing witness")
    mapping = []
    for y in range(M):
        post = dict(state, y=y)
        need(word.bad(post), "saturated-t fibre must be exceptional")
        actual = word.ideal(word.execute(post, layout, True))
        need(actual == dict(post, y=repair_formula(y, 15, 1, K, G, rho)), "inverse-source formula")
        mapping.append(actual["y"])
    histogram = Counter(len(cycle) for cycle in oracle.cycles(mapping))
    need(histogram == {1: 32768, 512: 64}, "complete target-fibre cycle inventory")
    for b in range(2*K):
        need(not invariant(mapping, [y >> b for y in range(M)]), "high-target partition admitted")
    safe = [y % h for y in range(M)]
    need(invariant(mapping, safe), "low-residue partition rejected")
    tokens = oracle.executable_local_repair(mapping, safe)
    need(tokens == tuple(oracle.inverse_table(mapping)), "orbit-cell keyed restoration")
    unsafe = [y >> (2*K-1) for y in range(M)]
    need(oracle.executable_local_repair(mapping, unsafe) is None, "half-range repair must reject")
    raw_zero = word.execute(state, layout)
    need(safe[0] != safe[raw_zero["y"]], "raw-invariance unnecessarily required")
    return {"parameters": {"G": G, "K": K, "rho": rho}, "post_raw": state,
            "raw_preimage": old, "repair_destination": destination, "shift": h,
            "target_records": M,
            "cycle_histogram": {str(k): v for k, v in sorted(histogram.items())},
            "proper_dyadic_partitions_rejected": list(range(2*K)),
            "safe_residue_cells": h, "safe_local_payload_records": len(tokens),
            "raw_invariance_not_required": True}


def partition_checks(oracle):
    pairs = admitted = 0
    for mapping, labels in oracle.all_small_cases(5):
        result = oracle.executable_local_repair(mapping, labels)
        accepted = invariant(mapping, labels)
        need(accepted == (result is not None), "partition criterion vs keyed reinsertion")
        if accepted:
            need(result == tuple(oracle.inverse_table(mapping)), "local endpoint mismatch")
            admitted += 1
        pairs += 1
    return {"maximum_records": 5, "permutation_partition_pairs": pairs, "admitted_pairs": admitted}


def tariff_checks(oracle):
    checked = 0
    for M in range(1, 7):
        for labels in oracle.partitions(M):
            for mask in range(1 << M):
                bad = [(mask >> i) & 1 for i in range(M)]
                A, R = 16, 16**3
                local = sum(tariff(sum(x == cell for x in labels),
                                   sum(bad[i] for i in range(M) if labels[i] == cell), A, R)
                            for cell in set(labels))
                need(local == tariff(M, sum(bad), A, R), "partition tariff not additive")
                checked += 1
    M, A, R, B = 1024, 32, 32**3, 4
    total = tariff(M, B, A, R)
    need(total == tariff(B, B, A, R) + tariff(M-B, 0, A, R), "bad-only tariff identity")
    need(total <= 3*M*R and tariff(B, B, A, R) > 3*B*R, "local/global admission distinction")
    duplicated, underbilled = tariff(M, M, A, R), tariff(M, 1, A, R)
    need(duplicated > 3*M*R and underbilled < 3*M*R, "duplicate-visit control")
    fragmented = tariff(M*R, 0, A, 1)
    need(tariff(M, 0, A, R) <= 3*M*R < fragmented, "fragmentation control")
    return {"partition_badset_cases": checked, "bad_only_partition": {
                "records": M, "record_bits": R, "key_bound": A, "bad_records": B,
                "global_tariff": total, "global_tariff_over_volume": str(Fraction(total, M*R)),
                "bad_cell_tariff_over_volume": str(Fraction(tariff(B, B, A, R), B*R))},
            "duplicate_visits_tariff": duplicated, "false_global_density_tariff": underbilled,
            "fragmented_tariff": fragmented}


def physical_checks(streams, compact, oracle):
    fixtures = []
    for rho in (0, 1):
        K, G = 2, 1  # Legal finite sizes; their sufficient good guard is empty.
        temporary = layout_for(compact, K, G)
        layout = layout_for(compact, K, G, temporary.bits)
        word = compact.Compact(1, K, G, rho, "x", "y")
        word.validate(layout)
        payload = b"".join(streams.bit_key(i, layout.bits) for i in range(layout.records))
        meter = streams.Meter()
        source = streams.Tape(meter, payload)
        actual = compact.execute(source, layout, word)
        expected = bytearray(len(payload))
        for address in range(layout.records):
            state = layout.decode(address)
            select = (1 << rho) | (1 << (rho+K))
            target = layout.encode(dict(state, y=state["y"] ^ (state["x"] & select)))
            expected[target*layout.bits:(target+1)*layout.bits] = payload[address*layout.bits:(address+1)*layout.bits]
        need(actual.data == expected and actual.head == 0 and not source.data,
             "complete source payload endpoint")
        # Actual raw sequential payload, followed by actual source key maps and
        # stable-radix operations. Group dispatch here is a finite test harness,
        # not a proposed fixed-tape partition dispatcher or its cost proof.
        raw = streams.Tape(streams.Meter(), payload)
        for op in word.operations():
            raw = (compact.ordinary(raw, layout, op[1], op[2]) if op[0] == "swap"
                   else compact.rotate(raw, layout, word, op))
        mapping, labels, unsafe_labels = [], [], []
        h = 1 << (rho+G+1)
        for address in range(layout.records):
            state = layout.decode(address)
            need(word.bad(state), "small fixture uses the all-bad guard")
            mapping.append(layout.encode(word.ideal(word.execute(state, layout, True))))
            prefix = (state['u'], state['t'], state['x'], state['b'])
            labels.append(prefix + (state['y'] % h,))
            unsafe_labels.append(prefix + (state['y'] >> (2*K-1),))
        need(invariant(mapping, labels), "physical safe partition")
        need(not invariant(mapping, unsafe_labels), "physical unsafe partition")
        need(oracle.executable_local_repair(mapping, unsafe_labels) is None,
             "physical cross-cell keyed reinsertion must reject")
        groups = {}
        for address, label in enumerate(labels):
            groups.setdefault(label, []).append(address)
        partitioned = bytearray(len(payload))
        partition_meter = streams.Meter()
        for addresses in groups.values():
            keyed = streams.Tape(partition_meter)
            for address in addresses:
                keyed.write(streams.bit_key(mapping[address], layout.bits))
                keyed.write(raw.data[address*layout.bits:(address+1)*layout.bits])
            keyed.rewind()
            sorted_tape = streams.stable_radix(keyed, layout.bits, layout.bits)
            for hole in addresses:
                need(streams.key_value(sorted_tape.read(layout.bits)) == hole,
                     "cell's actual sorted key does not fill its hole")
                partitioned[hole*layout.bits:(hole+1)*layout.bits] = sorted_tape.read(layout.bits)
            sorted_tape.finish()
            sorted_tape.erase()
        global_meter = streams.Meter()
        globally_repaired = compact.repair(streams.Tape(global_meter, raw.data), layout, word)
        need(partitioned == globally_repaired.data, "partitioned/global source repair mismatch")
        raw.erase()
        fixtures.append({"K": K, "G": G, "rho": rho, "records": layout.records,
                         "record_bits": layout.bits, "payload_bits": len(payload),
                         "safe_cells": len(groups), "complete_source_reads": meter.reads,
                         "complete_source_writes": meter.writes,
                         "partitioned_radix_reads": partition_meter.reads,
                         "partitioned_radix_writes": partition_meter.writes})
    return fixtures


def run():
    pins = authenticate()
    streams, compact, oracle = load_sources()
    rows, comparisons = address_checks(compact, oracle)
    return {"status": "PASS_COMPACT_REPAIR_PARTITION_AUDIT", "assignment_seed": 66,
            "authenticated_predecessor_files": pins, "address_cases": rows,
            "complete_address_comparisons": comparisons,
            "primary_orbits": primary_orbits(compact, oracle),
            "partition_census": partition_checks(oracle), "tariffs": tariff_checks(oracle),
            "physical_fixtures": physical_checks(streams, compact, oracle),
            "kappa": "No new κ"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="write a new receipt; never overwrite")
    args = parser.parse_args()
    if args.write is not None:
        need(not args.write.exists(), "refusing to overwrite receipt")
    result = run()
    if args.write is not None:
        with args.write.open("x") as output:
            output.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        expected = json.loads((HERE / "RESULT.json").read_text())
        need(canonical(result) == canonical(expected), "complete typed receipt mismatch")
    print(result["status"], "addresses=" + str(result["complete_address_comparisons"]),
          "orbit_length=512", "physical_records=" + str(sum(r["records"] for r in result["physical_fixtures"])),
          "no_new_kappa")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError) as error:
        raise SystemExit("FAIL_COMPACT_REPAIR_PARTITION_AUDIT: " + str(error))
