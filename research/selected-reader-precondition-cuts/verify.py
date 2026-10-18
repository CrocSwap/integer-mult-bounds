#!/usr/bin/env python3
"""Exact selected centre-reader invariance through every precondition cut.

Ross Richardson with substantial OpenAI Codex assistance. Apache-2.0.
PR2491's authenticated typed-segment check is reused with attribution;
the covector, prefix-invariance and defect checks below are new.
"""
import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as F
import gzip
import hashlib
import importlib.util
import io
import itertools
import json
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE = "research/community-frontier1094-audit/selected-replay.tar.gz"
ARCHIVE_SHA = "f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6"
PREDECESSOR_HEAD = "c25a4ce22a887daf8cba8b3cfad72796752ab2ee"
PINS = {
    "PR2491-README.md": "6a164e931c003927b6af2a64d64be6398a93b8261e6d7abee6500a21438e603b",
    "PR2491-PROOF.md": "f79adc0917cbedcce60bacf8c88539050c3f9b8ce584c0b30e4912519eb72a15",
    "PR2491-RESULT.json": "8c4cfe3caaf745e9b2516b5583494c808fc435e8e00d1b8711c17c75ef29d5b3",
    "PR2491-verify.py": "b5f33336c218d46a717ccf913685217c0aff1dac9dba838f9d7e1f1a5ec132a2",
}
CENTRES = (92, 57, 81, 224, 11, 240, 9, 256)
NORMS = (150, 130, 146, 134, 122, 126, 142, 146)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def load(root=ROOT):
    """Authenticate all borrowed executable bytes before importing any of them."""
    raw = (root / ARCHIVE).read_bytes()
    need(sha(raw) == ARCHIVE_SHA, "immutable selected archive")
    provenance = json.loads((HERE / "PREDECESSOR.json").read_text())
    need(provenance["head"] == PREDECESSOR_HEAD, "predecessor head")
    for name, digest in PINS.items():
        need(provenance["files"][name]["sha256"] == digest, "predecessor manifest")
        need(sha((HERE / "inputs" / name).read_bytes()) == digest,
             "immutable predecessor bytes: " + name)
    spec = importlib.util.spec_from_file_location("credited_pr2491_typed_check", HERE / "inputs/PR2491-verify.py")
    predecessor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(predecessor)
    data = {}
    with tarfile.open(fileobj=io.BytesIO(raw), mode="r:gz") as archive:
        for name, digest in predecessor.MEMBERS.items():
            entries = [m for m in archive.getmembers() if m.name == predecessor.PREFIX + name]
            need(len(entries) == 1 and entries[0].isfile(), "unique selected member")
            blob = archive.extractfile(entries[0]).read()
            need(sha(blob) == digest, "immutable selected member: " + name)
            data[name] = json.loads(gzip.decompress(blob) if name.endswith(".gz") else blob)
    return data, predecessor


def pullback(rows, gate):
    """Right-compose row covectors with one target-first scalar gate."""
    target = gate[1][1]
    if gate[0] == "scale":
        coefficient = F(gate[2], gate[3])
        for row in rows:
            row[target] *= coefficient
    else:
        source, coefficient = gate[2][1], F(gate[3], gate[4])
        for row in rows:
            row[source] += coefficient * row[target]


def reconstruct(gates):
    rows = [[F(j == centre) for j in range(704)] for centre in CENTRES]
    for gate in reversed(gates):
        pullback(rows, gate)
    return rows


def invisible_writes(rows, prefix):
    for gate in prefix:
        target = gate[1][1]
        need(all(row[target] == 0 for row in rows), "reader-visible prefix write")


def scan_cuts(rows, prefix):
    """Every cut is checked; a constant table is stored as one exact interval."""
    current = deepcopy(rows)
    for gate in reversed(prefix):
        pullback(current, gate)
        need(current == rows, "changed reader at an earlier cut")
    return len(prefix) + 1


def paired_cycles():
    for perm in itertools.permutations(range(8)):
        unseen, lengths = set(range(8)), []
        while unseen:
            at, length = min(unseen), 0
            while at in unseen:
                unseen.remove(at)
                length += 1
                at = perm[at]
            lengths.append(length)
        if sorted(lengths) == [4, 4]:
            yield perm


def rejection_witnesses(norms):
    witnesses = []
    for perm in paired_cycles():
        failed = [i for i in range(8) if norms[i] != norms[perm[i]]]
        need(bool(failed), "paired cycle survives diagonal condition")
        witnesses.append([list(perm), failed[0]])
    need(len(witnesses) == 1260, "complete paired-cycle census")
    return witnesses


def expect_reject(fn, reason):
    try:
        fn()
    except ValueError as error:
        need(reason in str(error), "wrong rejection predicate: " + str(error))
    else:
        raise ValueError("mutation accepted: " + reason)


