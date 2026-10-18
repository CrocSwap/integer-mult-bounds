# The P112 two-total boundary at 44–47 source ports

This is a scoped exact matrix theorem and a finite premise certificate, not a
formal proof of integer multiplication. The geometry and separate-total COPY
model are inherited. No new supplier, selected exponent or physical schedule
is claimed.

## Model and conclusions

Use the pinned integer `112 x 8` matrix `X`, binary source labels `l_t` and
dual labels `v_i` in `research/p112-single-lift/reference-geometry.json`.
Write `x_j` for coordinate column `j`, `S_j=supp(x_j)`, and

    beta(d,s) = rank_F2 [(v_i dot l_t)]_(i in supp(d), t in supp(s)).

All complex transposes are ordinary transposes. For an arbitrary deleted
source set `U`, put

    g_j(U) = 8 - beta(x_j, x_j restricted to S_j minus U),
    L(U) = sum_j g_j(U).

Consider an exact two-total factorization retaining the eight coordinate
readers. In the remaining full-rank on-column case of Philipp/mightyOil's
PR1197 it has the form

    XX^t = XY^t + (XA)Z^t,   Y = X - ZA^t,

where `A` is `8 x 2`, `Z` is `112 x 2`, both have complex rank two, and
`U=supp(z_1) union supp(z_2)`. The formula for `Y` follows from injectivity
of `X`; it is not an additional assumption on the source columns. In
particular, `Z` need not lie in `col_C(X)`.

The new conclusions are:

1. For **each** `M=44,45,46,47`, `max_(|U|=M) L(U)=5`. This is a bound on
   arbitrary deletion sets, irrespective of complex realizability.
2. If `|U|<=47` and `Y=X-ZA^t` with **at most two correction columns**, then
   `sum_j [8-beta(x_j,y_j)]<=4`. The new step excludes the geometric
   five-loss pattern by a rank-three cancellation minor. The bound is
   attained at union size 44 by the supplied rank-two overlapping fixture.
3. Charging both nonzero added terms gives **COPY rank sum at least 66**
   in the full-rank on-column case through source union 47. Attainment of
   this 66 lower bound is not claimed. Combined with PR1197's complementary
   reductions, **every exact two-total decoder in this fixed-reader model
   with source union at most 47 has COPY rank sum at least 64**.

Josie Elliston's PR1787 proves the general no-saving statement through 43,
and Philipp/mightyOil's PR1827 proves the full-rank floor 66 and exact joint
losses through 43. Those remain predecessor results. This package extends
their explicitly open boundary and adds the rank-two realizability argument.

## Exhaustive finite premises

For each reader construct the binary code `C_j` of evaluations on `S_j`.
The checker constructs it using all 512 ambient functionals, then checks
equality with the XOR span of the **literal pairing rows**. Each code has
256 words, and its weights are

    0^1, 24^63, 28^128, 32^63, 56^1.

The fixed reader dual span has dimension eight. Nullity gives

    g_j(U) = dim_F2 {c in C_j : supp(c) subset U}.

The checker establishes the following for **all eight readers**, without
assuming they are in one symmetry orbit:

- Every union of two distinct nonzero codeword supports of size at most 47
  is enumerated: 10,353 supports, of weights 36 (336), 40 (4,977), and
  44 (5,040). Each contains exactly four codewords.
- Extending these supports by a word with a new support coordinate gives
  all 12,012 three-space supports through 47: 1,260 of weight 44 and
  10,752 of weight 46. Each contains exactly eight codewords. A fourth
  independent word requires at least 48 ports.
- For every such three-space support `V` and every `k!=j`, the common
  coordinate cut `S_j intersect S_k` is either contained in `V` or needs
  **at least four** additional ports.

Here and below, support lists are exact sets, not heuristic searches. For
completeness, take any two independent words of a hypothetical kernel.
Their support occurs in the first list. Because that support contains
exactly their four-word span, every third independent word has a new
support coordinate and is included by the extension step. The same
argument, using the eight-word closure of every three-space support,
excludes a four-dimensional kernel below 48. A weight-56 word cannot fit
and is safely omitted from the truncated joins.

