# Exact optimum for the selected idle-axis reassignment domain

This is a finite, source-bound theorem about a STRUCTURAL RELAXATION of the
selected PR1094 word and owner map. Its attaining assignment fails the physical
operator test below, so it supplies an upper ceiling and no improved bound. It is not an optimum over other words, owner maps, frame rebases,
replica counts or multiplication algorithms. Majorization, conflict graphs
and integral flows are classical tools; no priority for those methods is claimed.

## 1. Domain and source extraction

The selected replay contains 7,526 nonempty residual frames. Hold all local
words, 144 calls, 69,120 whole-helper roles, source-event times, owner offsets,
physical families and hosted residuals fixed. The eligible rows have rank 48,
hosted count zero, pending offset zero, and no entry in the owner map. There
are 4,866 such rows in 1,792 `(replica, port)` groups, with group sizes
`{1:45, 2:703, 3:761, 4:283}`. These are exactly PR1276's selected-word inputs.

For a group with `k` children, label **every original axis occurrence** by its
original child and position. Equal vectors in different children remain
distinct occurrences. Assign each occurrence to one of the existing `k`
children, preserving the group multiset. A destination has positive rank at
most 51, equal to its number of axes, and its axes must be orthonormal over
F2. The cap satisfies `73^2 = 5329 > 2*51^2 = 5202`.

An occurrence may stay at its original child. To move from child `i` to `j`,
its vector must have zero dot product with every recipe stage entry/exit X/Y
translation, terminal Y translation, and the terminal translations of both
`i` and `j`. This is PR1324's final-list reassignment rule, applied to the
**selected** word. PR1276 allowed a smaller disjoint-star class; PR1324 uses
different pending T37 words. Our attained witness additionally has zero dot product with
**every** idle-child terminal translation, not only its two endpoints.
These dot-product conditions define the inherited combinatorial rule; they
do not imply that moving factors between different physical streams is valid.

No new vector, linear combination, basis rebase, owner move, child deletion,
helper splitting or new schedule is admitted by this domain. In particular,
an assignment that violates the commuting rule is outside the optimality claim,
even if some more general algebraic cancellation might make it valid.

## 2. Complete reduction to nine patterns

Make a vertex for each occurrence and give it its allowed destination list.
Two vertices are adjacent iff their vectors have dot product one. The source
has odd axes, so a proper list colouring is exactly an orthonormal assignment:
no two conflicting axes may enter the same child. Orthogonality with diagonal
one also proves linear independence, since the Gram matrix is the identity.

Propagate singleton lists by deleting their colour from adjacent lists. This
preserves all solutions: any legal colouring must use the forced colour.
The original assignment proves that this process cannot encounter an empty
list on these inputs. Every pairwise dot product and every deletion is
recomputed from the pinned vectors; there is no assumed graph template.

The verifier then checks the following properties, rather than assuming them:

* Every child has the same number `f` of forced occurrences.
* Every remaining connected component is a clique of equal axis vectors.
* Every remaining vertex permits every one of the `k` colours.
* The component inventory is one of the nine rows below.

There are 683 distinct `(port, children, original axes)` contexts. Aliasing is
used only for identical inputs, and all 1,792 groups are accounted for. Write
`n_q` for the number of mobile cliques of size `q` in a group.

| k | f | n1 | n2 | n3 | n4 | Groups | Attaining descending ranks |
|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | 48 | 0 | 0 | 0 | 0 | 45 | 48 |
| 2 | 18 | 30 | 15 | 0 | 0 | 240 | 51,45 |
| 2 | 18 | 0 | 30 | 0 | 0 | 164 | 48,48 |
| 2 | 42 | 6 | 3 | 0 | 0 | 258 | 51,45 |
| 2 | 42 | 0 | 6 | 0 | 0 | 41 | 48,48 |
| 3 | 18 | 15 | 15 | 15 | 0 | 532 | 51,51,42 |
| 3 | 42 | 3 | 3 | 3 | 0 | 229 | 51,48,45 |
| 4 | 18 | 0 | 30 | 0 | 15 | 264 | 51,51,51,39 |
| 4 | 42 | 0 | 6 | 0 | 3 | 19 | 51,51,45,45 |

## 3. Upper bounds on every sorted prefix

