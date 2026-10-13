# Fixed-factor frame 524 construction

Prepared by Ross Richardson (@RossRichardson) with substantial OpenAI Codex
assistance. Apache-2.0. The construction starts from the selected PR589 word,
which builds on PR555's punctured R439 word and its earlier E8 constructions.
It uses the fixed-factor destination-once class also investigated for other
objects in concurrent PR844, PR880 and PR908; no code from those PRs is imported.

The exact base is `f567884aeb8851b6e794af1184119a3bfbe1e631`. The source is
`research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz`, SHA256
`e3e301e62bc2b41dbf1ceac0acf3d35824ebeab1848c5a2142d4577b109da52f`.
All intervals below are zero-based and half-open. The object is exactly phase-B
`B[449:490]`, consisting of 41 singleton additions at frame 524 on registers
`[8,12,31,37,40,45,73,78,81,86,105,110]`.

## Fixed factors and finite search class

The source has two consecutive destination-grouped LU factors:
`B[449:466]` with 17 additions and `B[466:490]` with 24. Within either factor,
every nonidentity destination occurs in a single consecutive group. These
factor endpoints are held fixed as integer matrices, rather than only modulo 2.
The cut is the source LU turn before `73 += 40`; it is not a newly optimized
factorization. The source implementation of this class is
`research/e8-bit-p111-tuned/code/nodeopt.py:lu_ops`.

For each fixed factor, the searched domain permits any order of the 12
destinations. Each destination is written once by adding a multiset of the
other current rows with positive integer multiplicities. A zero-cost write is
permitted for an identity target row; its emitted circuit contains no gate.
Thus the search includes all `12! = 479001600` destination orders. The cost is
the sum of donor multiplicities: multiplicity `c` emits exactly `c` singleton
additions. No temporary register, negative donor, boundary change, alternative
factorization, repeated destination group or copied-information mechanism is
included. Identity writes merely multiply equivalent orders, and do not
increase the realizable circuit class or change its minimum.

## Exact subset recurrence

Let `T` be one fixed integer target matrix, with rows indexed by the sorted
register list. For a subset `S` of destinations already completed, let `M(S)`
have row `T_j` for `j in S`, and unit row `e_j` otherwise. This matrix depends
only on `S`, not on the history. Any legal history to `S` is a product of
elementary row additions and therefore makes `M(S)` unimodular with an integral
inverse.

For `i not in S`, the unique donor vector is

```text
c = (T_i - e_i) M(S)^(-1).
```

There is a legal write exactly when `c_i = 0` and every coefficient is a
nonnegative integer. Necessity follows by expressing the desired row increment
in the independent current rows. Sufficiency follows by emitting each donor
`c_j` times. Uniqueness excludes alternative positive multisets for the same
subset and destination.

Starting with `F(empty)=0`, the Bellman update is

```text
F(S union {i}) = min(F(S union {i}), F(S) + sum_j c_j)
```

over every legal transition. The search processes subsets in increasing integer
mask order; every child has a larger mask. It stores integral inverses and
updates them by

```text
M(S union {i})^(-1) = M(S)^(-1) (I - e_i c).
```

Since `c_i=0`, this is the exact inverse of the elementary write. When a subset
is reached through another history, the independently updated inverse must
match. `search.py` enforces this equality explicitly. The stopping rule is
completion of every reachable subset and every not-yet-written destination,
without a time cap, heuristic pruning or coefficient cap. Seed 13 selects the
lexicographic tie order after a seeded shuffle, and does not change coverage.

The independently written `factor_check.py` uses nonnegative donor multiset
exact-cover enumeration and a backward Bellman recurrence. It does not import
the inverse search or its helper functions. It therefore checks the same finite
class by a different method rather than replaying the same optimizer.

## Result and scope

Both factors have 4096 reachable subsets and 24576 examined transitions. Their
exact minimum costs are 12 and 15 respectively, so the block falls from 41 to 27
singleton additions. All emitted donor multiplicities equal 1.

| factor | feasible transitions | feasible orders | minimum-cost orders | old | minimum |
|---|---:|---:|---:|---:|---:|
| `[449:466]` | 23552 | 239500800 | 39916800 | 17 | 12 |
| `[466:490]` | 21120 | 43908480 | 992640 | 24 | 15 |

`CANDIDATE.json` contains the exact integer matrices, donor vectors, destination
orders and emitted gates. Exact integer equality implies equal action over F2
on every incoming column, including dirty source/helper columns. Concatenating
the two verified factors gives the source block's complete forward action.
This is a construction and a finite-class minimum, not an unrestricted circuit
minimum or a formal proof of the full multiplication theorem.

## Complete local addition and restoration accounting

The new block uses exactly the same register union and exactly the existing
frame 524. It introduces no helper, COPY, source-access operation or frame.
Each register's first touch in this block climbs from its unchanged incoming
frame to 524; subsequent touches stay at 524, and each register leaves at 524.
Changing the order therefore preserves all frame-transition charges. The
source/retained-total COPY interface precedes phase B and is unaffected.

Every destination in the block is a source register (`r < v=111`), so every
forward singleton addition also appears once in cleanup `C`, at the full frame,
in literal reverse order. The complete changed addition invoice is therefore:

```text
old B block:       17 + 24 = 41
old cleanup block: 17 + 24 = 41
old total:                  82
new B block:       12 + 15 = 27
new cleanup block: 12 + 15 = 27
new total:                  54
saved:                      28 common-frame singleton additions
```

Full-frame cleanup uses the same register union, so its frame-transition charge
is preserved as well. All other sections, scatter, COPY ranks and recursive
children are retained. This predicts unchanged paid recursive profile, with
the whole-word check and numeric invoice recorded separately in the package.

Over F2, elementary addition is self-inverse, so literal reverse cleanup remains
the inverse of the new forward block. Over nonnegative integers, its positive
reverse matrix is **not equal** to the old positive reverse matrix. The emitted
candidate's reverse matrix is entrywise at most the old one, independently for
each factor and for the whole block. These explicit finite inequalities are
stored and checked; they are not assumed for arbitrary minimum schedules.

For nonnegative incoming norm vectors, forward integer equality preserves the
block endpoint. Every intermediate positive addition is bounded by its own
final endpoint. Reverse entrywise domination bounds the new reverse endpoint
by the old one, and subsequent positive operations preserve that order.
Consequently this replacement cannot increase the whole-word cancellation-free
norm maximum. For the isolated block with unit input norms followed by its
positive literal reverse, the recorded maximum falls from 1101 to 165. This
local value is not substituted for the whole-word norm or precision check.

## Reproduction and inherited obligations

From the repository root:

```sh
python3 research/r439-frame524-seed13/search.py --check
```

Expected output reports `factor_minima: [12,15]`, `original_additions: 41`,
`candidate_additions: 27`, `integer_forward_identity: true` and
`positive_reverse_entrywise_dominated: true`. The checks use explicit exceptions,
so `python3 -O` retains the acceptance and source-pin checks.

The inherited selected construction's mutable-source, hosting, all-size
compiler, compressed-window, precision and tape assumptions remain obligations.
This result changes no selected frontier and claims no new kappa. The separate
whole-word endpoint, paid-profile, precision and official native checks are
required before accepting the word-level contribution.
