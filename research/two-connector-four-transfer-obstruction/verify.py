#!/usr/bin/env python3
"""Four-transfer obstruction: exact scoped checks, no predecessor imports.

Gareth Davidson (@bitplane), with substantial OpenAI Codex assistance.
Apache-2.0. Written proof is in README.md; this is not a proof assistant.
"""
import argparse
from collections import Counter
from hashlib import sha1, sha256
import importlib.util
from itertools import combinations, product
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = "4040a0f46d67b41c36a472a7cd4af791fd4c36cc"
INPUTS = {"research/universal-connector-boundary/" + name
          for name in ("README.md", "NOTICE.md", "CERTIFICATE.json")}
PROVENANCE = {"docs/research/agent-task-catalog.json", "certificates/selected-result.json"}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def read_json(path):
    def pairs(items):
        obj = {}
        for k, v in items:
            need(k not in obj, "duplicate JSON key: " + k)
            obj[k] = v
        return obj
    def bad(value):
        raise ValueError("noninteger/nonfinite JSON number: " + value)
    return json.loads(path.read_text(), object_pairs_hook=pairs,
                      parse_float=bad, parse_constant=bad)


def independent():
    spec = importlib.util.spec_from_file_location("four_transfer_independent", HERE / "independent.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def sources():
    pins = read_json(HERE / "SOURCES.json")
    need(pins["base_commit"] == BASE, "base pin")
    records = pins["files"]
    need(len(records) == 5 and {r["path"] for r in records} == INPUTS | PROVENANCE,
         "complete source inventory")
    for row in records:
        need(row["usage"] == ("input" if row["path"] in INPUTS else "provenance"), "source role")
        if row["path"] not in INPUTS:
            continue
        local = HERE / "references" / ("PR943-" + row["path"].rsplit("/", 1)[-1])
        data = local.read_bytes()
        need(sha256(data).hexdigest() == row["sha256"], "retained source SHA256: " + str(local))
        need(sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest() == row["git_blob"],
             "retained source Git blob")
        live = HERE.parents[1] / row["path"]
        if live.exists():
            need(live.read_bytes() == data, "live source drift: " + row["path"])
    remote = read_json(HERE / "REMOTE-SOURCES.json")
    expected_files = {"references/PR1438-README.md", "references/DISCUSSION1412.json"}
    need(len(remote["files"]) == 2 and {r["local_path"] for r in remote["files"]} == expected_files,
         "remote source inventory")
    need(remote["predecessor_head"] == "a61170c97c9ea2c396f6d76a953b0cf74a455cdd", "PR1438 head")
    for row in remote["files"]:
        data = (HERE / row["local_path"]).read_bytes()
        need(sha256(data).hexdigest() == row["sha256"], "remote retained source SHA256")
        if "git_blob" in row:
            need(sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest() == row["git_blob"],
                 "remote retained Git blob")
    return read_json(HERE / "references/PR943-CERTIFICATE.json")


def pair_words(n):
    """Restricted-growth words: each symbol occurs twice, labels open in order."""
    def walk(prefix, counts):
        if len(prefix) == 2 * n:
            yield tuple(prefix)
            return
        for j in range(min(n, len(counts) + 1)):
            if j == len(counts):
                yield from walk(prefix + [j], counts + [1])
            elif counts[j] == 1:
                new = counts[:]
                new[j] = 2
                yield from walk(prefix + [j], new)
    yield from walk([], [])


def differences(word):
    vertex = 0
    vertices = {0}
    for label in word:
        vertex ^= 1 << label
        vertices.add(vertex)
    return {a ^ b for a in vertices for b in vertices}


def old_boundary(other, predecessor):
    reports = []
    for n, total in ((1, 1), (2, 3), (3, 15), (4, 105), (5, 945)):
        first = {w: differences(w) for w in pair_words(n)}
        second = {w: other.interval_masks(w) for w in other.matchings(n)}
        need(first == second and len(first) == total, "independent pairing/interval coverage")
        hist = Counter(map(len, first.values()))
        entries = sorted((list(w), sum(1 << m for m in masks)) for w, masks in first.items())
        digest = sha256(json.dumps(entries, separators=(",", ":")).encode()).hexdigest()
        report = {"sources": n, "pairings": total,
                  "histogram": {str(k): v for k, v in sorted(hist.items())},
                  "canonical_entries_sha256": digest, "max_coverage": max(hist)}
        if n >= 4:
            need(canonical(report) == canonical(predecessor["censuses"][n - 4]), "pinned predecessor census")
        reports.append(report)
    return reports


def phase_census(other):
    result = []
    for r in range(6):
        histogram = Counter()
        digest = sha256()
        for a, b, c in product(range(1 << r), repeat=3):
            u = (a, b, c, a ^ b ^ c)
            actual = other.four_phase_masks(u)
            expected = {0, a ^ b, a ^ u[3]}
            need(actual == expected, "four-transfer phase projection")
            need(len(actual - {0}) <= 2, "unpaid mixed projection")
            # Both nonzero candidates are literal pairs of source prefixes.
            need(actual <= {x ^ y for x in u for y in u}, "all-source-port reduction")
            if r >= 2:
                need(bool(set(range(1, 1 << r)) - actual), "missing mixed projection not found")
            histogram[len(actual)] += 1
            digest.update((canonical([list(u), sorted(actual)]) + "\n").encode())
        result.append({"source_port1_dimension": r, "tuples": sum(histogram.values()),
                       "projection_sizes": {str(k): v for k, v in sorted(histogram.items())},
                       "sha256": digest.hexdigest()})
    return result


def phase_history(labels, ports, positions):
    """Normal form q0 + cumulative transfer prefix; separate from literal replay."""
    q0 = q1 = drift = parity = b = 0
    history = [(1, 2)]
    transfer_prefixes = []
    projected_word = []
    for pos in range(len(labels) + 4):
        if pos in positions:
            drift ^= q1
            parity ^= 1
            transfer_prefixes.append(q1)
            if q1:
                projected_word.append(q1)
        else:
            j = labels[b]
            if ports & (1 << j):
                q1 ^= 1 << j
            else:
                q0 ^= 1 << j
                projected_word.append(1 << j)
            b += 1
        history.append((1 | (parity << 1) | ((q0 ^ drift) << 2), 2 | (q1 << 2)))
    return history, transfer_prefixes, projected_word


def grouped_masks(history):
    groups = {1: set(), 2: set(), 3: set()}
    for state in history:
        for row in state:
            groups[row & 3].add(row >> 2)
    return {a ^ b for values in groups.values() for a in values for b in values}


def reductions(labels, ports, u, projected, masks):
    n = len(set(labels))
    all_sources = (1 << n) - 1
    r = ports.bit_count()
    mixed = {m for m in masks if m & ports and m & (all_sources ^ ports)}
    if r == 0 or r == n:
        need(masks <= differences(labels), "single-group prefix reduction")
    elif r >= 2:
        possibilities = {u[0] ^ u[1], u[0] ^ u[3]} - {0}
        need({m & ports for m in mixed} <= possibilities, "mixed-mask projection lemma")
        need(len(masks) <= (1 << r) + 3 * (1 << (n - r)) - 3, "partition ceiling")
    else:
        active = sum(bool(value) for value in u)
        need(active in (0, 2, 4), "single-source pulse parity")
        if active != 2:
            need(not mixed, "zero/four-pulse source leaked mixed mask")
        else:
            word = [value.bit_length() - 1 for value in projected]
            need(len(word) == 2 * n and Counter(word) == Counter({j: 2 for j in range(n)}),
                 "contracted source word multiplicity")
            need(masks <= differences(word), "one-port1-source contraction")


def small_census(n, other):
    histogram = Counter()
    branch_counts = Counter()
    candidates = restored = 0
    for labels in pair_words(n):
        for ports in range(1 << n):
            for positions in combinations(range(2 * n + 4), 4):
                candidates += 1
                h, u, projected = phase_history(labels, ports, positions)
                need(h == other.histories(labels, ports, positions), "normal-form/literal history mismatch")
                if h[-1] != (1, 2):
                    continue
                restored += 1
                masks = grouped_masks(h)
                need(masks == other.masks(h), "paired-readout independent oracle")
                reductions(labels, ports, u, projected, masks)
                histogram[len(masks)] += 1
                branch_counts[ports.bit_count()] += 1
    result = {"candidates": candidates, "restored": restored,
              "coverage_histogram": {str(k): v for k, v in sorted(histogram.items())}}
    need(canonical(result) == canonical(other.small_census(n)), "independent complete small census")
    return {"sources": n, **result,
            "restored_by_port1_count": {str(k): v for k, v in sorted(branch_counts.items())}}


def make_fixture(n, skeleton, targets):
    """Only a fixture builder; formal/dense engines verify its resulting word."""
    z = [1, 2]
    history = [tuple(z)]
    for op in skeleton:
        if op[0] == "C":
            z[0] ^= z[1]
        else:
            z[op[2]] ^= 1 << (op[1] + 2)
        history.append(tuple(z))
    slots = [[] for _ in history]
    pairs = []
    for i, mask in enumerate(targets):
        found = None
        for s, t in combinations(range(len(history)), 2):
            for p, q in product(range(2), repeat=2):
                if history[s][p] ^ history[t][q] == mask << 2:
                    found = (s, p, t, q)
                    break
            if found is not None:
                break
        need(found is not None, "fixture target unavailable")
        s, p, t, q = found
        slots[s].append(["A", i, p])
        slots[t].append(["A", i, q])
        pairs.append(list(found))
    word = []
    for i, events in enumerate(slots):
        word.extend(events)
        if i < len(skeleton):
            word.append(skeleton[i])
    return {"sources": n, "targets": targets, "skeleton": skeleton,
            "readout_pairs": pairs, "word": word}


def formal_fixture(item):
    n, targets = item["sources"], item["targets"]
    roles = [f"x{j}" for j in range(n)] + [f"y{i}" for i in range(len(targets))] + ["z0", "z1"]
    initial = {r: {(r,)} for r in roles}
    expected = {r: set(poly) for r, poly in initial.items()}
    for i, mask in enumerate(targets):
        for j in range(n):
            if mask & (1 << j):
                expected[f"y{i}"].add((f"A{i}", f"B{j}", f"x{j}"))
    def replay(state, word):
        state = {r: set(poly) for r, poly in state.items()}
        for op in word:
            if op[0] == "C":
                source, target, coefficient = "z1", "z0", ()
            elif op[0] == "B":
                source, target, coefficient = f"x{op[1]}", f"z{op[2]}", (f"B{op[1]}",)
            else:
                source, target, coefficient = f"z{op[2]}", f"y{op[1]}", (f"A{op[1]}",)
            state[target].symmetric_difference_update({coefficient + term for term in state[source]})
        return state
    actual = replay(initial, item["word"])
    need(actual == expected, "free noncommutative map / dirty restoration")
    need(replay(actual, reversed(item["word"])) == initial, "formal inverse")
    return len(roles)


def fixtures(other):
    tiny = [["C"], ["B", 1, 1], ["C"], ["B", 0, 0],
            ["B", 0, 0], ["C"], ["B", 1, 1], ["C"]]
    old = [0, 1, 2, 0, 3, 1, 4, 2, 3, 4]
    near = [["C"], ["C"]] + [["B", j, 0] for j in old] + [["C"], ["C"]]
    cases = {"two_source_universal": make_fixture(2, tiny, [1, 2, 3]),
             "five_source_31_masks": make_fixture(5, near, [m for m in range(1, 32) if m != 21])}
    result = {}
    for name, case in cases.items():
        count = formal_fixture(case)
        need(Counter(op[1] for op in case["word"] if op[0] == "B") ==
             Counter({j: 2 for j in range(case["sources"])}), "fixture B incidence")
        need(Counter(op[1] for op in case["word"] if op[0] == "A") ==
             Counter({i: 2 for i in range(len(case["targets"]))}), "fixture A incidence")
        dense_columns = noncommuting = 0
        for width, bank in product(range(1, 5), range(2)):
            columns, nc = other.dense_replay(case["sources"], case["targets"], case["word"], width, bank)
            dense_columns += columns
            noncommuting += nc
        need(noncommuting > 0, "dense bank accidentally entirely commuting")
        result[name] = {**case, "independent_dirty_rows": count,
                        "dense_forward_columns": dense_columns, "dense_inverse_columns": dense_columns,
                        "noncommuting_basis_witnesses": noncommuting}
    controls = {}
    base = cases["two_source_universal"]
    for kind in ("A", "B", "C"):
        failures = 0
        for index, op in enumerate(base["word"]):
            if op[0] != kind:
                continue
            changed = {**base, "word": base["word"][:index] + base["word"][index + 1:]}
            try:
                formal_fixture(changed)
            except ValueError:
                failures += 1
        need(failures == sum(op[0] == kind for op in base["word"]), "undetected omitted " + kind)
        controls["omit_each_" + kind] = failures
    changed = json.loads(json.dumps(base))
    first = next(op for op in changed["word"] if op[0] == "A")
    first[2] ^= 1
    try:
        formal_fixture(changed)
    except ValueError:
        controls["wrong_readout_port"] = True
    else:
        raise ValueError("wrong-port control escaped")
    dirty = [1 | (1 << 2), 2 | (1 << 3)]
    need((dirty[0] ^ dirty[1]) >> 2 == 3 and (dirty[0] ^ dirty[1]) & 3 == 3,
         "clean-input shortcut control")
    controls["discarding_dirt_fakes_a_mixed_mask"] = True
    need(21 not in differences(old) and len(differences(old)) == 31,
         "five-source positive fixture misses the required mask")
    return result, controls


def run():
    predecessor = sources()
    other = independent()
    old = old_boundary(other, predecessor)
    phases = phase_census(other)
    small = [small_census(n, other) for n in range(1, 4)]
    positive, controls = fixtures(other)
    port_pairs = 0
    for p, a, q, b in product(range(2), repeat=4):
        first = 1 if p == 0 else 2 ^ a
        second = 1 if q == 0 else 2 ^ b
        cancels = first == second
        need(cancels == (p == q and (p == 0 or a == b)), "two-B port-restoration reduction")
        port_pairs += cancels
    backend = []
    for width in range(1, 6):
        b0, b1 = 36 * width, 37 * width
        for bit in range(38 * width):
            initial = [int(i == bit) for i in range(38 * width)]
            expected = initial[:]
            for k in range(width):
                expected[b0 + k] ^= initial[b1 + k]
            actual, bill = other.transfer_backend(width, b0, b1, initial)
            need(actual == expected, "physical transfer dirty-tape column")
            restored, reverse_bill = other.transfer_backend(width, b0, b1, actual)
            need(restored == initial and reverse_bill == bill, "physical transfer inverse invoice")
            need(bill["cell_register_xors"] == 3 * width and
                 bill["head_steps"] == 77 * width * width - width and
                 bill["primitive_dispatches"] == 77 * width * width + 2 * width,
                 "unpaid scalar/head/dispatch work")
        backend.append({"width": width, "all_dirty_basis_columns": 38 * width, **bill})
    return {"schema": "four-transfer-obstruction-v1", "base": BASE,
            "status": "PASS_FOUR_TRANSFER_OBSTRUCTION", "old_boundary": old,
            "phase_census": phases, "small_four_transfer_census": small,
            "five_source_coverage_upper_by_port1_count": [31, 31, 25, 17, 19, 31],
            "five_source_maximum_coverage_including_zero": 31,
            "minimum_transfer_lower_bound_at_two_calls_per_operator": 6,
            "two_B_restoration_pairs_out_of_16": port_pairs,
            "illustrative_transfer_backend": backend,
            "positive_fixtures": positive, "failure_controls": controls,
            "scope": "two dirty roots; one-way C; read-only sources; exactly two calls per active A/B; no six-transfer sufficiency or new kappa"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-expected", action="store_true", help="explicitly regenerate the local receipt")
    args = parser.parse_args()
    report = run()
    path = HERE / "EXPECTED.json"
    if args.write_expected:
        path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        need(canonical(report) == canonical(read_json(path)), "receipt mismatch")
    print(report["status"], "max_coverage=31", "transfers>=6", "receipt_sha256=" + sha256(canonical(report).encode()).hexdigest())


if __name__ == "__main__":
    main()
