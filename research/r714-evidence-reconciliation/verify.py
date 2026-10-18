#!/usr/bin/env python3
"""Source-bound reconciliation of the archived R714 local obligation.

Hanson Sun, with substantial OpenAI Codex assistance. Apache-2.0.
No historical producer, solver, or replay engine is imported.
"""
import argparse
from collections import Counter
from copy import deepcopy
from functools import lru_cache
import gzip
import hashlib
import json
from math import gcd
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE = Path("research/experiment-log/negative-searches")
HIERARCHY = ARCHIVE / "hierarchy-rewrites"
FOLLOWUP = ARCHIVE / "r714-kernels"


class Rejected(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise Rejected(message)


def canonical_sha(value):
    data = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(data).hexdigest()


def read_json(path):
    return json.loads(path.read_bytes())


def check_sources(root):
    pins = read_json(HERE / "INPUTS.json")
    expected = dict(pins["files"])
    reference = pins["interface_reference"]
    expected[reference["path"]] = reference["sha256"]
    for name, digest in expected.items():
        require(hashlib.sha256((root / name).read_bytes()).hexdigest() == digest,
                "source digest: " + name)
    return len(expected)


def check_inventory(names, ids):
    expected = {f"{case}/{kind}" for case in ids
                for kind in ("WORD.json.gz", "RESULT.json")}
    require(len(names) == len(set(names)), "duplicate archive member")
    require(set(names) == expected, "missing or unexpected archive member")


def check_archive(root):
    rows = read_json(root / HIERARCHY / "LEDGER.json")
    ids = {"baseline"} | {f"candidate-{i}" for i in range(424)}
    require(len(rows) == len(ids) and {r["id"] for r in rows} == ids,
            "ledger case coverage")
    ledger = {r["id"]: r for r in rows}
    inventory = read_json(root / HIERARCHY / "r715-hierarchy-rewrite-inventory/RESULT.json")
    require(len(inventory["candidates"]) == 424, "hierarchy alternative count")
    require(ledger["baseline"]["rule"] is None, "baseline rule")
    for i, rule in enumerate(inventory["candidates"]):
        require(ledger[f"candidate-{i}"]["rule"] == rule, "hierarchy rule binding")
    names, raw = [], None
    # Stream members, never extract or execute the archived payloads.
    with tarfile.open(root / HIERARCHY / "ALL-COMPILED-CASES.tar.gz", "r|gz") as archive:
        for member in archive:
            require(member.isfile(), "non-file archive member")
            names.append(member.name)
            parts = member.name.split("/")
            require(len(parts) == 2 and parts[0] in ids, "archive member path")
            case, kind = parts
            require(kind in ("WORD.json.gz", "RESULT.json"), "archive member kind")
            data = archive.extractfile(member).read()
            if kind == "RESULT.json":
                require(json.loads(data) == ledger[case], "archive result/ledger mismatch: " + case)
            else:
                word = json.loads(gzip.decompress(data))
                require(canonical_sha(word) == ledger[case]["word_sha256"],
                        "archive word/ledger mismatch: " + case)
                require(word["R"] == ledger[case]["helpers"], "helper-count binding")
                if case == "candidate-201":
                    raw = word
    check_inventory(names, ids)
    require(raw is not None, "missing raw nominee")
    counts = Counter(str(r["helpers"]) for r in rows)
    lower = sorted(r["id"] for r in rows if r["helpers"] < ledger["baseline"]["helpers"])
    summary = read_json(root / HIERARCHY / "SUMMARY.json")
    require(dict(counts) == summary["helper_counts"], "helper histogram")
    require(lower == summary["lower_helper_candidates"] == ["candidate-201"], "nominee list")
    require(summary["cases"] == 425 and summary["alternatives"] == 424
            and summary["alternatives_without_helper_reduction"] == 423
            and summary["execution_failures"] == 0 and summary["new_certified_bounds"] == 0,
            "hierarchy summary coverage")
    require(all(r["status"] == "PASS_COMPILER_F2_REUSE_RETIMING_PROFILE_ONLY" for r in rows),
            "unexpected archived screen status")
    require(read_json(root / HIERARCHY / "COMPLETE.json") ==
            {"status": "FINISHED", "cases": 425, "failed": 0, "min_helpers": 714},
            "hierarchy completion")
    return raw, {"cases": len(rows), "members": len(names),
                 "helper_counts": dict(sorted(counts.items())), "nominee": lower[0]}, names


def primitive(row):
    divisor = 0
    for x in row:
        divisor = gcd(divisor, x)
    if not divisor:
        return tuple(row)
    first = next(x for x in row if x)
    divisor *= 1 if first > 0 else -1
    return tuple(x // divisor for x in row)


def reduce_row(row, basis):
    row = tuple(row)
    for pivot in basis:
        col = next(i for i, x in enumerate(pivot) if x)
        if row[col]:
            row = primitive(tuple(pivot[col] * x - row[col] * y
                                  for x, y in zip(row, pivot)))
    return row


@lru_cache(maxsize=None)
def rational_basis(vectors):
    # Fraction-free integer row elimination represents the exact Q-span.
    basis = []
    for vector in vectors:
        row = primitive(reduce_row(vector, basis))
        if any(row):
            basis.append(row)
            basis.sort(key=lambda r: next(i for i, x in enumerate(r) if x))
    return tuple(basis)


@lru_cache(maxsize=None)
def contains(large, small):
    return all(not any(reduce_row(row, large)) for row in small)


def check_adjoint(word):
    """Propagate all output covectors backward, including every dirty helper."""
    v, n = word["v"], 2 * word["v"] + word["R"]
    dual = [1 << i for i in range(n)]

    def backward(gates):
        for _, dest, sources in reversed(gates):
            # The transpose of dest += source updates source's covector.
            for source in reversed(sources):
                dual[source] ^= dual[dest]

    backward(word["C"])
    backward(word["B"])
    # COPY snapshots only helpers; scatter writes only targets, so these
    # simultaneous reads have the same adjoint as the following updates.
    for target, indices in enumerate(word["scatter"]):
        for index in indices:
            dual[word["ret"][index]] ^= dual[v + target]
    backward(word["A"])
    backward(word["D"])
    for i, actual in enumerate(dual):
        expected = (1 << i) ^ ((1 << (v + i)) if i < v else 0)
        require(actual == expected, f"F2 adjoint: input register {i}")
    return n


def check_geometry(word):
    v, h, helpers = word["v"], word["h"], word["R"]
    require((v, h, helpers) == (120, 8, 714), "R714 dimensions")
    require((word["format"], word["coords"], word["form"]) ==
            ("bitE8/1", "ham", "<x,y>/2"), "word interface")
    n = 2 * v + helpers
    lines = tuple(tuple(row) for row in word["lines"])
    require(len(lines) == v and all(len(row) == h for row in lines), "label dimensions")
    frames = []
    for indices in word["frames"]:
        require(len(indices) == len(set(indices)) and all(0 <= i < v for i in indices), "frame labels")
        frames.append(rational_basis(tuple(lines[i] for i in indices)))
    require(len(word["start"]) == len(word["final"]) == n, "boundary lengths")
    require(all(0 <= f < len(frames) for f in word["start"] + word["final"]), "boundary frame")
    cur = [frames[f] for f in word["start"]]
    require(all(cur[i] == rational_basis((lines[i],)) for i in range(v)), "source starts")
    require(all(not f for f in cur[v:]), "target/helper starts")
    support = [1 << i if i < v else 0 for i in range(n)]
    allowed = [sum(1 << i for i, line in enumerate(lines)
                   if contains(frame, (line,))) for frame in frames]
    histogram = Counter()

    def move(reg, frame):
        require(contains(frame, cur[reg]), f"non-nested frame: register {reg}")
        difference = len(frame) - len(cur[reg])
        if difference:
            histogram[difference] += 1
        cur[reg] = frame

    def phase(name):
        for index, (frame_id, dest, sources) in enumerate(word[name]):
            require(0 <= frame_id < len(frames) and v <= dest < n
                    and all(0 <= s < n for s in sources)
                    and dest not in sources and len(sources) == len(set(sources)), "gate shape")
            frame = frames[frame_id]
            for reg in [dest] + sources:
                move(reg, frame)
            for source in sources:
                if not v <= source < 2 * v:
                    require(not support[source] & ~allowed[frame_id],
                            f"integer source support: {name}[{index}]")
                if dest >= 2 * v:
                    # In this pinned family no target feeds a helper. With
                    # positive ADDs, OR is exactly integer coefficient support.
                    require(not v <= source < 2 * v, "target-to-helper outside scope")
                    support[dest] |= support[source]
            if dest >= 2 * v:
                require(not support[dest] & ~allowed[frame_id], "integer helper support")

    phase("D")
    require(all(cur[i] == frames[word["start"][i]] for i in range(v, n)), "D frame boundary")
    phase("A")
    require(all(not cur[v + t] for t in range(v)), "scatter target frame")
    require(len(word["scatter"]) == v and len(set(word["ret"])) == len(word["ret"]), "COPY shape")
    for reg in word["ret"]:
        require(2 * v <= reg < n and len(cur[reg]) > 0, "COPY helper")
        histogram[len(cur[reg])] += 1
    require(all(0 <= i < len(word["ret"]) for row in word["scatter"] for i in row), "scatter index")
    phase("B")
    phase("C")
    for reg, frame_id in enumerate(word["final"]):
        move(reg, frames[frame_id])
        if v <= reg < 2 * v:
            normal = lines[reg - v]
            require(len(cur[reg]) == h - 1 and all(sum(a * b for a, b in zip(normal, row)) == 0
                                                for row in cur[reg]), "target final hyperplane")
        else:
            require(len(cur[reg]) == h, "source/helper final full frame")
    return {str(k): value for k, value in sorted(histogram.items())}


def check_local(word, receipt):
    require(canonical_sha(word) == receipt["word_sha256"], "local word/receipt binding")
    require(receipt["status"] == "PASS_EXACT_CHANGED_STOCK_LOCAL", "local receipt status")
    profile = check_geometry(word)
    columns = check_adjoint(word)
    require(profile == receipt["profile"], "local profile/receipt mismatch")
    require(columns == receipt["columns"] and word["R"] == receipt["helpers"], "local dimensions")
    return {"canonical_sha256": canonical_sha(word), "columns": columns, "profile": profile}


def negative_controls(raw, receipt, archive_names):
    outcomes = {}

    def rejects(name, thunk, reason):
        try:
            thunk()
        except Rejected as exc:
            require(reason in str(exc), f"wrong rejection for {name}: {exc}")
            outcomes[name] = str(exc)
        else:
            raise Rejected("control accepted: " + name)

    for name, field, reason in [("omit_dirty_compensation", "D", "F2 adjoint"),
                                 ("omit_helper_cleanup", "C", "F2 adjoint")]:
        bad = deepcopy(raw)
        bad[field] = []
        rejects(name, lambda: check_adjoint(bad), reason)
    bad = deepcopy(raw)
    bad["scatter"][0] = bad["scatter"][0][1:]
    rejects("omit_copy_operand", lambda: check_adjoint(bad), "F2 adjoint")
    bad = deepcopy(raw)
    bad["A"][0][0] = 0
    check_adjoint(bad)  # Scalar-preserving corruption must fail geometry.
    rejects("scalar_preserving_bad_frame", lambda: check_geometry(bad), "non-nested frame")
    bad = deepcopy(raw)
    bad["final"][raw["v"]] = 1
    check_adjoint(bad)
    rejects("scalar_preserving_bad_target_cap", lambda: check_geometry(bad), "target final hyperplane")
    bad_receipt = deepcopy(receipt)
    bad_receipt["profile"]["1"] += 1
    rejects("wrong_paid_profile", lambda: check_local(raw, bad_receipt), "local profile/receipt mismatch")
    bad_receipt = deepcopy(receipt)
    bad_receipt["word_sha256"] = "0" * 64
    rejects("wrong_word_binding", lambda: check_local(raw, bad_receipt), "local word/receipt binding")
    ids = {"baseline"} | {f"candidate-{i}" for i in range(424)}
    missing = [name for name in archive_names if name != "candidate-201/WORD.json.gz"]
    rejects("missing_archive_case", lambda: check_inventory(missing, ids), "missing")
    duplicate = archive_names + ["candidate-201/WORD.json.gz"]
    rejects("duplicate_archive_case", lambda: check_inventory(duplicate, ids), "duplicate")
    return outcomes


def reconcile(root):
    source_count = check_sources(root)
    raw, coverage, archive_names = check_archive(root)
    precursor = root / FOLLOWUP / "precursor"
    raw_receipt = read_json(precursor / "RAW-LOCAL.json")
    mixed = read_json(precursor / "MIXED.json")
    retimed = json.loads(gzip.decompress((precursor / "PRECURSOR.json.gz").read_bytes()))
    local = {name: check_local(word, read_json(precursor / (name + "-LOCAL.json")))
             for name, word in [("RAW", raw), ("MIXED", mixed), ("RETIMED", retimed)]}
    terminal = read_json(precursor / "RECEIPT.json")
    require(terminal["steps"] == ["RAW-LOCAL", "MIXED-LOCAL", "RETIMED-LOCAL"]
            and terminal["moves"] == 0
            and terminal["status"] == "PASS_R714_RAW_MIXED_RETIMED_LOCAL_ONLY", "terminal receipt")
    require(mixed == retimed, "zero-move retimed payload differs")
    trials = {}
    for group, expected_records in [("fresh", 20), ("transferred", 21)]:
        rows = read_json(root / FOLLOWUP / group / "LEDGER.json")
        complete = read_json(root / FOLLOWUP / group / "COMPLETE.json")
        require(len(rows) == expected_records == complete["records"] and complete["trials"] == 20,
                "kernel trial record count")
        labels = [r["label"]["trial"] for r in rows if "trial" in r["label"]]
        require(sorted(labels) == list(range(20)), "kernel trial ID coverage")
        trials[group] = {"records": len(rows), "trial_ids": sorted(labels),
                         "scope": "archived coverage only; no kernel, solver or hosting replay"}
    return {"status": "PASS_R714_EVIDENCE_RECONCILIATION", "pinned_files": source_count,
            "archive": coverage, "local_replays": local, "retiming_moves": 0,
            "kernel_ledger_coverage": trials,
            "negative_controls": negative_controls(raw, raw_receipt, archive_names),
            "scope": "425 archived case bindings and three finite R714 local replays (two distinct words); "
                     "no native, hosting, supplier, all-size or multiplication-theorem certification; no new kappa"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, help="write the deterministic receipt to this path")
    parser.add_argument("--check", action="store_true", help="compare with the committed EXPECTED.json")
    args = parser.parse_args()
    result = reconcile(args.root)
    if args.check:
        require(result == read_json(HERE / "EXPECTED.json"), "expected receipt mismatch")
    if args.output:
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(result["status"] + ": 425 case bindings; 3 local replays / 2 words; "
          f"{len(result['negative_controls'])} controls rejected; no new kappa")


if __name__ == "__main__":
    main()
