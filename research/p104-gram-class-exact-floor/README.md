# Exact E8 Gram-class floor through 24 deleted lines

No new kappa, supplier word or multiplication theorem is claimed.

For the Gram class of DreamingOfClouds's [PR #6888](https://github.com/CrocSwap/integer-mult-bounds/pull/6888),
let `g(d)` be the minimum cost over **both** the deleted set `D` with `|D| = d`
and all Gram-class designs on its complement. This package proves

```text
g(d) = 72 - 2 min(d, 8),       0 <= d <= 24.
```

The claim is a scoped written proof with exact finite certificates. The new
lower-bound step treats `d <= 7`. Explicit designs attain the bound for every
`d <= 24`, including the previously uncovered range below 16. The lower bound
56 for `8 <= d <= 24` uses the argument already in #6888, Theorem O, whose
codimension-two census applies throughout `d <= 24`.

In particular, deleting the eight simple-root lines gives `c = 56`, with eight
terms of price 7 and `det M = 65536`. Its 112 live ports have `v - c = 56`.
Thus `c >= 72 - |D|` and `v - c <= 48` do not hold for arbitrary deleted sets
in this enlarged Gram class. This set has the **size** of P112. It is not the
fixed P112 unit obtained by deleting an orthogonal frame. The example has
`M` nonscalar, so it does not contradict the exact-decoder floors in #2338.

## Model and precise quantifiers

Use doubled coordinates for the 240 E8 roots, of squared norm 8. Let `L` be
their 120 unoriented lines and choose a representative `l_p` on each line.
Set `N[p,q] = 1` over F2 when `(l_p . l_q)/4` is even. It has rank 9 and
admits a factorization `N = A G A^T`, with nine-column label matrix `A` and
invertible symmetric `G` over F2.

A design on `P = L \ D` is a finite family of pairs `u_k,w_k` in C^8 such
that `M = sum_k u_k w_k^T` is invertible. Its supports and prices are

```text
S_D(u) = {p in L \ D : l_p . u != 0},
rho_D(u,w) = rank_F2 N[S_D(u), S_D(w)],
c = sum_k rho_D(u_k,w_k).
```

The dot product is bilinear, with no complex conjugation. The theorem says
that **every** such design for **every** `D` of size `d <= 24` has cost at
least `72 - 2 min(d,8)`, and for **some** `D` of each size there is a design
with equality. It does not give the optimum for each individual deleted set.

## Proof

Write `a_D(u) = 9 - dim_F2 span{A[p] : p in S_D(u)}` for nonzero `u`.
Zero terms may be discarded.

### 1. Eight independent pairs and their price bound

Let `U,W` have the term vectors as columns. Cauchy-Binet expands
`det(U W^T)` as a sum over eight-element subsets `K` of
`det(U_K) det(W_K)`. Since the sum is nonzero, some `K` makes both selected
families bases of C^8. Discarding other terms can only lower the total price.
Sylvester's inequality in the nine-dimensional label space gives, termwise,

```text
rho_D(u,w) >= 9 - a_D(u) - a_D(w).
```

These are the Cauchy-Binet and Sylvester steps of #6888, Theorem O.

### 2. The finite geometric inputs

The ray census in #6888 gives the following numbers. Here `T(r)=S_empty(r)`;
`cost_j` is the least number of lines removed from `T(r)` to make its label
span have codimension at least `j`.

| `|T(r)|` | `cost_1` | `cost_2` |
|---:|---:|---:|
| 57 | 1 | 25 |
| 78 | 14 | 42 |
| 83 | 27 | 51 |
| 92 | 28 | 56 |
| 97 | 33 | 61 |
| 98 | 35 | 62 |
| 104 | 40 | 68 |
| 106 | 43 | 70 |

These are the eight fundamental-weight rays up to the E8 Weyl group. Only
`omega_8`, which is a root, has `cost_1 < 14`. The standalone verifier
reconstructs the Cartan matrix and its inverse, constructs the rays, and
computes this table by enumerating all label hyperplanes and all two-dimensional
annihilator subspaces. This checks a dependency of the new argument; the
census and the general `a_D(u) <= 1` consequence for `d <= 24` are credited
to #6888, rather than claimed as new results.

The verifier also checks the following root-specific fact over all 120 roots
and all 511 nonzero label functionals. For a root line `r`, exactly one label
hyperplane omits just `{r}` from `T(r)`; every other label hyperplane omits at
least 24 lines. The 63 roots orthogonal to `r` have rational rank 7.
Consequently, when `|D| <= 7`,

```text
a_D(r) = 1 if r belongs to D, and 0 otherwise.
```

Indeed, label-span deficiency means that some nonzero functional vanishes
on every surviving label. With at most seven deletions, its omitted set must
be the unique singleton `{r}`. Removing that singleton gives rank exactly 8.

### 3. Only deleted root directions can be deficient at small d

First take `x` real and nonzero, with `|D| <= 7` and `a_D(x) > 0`. Move it
by an E8 Weyl transformation into the closed fundamental chamber, moving `D`
as well. This preserves the mask and all relevant ranks. Write
`x = sum_i t_i omega_i`, with `t_i >= 0`.

Every positive root has nonnegative simple-root coefficients. Hence its
pairing with this sum vanishes exactly when its pairing with every active
`omega_i` vanishes. Thus `T(x)` is the union of `T(omega_i)` over `t_i > 0`.
Each active ray must therefore have deficient surviving label span. Its
`cost_1` is at most seven. The table forces every active index to be 8.
It follows that `x` is proportional to a root.

