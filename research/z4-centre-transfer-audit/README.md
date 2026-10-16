# Typed-echo scalar saving does not yet establish a centre-child saving

**Independent source-bound audit; no new kappa or native obstruction.**
PR [2464](https://github.com/CrocSwap/integer-mult-bounds/pull/2464), at
`f364b97ff4700147fc06e622b79952b9fe6c4fa8`, correctly reproduces the
order-four echo's scalar saving. Its typed contract alone does **not** imply
the proposed deletion of eight rank-eight recursive children per pair.
That transfer needs an additional native compiler and cost correspondence.
The PR's explicit no-admission/no-new-kappa disclaimer remains appropriate.

## Exact result and covered domain

For the pinned 8-output, 24-source, 24-dirty-workspace interface, both schedules
implement `D += R_0 X + R_1 X`, preserving all source and workspace inputs.
Every forward and literal inverse occurrence of each typed child remains.

| Complete pair | ADD | NEG | Scalar primitives | Typed child calls |
|---|---:|---:|---:|---:|
| Separate | 560 | 48 | 608 | 2 forward + 2 inverse |
| Joint | 440 | 56 | 496 | 2 forward + 2 inverse |

The saving is **48 scalar source-shear ADDs plus 64 boundary primitives**.
For any fixed additive nonnegative histogram tariff on the indivisible
typed children, with the emitted scalar source shears and phase words charged
their scalar costs, the recursive histogram is unchanged. In particular,
assigning four rank-eight calls to each child orientation gives **16 before
and 16 after**, while retaining the exact 112-primitive saving. This is a
countermodel to inference from the typed contract alone, not a physical
implementation or a lower bound against a different native decomposition.

The [independent written proof](REVIEW.md) covers arbitrary exact intertwiners
`R_i P = Q R_i`, arbitrary child lists, disjoint source/work/output roles,
literal inverses, and the same-source, same-output endpoint contract. The
finite verifier checks all 56 dirty-input columns (3,136 coefficients per
map) for the actual emitted smallest pair, both literal inverses, and all
4 + 16 phase paths for one and two children. This is not a formal-kernel proof.

## Source-to-claim boundary

The immutable PR2464 verifier
[sets `hist_shared[8] = 576`](https://github.com/CrocSwap/integer-mult-bounds/blob/f364b97ff4700147fc06e622b79952b9fe6c4fa8/research/z4-typed-echo-supplier-instance/verify.py#L524)
and separately
[assigns 64 eliminated rank units and zero recursive overhead](https://github.com/CrocSwap/integer-mult-bounds/blob/f364b97ff4700147fc06e622b79952b9fe6c4fa8/research/z4-typed-echo-supplier-instance/verify.py#L568).
Those constants correctly describe the favorable halved-centre ledger, but
are not derived from the scalar echo's emitted child calls. The baseline
histogram matches the selected assembly exactly. This audit reproduces the
source's entire 51-control result, including its conditional moment fields;
that reproduction is expressly a **primary-source positive control**.

An eight-coordinate reader rank and a native Fourier child rank are
different quantities. The native centre episode copies a total, changes
the private copy's frame, scatters it, and clears it. Removing a scalar
`W += X`/`W -= X` pair does not identify the deleted frame-changing children.
Widening a lifetime alone does not provide that identification either.

This audit supplies an exact tariff non-entailment proof and binds it to a
new transfer claim. It does not repeat or strengthen the existing adjacent
owner census or the particular pair's rank-16 **scalar projection** in
`selected-centre-composed-source-rank`. Those are credited context with
different, explicitly limited hypotheses.

## Reproduce

From the repository root, Python 3.12, standard library only:

```sh
python3.12 -B scripts/research_package.py --package research/z4-centre-transfer-audit
```

The registered commands run the independent audit, reproduce all original
PR2464 result fields by canonical JSON digest, and run five behavioral tests.
Direct replay also works under Python 3.14 and `-I -O -B`.

Expected marker:

```text
PASS_Z4_CENTRE_TRANSFER_AUDIT scalar_saving=112 child_multiset_unchanged=4 controls=7 no_new_kappa
```

Seven semantic controls cover omitted children, wrong phases, wrong inverse,
missing copy-out, an actual emitted ADD-sign fault, deleted inverse-child
charges, and the unsupported eight-child deduction. A positive premise
control shows that assigning eight rank-eight calls to each complete wrapper
*would* yield the deletion; that is the extra binding to prove. Behavioral
tests also show identical endpoint maps with different recursive invoices.
All predicates remain active under optimization. Ordinary replay is read-only.

Source commits, blobs and SHA256 pins are in `SOURCES.json` and
`EXTERNAL-SOURCE.json`. Three PR2464 files are preserved byte-identically in
`inputs/pr2464/`; source path relocation in `replay_source.py` changes no
mathematics. `RESULT.json` is compared in full. Selected source/frontier files
are unchanged. No full selected cold replay, native supplier admission,
precision/tape proof, all-size transfer or hosted-CI success is claimed.

## Open next questions

Name one actual native centre episode, then one pair, and supply its typed
source/sink embeddings, exact intertwiners, complete replacement and literal
before/after recursive child ledger. Price every adapter, source access,
restoration, lifetime and precision change. The first decisive test is whether
the episode exposes the required typed boundary **and** identifies the claimed
deleted rank-eight children. A full map without that cost link is insufficient.
The missing native refinement is the blocker; further moment digits do not
resolve it. Structured details are in `TASK.json`.

Concurrent [PR2491](https://github.com/CrocSwap/integer-mult-bounds/pull/2491),
by ywz65 at `c25a4ce22a887daf8cba8b3cfad72796752ab2ee`, reports a direct
unitary paired-cycle obstruction for one full selected dirty reader. Its
README and PR description were read during submission screening, but its
certificate was not replayed here. It addresses the actual-reader embedding;
this audit addresses the separate implication from a typed word to a changed
recursive tariff. Follow-up should coordinate with its paid nonunitary or
changed-cut alternatives and still provide the complete cost correspondence.

## Credit and coordination

Aaron Wang (navinor), with opencode assistance, supplied PR2464's scalar and
conditional-pricing audit. Cinna Davis supplied PR1391/1410's typed echo,
following Ross Richardson's PR1287 and Sagar Thakrar's PR1227. PR1708/1748,
rtyu193-rgb's centre-sharing overhead budgets, Adam Gall's composed-source
rank result, and the selected #1094/#589 lineage retain their own credit.
See `NOTICE.md` and the frozen source notice.

Prepared by Ross Richardson with substantial OpenAI Codex assistance.
A separate math-recursive-interfaces specialist derived `REVIEW.md`
independently of the replay implementation. This is independent AI-assisted
checking, not independent human review. New material is Apache-2.0.
Canonical investigation:
[Discussion2488](https://github.com/CrocSwap/integer-mult-bounds/discussions/2488).
