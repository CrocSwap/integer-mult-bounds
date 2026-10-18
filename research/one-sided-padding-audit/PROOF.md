# Exact support certificates and the normalization boundary of padding

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
This is a written proof with exact finite inputs, not a proof-kernel result.

## Statement and model

Fix the 120 E8 root lines, the orthogonal eight-line frame F, and the dense
binary pairing used in PR2816 and PR3074. Let X be the 112 non-frame lines and
E = X union F. Roots have squared length two. With the frame order in the
pinned PR2816 data, put

\[
C_{ti}=\langle r_t,f_i\rangle,\qquad C_{f_i}=2e_i,\qquad
B_{ts}=1+\langle r_t,r_s\rangle\pmod 2.
\]

Scalar coefficients below lie in a field K of characteristic different from
two. The **binary cost table B stays fixed**; it is not reduced from a scalar
matrix over K. Labels l_t span V = F2^9 and realize B through a nondegenerate
symmetric bilinear form beta. Write z_i = l_(f_i), and
`w(p) = dim_F2 span{l_t : p_t != 0}` on the specified line set.

A one-sided decoder here means a finite identity

\[
P Y^T=C_X,\qquad q_k=C_X y_k,
\]

so `P Q^T = C_X C_X^T`. Its algebraic cost is

\[
c(P,Y)=\sum_k\operatorname{rank}_{F_2} B[\operatorname{supp}p_k,
                                              \operatorname{supp}(C_Xy_k)].
\]

Zero terms may be discarded. This is a fixed Gram and dense-pairing model;
we do not prove that another realization, pairing, or physical supplier must
have this form.

**Audited conclusion.** Merging proportional corrected terms, discarding zero
sums, and reclassifying the remaining terms produces a decoder of cost
`c_normalized <= c_raw`. PR3074's padding then gives a one-sided E decoder with

\[
c_E=c_{\rm normalized}+8\ \leq\ c_{\rm raw}+8.
\]

The equality refers to the normalized cost. An explicit rational input below
has `(c_raw,c_normalized,c_E)=(72,64,72)`. This is not a counterexample to the
existence of some artificially more expensive decoder of cost `c_raw+8`.

The support and padding statements in this proof extend to all K of
characteristic different from two. This extension does **not** transfer the
other characteristic-zero results of PR2816 to positive characteristic.

## 1. What the finite certificate proves

PR845 supplies the original real P112 support lemma. PR1098 gives a different
exact Gram-spectrum certificate; PR1815 gives exact deletion-rank evidence
for a further fitting corollary. Those results retain priority. PR2816's
specific `checks/w8.py` uses NumPy `matrix_rank`, SVD, and tolerances for its
copy of the premise. The present certificate binds that same literal chart
to integer minors, includes the full E set needed by PR3074, and records the
characteristic restriction explicitly.

For every nonzero `h in F2^9`, let

\[
D_X(h)=\{t\in X:h\mathbin{\cdot}l_t=1\},\qquad
D_E(h)=\{t\in E:h\mathbin{\cdot}l_t=1\}.
\]

`CERTIFICATE.json` lists all 511 characters, without symmetry reduction. For
each it supplies original row indices, column indices and an exact signed
determinant for a minor of C on each of these two sets. A Fraction-based
generator chooses the minors. The verifier recomputes their determinants by
integer Bareiss elimination; it checks every exact division.

| Matrix | Exact rank distribution | Upper-rank evidence |
|---|---|---|
| C on D_X(h) | 503 rank eight; eight rank seven | Eight columns; in each rank-seven case one specified coordinate is identically zero |
| C on D_E(h) | All 511 rank eight | Eight columns |

The absolute values of all 1,022 certifying determinants are **16, 32 or 64**.
They are therefore nonzero over every K with characteristic other than two.
The rank-seven nullspace is exactly `K e_i`, with each i occurring once. Its
complement in X is precisely the 56-element support of `C_X e_i`. The verifier
checks its binary label span has dimension eight, and identifies its defining
functional with `beta(-,z_i)` at all 120 labels.

