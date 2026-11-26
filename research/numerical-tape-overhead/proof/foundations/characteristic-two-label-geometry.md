# Power-of-two distance labels in characteristic two

Status: **proved enabling geometry; no complete interchange algorithm**.
This makes the source shared-swap pencil available over characteristic two
with an adjustable distance parameter. A low-rank spatial correction still
needs a physical implementation before it can supply a full interchange.

The geometry is a generalization of the November source's two-level
distance labels, not a transfer of its odd-characteristic scalar matrix.
Source pin: OpenAI `math@3344da59991ed94f9ba711217b29c1d760badfa6`, tape
`build/interchange.tex`. B derived the characteristic-two construction
independently after discovering the degree-filtration truncation bound;
the session lead independently developed a stronger exact residual-rank
identity. Their spatial correction question remains shared and open.

## 1. An indicator for distance zero or a power of two

Let `d=2^r>=2`, `h=2d-1`, `q=2^t>=2`, and `U=[q]^h`, of size `n0=q^h`.
Over `F_2`, for Boolean variables `delta_1,...,delta_h`, define

\[
 B_d(\delta)=\sum_{s=0}^{d-1}e_s(\delta_1,\ldots,\delta_h). \tag{C2-1}
\]

Here `e_s` is the elementary symmetric polynomial. If exactly `c` variables
are one, its value is `sum_(s<d) binom(c,s) mod 2`. In `F_2[T]`,

\[
 (1+T)^c=\prod_{a:\,\operatorname{bit}_a(c)=1}(1+T^{2^a}).
\]

The sum of coefficients of degrees below `d` is one exactly when the low
`r` bits of `c` all vanish. Since `0<=c<=2d-1`,

\[
 B_d(\delta)=1\quad\Longleftrightarrow\quad c\in\{0,d\}. \tag{C2-2}
\]

This has degree `d-1` in the individual indicators. It is not a polynomial
of the residue `c mod 2`; keeping the individual variables is essential.

For `u,v in U`, put `delta_j=1_{u_j!=v_j}` and let `P0(u,v)=B_d(delta)`.
Thus `P0` marks equal pairs and pairs at distance `d`. Each monomial on
`s` coordinate indicators is a tensor product of `s` inequality matrices
and `h-s` all-ones matrices, so its rank is at most `q^s`. Set

\[
 C_0=\sum_{s=0}^{d-1}\binom hs=2^{h-1}=2^{2d-2}.
\]

Then

\[
 \operatorname{rank}_{\mathbb F_2}P_0\le C_0q^{d-1},
 \qquad {\operatorname{rank}P_0\over n_0}
            \le\min\{1,C_0q^{-d}\}.                 \tag{C2-3}
\]

## 2. The two-level scalar transfer matrix

Let `V=U^h`, with `N=q^(h^2)` labels. The outer coordinate inequality
indicators are `Delta_i=1_{v_i!=w_i}`. Define entrywise

\[
 P_*(v,w)=\left(\prod_{i=1}^hP_0(v_i,w_i)\right)B_d(\Delta).
                                                               \tag{C2-4}
\]

Its support consists exactly of the diagonal and the pairs differing in
`d` outer positions, each of whose inner words is at distance `d`.
Expand the second factor into its `C0` monomials. A term involving at most
`d-1` outer coordinates retains at least `h-(d-1)=d` copies of `P0` in
its tensor factorization. Other coordinates have rank at most `n0`.
Therefore, with `r_*` the rank over `F_2`,

\[
 {r_*\over N}\le C_0\left(\min\{1,C_0q^{-d}\}\right)^d
       \le C_rq^{-d^2},\qquad C_r=C_0^{d+1}=2^{2d^2-2}. \tag{C2-5}
\]

This factorization continues to hold over every commutative
characteristic-two algebra by using its `F_2` matrix factors. No eigenbasis
or division by two is needed for the shared pencil itself.

## 3. Rectangles and rational address coordinates

Use exactly the source directed-rectangle construction, replacing the
distance parameter `p` by `d`. For a far inner pair, choose its `d`
differing coordinates and its common letters elsewhere. At the first
differing coordinate fix the ordered distinct letters. In each of the
remaining `d-1` differing coordinates, use the first-differing-bit partition
of distinct `t`-bit labels. Each label belongs to exactly `t` such directed
rectangles on a prescribed side.

The resulting inner incidence per word is at most
`binom(h,d)(q-1)t^(d-1)`. Two words on the same side can vary in only
`d-1` positions, so cannot be far. At the outer level choose the `d`
differing positions, fix all other inner words, and take the product of
the selected inner rectangles. The support remains disjoint, and each
outer label has incidence at most

