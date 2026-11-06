# Gaussian rounding cannot retain these tensor identities

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
This is a universal incompatibility theorem under two explicit rounding
hypotheses, with a sharp quantitative witness. It is not a counterexample to
the selected multiplication theorem and makes no claim about its unstated
caller contracts.

## 1. Native transform, rounding hypotheses and conclusion

Let `G=Z[i]`, let `n>=1`, and put `N=2^n`. Use the exact native transform

\[
 M=\frac{(1+i)I+(1-i)X}{2}
   =\frac12\begin{pmatrix}1+i&1-i\\1-i&1+i\end{pmatrix},
 \qquad U=M^{\otimes n}.
\]

The coordinate order is the binary order on `n` bits. `M`, and hence `U`,
is unitary. Let \(F:G^N\to G^N\) be **any** map satisfying:

* **Global unit covariance:** \(F(\zeta z)=\zeta F(z)\) for all `z` and
  \(\zeta\in\{1,-1,i,-i\}\).
* **Exactness on integral ideal images:** whenever \(Uz\in G^N\),
  \(F(z)=Uz\).

No bijection, inverse, error bound, sum preservation, affine period,
finite table, locality, computational complexity or exact-square assumption
is imposed. Global unit covariance does not mean independently chosen
coordinate phases. Exactness is required on the full displayed set of inputs,
not merely on zero or a sampled set.

For an `N x N` Gaussian array, let `R_F` apply this same `F` independently to
each row, in the fixed coordinate order, and let `C_F` apply it independently
to each column. The ideal row and column actions commute because one is
right multiplication by \(U^T\) and the other is left multiplication by `U`.
The superscript `T` here is ordinary transpose, not complex conjugation.

**Theorem.** There is an explicit Gaussian-unit column \(\lambda\in G^N\)
and Gaussian integer \(\alpha=(1-i)^n\) such that, for every \(z\in G^N\),

\[
 \boxed{\quad
 (R_FC_F-C_FR_F)(\lambda z^T)
   =e_0\,[\alpha(Uz-Fz)]^T.
 \quad}                                                    \tag{1}
\]

The subtraction means the difference of the two evaluated arrays; neither
`F` nor the difference operator is assumed linear. In particular

\[
 \|(R_FC_F-C_FR_F)(\lambda z^T)\|_F
   =\sqrt N\,\|Uz-Fz\|_2.                                 \tag{2}
\]

At the fixed input \(X_0=\lambda e_0^T\), every coordinate in the first row
of the difference is nonzero, every other row is zero, and

\[
 \boxed{\quad
 \|(R_FC_F-C_FR_F)(X_0)\|_F\ge\sqrt N.
 \quad}                                                    \tag{3}
\]

Thus `R_F` and `C_F` cannot commute. The constant in (3) is sharp for the
stated broad class of maps. The attainment example below is nonbijective;
Section 6 proves the sharper bound forced by a nonzero basis image, including
sharp attainment within conservative bijections when no uniform error bound
is required.

## 2. The denominator and unit column

Set

\[
 \alpha=(1-i)^n,\qquad
 \lambda_r=(-i)^n i^{\operatorname{wt}(r)}.
\]

Since \((1-i)(1+i)=2\), the native tensor coefficients are

\[
 \alpha U_{rs}=(-i)^{\operatorname{wt}(r\mathbin{\mathrm{xor}}s)}.
                                                               \tag{4}
\]

Every entry of `alpha U` is a Gaussian unit, and every entry of `lambda`
is a Gaussian unit. Also \(|\alpha|^2=2^n=N\), so `alpha` is a nonunit
for `n>=1`.

We have

\[
 U\lambda=\alpha e_0,\qquad \lambda=\alpha U^{-1}e_0.           \tag{5}
\]

One derivation uses unitarity: the entries of \(U^{-1}e_0\) are
\(i^{\operatorname{wt}(r)}/\bar\alpha\), and
\(\alpha/\bar\alpha=(-i)^n\). An independent direct derivation factors
the sum in \((\alpha U\lambda)_r\) over the bits of `r`. For a zero bit,
the factor is \(1+(-i)i=2\); for a one bit it is \(-i+i=0\). Therefore

\[
 \alpha U\lambda=(-i)^n2^n e_0=\alpha^2 e_0,
\]