For **any** set of `s` children, forced occurrences contribute `s*f`. A clique
of size `q` contributes at most `min(q,s)`, because its colours must be distinct.
The rank cap gives a second bound `51*s`. Therefore any legal descending rank
vector `r` satisfies

`sum(r[:s]) <= U_s := min(51*s, s*f + sum_q n_q*min(q,s))`.

This argument counts occurrences, not distinct vector values. Treating repeated
axes as a single movable item would be unsound. For example, six duplicated
axes with `k=2,f=42` force the ranks to remain `(48,48)`.

For each observed row, form `R_s = U_s-U_(s-1)`, with `U_0=0`. The verifier
checks that these differences are descending, positive, at most 51 and sum
to `48*k`. They give precisely the final column of the table. These are upper
bounds until an actual assignment attains them.

## 4. Attainment and an independent complete finite check

The constructor processes cliques in descending size, assigning their distinct
vertices to children with the largest remaining target counts. It starts each
child with its forced axes. We do not assume this greedy procedure succeeds
for arbitrary list-colouring problems. For **every actual context**, the
verifier checks the resulting assignment, zero unfilled demand, allowed
colours, complete original multiset and every final pairwise dot product.
Every group attains the displayed `R` and hence every prefix bound `U_s`.

There is also a separately implemented exhaustive rank-vector audit. Since
`sum r_i=48*k` and `r_i<=51`, the deficits `51-r_i` are nonnegative integers
summing to `3*k`. For `k<=4` this automatically implies positive ranks. The
checker enumerates **all 1,049 labelled vectors** across the nine patterns.
For each it builds an integral flow network: a source edge of capacity `q`
to each clique, capacity-one edges from that clique to each child, and a sink
edge of capacity `r_i-f` from each child. It verifies flow conservation and a
matching minimum-cut value. A saturated flow is exactly a legal colouring.

There are 795 feasible vectors and 254 infeasible vectors. Their verdicts agree
with the prefix inequalities, and every feasible vector is majorized by `R`.
This second check uses neither the witness constructor nor its prefix formula
to decide feasibility. Its complete verdict stream is hashed in EXPECTED.json.
The proof does not rely on a floating-point optimizer or a solver status.

## 5. Exact moment optimum for the entire exponent interval

For every real `0<a<1`, the function `r -> r^(1-a)` is strictly concave. If a
descending vector majorizes another of equal sum, transfers from a smaller
coordinate to a larger coordinate decrease its sum of concave costs. Iterating
these transfers gives the usual majorization inequality. Because `R` attains
every upper prefix bound, it majorizes every legal vector in its group.
Consequently the witness minimizes `sum r^(1-a)` **simultaneously for every
real `0<a<1`**, not just at the chosen endpoint.

All other paid children and the width/role normalization remain fixed. The
number of residual children also remains fixed, so the retained conservative
complex surcharge is the same function of `a` for every assignment. The
optimality statement therefore applies to both the native and conservative
complex moment models. It does not optimize a different outer recipe.

The resulting eligible-child histogram is

`{39:264, 42:532, 45:765, 48:684, 51:2621}`.

Relative to PR1276's star optimum, exactly 264 groups improve from
`(51,51,48,42)` to `(51,51,51,39)`. The remaining rows already attain that
smaller class's optimum. The rank-only ceiling of PR1276 is not attainable
under this rule: the two-child duplicate-only, three-child low-mobility and
four-child low-mobility rows supply explicit compatibility obstructions.

## 6. Exact obstruction to physical realization of the witness

The source convention in the pinned `INHERITED-COMPLEX-GEOMETRY.txt` is

`X_t f(x)=f(x+t)`, `C_v=((1+i)I+(1-i)X_v)/2`.

On Fourier character `chi_u(x)=(-1)^(u dot x)`, address translation has
multiplier `(-1)^(u dot t)` and C_v has multiplier `i^(u dot v)`.
An address translation does **not** change the Fourier label u. In addition,
the eight physical data streams have separate multipliers. Commutativity of
address operators on one stream does not permit moving a factor to another
stream. Their subsequent scalar shears mix those streams.

The retained local invocation contract gives canonical frames

`X_s=C_[0,9+8s)`, `Y_s=X_s C_q^(-1)` for s>=0,
`X_-1=C_q`, `Y_-1=I`.

