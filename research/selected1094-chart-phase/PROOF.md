# An active subspace does not fix its exact complex residual

Gareth Davidson, with substantial OpenAI Codex assistance. Apache-2.0.
The quadratic-refinement principle is classical; the contribution is its
explicit application, counterexample and source binding at this supplier boundary.

## 1. The inherited operation and the audited implication

The pinned `clifford_exact.py` defines, for a binary displacement `q`,

\[
C_q^{(s)}=\frac{1+s i}{2}I+\frac{1-s i}{2}X_q,
\qquad (X_q f)(x)=f(x+q),\quad s\in\{1,-1\}.
\]

Its `fourier(n, axes)` is the product of these commuting `C` gates on the
named coordinate axes. This is **not the ordinary real Walsh–Hadamard gate**;
the source constructs the latter using additional diagonal gates. The exact
Gaussian phases matter here. The positive sign is the normalized residual in
the inherited wrapper contract. The negative sign is its operator inverse; it
is not an assertion that the complete scalar-backward supplier has a different
helper endpoint. The source uses the same normalization wrappers in both scalar
orientations.

The local normalization hypothesis is inherited: the fully wrapped helper acts
as `C_[w] tensor I` on its nine coordinates. This audit concerns the subsequent
physical coordinate chart. It does not re-prove the scalar word or its wrappers.
The coordinate-operator calculation below holds on complex functions on
`F2^m`; its use in the whole physical cover/compiler retains the source's
realization hypotheses.

The false weakened implication is:

> Two orthogonal charts with the same active subspace/projector implement the
> same normalized complex residual.

The selected production contract is stronger: it binds the literal ordered
pending axes, routes and emitted chart table. It passes this audit.

## 2. Exact kernel and spectator lifting

Let `U` be an `m`-by-`w` binary matrix with `U^t U = I`, with columns `u_j`.
Write `C_U^(s)` for the product of `C_(u_j)^(s)`. Its convolution coefficient at
displacement `U z`, for `z in F2^w`, is

\[
K_U^{(s)}(Uz)=\left(\frac{1+s i}{2}\right)^w
                  (-s i)^{\operatorname{wt}(z)}. \tag{1}
\]

All these coefficients are nonzero, and other displacements have coefficient
zero. Expand the product, selecting the `X` term exactly where `z_j=1`.
Independence of the columns gives a unique subset for each displacement, and
`(1-si)/(1+si)=-si`, proving (1).

For a complete orthogonal chart `Q`, the address permutation `P_Q e_x=e_(Qx)`
satisfies `P_Q X_ej P_Q^-1=X_(Qej)`. Consequently,

\[
P_Q(C_{[w]}^{(s)}\otimes I)P_Q^{-1}=C_{Q[:,0:w]}^{(s)}. \tag{2}
\]

The remaining chart coordinates are unchanged. This holds for every spectator
fiber and arbitrary complex payload by linearity. Neither (1) nor (2) needs a
clean spectator. Translation invariance means a complete kernel fixes every
input column; there is no zero-input-column blind spot **within this convolution
class**. No `2^73`-column numerical replay is claimed.

## 3. Necessary and sufficient phase refinement

Let `S in O(w,2)` and `V=U S`. The two active projectors agree:
`VV^t=U SS^t U^t=UU^t`. Define the binary vector

\[
d_j=\frac{\operatorname{wt}(S^t e_j)-1}{2}\pmod2. \tag{3}
\]

The numerator is even because every row of an orthogonal matrix has odd weight.
For every `z`,

\[
\operatorname{wt}(S^t z)-\operatorname{wt}(z)=2d\cdot z\pmod4. \tag{4}
\]

To prove this, put `q(z)=wt(z) mod4`. Its polarization is
`q(x+y)-q(x)-q(y)=-2(x dot y) mod4`. Orthogonality preserves this polarization
and preserves `q mod2`. Thus `(q(S^t z)-q(z))/2 mod2` is additive and takes the
values (3) on the coordinate basis. This proves (4) for every dimension.

Since `V(S^t z)=Uz`, equations (1) and (4) give

\[
K_V^{(s)}(Uz)=(-1)^{d\cdot z}K_U^{(s)}(Uz). \tag{5}
\]

Therefore `C_V^(s)=C_U^(s)` **if and only if every row of `S` has weight `1 mod4`**.
Necessity uses the nonzero coefficient at `Ue_j` whenever `d_j=1`.
The same criterion holds for both signs. Equivalently, `S^t` must preserve the
`Z/4` weight refinement, not only its binary bilinear form.

More explicitly, with `D_d f(x)=(-1)^(d dot U^t x) f(x)`,

\[
C_V^{(s)}=D_d C_U^{(s)}D_d. \tag{6}
\]