which proves (5) without a numerical inverse or a finite dimension cutoff.

Equations (4) and (5) imply that, for every Gaussian scalar `t` and vector
`z`, both \(U(\lambda t)=\alpha t e_0\) and \(U(\alpha z)\) are
Gaussian-integral. The exactness hypothesis applies to these actual inputs.
It is not necessary to assume that `F` commutes with general Gaussian scalars.
Indeed the proof uses integral-image exactness only on the two explicit
families `lambda G` and `alpha G^N`; exactness on all integral ideal images
is a convenient sufficient hypothesis.

## 3. Evaluate the two orders exactly

Take \(X=\lambda z^T\). Its `j`th column is \(\lambda z_j\), whose
ideal image is \(\alpha z_j e_0\). Integral-image exactness gives

\[
 C_F(X)=e_0(\alpha z)^T.
\]

Also `F(0)=0` by exactness at zero. Applying `F` to the rows, and then using
exactness again because \(U(\alpha z)\) is integral, yields

\[
 R_FC_F(X)=e_0 F(\alpha z)^T=e_0(\alpha Uz)^T.               \tag{6}
\]

In the other order, each row of `X` is \(\lambda_r z\), and each
`lambda_r` is a **global** Gaussian unit for that row. Covariance gives

\[
 R_F(X)=\lambda(Fz)^T.
\]

Its columns are again Gaussian scalar multiples of `lambda`, so exactness
applies independently to each column:

\[
 C_FR_F(X)=e_0(\alpha Fz)^T.                                \tag{7}
\]

Subtracting (7) from (6) proves (1). Exactly one row can be nonzero, and
\(|\alpha|=\sqrt N\), proving (2).

If the two orders commuted on all arrays, equation (1) would force `Fz=Uz`
for every Gaussian input. This is already impossible on `e0`: each entry of
`Ue0` is a Gaussian unit divided by the nonunit `alpha`. The next section
makes the failure quantitative on a single fixed array, rather than relying
only on this contradiction.

## 4. Every first-row coordinate has an integer gap

For `z=e0`, the `r`th first-row difference is

\[
 \alpha(Ue_0)_r-\alpha F(e_0)_r
   =(-i)^{\operatorname{wt}(r)}-\alpha F(e_0)_r.              \tag{8}
\]

The first term is a unit of `G`; the second belongs to the proper principal
ideal `(alpha)`. They cannot be equal, because a nonunit cannot divide a
unit. Their difference is a nonzero Gaussian integer, so its complex absolute
value is at least one. There are `N` such entries. This proves (3) and the
assertion that all first-row coordinates differ.

An equivalent argument uses the ideal column norm: zero is a nearest
Gaussian-grid point to `Ue0`, and \(\|Ue_0\|_2=1\), so every Gaussian
output is at distance at least one; substitute into (2). The Gaussian-integer
argument in (8) avoids treating a finite numerical distance check as a proof.

At a uniform grid spacing `h>0`, define \(F_h(hz)=hF(z)\). The witness is
`h X0`, its Frobenius norm is `h sqrt(N)`, and the lower bound is likewise
`h sqrt(N)`. This is a scale statement, not a precision/tape cost estimate.

## 5. Sharpness and nonempty hypotheses

For a real number `x`, let `r(x)` be nearest-integer rounding, with an exact
half-integer tie sent to the even integer. Then `r(-x)=-r(x)` and `r(k)=k`
for every integer `k`. Apply this rounding independently to real and imaginary
parts of each coordinate of `Uz`:

\[
 F_*(z)_j=r(\Re(Uz)_j)+i\,r(\Im(Uz)_j).
\]

This is a total Gaussian-integer map. Coordinate rounding commutes with global
multiplication by `i`, because that multiplication swaps the two components
and negates one; oddness of `r` handles the sign. It therefore commutes with
all four Gaussian units. It also fixes every already integral ideal image.
Thus the hypothesis class is nonempty.

For `n=1`, the two coordinates of `Ue0` are `(1+i)/2` and `(1-i)/2`, and
ties-to-even sends all four real components to zero. For `n>=2`, each complex
coordinate has magnitude \(2^{-n/2}\le1/2\), so every real and imaginary
component lies in `[-1/2,1/2]` and also rounds to zero. Consequently
`F_*(e0)=0`. Substituting in (1) gives a first row consisting entirely of the
units in (4), with squared Frobenius norm exactly `N`.

