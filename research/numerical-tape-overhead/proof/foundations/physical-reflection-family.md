# A finite reflection family for constant-tail interchange repair

## 2. Half-angle involutions on occupied address pairs

Let `Q_j` exchange the two disjoint fields `H_j,N_j`, for `j=1,...,m`.
Use their ordinary numeric order to define pointwise diagonal operators

\[
 Z_j(d)=\begin{cases}1&H_j<N_j,\\-1&H_j>N_j,\\0&H_j=N_j,\end{cases}
 \qquad E_j(d)=\mathbf1_{H_j=N_j}.
\]

On a two-element orbit, in smaller/larger address order, `Q_j=X` and
`Z_j=diag(1,-1)`. On a fixed point, `Q_j=E_j=1` and `Z_j=0`.
Different indices act on disjoint fields.

Fix a finite depth `h>=0`. Over `Z[1/2]`, adjoin a primitive
`2^(h+2)`-th root `zeta`, put `i=zeta^(2^h)`, and, for `0<=t<=h`, set

\[
 \zeta_t=\zeta^{2^{h-t}},\qquad
 a_t={\zeta_t-\zeta_t^{-1}\over2i},\qquad
 b_t={\zeta_t+\zeta_t^{-1}\over2},\qquad
 R_{t,j}=a_tQ_j+b_tZ_j+(1-a_t)E_j.                 \tag{RF1}
\]

The trigonometric names `a_t=sin(pi/2^(t+1))` and
`b_t=cos(pi/2^(t+1))` describe one complex embedding, but no analytic
approximation is used. These are identities in a finite free cyclotomic
ring and specialize to any odd characteristic. They satisfy, with the
half-angle identities taken for `0<=t<h`,

\[
 a_t^2+b_t^2=1,\quad
 a_t=2a_{t+1}b_{t+1},\quad
 b_t=b_{t+1}^2-a_{t+1}^2.                         \tag{RF2}
\]

In particular `R_{0,j}=Q_j`, and every `R_{t,j}` is an involution.
The fixed-point correction in (RF1) is essential. On a two-element orbit,
direct multiplication of the matrices
`[[b_t,a_t],[a_t,-b_t]]` gives

\[
 R_{t+1,j}R_{t,j}R_{t+1,j}=Z_j+E_j.              \tag{RF3}
\]

The same equality holds on fixed points because all three factors are
the identity there. Put

\[
 F_t=\prod_{j=1}^m R_{t,j},\qquad S_t=F_{t+1}
 \quad(0\le t<h).
\]

The factors with different indices commute, so `S_t^-1=S_t`, and `S_t`
simultaneously diagonalizes all `R_{t,j}`. At an ordinary address its sign
tuple is `(-1)^k_j=Z_j+E_j`; equivalently `k_j=1` exactly when `H_j>N_j`.
Thus the **forward and inverse spectral conversions for `F_t` are both
`F_{t+1}`**. The table depends on the same orientation sign tuple at every
level. All sign tuples are realizable whenever every field has two values.

This is finite family closure, not an assertion that a swap is its own
diagonalizer. The last member `F_h` will be evaluated directly.

## 3. The source physical pencil implements every family member

Suppose the source label geometry implements a pencil of `m` swaps with
at most `R(m)` recursive field-swap calls per independent input stream.
For fixed row matrices `A_j`, the family pencil splits exactly as

\[
 A_0+\sum_j A_jR_{t,j}
 =\left(A_0+a_t\sum_j A_jQ_j\right)
  +\sum_j A_j\bigl(b_tZ_j+(1-a_t)E_j\bigr).      \tag{RF4}
\]

The first summand is precisely a source shared pencil. The second is a
pointwise map in the **original physical layout**. Evaluate it separately
from retained input copies and add it to the shared-pencil output. No
address-dependent matrix is moved through a source endpoint map.

