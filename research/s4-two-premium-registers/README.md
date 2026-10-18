# S4 two-premium calls do not share work across two dirty registers

For adjacent labels in `S4` priced `(2,1,2)`, all **576 ordered diagonal
pairs** have exact minimum `d(a)+d(b)` in the formal model below. Here
`d` is the one-register weighted Cayley distance. The two-register search
closes the cases not decided by the inherited cut bounds. This is a finite
certificate, not an arbitrary-register theorem or a new kappa.

The selected result and every frozen predecessor remain unchanged.

## Model and changed hypothesis

Use the full formal algebra `F2[S4]`. The paid labels are
`s1=(12), s2=(23), s3=(34)` with respective costs `2,1,2`. A paid factor is

`D_N(s_i) = I_2 + ([s_i]+1)N`,

where `N` is any binary rank-one idempotent. There are six such `N`, giving
18 paid factors. Both registers start arbitrary and must have complete
endpoint `diag([a],[b])`, including zero off-diagonal coefficients. An
identity target is an arbitrary dirty spectator, not a clean ancilla.
Arbitrary scalar `GL_2(F2)` mixing is free. No extra registers, resets,
COPYs or free address maps are allowed. Every restoration call is charged.

As in Ross Richardson's [PR1989 proof](../symmetric-adjacent-cut-bound/PROOF.md),
scalar maps can be moved to one end by conjugating `N`. Augmentation forces
that final scalar map to be the identity. Thus the normalized paid alphabet
covers all interleaved free scalar circuits in this model.

The changed premise is the price, not a new alphabet. PR1989 proves the
unit-price obstruction and explicitly leaves weighted prices open.
Discussion2563 and its PR2577 address the distinct one-premium family,
starting at `(1,2,1)`. PR2544 concerns the two-generator `S3` coordinate-SWAP tariff. This package
uses two premium outer labels in `S4`; neither predecessor settles it.

## Cut bound and the two exceptional permutations

Let `c_p(w)` count `i<=p` with `w(i)>p`. In the natural permutation action,
the cut from the first `p` coordinates to their complement has rank
`c_p(w)`. Its charge on `s_i` is `1` for `i=p` and `0` otherwise.
Tensoring with a rank-one scalar projector preserves that charge, and
free scalar maps have charge zero. The subadditivity proof is exactly the
block-rank argument credited to PR1941/PR1966/PR1989.

Combine the natural cuts at `p=1,3` with PR1989's ordered-pair cut. Every
circuit, with any finite dirty role count, has weighted cost at least

`sum_j L(w_j)`, where `L(w)=inv(w)+c_1(w)+c_3(w)`.

The charge of each generator is precisely `(2,1,2)`. For `S4`,
`c_1(w)=1` iff `w(1)!=1`, and `c_3(w)=1` iff `w(4)!=4`.
The exact 24-vertex one-role calculation gives `d(w)=L(w)` except for:

| One-line permutation | `L(w)` | `d(w)` | Attaining chronological labels |
| --- | ---: | ---: | --- |
| `4231`, the transposition `(14)` | 7 | 8 | `1,2,3,2,1` |
| `4321`, the reversal | 8 | 9 | `2,1,2,3,2,1` |

`EXPECTED.json` contains all 24 distances and attaining words. Every graph
edge satisfies the shortest-path dual inequality, and every word has its
stated bill and full formal endpoint. The combined cut cannot certify the
exact weighted tariff for these two permutations: `d=L+1`. This is a gap in
that particular lower bound, not evidence of a sharing construction.

For the other 22 permutations, the cut plus direct words already proves
additivity for any target tuple and any finite number of restored dirty
roles. That consequence does not require a search.

## Complete two-role exclusion

There are 300 unordered pairs including repetitions. The cut settles 253.
The remaining 47 unordered pairs, or 92 ordered pairs, contain at least one
of the exceptional permutations. Role exchange preserves the alphabet,
prices and boundary, so checking the unordered pairs is exhaustive.

Both engines construct the exact weighted ball of radius nine:

| Minimum cost | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| States | 1 | 6 | 19 | 134 | 542 | 2,058 | 10,568 | 40,562 | 166,385 | 751,094 |

The ball has **971,369 distinct formal states**. For each of the 47 pairs,
the complete meet finds minimum exactly `d(a)+d(b)`, including 16 for two
`4231` targets and 18 for two reversals. The receipt includes every query,
its cut/direct bills and its number of ball intersections. Each query row
is `[a,b,direct,cut,meet,hits]`; `a,b` index `permutation_order`.

