# A defect bound for no-idle rank-two query callers

**Scoped obstruction; no new κ.** This note concerns a normalized,
arbitrary-input caller with nonzero rank-one queries, a fresh coordinate
rank-two stage at each full query, and no idle stage operations. It does not
exclude the idle-bearing caller of CrocSwap/integer-mult-bounds#6833,
noncommuting productive masks, or different native suppliers.

## 1. Model and statement

Work over a field of characteristic different from two. There are `n`
independent productive fields. For `N` query positions, let

\[
R_i=x_i y_i,\quad y_i x_i=0,\quad
T_i(S)=I+(S-1)R_i,\quad S^2=1.
\]

Here `x_i` is a column, `y_i` a row, and each query operator is nonzero rank one.
The complete query word obeys

\[
T_N(S)\cdots T_1(S)=S I_n.\tag{1}
\]

No input is assumed zero; every field is an independent restored productive
input. Put `δ=N−n`. Of these positions, `F` are full native calls. At each full
position there is a fresh commuting formal stage `D_i`, of rank eight in the
priced source, and a coordinate rank-two projector `P_i` with
`P_i R_i=R_i P_i=R_i`. The full call has normalized form

\[
(I+(D_i-1)P_i)T_i(S).
\]

All `P_i` are coordinate projectors in **one common basis**. Their two-element
supports may repeat; `F` counts full occurrences with multiplicity. The other
`q=N−F` positions are thin queries with arbitrary rank-one square-zero operators,
supports, and positions. There are no idle stage calls or other operations
involving the `D_i`. The complete caller must produce independent whole targets
with one `S` and each stage incident to that coordinate appearing once. Thus a
coordinate of full-stage incidence degree `d` has target rank `1+8d`.
These target conditions are hypotheses: (1) alone does not establish a caller.

Ordinary invertible basis controls independent of `S` and all stages can be
absorbed into normalized queries and projectors. If the resulting endpoint is
diagonal in independent formal stages and equals the identity when all stages
and `S` equal one, the product of those controls is the identity. Set `S=1`, set
every stage except `D_i` to one, and compare the coefficient of `D_i−1`: the
absorbed projector is the diagonal incidence projector of that stage in the
target. This explains when the common-coordinate premise follows from a
normalized whole-target contract. It does not justify it for stage-dependent
controls, restricted-input states, quotient targets, or noncommuting outputs.

**Theorem.** Every caller in this class satisfies

\[
F\le 2\delta(\delta+1).\tag{2}
\]

For eighteen native calls with the exact helper/paid profile retained from
CrocSwap/integer-mult-bounds#6833, no caller in this class can reach that
contribution's pending `κ=0.00337180`. Its complete signed moment has one of two
explicit upper envelopes, whose unique crossings in `κ` obey

\[
0.0033288660495<\kappa_3<0.0033288660497,
\]

\[
0.0029312090589<\kappa_{\ge4}<0.0029312090593.
\]

These are upper bounds on this class, not attained constructions or new
multiplication bounds. Section 6 excludes any later positive interval.

## 2. The rank defect of the entire query word

Let `X=[x_1 ... x_N]`, let `Y` have rows `y_i`, and set

\[
G=YX,\qquad A=I_N+2\operatorname{lower}(G),
\]

where `lower` is the strictly lower triangular part. Expanding at `S=−1` gives

\[
(I-2R_N)\cdots(I-2R_1)=I_n-2XA^{-1}Y.\tag{3}
\]

Indeed, with `L=lower(G)`, the finite series `A^{-1}=I−2L+4L²−...` enumerates all
strictly decreasing chains of query indices in the ordered product. Every term
of degree `k` in `−2XA^{-1}Y` has coefficient `(-2)^k` and exactly the factors in
the direct ordered-product expansion.

Equation (1) implies `XA^{-1}Y=I_n`. Thus `Q=A^{-1}YX` is an idempotent of rank
`n`: `Q²=Q`, and `XA^{-1}Y=I_n` makes `X` surjective and `A^{-1}Y` injective.
Consequently

