"""Exhaust and verify at-most-four-wire rewrites of the pinned R420 cleanup.

Jeffrey Cox, with substantial OpenAI assistance; Apache-2.0.
Run from any directory with Python 3.11+: python3 -I -B /path/to/verify.py
"""

from __future__ import annotations

import argparse
import copy
import gzip
import hashlib
import importlib.util
import json
import struct
import subprocess
import sys
import tempfile
from collections import Counter, deque
from itertools import permutations
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
Gate = tuple[int, int]
Matrix = tuple[int, ...]


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    need(spec is not None and spec.loader is not None, f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_source() -> tuple[dict, dict]:
    pins = json.loads((HERE / "SOURCE.json").read_text())
    for relative, expected in pins["files_sha256"].items():
        actual = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
        need(actual == expected, f"source pin mismatch: {relative}")
    word = json.loads(gzip.decompress((ROOT / pins["word"]).read_bytes()))
    need(hashlib.sha256(canonical(word)).hexdigest() == pins["word_canonical_sha256"],
         "word canonical hash mismatch")
    need(word["v"] == 120 and word["R"] == 420 and word["h"] == 8, "wrong word")
    need(all(f == 1 for f, _, _ in word["C"]), "cleanup is not all FULL")
    return word, pins


def shortest_tables():
    tables, parents = {}, {}
    for width in (2, 3, 4):
        identity = tuple(1 << i for i in range(width))
        distance, parent = {identity: 0}, {}
        queue = deque([identity])
        generators = list(permutations(range(width), 2))
        while queue:
            matrix = queue.popleft()
            for target, source in generators:
                successor = list(matrix)
                successor[target] ^= successor[source]
                successor = tuple(successor)
                if successor not in distance:
                    distance[successor] = distance[matrix] + 1
                    parent[successor] = matrix, (target, source)
                    queue.append(successor)
        tables[width], parents[width] = distance, parent
    return tables, parents


def search(gates: list[Gate], tables: dict, parents: dict) -> dict:
    census, candidates = Counter(), []
    for start in range(len(gates)):
        registers: set[int] = set()
        for last in range(start, len(gates)):
            registers.update(gates[last])
            if len(registers) > 4:
                break  # The union only grows: all later windows are out of scope.
            labels = sorted(registers)
            index = {label: i for i, label in enumerate(labels)}
            matrix = [1 << i for i in range(len(labels))]
            for target, source in gates[start:last + 1]:
                matrix[index[target]] ^= matrix[index[source]]
            endpoint = tuple(matrix)
            saving = last + 1 - start - tables[len(labels)][endpoint]
            census[len(labels), saving] += 1
            if saving:
                path = []
                while endpoint in parents[len(labels)]:
                    endpoint, gate = parents[len(labels)][endpoint]
                    path.append([labels[i] for i in gate])
                candidates.append({"start": start, "stop": last + 1, "registers": labels,
                                       "old": [list(g) for g in gates[start:last + 1]],
                                       "new": list(reversed(path)), "saving": saving})

    # Maximum saving among disjoint ORIGINAL intervals. Equal-score ties skip
    # the current position; otherwise the first (shortest) stop wins.
    by_start: dict[int, list[dict]] = {}
    for candidate in candidates:
        by_start.setdefault(candidate["start"], []).append(candidate)
    best = [0] * (len(gates) + 1)
    choice = {}
    for start in reversed(range(len(gates))):
        best[start] = best[start + 1]
        for candidate in by_start.get(start, []):
            score = candidate["saving"] + best[candidate["stop"]]
            if score > best[start]:
                best[start], choice[start] = score, candidate
    windows, position = [], 0
    while position < len(gates):
        if position in choice:
            windows.append(choice[position])
            position = choice[position]["stop"]
        else:
            position += 1
    return {"width": 4, "original_xors": len(gates),
                "windows_examined": sum(census.values()), "shorter_windows": len(candidates),
                "census": [{"wires": w, "saving": s, "count": n} for (w, s), n in sorted(census.items())],
                "distance_layers": {str(w): {str(d): n for d, n in sorted(Counter(t.values()).items())}
                                 for w, t in tables.items()},
                "saving": best[0], "windows": windows}


def replace_cleanup(word: dict, windows: list[dict]) -> dict:
    gates = [(target, source) for _, target, sources in word["C"] for source in sources]
    replacement, position = [], 0
    for window in windows:
        replacement.extend(gates[position:window["start"]])
        replacement.extend(window["new"])
        position = window["stop"]
    replacement.extend(gates[position:])
    result = copy.deepcopy(word)
    result["C"] = [[1, target, [source]] for target, source in replacement]
    return result


def prefix(records: list[tuple], size: int, reverse: bool) -> int:
    values = [1] * (size + 1)
    peak, active = 1, None
    stream = reversed(records) if reverse else iter(records)
    for kind, a, b, coefficient, _, _ in stream:
        if kind == 0:
            continue
        if reverse and kind in (2, 3):
            kind = 5 - kind
        if kind == 1:
            values[a] += abs(coefficient) * values[b]
            peak = max(peak, values[a])
        elif kind == 2:
            need(active is None, "nested prefix copy")
            values[b], active = values[a], (a, b)
        else:
            need(active == (a, b), "prefix copy mismatch")
            values[b], active = 0, None
    need(active is None, "unclosed prefix copy")
    return peak


def audit_records(records: list[tuple], model) -> dict:
    """Replay actual exporter bytes, including every MOVE and COPY/ERASE."""
    word, size = model.w, model.n
    current = list(word["start"]) + [model.ZERO]
    values = [1 << r for r in range(size)] + [0]
    paths = [[] for _ in range(size)]
    histogram, operations, phases = Counter(), Counter(), Counter()
    copies, active = [], None
    for kind, a, b, c, f, z in records:
        need(0 <= a <= size, "bad native destination")
        operations[kind] += 1
        if kind == 0:
            need(a < size and current[a] == b and z == 0, "wrong MOVE source frame or reserved field")
            need(model.nested(b, c) and model.fdim[c] - model.fdim[b] == f and f > 0,
                 "non-nested or mispriced MOVE")
            current[a] = c
            paths[a].append((b, c, f))
            histogram[f] += 1
        elif kind == 1:
            need(0 <= b <= size and a != b and c == 1, "bad native ADD")
            need(current[a] == current[b] == f, "ADD operands not in a common frame")
            need(a < size and (b < size or active is not None), "inactive temporary ADD")
            need(active is None or a != active[0], "copied source mutated")
            values[a] ^= values[b]
            phases[z] += 1
        elif kind == 2:
            need(active is None and b == size and current[a] == c and f == model.ZERO,
                 "invalid COPY")
            need(z == model.fdim[c], "mispriced COPY")
            values[b], current[b], active = values[a], f, (a, b, c, f)
            histogram[z] += 1
            copies.append((kind, a, b, c, f, z))
        elif kind == 3:
            need(active == (a, b, c, f) and current[a] == c and current[b] == f and z == 0,
                 "invalid ERASE")
            need(values[b] == values[a], "copied centre changed before ERASE")
            values[b], active = 0, None
            copies.append((kind, a, b, c, f, z))
        else:
            raise ValueError("unknown native operation")
    need(active is None and values[size] == 0, "unclosed native copy")
    need(current[:size] == word["final"], "wrong native final frames")
    expected = [1 << r for r in range(size)]
    for source in range(word["v"]):
        expected[word["v"] + source] ^= 1 << source
    need(values[:size] == expected, "native arbitrary-input identity failed")
    forward, backward = prefix(records, size, False), prefix(records, size, True)
    payload = 64 * forward**3 * backward**2
    return {"records": len(records), "adds": operations[1], "moves": operations[0],
                "copies": operations[2], "erasures": operations[3],
                "paid_histogram": {str(k): v for k, v in sorted(histogram.items())},
                "rank_mass": sum(k * v for k, v in histogram.items()),
                "phase_adds": {str(k): v for k, v in sorted(phases.items())},
                "forward_prefix": forward, "reverse_prefix": backward,
                "payload_upper": str(payload), "payload_bits": payload.bit_length(),
                "paths": paths, "copy_records": copies}


def export_and_audit(word: dict, model, pins: dict, output: Path) -> tuple[dict, list]:
    output.mkdir()
    path = output / "word.json"
    path.write_bytes(canonical(word) + b"\n")
    result = subprocess.run([sys.executable, "-I", "-B", str(ROOT / pins["exporter"]),
                             str(path), str(output / "records")],
                            check=True, capture_output=True, text=True)
    need("exported" in result.stdout, "native exporter did not report completion")
    data = (output / "records/249-records.bin").read_bytes()
    need(len(data) % 24 == 0, "truncated native records")
    records = list(struct.iter_unpack("<6i", data))
    report = audit_records(records, model)
    return report, records


def expect_rejection(label: str, action) -> str:
    try:
        action()
    except (ValueError, AssertionError):
        return label
    raise ValueError(f"negative control was accepted: {label}")


def run(output: Path) -> dict:
    word, pins = load_source()
    gates = [(target, source) for _, target, sources in word["C"] for source in sources]
    tables, parents = shortest_tables()
    computed = search(gates, tables, parents)
    certificate = json.loads((HERE / "CERTIFICATE.json").read_text())
    need(computed == certificate, "certificate differs from exhaustive deterministic search")
    independent = load_module("r420_independent", HERE / "independent.py")
    distance_evidence = independent.verify_distances(tables)
    window_evidence = independent.verify_windows(gates, certificate["windows"])
    independent_census = independent.census(gates)
    need(independent_census["windows_checked"] == certificate["windows_examined"], "independent window count")
    need(independent_census["shortenable_windows"] == certificate["shorter_windows"], "independent shorter-window count")
    need(independent_census["optimal_disjoint_original_window_saving"] == certificate["saving"], "independent packing optimum")
    gaps, widths, shorter = Counter(), Counter(), Counter()
    for entry in certificate["census"]:
        gaps[str(entry["saving"])] += entry["count"]
        widths[str(entry["wires"])] += entry["count"]
        if entry["saving"]:
            shorter[str(entry["wires"])] += entry["count"]
    need(dict(gaps) == independent_census["saving_histogram"], "independent gap census")
    for width, evidence in independent_census["by_width"].items():
        need(widths[width] == evidence["windows"] and shorter[width] == evidence["shortenable"],
             "independent census by width")
    changed = replace_cleanup(word, certificate["windows"])
    need(all(word[k] == changed[k] for k in word if k != "C"), "change outside C")

    xcheck = load_module("r420_xcheck", ROOT / pins["xcheck"])
    original_model, changed_model = xcheck.Word(word), xcheck.Word(changed)
    labels = original_model.labels()  # All label/frame data is pinned and unchanged.
    original_model.full()
    changed_model.full()
    original_h, original_c, _ = original_model.interface()
    changed_h, changed_c, _ = changed_model.interface()
    need(all(original_h.values()) and all(original_c.values()), "baseline interface")
    literal = "H4_C_literal_reverse_at_full"
    need(not changed_h[literal], "literal-reversal guard unexpectedly accepts rewrite")
    need(all(v for k, v in changed_h.items() if k != literal) and all(changed_c.values()),
         "semantic H4-prime interface failed")
    before, original_records = export_and_audit(word, original_model, pins, output / "original")
    after, changed_records = export_and_audit(changed, changed_model, pins, output / "rewritten")
    for key in ("paths", "copy_records", "paid_histogram", "rank_mass", "moves", "copies", "erasures"):
        need(before[key] == after[key], f"changed paid work: {key}")
    need(before["adds"] - after["adds"] == certificate["saving"], "incorrect complete XOR saving")
    need(after["forward_prefix"] <= before["forward_prefix"] and
         after["reverse_prefix"] <= before["reverse_prefix"], "larger native prefix envelope")
    need(int(after["payload_upper"]) < 1 << 104, "native payload exceeds inherited ceiling")

    controls = []
    first = certificate["windows"][0]
    broken = copy.deepcopy(certificate["windows"])
    broken[0]["new"].pop()
    broken[0]["saving"] += 1  # Keep the cost declaration honest; the map must fail.
    controls.append(expect_rejection("dropped replacement XOR", lambda: independent.verify_windows(gates, broken)))
    swapped = copy.deepcopy(certificate["windows"])
    swapped[0]["new"][0].reverse()
    controls.append(expect_rejection("reversed source and destination", lambda: independent.verify_windows(gates, swapped)))
    controls.append(expect_rejection("overlapping windows", lambda: independent.verify_windows(gates, [first, first])))
    forged = {k: dict(v) for k, v in tables.items()}
    nonidentity = next(m for m, d in forged[2].items() if d == 1)
    forged[2][nonidentity] += 2  # Still positive, but inconsistent with a one-gate edge.
    controls.append(expect_rejection("forged distance potential", lambda: independent.verify_distances(forged)))
    incomplete = {k: dict(v) for k, v in tables.items()}
    del incomplete[2][nonidentity]
    controls.append(expect_rejection("missing GL state", lambda: independent.verify_distances(incomplete)))
    outside = copy.deepcopy(certificate["windows"])
    outside[0]["new"][0][0] = original_model.n
    controls.append(expect_rejection("undeclared ancillary register", lambda: independent.verify_windows(gates, outside)))
    mutated_records = list(changed_records)
    move_index = next(i for i, r in enumerate(mutated_records) if r[0] == 0)
    record = list(mutated_records[move_index])
    record[4] -= 1
    mutated_records[move_index] = tuple(record)
    controls.append(expect_rejection("unpaid frame rank", lambda: audit_records(mutated_records, changed_model)))
    controls.append(expect_rejection("missing cleanup", lambda: audit_records(
        [r for r in original_records if not (r[0] == 1 and r[5] == 5)], original_model)))
    for report in (before, after):
        report.pop("paths")
        report.pop("copy_records")
    report = {"status": "PASS_R420_FOUR_WIRE_CLEANUP", "base_commit": pins["base_commit"],
                  "seed": 17, "saving": certificate["saving"], "selected_windows": len(certificate["windows"]),
                  "windows_examined": certificate["windows_examined"],
                  "independent_distances": distance_evidence, "independent_windows": window_evidence,
                  "independent_census": independent_census, "labels": labels,
                  "original": before, "rewritten": after, "negative_controls": controls,
                  "rewritten_word_canonical_sha256": hashlib.sha256(canonical(changed)).hexdigest(),
                  "literal_H4": False, "semantic_H4_prime": True, "all_input_columns": original_model.n}
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, help="retain generated word, native records and report in a NEW directory")
    arguments = parser.parse_args()
    if arguments.out is None:
        with tempfile.TemporaryDirectory(prefix="r420-four-wire-") as temporary:
            report = run(Path(temporary))
    else:
        arguments.out.mkdir(parents=True, exist_ok=False)
        report = run(arguments.out)
        (arguments.out / "REPORT.json").write_text(json.dumps(report, indent=2) + "\n")
    expected = json.loads((HERE / "EXPECTED.json").read_text())
    need(report == expected, "verification receipt differs from EXPECTED.json")
    print(f"{report['status']}: {report['selected_windows']} windows, {report['saving']} XORs saved; "
          f"{report['original']['adds']} -> {report['rewritten']['adds']} native ADDs; "
          f"{len(report['negative_controls'])} negative controls rejected")


if __name__ == "__main__":
    main()