This proves sharpness of (3). In fact the example has the ordinary uniform
rounding bound \(\|F_*(z)-Uz\|_2\le\sqrt{N/2}\); the theorem does not
need that bound. Since \(F_*(e_0)=F_*(0)=0\), this example is not bijective,
and it does not preserve the sum of the coordinates. Neither property is
part of the theorem's hypotheses or of the sharpness claim.

## 6. Sharp stronger bound for nonzero basis images

Suppose additionally that `F(e0) != 0`. This follows either from injectivity,
since `F(0)=0`, or from preservation of the complex coordinate sum, since
that sum equals one on `e0`. Define

\[
 m=2^{-\lceil n/2\rceil}.
\]

Every real and imaginary component of `u=Ue0` has absolute value at most `m`.
To see both the bound and its attainment without trigonometry, write `n=2k`
or `n=2k+1`. For the coordinate
\(j_*=2^k-1\), which has weight `k`, equation (4) gives

\[
 u_{j_*}=\begin{cases}2^{-k},&n=2k,\\
                     (1+i)2^{-(k+1)},&n=2k+1.
        \end{cases}
\]

All other entries differ by Gaussian unit factors, so
\(\Re u_{j_*}=m\) and the component bound holds globally.

For any nonzero Gaussian-integer vector `w`, let
\(\ell=\sum_r(|\Re w_r|+|\Im w_r|)\). Integer squares dominate integer
absolute values, giving \(\|w\|_2^2\ge\ell\ge1\). Moreover
\(\Re\langle u,w\rangle\le m\ell\). Since `u` has norm one and
`m<=1/2`,

\[
 \|u-w\|_2^2
 =1+\|w\|_2^2-2\Re\langle u,w\rangle
 \ge1+(1-2m)\ell\ge2-2m.
\]

Apply this with `w=F(e0)` in (2). The strengthened witness bound is

\[
 \boxed{\quad
 \|(R_FC_F-C_FR_F)(X_0)\|_F^2
 \ge N(2-2m)=2N-2^{\lfloor n/2\rfloor+1}.
 \quad}                                                    \tag{9}
\]

It equals the broad-class squared bound `N` for `n=1,2` and is strictly
larger for `n>=3`.

### Attainment even with a conservative bijection

The bound in (9) is sharp within maps that are simultaneously bijective,
global-unit-covariant, exact on integral ideal images, and sum-preserving,
when no uniform approximation bound is required. Here is an explicit total
map establishing that precise claim.

Let \(L_U=\{z\in G^N:Uz\in G^N\}\). The identity `M²=X` gives
`U²=J`, where `J` complements all `n` bits, and `U⁴=I`. If `z` is in
`L_U`, then `Uz` is integral and `U(Uz)=Jz` is integral; hence `Uz` is in
`L_U`. Thus `U` is a bijection of `L_U` onto itself. The lattice is also
stable under global Gaussian units. Every unit-coordinate vector `zeta e_j`
lies outside `L_U`, by the nonunit denominator in (4).

Define `F_sharp` to be `U` on `L_U`. On its complement, swap the two full
Gaussian-unit orbits of `e0` and `e_(j*)`, and fix every other vector. When
`j*=0`, this means the identity on the complement. The two parts are
disjoint invariant sets, so this is a bijection. It is globally unit-covariant
because both the linear restriction and the complete orbit swap are so.
Integral-image exactness holds by definition. The matrix `M`, hence `U`,
has column sums one. The swapped vectors `zeta e0` and `zeta e_(j*)` also
have the same sum, so `F_sharp` preserves the complex coordinate sum.

Finally `F_sharp(e0)=e_(j*)`. Its squared error at `e0` is exactly
`2-2 Re(u_(j*))=2-2m`; equation (2) proves equality in (9). Thus there is
no missing bijection or sum obligation in this sharpness statement.

