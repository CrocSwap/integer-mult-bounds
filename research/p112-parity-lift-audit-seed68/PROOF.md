# A copy-rank floor for orthogonal two-sided parity lifts

This is a finite, computer-assisted result with a written reduction from
arbitrary complex amplitudes to a finite support domain. It is not a
proof-assistant formalization or a theorem about all ten-term decoders.

## Model and quantified claim

Take the pinned P112 data from Mihir Srivastava's PR845, derived from
DreamingOfClouds' PR717. Let X be its 112 by 8 coordinate matrix and x_k its
columns. All entries are in {-1,0,1}. In the file's doubled-root units,
the roots have squared norm 8, their normalized Gram matrix is G, and
`XX^T = 2G`, `X^T X = 56 I_8`.

For row and source vectors d,t, define

```
beta(d,t) = rank_F2 E[supp(d), supp(t)],
E_rs = (1 + G_rs) mod 2.
```

The pinned nine-bit labels and duals factor E. Zero columns have cost zero.
The eight coordinate terms have beta=8 each. Their total 64 is the
predecessor value from Joel Pulikkan / GamingPuzzled's PR620 and its lineage.

Fix `(i,j)=(0,5)`, selected in the interrupted experiment by seed 32.
For every `q,s in {0,...,511}` and `t,h in C`, put

```
chi_q(r) = parity(q & label_r),
a = e_i + e_j,       b = e_i - e_j,
u_r = -t x_i(r) chi_q(r),
v_r =  h x_j(r) chi_s(r),
D = [X + u a^T, u, Xb],
T = [X + v b^T, -Xa, -v].
```

Transpose is ordinary transpose, without complex conjugation. The
certificate-backed claims for this exact family are:

1. `DT^T=XX^T` for every parameter choice.
2. `sum_(k=0)^9 beta(D_k,T_k) >= 64`. Equality occurs, for example, at t=h=0.
3. If both D and T have a column outside `col_C(X)`, that sum is at least 76.
4. Every individual term in this family has beta at most eight.

The first claim is algebraic. The remaining claims use the exhaustive
finite rank calculation below and the amplitude reduction. There is no
restriction to real or bounded-denominator amplitudes in the statement.

## Identity and exact support reduction

Since `a^T b=0`, expansion gives

```
(X+u a^T)(X+v b^T)^T
    = XX^T + (Xb)v^T + u(Xa)^T.
```

The ninth and tenth terms are `-u(Xa)^T` and `-(Xb)v^T`.
They cancel exactly for all complex t,h. Dropping either term is not this
identity.

Only columns i and j change among the first eight. Their entries are

```
D_i = x_i - t x_i chi_q,    D_j = x_j - t x_i chi_q,
T_i = x_i + h x_j chi_s,    T_j = x_j - h x_j chi_s.
```

For a fixed row and gate, each entry is `c + z d` with c,d in {-1,0,1}
and z equal to t or h. If d=0 its zero status is constant. Otherwise its
only possible zero is `z=-c/d`, hence in {-1,0,1}. The extra factors u and
-v can change support only at zero; Xa and Xb are fixed. Thus all ten
support pairs, and consequently every beta, are constant on each product
of the four amplitude classes

```
{0}, {1}, {-1}, C \ {0,1,-1}.
```

Representatives 0,1,-1,2 cover them exactly. This is a proof about zero
sets of linear polynomials, not an extrapolation from sampled amplitudes.
The verifier independently enumerates every nonconstant entry polynomial's
root and checks the breakpoint set is exactly {-1,0,1}.

Also, `X^T X=56 I` gives the exact membership test

```
w in col_C(X)  iff  X(X^T w) = 56 w.
```

For nonzero t, membership of u is independent of the value of t; likewise
for v and nonzero h. D has an outside-code column exactly when u is outside,
since its other columns differ from columns of X by multiples of u and
it includes u itself. The analogous statement holds for T and v.
Consequently the same four-class reduction also preserves the hypotheses
of claim 3.

## Finite certificate and two rank implementations