Why radius nine suffices: each factor costs at most two. Any word of cost
at most 17 splits into two subwords of cost at most nine. Choose the first
prefix of cost at least eight; it costs eight or nine. If the whole word
costs less than eight, use the identity as the other half. Since every
factor is an involution, every such word has form `A B^-1`, with both
states in the ball. The producer enumerates all `B` and tests `A=T B` by
full formal equality. Every direct pair bill is at most 18, so excluding
all cheaper words through 17 is sufficient.

The weighted layers are also exhaustive. A state of minimum cost `k` has a
last factor of cost one or two and a shortest predecessor at cost `k-1`
or `k-2`. The engines apply every legal factor from both relevant layers,
discard only exact states already at smaller cost, and record all remaining
states at cost `k`. No heuristic or quotient filter prunes the ball.

## Evidence and replay

```sh
python3.12 -I -B scripts/research_package.py --package research/s4-two-premium-registers
```

The registered replay runs all three checks, about one minute on the recorded
Linux environment with CPython 3.12.15 and GCC 14.2.0:

```sh
python3.12 -I -B research/s4-two-premium-registers/verify.py
python3.12 -I -B research/s4-two-premium-registers/independent.py
python3.12 -I -B research/s4-two-premium-registers/test_verify.py
```

The producer compiles `engine.cpp` in a temporary directory with strict
warnings. A C++17 compiler is required. `verify.py --write` is the only
receipt-regeneration command. Default replay does not change package files.

The C++ producer uses four 24-bit coefficient sets, left multiplication,
and full-key hash-table equality. The separately written Python engine
uses packed 96-bit integers, right multiplication, its own permutation
multiplication tables and Dijkstra distances. It imports no producer or
predecessor implementation. Both independently regenerate the full ball
and all 47 queries; **their complete census receipts agree**, including
all intersection counts. These are separate implementations from the same
session, not independent human review or proof-assistant verification.

Other checks include all 576 formal endpoints and their inverses, all
3,456 single-call omissions, 18 paid involutions, 54 explicit paid-factor
cut ranks, 72 target cut ranks, 18 free-scalar cut ranks, exact equality of all
702 radius-four states, every transition from that small ball against a
literal matrix oracle, and undeduplicated word enumeration through cost
four. Seven behavioral test groups reject corrupted scientific receipts,
wrong order, dirty leaks, nonfaithful-representation endpoint aliases,
invalid projectors, malformed radii and exhausted state capacity. Forcing
hashes to one bit leaves the small ball unchanged. Optimized read-only,
Git-free replay succeeds; changing a pinned source fails before search.

Only the credited proof is a live external dependency. Its exact SHA256
and Git blob are in `SOURCES.json`; the catalogue and selected result are
historical provenance. No predecessor search code is imported.

### Implementation limits

The search radius is capped at nine, the state capacity at two million,
and subprocesses have explicit timeouts. Capacity exhaustion fails without
an exclusion receipt. The language/runtime allocation deviation is confined
to these finite checkers: Python dictionaries and C++ hash nodes allocate
during enumeration. The enforced state cap bounds live search storage;
tables have 24 group elements, 18 calls and ten layers. There is no recursion
or service loop. C++ tables are initialized once and read-only during search.
The standard hash table and Python runtime allocate internally; no hard
real-time memory guarantee is claimed. GCC strict warnings, AddressSanitizer
and UndefinedBehaviorSanitizer pass on the full census. Python development-mode
compilation with warnings treated as errors passes; a separate Python linter
was unavailable in the recorded environment. A larger search requires an explicit
capacity and memory review, not removal of the guard.

## Open next questions

- Does an exceptional target admit weighted sharing with a third restored
  dirty role? The smallest first test is two `4231` targets plus an identity
  spectator, against bill 16. A favorable word must be checked formally and
  completely charged. The larger 84-factor alphabet and exact weighted-ball
  memory are the blockers; the present two-role census does not settle it.
- Does additivity persist for the symmetric price cone `(beta,alpha,beta)`
  with `0<alpha<beta`, beyond the tested ratio two? First enumerate Pareto
  costs by total calls and outer-label calls for the two exceptional targets.
  One fixed weighted ball is not a complete parameter-cone certificate.

These questions are recorded in `TASK.json`. No physical native conversion,
compiler, hosting, precision/tape, recursive moment, selected-supplier cold
replay or multiplication theorem is supplied. The bit supplier is not the
currently binding side, and this formal tariff alone changes no kappa.

## Credit

Ross Richardson's PR1989 supplies the operation model, ordered-pair cut,
free-scalar normalization, direct-construction argument and weighted-price
handoff. Adam Gall's PR1941 and Ross Richardson's PR1966 supply the underlying
cut method. Josie Elliston's PR1974 is a related exact-register-census
precedent, not an input to this search. Discussion2563/PR2577 and PR2544
are complementary changed-price investigations, not claimed as new here.
The retained bit-supplier lineage and attribution remain in those sources.
New work is Apache-2.0.