\[
B=A-G=A(I_N-Q),\qquad \operatorname{rank}B=N-n=\delta.\tag{4}
\]

In particular

\[
B_{ii}=1,\qquad B_{ij}=\operatorname{sgn}(i-j)G_{ij}\quad(i\ne j).\tag{5}
\]

This uses **all** positions, including every thin operator. No assumption about
a thin operator's support or commutation was made. Adding arbitrary thin
operators changes `N`, `δ`, and the paid query count; it cannot evade (4).
The unit diagonal implies `δ≥1`. The determinant of (1) also requires even `n`,
but the bounds below do not need this additional restriction.

## 3. The full-support graph

Form a simple graph `H` on the `v` coordinates incident to at least one full
call, with an edge for each distinct full support pair. Parallel occurrences
are discarded **only in this graph**. A nonzero rank-one square-zero operator
cannot live in one coordinate, so each full support really is a pair. Write
`ν` for maximum matching size and `Δ` for maximum degree.

### 3.1 A matching costs rank

Select one full occurrence on each edge of a matching. Their coordinate supports
are disjoint, so every off-diagonal `G_ij` in their principal block vanishes.
By (5) the block of `B` is `I_ν`. Hence

\[
\nu\le\delta.\tag{6}
\]

### 3.2 A star costs at least half its degree

Fix hub `z` with `k` distinct neighbours; select one full query on each incident
pair, in actual temporal order. Distinct supports meet only at `z`. Put
`a_i=x_i[z]`, `c_i=y_i[z]`. Then

\[
G_{ij}=c_i a_j\quad(i\ne j).\tag{7}
\]

The pair `(a_i,c_i)` cannot be `(0,0)`: otherwise both factors would live on the
other coordinate, where `y_i x_i=0` forces a zero operator.

First assume every `σ_i=a_i c_i` is nonzero. Conjugating the principal block of
`B` by `diag(a_i)` gives off-diagonal entries `sgn(i−j) σ_i`. Divide row `i` by
`σ_i` to obtain `C` with off-diagonal entries `sgn(i−j)` and diagonal `1/σ_i`.
Therefore

\[
C+C^T=2\operatorname{diag}(1/\sigma_i),\qquad
k\le2\operatorname{rank}C.
\]

The principal block has rank at least `ceil(k/2)`.

Now allow zeros. An index with `c_i=0` has a unit row in the principal block of
`B`; one with `a_i=0` has a unit column. These sets are disjoint. Simultaneously
permute rows and columns, putting zero-`c` indices first, nonzero-product
indices next, and zero-`a` indices last. The block has shape

\[
\begin{pmatrix}I&0&0\\ *&M&0\\ *&*&I\end{pmatrix}.
\]

With `z_0` zero-product indices, elimination gives rank
`z_0+rank(M)≥z_0+ceil((k−z_0)/2)≥ceil(k/2)`. The nonzero middle block retains its
temporal order and the symmetrization applies. Thus

\[
\Delta\le2\delta.\tag{8}
\]

This degree counts distinct neighbours, not repeated occurrences. No coefficient
alphabet or special hub sign pattern was assumed.

### 3.3 Count parallel occurrences separately

Restrict `A,G,B` to all full positions in increasing order. The principal block
`A_F` is unit lower triangular, so has rank `F`. All selected columns and rows
are supported in the same `v` active coordinates, so `rank(G_F)≤v`. Thus

\[
F=\operatorname{rank}A_F\le\operatorname{rank}B_F+
\operatorname{rank}G_F\le\delta+v.\tag{9}
\]

This step counts every parallel full occurrence.

### 3.4 Maximum matching controls active vertices

Every simple graph without isolated vertices satisfies

\[
v\le\nu(\Delta+1).\tag{10}
\]

