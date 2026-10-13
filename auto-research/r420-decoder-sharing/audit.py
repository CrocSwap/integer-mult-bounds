"""Independent set-valued audit of a bitE8 phase-A decoder rewrite.

No construction or upstream checker is imported. Geometry is inherited from the
pinned baseline: equality of every register's frame path transfers its legality.
Positive bounds below concern the scalar word, not the hosted/cohort invoice.
Prepared for Sagar Thakrar with substantial OpenAI Codex assistance; Apache-2.0.
"""

import argparse
import gzip
import json


def _load(path):
    with (gzip.open(path, "rt") if str(path).endswith(".gz") else open(path)) as stream:
        return json.load(stream)


def _check_shape(word):
    n = 2 * word["v"] + word["R"]
    frames = word["frames"]
    if len(word["start"]) != n or len(word["final"]) != n:
        raise ValueError("register frame table length")
    if any(type(f) is not int or not 0 <= f < len(frames)
           for f in word["start"] + word["final"]):
        raise ValueError("register frame index")
    for section in "DABC":
        for i, gate in enumerate(word[section]):
            if len(gate) != 3:
                raise ValueError(f"{section}[{i}]: malformed gate")
            frame, destination, sources = gate
            registers = [destination] + sources
            if type(frame) is not int or not 0 <= frame < len(frames):
                raise ValueError(f"{section}[{i}]: frame index")
            if (not sources or any(type(r) is not int or not 0 <= r < n for r in registers)
                    or len(set(registers)) != len(registers)):
                raise ValueError(f"{section}[{i}]: operands")
    if len(word["scatter"]) != word["v"]:
        raise ValueError("scatter target count")
    if any(type(r) is not int or not 2 * word["v"] <= r < n for r in word["ret"]):
        raise ValueError("retained register index")
    for row in word["scatter"]:
        if (len(set(row)) != len(row)
                or any(type(k) is not int or not 0 <= k < len(word["ret"]) for k in row)):
            raise ValueError("scatter operand index")
    return n


def _events(word, sections):
    for section in sections:
        if section == "scatter":
            for t, row in enumerate(word["scatter"]):
                for k in row:
                    yield None, word["v"] + t, [word["ret"][k]]
        else:
            yield from word[section]


def _symbolic(word, sections):
    values = [{r} for r in range(2 * word["v"] + word["R"])]
    for _, destination, sources in _events(word, sections):
        for source in sources:
            values[destination].symmetric_difference_update(values[source])
    return values


def _paths(word):
    paths = [[f] for f in word["start"]]
    for frame, destination, sources in _events(word, ("D", "A", "scatter", "B", "C")):
        if frame is not None:
            for register in [destination] + sources:
                if paths[register][-1] != frame:
                    paths[register].append(frame)
    for register, frame in enumerate(word["final"]):
        if paths[register][-1] != frame:
            paths[register].append(frame)
    return paths


def _positive_bounds(word):
    """Exact 1/infinity norms of the matrix obtained by replacing XOR with +.

    Forward multiplication of all ones gives row sums. Reversed transposed
    updates give column sums, using arbitrary-precision integers in both cases.
    """
    events = list(_events(word, ("D", "A", "scatter", "B", "C")))
    n = 2 * word["v"] + word["R"]
    rows, columns = [1] * n, [1] * n
    for _, destination, sources in events:
        rows[destination] += sum(rows[source] for source in sources)
    for _, destination, sources in reversed(events):
        for source in sources:
            columns[source] += columns[destination]
    return {"max_row_sum": max(rows), "max_column_sum": max(columns),
            "row_sum_bits": max(rows).bit_length(), "column_sum_bits": max(columns).bit_length()}


