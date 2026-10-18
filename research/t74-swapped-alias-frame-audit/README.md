# Independent frame and lender-readiness audit of PR2588's swapped aliases

**Finite certificate and a scoped analytic corollary; no new κ.** On both
pinned providers, PR2588's substitutions of helpers 596/600 for 648/649 at
lenders 80/88 have the claimed complete local histogram change

\[
\Delta n=-2e_1-2e_3+2e_4.
\]

The audit independently reconstructs all chronological frame charges with
explicit subsets of the 512-element vector space, and pulls the two moved
source-partner rows backwards through exact rational, noncommuting operator
words. All **four moved-handoff rows** (two lenders, two candidate providers) are
the lender's own arbitrary input. The main contribution is a source-bound
explanation and independent check of this particular component, including
failure controls that distinguish frame legality from dirty-state correctness.
The construction and its improvement belong to Jeremy Kothe and the credited
predecessors. No defect in the audited component was found.

These are separately implemented, author-run checks, not maintainer review or
independent human review. They do not certify the complete κ claim.

## Exact sources and task

Base main: `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4.
The claim is in [discussion #2605](https://github.com/CrocSwap/integer-mult-bounds/discussions/2605).
Task `complex-new-helper-inventory`, chooser nonce
`b3b5ee2f84cf3429266e004dacac0b21`, scope key `5868e5281a1e63d41a22`.
The scope is **changed** from constructing a new helper inventory to auditing
a changed source binding and its dirty-lender interface. This does not claim
to meet the original construction card's acceptance gate. See `TASK.json`.

| Source | Exact head | Role |
|---|---|---|
| [PR2588](https://github.com/CrocSwap/integer-mult-bounds/pull/2588) | `8cd9dc88e24f062e2ca2fa7f4844a3d3319381fb` | Candidate complete base/extra BORROW-WORD payloads |
| [PR2575](https://github.com/CrocSwap/integer-mult-bounds/pull/2575) | `921c229b4f030121a1d305de6259e174cd391955` | Comparison complete base/extra payloads |
| [PR2530](https://github.com/CrocSwap/integer-mult-bounds/pull/2530) | `b4012098048e12500b2d33d2e84be281915a27ac` | Source-partner mechanism credit; no direct code import |

`INPUTS.json` records original paths, Git blobs, compressed SHA256 and
uncompressed-payload SHA256 for the four verbatim inputs. No predecessor
builder, elimination routine, frame pricer, scalar replay or stored receipt is
imported. Only the input word data and its inherited frame-charge contract are
used. `inputs/NOTICE` preserves the source notice. The selected-result record
and catalogue in `SOURCES.json` are historical provenance, not mutable inputs
to this audit.

The closest earlier pricing audit is [PR2359](https://github.com/CrocSwap/integer-mult-bounds/pull/2359),
which reconstructed the earlier PR2322 handoff bill. This package checks the
new PR2588 source/helper substitutions and their earlier source-partner cuts.
The concurrent [discussion #2606](https://github.com/CrocSwap/integer-mult-bounds/discussions/2606)
audits all eight predecessor source partners and recovery/read ordering; the
optional content check here is restricted to PR2588's two newly moved cuts.
[Discussion #2612](https://github.com/CrocSwap/integer-mult-bounds/discussions/2612)
searches further simultaneous assignments, rather than auditing this fixed swap.
At the final overlap check, [PR2621](https://github.com/CrocSwap/integer-mult-bounds/pull/2621)
reported a new order/fill on unchanged PR2588 words. Its global claim is not
audited here; this package intentionally retains the exact local source pins.
PR2472 checks entrance Clifford wrappers; PR2478 and PR2508 guard centre-cut
and helper-index bindings. Their coverage is credited and is not replaced by
this package. This account's PR2394 checks PR2339's initial native prefix,
a different component and different word.

## Reconstructed invoice

The following values are independently reproduced for **each** provider:

| Quantity | PR2575 | PR2588 |
|---|---:|---:|
| Rank-1 children | 2,369 | 2,367 |
| Rank-2 children | 632 | 632 |
| Rank-3 children | 320 | 318 |
| Rank-4 children | 118 | 120 |
| Rank-5 children | 26 | 26 |
| Rank-7 children | 8 | 8 |
| Total local rank mass | 5,251 | 5,251 |
| Total charged children | 3,473 | 3,471 |
| Surviving helpers | 422 | 422 |
| Helper width mass | 3,395 | 3,395 |

Both inventories are `{4:33, 5:9, 7:62, 8:78, 9:240}`. Each word has
646 independent live roles, 58 B-phase handoffs, 24 prelude warps and 4,529
explicit cleanup events. The full local invoice includes prelude raises,
ordinary A/B climbs, centre COPY descents, restoration and final-frame raises.
Cleanup touches only full-frame live roles or their full-frame private buffer
counterparts; no additional local frame climb is hidden there. Buffer values,
allocation, clearing and global stock charges are separate obligations.

The section delta is particularly useful for review:

| Section | Candidate minus predecessor |
|---|---|
| Prelude | `+4 e1` |
| B | `-6 e1 -2 e3 +2 e4` |
| Ordinary A, centre COPY, restoration, final raises | zero |

The net four extra prelude raises come from **eight new line-45 target levels**
(targets 11, 63, 71, 76, 81, 87, 90, 92), while **four line-30 levels disappear**
(targets 75, 82, 86, 93). Target indices are zero-based, relative to the target
block. The eight centre descents still split into eight rank-7 and eight rank-1
children. Thus the net prelude bill must be counted even though the centre bill
is unchanged.

Only six raw register charge histograms change:

| Register(s) | Delta per register |
|---|---|
| Lenders 80, 88 | `-2 e1 + e2` |
| Helpers 596, 600, newly removed | `-3 e1 -e2 -e3` |
| Helpers 648, 649, restored to the inventory | `+4 e1 +e4` |

`CERTIFICATE.json` contains their complete before/after charged transitions,
including event positions and exact subspace incidence masks, all per-role and
per-section histograms, and full charge/warp trace hashes. It also records all
twelve target-level changes. Equal per-role histograms need not mean equal
chronology, so the trace hashes and section charges are retained separately.

## Why this lowers every local moment

For any `0 < p < 1`, both `(1/4)^p > 1/4` and `(3/4)^p > 3/4`.
Multiplying their sum by `4^p` gives `1 + 3^p > 4^p`. Consequently,

\[
\sum_r\Delta n_r r^p=2(4^p-3^p-1)<0.
\]

The rank mass is unchanged because `-2 - 2*3 + 2*4 = 0`. For any fixed
normalization `m^p W > 0`, the normalized local moment strictly decreases by
this expression divided by `m^p W`. This is an analytic statement throughout
the open interval, not a numerical comparison at a chosen saving.

The corollary applies when all other charges are held fixed. It establishes
neither feasible reuse of a physical owner map nor a global saving or κ.
The complete swapped construction still needs its native, physical and outer
checks. No global optimum or new ceiling is claimed.

## Frame and source-state methods

The frame engine expands every generating list by XOR into a literal set.
Dimensions are the base-two logarithms of set cardinalities; containment is
set inclusion. Chronological gates require monotone frames, except for the
explicit zero-rank coordinate changes. Each warp is checked as a permutation
of all 512 vectors, mapping its source subspace onto its destination. The
inverse-transpose maps the complementary subspaces correctly. The checker
also maps all 512 elements of
`L_U = {(x,x+z): x in U, z in U^perp}` onto `L_E` under
`(x,y) -> (Gx, Gx + G^-T x + G^-T y)`.
This verifies the stated geometric interface, not the phase of an emitted
Gaussian/Clifford circuit.

The scalar checker is a separate reverse-covector calculation. A coefficient
is a rational linear combination of reduced words in formal invertible warp
symbols. Pulling a row backward through an ADD adds its coefficient to the
source; pulling it through a warp multiplies that coefficient **on the right**
by the warp symbol. Only adjacent inverse symbols cancel. Hence an identity
in this free algebra holds for any realization of the invertible symbols,
without assuming that unrelated warps commute.

At the two newly moved handoffs in PR2588, the complete pulled-back row
is exactly `e_lender` in both providers:

| Lender | PR2588 B cut | Pulled-back row |
|---|---:|---|
| 80 | 916 | `e80` |
| 88 | 931 | `e88` |

A cut `j` means immediately before event `B[j]`, after any earlier same-cut
warps. The comparison word places these warps at cuts 1062 and 1063; those
predecessor row identities and its other six source-partner handoffs are left
to the distinct concurrent audit linked above.

These are forward arbitrary-input readiness statements. For an invertible
prefix `P`, `e_r^T P=e_r^T` also implies `P^-T e_r=e_r`; that is a dual
**column** identity, not a claim that the dual row is restored. Complete dual
word correctness is outside this package.

The readiness checks include the actual prelude, preconditioner, compensation,
centre-cut scalar gates and all earlier B gates/warps. The pinned words have no
initial operator-correction terms. No non-target reads a target in A or B.
Thus no clean-input assumption or omitted target feedback is used.

Two sign faults are especially diagnostic. In each candidate provider,
flipping B[688]'s `80 += -88` coefficient gives lender 80 the row
`x80 + 2*x88`. Flipping B[687]'s `88 += x80/2` coefficient gives lender 88
the row `-x80`. Both mutations leave the **entire independently computed frame
receipt unchanged** and fail the readiness check. This demonstrates why a
correct rank ledger alone does not establish the dirty-lender interface.

## Reproduce and controls

CPython 3.12, standard library only, from the repository root:

```sh
python3 -I -B scripts/research_package.py --package research/t74-swapped-alias-frame-audit
```

Expected marker, in both normal and optimized modes:

```text
PASS_T74_SWAPPED_ALIAS_FRAME_AUDIT words=4 providers=2 delta=-2r1-2r3+2r4 helpers=422 handoff_rows=4 frame_controls=18 readiness_controls=4 positive=4 no_new_kappa
```

The hook compares regenerated mathematical data with `CERTIFICATE.json` and
writes no package files. For explicit regeneration to a **new** path:

```sh
python3 -I -B research/t74-swapped-alias-frame-audit/verify.py --write-certificate new-certificate.json
```

The 18 frame controls cover incorrect reports, singular and wrong-image warps,
a late handoff, a non-centre cut read, a wrong target room, a wrong inventory,
a removed-helper touch and a nonzero wrapper frame, on both providers. Four
additional coefficient-sign mutations preserve the frame receipt but fail
handoff readiness. Positive controls include equivalent redundant/reordered
frame generators on both providers, an explicitly noncommuting two-warp
covector with coefficient `2/3`, and its exact inverse prefix. Runtime guards
remain active under `python -O`.

## Limits

Not checked: the complete scalar endpoint or cleanup-buffer values, native
Clifford phases and lowered circuits, physical owner placement and private
stock, precision/tape costs, the full global moment, outer arithmetic, all-size
compiler/realization/analytic assumptions, or bit H1–H5. None of these is
inferred from the local certificate. The maintainer-selected record is unchanged.
The only selected-record operation used in validation is its binding check,
not its complete cold replay.

## Open next questions

The structured questions are in `TASK.json`:

1. Test one further pinned lender/helper substitution using these per-role
   traces and covectors, then its full native and global admission. It needs an
   actual changed word and complete phase, hosting, stock and precision checks.
2. Independently replay the complete predecessor supplier and outer packages.
   This needs their full dependency environment and owner/native sources;
   the local result here is only one reusable part of that review.

## Credit

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.
OpenAI Codex (GPT-6 Astra) performed the derivation, implementation, checking and
writing. No independent human review is claimed. Apache-2.0.

Jeremy Kothe (jeremykothe2) supplies PR2588's swap and PR2575's integration;
zxv supplies PR2530's source-partner aliases and restoration schedule; Tekalign
(tekuuu), PR2436, supplies lifted-target aliases and the prelude mechanism;
Vlado Vojdanovski, PR2322, supplies coherent handoffs; Cinna Davis
(1337isnot1337), PR2226, supplies anticipatory dirty borrowing. The T74,
entrance-raise, native/compiler and supplier lineage retains all source credit.
Marius-Paul Dumitrean's centre-cut guard, ywz65's helper-index guard and the
independent pricing/wrapper audits are credited above. The original source
notice is retained verbatim. The new material is the finite-set interpreter,
reverse-covector checker, localized delta certificate, analytic corollary and
semantic controls.