At a fixed Fourier character, stage s therefore acts by
`D_s F D_(s-1)^(-1)` or `D_s B D_(s-1)^(-1)`, on its declared pair,
where `D_s=diag(X_s(u),Y_s(u))`, `F:(X,Y)->(X,Y+X)`,
and `B:(X,Y)->(X-Y,Y)`. The stored entry/exit phase adapters are included
in this canonical boundary contract. A bridge from src to dst adds
`c*X_src` to `X_dst` and subtracts `c*Y_dst` from `Y_src`.
The terminal translation multiplies every Y by `(-1)^(u dot q)` before
`(X,Y)->(Y,-X)`.

`stream_check.py` composes these matrices with **the actual selected emitted
schedule**, preserving the pair/side family of every residual and translation.
It also applies all 30 hosted helper occurrences affecting replica 0, port 0
at their actual local sweeps, including sweeps on other replicas. Those helpers
are not dropped or moved back to the idle event. The source contract says the
other helpers are restored at each completed invocation. At cover g=I the
all-live cover correction is zero; the selected bank padding is empty.
Arithmetic is exclusively Gaussian integers represented by two Python integers.
This is a source-contract composition check, not a fresh local native proof.

Take replica 0, port 0, `q=11`, cover identity and Fourier character `u=32=e5`.
Order the physical streams as `(X0,Y0,X1,Y1,X2,Y2,X3,Y3)`. The baseline is
exactly `i*I_8`. The optimized assignment differs in precisely three entries:

| Output, input | Baseline | Optimized assignment |
|---|---:|---:|
| Y0, Y0 | i | -1 |
| Y1, Y0 | 0 | -1-i |
| Y3, Y3 | i | 1 |

All other entries equal the baseline. For example, an input supported only on
Y0 produces an unwanted nonzero Y1 output. This is an exact counterexample,
not a numerical tolerance or an inference from determinant alone.

A smaller witness moves just axis 32 from child 8 (family 672, pair 3 X) to
child 12 (family 0, pair 0 X), giving ranks 47 and 49. Both are unhosted and
owner-free. It passes every declared structural condition, group multiset,
orthonormality, X2 and legacy flattened-polynomial test, but differs from
`i*I_8` in the same first two entries and at `(X3,X3)`, which becomes 1.
Thus the structural rule itself does not imply physical equality.

Both counterexamples are rejected by the new stream equality guard. The
baseline also agrees exactly with the target on 147 explicitly listed modes
(zero, all 73 coordinate characters, all-ones and 72 adjacent pairs). These
positive checks support the implementation; they are not an exhaustive proof
for all 2^73 characters. One failing character is sufficient for the negative
result. The saved matrices and source schedule hash are in EXPECTED.json.

## 7. What the inherited checks establish

The inherited PR1324 checker erases family labels and models translations as
Fourier-label shifts. `core.legacy_flattened_operator` explicitly reproduces
that abstract check; its equality is not a physical operator certificate.
`--full` freshly emits and checks the selected baseline, then reproduces the
adapted global controller, invoice and strict assembly acceptance of this
invalid witness, including 15 controller, 69 assembly and 12 bit controls.
This is evidence of the missing semantic implication, not admission.
`LEGACY-PATCHES.json` lists all exact source edits and hashes; only scratch
copies are changed. The local/native and bit artifacts are authenticated and
reused, rather than rebuilt.

The resulting formal profile prices to kappa `0.001673074238324615` (native)
and `0.001673074235472000` (conservative), using both rational moment engines
and all 47 retained outer constraints. These are **relaxation prices only**.
They bound any operator-preserving subdomain of the stated assignment rule
under the same pricing assumptions, but this package does not exhibit a
physical construction attaining them. It also does not prove that every
nontrivial assignment fails, or that every assignment with the optimum rank
profile fails. The selected bound remains unchanged.

The cross-family issue was already acknowledged in PR1324's closure comment
at 2026-10-13 23:22:56 UTC, crediting Rohan Arun. Our later overlap refresh
found that acknowledgment before publication. We claim the complete selected
structural optimum and this explicit source-bound regression, not discovery
priority for the underlying flaw. See README.md and OVERLAP.json for credit.