The source data's labels are authenticated without reusing its floating
basis selection: generate the D8-plus-half-integral description of E8, check
the full line set and frame, derive C and all 14,400 entries of B exactly,
then verify that `l_t -> B[t,:]` extends to an injective linear map on V.
Symmetry of B makes this map a symmetric bilinear pairing on V, and
injectivity makes it nondegenerate. Thus the recorded label chart is a valid
chart for the literal cost table. No predecessor Python code is executed by
the new verifier.

All ranks claimed here follow from nonzero integer minors and explicit null
directions, not from a failed search or approximate rank threshold.

## 2. Universal support and term-cost consequences

Let `y != 0` in K^8. If the labels on `Off_X(y) = supp(C_X y)` span a proper
subspace of V, some nonzero h annihilates that span. Then `C_t y=0` for all
`t in D_X(h)`. Section 1 forces h to be one of the eight exceptions and
`y in K e_i`. Conversely, for nonzero `y=mu e_i`, the exact support is the
56-element set already checked, with span `W_i=z_i^perp` and dimension eight.
Hence

\[
\operatorname{span}l(\operatorname{Off}_X(y))=
\begin{cases}
W_i,& y\in K^\times e_i,\\
V,& \text{otherwise}.
\end{cases}
\]

The same annihilator argument on E has no exceptional character: every
nonzero y has full binary support span V. The quantifier over all y and all
such fields is justified by the minor argument, not by testing finitely many
coefficient values. The additional enumeration of all 6,560 nonzero F3^8
vectors is a control: X has sixteen rank-eight and 6,544 rank-nine supports;
E has 6,560 rank-nine supports.

For `U=span l(supp p)`, restricting the nondegenerate pairing gives

\[
\operatorname{rank}B[\operatorname{supp}p,\operatorname{Off}(y)]
=\dim U-\dim\bigl(U\cap\operatorname{span}l(\operatorname{Off}(y))^\perp\bigr).
\]

Thus the X term cost is `dim U - epsilon`, with epsilon one exactly when
`y=mu e_i` and `z_i in U`; call such a term **corrected**. Otherwise epsilon
is zero. On E, every nonzero term has cost exactly `dim U`.

Characteristic two cannot be silently included: the nonzero vector
`y=(1,1,1,1,1,1,1,1)` satisfies `C_E y=0` modulo two. Its support has rank zero.
This is an explicit counterexample to extending the support conclusion.

## 3. Merging, including cancellation of the correction

For one axis i, take all r corrected terms with `y_k=mu_k e_i`. Replace them
by `(p,e_i)`, where `p=sum mu_k p_k`, and discard it if p=0. Exactness is
preserved. Put `U_k=span l(supp p_k)`, `T=sum U_k`, and
`W=span l(supp p)`. Each U_k contains z_i, and `W subset T`, so

\[
\dim T\leq\sum_k\dim U_k-(r-1).
\]

If `z_i in W`, the new cost is `dim W-1 <= dim T-1`. If `z_i notin W`,
then W is proper in T because T contains z_i; the new cost is
`dim W <= dim T-1`. Both cases give

\[
c_{\rm new}\leq\sum_k(\dim U_k-1)=c_{\rm old}.
\]

This explicitly handles the cancellation branch not spelled out in the short
dimension inequality in PR2816 section 3.1. It confirms nonincrease; it does
not find a false theorem there. Nonincrease also follows directly from the
common-column-set rank subadditivity of joaqcoo's PR1224 merge lemma; no priority
for that lemma is claimed. No full-correction absorption is required
for padding. Reclassification after the merge leaves at most one corrected
term for each axis, giving a set I of corrected axes.

## 4. Padding and its complete algebraic charge

