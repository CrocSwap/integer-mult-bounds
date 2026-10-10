"""Bind the inherited 25 retimings to an otherwise unchanged scalar core.

Only zero-frame compensation reads (category 4) and explicitly checked kernel
basis operations (28, 29) may differ. Every other scalar/COPY event, including
its frame and order, must agree with the freshly replayed baseline.
"""
from pathlib import Path
import hashlib
import json
import struct


def rebind(baseline_word, candidate_word, original_selection, output):
    baseline_word, candidate_word = Path(baseline_word), Path(candidate_word)
    old_bytes, new_bytes = baseline_word.read_bytes(), candidate_word.read_bytes()
    record = struct.Struct("<6i")
    old = [e for e in record.iter_unpack(old_bytes) if e[0]]
    new = [e for e in record.iter_unpack(new_bytes) if e[0]]
    excluded = {4, 28, 29}
    old_core = [(i, e) for i, e in enumerate(old)
                if not (e[0] == 1 and e[5] in excluded)]
    new_core = [(i, e) for i, e in enumerate(new)
                if not (e[0] == 1 and e[5] in excluded)]
    assert [e for _, e in old_core] == [e for _, e in new_core]
    mapping = {i: j for (i, _), (j, _) in zip(old_core, new_core)}
    selection = json.loads(Path(original_selection).read_text())
    assert hashlib.sha256(old_bytes).hexdigest() == selection["input_record_sha256"]
    for entry in selection["entries"]:
        old_index = entry["gate"]
        entry["gate"] = mapping[old_index]
        assert old[old_index] == new[entry["gate"]]
    output = Path(output)
    replay = json.loads((candidate_word.parent / "COHORT249-REPLAY.json").read_text())
    selection["input_record_sha256"] = hashlib.sha256(new_bytes).hexdigest()
    selection["input_record_count"] = len(new_bytes) // record.size
    selection["expected_rank_mass"] = replay["new_rank_mass"]
    selection["expected_scalar_additions"] = sum(e[0] == 1 for e in new)
    output.write_text(json.dumps(selection, indent=2) + "\n")
    return dict(status="PASS_UNCHANGED_ORIGINAL_CORE_EVENT_ALIGNMENT",
                events_compared=len(old_core), gate_count=len(selection["entries"]),
                baseline_pre_descent_sha256=hashlib.sha256(old_bytes).hexdigest(),
                candidate_pre_descent_sha256=hashlib.sha256(new_bytes).hexdigest())