\[
 \lambda\le\binom hd^{d+1}(q-1)^d t^{d(d-1)}.          \tag{C2-6}
\]

Let `k(v,w)` count far inner-coordinate pairs. Across every rectangle
`k=d`; within either side `k=0`. Build the rational Gram blocks

\[
 G_{vw}=(1-k(v,w)/d)I_2+(k(v,w)/d)
                  \begin{pmatrix}0&1\\1&0\end{pmatrix}. \tag{C2-7}
\]

The quotient by the radical has dimension

\[
 2\le D_{\rm route}\le2+hq^h.                          \tag{C2-8}
\]

Indeed the constant block has rank at most two; `k` is a sum of `h`
matrices factoring through one `n0`-valued inner coordinate, and the
nonconstant two-by-two factor has rank one. Its diagonal blocks are `I2`,
so every endpoint still supplies an orthonormal pair. The source rectangle
endpoint proof uses precisely the Gram values at `k=0,d`, hence applies
without change. Address arithmetic is rational; choose an odd prime radix
avoiding its denominators and required units. Characteristic two governs
only data symbols, not these address coordinates.

Consequently the physical source layout construction implements

\[
 A_0+\sum_{j=1}^m A_jQ_j
\]

on independent data streams over a fixed finite characteristic-two algebra,
with at most

\[
 O\!\left(D_{\rm route}(1+\lambda)(1+mr_*/N)\right)      \tag{C2-9}
\]

recursive field-swap calls per input stream and fixed-parameter
linear-volume scans. In characteristic two the subtraction of rectangle
contributions is addition; the exact scalar identity remains
`I=P_* - sum_(L,K) 1_K 1_L^T`. Endpoint cancellation still refers to the
same logical common address. All matrix factors are computed over `F2`.

The odd-characteristic semisimple repair theorem is **not** invoked here.
The conclusion is the pencil interface, not the completed swap product.

## 4. Uniform parameter growth

For `m>=2`, choose `q` as the least power of two with
`q^(d^2)>=Cr m`. If `u=log2 m`, then

\[
 t\le3+u/d^2,\qquad mr_*/N\le1.
\]

Equations (C2-6)--(C2-8), including their constants, imply

\[
 \log_2\bigl(D_{\rm route}(1+\lambda)\bigr)
 \le (3d-1)t+d(d-1)\log_2t+O(d^2).                     \tag{C2-10}
\]

Choose a power of two `d` between `x` and `2x`, where
`x=(u/log2(u+2))^(1/3)`, once `x>=2`. Then

\[
 R_{\rm pencil}(m)
   \le2^{O(u^{2/3}(\log(u+2))^{1/3})},\qquad
 N\le m^{4+o(1)},\qquad D_{\rm route}=m^{o(1)}.          \tag{C2-11}
\]

All constants are absolute. This matches the qualitative shared-call
geometry of the source odd-prime family, now over characteristic two.
The finite scalar module and the missing repair remain uncharged by
(C2-11); they cannot be replaced by one in a global time recurrence.

## 5. Verification and a separate completion

Route C independently reviewed Sections 1--4 against the source and accepted
the stated shared-pencil interface; see [REVIEW-B-CHAR2-LABELS.md](https://github.com/CubeJerry/integer-mult-bounds/blob/a2a17b61d943676c757e0bbfaef3f4fae03ab8e5/research/moonshot-overhead-program/routes/C/REVIEW-B-CHAR2-LABELS.md).
The subsequent [verify_characteristic_two_labels.py](https://github.com/CubeJerry/integer-mult-bounds/blob/a2a17b61d943676c757e0bbfaef3f4fae03ab8e5/research/moonshot-overhead-program/routes/B/verify_characteristic_two_labels.py) checks 508 exact count
selectors, four inner matrix ranks, and the complete directed-rectangle
partition for `d=2,q=4`: 864 rectangles cover 1728 far ordered pairs exactly
once, with maximum incidence 18 as predicted. For the full outer
`d=2,q=2` graph it computes rank 64 on 512 labels and verifies `P_*^2=0`.
Results are in `characteristic-two-label-verification.json`.

The new companion [characteristic-two-order-three-interchange.md](characteristic-two-order-three-interchange.md) supplies
a different repair completion, using exact order-three gates over `F4` and
finite batch contraction. It avoids the unresolved physical application of
a spatial low-rank error. That companion has its own proof and verifier;
the geometry theorem alone does not imply its conclusion.
