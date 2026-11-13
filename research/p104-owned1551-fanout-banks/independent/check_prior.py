"""Recheck the prior probe only, with no attempt to solve chart127 support."""
import argparse
from fractions import Fraction as F
import gzip
from hashlib import sha256
import json
from pathlib import Path
from runpy import run_path
from signal import alarm
from time import perf_counter

ENGINE = "62244f1b1c3e142f7ecf566d344f68c1b3362755e00663415f7277292bd18b34"
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--word", type=Path, required=True)
args = parser.parse_args()
start = perf_counter()
alarm(30)
script = Path(__file__).with_name("verify_first_outward.py")
assert sha256(script.read_bytes()).hexdigest() == ENGINE
engine = run_path(str(script))
archive = args.word.read_bytes()
assert sha256(archive).hexdigest() == engine["ARCHIVE"]
raw = gzip.decompress(archive)
assert sha256(raw).hexdigest() == engine["NATIVE"]
word = json.loads(raw)
tape = word["program"]
cut, source = engine["CUT"], engine["SOURCE"]
assert tape[source] == ["ADD", 1551, 862, "-1", 1091]
assert tape[cut - 1:cut + 1] == [
    ["MOVE", 878, 267, 127, False], ["ADD", 549, 878, "1", 127],
]
writes = engine["WRITES"]
first_outward = {}
for clock, event in enumerate(tape):
    if event[0] in ("ADD", "COPY") and event[2] in writes.values():
        first_write = next(i for i, role in writes.items() if role == event[2])
        if clock > first_write and event[2] not in first_outward:
            first_outward[event[2]] = clock
assert min(first_outward.values()) == cut
probe = {230: F(-1), 547: F(1)}
old, a, old_guards, old_bank = engine["forward"](word, probe, edited=False)
new, b, new_guards, new_bank = engine["forward"](word, probe, edited=True)
assert a == b == -1 and old_guards == new_guards and old_bank == new_bank
delta = {role: new.get(role, 0) - old.get(role, 0) for role in old.keys() | new.keys()}
delta = {role: val for role, val in delta.items() if val}
assert delta == {role: -1 for role in writes.values()}
affected = [role for role in new_bank if new.get(role, 0)]
assert len(affected) == 284
print(json.dumps({
    "status": "PASS_PRIOR_PROBE_INCONCLUSIVE_AND_CHRONOLOGY",
    "first_outward_by_recipient": first_outward, "edited_bank_size": len(new_bank),
    "old_source_response": a, "nonzero_edited_bank_ids": affected,
    "nonzero_edited_bank_count": len(affected), "old_minus_edited": {k: -v for k, v in delta.items()},
    "init_copy_guards_each": old_guards, "seconds": perf_counter() - start,
    "full_span_test_run": False, "cut_before": cut, "native_sha256": engine["NATIVE"],
}, sort_keys=True, indent=2, default=str))
alarm(0)