For completeness, these are actual linear-volume scans for fixed
parameters, including arbitrary spectators. Fix a prefix immediately before
`N_j`. Its controlled field `H_j` is known. The `N_j`-and-suffix fiber has
three consecutive runs, for `N_j<H_j`, equality, and `N_j>H_j`. Preparing
their lengths costs a fixed polynomial in `f+log S+1`, where `S` is the
suffix range, and the complete `b_addr^f S`-position fiber pays for that
work. Nested counters advance and reset amortized linearly. This is exactly
the comparison implementation proved in the source swap-spectrum paragraph.
Apply it for each of the fixed `m` indices and perform the fixed finite row
matrix on its indicated runs. All extra work is `C_m V`; it uses `C_m V`
visited cells with a constant depending on the finite program, not `f`.

Consequently every family pencil has the **same recursive-call bound
`R(m)`**, although its nonrecursive scan constant can be larger. We keep
that constant in the physical invoice; it is not declared uniform in `m`.

## 4. A constant-tail integral predictor at every level

Take all binary shifts with equal multiplicity. At any fixed sign tuple,
the count `c=|k xor beta|` has the `Bin(m,1/2)` distribution over the rows.
For `m>=4` choose

\[
 B=\lceil\sqrt{2m}\rceil,\qquad
 u=\lfloor m/2-B\rfloor,\qquad v=\lceil m/2+B\rceil .
\]

The tail is at most `2 exp(-4)<1/16`. The integral count-predictor lemma
represents parity correctly on this window by a polynomial in the
**individual involutions** of degree

\[
 D_{\rm pred}=v-u\le2\sqrt{2m}+3.
\]

Use the source matrix-root representation, with `b_pred` the least power
of two at least `max(2,D_pred)`. It takes `b_pred` pencil stages per
predictor application and has a common power-of-two row dimension after
zero padding. Let `R` be the resulting number of rows over all shifts;
duplicate if necessary so `16|R`. Use the inflated defect budget `s=R/16`.
The Hermite repair is valid because the actual exceptional set is contained
in the outside-window rows. It uses four predictor applications and two
sequential conversion phases of `2s=R/8` rows each.

This is not ordinary count evaluation modulo the data prime. The generating
function construction retains individual query variables and has dyadic
coefficients. No division by `D_pred!` is introduced. Thus the count-aliasing
obstruction for rational Newton evaluation does not apply to this predictor.
Its large matrix-root dimension is still paid.

Fix a single power-of-two cyclotomic extension containing the predictor
coefficients, all `R` Vandermonde nodes with pairwise unit differences, and
the roots in (RF1). After specialization it is a finite free
`F_p`-algebra `E`. Every level uses this same algebra. For the chosen depth
below, the source node extension already contains the half-angle roots
because `R>=2^m>=2^(h+2)` for sufficiently large `m`.

The diagonal sign tuple and all predictor eigenvalues are independent of
`t`. Therefore the same exceptional sets, Vandermonde maps, and Hermite
tables serve every `F_t`. Only the pencils and their spectral conversions
change according to (RF4) and (RF3).

## 5. Finite contraction with changing targets

Let the routing label set have size `N_lab` and set `W_0=R N_lab`.
For a fixed total depth `h`, run on

\[
 W_h=W_0\,8^h
\]

independent `E`-valued streams, arranged as `8^h` copies of the labeled
base batch. At level `t`, invoke the repair for `F_t`. Collect pending check
rows **within each label**, across the batch copies. Their count is exactly
one eighth of the current rows at that label. They therefore form the
required smaller number of full labeled batches for the `F_(t+1)` program.
Return the rows to their original repair batches before processing the
spectral tables. Perform the second phase in the same way after those
tables have actually been computed. All regroupings are fixed finite row
permutations implemented by splitting, copying and merging streams.

At level `h`, apply `F_h` directly. Each factor `R_(h,j)` needs one copied
`Q_j` swap followed by the pointwise combination in (RF1), so the leaf bill
is exactly at most `m` recursive field-swap calls per input stream.

**Finite-family contraction theorem.** Let

\[
 a_m=4b_{\rm pred}R(m).
\]

There is an exact finite physical program computing `F_0=prod_j Q_j` on
`W_h` independent streams, with at most

\[
 {\sigma_h\over W_h}
 \le a_m\sum_{d=0}^{h-1}4^{-d}+m4^{-h}
 \le {4\over3}a_m+m4^{-h}                       \tag{RF5}
\]