Next, for every reader subset of size 1 through 5, the checker recursively
joins one nonzero codeword support from each reader, keeping every distinct
union of size at most 47. Prefix pruning is complete: unions only grow.
The total numbers of unions, counted separately for each reader subset,
are `2032, 280252, 9072, 42, 0`. Every three-reader subset has minimum union
40. Across all four-reader subsets, exactly the predecessor's **42
40-port cuts** occur; the larger cap introduces no new four-reader union.
Each has four losses of size one. The complete two-space inventories show
that a second loss at an affected reader requires at least **12** ports
outside each such cut. Both kernel cardinalities and a separate unpacked
binary matrix-rank oracle check their loss vectors.

For every ordered pair `j!=k`, exactly one nonzero word of `C_k` is wholly
supported inside `S_j`: its support is `S_j intersect S_k`, of size 24.
Every other nonzero word needs at least **12 ports outside `S_j`**. Finally,
for each of the 56 unordered coordinate triples, the eight common-support
rows of `X` contain an explicit nonzero integer `3 x 3` minor on those
columns. `RESULT.json` records its rows, matrix and determinant. A separate explicit
pass checks all 672 minimal `3+1+1` cancellation classes (84 for each
third-loss reader): all have size 44 and their forced three-column partial
completion has exact rational rank three. No coordinate symmetry is assumed.

## The geometric maximum and its only five-loss shape

At most four readers are affected. At most one reader can lose two or more
ranks: two such readers need at least `36+36-24=48` ports, because their
coordinate supports intersect in 24 positions. No reader loses four ranks
below 48. If four readers are affected, the four-reader census and its
12-port second-loss margin force all losses to be one. Otherwise there
are at most three affected readers, at most one with loss three, so the
total loss is at most five.

Consequently the **only** possible five-loss shape through 47 is
`g_j=3, g_k=g_l=1` for distinct `j,k,l`. The checker derives a 44-port
three-space support with this shape, rather than reading a proposed
witness from the receipt. Seed 49 selects reader 1 and a deterministic
SHA256 ordering of its 84 maximizing supports. Padding the selected set
gives literal-rank-checked witnesses at 45, 46 and 47 as well. Thus the
geometric maximum five is exact for every new size. Deleting one port
from the 44-port witness reduces the loss to at most four.

The old geometric maxima below 44 also follow from these same inventories:
zero below 24; two on 24–35; three on 36–39; four on 40–43. Their sharpness
and priority belong to PR1827; no new claim for that interval is needed.

## Why two correction columns cannot realize five losses

Let `delta_j=8-beta(x_j,y_j)`. The fixed reader dual span has dimension
eight, so `delta_j>=0`. Outside `U`, `y_j=x_j`; restriction of columns
cannot increase rank, so `delta_j<=g_j(U)`.

Suppose `sum delta_j>=5`. The geometric bound forces equality and the
unique shape `delta_j=3, delta_k=delta_l=1`. In `C_j`, the words vanishing
on the active source positions of `y_j` within `S_j` form a
three-dimensional kernel. Its support `V` is in the complete three-space
list, is contained in `U intersect S_j`, and has size at least 44. Thus
`|U minus V|<=3`. At every port of `V`, `y_j` is zero.

The lost rank at reader `k` supplies a nonzero word of `C_k` supported on
zero positions of `y_k`, hence supported inside `U`. It cannot need 12
ports outside `S_j`, since `U` has at most three outside `V subset S_j`.
The unique shared-word premise therefore forces its support to be
`S_j intersect S_k`. The four-port positive extension margin forces that
entire common cut inside `V`: there is room for at most three new ports.
The same argument applies to `l`.

On the eight ports `S_j intersect S_k intersect S_l`, all three source
columns `y_j,y_k,y_l` must consequently vanish. On these rows and columns,

    (X-Y)[common rows, {j,k,l}] = X[common rows, {j,k,l}].

The right side has rank three over `C`, certified by its nonzero integer
minor. But `X-Y=ZA^t` has rank at most two. This contradiction proves
`sum delta_j<=4`. It uses no reality, positivity, magnitude bound or
coordinate-support-disjointness assumption on `A,Z`.

