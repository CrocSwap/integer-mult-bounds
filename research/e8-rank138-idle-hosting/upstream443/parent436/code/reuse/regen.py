"""Regenerate the word from pinned inputs.

  1. PR #370's producer, unchanged (ham2.build -> compile2 -> fullword.build), with our producer parameters
     (data/params/params-r740.json, found by discovery/search_params.py)            -> raw word (R = 863)
  2. reuse.reuse: helper-slot reuse by elimination of dead registers               -> reused word
  3. retime.retime: single-gate frame retiming (6 sweeps, M = 64)                  -> final word
Each word is written as PR #370's fullword.save does (sorted keys, compact JSON, gzip mtime 0).
usage: regen.py PARAMS.json OUT_RAW.json.gz OUT_REUSED.json.gz OUT_FINAL.json.gz OUT_LEDGER.json
OUT_LEDGER lists the inserted elimination gates (phase, index, kind) of the final word, for the negative controls.
Prepared by eumemic with Anthropic Claude assistance; Apache-2.0."""
import ast
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ["E8COORD"] = "ham"
sys.path.insert(0, os.path.join(HERE, "..", "bit", "producer"))
sys.path.insert(0, HERE)
import compile2 as C2  # noqa: E402  (PR #370 producer)
import fullword  # noqa: E402  (PR #370 producer)
import ham2  # noqa: E402  (PR #370 producer)
import reuse as RU  # noqa: E402
import retime as RT  # noqa: E402

params, out_raw, out_reused, out_final, out_ledger = sys.argv[1:6]
Pd = {ast.literal_eval(k): v for k, v in json.load(open(params))}
ham2.P.clear()
ham2.P.update(Pd)
h = ham2.build(0, True)
W = C2.compile2(h)
raw = fullword.build(W)
fullword.save(raw, out_raw)
print("   1. PR #370 producer with our parameters: R %d, gates D/A/B/C %d/%d/%d/%d, frames %d"
      % (raw["R"], len(raw["D"]), len(raw["A"]), len(raw["B"]), len(raw["C"]), len(raw["frames"])), flush=True)
reused, nre = RU.reuse(raw)
fullword.save(reused, out_reused)
print("   2. elimination reuse: %d dead slots reused by later helpers, %d by the retained totals: R %d -> %d"
      % (nre["helpers"], nre["totals"], raw["R"], reused["R"]), flush=True)
final, moved = RT.retime(reused, sweeps=6, M=64)
fullword.save(final, out_final)
for ph, i, kind in nre["eliminations"]:      # retiming moves frames only: the ledger positions are unchanged
    assert final[ph][i][1:] == reused[ph][i][1:]
with open(out_ledger, "w") as fh:
    json.dump(dict(helpers=nre["helpers"], totals=nre["totals"], eliminations=nre["eliminations"]), fh)
    fh.write("\n")
print("   3. retiming: %d gate moves; final R %d, gates D/A/B/C %d/%d/%d/%d, frames %d"
      % (moved, final["R"], len(final["D"]), len(final["A"]), len(final["B"]), len(final["C"]), len(final["frames"])),
      flush=True)
