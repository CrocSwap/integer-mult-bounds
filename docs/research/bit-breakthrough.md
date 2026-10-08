# Affine center changes cannot supply the next orders of magnitude

This is a scoped obstruction found while searching beyond the aligned-bit
construction. It establishes no new multiplication exponent. The current
conditional witness remains `kappa = 1624/10^12`.

The experiment is
[scripts/experiments/bit_breakthrough_affine_centers.py](../../scripts/experiments/bit_breakthrough_affine_centers.py).
It regenerates [the exact audit certificate](../../certificates/affine-center-targets.json),
checking support-span identities and rational upper bounds without changing
any multiplication witness or construction. Independent tests in
[tests/test_affine_center_targets.py](../../tests/test_affine_center_targets.py)
use rational elimination on explicit triple indicators and direct bitset
elimination on the binary central matrix.

## The class being screened

Keep the complete triple family on `h` points and the rational form
`H = I - J/9`. Keep the scalar central matrix

    B_ST = |S intersection T| mod 2 = (Q Q^t)_ST,

where `Q` is the triple-by-point incidence matrix. The side correction is
still `A1`, so `B + A1 = I` over `F2`.

Permit any number of center rectangles, including redundant factorizations,
but require each center's gather and scatter predicates to be affine in point
incidence:

    f(T) = c + sum_{i in T} a_i mod 2.

This includes arbitrary changes of basis among the current point centers,
complement stars, and parity of pairs or larger point subsets. Each center
has one gather passage and one scatter passage. At its gather, its subspace
frame contains the span of its source indicators; at its scatter, its frame
lies in the orthogonal complement of its target-indicator span. These are
the source-span and target-complement rules used in the existing proof.

Also retain the three tensor stages and auxiliary-bank factorization of the
invocation, `J L V = I`. This last equation includes both side and center
outputs, as `J' L' V = I` in the aligned construction.

This screen does not cover nonlinear predicates on triples, changing the
scalar central matrix together with the side correction, interleaved
partial gathers and scatters, more general data or gate frames, or different
tensor-stage architecture.

## Every affine predicate has a large rational source span

Because every triple has odd size, adding a constant to the predicate is the
same as replacing the point mask by its complement. It suffices to study the
triples meeting a mask `A` in an odd number of points.

For `h >= 6`, their rational span has these dimensions. Write `a=|A|` and
let `1_A` be the indicator of `A`.

| Mask size | Span dimension | A normal when the span is a hyperplane |
| --- | --- | --- |
| `a=0` | `0` | Predicate is zero |
| `a=1` or `a=2` | `h-1` | `3 1_A - 1` |
| `3 <= a <= h-3` | `h` | No normal |
| `a=h-2` | `h-1` | `e_i-e_j`, where the omitted pair is `{i,j}` |
| `a=h-1` | `h-1` | `e_i`, where `i` is omitted |
| `a=h` | `h` | All triples |

For the middle case, differences of allowed triples span all coordinate
differences within `A` and within its complement. These provide `h-2`
independent directions. Allowed intersection sizes one and three give
independent vectors of block sums `(1,2)` and `(3,0)`, supplying the remaining
two dimensions. For `a=1,2`, only the first block-sum pattern occurs, leaving
exactly the displayed one relation. Complement masks reduce the last cases
to triples containing either zero or two points of the omitted pair, or
avoiding the omitted singleton. Those have exactly the displayed relation.
The all-triples family spans the whole space by coordinate differences and
one triple of nonzero coordinate sum.

Thus **every nonzero affine predicate spans at least `h-1` dimensions**.
The script exhausts every mask for `h=6,7,8,9` and every mask-size orbit at
`h=10,11,24,38,48,50`. A full modular rank is a rational lower bound; the exact
integer normals, or ambient dimension, give the matching rational upper
bound. The general statement follows from the proof above, not from
extrapolating the finite checks.

## Center loss is at least `h(h-2)`

A useful center has nonzero gather and scatter predicates. Its source span
has dimension at least `h-1`; the orthogonal complement of its target span
has dimension at most one. The center must therefore lose at least `h-2`
dimensions along its gather-to-scatter passage. Allowing a nonnested path
cannot evade the bound: rank subadditivity bounds the entire passage through
its endpoint rank difference. Additional decreases only increase the charge.

There must be at least `h` centers. Indeed, `Q` has full column rank over
`F2`: differences of triples span the even-weight subspace, and a triple has
odd weight. Hence `rank_F2(Q Q^t)=h`. Every center rectangle has scalar rank
at most one, so any factorization of `B` has at least `h` nonzero terms.
Consequently the loss per invocation obeys

    center_loss >= h(h-2).

The aligned loss is `h(h-1)`. This theorem leaves room for one dimension per
center; it does not claim the current loss is exactly optimal. In particular,
complement-pair predicates have normals `e_i-e_j`, and some such hyperplanes
can have orthogonal normals. Assuming all parity masks span the full space,
or assuming every center necessarily costs `h-1`, would be incorrect.

## Even an optimal side circuit in this class stays within a factor 15

The auxiliary-bank factorization supplies another useful lower bound:
`rank(J L V)=v`, where `v=C(h,3)`, so the number of auxiliary roles satisfies
`R >= v`. This is independent of the current binary-addition compiler.

Give the candidate both optimistic floors, `R=v` and loss `h(h-2)`, whether
or not they can be simultaneously achieved. Under the retained network
counts,

    eta <= [v - 6h(h-2)] / [4 h^3 v],
    a_b <= -log(1-eta) / log(h^3),
    kappa < a_b/2.

The optimistic deficit first becomes positive at `h=38`. Exact logarithm
enclosures isolate `h=48` as the maximum among `11 <= h < 200`. For all
`h >= 200`, the uniform bound

    a_b < 1 / (4*200^3 - 1)

is below that maximum, because `eta < 1/(4h^3)`,
`-log(1-eta) < eta/(1-eta)`, and `log(h^3)>1`.
The resulting convenient exact ceiling is

    kappa < 22778/10^12 = 2.2778e-8,

which is less than `14.027` times the current conditional witness. This is
an upper bound for the specified construction class, not an achievable
witness and not a general bound on integer multiplication.

Thus merely changing the basis of point centers and making the current side
circuit arbitrarily efficient cannot provide multiple orders of magnitude.
A larger jump needs to escape at least one of the explicit restrictions:
nonlinear center supports or a changed scalar correction, smaller rational
label spaces, a different stage architecture, or a different transfer.

Reproduce with:

```sh
python3 scripts/experiments/bit_breakthrough_affine_centers.py
python3 -m unittest discover -s tests -p test_affine_center_targets.py -v
```