The positive fixture in the receipt has full-rank `A,Z`, overlapping
coefficient supports, source union 44 and retained COPY ranks
`(8,5,7,8,8,8,8,8)`. Both added sources leave `col(X)`; the exact rank of
`[X Z]` is 10. Its added COPY ranks are `(8,7)`, so its complete COPY bill
is **75**, not 66. This proves sharpness of the retained-loss-four bound,
not of the total bill.

As a negative control, allowing **three** correction columns on the same
44-port set gives retained loss five. It is a valid all-pairs decoder with
COPY bill 81 and `[X Z]` rank 11. Both complete identities are checked on
all 12,544 ordered port pairs and all term costs by two rank engines. The
control refutes a version of the realizability claim that omits the
two-column hypothesis; it is not a cheaper decoder or supplier.

## Charging the added terms

The added-reader premise is from Mihir Srivastava's PR845, reused by
PR1787/PR1827. For all 511 nonzero nine-bit functionals `q`, the checker
recomputes the rank of `X[{i:q dot v_i=1},:]`: 503 have complex rank eight;
eight have rank seven, with distinct coordinate-axis kernels. Each lower
bound is certified by rank modulo 3; eight columns, or the one identically
zero column, give the matching characteristic-zero upper bound. This does
**not** assume ranks over unrelated fields are generally equal. No live
source label is exceptional.

For any nonzero `d=Xa` with arbitrary complex `a`, its active dual span
therefore has dimension at least eight. Otherwise at least three nonzero
functionals annihilate it, putting `a` in three of these kernels. A
full-rank functional forces `a=0`, as do two distinct exceptional axes.
Also every live source label is visible: an invisible label would put `a`
in the corresponding full-rank kernel.

Evaluation on this active dual span has kernel dimension at most one. If
an added source has `m` distinct active labels and COPY rank `r`, those
labels lie in the preimage of an `r`-dimensional image. Hence the deliberately
weak inherited bound is

    r >= p(m) = min {r>=1 : m <= 2^(r+1)}.

This is PR1432's support-from-rank argument, not a new price theorem. In the
full-rank two-total case both sources/readers are nonzero, and their sizes
`m_1,m_2` satisfy `1<=m_h<=M` and `m_1+m_2>=M`. The checker exhausts this
integer price relaxation for each `M=1..47`. At `M=44..47` its minimum is
six. Thus the retained bill at least 60 plus both added bills gives **66**.
The already known geometric bounds below 44 give the same uniform floor.

PR1197's pinned written theorem supplies the complementary rank-one,
off-column and disjoint-coefficient reductions, with COPY sum at least 64.
Those cases are not assigned the stronger 66 floor here. Combining the
reductions proves the stated general no-saving range through 47.

## Scope and credit

All helpers, source access, frame changes, copies beyond the named totals,
restoration, hosting, precision and additional recursive work are granted
zero extra charge for this favorable COPY-rank screen. The result excludes
a reduction of this **separate-total rank sum** in the stated support
range. It does not compare power sums or rank distributions, and does not
exclude improvements in other components of a completed supplier bill.
Unions of 48 or more, changed readers, masked exactness and different
physical delivery models are outside the theorem. The finite certificate
does not formalize the written implications or the multiplication theorem.

Immediate credit: Josie Elliston PR1787; Philipp/mightyOil PR1827 and
PR1197; Mihir Srivastava PR845; woklerx PR998; commdata2338 PR1375;
Hanson Sun/bbMisk PR1432; adamgall's Gram census; DreamingOfClouds' root-unit
and separate-total model (including PR446/PR717), and Joel
Pulikkan/GamingPuzzled's coordinate COPY lineage. The broader pending
PR2338 assumes both factors in the column space of a minimal-rank
realisation; the new argument allows arbitrary source columns `Z` and
does not rely on that proposal. Exact source pins and review heads are in
`SOURCES.json` and `TASK.json`.

Prepared by Sricharan Vagvala (@theon199), with substantial OpenAI Codex
assistance for mathematics, implementation, checks and writing. Author-run
evidence; no independent human review. Apache-2.0.