For complex nonzero `u`, choose a complex scalar `z` so that
`x = Re(z u)` has the same support on all 120 root lines as `u`. Such a scalar
exists because each nonzero root pairing forbids only a real line of choices
for `z`, and there are finitely many pairings. The real argument makes `x`
a root direction. Every root orthogonal to that direction is then also
orthogonal to `u`. Since these roots span its seven-dimensional orthogonal
complement, `u` is a complex multiple of the same root. The root-specific
fact in step 2 now forces that root line to lie in `D`, with deficiency 1.

### 4. Lower-bound assembly

For `d <= 7`, a basis contains at most one vector on each deleted root line.
Step 3 therefore gives `sum_{k in K} a_D(u_k) <= d` and the same bound for
bottoms. Step 1 implies `c >= 72 - 2d`.

For `8 <= d <= 24`, #6888's domination and `cost_2 >= 25` give
`a_D(u) <= 1` for every nonzero direction, including complex directions.
For completeness, its domination step replaces the root-hyperplane flat of
`u` by a real arrangement ray in that flat. The ray support is contained
in the original support. A deficiency of two would therefore force at least
25 deletions on that ray. Every selected term costs at least 7, so `c >= 56`.

### 5. Attainment

Take the Bourbaki simple-root basis `a_1,...,a_8`, whose doubled coordinates
are recorded in `build_designs.py`. Its Dynkin diagram has the perfect matching

```text
(1,3), (2,4), (5,6), (7,8).
```

For even `d <= 8`, delete the endpoints of the first `d/2` matching edges,
and pair their endpoints by transposition. Pair each remaining root with
itself. For odd `d < 8`, also delete one endpoint of the next edge and
transpose it with an unused simple root. Use the eight terms
`(u_k,w_k) = (a_k,a_tau(k))`. Both families are bases, so `M` is invertible.
For `d >= 8`, keep the `d=8` terms and append `d-8` other deleted lines.

`data/designs.json` lists all 25 resulting designs. The verifier independently
rebuilds every support from integer dot products and every term price from
the corresponding binary submatrix of `N`. It checks invertibility by exact
Bareiss determinants. The costs equal the stated floor at every `d=0,...,24`.
This finite enumeration proves attainment for the full asserted range.

## Reproduce and evidence limits

From the repository root, any CPython 3.12 can replace the interpreter below.
No third-party dependencies are needed.

```sh
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/p104-gram-class-exact-floor
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/p104-gram-class-exact-floor --check-source-history
~/git/integer-mult-bounds/.venv/bin/python3.12 -I -B -W error -X dev research/p104-gram-class-exact-floor/verify.py
```

The direct check ends with
`PASS_P104_GRAM_CLASS_EXACT_FLOOR designs=25 root_hyperplanes=61320 no_new_kappa`.
The registered commands run normal and optimized Python. Controls detect a
singular term family and compare the price-7 construction with identity pairing
on the same deleted set, which costs 64, and with restored lines, which costs 72.

To regenerate the committed design data without writing replay output into the
checkout, run `build_designs.py /absolute/scratch/designs.json` with the same
interpreter, then compare that JSON with `data/designs.json`.

No solver, Lean, Docker, selected supplier replay, physical COPY implementation
or complete multiplication theorem was run or established. The written proof
uses the usual E8 Weyl chambers and positive-root expansion. Its finite inputs
are checked exactly; independent human and formal proof-kernel acceptance
remain unclaimed. The theorem excludes `d >= 25`, non-Gram carriers and other
line systems. It gives no new floor for the subclass `M` proportional to `I`.

The verifier has bounded loops on at most 120 lines, 512 labels, eight-dimensional
matrices and 25 certificates. Python's managed allocation is the power-of-ten
memory-allocation deviation; all collections have these finite bounds. The
largest elimination matrices are 120 by 8 over integers and 8 by 16 over rationals.
Diagnostics use `-W error -X dev`; there is no separate configured static analyzer.

## Open next questions

1. For a fixed deleted set with `d <= 7`, determine when equality `72-2d`
   is attained. The first test is the odd-inner-product matching graph on
   independent deleted roots. This distinguishes the global minimum proved
   here from a statement about every deleted set. The pairing constraint
   after Cauchy-Binet is the remaining issue.
2. Determine the minimum under `M` proportional to `I` for nonorthogonal small
   deleted sets. Start with the eight-simple-root set, impose the exact matrix
   identity and reprice every term. The nonscalar construction here does not
   answer that decoder question.

Both questions and their first steps are in [TASK.json](TASK.json).

## Credit and provenance

This package was produced by Nick Petalas. New work is Apache-2.0.
DreamingOfClouds's #6888 supplies the Gram model, Theorem O's Cauchy-Binet,
Sylvester and domination argument, the ray census and the open question below
16 deletions. The new contribution is the small-deletion deficient-direction
argument and the attaining designs, giving the exact minimum over deleted sets.
DreamingOfClouds's #2338 and its credited decoder lineage concern the stronger
exact-decoder constraints and are cited for context, without replaying them.
Source commits, blobs and SHA256 pins are in [SOURCES.json](SOURCES.json).
The selected record and catalogue remain historical provenance.
