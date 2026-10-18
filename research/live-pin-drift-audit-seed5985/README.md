# Live-byte source-pin drift audit at base 0fdd7d82

**Tooling audit and precise obstruction record; no new kappa, no certificate, pin,
frozen package or frontier change.** Drawn card `replay-runtime` (track
verifier-engineering, chooser OS nonce `5985f17ee9293abc98cbb69a85efb569`),
scope refined; see [TASK.md](TASK.md) and [TASK.json](TASK.json). Base
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`. Aaron Wang, with help from opencode
(substantial AI assistance). Apache-2.0.

## Question

Several merged replay-speed tooling changes rewrote shared scripts
(`scripts/exclusion_circuit.py`, `scripts/shared_point_circuit.py`,
`scripts/experiments/disjoint_tensor.py` and others). Repository checkers pin
the bytes of such scripts by SHA-256. Which recorded pins no longer match the
bytes their path holds, which checker rejections can be reproduced from those
mismatches, and which later commits touched each pinned file after its manifest
last changed?

## What a pin means here

The audit enumerates every JSON `{repo path: sha256}` entry (exact rule in
`RESULT.json`) and classifies each by the **shape** of its container:

- shape **L**, `check_sources`-style `"files": {path: sha256}` maps (for
  example `research/skip-clones/SOURCE.json`),
- shape **R-input** and **R-provenance**, `research_package.py` `SOURCES.json`
  records with `usage: "input"` and `usage: "provenance"` respectively, and
- shape **P**, every other `{path: sha256}` entry (for example the
  "catalogue SHA-256" recorded in claims and ledgers).

Shape is a syntactic category, not a statement about what a consumer does with
the entry. Two live-byte consumers are named and reproduced below:
`research/skip-clones/clone_io.py:check_sources` hashes current bytes for the
L-shaped pins of `research/skip-clones`, and `scripts/research_package.py
--check-only` hashes current working bytes for R-input rows of the packages it
checks ("working source drift"); for that validator, R-provenance rows bind the
recorded git blob instead. No other consumer was audited per entry. In
particular, P-shaped entries are not guaranteed to be inert: at this frozen
head `scripts/verify_pr_reconciliation.py:207` hashes every current path in
`ledger["source_sha256"]`, and `scripts/verify_replay_coverage.py:98` hashes
every current path in `selected["source_sha256"]`, and those entries fall into
shape P. Drift in P or R-provenance is therefore **candidate** drift: this
package records it, and neither calls it a failure nor calls it harmless.

Distinguishing the demonstrated failures from the candidate drift is the point
of the separation: a stale digest may be a historical fact or a live check, and
only a replayed consumer decides which.

## Established (all recomputed by `verify.py`; counts in `RESULT.json`)

| Shape | Pins | Match | Drift | Unresolved | Ignored |
|---|---:|---:|---:|---:|---:|
| L (check_sources-style) | 20,737 | 19,735 | 127 | 46 | 829 |
| R-input (usage="input") | 1,841 | 1,814 | 22 | 0 | 5 |
| R-provenance (usage="provenance") | 1,363 | 806 | 517 | 0 | 40 |
| P (all other entries) | 2,457,086 | 2,379,080 | 16,673 | 2,215 | 59,118 |

Total 2,481,027 entries across 17,525 tracked JSON manifests (2 manifests
unreadable). The inventory is bound to the `git ls-files` tracked set with the
`.json` extension matched case-insensitively: 17,529 tracked JSON files minus
this package's own 4. Twenty-two of the manifests are tracked with an uppercase
`.JSON` extension (`PREMERGE.JSON` and `SELECTION.JSON` in each of
`research/community-efficient{100,...,1000}-audit/`, plus `ENDING-OPEN.JSON`
and `NEXT-QUEUE-SUMMARY.JSON` in `research/community-efficient500-audit/`);
they are retained and contribute zero pins. A working-tree glob or a
case-sensitive `*.json` query drops those 22 and reports 17,503, which is how
an earlier replay of this package failed saved-census equality in a review
checkout. The 149 live-drift pins touch 48 distinct files.

1. **Smallest falsifying instance, reproduced exactly.**
   `research/skip-clones/clone_io.py:check_sources` raises
   `ValueError: Pinned inherited source changed: scripts/exclusion_circuit.py`.
   Its manifest recorded `b253f9d7318b...`, which equals the file's blob at the
   manifest's own last commit `c02590dd`; the current bytes hash
   `f9fbcd6e85e4...`. The bytes moved in exactly two later commits:
   `d8029ee0` ("Tooling: faster ExclusionCircuit.verify leave-two-out supports",
   blob `40bdb64670...`) and `d7d8bfcb` ("Tooling: fold
   ExclusionCircuit.verify_embedding reverse masks into #2001",
   blob `f9fbcd6e85...`, PR https://github.com/CrocSwap/integer-mult-bounds/pull/2001 ).
   The package's `make skip-clones-verify` replay and `tests/test_skip_clones.py`
   cannot run at base. This is the drawn card's coverage question answered
   after the fact: the speedups updated the shared certificate pins they
   touched (the refreshed pins in `certificates/dyadic-central-factor.json`
   and three sibling certificates now record `f9fbcd6e85...` and verify clean)
   but left older frozen packages' live pins stale.

2. **Registered rejections, reproduced exactly.** `scripts/research_package.py
   --check-only` fails three audited packages with `working source drift`:
   `research/clean-selector-embedding` and
   `research/complex-frame-plane-rail-seedca04cc`
   (`docs/research/agent-task-catalog.json`, recorded `6686ad58f1...`, current
   `d46eb6d5b3...`, changed by priority revision 4 "Focus research revision 4 on
   concrete missing interfaces"), and
   `research/complex-cartesian-grid-screen-seed506af`
   (`docs/research/bottleneck-brief.md`, recorded `a5e3165696...`, current
   `bbc9396c5c...`). Of the 22 drifted R-input pins, 10 pin evolving documents
   (the task catalogue, bottleneck brief or PR ledger) as `usage: "input"`: any
   later document update disables those replays. The remaining 12 pin tool
   scripts changed by the speedups above or by later tooling (for example
   `research/exact-frame-containment`, `research/finite-bit-rank-cache-seed87`
   and `research/rational-containment-performance` pin
   `scripts/exclusion_circuit.py` as `usage: "input"`).

3. **Provenance is recorded for every live-drift pin** in `RESULT.json`
   (`drift_provenance`): for each (manifest, pinned path) pair, the manifest's
   last commit, the pinned file's blob digest at that commit, and every later
   commit touching the pinned file with its blob digest. Of the 149 pairs, 68
   record a digest equal to the file's blob at the manifest's last commit (the
   pin was honest when the manifest froze and later commits moved the file);
   70 record a state older than the manifest's last commit, typical of vendored
   review snapshots that pin a historical selected record; 11 pairs have no
   blob at that commit.

## What this does not establish

No pin is repaired here: refreshing a frozen package's recorded digest would
rewrite the very evidence the pin protects, and vendoring freeze-time bytes
would change frozen files. Both are maintainer decisions, so this package stops
at the exact ledger and the two reproductions. `research/shared-point-digest`
already records the decision as its open question ("Pin repair is outside this
tooling change"), and this ledger is the data that follow-up needs. This is not
a claim that any mathematical result is wrong: the drift disables replay
checks, it does not falsify a certificate. The audit covers JSON `{path: sha256}`
pins only; not `Makefile` targets, environment pins, or non-JSON manifests.
Two of the 17,525 manifests were unreadable JSON and are counted, not audited.
An earlier revision of this README said 17,528 here; that figure equals 17,525
external manifests plus the three JSON files this package itself then carried
(`RESULT.json`, `SOURCES.json`, `TASK.json`; `VERIFY.json` is written last) and
is corrected to 17,525 everywhere. Only four drifted pins are demonstrated
failures — the pins named in the reproduced rejections (the skip-clones pin of
`scripts/exclusion_circuit.py` and the three registered R-input pins). The
remaining 145 live-drift pins and all P/R-provenance drift are candidate
drift: recorded here, with no consumer replayed against them.

## Reproduce

```sh
python3 -I -B research/live-pin-drift-audit-seed5985/verify.py
```

Expected:

```text
PASS_LIVE_PIN_DRIFT_AUDIT pins=2481027 manifests=17525 L(match=19735,drift=127,unresolved=46,ignored=829) R-input(match=1814,drift=22,unresolved=0,ignored=5) R-prov(match=806,drift=517,unresolved=0,ignored=40) P(match=2379080,drift=16673,unresolved=2215,ignored=59118) live_drift_paths=48 controls=8 skip_clones=ValueError
```

The run recomputes the whole ledger over the git-tracked manifest inventory
(case-insensitive `.json` extension) and requires it to match `RESULT.json`
exactly, so the census is identical in a complete frozen checkout and on
case-sensitive platforms. Eight controls: the headline digest is fixed; a
matching pin reports clean (the refreshed `certificates/dyadic-central-factor.json` pin of
`scripts/exclusion_circuit.py`); a corrupted digest registers as drift; a
missing target is unresolved; a non-repository key is ignored; a malformed
`"files"` map is not treated as an L manifest; a second independent
enumeration is byte-identical; and the inventory retains a tracked
case-variant `.JSON` manifest (the 22-file extension rule above). `--write`
regenerates `RESULT.json`.

## Open next questions

- **Pin repair policy for the 149 live-drift pins.** For each frozen package,
  should a maintainer (a) refresh the recorded digest with the old digest and
  this provenance retained, (b) vendor the freeze-time bytes and check those,
  or (c) declare the replay historical and bind it to its recorded commit?
  First step: apply one option to `research/skip-clones` alone and rerun
  `tests/test_skip_clones.py`. Blocked by: modifying frozen package bytes or
  pins needs maintainer authorization.
- **Should `usage: "input"` be reserved for genuinely required live tools?**
  Ten packages pin the evolving task catalogue or brief as a live input, so
  every priority revision disables them. First step: a one-line convention in
  `docs/research/research-package-guide.md` distinguishing live inputs from
  provenance pins. Blocked by: documentation ownership.
- **Automated drift guard.** This audit is deterministic and cheap enough
  (~100 s) to run in CI against a pinned base. First step: a check that fails
  only on *new* L/R-input drift relative to a recorded baseline. Blocked by:
  maintainer choice of the baseline policy.

## Credit

Predecessors: Chafik Boukhalfa (`research/skip-clones`, whose pinned replay is
the smallest falsifying instance); Douglas Colkitt (`scripts/research_package.py`
pin validation and its input/provenance distinction); the authors of
`research/exclusion-support-masks`, `research/exclusion-embedding-masks`
(PR https://github.com/CrocSwap/integer-mult-bounds/pull/2001 ) and
`research/disjoint-tensor-support-masks` (the merged speedups under audit, which
already updated the shared certificate pins they touched); the author of
`research/shared-point-digest` (the recorded "Pin repair is outside this tooling
change" open question); woklerx (`research/git-provenance-stream`, pin-validation
tooling precedent). No predecessor code was imported; the verifier is
independently written and only executes `research/skip-clones/clone_io.py` and
`scripts/research_package.py` as black-box reproductions of their own checks.
