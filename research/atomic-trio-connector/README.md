# Atomic triple-sum connector

**Scoped negative result; no new kappa.** One new complete call
`TRIO_{j,k,l}: z += B_j x_j + B_k x_k + B_l x_l` does not improve the charged
universal all-nonzero-row budget on three or five sources. The symbol is
atomic: it contributes one prefix step of weight three, three source-map
applications and one root frame. It does not expose the two partial sums.

This refines the connector-alphabet card. The fixed-alphabet premise that
changes is the ban on combined source queries in
[the universal connector boundary](../universal-connector-boundary/README.md).
Weight-2 DUO steps, a second connector, mutable sources and a larger source
count are not part of this result.

```sh
python3 -B research/atomic-trio-connector/verify.py
```

Expected:

```text
PASS_ATOMIC_TRIO_CONNECTOR three_source_orders=24 misses={3: 8, 5: 8, 6: 8} five_source_words=6048000 full_covers=0 best_coverage=30
```

Python 3.10+ and the standard library suffice. The registered replay is the
same command through `scripts/research_package.py`.

## Interface and price

The predecessor interface is unchanged except for the new symbol. Rows `x_j`,
`y_i` and the connector `z` start arbitrarily dirty. Maps `A_i` and `B_j` are
exact and need not commute. Sources stay read-only. A schedule may use the old
calls `B_j: z += B_j x_j` and `A_i: y_i += A_i z`, plus any number of atomic
triple sums on distinct sources. Paired `A` readouts still see only the
boundaries between B-side calls. Each nonzero output row therefore still needs
two boundaries whose prefixes differ by its mask, and every source must appear
an even number of times for `z` to return to its initial value.

Let `λ_j > 0` be the price of one application of `B_j`, and let `f ≥ 0` be the
price of one B-side root frame: dispatch, private-scratch restoration, head
return and entry/exit. A single toggle costs `λ_j + f`. A triple sum costs
`λ_j + λ_k + λ_l + f`. Charging it as one frame without the three applications,
or as a free fusion of an arbitrary old word, is a different contract and is
not used here.

## Why fewer frames cannot cover

A closed B-side word of `k` calls has at most `k` distinct prefixes. Those
prefixes determine at most `k(k-1)/2` nonzero differences. Covering every
nonzero mask of `n` sources therefore needs `k(k-1)/2 ≥ 2^n - 1`. Restoration
makes `k` even once any number `t ≥ 1` of triple sums is included, because the
application count is `A = k + 2t`.

| Batch | Known repair | Counting | Only shape that could tie that repair | Outcome |
|---|---|---|---|---|
| 3 sources, 7 masks | 6 toggles, 6 applications | `k ≥ 6` and `A ≥ 8` | none | strictly more applications |
| 5 sources, 31 masks | 12 toggles, 12 applications | `k ≥ 10` and, to keep `A ≤ 12`, only `t = 1`, `k = 10`, `A = 12` | 6,048,000 words | none covers all 32 masks |

The original counting window above does not alone exclude ten calls with
multiple TRIOs. The [parity supplement](PARITY.md) now excludes every ten-call
odd-step cover, independently of its source-application count. Its complete
8,736-case check supplies the missing premise in the price argument below.

The three-source repair is the predecessor's four-source word with the idle
source deleted: `B0 B1 B0 B1 B2 B2`. The five-source repair is the predecessor's
twelve-toggle word, which can repeat whichever source is cheapest. Against
either repair, every positive price vector leaves a gap of at least
`2 min λ_j` on the source side and no frame saving.

The four-call three-source words are not covering candidates: four prefixes
give at most six nonzero differences. They do meet that ceiling. All 24 orders
of `{e0+e1+e2, e0, e1, e2}` have four distinct prefixes and miss exactly one
weight-2 mask, eight times each for masks 3, 5 and 6. The word `TRIO, B0, B1, B2`
has prefixes `0, 7, 6, 4` and misses 5. The missing mask is the sum of the four
prefixes in every order.

## Five-source census

Appearances totaling 12, each even and at least 2, must be `4,2,2,2,2`. With
one triple sum, the source of multiplicity 4 may lie inside or outside the
triple. There are 30 inside-heavy patterns and 20 outside-heavy patterns.

```text
30 * 10! / (3! 2! 2!) + 20 * 10! / (4! 2!) = 6048000
```

Two generators enumerate every word: multiset permutations with the triple sum
inserted in each slot, and direct placement by index combinations. They agree
on the coverage histogram

| Masks covered | 16 | 19 | 21 | 22 | 23 | 24 | 25 | 26 | 28 | 29 | 30 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Words | 140400 | 878400 | 1162800 | 208800 | 993600 | 1022400 | 399600 | 658800 | 396000 | 57600 | 129600 |

The largest coverage is 30 of 32. No word covers 32. A listed control,
`TRIO_{0,1,2} B0 B0 B0 B1 B2 B3 B3 B4 B4`, is restored and misses at least one
mask; no paired readout emits that mask from the all-ones input.

The predecessor controls are also checked, not re-proved: the ten-toggle word
misses only mask 21, and the twelve-toggle word covers every mask. Identity
schedules for the three-source repair and the twelve-toggle repair are replayed
on basis and mixed inputs, with a dirty connector, forward and backward. The
three-source repair is additionally replayed at length 2 with three
noncommuting source maps. Dropping the mask-7 row is a failure control.

## Open next questions

Could a different single instruction, whose step is not an atomic weight-3 sum
and not a weight-2 DUO, cover all 32 five-source masks in ten B-side calls
while paying at most twelve source applications? The parity supplement rules
out every odd-weight candidate; a new step must escape that parity premise. That is the only remaining
counting window in which a new B-side step could tie the twelve-toggle leaf
bill and still reduce the frame count. The first step is to fix the step subset
and the even-appearance equation before searching. Weight-2 DUO is discussion
#1403. Two-connector transfers are #1412, #1486 and PR #1438; #1486 has since
reported that four paid transfers do not cover these masks, and this package
does not continue that search.
An interruptible triple that exposes its partial sums is the old toggle
alphabet inside one frame, which this price model does not treat as free.

## Credit and limits

The predecessor is Ross Richardson's universal connector boundary, with the
PR934 binary-query contract. This package adds the atomic triple-sum price and
the three-source and five-source exclusions above. It does not claim priority
for that boundary, for Navinor's DUO proposal, or for the two-connector
transfer results.

No selected supplier, certificate, review ledger or kappa changes. Common-label
realization, frames, hosting, precision, tape and the analytic hypotheses of the
selected construction remain open. The census is a finite exclusion of one
charged symbol on two batch sizes, not a proof-assistant theorem and not a
lower bound for every other connector alphabet.

Prepared by Riquelme Soares (@hevlyo) with substantial Cursor agent assistance.
New work is Apache-2.0. No independent human peer review is asserted.
