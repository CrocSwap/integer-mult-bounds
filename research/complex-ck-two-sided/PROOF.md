# Finite two-sided compensation identity and price

Let `y` be the 112 target registers and `h` the 254 helper registers read by
PR626 CK compensation. Its map is `(y,h) -> (y+C h,h)`, with entries of `C`
in `(1/4) Z`. All relevant registers start in frame zero. The source helpers
also end at the full frame: none requires an entrance wrapper before access.
These properties are checked from the historical SPEC-bound canonical word.
The preceding precondition is retained, so `y` and `h` are arbitrary inputs.

## Circuit

For a signed target forest, define `(T y)_t = y_t - s_t y_parent(t)` on nonroots
and `(T y)_t=y_t` on roots. Prepare its shears deepest-first, so each parent is
read in its original basis. This produces `T y`; it also gives the literal
row formula `(T C)_t=C_t-s_t C_parent(t)`. The inverse reverses the chronological
preparation list and negates its coefficients.

Next prepare disjoint helper shears `h_a += s h_b`, with `s` in `{-1,+1}`;
let their product be `H`. Since every helper occurs in at most one pair, the
updates commute and `H^-1` negates their coefficients. Right multiplication
of `D=T C` by `H^-1` changes exactly column `b` to `D_b-s D_a` in each pair.
Use the columns of `D`, not the original `C`, to compute this residual.

The emitted chronological circuit is

```text
y <- T y
h <- H h
y <- y + (T C H^-1) h
h <- H^-1 h
y <- T^-1 y
```

Hence its output is `T^-1(T y + T C H^-1 H h)=y+C h`, with helpers restored.
Every step is an explicit frame-zero scalar addition. No extra register,
recursive child, source copy or unpriced boundary work is used. The target
and helper bank preparation commute across banks, but target internal order
must remain as specified.

For a logical addition `E=I+q e_t e_s^T`, `E^-T=I-q e_s e_t^T`. Mapping each
logical gate to this dual in the **same chronological order** dualizes the
whole map, because `(AB)^-T=A^-T B^-T`. Consequently the candidate backward
panel equals the inherited `(y,h)->(y,h-C^T y)`. Helpers at that panel boundary
need not equal their inputs; the rest of the complete backward program restores
them. Dualize the logical additions before lowering. The destructive private
clears themselves are not asserted to be invertible.

## Exact complete price

For reduced nonzero `q=a/2^d`, the inherited binary-Horner price in one component
is `p(q)=3+floor(log2|a|)+popcount(|a|)+d`. Set `p(0)=0` because zero entries emit
no gate. The initial work clear, every source accumulation and doubling, each
halving, signed target accumulation, and final clear are included. A unit shear
costs four component primitives, so preparation plus restoration costs eight.
Applying the same scalar arithmetic to real and imaginary parts doubles prices.

For a fixed signed target forest with `e_T` edges, and fixed disjoint helper
pairs with `e_H` edges, the compensation price is exactly

```text
8 e_T + 8 e_H + sum_(i,j) p((T C H^-1)_(i,j)).
```

The target-only forest is obtained by a minimum spanning tree on the 112 target
rows and a superroot: root-edge price `sum_j p(C_ij)` and signed-edge price
`8+sum_j p(C_ij-s C_kj)`. Edge prices are symmetric since `p(q)=p(-q)`. Removing
the superroot gives the forest, and the chronological schedule above realizes
its cost. A separately implemented Prim algorithm corroborates the Kruskal
price. This standard reduction proves a floor only within the target-only
signed-unit forest class; it says nothing about the joint two-sided optimum.

For one helper choice `(a,b,s)` on `D=T C`, the complete saving is
`sum_i[p(D_ib)-p(D_ib-s D_ia)]-8`. Scores add for register-disjoint pairs since
they change different columns and do not modify each other's source columns.
The greedy selection is a construction, not a maximum-weight matching proof.

| Compensation stage | Component primitives |
|---|---:|
| Original `C` | 49,624 |
| Target forest, including 212 basis gates | 16,364 |
| Two-sided, including 212 target and 224 helper basis gates | 11,965 |

The residual has 2,105 nonzero additions, yielding 2,541 total additions.
The helper stage saves 4,399 component primitives beyond the target-only
forest. Therefore both complete orientations save
`2(49,624-11,965)=75,318` real primitives, including `2(4,399)=8,798` beyond
that target-only price. No pricing improvement outside compensation is used.

## Prefixes, children and verification limits

Starting from norm one for every independent input, propagate a positive
envelope through every literal primitive: addition sums norms, doubling/halving
scale them, copying copies the norm, and clearing sets it to zero. This gives
an upper bound on every scalar row norm, including work values before division.
The candidate maxima are `1200150150114` forward and
`626977768061479717259/32` backward (41 and 65 bits). Both are strictly below
`2^192`; the higher bounds are reported rather than assumed unchanged.
The largest reduced dyadic denominator exponent across every intermediate
symbolic row remains 3 forward and 8 backward, equal to the original programs.
Both arithmetic engines check this separately from the magnitude envelope.

The native paid histogram remains
`{1:2596,2:552,3:304,4:160,5:70,6:8,8:8}`: 3,698 children.
All non-scalar events retain their literal order, including center operations,
frame climbs, residual wrappers and adapters. No changed asymptotic recurrence
or κ follows from this finite scalar saving. Global hosting/invoice admission
and all-size/analytic obligations remain outside this contribution.

Two new arithmetic implementations check the full original/candidate scalar
projections in both directions on 725 independent input columns. The unchanged
native emitter/auditor separately checks the finite common-frame and wrapper
contract on all 716 logical columns, with its 25 original rejection controls.
Ten new controls include omitted target preparation: it passes a helper-only
projection and fails arbitrary-target checking, illustrating why all-column
replay is required. These finite checks do not formalize the full theorem.
