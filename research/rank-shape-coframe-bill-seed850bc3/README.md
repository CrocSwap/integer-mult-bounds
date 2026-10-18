# Fully charged block-climb gate screen over all payload reblockings

**Scoped cost-alphabet result for the drawn `complex-rank-shape-decoder` card
(method 2). No physical decoder, word-level co-frame census, supplier admission
or new kappa; the selected record is unchanged.**
Agent: Aaron Wang, with help from opencode (substantial AI assistance; no model
named; no independent human review). Base commit
`d8e0f83f00191df62174b641e9fff055c357f641`, priority revision 6.

The card asks whether a decoder can deliver the local paid mass in fewer,
larger-rank children, with copies, frames and restoration counted. After
[PR 3039](https://github.com/CrocSwap/integer-mult-bounds/pull/3039) excluded every charged
block-climb group and [PR 3066](https://github.com/CrocSwap/integer-mult-bounds/pull/3066)
showed free and charged groups can mix in a passing call, the open question is
quantitative: how much zero-charge structure does the card's +5% gate actually
require? This package answers that exactly, over **all** partitions of the
selected word's 2,412 rank-one payloads into block children, with the proved
minimum charges for copies (rank-k frame transports, PR 1429) and dirty-slot
restoration (one rank-1 save per block without owned temporaries, PR 3039).

## Model and conventions

The frozen PR 1240/PR 1429/PR 1605 cost alphabet: width 73, stock 896/9,
centre charge 64, old idle mass 1,646 at rank 51 (halving guard), baseline
profile `{1:2412, 2:418, 3:432, 4:142, 5:82, 8:8}`, paid mass 5,586. The
acceptance target is `a* = 21/20 * 1690054109089/10^15` (the card's +5% over
the selected packing ceiling). Two accounting conventions are reported:

- **strict contract** (PR 1605's added-work contract, PR 3066's convention):
  every added child is paid on top of the old idle bill, none receives idle
  credit. This is the acceptance-relevant screen ("all copied information,
  frames and restoration counted").
- **coverage-law convention**: every added rank unit is refunded from old idle
  mass (the `ceiling.py` model). Favourable to any construction.

## What is established

1. **Exact gate thresholds for zero-charge groups (strict contract).** A
   reblocked profile passes the +5% moment gate at `a*` only if zero-charge
   groups (both operand vectors already at the block frame, owned gather
   slots) cover enough payloads:

   | Block cap | Minimum zero-charge coverage | Blocks | Full-coverage slack | Taxed blocks allowed at full coverage |
   |---|---:|---:|---:|---:|
   | 16 | 363 of 2,412 payloads | 23 | 10 rank-1 units | 10 of 151 (at least 141 zero-charge) |
   | 51 | 255 of 2,412 payloads | 5 | 14 rank-1 units | 14 of 48 (at least 34 zero-charge) |

   Coverage/charged-work tradeoff (slack in rank-1 units at `a*`): cap 16 with
   363, 768, 2,412 covered payloads gives 0, 1, 10 units; cap 51 with 255,
   1,530, 2,412 gives 0, 8, 14 units. Under the coverage-law convention the
   slack is 1,447 units (cap 16) and mass-law-capped 1,646 (cap 51).

2. **The uniformly taxed family is excluded under the strict contract.** With
   the PR 3039 restoration tax imposed on every block (no owned temporaries),
   a taxed block of any size `k = 2..51` is strictly dearer than its `k`
   payload singles at `a*` (50/50 exact enclosure inequalities). Blocking is
   then counterproductive at every size, so the optimal uniformly taxed
   realization is the unchanged selected word: moment
   `1.000245413040243..1.000245413040244` at `a*` (fail). The taxed greedy-51
   profile is worse: its strict-contract moment is above one for **every**
   `a >= 0`. This closes PR 3066's conditional sentence about a uniformly
   taxed construction with exact numbers. Under the coverage-law convention
   the same taxed profile would still clear the +5% ceiling gate (1.79x), so
   the exclusion is a statement about the added-work contract, not about the
   coverage law alone.

3. **Charged copies are excluded too, and exceed the mass law.** One paid
   rank-k transport per block is strictly dearer than the payload singles for
   every `k = 2..51` at `a*` (50/50), and its rank mass is 7,998, above the
   coverage law's 7,232 total, so the law rejects such profiles outright.
   Every mixed transport/restoration variant screened fails the strict moment
   (see `RESULT.json` `contracts`).

4. **Exact predecessor convergence.** The 363-payload minimum coverage and the
   10-unit slack are PR 1605's independently derived rank-16 threshold and
   call budget, now derived as optima of one exact gate arithmetic. PR 3066's
   seven published mixed-profile moments are reproduced as controls; its five
   charged pairs spend `0.001390065582957` of the `0.001395098052012` slack its
   q=0 zero-charge row leaves (about 10.0 rank-1 units at the margin, matching
   the budget computed here), and six pairs exceed it.

5. **Ceiling screen (coverage law, the card's ceiling definition).** The greedy
   reblocked shapes clear the +5% ceiling gate by a wide margin once their
   groups are zero-charge:

   | Profile | Ceiling bracket | Ratio to selected ceiling | +5% gate |
   |---|---|---:|---|
   | Selected word (control) | 0.001690054109..0.0016900541091 | 1.000x | fail |
   | Greedy cap-16 (150x16 + 12) | 0.002480124284..0.0024801242841 | 1.467x | pass |
   | Greedy cap-51 (47x51 + 15) | 0.0030761867866..0.0030761867867 | 1.820x | pass |
   | Greedy cap-51 + 48 saves | 0.0030266309503..0.0030266309504 | 1.790x | pass (relaxation) |

   The last row is the favourable coverage-law relaxation only: under the
   strict contract the same profile has moment above one for every `a >= 0`.
   An optimistic passing relaxation is not acceptance; the strict screens in
   items 1-3 are the acceptance-relevant statements.

6. **Certificates.** Greedy block-size optimality is exact, not heuristic: 600
   strict subadditivity inequalities (every legal merge strictly lowers cost),
   1,225 payload-monotonicity inequalities (`c(k)/k` strictly decreasing), 50
   tax-dominance and 50 transport-dominance inequalities at `a*`, and an
   exhaustive small-instance check (all 918 other partitions of 24 payloads
   under cap 8 are strictly dearer than greedy `[8,8,8]`). All signs are
   strict enclosures from the retained PR 1240 engine, executed from
   authenticated source bytes.

## Route note (recorded obstruction)

PR 3039's open question 1 (read the pinned t16 canonical word's per-child
operand frames and partition the payload into co-frame groups) was assessed
and killed for this session: the canonical word archives record operations and
a frame registry, but no per-child operand frame field, so deriving them needs
a separate frame-propagation pass over each child's operand spans; guessing
them would misstate the word. The thresholds above are the exact bar that pass
must clear.

## Reproduce

Python 3.12, standard library only, exact rational arithmetic throughout
(about 40 seconds):

```sh
python3.12 -I -B research/rank-shape-coframe-bill-seed850bc3/verify.py
python3.12 -I -B research/rank-shape-coframe-bill-seed850bc3/verify.py --write
```

Expected final line:

```text
PASS_RANK_SHAPE_COFRAME_BILL min_cover_cap16=363 slack_units_cap16=10 min_free_blocks_cap16=141 slack_units_cap51=14 min_cover_cap51=255 uniform_tax_excluded=1 no_new_kappa
```

`verify.py` is read-only without `--write`; it recomputes every number from the
pinned inputs and fails on receipt drift, source drift, any predecessor moment
mismatch or any undecided sign.

## Scope and limits

- Covered: the cost-alphabet model above, block caps 16 and 51, the PR 1429
  transport charge, the PR 3039 per-block restoration tax, both accounting
  conventions, all payload partitions (greedy optimality certified).
- Not covered: word-level realizability (which of the actual 2,412 rank-one
  children are co-frame with owned gather slots); physical decoder identities;
  the rank-2/rank-3 step children; masked or overcomplete supports (which
  would change an assumption of the eight-term all-pairs bound); any changed
  coverage law, template, port count or centre path; native/hosting/precision
  bills. No supplier admission and no kappa claim.
- Claims: a scoped lower bound on effective payload child rank for one fixed
  support alphabet (with the proved minimum charges, blocking helps only at
  zero charge), exact gate thresholds, and the strict-contract exclusion of
  the uniformly taxed family. Not a lower bound on all decoders.

## Credit

- [PR 3039](https://github.com/CrocSwap/integer-mult-bounds/pull/3039) by Aaron Wang
  (navinor, AI-assisted): the charged-group obstruction, the `k = 2`
  identity classification and the restoration tax made into a lower bound.
- [PR 3066](https://github.com/CrocSwap/integer-mult-bounds/pull/3066) by Ross
  Richardson (AI-assisted): the mixed-profile correction and its published
  moments, replayed here as controls; its conditional uniformly-taxed sentence
  is what items 2-3 close.
- [PR 1605](https://github.com/CrocSwap/integer-mult-bounds/pull/1605) by Arham Tahir
  (AI-assisted): the integer block budgets, the exact target and the added-work
  contract; its 363 threshold and 10-unit budget are re-derived in item 1.
- [PR 1240](https://github.com/CrocSwap/integer-mult-bounds/pull/1240) by Doug
  Colkitt (AI-assisted): the cost model and the retained exact interval engine,
  executed from authenticated source bytes.
- [PR 1429](https://github.com/CrocSwap/integer-mult-bounds/pull/1429) by Ali Romman
  (AI-assisted): the transport-charge contract.
- [PR 679](https://github.com/CrocSwap/integer-mult-bounds/pull/679) by Greer Guthrie:
  the native direct-sum/tensor-child obstruction, unchanged.

Apache-2.0.

## Open next questions

- **How many of the selected word's actual 2,412 rank-one payloads are
  zero-charge co-frame groups?** This decides the lever: item 1 shows at least
  363 (cap 16) or 255 (cap 51) payloads must be, with at most 10/14 taxed
  blocks even at full coverage. First step: the per-child operand-frame data
  pass over `t16/global/base/providers/gauge44` recorded in the route note.
  Blocked by: that frame-propagation pass and the owned-slot (temporary
  lifetime) analysis, neither of which exists in the archives.
- **Does a shared-call transport contract change the strict-contract
  exclusion?** PR 1605 budgets ten rank-1 units per call for shared charged
  work; item 3 excludes per-block charges but shared charges inside the slack
  remain open. First step: declare one explicit sharing schedule and screen its
  profile at `a*`. Blocked by: no such schedule is currently proposed.
- **Do the rank-2/rank-3 step children admit the same treatment?** The card
  names "rank-1 to rank-3 steps"; this package covers the rank-one payload
  only. First step: declare the joint replacement contract and its coverage
  identity before any synthesis (PR 3039 open question 2).
