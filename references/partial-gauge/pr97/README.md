This is a compact, unmodified snapshot of the PR97 physical bit ledger and
the underlying frozen round-seven input. `SOURCE.json` pins the commits and
every imported file's SHA-256. Each imported byte sequence also matches the
round-six handoff's original manifest. Original LICENSE and NOTICE are retained.

Zhihao Chen / jacklightChen supplies the PR97 literal forward/reflected physical
ledger and proof, with the Codex assistance disclosed in those files. Swapnil
Jain supplies the underlying deferred word, frame witnesses and frame/lifted
checking sources. Earlier authors and assistance disclosures remain credited
in NOTICE, PROOF.md, and the original source headers.

The snapshot preserves `witness_23.json.gz` and `deferred_23.json.gz` (about
2.3 MB together), not the large expanded event/path dumps. The archived
`bit-ledger-result.json` is a validation receipt, not a new test result. Its
historical elapsed time is preserved verbatim. The original scripts retain
their upstream directory assumptions; they are source/proof witnesses here,
not a relocated full-audit harness.

`scripts/partial_gauge_bit.py` verifies every byte pin, loads the compressed
inputs explicitly, reconstructs auxiliary and data-chain rank increments,
checks them against the actual physical ledger, reconstructs exit nullities
from each physical slot's deferred frame, and composes the new whole-projector
histogram. It compares every coefficient to the round-six input certificate.
It does not repeat the unchanged complete-basis replay or rational geometry
audits; rank differences alone would not establish those geometric hypotheses.

The whole-projector reconstruction counts two stages of v physical invocations,
with each local rank increment kept whole, each exterior assigned rank
`m-(h-dim sigma)`, two bank-pair entrance projectors of rank `(h-1)^2`, and
one rank-one copy correction per source pair. This replaces the old corner
splitting while preserving the exact physical total rank mass.

New reconstruction and integration: copyright 2026 icekylinx, Apache-2.0,
prepared with OpenAI Codex assistance. No independent review or endorsement
by the predecessor authors is implied.