The stopping rule is complete coverage of
`512^2 * 4^2 = 4,194,304` parameter-class records, not unique decoders.
For every pair, six unchanged terms cost 48 in total. The verifier prices
the two changed terms and both compensation terms, with zero supports
charged zero. It checks the following complete histogram:

| Copy-rank sum | Parameter-class records |
|---:|---:|
| 64 | 270400 |
| 70 | 528320 |
| 71 | 1056640 |
| 72 | 4160 |
| 76 | 258064 |
| 77 | 1032256 |
| 78 | 1036320 |
| 79 | 8128 |
| 80 | 16 |

When both factors leave the code, the costs are 76,77,78, with counts
258064,1032256,1032256. At t=h=1 alone the histogram is
`{64:16, 70:4064, 76:258064}`. These are class counts; the generic amplitude
class contains infinitely many complex values.

The first rank implementation forms canonical bases for the row dual-label
span and column label span in F2^9, then eliminates their pairing matrix.
The second constructs all 112 by 112 bits of E directly from integer root
inner products. It uses a separate set-based, low-pivot elimination on the
literal binary rows. Taking a row basis before projecting to the selected
columns is valid because projection commutes with linear combinations.
Its rank therefore equals the rank of the literal restricted matrix.
The two algorithms agree on all 325638 distinct support pairs used by the
census and literal representative checks. Their shared inputs are the
validated geometry and support masks; they are not independent derivations
of the support formula.

Both rank implementations use exact integers. Cache keys contain actual
support masks or full bases, never just dimensions. The certificate records
all 25 four-rank profiles and witnesses. Literal factor multiplication
checks all entries at those witnesses and two nonintegral rational examples.
The all-amplitude identity follows from the expansion above, not those 27
finite examples. One uses exact rational amplitudes within 2^-80 of 1 and
3^-60 of -1; rounding them would change the support class.

## Audit finding and controls

The interrupted seed-32 checker selected q=32,s=97,t=h=1 for its allegedly
two-sided control. On the pinned geometry, q=32 yields `u=-x_0`, which is
inside col(X). The source correction is outside. This is a failed test
precondition, not a counterexample to any cost inequality and not a defect
in the selected supplier.

The repaired control chooses from gates whose outside-code condition was
actually checked. Audit seed 68 selects `(q,s)=(72,443)`. The full identity
costs 76; failing to bill both extra terms would falsely report 62. Omitting
either compensation column, reversing the final sign or replacing b by a
breaks exact equality. Other controls distinguish support cardinality from
rank, dependent binary rows from full rank, equal-dimensional spaces with
different pairing ranks, and corrupted label data.

## Accounting and limits

The algebraic statement concerns the defined sum of pairing ranks. Reading
it as a physical copy lower bound inherits PR446 Theorem C's separate-total,
drop-free gathering and copy-tree assumptions. This package does not prove
those interfaces or upgrade the review status of PR446 or PR620.

For the proposed reduction in copied information, the optimistic budget is
`C_copy = sum beta`. Preparation, source access, frame changes, additional
copies, restoration and every recursive child are separately granted zero
expense at this screen. They are not omitted terms in the ten-term identity:
both added totals are already priced. The screen fails to reduce the
copy-rank component below 64, and a genuinely two-sided member costs at
least 76. A physical model must still price each of those other expenses;
this note does not add operation counts to ranks as though they shared
units. It is not a complete supplier recurrence or a runtime comparison.
At a fixed rank sum, helper work, rank distribution, geometry, scheduling
and hosting could still improve. No conclusion about those opportunities,
the recursive moment or kappa follows from this census.

Arbitrary nonlinear gates, other coordinate pairs, nonorthogonal directions,
more general extra terms, masked E-graph identities and interacting delivery
programs are outside the quantified domain. PR1224 already provides a
ten-term two-sided identity; this package claims a cost result for one
specified class, not priority for existence. The fixed-reader obstruction
in PR1197 does not apply directly because both original factors change here.

Prepared for Sagar Thakrar with substantial OpenAI Codex assistance.
Apache-2.0. Source identities and attribution are in SOURCES.json.
