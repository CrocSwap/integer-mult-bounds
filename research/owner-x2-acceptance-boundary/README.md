# X2 acceptance boundary for the selected CrocSwap/integer-mult-bounds#1094 owner map

**Adversarial audit of one selected supplier obligation; no new κ.** Navinor,
with help from opencode. Apache-2.0.

This package answers one question from the `supplier-boundary-audit` card
(adversarial-audit track, task catalogue revision 2): does one selected
supplier obligation follow from its actual source-bound checks?

**Object.** The frozen owner map of the selected complex supplier: CrocSwap/integer-mult-bounds#1094's
`data/OWNERS.json.gz` / `PLAN.json` / `SPEC.json` in
`research/complex-t16-rare-pattern-exchanges/`, at audited head
`0fc329d0bec93ca7cd288eaea1295172e8789810` (recorded in
`certificates/selected-result.json`, κ = 836330098538459/500000000000000000).

**Obligation (named X2).** Pending axes of distinct idle children of one
physical family are disjoint, so a family's hosts on different children never
share a cell. X2 is stated and checked in Josie Elliston's independent owner
audit (`research/t16-owner-audit-seed67/verify.py`, `geometry()`).

**Answer.** No. X2's acceptance does not follow from the selected record's
reproduce command. It depends on the review-time maintainer composition
`research/community-batch1099-audit/check_frontier1094.py`, which is pinned in
the record's `proof_supplements` but is executed neither by
`make frontier1094-verify` nor by the `community-batch1099.yml` CI job. No
checker that the reproduce path does execute recomputes X2 semantically. That
is a missing-semantic-recomputation gap, not demonstrated end-to-end
acceptance of a mutated pinned input: the source-hash layers reject the
mutated fixture before the semantic rules ever run (executed evidence below),
and full mutated-chain acceptance was not executed. Which layer catches what
is recorded in `RESULT.json` under `source_bound_acceptance`.

## Task card

```text
Task ID / proposed scope key: supplier-boundary-audit / dcdb0fa8e49b08a958d0
  (refined to the selected CrocSwap/integer-mult-bounds#1094 owner map, obligation X2)
Base commit; exact predecessor and dependency heads:
  bce54fb3f895cbe5cd4c0eb477c3afeed100190f; audited source head
  0fc329d0bec93ca7cd288eaea1295172e8789810 (CrocSwap/integer-mult-bounds#1094); owner audit CrocSwap/integer-mult-bounds#1091
  as composed by research/community-batch1099-audit/check_frontier1094.py
  (sha256 2608ef213260a43d09a40b3429742f7a5f280861b54acae66400a7c29a123f51)
Concrete object and question:
  one named condition, X2, of the selected supplier's hosting soundness:
  does its acceptance follow from the actual source-bound checks?
Scope status: refined (one named current condition audited with a new
  semantic counterexample, as the card allows; wording refined to the
  selected CrocSwap/integer-mult-bounds#1094 owner map and obligation X2)
Existing restriction being changed (or exact claim being audited):
  audited claim: the selected composition's owner/hosting acceptance
Method; explicit parameter ranges/candidate alphabet:
  enforcement trace of every checker on the reproduce path; then one exact
  one-integer mutation of the pinned DATA-PHASES pending axes (children 0 and
  1 at port 0) with rejection testing and a colliding-cell witness
Nearest overlapping PRs and why this adds something:
  CrocSwap/integer-mult-bounds#1277 (the reuse replay discards its ancestry
  recheck) — same replay-coverage class, different obligation; this package
  covers owner-rule X2 and supplies the missing rejection controls.
  CrocSwap/integer-mult-bounds#1209 audits pending-axis independence of the
  selected data semantically; this package tests which checkers reject a
  corrupted fixture at all. Josie Elliston's CrocSwap/integer-mult-bounds#1091
  owns the X2 rule and the 11-control battery; this package adds the first
  X2-directed mutants and the acceptance trace for CrocSwap/integer-mult-bounds#1094.
Optimistic full cost budget; required observable improvement:
  stdlib-only replay of the pinned audit on pinned inputs; no construction
Success evidence; falsification test; time/compute cap:
  RESULT.json from one command; falsified if geometry() accepts M1 or if any
  executed semantic rule on the reproduce path rejects M1 (source-hash pin
  rejections do not count as semantic detection); minutes on one core
Predecessor authors; intended artifact and reproduction command:
  Josie Elliston (X2 rule, owner audit), Rohan Arun (CrocSwap/integer-mult-bounds#1094 owner map),
  Jeremy Kothe (T16 owner-map lineage), Hao Yan (CrocSwap/integer-mult-bounds#858 controller/indep16),
  Sagar Thakrar (independent pricing), Douglas Colkitt (batch1099
  composition); artifact research/owner-x2-acceptance-boundary/;
  python3 -B research/owner-x2-acceptance-boundary/verify.py
```

## What the trace shows