This follows by multiplying each convolution coefficient at `Uz` by the two
endpoint characters. It suggests a possible pair of diagonal repairs, but
this package implements no physical repair and claims no free adapters or
cost improvement. Also, a nonzero defect is not removable by a global scalar:
the nonzero zero-displacement coefficient is unchanged, forcing that scalar
to be one, while a coefficient with `d dot z=1` changes sign.

## 4. Smallest bad rebase and a nonpermutation positive case

In dimension four use `S=I+J`, where `J` is the all-ones matrix. Its columns
are `(14,13,11,7)` in bit-mask notation. It is orthogonal, but each row has
weight three, so `d=15`. It preserves the full active projector and, when
embedded as `diag(S,I_(m-4))`, every spectator column. All support and amplitude
magnitudes are unchanged. Exactly eight of sixteen displacement coefficients
change sign: the coefficient at zero stays `-1/4`, whereas that at the first
original active axis changes from `i/4` to `-i/4`.

Even squaring the operators misses this distinction. Directly `C_q^2=X_q`;
both products square to the same translation, since an orthogonal matrix fixes
the all-ones characteristic vector of the binary dot product.

Dimension six supplies a useful positive control. `I+J` is orthogonal with
row weights five, so it preserves `C` exactly although it is not a permutation.
The criterion does not simply ban all changes of basis.

The complete finite enumeration selects every possible ordered unit-norm,
pairwise-orthogonal column sequence. Pruning a prefix only removes vectors
that cannot be its next orthogonal column. A complete sequence is a basis,
because taking its inner product with any column proves linear independence.
This gives an exhaustive enumeration without a heuristic or random search:

| Dimension | Orthogonal matrices | Exact `C` preservers | Permutations |
|---|---:|---:|---:|
| 1 | 1 | 1 | 1 |
| 2 | 2 | 2 | 2 |
| 3 | 6 | 6 | 6 |
| 4 | 48 | 24 | 24 |
| 5 | 720 | 120 | 120 |
| 6 | 23,040 | 1,440 | 720 |

Literal Gaussian-integer convolution checks (5) for every displacement and
both signs of all 23,817 matrices: 2,996,852 coefficient comparisons. A separate
unpruned tuple enumeration corroborates the complete matrix sets through
dimension four. Thus four is the first failing dimension, and six the first
dimension with a nonpermutation exact preserver, within these completely
enumerated smaller dimensions. The universal criterion itself is proved above.

## 5. Binding to the selected PR1094 replay

The inputs are the current selected replay archive, not the older
`gauge44-slots-t16/evidence/` directories. The complete archive, eight consumed
members, literal owners and reference code are pinned. The hosted decoded
template hash, phase/canonical-word/check hashes and selected REPLAY object
are cross-bound before the mathematical check.

The check covers all 69,120 roles in 144 calls. It binds their actual emitted
routes to the pending ordered slice and spectator coordinates, and reconstructs
the complete chart stream digest. All 10,002 emitted 73-column charts pass all
53,300,658 Gram entries. There are 10,008 `(chart,width)` signatures: the same
complete chart can be used at different active widths, so width is part of
the cache key. For each signature, literal physical convolution, a separate
closed subset formula and chart-transported coordinate convolution agree on
every coefficient in both directions: 5,348,224 comparisons.

Every active width is at least four. The embedded bad rebase has a nonzero
phase witness on each of the 10,008 signatures. The retained concrete example
is stage 0, invocation replica 0, helper 49, physical family 4467, owner replica
4, port 99, child 10, offset 0, width 4. Its original active axes are
`[477,475,478,463]`; the rebased axes are `[458,460,457,472]`. At displacement
477 the coefficient changes from `i/4` to `-i/4`. The example also applies to
the spectator fiber starting at 471. These are binary address masks, not data
values. The complete dirty data can be arbitrary.

`production_check.py` separately executes the **unchanged ASTs** of the pinned
controller's `orthobasis` and `audit` functions and its emitted-chart equality
assertion. The surrounding namespace is explicitly reconstructed from pinned
archive inputs; other top-level obligations are not re-executed. Compilation
uses `optimize=0`, preserving the predecessor's assertions even under `-O`.
The original table passes. A same-projector mutant with a correctly recomputed
chart hash fails the source equality guard, and a wrong spectator route fails
the source route predicate. This is evidence for an existing protection, not
a defect report or a full production-driver replay.
The same companion check also executes the verbatim source `Op.zero_state`
method on only `C` gates: all 64 columns of four six-coordinate circuits, in
both directions (512 columns), agree with the new Gaussian-integer kernels.
This binds the formula to the actual gate semantics without importing the
source compiler or claiming coverage of its other gate types.

Local scalar/native/phase-wrapper replay, chronology beyond that extracted
predicate, cost/precision/tape invoices, compiler/physical realization and
analytic transfer remain inherited. The theorem and finite checks do not
promote a new supplier or change the selected multiplication exponent.