To prove it, fix a **maximum**, not merely maximal, matching. Unmatched vertices
form an independent set and each has a neighbour on a matched edge. For a
matched edge `ab`, if both endpoints have unmatched neighbours, their neighbour
sets must be the same singleton: two distinct unmatched neighbours would give
an augmenting path of length three. Otherwise only one endpoint has unmatched
neighbours, at most `Δ−1` of them. For `Δ≥2`, every matched edge consequently
sees at most `Δ−1` distinct unmatched vertices. Summing covers every unmatched
vertex, bounding their number by `ν(Δ−1)`. Add the `2ν` matched vertices.
For `Δ=1`, the graph itself is a matching. The empty graph is immediate.

Combining (6), (8), (9), and (10),

\[
F\le v+\delta\le\nu(\Delta+1)+\delta
\le\delta(2\delta+1)+\delta=2\delta(\delta+1).
\]

Eighteen full calls therefore require `δ≥3`. The necessary bounds `F≤4` at
`δ=1` and `F≤12` at `δ=2` do not assert either bound is attainable.

## 4. The exact eighteen-call price

Parse the literal `HELPERS` and `LOCAL_PAID` dictionaries in byte-pinned
`retained/pricing.py`, without importing it. Their difference at ranks one
through nine is

\[
(d_1,\ldots,d_9)=(-2220,-446,-485,-1,-135,-4,1,39,359).
\]

For `0<t<1`, define

\[
D(t)=\sum_{r=1}^9d_r r^t,\qquad \phi_t(d)=(1+8d)^t-1.
\]

There are eighteen native calls and 104 ports. Every full support contributes
two incidence units, so `sum_v d_v=36`, counting parallel calls each time.
The `n` independent targets and `q=N−18=n+δ−18` thin queries have complete signed
target-minus-paid moment

\[
\begin{aligned}
M(t)&=18D(t)+104\left[\sum_{v=1}^n(1+8d_v)^t-q\right]\\
&=18D(t)+104\left[18-\delta+\sum_{v=1}^n\phi_t(d_v)\right].\tag{11}
\end{aligned}
\]

This includes every native helper, native paid request, main target, and thin
query in the class. Degree-zero coordinates are not omitted: their rank-one
target contribution cancels the corresponding part of the thin-query count.
This is a favorable invoice for an obstruction. Additional paid operations or
nonrecursive implementation overhead cannot repair a negative moment bound.

## 5. Two universal moment envelopes

### 5.1 Defect three

By (6), a maximum matching has at most three edges. Its endpoints form a vertex
cover of size at most six; pad with degree-zero slots if necessary. Let `h` be
the sum of full-occurrence degrees in these slots. Each full edge meets the
cover, including repeated edges, so `18≤h≤36`. Concavity gives

\[
\sum_{\mathrm{cover}}\phi_t(d_v)\le6\phi_t(h/6).
\]

For integral `d≥0`, concavity and `φ_t(0)=0` give `φ_t(d)≤d φ_t(1)`. The other
slots contribute at most `(36−h)φ_t(1)`. The function

\[
f(h)=6\phi_t(h/6)+(36-h)\phi_t(1)
\]

is strictly decreasing for `18≤h≤36`: its derivative is
`φ_t'(h/6)−φ_t(1)<0`, since `h/6≥3` and the derivative of a strictly concave
function there is less than its average derivative on `[0,1]`. Therefore

\[
\sum_v\phi_t(d_v)\le6\phi_t(3)+18\phi_t(1).
\]

Substitute `δ=3` into (11):

\[
M(t)\le E_3(t):=18D(t)+104[6\,25^t+18\,9^t-9].\tag{12}
\]

### 5.2 Every larger defect

For all `δ≥4`, use `sum_v φ_t(d_v)≤36φ_t(1)` and `18−δ≤14` in (11):

\[
M(t)\le E_4(t):=18D(t)+104[36\,9^t-22].\tag{13}
\]

This bounds every larger defect, every number of thin queries, and every number
of unused productive coordinates in the stated class, without a finite cutoff.