recursive field-swap calls per stream, and with all remaining work linear
in input volume for these fixed parameters.

**Proof.** All target programs are exact on arbitrary inputs in the same
algebra. At a nonleaf node use its four routed predictor applications and
the two recursively supplied `F_(t+1)` conversion phases. These are the
correct forward and inverse conversions by (RF3). The Hermite identity
therefore returns `F_t` on every independent row. Correlations among the
check rows do not alter an identity valid on arbitrary inputs. The label
regrouping preserves the source routing contract.

At depth `d` there are `2^d` program nodes, each with `8^-d` of the root
row mass. Internal non-spectral calls thus sum to
`a_m W_h sum_(d<h) 4^-d`; the leaves cost `m W_h 4^-h`. Each volume-linear
nonrecursive operation satisfies the same mass ledger, with its largest
finite coefficient over `t<=h`. Calls occur in the stated dependency order.
The recursion terminates at the explicitly supplied leaf program. This
proves correctness and (RF5). No self-referential same-size recurrence or
empty input padding is used. QED.

Choose `h=ceil((log2 m)/4)`. Then

\[
 W_h\le8W_0m^{3/4},\qquad
 {\sigma_h\over W_h}=O\!\left(\sqrt m\,(R(m)+1)\right). \tag{RF6}
\]

The constants in this call estimate are absolute once the explicit source
pencil invoice is fixed. The physical scan constants may depend on the
whole expanded finite template.

## 6. Physical space, full rate, and the spatial recurrence

During the finite family computation, a child conversion phase has one
eighth of the parent's data volume. Park the other live streams, run the
first child, restore and process its outputs, then run the second child.
The parked data volumes sum to at most `8V/7`, times the base program's
finite workspace coefficient. The source's physical row splits and merges
implement the finite regroupings. Siblings reuse the same marked work
regions. This is a fixed-parameter linear visited-cell bound, including
the original input copy retained for (RF4).

The alphabet throughout all spatial recursion can be the same finite
algebra `E`. The complete main computation is `F_0`, a permutation with
base-field coefficients. Thus, if one expands a whole completed program
in an `F_p` basis of `E`, every basis component carries its own independent
input and receives its own swapped output. This statement uses the
correctness on arbitrary `E`-valued inputs. It does **not** assert that an
intermediate `F_t` acts componentwise over `F_p`, nor descend or enlarge the
scalar algebra separately at each family level. Encoding `E` by binary
blocks must still pay its dimension and all fixed scalar arithmetic.

Let `a_route=D_route-2`. In the source spatial descent choose the address
radix prime above `W_h` and all required address-map units. The first digit
then supplies full labeled batches, with each stream's volume at most
`2V/W_h`. The finite-family main computation makes `sigma_h` single-stream
calls on width-`f` fields. After merging and clearing its workspace, the
source's `2a_route` full-volume reserve interchanges remain. Therefore

\[
 T(e)\le C_{\rm template}
   +\left(2\sigma_h/W_h+2a_{\rm route}\right)T(f),
 \qquad f=\left\lfloor{e-1\over m+2a_{\rm route}}\right\rfloor . \tag{RF7}
\]

The existing depth-first spatial schedule still applies: main calls shrink
volume, while full-volume reserve calls occur only after the main workspaces
have been cleared and retain just descriptors. No additional full-volume
data stack is hidden in the changing targets.

For the source's fixed data prime `p` and `q` the least power of two at
least `m^(1/p^2)`, its explicit label bounds give

\[
 R(m)=O_p\!\left(m^{(3p-1)/p^2}(1+\log m)^{p^2}\right).
\]

Thus (RF7) has a main bill

\[
 O_p\!\left(m^{1/2+(3p-1)/p^2}(1+\log m)^{p^2}\right),
\]

removing the factor `sqrt(log m)` from the same label family's original
main estimate. The source's reserve term and rank/rectangle dependence are
unchanged. For every fixed exponent above `1/2`, the source's choice of a
sufficiently large `p` and then `m` still gives a strict spatial contraction.
This rederives that fixed-exponent result with a different finite main
program; it is not a stronger asymptotic multiplication theorem by itself.