This attaining map is **not a uniformly accurate approximation** to `U`.
For example, `z_t=e0+alpha t e0` remains outside `L_U` for integer `t`:
`alpha t e0` lies in `L_U` and `e0` does not. For sufficiently large `t` it
is outside the swapped finite orbits, so `F_sharp(z_t)=z_t`. The error
contains the nonzero linear term `alpha t(e0-Ue0)` and is unbounded. It also
fails the exact native square on `e0`: the complement swap squares to the
identity, whereas `J e0 != e0` for `n>=1`. This piecewise construction does
not establish attainment under an additional uniform approximation bound or exact native square. The separate
[four-axis certificate](https://github.com/CubeJerry/integer-mult-bounds/blob/6ea7d0886e62d6c0f53aa90ae8691dbcc61ea04a/research/four-axis-exact-square-grid/PROOF.md) now establishes both at `n=4`: it has `F(e0)=e3`, sharp uniform
error `sqrt(8) h`, native square `F²=J`, and fixed-witness squared discrepancy
24. Its source and certificate are pinned in `SOURCES.json`; that companion
result is context for the remaining question, not a premise of this all-`n`
theorem. Other dimensions and additional caller contracts are not settled
here, and fixed-witness sharpness is not a worst-case discrepancy optimum.

## 7. Hypothesis and scope boundaries

The dimension restriction is real: for `n=0`, `N=1`, `alpha=1`, and `U=I`;
exactness forces `F=I`, and row/column actions commute. The positive bounds
use the nonunit denominator and do not apply when `n=0`.

For the fixed witness `X0`, the proof only needs covariance on the unit orbit
of `e0` and exactness on `lambda Z[i]` and the single input `alpha e0`. The
all-input identity (1) retains the larger families in Section 2.

If integral-image exactness is dropped, `F=I` is a Gaussian-valued,
global-unit-covariant commuting map. It fails exactness on `lambda` for
`n>=1`. If the integer-output requirement is dropped, the ideal linear map
`U` itself commutes on rational Gaussian arrays. These are concrete controls
for two material boundaries of the statement.

Coordinatewise floor rounding preserves integral ideal images but fails
global-unit covariance. The verifier checks that failure explicitly. It is
not offered as a commuting construction after relaxing covariance; necessity
of covariance in every possible alternative theorem has not been proved.

This theorem concerns the same deterministic state-free map applied to each
row and column with a fixed ordering. Shared carry state, additional retained
coordinates, distinct row and column maps, altered lattices, approximate
commutation, or a relaxation of integral-image exactness are outside the
stated contract. Their feasibility or cost is not settled by this result.
Likewise exact same-block identities such as `F²=J` do not imply row/column
commutation and are not contradicted here.

## 8. Relation to earlier work and verification

Ali Romman's CrocSwap/integer-mult-bounds#6509,
`research/conservative-gaussian-rounding/PROOF.md` at head
`a4173e810c4d34a1d13b9745af123ad0ec6cfed5`, gives a concrete four-coordinate
noncommutation example in **Limits of the invariant**, as well as scoped
restrictions on other rounding families. The present contribution is a
universal implication from the two explicit hypotheses for every `n>=1`,
with an exact rank-one witness formula and a sharp quantitative defect. It
does not assume every earlier rounder satisfies those hypotheses; that must be
checked at each actual caller.

The proof is self-contained and depends on no pending construction, finite
lookup table, search result or unmerged Git object. `verify.py` builds `U`
from the original two-by-two tensor matrix using exact rational Gaussian
arithmetic, separately checks the coefficient/denominator formulas for
`n=0..6`, and checks both complete nonlinear fiber orders on twelve fixtures
for `n=1..4`, plus one signed fixture at scale `2^257` (258 component bits). It also checks 84 global-unit
cases, 56 integral-image cases, both sharp witness families for `n=1..6`,
literal inverses, phase and sum for the piecewise conservative bijection, and seven hypothesis/phase
controls in ordinary and optimized Python modes. These bounded checks support
the algebra; Sections 2–6 supply the quantifiers over all dimensions and all
inputs. No finite search is presented as an impossibility proof.

The selected multiplier's five inherited assumptions are unchanged. Before
using this obstruction to diagnose any supplier, identify where its exact
caller actually requires all three interfaces: global Gaussian-unit
covariance, exactness on every integral ideal image, and independent
row/column commutation. **No new κ; no selected-theorem counterexample.**
