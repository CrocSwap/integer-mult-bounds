# Five-port quadratic decoder: a scoped format obstruction

This is a written mathematical argument with exact finite rank certificates.
It is **not** a proof-assistant verification, an unrestricted decoder lower
bound, or a new integer-multiplication construction.

## 1. Object and statement

Let `p >= 5`. The ports are the `v = 32 binom(p,5)` five-element subsets of
`{0,...,2p-1}` containing at most one element of each pair `{2i,2i+1}`.
Write `j = |S intersect T|`. The five-port, level-one star identity over F2 is

```
x_T = sum_(a in T) z_a + sum_(S: |S intersect T| in {1,3}) x_S,
z_a = sum_(S: a in S) x_S.
```

The coefficient of `x_S` on the right is `j + 1_{j in {1,3}} (mod 2)`.
It is zero for `j = 0,...,4` and one for `j = 5`, which means `S = T`.
Joel Pulikkan's PR231 establishes the parity context and explicitly leaves
the geometry and cost of `k=5` open. We investigate **one** geometry:

```
G(S,T) = 2(j-1)(j-3).
```

The theorem concerns every rational common-label realization of this Gram
matrix, with the displayed correction terms delivered drop-free and each
of the `2p` coordinate-star totals gathered drop-free and copied separately
to all its coordinate-star readers in each stage, under the accounting
premises in section 4. The copy of one total may use a tree or split its
readers; mixing different totals into a new coded message is outside scope.

**Theorem.** In this class, no positive supplier saving is possible at
`p=5,6,7`. For every `p >= 5` and every integer number of stages `s >= 3`,
any positive supplier saving `gamma` satisfies

```
gamma < 125/76433 = 0.0016354192560804888... .
```

This is below the **frozen, maintainer-reviewed** selected
`kappa = 1661957774647029/10^18` at base
`47481c89fd30a43f8f882eb4b391e89c29273fd0`. Since the inherited assembly
requires kappa below its bit supplier saving, this decoder class cannot
improve that selected result, even if the other supplier is free. The
number above is an upper bound on a proposed supplier class, **not a
new certified kappa**.

## 2. Why a new geometry is needed

Fix five coordinate pairs. Among their 32 orientations, take the 16 whose
number of odd coordinates is even. Two distinct such ports differ in two
or four coordinates, hence have intersection three or one. The decoder
requires a drop-free correction between every two distinct ports in this
set. Under the common-label frame rule, their nonisotropic rank-one labels
must be pairwise orthogonal. They are therefore linearly independent.

In contrast, affine functions of the five orientation bits span a space
of dimension at most six. Any linear transformation of the original
ten incidence coordinates, even with a constant coordinate and an
arbitrary symmetric rational bilinear form, still has label span at most
six on this cube. Thus the old incidence-linear geometry cannot realize
this correction pattern. This is not merely a failure of a symmetric
choice of bilinear form.

A quadratic lift does realize the required zeros. Use feature coordinates
`1`, `1_{a in S}`, and `1_{{a,b} subset S}` for pairs of coordinates from
distinct coordinate pairs. Give the three groups diagonal form weights
`6`, `-6`, and `4`, respectively. The resulting rational symmetric form is
nondegenerate on this feature space, and

```
<u_S,u_T> = 6 - 6j + 4 binom(j,2) = 2(j-1)(j-3).
```

In particular the diagonal is 16 and both correction classes are
orthogonal. The form is indefinite; positive definiteness is not claimed
or needed for the retained rational frame model. Up to scaling, this is
the unique nonzero polynomial in `j` of degree at most two that vanishes
at one and three. The 16-orientation clique attains rank 16 inside one
cube for this lift. The rest of this note shows why algebraic admissibility
alone does not make the lift useful.

## 3. Finite rank certificates and the infinite tail

Let `N_T` be all ports intersecting target `T` in one or three coordinates.
Let `P_a` be all ports containing coordinate `a`. The two needed ranks are:

- `d_p <= rank G[N_T,N_T]`, a lower bound on the bilinear rank of the
  drop-free corrector space;
- `r_p <= rank G[P_a,P_a]`, a lower bound on the source/reader pairing rank
  for the separate total `z_a`.

Permuting coordinate pairs and swapping the two coordinates of any pair
preserves both the port family and `G`. This group acts transitively on
targets and on coordinates. A witness at the canonical target
`{0,2,4,6,8}` and coordinate `0` therefore applies to **every** target or
star at that `p`.

| p | v | d_p | r_p | c_p = 2p r_p |
|---|---:|---:|---:|---:|
| 5 | 32 | 15 | 11 | 110 |
| 6 | 192 | 50 | 35 | 420 |
| 7 | 672 | 83 | 60 | 840 |
| 8 | 1,792 | 111 | 84 | 1,344 |
| 9 | 4,032 | 143 | 112 | 2,016 |
| 10 | 8,064 | 179 | 144 | 2,880 |
| 11 | 14,784 | 219 | 170 | 3,740 |
| 12 | 25,344 | 263 | 210 | 5,040 |
| 13 | 41,184 | 311 | not needed | granted zero in tail |

`WITNESSES.json` contains the row and column ports of 17 square minors,
their dimensions, and their nonzero determinants modulo **65521**. Each
entry is an integer. A determinant nonzero modulo a prime is a nonzero
integer determinant, so each minor proves the stated **rational lower
bound**. This implication is exact; it is not a probabilistic modular-rank
estimate and needs no determinant height bound. The row and column sets
may differ; both lie in the same stated neighborhood or star.

