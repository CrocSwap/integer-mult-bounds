# Exact rank-capped tariffs for Coxeter targets with a common generator order

This scoped proof gives the exact formal price of a heterogeneous diagonal
target whose entries are subsequences of one order of distinct simple
generators. It applies to every field and every finite-rank Coxeter system,
including infinite groups. The number of restored dirty roles is arbitrary
and finite.

## Model and result

Let `(W,S)` be a Coxeter system and work in `M_r(K[W])` over a field `K`.
A paid factor for `s in S` is `I + ([s]-[e])A`, where `A` is a scalar matrix
of rank between 1 and `b`. The model allows non-idempotent and singular
couplings. Scalar invertible maps interleaved with the paid factors are free.
All initial roles are arbitrary. The required endpoint is the full formal
diagonal with target `[w_j]` on role `j` and `[e]` on each spectator.

Fix an ordered list of distinct simple generators. Assume each `w_j` is the
product of a subsequence of this list, in the given order. Let `d_s` count
the roles whose subsequence contains `s`. Each call of rank `k` costs
`f(k)`, where `f(0)=0` and the increments of `f` are nonnegative and
nonincreasing. The exact price is

```text
sum over s in S of (floor(d_s / b) f(b) + f(d_s mod b)).
```

### Lower bound

For a given generator `s`, put `H = <S minus {s}>`. The generator `s`
lies outside `H`. In the real geometric representation, every other
simple reflection changes only its own simple-root coordinate and hence
preserves the `s` coordinate. The reflection `s` sends its simple root
to its negative. This group fact precedes the choice of coefficient
field `K`. The real geometric representation is the one used in
[David Arias's Coxeter tariff](../coxeter-root-tariff/PROOF.md).

Use the left action of `W` on the basis of left cosets `gH` over `K`.
Tensor the action with the role space `K^r`. Separate the copy of `K^r`
over `H` from all other cosets, and let `q(X)` be the rank of the block
from that copy to the rest. With the base coset indexed by 0 and
the rest by 1, the crossing block of `XY` is
`X_10 Y_00 + X_11 Y_10`. Subadditivity of rank gives
`q(XY) <= q(X) + q(Y)`. This holds on the algebraic direct sum for
infinite `W`, since the block's domain is finite-dimensional.

A paid factor labelled `t != s` has zero crossing rank because `t`
fixes the coset `H`. Scalar maps also have zero crossing rank. A paid
`s` factor sends its crossing block entirely to `sH` with matrix `A`.
Its crossing rank is exactly `rank(A)`.

A target that omits `s` fixes `H`. A target that uses it has the form
`a s c` with `a,c in H`. It moves `H`, since `a s c in H` would imply
`s in H`. The crossing images of the `d_s` target columns belong to
distinct role coordinates, so the target crossing rank is `d_s`. Hence
the sum of the ranks of the paid `s` factors is at least `d_s`.

Apply concave packing separately to each generator. Given a fixed rank
mass, transferring a unit from a smaller nonempty part to a larger part
below the cap does not increase cost, by the
nonincreasing increments. This leaves full cap-sized parts and at most
one remainder. The resulting packed price is nondecreasing in the mass,
so mass at least `d_s` costs at least the displayed term. Sum over the
generators. [Benny Zhao's concave packing bound](../coxeter-capped-concave-tariff/PROOF.md).

### Attainment

For each generator in the common order, partition the roles requesting
it into blocks of size `b` and one remaining block if needed. On each
block `B` use the coordinate projector `E_B` and the paid factor
`I + ([s]-[e])E_B`. In written product order, the entry on role `j`
is exactly the subsequence product `[w_j]`. All other entries have their
required diagonal or zero value. This is equality in the full group
algebra. The rightmost factor acts first. The construction uses just
the requested ranks, even when `b > r`.

### Mixed A3 example

Take adjacent swaps `s,t,u` in order and five targets
`(s, st, tu, su, stu)`. With cap two, their respective generator demands
are `(4,3,3)`. One attaining written word is

```text
s{1,2} s{4,5} t{2,3} t{5} u{3,4} u{5}
```

At `f(k)=k/(k+1)` this costs **11/3**. The pooled root-orbit bound is
`10/3`, because the ten inversions form one orbit and fit into five
parts of size two. Separate target-by-target calls cost `5`. The
separate cuts explain why the pooled lower bound is strict, and the
schedule saves `4/3` against separate calls.

## Evidence and reproduction

From the repository root with CPython 3.12.15, standard library only:

```sh
python3.12 -I -W error -B research/coxeter-common-order-tariff/verify.py
python3.12 -I -O -W error -B research/coxeter-common-order-tariff/verify.py
python3.12 -B scripts/research_package.py --package research/coxeter-common-order-tariff
python3.12 -B scripts/check_research_commit.py --package research/coxeter-common-order-tariff --check-source-history
```

Both direct commands print `PASS_COXETER_COMMON_ORDER_TARIFF`. They check
10,512 full formal A3 endpoints with a restored spectator, over all three
rank caps, all six generator orders and all ordered lists of up to three
non-spectator targets of that form. They also check 873 paid-factor cuts
using every two-by-two coupling over F2 and F3, including singular
matrices. The separate five-target example checks all six batch omissions
and reversal of the word. The written argument gives the universal result.

## Scope and credit

This contribution was produced by Nick Petalas. Benny Zhao's #6817 posed
the heterogeneous-target question and supplied the rank-capped model and
packing bound. ToikY's #6821 supplies the repeated A2 precedent with
selective cuts. Credit Adam Gall #1941 and Ross Richardson #1966/#1989 for
the separate-letter cut method, and David Arias #2738 and the retained
lineage for Coxeter tariffs. The new step is the coset cut for each simple
generator with simultaneous attaining batches for the common-order
heterogeneous family. [#6817](https://github.com/CrocSwap/integer-mult-bounds/pull/6817),
[#6821](https://github.com/CrocSwap/integer-mult-bounds/pull/6821),
[#2738](https://github.com/CrocSwap/integer-mult-bounds/pull/2738),
[advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19717633).

The theorem concerns the formal group-algebra tariff. Native
realization, physical scalar-map and movement costs, precision, compiler
closure, supplier admission and a new κ remain open. Independent human
and formal proof-kernel review are unclaimed.

## Open next questions

- For target orders that disagree on a noncommuting pair, what extra
  price does chronology require? Start with `(st,ts)` and cap two.
  The two individual generator cuts bound rank mass but do not encode
  relative order.
- Can one physical rank-two primitive realize a formal batch at a net
  saving? Start by specifying the boundary layout and pricing one
  shared call including all routing and restoration. A supplier needs
  that conversion before the formal price can enter its invoice.
