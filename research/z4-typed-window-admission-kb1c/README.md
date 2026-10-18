# Admission-ready evidence for the typed-window z4 typed-echo schedule

**KB1c: the last mile before a maintainer kappa decision.** PR
https://github.com/CrocSwap/integer-mult-bounds/pull/2464 priced the fused z4
typed-echo pair and stopped on hosting; PR
https://github.com/CrocSwap/integer-mult-bounds/pull/2595 removed that
obstruction with legal per-call sequential immutable COPY/ERASE windows (384
records literal / 304 typed per k=2 pair against the priced 608 baseline,
typed relabeling at zero extra). This package runs the pinned PR1087 chain's
own admission/consistency machinery against that schedule as far as
non-invasive execution reaches, produces the exact evidence bundle (inputs
hashed, boundary contracts, dirty-column counts, the priced ledger), and
states the named maintainer decisions that remain. **No frozen pin, selected
record or selected frontier is changed; no new kappa and no supplier
admission is claimed.**

Agent: **Aaron Wang**, with help from opencode (substantial AI assistance; no
independent human review). Task card: [TASK.json](TASK.json) (card
`centre-path-sharing`, scope changed to the assigned kappa-blocker KB1c
request; see the recorded reason). Claim:
[discussion comment](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18954210).

## What the frozen chain does when run fresh

