# z4 typed echo as a supplier instance: priced, and blocked in one obligation

**Supplier instantiation of a certified mechanism; no new kappa and no change to
the selected record.** The certified z4 order-four typed echo (PR #1391's
five-child contract, PR #1410's persistent pair) is instantiated as far as the
repository's contracts allow: the smallest falsifying typed pair, the priced
whole-construction physical budget, and the hosted aggregate ledgers with their
exact moments and `a < D/E` diagnostics. The instantiation fits the sharpest
available overhead budget with zero recursive overhead of its own. It is
blocked in exactly one obligation, **hosting**: the named host's contract keeps
`COPY/ERASE` windows sequential and immutable and delivers totals per call,
while the typed echo must defer the first wrapper's restoration across the
second call's window. Under the unchanged contract the pair pays both wrappers,
the ledger returns to the selected histogram, and the 112 saved primitives per
pair are scalar-only.

Agent: **Aaron Wang**, with help from opencode (substantial AI assistance; no
independent human review). Task card: [TASK.json](TASK.json) (card
`centre-path-sharing`, scope changed to the assigned kappa-blocker KB1 request;
see the recorded reason). Claim:
[discussion comment](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18947139).

## The mechanism, rebuilt and falsified at the smallest instance

The typed echo composes children `C_i(D,W) = (D + R_i W, P W)` with the
order-four intertwiner `R_i P = Q R_i`; a complete root echo maps
`(D, X, W) -> (D + sum R_i X, X, W)` for arbitrary dirty `D`, `X`, `W`. The
boundary schedule costs `g(k)`; this package re-derives it by an independent
dynamic program and checks it against the pinned brute force:

| children k | 1 | 2 | 3 | 5 | 10 |
|---:|---:|---:|---:|---:|---:|
| boundary g(k) | 60 | 88 | 116 | 140 | 248 |

**Smallest falsifying instance first: the `k = 2` typed pair.** Two one-child
echoes on children 0 and 1, fused into one two-child echo. All `4^2 = 16` phase
paths enumerated; the minimum is `g(2) = 88`. The joint word, the two separate
words and their sequential composition agree exactly as integer maps on all 56
basis columns, which by linearity is every dirty state of `(D, X, W)`; the
literal reversed word is an exact inverse. Three schedule mutants (wrong first
output phase, omitted terminal gap, forward word substituted for the inverse)
all produce different maps and are rejected.

Complete invoices (ADD, NEG), reproduced from the pinned predecessor numbers:

| schedule | ADD | NEG | total | comparison |
|---|---:|---:|---:|---|
| five-child echo | 920 | 88 | 1,008 | eager 1,328 (PR #1391) |
| ten-child joint echo | 1,720 | 184 | 1,904 | two separate 2,016 (PR #1410) |
| two-child joint echo | 440 | 56 | 496 | two separate 608 (this package) |

Prefix row-L1 peaks (the precision proxy of the predecessor packages) are 4 at
`k = 1`, 10 at `k = 2`, 20 at `k = 5`, 30 for two separate five-child calls and
42 for the joint ten-child call, reproducing PR #1410's 30/42 exactly.

## Priced whole-construction budget

The predecessor packages price primitives, reads and writes, and leave
"address travel, coefficient fetches and descriptor storage" unpriced. Declared
model (one machine, both schedules priced in it): rows of width 73 on a
row-indexed tape; one dispatch, one instruction fetch and one coefficient fetch
per record; ADD reads two rows and writes one, NEG reads and writes one; address
travel is `2 * max(source, target)` row-index steps per record, the
visit-source/visit-target/return convention of
`research/mutable-source-persistent-connector`; descriptor storage is 16 bits
per record plus one 128-bit call record; data storage is `56 * width` cells.

| quantity | two separate calls (k=2) | joint k=2 | saving per pair |
|---|---:|---:|---:|
| primitives | 608 | 496 | 112 |
| dispatches | 608 | 496 | 112 |
| instruction fetches | 608 | 496 | 112 |
| coefficient fetches | 608 | 496 | 112 |
| reads | 1,168 | 936 | 232 |
| writes | 608 | 496 | 112 |
| address travel (row steps) | 53,024 | 36,944 | 16,080 |
| descriptor bits | 9,984 | 8,064 | 1,920 |
| data storage cells | 4,088 | 4,088 | 0 |

The `k = 5+5` versus `k = 10` pair has identical savings. The saving is real at
every charged level of this model except storage, and it is scalar: no charged
quantity in the moment ledger moves.

## Hosted ledgers, exact moments, and `a < D/E`

The named host is the binding selected complex ledger (width `m = 73`, live
stock `W = 14,336`, `N = 144` calls, published histogram, no surcharge). The
typed echo applied to consecutive same-source call pairs is the shared-centre
ledger of `research/centre-sharing-overhead-budget`: the shared rank-8 centre
children go from 1,152 to 576 and the coverage identity from `72W + 64N` to
`72W + 32N`. Exact rational enclosures (independent atanh/Taylor engine, no
import of the retained pricing engines):

| ledger | rank mass | D | `a < D/E` | exact moment root `a*` |
|---|---:|---:|---:|---|
| selected baseline | 1,041,408 | 5,120 | 0.0016805907097543218 | [0.001675462676, 0.001675462677] |
| shared k=2 typed echo | 1,036,800 | 9,728 | 0.003203836729943888 | [0.003185242415, 0.003185242416] |

The baseline `D/E` matches the published 0.001680590709754321699421 to 2.4e-25
(printing precision) and the baseline root is the recorded complex endpoint
0.0016754626768081035, whose moment residual sits in the published
`-1.30e-24` band; the next `10^-24` grid point is rejected. At the recorded bit
endpoint 0.0017334270395898442 the shared ledger gives `f(a) - 1 = -4.25e-3`,
matching `research/centre-sharing-overhead-budget`'s table entry for `k = 2`.
So with sharing the complex side stops binding and the whole bound becomes
bit-limited at `kappa = 0.001730427469823602` (+3.4536% on the selected
0.001672660197076918), which is that package's published figure, here reached
by a concrete mechanism rather than a relaxation.

**`a < D/E` is a screen, not the acceptance test** (a control enforces this:
the exact moment at `D/E` exceeds 1 strictly). The exact moments above are the
acceptance tests.

## Delta-H: the instantiation fits the sharpest overhead budget

`research/centre-sharing-overhead-budget` prices the sharing lever's overhead
`Delta-H` as extra paid children: sharing saves 32 rank units per call, and the
overhead must stay under about 30.5-30.8 units per call to keep the full
+3.4536% gain, or 31.9-32.0 for any gain. The typed echo eliminates one
wrapper per pair: 8 rank-8 children, 64 rank units per pair, 32 per call. Its
own added work is scalar (frame powers, the two 24-ADD copy edges, the boundary
schedule), so its recursive overhead is 0 rank units and the elimination lands
entirely inside the budget. The measured scalar side also falls (table above).

## The one obstruction: hosting (window lifetime and totals delivery)

The fused pair defers the first call wrapper's `W -= X` (the ERASE analogue)
past the second call's child block. The smallest instance exhibits it exactly:
in the `k = 2` joint word all 24 work rows are dirty at the second block's
entry, where the separate schedule has already restored. The named host's
pinned contract, `research/split-centres-global/proofs/PR386-BIT-GEOMETRY.txt`,
states that `COPY/ERASE` windows remain sequential and immutable, and the
coverage identity charges one centre path per call because each call's totals
are copied out and its private temporary erased within that call. The typed
carry needs the opposite: one window spanning the pair, the first call's totals
delivered at the pair end, and uninterrupted ownership of the temporary across
the boundary.

Everything else is charged and closes:

- **Moment:** the shared ledger above, with `Delta-H` inside the sharp budget.
- **Scalar price:** fully paid, and smaller than the separate schedule.
- **Dirty state and restoration:** exact on all 56 basis columns.
- **Precision:** quantified but not closed (see the open questions); the carry
  raises prefix row-L1 from 30 to 42 at the persistent pair.

Under the unchanged contract the pair pays both wrappers: the histogram stays
`n_8 = 1152`, the moment is exactly the selected one, and no kappa change
follows from 112 saved primitives. The contract change would also require a
child exposing the order-four intertwiner `R P = Q R` (the certified typed
contract; no named host child exposes one) and a common sink for the pair's
totals, the first blocker of PR #1748.

The source-bound side of the same obstruction is already recorded on the named
schedule: `research/selected-centre-adjacent-pair-seed01fcb1` censused all 143
adjacent ordered call pairs of the pinned selected 144-call schedule and found
no pair sharing a single physical owner among its eight centre source rows, so
no adjacent pair meets even a zero-transport shared-source boundary. That
census leaves aliases, copied values, nontrivial linear maps between owners,
nonadjacent calls and a changed schedule open; those escapes are paid owner or
chart transport, which is this same hosting obligation. This package does not
rerun that census; it adds the window-lifetime and delivery side at the word
level and prices the mechanism.

**Bounded pivot (one): the single-call realization.** Make the pair one
supplier call from the start, so its single window stays sequential and
immutable. The per-call totals-delivery contract then makes the fused call copy
both calls' totals: 16 rank-8 children per pair, 128 rank units, exactly the
two-wrapper baseline. The ledger returns to the selected histogram and the
moment is identical (checked exactly). Delivering one shared set of totals
instead is the same common-sink contract change the obstruction names, so the
pivot does not escape the obligation. The route stops here.

## Reproduce

Python 3.12+ standard library and `git`, from the repository root:

```sh
python3 -B research/z4-typed-echo-supplier-instance/verify.py
python3 scripts/research_package.py --package research/z4-typed-echo-supplier-instance --check-only
```

Expected final line:

```text
PASS_Z4_TYPED_ECHO_SUPPLIER_INSTANCE smallest_k2 whole_price saved=112 D_over_E_shared=306866593893834978883114841401737599624288907847049/95780971304118053647396689196894323976171195136475136 controls=51 no_new_kappa
```

`--write` regenerates [RESULT.json](RESULT.json); the default run recomputes
and rejects drift. The engine re-checks the pinned PR #1391 emitter and
certificate hashes before importing the word emitter; all other arithmetic
(boundary recurrence, maps, invoices, tape model, ledger moments, `ln`/`exp`
enclosures) is implemented independently in this package. 51 controls cover the
mechanism reproductions, the smallest-instance map and inverse identities,
three schedule mutants, the wrapper counts and the deferred-restoration
witness, the whole-price dispatch charges, the row-L1 reproduction, both
coverage identities, the published `D/E` and moment-residual bands, the
`D/E`-is-not-acceptance control, the `Delta-H` budget fit, the pivot's
identical moment, and three mutated-ledger rejections.

**Not checked:** any native or hosted emission, the registered 3.12 replay
environment beyond this file's commands, the complex host's precision bucket
law, all-size/compiler, common-label/mutable-source realization, tape,
analytic transfer and the bit H1-H5 obligations. This is not a multiplication
theorem and does not admit any supplier.

## Open next questions

- **Does a named selected supplier admit a widened `COPY/ERASE` window with
  per-pair totals delivery?** This is the single contract change the
  instantiation needs; the shared ledger would then accept at `a* = 0.0031852`
  and move the binding side to the bit primitive. First step: inspect one
  retained supplier's owner-map window definitions and totals schedule for a
  consecutive same-sink pair, and price the widened window as extra live
  families. Blocked by the pinned immutable-window sentence and the absence of
  a child exposing `R P = Q R`.
- **Can a named host price the carry's precision envelope?** The measured cost
  is the prefix row-L1 rise 30 to 42. First step: propagate the joint word's
  exact prefix coefficient envelope through a host's fixed precision buckets
  (the 192/512-bit conventions used in the bit invoice). Blocked by the complex
  host's bucket law not being pinned in a chargeable form.

## Credit and scope

Mechanism and certified invoices: **PR #1391** (order-four paired frames) and
**PR #1410** (persistent pair), both by Cinna Davis with OpenAI Codex
assistance, extending Ross Richardson's PR #1287 and Sagar Thakrar's PR #1227;
the heterogeneous variants are PR #1768 and PR #2098. The shared-centre
scalar-macro halves are **PR #1708** (1337isnot1337) and **PR #1748**
(ToikY). The lever's sharp overhead budgets and the bit-limited kappa figure
are `research/centre-sharing-overhead-budget` (rtyu193-rgb); the adjacent-pair
owner census is `research/selected-centre-adjacent-pair-seed01fcb1`; the moment
enclosure technique and the published `D/E` are `research/selected-suppliers-de-diagnostic`
(Navinor) and the pricing model is Douglas Colkitt's
`research/complex-local-word-ceiling` with PR #1012's coverage identity. The
immutable-window sentence is from the PR #386 bit geometry (Dylan Crow lineage)
as pinned in `research/split-centres-global`. The tape convention is
`research/mutable-source-persistent-connector` (woklerx). The task-draw scope
change and its reason are recorded in [TASK.json](TASK.json); the pair-collision
check and overlap refresh are recorded there and in the claim.

New package material is Apache-2.0. Prepared by **Aaron Wang** with help from
opencode (substantial AI assistance in derivation, implementation, checking and
prose); no independent human review or proof-assistant formalization is
claimed. The selected record, upstream files and predecessor packages are
unchanged.