def _interface(word):
    v = word["v"]
    zeros = [i for i, frame in enumerate(word["frames"]) if not frame]
    fulls = [i for i, frame in enumerate(word["frames"]) if set(frame) == set(range(v))]
    if len(zeros) != 1 or len(fulls) != 1:
        raise ValueError("unique zero/full frame required")
    zero, full = zeros[0], fulls[0]
    is_target = lambda r: v <= r < 2 * v
    reverse = [[full, destination, sources] for section in ("A", "B")
               for _, destination, sources in word[section] if not is_target(destination)]
    return {
        "H1_no_target_feeds_z": all(is_target(d) or all(not is_target(s) for s in sources)
                                    for section in "DABC" for _, d, sources in word[section]),
        "H2_D_frame0_targets_from_helpers": (
            all(f == zero and is_target(d) and all(s >= 2 * v for s in sources)
                for f, d, sources in word["D"])
            and all(f == zero for f in word["start"][v:])),
        "H3_A_writes_z": all(not is_target(d) for _, d, _ in word["A"]),
        "H4_C_literal_reverse_at_full": (word["C"] == reverse[::-1]
                                           and all(f == full for r, f in enumerate(word["final"])
                                                   if not is_target(r))),
    }


def compare(baseline, candidate):
    """Return a JSONable comparison; malformed words raise ValueError.

    Inputs may be decoded word dictionaries or paths to JSON/JSON.gz files.
    Failed mathematical checks return status FAIL. A PASS verifies this rewrite
    relative to the baseline, not the full theorem.
    """
    baseline = baseline if isinstance(baseline, dict) else _load(baseline)
    candidate = candidate if isinstance(candidate, dict) else _load(candidate)
    n = _check_shape(baseline)
    if _check_shape(candidate) != n:
        raise ValueError("register count changed")
    unchanged = {key: baseline.get(key) == candidate.get(key)
                 for key in sorted((set(baseline) | set(candidate)) - {"A", "C"})}
    maps_a = [_symbolic(word, ("A",)) for word in (baseline, candidate)]
    maps_full = [_symbolic(word, ("D", "A", "scatter", "B", "C"))
                 for word in (baseline, candidate)]
    expected = [{r, r - baseline["v"]} if baseline["v"] <= r < 2 * baseline["v"] else {r}
                for r in range(n)]
    paths = [_paths(word) for word in (baseline, candidate)]
    differing_a = [r for r in range(n) if maps_a[0][r] != maps_a[1][r]]
    differing_paths = [r for r in range(n) if paths[0][r] != paths[1][r]]
    interfaces = {name: _interface(word) for name, word in (("baseline", baseline), ("candidate", candidate))}
    checks = {
        "only_A_and_C_changed": all(unchanged.values()),
        "whole_A_operator_equal": not differing_a,
        "full_operator_equal": maps_full[0] == maps_full[1],
        "baseline_full_operator_is_target_add": maps_full[0] == expected,
        "candidate_full_operator_is_target_add": maps_full[1] == expected,
        "all_register_frame_paths_equal": not differing_paths,
        "interface_checks_hold": all(all(value.values()) for value in interfaces.values()),
    }
    counts = {}
    for name, word in (("baseline", baseline), ("candidate", candidate)):
        counts[name] = {
            "gates": {section: len(word[section]) for section in "DABC"},
            "adds": {section: sum(len(g[2]) for g in word[section]) for section in "DABC"},
            "scatter_adds": sum(len(row) for row in word["scatter"]),
        }
    return {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "scope": "relative scalar-word rewrite; baseline geometry and hosted realization inherited",
        "symbolic_columns": n,
        "checks": checks,
        "changed_immutable_keys": [key for key, same in unchanged.items() if not same],
        "different_A_output_registers": differing_a,
        "different_frame_path_registers": differing_paths,
        "interface": interfaces,
        "counts": counts,
        "scalar_ADD_saving_including_C": sum(counts["baseline"]["adds"].values())
                                           - sum(counts["candidate"]["adds"].values()),
        "positive_scalar_word_bounds": {name: _positive_bounds(word)
                                         for name, word in (("baseline", baseline), ("candidate", candidate))},
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline")
    parser.add_argument("candidate")
    args = parser.parse_args()
    report = compare(args.baseline, args.candidate)
    print(json.dumps(report, indent=2, sort_keys=True))
    raise SystemExit(0 if report["status"] == "PASS" else 1)