The proof needs only these lower bounds. It does not assume that the
listed ranks are maximal. In particular it does **not** extrapolate the
ordinary star values to 180 at `p=11` or 220 at `p=12`: discovery found
degenerate pairings there, and the actual witnesses certify 170 and 210.
No all-parameter rank formula or unverified numerical rank is a premise.

For **every `p >= 13`**, fix any target and choose eight additional
coordinate pairs. The 13 selected pairs contain an isometric copy of the
entire `p=13` configuration, including its corrector minor. Consequently
every target has corrector rank at least **311**. This embedding, together
with the finite certificate, proves the all-p tail statement. It is not
an inference from failure to find a better candidate in a finite search.

## 4. Explicit accounting premises and optimistic budget

We retain the following common-label, compressed-window accounting
premises. They specialize DreamingOfClouds' PR446 Theorems B/C and the
format-limit axioms `(P)`, `(Dfc)`, `(Win)`, `(Sch)`, `(Bat)` to the present
decoder. The retained sources are pinned in `SOURCES.json`. We do not
claim to prove their all-size machine realization here.

1. There are `s >= 3` stages, one active source/target bank pair per stage,
   rank-one data labels, drop-free delivery of the displayed correctors,
   and a common stage climb `a`. Corrector rank forces `a >= d_p`.
   The retained fixed-window `(Win)` accounting requires ambient dimension
   `m >= 1+s*a`. This last relation is an explicit format premise; the
   rank witnesses alone would only force `m >= 1+s*d_p`.
2. At each stage, each of the `2p` totals is gathered **drop-free** from
   `P_a` and delivered to `P_a` through its own rooted copy tree. The
   pairing-rank drop bound is paid **additively
   for these separate totals**, so per-stage copy charge `c >= c_p`.
3. Per replica, the pressure deficit obeys
   `D <= (s-1)v - s*c`. For paid recursive children of ranks `0<r<m`,
   the saving satisfies the pressure equation
   `sum_r z_r r((m/r)^gamma - 1) = D`. A nonnegative fallback term only
   makes admission harder.
4. The two active data climbs per port per stage have total mass `2sva`.
   Each child doing this active work has rank at most `a`, as in the
   fixed-window batching premise. Thus their pressure alone is at least
   `2sva((m/a)^gamma - 1)`. A child cannot discharge this mass twice.

These are restrictions on the format, not assertions about every possible
integer-multiplication algorithm. They are compatible with granting all
of the following unpriced work zero additional expense:

| Work | Optimistic treatment |
|---|---|
| Source access, gathers and decoder arithmetic | zero |
| Helpers, frame adapters, private scratch | zero |
| Restoration and dirty compensation | zero |
| Idle climbs, hosting, bridges and stage changes | zero |
| Copy-related pressure beyond its deficit charge | zero |
| All other recursive children and their fallback charges | zero |
| Precision, tape, row, and outer-assembly overhead | zero |

Required active recursive mass and the separate-star copy deficit are the
only charges retained. They are **lower bounds**, not a complete proposed
supplier invoice. Any additional nonnegative cost strengthens the
obstruction. A mechanism invalidating a premise must be priced afresh.

For `gamma>0`, `exp(x)-1 >= x` and `m/a > s >= 3` give

```
D >= 2sva((m/a)^gamma - 1)
  >  2sv d_p gamma log(3).
```

Combining with the deficit bound and discarding the favorable `-1/s`
term yields

```
gamma < (1 - c_p/v) / (2 d_p log(3)).
```

If `c_p >= v`, the deficit is negative at every positive `s`; this
settles `p=5,6,7` before implementing any supplier.

For a rational bound, the first six positive terms of

```
log(3) = 2 sum_(i>=0) (1/2)^(2i+1)/(2i+1)
```

already exceed `549/500`. The verifier checks that strict inequality
using `Fraction`, with no logarithm library or floating point. Substitution
gives the following strict supplier upper bounds:

| p | rational upper bound |
|---|---|
| 8 | `125/121878` |
| 9 | `125/78507` |
| 10 | **`125/76433`** |
| 11 | `31375/20198808` |
| 12 | `5875/4235352` |

For `p >= 13`, grant **even the copies** zero cost and use `d_p >= 311`:

```
gamma < 1/(2*311*log(3)) < 250/170739 < 125/76433.
```

All comparisons, including the strict gap to the frozen selected kappa,
are rational and reproduced by the checker. No stage-count cutoff is
used: `s>=3` was eliminated algebraically. This completes the theorem.

## 5. Boundaries

This closes the **specified natural quadratic Gram / separate coordinate
star / compressed-window accounting** class. It does not close other
quadratic label pairings, asymmetric labels, coded combinations of stars,
punctured ports, higher-star decoders, retained cross-stage information,
paid non-drop-free gathers or corrections, or a different bank schedule.
It makes no claim that a stronger kappa
exists in those classes.

There is no circuit, hosted profile, all-size compiler or assembly
certificate here. Realization, common-label/mutable-source validity,
whole-call hosting, restoration, precision/tape, bit H1–H5 and analytic
transfer remain inherited obligations for any actual construction.
Finite exact rank verification does not discharge them.
