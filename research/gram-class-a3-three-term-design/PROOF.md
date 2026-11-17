# Proof note: an exact three-term Gram-class design on A_3

Model, quoted from DreamingOfClouds' `research/p104-duality-ceiling-flag-note`
(Theorem O, section 2, and the A_2 toy, section 4). Let `V = {x in Q^(n+1) :
sum_i x_i = 0}` and `Pi = I - J/(n+1)` the orthogonal projector onto V. The A_n
lines are the pairs `(i,j)`, `i < j`; the line `(i,j)` is orthogonal to `x` iff
`x_i = x_j`. The even-inner-product mask of the line set is `N = I`, so for
`u, w in V` the price of a term is

```text
rho(u,w) = rank_F2 N[S_u, T_w] = |Sep(u) cap Sep(w)|,
Sep(x) = {(i,j) : x_i != x_j}.
```

A Gram-class design is a finite family `(u_k, w_k)` in `V x V` with
`sum_k u_k w_k^T = Pi`; its cost is `sum_k rho(u_k, w_k)`. This package fixes
n = 3: four coordinates, six lines, `Pi_4 = I - J/4`. Labels are [P] written
proof, [C] exact computation in `verify.py`.

## 1. The written design [P+C]

Set

```text
u_1 = (0, 0, 1, -1)      w_1 = (-1/2,  1/2,  1/2, -1/2)
u_2 = (0, 1, -1, 0)      w_2 = ( 1/2,  1/2, -1/2, -1/2)
u_3 = (1, -1, 1, -1)     w_3 = ( 3/4, -1/4, -1/4, -1/4)
```

Every coordinate vector has coordinate sum zero, so `u_k, w_k in V`, and
`sum_k u_k w_k^T = Pi_4` holds identically over the rationals [C]. The three
prices are 3, 3 and 2 [C]:

| k | Sep(u_k) | Sep(w_k) | intersection | price |
|---|---|---|---|---|
| 1 | 5 pairs | 4 pairs | `(0,2),(0,3),(1,2),(1,3)` | 3 |
| 2 | 5 pairs | 4 pairs | `(0,2),(0,3),(1,2),(1,3)` | 3 |
| 3 | 4 pairs | 3 pairs | `(0,1),(0,3)` | 2 |

Total cost 8. (The check recomputes the separations from the vectors; the table
is descriptive.)

## 2. The natural dual-basis design costs 9 [P+C]

Let `u_k = e_k - e_4` for `k = 1,2,3` and let `w_k` be the dual basis of V
with respect to the dot product, `w_k = e_k - (1/4) 1`. Then `u_k . w_l =
delta_kl` and `sum_k u_k w_k^T` is the orthogonal projector of V = col(U), so
the design is exact [C].

Price: `u_k` has entry 1 at k, -1 at 4 and 0 elsewhere, so `Sep(u_k)` is the
set of pairs meeting `{k,4}`, of size `2n-1 = 5`. `w_k` has entry `3/4` at k and
`-1/4` at the other three coordinates, so `Sep(w_k)` is the set of pairs meeting
`k`, of size `n = 3`. The pairs meeting both `k` and `{4}` are exactly the pairs
meeting `k`, so `rho(u_k,w_k) = 3` and the total cost is `3 * 3 = 9`. The same
count gives `n^2` for general n. Hence the written design of section 1 improves
the dual-basis design inside the same model by one unit.

## 3. Every design has at least three terms [P]

`Pi_4` has rank 3, and each term `u_k w_k^T` has rank at most 1. So a Gram-class
design needs at least three terms. No lower bound on the cost beyond
`cost >= number of terms >= 3` is claimed.

## 4. The declared finite family [C]

Take the primitive integer vectors in `[-3,3]^4` with coordinate sum zero and
positive first nonzero entry, and keep the lexicographically first vector of
each equality pattern. There are 14 patterns; the list is fixed by the check
(`candidate_vectors`). Enumerate all ordered triples, solve `Pi_4 = U W^T` for
`W` exactly (the solution is unique when `U` has full rank), and price the
result. Of the `14^3 = 2744` triples, 1812 have full-rank `U` and an exact
solution; every one of the 1812 has cost at least 8, and the written design of
section 1 is one of the minimisers [C].

Because the family keeps one representative per equality pattern, this is not a
search over all rational carriers. A design with different carriers in the same
pattern can have a different price, so the enumeration does not prove that 8 is
the Gram-class minimum.

## 5. Rejection controls [C]

The check requires that (i) adding 1/2 to one entry of `w_1` destroys the
projector identity, (ii) replacing `u_1` by the zero vector destroys it, and
(iii) the three `u_k` of the written design are linearly independent. It also
requires the dual-basis design to be exact at cost 9 and the A_2 control below
to be exact at cost 4, so a broken cost or identity check fails loudly.

## 6. A_2 control [C]

`u_1 = (0,1,-1)`, `w_1 = (1,0,-1)`, `u_2 = (1,-2,1)`, `w_2 = (2/3,-1/3,-1/3)`
give `sum_k u_k w_k^T = Pi_3` with prices 3 and 1, total 4. This reproduces the
A_2 Gram value reported by the predecessor's section 4; it is a control for this
package's price code and is not claimed as new.

## Scope

Nothing here is a lower bound over all Gram-class designs, a statement about
A_n for n >= 4, a kappa change, a physical word, or a supplier admission. The
exact A_3 minimum remains open. The model, definitions and A_2 value are the
predecessor's; this package adds the explicit A_3 design, the dual-basis price
comparison and the bounded enumeration.
