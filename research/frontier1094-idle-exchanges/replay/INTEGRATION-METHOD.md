# Candidate audit and admission method

`BASE-EMITTER-REPLAY.json` binds a fresh #1094 hosted emission to the archived
template, idle frames, sigma maps and summary. The candidate builder applies
the disjoint pair exchange to those byte-identical baseline artifacts.

[`audit_allcold_idle_overlay.py`](../audit_allcold_idle_overlay.py) is the
independent serialized controller/owner auditor from the retained T16 source,
adapted to consume the explicit overlay frame file. It independently checks
the call schedule, all 69,120 owner charts and windows, candidate profile,
provider bindings, and the 15 existing controller mutations. It runs in strict
pin mode using `SPEC-candidate.json`; `WITNESS_DISCOVER` is unset. The separate
[`verify_overlay.py`](../verify_overlay.py) checks every changed pair's axes,
phase polynomial, owner slots, translations, and maximum matching size.

After building the overlay, copy
[`SPEC-candidate.json`](SPEC-candidate.json) to `/tmp/rarepkg/data/SPEC.json`
and rerun the independent controller audit in strict pin mode:

```sh
cp research/frontier1094-idle-exchanges/replay/SPEC-candidate.json \
  /tmp/rarepkg/data/SPEC.json
T16_SOURCE_CODE=/tmp/rarepkg/code \
T16_BASE_HOSTED=/tmp/frontier1094/baseline-hosted \
WITNESS_SPEC=/tmp/rarepkg/data/SPEC.json \
python3 -B research/frontier1094-idle-exchanges/audit_allcold_idle_overlay.py \
  /tmp/frontier1094/candidate/strict/global/base \
  research/frontier1094-idle-exchanges \
  research/frontier1094-idle-exchanges/replay/audit/ASYNC-AUDIT.json \
  --mutation-controls
```

The full mixed-provider invoice uses the package's unmodified
`invoice_allcold.py` and retains the previous invoice from the archived T16
source package. The strict assembler is the package assembler with its fixed
rank-48 guard generalized to the candidate's exact rank-51 guard
`[5329, 5202]`. The resulting assembly is pinned by
[`SPEC-candidate.json`](SPEC-candidate.json). The 69 assembly negative controls
and 12 PR589 bit-supplier controls also pass.

`assemble_candidate.py` is the strict assembler copy used for the final run;
its only algorithmic change is deriving the halving vector from the candidate
maximum rank. Its source package argument provides the three exact moment
engines; the PR589 bit input remains pinned to the retained package.

The source-level patch is limited to understanding the explicit idle-axis
overlay in the independent auditor and comparing the halving guard against the
candidate maximum rank. The local providers, role map, invocation schedule,
and bit supplier remain byte-identical to the archived #1094 replay.