The full strict T16 replay (`research/gauge44-slots-t16/verify_t16.py`, the
PR1087 chain as composed in PR 1042) runs end to end on the retained local
word from the pinned replay archive: `restore-parent, bind8, lift16, bind,
emit, audit, invoice, assembly, admission-controls, bit-supplier-controls,
independent-t16`, verdict `PASS_GAUGE44_T16_STRICT_GLOBAL_REPLAY` at kappa
`1672188119205421/1000000000000000000` (0.001672188119205421 — the PR 1042
composition value, not the selected record's 0.001672660197076918). Controls
run fresh: 69 admission controls (all mutations rejected, none accepted), 12
bit-supplier controls (derived deficit 10272), 15 controller mutations, 6
independent-t16 controls, 47 strict outer margins all positive. Binding
inventory: 69,120 roles, 144 complete calls, prefix 397 at charge 512,
physical row coefficient 16,469 below 20,161, 9,938 axis charts.

The owner receipt reproduces the archived PR 1042 receipt byte-exactly
(SHA-256 `888d63e292eed39215fe9f1440b15018f71507e13132f0e02bf0c636d56908e6`);
the invoice receipt and the stage outputs are semantically identical to the
archive. Byte differences are JSON key ordering of one receipt and the
absolute input paths `independent-t16` records; nothing mathematical differs.

## Boundary contracts (what admission runs against)

| contract | pinned source | enforcing check |
|---|---|---|
| COPY/ERASE windows sequential and immutable, per-call totals | PR386 bit geometry, line 54 (`research/split-centres-global/proofs/PR386-BIT-GEOMETRY.txt`) | per-call delivery checks of PR 2595; the chain's literal-window model |
| wrapper counts bound to entering helpers | `code/assemble.py` line 102 | `pre_wrappers == post_wrappers == entering_helpers` |
| wrapper factors charged per call | `code/assemble.py` line 126 | `sum(pre+post) * 144` |
| coverage identity / selected deficit | `code/assemble.py` line 188 | `owner deficit == 5120` literal |
| supplier profile pins | `code/assemble.py` lines 67, 85, 92, 97, 182 | `expected.rank_mass`, `expected_profile`, `complete_contract`, `expected_local`, `expected.global_profile` |
| typed-window extension (frame-relabelled ERASE rows) | PR 2595 RESULT (vendored, SHA-256 `a740acb4727ca5141154617e47986de41a3c7cfbfdac2ec2c5885eace55552e7`) | priced at 0 extra records/descriptor bits; **no chain receipt field names it** |

The provider local receipt has 13 fields (`events, macros,
real_component_primitives, coefficient_work_primitive_count, prefix_l1,
prefix_bits, all_exact_columns, dirty_helper_columns,
all_dirty_helper_columns_restored, private_centres_and_coefficient_work_cleared,
pre_wrappers, post_wrappers, endpoint_evidence`); none names a typed
relabeling, a window width, or a per-pair totals sink.

## Dirty-column counts

| quantity | chain receipt | typed-window schedule (k=2) |
|---|---:|---:|
| all exact columns per call | 704 = 2x112 + 480 | 56 basis columns (every dirty state of (D, X, W)) |
| dirty helper columns per call | 480 | 24 wrapper rows (PR 2464 fused) |
| all dirty helper columns restored | true | 0 dirty rows at block-2 entry for legal per-call windows (24 fused, 16/24 row-minimal deferral) |
| hosted residual roles | 69,120 = 144 x 480 | per-call totals delivery checked exactly on all 56 columns |

## The priced ledger (both ledgers, chain's own engines)

Width `m = 73`, live stock `W = 14,336`. The chain receipt histogram
(`1:349577, 2:60193, 3:62608, 4:20448, 5:11808, 7:3, 8:1152, 16:47, 48:4850`)
and PR 2595's published baseline histogram both give `D = mW - sum(r n) =
5120`; the widened-window shared ledger (`8: 576`) gives `D = 9728`. Exact
moment acceptance is the chain's own `engines/moment.py` +
`engines/base_two_moment.py` predicate (accept at the endpoint, reject at
endpoint + 10^-24, both engines strict):

| ledger | endpoint (chain oracle) | rejects at | cross-check |
|---|---|---|---|
| chain receipt baseline | 418747253984418082117/250000000000000000000000 | +1e-24 | the chain's recorded `complex_lower` (accept/reject reproduced) |
| published baseline | 67018507072324140917/40000000000000000000000 | +1e-24 | equals the published root 0.0016754626768081035 |
| chain shared (widened window) | 796085643023976876837/250000000000000000000000 | +1e-24 | above certify's 0.003 ceiling (obstruction below) |
| published shared (widened window) | 1592621207654949794599/500000000000000000000000 | +1e-24 | equals PR 2595's enclosure [0.003185242415, 0.003185242416] |

The `a < D/E` screens of PR 2595 (0.0016805907097543218 baseline,
0.003203836729943888 shared) remain screens, not acceptance tests: the chain
engine's moment lower bound at the pinned `D_over_E_lo` is already above 1
(control `D_over_E_screen_not_acceptance`).

Scalar schedules (PR 2595 machine receipt, vendored): k=2 pair 384 literal /
304 typed against the priced 608 baseline (224/304 primitives saved; witness
rows at block-2 entry 24 fused, 16/24 deferral, 0/0 legal). One bounded pivot
(k=5+5 persistent pair): phase-indexed readers 1,456 separate / 1,408 joint
(48 saved). Adjacent concurrent work qualifies the fixed-reader family: PR
https://github.com/CrocSwap/integer-mult-bounds/pull/2626 computes 1,616
separate / 1,672 joint (56 extra) there, so the widening decision should be
priced on the phase-indexed family.

## Admission disposition, stage by stage

| stage (pinned PR1087 chain) | run against the typed-window schedule | result |
|---|---|---|
| strict T16 replay (all 11 stages) | fresh full run on the retained local word | passes on the frozen data (control) |
| admission-controls (69) | fresh run on the frozen receipts | passes; no control binds a typed-window declaration (none exists) |
| supplier-control (12) | fresh run on the frozen receipts | passes; bit supplier untouched by the schedule (derived deficit 10272) |
| verify_t16-style binding checks | final binding assertions on the fresh outputs | pass (roles/calls/prefix/row coefficient/outer margins) |
| invoice/assembly boundary, frozen receipts | `assemble()` on the fresh receipts | passes; kappa reproduced |
| invoice/assembly boundary, widened-window ledger declared | `assemble()` probes (below) | rejected; exact rejections recorded |
| moment certification (both engines) | both ledgers at their own endpoints | accept at endpoint, reject at +1e-24 for all four ledgers |
| scalar re-window declaration | `assemble()` probe | rejected at `providers.gauge44.complete_contract` |

## Scoped obstructions (exact stage and error)

1. **Moment certification, `engines/moment.py` certify search bracket.** The
   widened-window ledger (n_8 = 576, D = 9728) has its moment root at about
   0.0031852, above the engine's hard-coded search ceiling
   `hi = Decimal('.003')` (line 78); the final bracket assertion at line 86
   fails (`AssertionError: assert lv[1]<1<hv[0]`). The engine's `moment()`
   acceptance oracle itself accepts the ledger at its own grid endpoint (the
   two shared rows above, found by bracket bisection on that oracle).
2. **Invoice/assembly boundary, `code/assemble.py` owner deficit literal.**
   With the widened ledger declared consistently (owner profile, rank mass,
   deficit 9728, per-call rank-8 children 8 -> 4, adapter charges, pervertex
   and finite envelopes re-derived) and every SPEC pin relaxed, the
   acceptance function still hard-codes `owner['deficit'] == 5120`
   (line 188; empty AssertionError). Reaching it needs the certify bracket
   bypassed by its oracle-equivalent bisect (probe
   `widened_window_consistent_declaration_certify_bypassed`).

Intermediary rejections, all recorded in RESULT.json: the owner-ledger-only
declaration dies at the per-call profile/idle consistency (line 130: the
rank-8 idle remainder 576 - 1152 goes negative — a per-pair sink has no
per-call declaration); the same declaration in strict mode is rejected at the
SPEC pin `expected.rank_mass` (`expected 1041408 got 1036800`), as is the
consistent declaration; a scalar re-window is rejected at the
`providers.gauge44.complete_contract` pin.

## Named maintainer decisions

- **MD-1 — widened-window / common-sink contract change** (the only decision
  that moves the moment ledger; consistent with PR
  https://github.com/CrocSwap/integer-mult-bounds/pull/2500 that the typed
  contract alone does not imply fewer recursive children). Admitting the
  shared ledger (`n_8` 1,152 -> 576, `D` 5,120 -> 9,728) needs: the PR 386
  sentence amended for one widened window with per-pair totals delivery; a
  declaration path for a per-pair sink in the per-call receipt schema;
  `assemble.py`'s deficit literal replaced by the coverage identity; SPEC
  `expected.rank_mass` / `expected.global_profile` / `expected_profile`
  regeneration; and the moment engine's certify ceiling raised past the
  shared root (about 0.0031852) or its bracket made adaptive. The chain's
  own moment oracle already accepts the shared endpoint.
- **MD-2 — supplier admission fields for typed windows.** Declared fields for
  typed (frame-relabelled) window source rows, 8-row per-call windows and
  per-call totals delivery in the provider local receipt (today's 13 fields
  cannot express them), plus negative controls beside
  `false_dirty_restoration` in `code/assembly_controls.py`; a scalar
  re-window is rejected at the `complete_contract` / `expected_local` pins,
  so the admission route is a SPEC regeneration through the chain's
  discovery path with the new fields added.

## Scope, limits, and what is not claimed

This is admission-stage evidence only. The typed echo is **not placed** on
the selected 144-call schedule:
`research/selected-centre-adjacent-pair-seed01fcb1` found no adjacent pair of
that schedule sharing a physical owner among its eight centre source rows, so
no placement exists without paid owner transport (the same hosting
obligation). The strict replay is the pinned PR 1087 chain (PR 1042
composition, kappa 0.001672188119205421), not the selected PR 1094 record
(0.001672660197076918); the selected record is unchanged. The probes'
re-derivation of the invoice envelope mirrors `code/assemble.py`'s formulas
inside the probe harness only; the frozen chain files are untouched. Not
checked: native emission, all-size/compiler, precision buckets, tape,
analytic transfer and the bit H1-H5 obligations. This is not a multiplication
theorem and admits no supplier.

## Reproduce

Python 3.12 standard library and `git`, from the repository root:

```sh
python3 -I -B research/z4-typed-window-admission-kb1c/verify.py
python3 scripts/research_package.py --package research/z4-typed-window-admission-kb1c --check-only
```

Expected final line:

```text
PASS_Z4_TYPED_WINDOW_ADMISSION_KB1C controls=42 admission=69 supplier=12 kappa=0.001672188119205421 D=5120/9728 no_new_kappa
```

`--write` regenerates [RESULT.json](RESULT.json); the default run recomputes
everything (including the fresh strict T16 replay in a temporary directory)
and rejects drift. 42 controls cover the k=2 schedule invoices and savings,
the witness rows and basis coverage, the pivot prices and PR 2626's
fixed-reader qualification, both coverage identities, the fresh replay
verdict and its byte/semantic receipt comparison against the pinned archive,
all binding numbers, the dirty-column counts, every boundary-contract
location, the four moment accept/reject rows, the `D/E`-is-a-screen control,
and all six assembly probes at their exact rejection points.

## Open next questions

- **Can a maintainer make one named decision MD-1 in a single reviewable
  change?** The package reduces it to: contract sentence, per-pair sink
  declaration, deficit literal, SPEC regeneration, certify ceiling. First
  step: amend the PR 386 sentence and widen the certify bracket in one PR,
  then re-run this package's probes against the new chain. Blocked by: the
  contract owner's decision on per-pair totals delivery (the `2d = 48`
  record item of the persistent pair is the same question).
- **Do the typed-window declarations need a provider artifact of their own
  (MD-2) before any chain instance can carry them?** First step: add the
  typed-relabeling field and its negative control to one provider receipt
  schema and regenerate that chain's SPEC through the discovery path.
  Blocked by: no named host child exposes the order-four intertwiner
  `R P = Q R` (PR 2464's named gap), so no host-side consumer exists yet.

## Credit and scope

Mechanism and certified child family: **https://github.com/CrocSwap/integer-mult-bounds/pull/1391 / https://github.com/CrocSwap/integer-mult-bounds/pull/1410** (Cinna Davis
with OpenAI Codex assistance), extending Ross Richardson's
https://github.com/CrocSwap/integer-mult-bounds/pull/1287 and Sagar Thakrar's
https://github.com/CrocSwap/integer-mult-bounds/pull/1227; the heterogeneous
variants are https://github.com/CrocSwap/integer-mult-bounds/pull/1768 and
https://github.com/CrocSwap/integer-mult-bounds/pull/2098. The
priced whole-construction instantiation and the named hosting obstruction:
**https://github.com/CrocSwap/integer-mult-bounds/pull/2464**; the legal
typed-window schedules and the priced ledgers:
**https://github.com/CrocSwap/integer-mult-bounds/pull/2595** (both this task's direct predecessors). The fixed-reader fusion
tariff qualification is PR
https://github.com/CrocSwap/integer-mult-bounds/pull/2626 (petalas,
Discussion 2610); the typed-contract-vs-recursive-children finding is PR
https://github.com/CrocSwap/integer-mult-bounds/pull/2500 (Discussion 2488).
The pinned chain is Jeremy Kothe's
https://github.com/CrocSwap/integer-mult-bounds/pull/1087 package
(`research/gauge44-slots-t16`) with Hao Yan's T16 controller and the credited
bit/complex lineage, orchestrated by Douglas Colkitt; its vendored source is
`research/complex-k492-owner-repair/vendor/multicold` and its frozen receipts
are `research/community-frontier1042-audit/selected-replay.tar.gz`. The
immutable-window sentence is the bit-geometry artifact `PR386-BIT-GEOMETRY.txt`
in https://github.com/CrocSwap/integer-mult-bounds/pull/386 by Zhihao Chen
(jacklightChen, with OpenAI Codex assistance), whose local E8 bit word is Dylan
Crow's from https://github.com/CrocSwap/integer-mult-bounds/pull/370 (with
Anthropic Claude assistance), as pinned in `research/split-centres-global`; the adjacent-pair owner census is
`research/selected-centre-adjacent-pair-seed01fcb1`; the published `D/E`
diagnostic is `research/selected-suppliers-de-diagnostic` (Navinor) and the
pricing model is Douglas Colkitt's `research/complex-local-word-ceiling`.

New package material is Apache-2.0. Prepared by **Aaron Wang** with help from
opencode (substantial AI assistance in derivation, implementation, checking
and prose); no independent human review or proof-assistant formalization is
claimed. The selected record, upstream files and predecessor packages are
unchanged.

## Maintainer integration note

Integration refresh of the runtime provenance digests in RESULT.json to main 2a0d3aeab3016f5b5d85a5c0f956b9db5376c77d. The original task card, SOURCES.json and their historical base remain unchanged. Frozen chain code, archived mathematical receipts, probes and numerical results are unchanged; the complete registered T16/admission replay passed against the refreshed runtime inputs.

The hypothetical widened ledger is not an admitted supplier. Changing a contract sentence, receipt schema or acceptance assertion alone cannot admit it. A compatible typed child, concrete placement, changed-boundary correctness proof and complete physical bill remain necessary. The original scientific base identifier in the receipt is retained.
