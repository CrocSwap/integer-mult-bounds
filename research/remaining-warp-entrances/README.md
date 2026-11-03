# The remaining single-warp least completions do not improve the power bill

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: a source-bound finite certificate with a scoped written proof of
its all-exponent price signs. No new kappa is claimed.

For the **62 native events strictly after warp array index 13** in Dugongue's
[PR3929](https://github.com/CrocSwap/integer-mult-bounds/pull/3929) base word:

- Ten events admit no legal entrance enlargement.
- The other 52 each admit exactly one. Their original entrance dimension is
  four and their unique maximal legal entrance has dimension five.
- The canonical least completion has the identical paid histogram at warp
  indices **31 and 40**. The other **50 strictly increase every power tariff
  `r^q`, for `0<q<1`**. None decreases it.

Every maximal entrance has dimension five. The rigid array indices, in
chronological order, are `29,30,65,66,67,68,69,6,41,64`. Array order and
chronological order differ. Events at the same B position keep array order.
The verifier emits every original/capacity basis, complete new histogram,
terminal bill and price class, so these statements are independently inspectable.

This answers the remaining-event part of Open next question 1 in unpaidmoon's
[PR4163](https://github.com/CrocSwap/integer-mult-bounds/pull/4163).
That predecessor settles warp 13; ToikY's
[PR3933](https://github.com/CrocSwap/integer-mult-bounds/pull/3933) settles warp 0
and supplies the capacity method. Neither earlier event is a census target here.
Their results are cited and built on, rather than audited or replayed.

## Exact domain and the remaining choice

Fix the source word, scalar operations and coefficients, native maps and order,
registers, productive inventory and terminal caps. For each selected event,
freeze its entire earlier prefix. Enlarge that native entrance, transport its
exit through the same binary map, and allow subsequent scalar frames and native
boundaries to enlarge above their original floors. A scalar frame contains the
incoming frames of all its operands. A native exit is the image of its entrance.
Pay an explicit identity scale for each entrance climb and every terminal climb.

The capacity claim covers **every legal suffix assignment in this domain**.
The price claim covers only the **canonical least-join completion** of each
legal nontrivial seed. Larger legal scalar frames may be cheaper. PR3933 already
exhibits that distinction, so this result does not close their optimization.
Simultaneous seeds, changed words/maps, reordered operations and new helpers
are outside the finite domain. The old word is a research test case, not the
current selected PR6030 supplier.

The new result removes an unpriced canonical search direction. A next attempt
on this word needs nonminimal suffix frames or simultaneous changes. Merely
moving the same canonical one-entrance experiment to another remaining event
cannot improve its paid power bill.

## Capacity proof and finite certificate

Use the backward-capacity theorem of PR3933, whose proof is pinned in
[SOURCES.json](SOURCES.json). Here is the complete recurrence. Initialize each
register capacity to its fixed terminal cap. At a scalar event touching R,
intersect those capacities into K, require its original frame to lie in K,
and set every touched capacity to K. At a native event with map G and original
entrance U, replace the lender capacity C by `G^-1 C`, checking `U <= G^-1 C`.

For a scalar event, its common frame `Q + sum(F_r)` fits every outgoing cap
exactly when Q and every F_r fit their intersection. For a native event,
`G(U+F)` fits C exactly when U and F fit `G^-1 C`. Reverse induction therefore
gives the exact product of incoming capacities. Immediately before the chosen
native event, its lender capacity is the unique maximal entrance C. The legal
seeds are exactly `U <= U' <= C`, provided the frozen prefix fits the other
capacities. The explicit successful closure checks that proviso for every
nontrivial seed. The source word supplies the original-seed witness.

A separate implementation stores annihilator equations instead of point sets.
Intersections become row-span joins; inverse images become `h -> G^T h` on
constraint rows. Its Gaussian elimination agrees with every one of the 62
point-set capacities. This agreement and all emitted bases are finite evidence,
not an independent human or proof-kernel review of the cited theorem.

For each of the 52 nontrivial seeds, forward propagation takes the join of
original and incoming frames, and transports each native frame exactly.
The compiler emits one identity scale, on the selected lender. It preserves
every ordered nonidentity scalar/native operation, all caller fields and
original frame floors, and recomputes literal inverse cleanup. The complete
retained frame walker then checks all new frames, lifted binary actions and
climbs. Helper widths and rank mass are unchanged.

The centre descent convention is inherited unchanged. No B gate touches a
centre; restore[191], the sole centre-touching restore record, remains literal.
No native phase replay is implied by a binary lifted-action check. These are
frame/pricing certificates under the source contract, rather than a new
physical implementation or admission of the predecessor.

## All-exponent price proof

Write `x=2^q`, `y=3^q`, `d2=2-x`, `d3=3-y`, for `0<q<1`. Then

```text
1<x<2,  d2>0,  d3>0,
2d2 < d3 < (2+x)d2 < 4d2.
```

The lower bound follows from strict concavity, `2*2^q>1+3^q`.
For the upper bound, `r-r^q` is strictly increasing for `r>=2`, so
`d3<4-4^q=(2+x)d2`.

All 52 generated histogram deltas have the following forms. H_r means one
paid child of rank r; every row has zero rank mass.

| New minus original histogram | Occurrences | Power price or strict positive lower bound |
| --- | ---: | --- |
| zero | 2 | zero |
| `n(2H1-H2)`, `4<=n<=12` | 38 | `n*d2` |
| `12H1-8H2-4H3+4H4` | 3 | `4*((2-x)^2+(2x-1-y))` |
| `13H1-7H2-H3+H4` | 3 | `(2-x)*(5-x)+d3` |
| `12H1-9H2-2H3+3H4` | 1 | greater than `(7-3x)*d2` |
| `20H1-13H2-2H3+3H4` | 1 | previous row plus `4*d2` |
| `21H1-12H2+H3` | 2 | greater than `8*d2` |
| `13H1-8H2+H3` | 1 | greater than `4*d2` |
| `20H1-14H2+2H4` | 1 | `2*(2-x)*(5-x)` |

For the fifth row, its price is
`9d2+2d3-3*(2+x)d2 > (7-3x)d2 > 0`.
The seventh and eighth rows use `d3<4d2`. All other identities are direct
expansions. Thus every nonzero delta is positive throughout the open interval;
no float grid or numerical root is used. At q=1 all deltas vanish.
A fixed common ambient normalization multiplies these differences by a positive
factor. Productive targets are unchanged, so adding the same productive side
also preserves the comparison. This is not a new complete supplier invoice.

## Reproduction and evidence

From the repository root, CPython 3.12 and its standard library suffice:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/remaining-warp-entrances/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/remaining-warp-entrances/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/remaining-warp-entrances
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/remaining-warp-entrances --check-source-history
```

Another CPython 3.12 installation may replace the displayed interpreter.
The direct marker is `PASS_REMAINING_WARP_ENTRANCES no_new_kappa`. Direct
verification writes nothing and emits a newly generated receipt containing
all 62 rows and SHA256 hashes for every package file and declared live input.
The registered normal and optimized commands each have a 180-second limit.
The PR body records executed times and hosted status.

Both capacity representations, all 52 compiled words and complete frame bills,
ordered-operator preservation, original floors, caller fields, helper widths,
rank mass and all symbolic sign classes are checked. Rejections cover malformed
vectors/subspaces, singular maps, unproved price patterns, an under-sized seed,
an over-capacity seed, a wrong transported exit and an omitted entrance climb.
Nineteen rejection controls run in total, including four altered-source byte checks.
Input bytes and Git blob IDs are authenticated before execution and again after.
The retained frame walker is loaded from those source bytes; it is not a new
independent audit. No predecessor verification entry point is executed. The retained frame bill
and cleanup routines are explicit reused dependencies.

## Scope, credit and next questions

Source base is canonical main `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority
8, selected conditional kappa .003125804. The selected binding control passed.
[TASK.json](TASK.json) explicitly changes the current decoder/coframe card to
this older source-bound obstruction. Live PRs, handoffs, reservations, main and
merged-work terms were checked. The overlap snapshot covers 560 open PRs and
6,601 Discussion records, but local sparse notes omit 8,775 HEAD note paths.
Arbitrary historical diffs and unpublished work remain outside coverage.

Credit unpaidmoon/PR4163 for the remaining-event question; ToikY/PR3933 for the
capacity and least-completion theorem; Dugongue/PR3929 for the word, transported
frame interface and compiler; Sagar Thakrar/PR3687 and Arham Tahir for the retained
frame semantics; dataisfire/PR3734, zxv/PR3682, Ross Richardson/PR3605, Jeremy
Kothe, Cinna Davis/PR2226, Tekalign and the retained native, owner and compiler
lineage. Classical binary elimination, lattice joins, concavity and elementary
power identities retain their credit. The new contribution is the remaining
62-event certificate and its price classification. Global mathematical
literature priority is unclaimed. Existing credits and source bytes are intact.

Physical native phases, actual owner/idle fills, ordinary tape/precision costs,
compiler closure, stock, analytic recovery and selected admission are not proved
or replayed. All five selected framework assumptions remain. No selected cold
replay, Lean or Docker run was performed. Independent human and formal
proof-kernel review are unclaimed.

### Open next questions

Can larger legal suffix frames beat the canonical price for one of these 52
seeds? First optimize frames within the emitted exact capacities and pay every
transition. Least closure settles feasibility, not price; a priced attaining
word and its native/owner contract remain blockers. The two equal-price seeds
are concrete starting points, without a predicted gain.

Can simultaneous entrance changes share enough suffix climbs to improve the
bill? First specify one pair and propagate their joint seed while preserving
all arbitrary inputs and terminal caps. The single-seed census gives no
additivity theorem or favorable joint budget. This follow-on is not pursued.

## Verifier constraints

The fixed source has nine binary axes, 704 possible physical registers, 72
native events and fewer than 20,000 B/restore events. Subspace point sets have
512 bits. A bounded 4,096-entry span cache retains at most 18 input vectors per
key. At most one new word and its frame walk are live at a time. Each source
and package read is capped at four MiB; expanded input is separately capped.
Functions are shorter than sixty physical lines. Checks use explicit failures
and remain active under optimization.

Power of Ten rule 3 deviation: CPython allocates managed integers, dictionaries,
Fractions in the retained walker and transient lists. These fixed source/input
caps and sequential processing bound the collections; no fixed-allocation
runtime guarantee is claimed. Rules 8/9 deviation: two fixed, byte-authenticated
Python modules are compiled directly, avoiding stale local bytecode; the span
cache and rejection helper have bounded local call targets. No plugins,
subprocesses, network or generated executable code are used. Source/checkout
stability is required; before/after hashing is not an atomic snapshot. The
retained walker has its existing local lambdas and mutable memo table, bounded
here by the fixed finite family. Warning-strict normal/optimized replay and AST inspection
provide the available diagnostics; no external static analyzer was run.