| Path | Executes the CrocSwap/integer-mult-bounds#1094 owner composition (`check_frontier1094.py`) | Sees X2 |
| --- | --- | --- |
| `make frontier1094-verify` (the record's `reproduce`) | no — stages: `historical-source`, `baseline1042-cold` (or reuse), `rare-pattern-exchanges` | no |
| `scripts/verify_selected_result.py` (CI + target dependency) | no — validates the record and `proof_supplements` hashes; imports no subprocess module | hashes only |
| `.github/workflows/community-batch1099.yml` | no — runs `research/t16-owner-audit-seed67/verify.py --fetch` and `check_pr1048_counterexample.py` | yes, but only for its pinned claim list (CrocSwap/integer-mult-bounds#1022 through CrocSwap/integer-mult-bounds#1087), which excludes the selected supplier |
| frozen `upstream1087.tar.gz` chain (`verify_t16.py` → `lift16`/`audit_allcold`/`indep16`) | n/a | no — `indep16.py` keys cells per `(owner, child, port)`; `audit_allcold.py` asserts only `len(pending) == rank` per child |
| `research/community-batch1099-audit/check_frontier1094.py` (batch1099 review time) | — | **yes**, via `geometry()`; its result is pinned evidence in `docs/research/community-batch1099-integration.json` |

So the obligation is real and currently checked semantically exactly once, at
review time, by a composition that neither the reproduce command nor CI
re-runs for CrocSwap/integer-mult-bounds#1094. The construction-time receipts in
`hosting/expand_owners.py` and `hosting/reuse_owners.py` record
`all_footprints_disjoint_compacted_prefixes: True` as a flag; the flag is not
independently enforced on the reproduce path.

## Hash/pin layer vs semantic layer (executed)

Review follow-up: missing semantic recomputation is not the same as acceptance
of mutated pinned inputs, because the source-hash layers can reject the
mutation first. The source-bound acceptance path has three layers, and each
one's relation to the M1 fixture is measured:

| Layer | Checker | M1-mutated pinned `DATA-PHASES.json` |
| --- | --- | --- |
| record/manifest hashes | `scripts/verify_selected_result.py` (record, `SELECTED-SOURCE.json` package inventory, `proof_supplements`) | the top-level audit fixture is outside the manifest's package roots, so this layer alone neither accepts nor rejects it; the three vendored `DATA-PHASES.json` copies are pinned at `c5916ff3…` and a mutation of those is rejected |
| source input pins, before any semantic rule | `check_frontier1094.py` line 19; `t16-owner-audit-seed67/verify.py` line 359 | **rejected** at the sha256 pin (`SOURCES.json` `inputs.data_phases_sha256`) |
| semantic rules | R1–R7/X1, X2 (`geometry()`); frozen `indep16`/`audit_allcold` | R1–R7/X1 accept (executed, in-memory); X2 rejects (executed); frozen chain carries no cross-child rule (code trace) |

Executed evidence (verify.py section 7, recorded in `RESULT.json`
`source_bound_acceptance.executed`): the one-integer M1 edit is applied to a
copy of the pinned fixture bytes in a scratch tree (byte delta 4; parsing the
edited bytes yields exactly the in-memory M1 fixture; tracked files are
untouched and the scratch tree is deleted), and the real source-bound
entrypoints are run against it. With the mutation,
`check_frontier1094.py` stops at its DATA-PHASES hash require (line 19,
before `geometry()` at line 21) and the owner audit stops at
`FAIL input: DATA-PHASES hash` (line 359, before `geometry()` at line 362).
With intact bytes, both entrypoints pass the pins and reach later code: the
composition stops only at the intentionally absent scratch dependency past
`geometry()`, and the owner audit reaches its claim loop and stops only on the
absent git blob store. So the demonstrated gap is that no executed checker
recomputes X2 semantically on the reproduce path; a mutated pinned input is
rejected by the source-hash layer before the semantic rules, and end-to-end
acceptance of the mutated chain was not executed.

## Minimal adversarial instance

One integer in the pinned `DATA-PHASES.json` pending axes: child 1's
`orthogonal_axes[0]` at port 0, value 131072, replaced by 13, which is already
pending for child 0. Children 0 and 1 are distinct idle children of the same
physical family place (pair 1, side 0). This preserves every rank, window,
role count, width and profile aggregate (exactly one differing integer), and:

- `geometry()` rejects it: `X2: children [0, 1, 14] share axes at port 0`.
- With only the X2 `need()` suppressed, `geometry()` returns a byte-identical
  geometry object and the complete R1–R7/X1 rule set accepts the fixture —
  the X2 rule is the only rule that reads pending axes. This is a
  semantic-layer measurement on in-memory mutated bytes: the source-bound
  entrypoints never deliver mutated pinned bytes to these rules (hash layer,
  above).
- The concrete damage: roles at time 3 and time 6 (both helper 476, owner
  replica 0, family 224, port 0, offset 0, width 8) resolve the same
  pending axis 13 of family 224 — one physical cell written twice — while
  every role-level rule accepts both.

A second mutation (one axis duplicated inside a single child's list) is
rejected at X2 as well; both are failure controls in `verify.py`.

## Controls coverage added

The existing rejection batteries contain no X2-directed mutant: the owner
audit's 11 controls (`drop_role`, `narrow_width`, `duplicate_helper`,
`private_family`, `active_pair`, `family_collision`, `past_idle_sweep`,
`overlap`, `prefix_gap`, `claimed_idle_tampered`, `plan_window_truncated`)
and the frozen verifier's 6 independent-t16 controls
(`private_namespace_collision`, `copy_replica_alias`, `missing_whole_helper`,
`split_whole_helper`, `truncated_helper_width`, `cross_idle_boundary`).
This package supplies the first two X2-directed mutants with single-locus,
rank-preservation and null-mutation guards.

## Reproduce

```sh
python3 -B research/owner-x2-acceptance-boundary/verify.py
```

Expected status: `PASS_PR1094_X2_ACCEPTANCE_BOUNDARY_AUDIT`. The deterministic
record is [RESULT.json](RESULT.json) with exact input pins (template
`025448ab…`, DATA-PHASES `c5916ff3…`, word `c2b29430…`, OWNERS `87902c52…`,
PLAN `7bd786ba…`, SPEC `8cb51f25…`, owner audit `f6e27f76…`, composition
`2608ef21…`, upstream1087 archive `d4acf04d…`).

## Open next questions

- Should `scripts/verify_frontier1094.py` execute the pinned
  `check_frontier1094.py` composition (or a source-bound X2 recount) so the
  record's reproduce command enforces X2 for CrocSwap/integer-mult-bounds#1094? Why it matters: the
  selected record's hosting soundness currently rests on a review-time run
  that the reproduce path does not repeat. First step: add the composition as
  a `verify_frontier1094.py` stage and measure replay time. Blocker: needs
  maintainer authorization to change the selected reproduction path; this
  package does not change it.
- Does the same boundary hold for the other T16 claims' X1/X2 checks (the
  `--fetch` claim list, CrocSwap/integer-mult-bounds#1022 through
  CrocSwap/integer-mult-bounds#1087, is audited in CI, but its composition with
  the pricing audit is not)? First step: enumerate which obligations of
  `docs/research/community-batch1099-review.md` are enforced where, one rule
  per table row. Blocker: none; this is a natural continuation.
- Would the frozen `indep16` chain accept a mutated fixture end to end below
  the hash pins? Why it matters: it would close the remaining code-trace claim
  (the frozen chain carries no cross-child pending-axis rule) by execution.
  First step: run `make frontier1094-verify` with `--baseline1042` reuse and
  the mutated phases re-pinned consistently at generation time. Blocker: the
  published frontier1042 baseline artifacts and cold replay time were outside
  this session's budget. What is already executed: the source-bound
  entrypoints reject the mutated pinned bytes at their hash pins before any
  semantic rule runs, so the mutated pinned input never reaches the frozen
  chain; the chain's own DATA-PHASES hash handling is an emit-time
  self-consistency binding (`emit_allcold.py` `source_artifacts` ↔
  `audit_allcold.py` `exact_data_phase_recipe_sha256`), not an external pin.

## Limitations and unrun obligations

- This is a checker-coverage audit of one named obligation. It is not a
  construction, not a supplier change, and not a κ claim; the selected record
  and `upstream/` are unchanged.
- The full `make frontier1094-verify` cold replay with the mutated phases was
  not run (see above); frozen-chain blindness is code-trace evidence, and
  end-to-end acceptance of a mutated pinned input is not claimed anywhere in
  this package. The executed evidence covers the semantic layer (in-memory
  mutation) and the hash/pin layer (real entrypoints run against a scratch
  copy of the mutated bytes).
- No claim other than the selected CrocSwap/integer-mult-bounds#1094 inputs was re-audited; the
  historical `research/owner-boundary-audit/` package was used as an example
  of the method only and was not rerun.
- A finite rejection test is not a proof of hosting soundness; X2 itself is
  proved by enumeration over the pinned phases, not universally.

## Attribution and coordination

The X2 rule, its wording, and the independent owner audit are Josie
Elliston's (`JosieElliston`, CrocSwap/integer-mult-bounds#1091), reused here
unchanged as a library. The selected owner map is Rohan Arun's
CrocSwap/integer-mult-bounds#1094 on Jeremy Kothe's T16 owner-map lineage;
the frozen verifier chain is Hao Yan's (`FanPUYen`)
CrocSwap/integer-mult-bounds#858 lineage; the batch1099 composition and
review are Douglas Colkitt's; independent endpoint pricing is Sagar
Thakrar's CrocSwap/integer-mult-bounds#1069. The nearest concurrent finding
is CrocSwap/integer-mult-bounds#1277 (ancestry recheck dropped by the reuse
replay), credited for the replay-coverage direction; this package adds the
X2 boundary and its first rejection controls. Audit work by Navinor with
help from opencode. Tasks selected with
`scripts/choose_research_task.py` (track `adversarial-audit`, OS-random
nonce `ca8debca8488dd850dd6c0afb7398632`).