def controls(rows, prefix):
    altered = deepcopy(prefix)
    # This changes a genuine source program gate; 92 is a legal zero-frame
    # source-data field but now the write is visible to the centre reader.
    index = next(i for i, g in enumerate(altered) if g[0] == "add" and g[2][1] != 92)
    altered[index][1][1] = 92
    expect_reject(lambda: invisible_writes(rows, altered), "reader-visible prefix write")
    expect_reject(lambda: scan_cuts(rows, altered), "changed reader at an earlier cut")
    scaled = deepcopy(prefix)
    index = next(i for i, g in enumerate(scaled) if g[0] == "scale")
    scaled[index][1][1], scaled[index][2:] = 92, [2, 1]
    expect_reject(lambda: invisible_writes(rows, scaled), "reader-visible prefix write")
    expect_reject(lambda: scan_cuts(rows, scaled), "changed reader at an earlier cut")
    expect_reject(lambda: rejection_witnesses([56] * 8), "paired cycle survives")
    # Prefix sign and order changes are genuinely invisible, not rejection
    # controls. Accept the equivalent reader with every ADD sign reversed.
    equivalent = deepcopy(prefix)
    for gate in equivalent:
        if gate[0] == "add":
            gate[3] *= -1
    invisible_writes(rows, equivalent)
    need(scan_cuts(rows, list(reversed(equivalent))) == 7401, "equivalent prefix")
    # A general nonunitary prefix does not preserve Gram: diag(1..8) times
    # diag(1,1/2,..,1/8) is I, which admits every paired permutation.
    old = [[F((i + 1) if i == j else 0) for j in range(8)] for i in range(8)]
    early = deepcopy(old)
    for i in range(8):
        pullback(early, ["scale", ["L", i], 1, i + 1])
    need(early == [[F(i == j) for j in range(8)] for i in range(8)], "nonunitary changed-cut escape")
    rejection_witnesses([(i + 1) ** 2 for i in range(8)])
    expect_reject(lambda: rejection_witnesses([1] * 8), "paired cycle survives")
    # A noncommuting two-shear fixture makes inverse order and signs observable.
    g = [["add", ["L", 0], ["L", 1], 2, 1], ["add", ["L", 1], ["L", 0], 3, 1]]
    correct = [[F(1), F(0)], [F(0), F(1)]]
    for gate in reversed(g):
        pullback(correct, gate)
    need(correct == [[1, 2], [3, 7]], "noncommuting orientation fixture")
    wrong = [[F(1), F(0)], [F(0), F(1)]]
    for gate in g:
        pullback(wrong, gate)
    need(wrong != correct, "wrong-order control nonvacuity")
    wrong = deepcopy(correct)
    for gate in g:
        inverse = deepcopy(gate)
        inverse[3] *= -1
        pullback(wrong, inverse)
    need(wrong == [[1, 0], [0, 1]], "literal inverse signs")
    return {"rejected_semantic_faults": 6, "equivalent_prefix_sign_and_order": True,
            "generic_nonunitary_prefix_escape": True, "noncommuting_order_and_inverse_fixture": True}


def calculate():
    data, credited = load()
    gates, boundary = credited.typed_segment(data)
    program = data["LOCAL-PROGRAMS.json.gz"]["forward"]
    first = program.index(["phase", "entry_adapters"])
    prefix = [e[1] for e in program[:first] if e[0] == "scalar"]
    need(first == 7401 and len(prefix) == 7400, "exact prefix boundary")
    rows = reconstruct(gates)
    strings = [[str(x) for x in row] for row in rows]
    previous = json.loads((HERE / "inputs/PR2491-RESULT.json").read_text())
    need(strings == previous["reader"], "complete predecessor reader binding")
    writes = sorted({g[1][1] for g in prefix})
    need(writes == list(range(112, 224)), "all and only target-field writes")
    invisible_writes(rows, prefix)
    cuts = scan_cuts(rows, prefix)
    norm = [sum(x*x for x in row) for row in rows]
    need(norm == list(NORMS), "exact Gram diagonal")
    gram = [[sum(a*b for a, b in zip(r, s)) for s in rows] for r in rows]
    need([[str(x) for x in row] for row in gram] == previous["gram"], "complete predecessor Gram binding")
    witnesses = rejection_witnesses(norm)
    active = [j for j in range(704) if any(row[j] for row in rows)]
    touched = set(writes) | {g[2][1] for g in prefix if g[0] == "add"}
    word = data["CANONICAL-WORD.json.gz"]
    wrapped = {r for r in range(224, 704) if word["start"][r] != 0 or word["final"][r] != 1}
    need(not touched & wrapped and all(word["start"][r] == 0 for r in touched), "prefix frame calibration")
    return {"status": "PASS_SELECTED_READER_PRECONDITION_CUTS", "no_new_kappa": True,
            "predecessor_head": PREDECESSOR_HEAD, "archive_sha256": ARCHIVE_SHA,
            "member_sha256": credited.MEMBERS, "inherited_typed_boundary": boundary,
            "prefix_gates": len(prefix), "gate_kinds": dict(Counter(g[0] for g in prefix)),
            "prefix_write_fields": writes, "prefix_touched_fields": sorted(touched),
            "active_reader_columns": active, "reader": strings,
            "gram": [[str(x) for x in row] for row in gram], "row_norms": list(NORMS),
            "cut_intervals": [{"first": 0, "last": 7400, "count": cuts, "reader_sha256": sha(encoded(strings))}],
            "checked_reader_coefficients_per_cut": 5632, "paired_cycle_rejections": witnesses,
            "excluded_cut_cycle_pairs": cuts * len(witnesses), "controls": controls(rows, prefix),
            "scope": "Fixed selected eight-centre reader, all704 arbitrary fields, every zero-frame precondition cut. Native implication inherits PR2491 exact unitary-frame binding. No other cuts, output normalization, paid nonunitary actions, supplier or full theorem."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", action="store_true")
    args = parser.parse_args()
    result = calculate()
    content = json.dumps(result, sort_keys=True, indent=2) + "\n"
    output = HERE / "RESULT.json"
    if args.write_result:
        with output.open("x") as handle:
            handle.write(content)
    else:
        need(output.read_text() == content, "complete committed receipt mismatch")
    print("PASS_SELECTED_READER_PRECONDITION_CUTS cuts=7401 gates=7400 coefficients_per_cut=5632 paired_cycles=1260 no_new_kappa")


if __name__ == "__main__":
    main()