## 6. Crossings and no re-entry

The rational interval verifier certifies the crossing brackets in Section 1.
For orientation, proposal values are approximately
`κ_3=0.003328866049597376` and `κ_≥4=0.002931209059061556`. At
`C=0.0033718004755`, it certifies

\[
-7.086<E_3(1-C)<-7.085,\qquad
-67.047<E_4(1-C)<-67.046.
\]

Rational arithmetic encloses these decimals; floating point determines no sign.
The verifier also checks negativity at the pending headline `C=0.00337180`.

Normalize by `9^t` to rule out a later positive interval. On `0≤t≤1`, the
negative-coefficient terms with `r<9` in `D(t)/9^t` have positive derivative.
Keep just the `r=1` positive derivative and bound the two negative derivatives:

\[
\begin{aligned}
\frac{d}{dt}\frac{D(t)}{9^t}
&\ge\frac{2220}{9}\log9-\log(9/7)-39\log(9/8)\\
&\ge\frac{2220\cdot8}{81}-\frac27-\frac{39}{8}
=\frac{323717}{1512}>0.\tag{14}
\end{aligned}
\]

The elementary inequalities are `log x≥(x−1)/x` and `log x≤x−1` for `x≥1`.
This native monotonicity estimate is retained from
CrocSwap/integer-mult-bounds#6839 and recomputed here.

The remaining nonconstant terms of `E_3(t)/9^t` are
`624(25/9)^t−936/9^t`, both increasing. In `E_4(t)/9^t`, the remaining
nonconstant term is `−2288/9^t`, also increasing. Both normalized envelopes are
strictly increasing in `t`, hence decreasing in `κ=1−t`. The unnormalized envelopes at `t=1` equal
552 and 448, and at `t=0` both are negative. Each has exactly one crossing;
neither can become positive after its crossing.

## 7. Prior and concurrent work; limitations

CrocSwap/integer-mult-bounds#6833 supplies the pinned eighteen-call native
profile and the stronger **idle-bearing** pending benchmark. Its native source
is CrocSwap/integer-mult-bounds#6824. The header rank identity in Section 2 is a
rederivation of the query-block defect identity in DreamingOfClouds's
CrocSwap/integer-mult-bounds#6832 (`research/p104-query-block-bound`, head
`99a165a81be808f45c1b6f4b0a809145ac7923d1`). The shortest-header classification in
CrocSwap/integer-mult-bounds#6842 concerns `N=n+1`; this argument treats all
defects but only coordinate rank-two no-idle callers.

The star symmetrization extends scoped rank ideas in
CrocSwap/integer-mult-bounds#6840. New here are arbitrary hub coefficients and
zero-product cases, simple-graph versus occurrence counting, the universal
full-call defect bound, and its complete native invoice consequence.
CrocSwap/integer-mult-bounds#6839 provides a preceding chain-family ceiling and
the native monotonicity estimate. The present family is not restricted to
chains. Pending claims are not treated as admitted selected frontiers.

An algebraic quotient can close a root with fewer fields and one thin query
without contradicting this result. If such a quotient had eighteen nonzero
full queries and `δ=1`, (2) says that its eighteen stage masks could not all be
coordinate rank-two projectors in one independent-target basis under this
model. The compatible productive projectors, not root closure alone, are the
remaining obligation. This is a conditional consequence, not an assertion that
an unfinished quotient proposal is incorrect.

The theorem does not cover idle stage work, higher-rank full masks,
noncoordinate productive output representations, stage-dependent controls,
zero-query native calls, non-rank-one queries, dirty auxiliary fields that are
restored but not independent productive targets, characteristic two, or changed
native prices. Finite matrix/graph controls in `verify.py` test implementation
and boundary cases; the universal statements are proved above, not inferred
from finite tests. No claim about all multiplication algorithms, removal of
inherited framework assumptions, or stronger selected κ follows.