Zero-extend every p to E. For each corrected term `(p,mu e_i)` put
`p(f_i)=2/mu`. For each `j notin I`, append `(delta_(f_j),2e_j)`.
Every old row of `P Y^T` is unchanged; row f_i is exactly 2e_i. Therefore the
new decoder is exact and one-sided with `q_k=C_E y_k`.

| Terms | Support-span change | Change in cost |
|---|---|---|
| Corrected term on i | Adding z_i does not enlarge U because z_i was already in U | +1: its former epsilon disappears |
| Other surviving old term | Zero extension preserves its support span | 0 |
| New delta term on j not in I | One nonzero label; `C_E 2e_j` has full support span | 1 each |

The total increase is `|I|+(8-|I|)=8`, measured from the normalized decoder.
This is a complete bill for the **declared algebraic rank-cost model** only;
it is not a physical instruction, storage, restoration or recursive invoice.

## 5. Lift implication, without assuming its open floor

For `X_I=X union {f_i:i in I}`, let S contain the code `col C_(X_I)`. Define
`cost_w(S)` as the minimum total w over bases of S. Zero-extend S to E and
adjoin the missing frame units to form S+. Then `S+` contains `col C_E`:
the discrepancy between any extended codeword and its E codeword is supported
only on the missing frame rows. An extended minimum-weight basis of S and the
`8-|I|` missing units span S+; selecting a basis from that spanning set cannot
increase total nonnegative weight. Consequently

\[
\operatorname{cost}_w(S^+)\leq\operatorname{cost}_w(S)+8-|I|.
\]

If **L120(K)** holds, namely every S+ containing `col C_E` has weight cost
at least 72, this implies `cost_w(S)>=64+|I|`. This conditional implication
does not prove L120(K).

For a normalized X decoder, first adding only its corrected frame rows gives
an epsilon-free representation of C_(X_I) with total weight
`c_normalized+|I|`. Its column span is an eligible S, so the last lower bound
would imply `c_normalized>=64`, hence `c_raw>=64`. This directly supplies the
padding corollary without importing the unresolved global lift claims.
The 256 coordinate-code controls check the extension construction for every
I; they do not enumerate arbitrary S or prove the open floor.

On E the term cost equals w, by section 2. Thus L120(K) is equivalent to a
72 lower bound for all one-sided decoders of this fixed Gram matrix: decoder
columns contain a basis of their span, and conversely any basis of a lift S
expresses every column of C_E. Zero coefficient rows can only lower the
constructed decoder's cost. This equivalence remains conditional evidence
about the named model, not about all possible masked realizations.

## 6. A precise normalization control

Over Q, let u be the all-ones vector on X. In the coordinate decoder replace
the axis-zero term `(C_0,e_0)` by

\[
(C_0+2u,e_0),\quad(-2u,e_0).
\]

Both new columns have full support; their label spans have dimension nine
and both are corrected, so each costs eight. The seven untouched coordinate
terms cost eight each. The raw cost is 72. Merging produces C_0, whose span
W_0 does not contain z_0; it is no longer corrected. The normalized cost is
64 and the padded cost is 72. If merging is skipped but only the first term
receives the f_0 row, the endpoint is still exact, yet the cost is **81**:
both old corrected terms lose one unit of relief and seven new units are
added. Endpoint equality alone would miss this cost failure.

The parent PR3074 audit already compares padded cost with its post-merge
variable c. Its raw-versus-normalized distinction is correct in code. The
new fixture clarifies the prose reference point and exercises loss of a
correction, rather than only duplication of an unchanged corrected column.

## Boundaries

The proof is about the finite fixed geometry, dense B, arbitrary finite term
counts and scalar fields of characteristic not two. It establishes neither
L120 nor a new decoder lower bound, and does not audit PR2816's LP/flat/census
arguments or PR1815's fitting theorem. It gives no native circuit, physical
copy program, recursive cost, selected-frontier admission, full multiplication
theorem or new kappa. Those boundaries are unchanged by finite replay.
