# Actual paid-site precision sensitivity of the two-full Laurent word

Prepared by Yiyang (@Lyy-iiis), with substantial OpenAI Codex assistance.
SPDX-License-Identifier: Apache-2.0.

This is an exact sufficient census of independent error directions at actual
paid sites. It is not a lower bound for multiplication or for every numerical
implementation. In particular, a coherent reuse or recomputation policy may
correlate errors in ways excluded by the model below.

## Source and claim

The literal source is the current round-three `ACTUAL-WORD.json.gz`, compressed SHA256
`7679daa4ec6a40f56fc7f0202379a6f454310e94945aba4f48beaaaafb838d05`,
at head `1eb8da6cfb35512c0cc2533413e5ca42f48e13c6`, path
`research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz`.
The Git blob is `46d929df83817b85a5387bcdb9745e0627d6366e`.
The current research base `cef4b52f2a59009865bf8eabde1be3f159063703`
contains the identical blob at that path. The earlier public border's
profile citation `0ce1b5c9fb7163d0b2f0ac3db95fc418dbbcec62` also contains
that exact blob at the same path, as checked by the parent source audit.
This checker derives the actual helper and paid profiles from the pinned
round-three word; it does not substitute a profile for the actual
chronology. The round-three source is credited to Cao Yifan and
retains the PR4610 predecessor attribution.

Each orientation contains 21,449 events, including 3,298 paid sites, 240
logical warps, all 408 independently productive helpers, and 16 owned clears.
The two-full Laurent construction uses source-forward for the lower shear
and source-backward for the upper shear. It has 6,596 original paid sites.

At one actual normalized paid Gaussian `G`, allow the independent fault
`G -> (1+eta)G`; every other paid operator remains exact. This is a legitimate
operator-error direction of norm `|eta|`, because `G` is unitary. Retain the
original left/right whole-job normalizers. The scalar multiplier commutes
with these normalizers and therefore multiplies the corresponding logical
register by `1+eta`. This argument also applies to an individual factor of
the exact disjoint-axis split `4=3+1`, `5=3+2`, or `8=3+3+2`.

The finite checker finds 5,639 original sites with a nonzero
`eta/epsilon` coefficient. After splitting, the sufficient profile is

`4060 H1 + 775 H2 + 1131 H3` (5,966 jobs).

Only main outputs are needed for the subprofile

`3608 H1 + 700 H2 + 886 H3` (5,194 jobs).

Unflagged sites are not proved safe. These counts concern sufficient scalar
error directions, not every possible error matrix.

## Why one exact address suffices

The inherited logical warp is the quadratic-phase monomial

`K_G |x> = i^(q_M(Gx)) |Gx>`, where `M=I+G^(-T)G^(-1)` over F2 and

`q_M(y)=sum_i M_ii y_i + 2 sum_(i<j) M_ij y_i y_j (mod 4)`.

There is no constant phase or affine address offset. Thus `G0=0` and
`q_M(0)=0`: the warp, its inverse, transpose and inverse transpose all fix
`delta_0` with phase exactly one. The checker binds every actual signed
warp identifier and checks all 72 binary matrices are invertible. The
definition is inherited from `bw_gauss.py::monomial`; an independent source
audit checks its precise phase convention.

Every ideal paid transition is the identity on the logical state in its
moving canonical frame; it changes the physical frame. Scalar operations
on `delta_0` are exactly their rational scalar instructions. Consequently,
the literal forward program restricted to this address is an exact
633-register rational circuit, including the owned register. Physical
input/output adapters need not fix physical `delta_0`; they are absorbed by
the moving-frame definition. Some identity X-output adapter markers precede
the final climb, and no extra ordering assumption about those markers is
used here.

Setting the original independent helper inputs to zero is allowed when
constructing an adversarial unit-input witness. It does not declare helpers
to be clean resources: the source program, paid transitions and all helper
outputs remain present. The suffix census observes every helper output.

## Exact normalized boundary calculation

Write `Q` for the common central Gaussian, `D_s` for the fresh rank-eight
Gaussian in full call `s`, and `N_(s,i)` for the homogeneous monomial port
chart. All these maps are unitary. `D_1,D_2,Q` commute, and each fresh `D_s`
commutes with the other call's chart. Let `C_c`, `C_A`, and `C_F` denote
the source entrance-X, exit-Y, and full exit-X frame Gaussians.

The retained free wrappers are, in ordinary matrix multiplication order,

```
MX = C_c N Q^-1,        MY = N,
OX = D Q N^-1 C_F^-1,   OY = D N^-1 C_A^-1.
```

Thus normalized physical inputs `(X,Y)` correspond to source logical inputs
`(N Q^-1 X, N Y)`. The source-forward endpoint `(x,y+x)` gives
`D L(Q^-1)`; source-backward `(x-y,y)` gives `D U(-Q)`. Conjugating each
by the sign change `diag(1,-1)` gives the required `D L(-Q^-1)` and
`D U(Q)`. These are retained source charts, not new free Fourier operations.

The full border, read right to left, is

```
S_epsilon D_2 U(Q) D_1 L(-Q^-1) B S_epsilon^-1,
B = [[1,-1],[1,0]],   S_epsilon = diag(1,epsilon).
```

Set original main input `X=0`. In the first call, the coefficient of
`epsilon^-1` has normalized inputs `(-Y,0)`. Choosing port `Y_i=Q delta_0`
makes source logical input `x_i=-delta_0`, all other source inputs zero.
If a fault changes the source logical endpoint by `(dx_i,dy_i)`, its final
unscaled main-X contribution is

`D_2 D_1 Q N_(1,i)^-1 (dx_i-dy_i) / epsilon`.

The lower-call suffix therefore observes source logical `X_i-Y_i` and all
helpers. The factor in front of each main observation is invertible and
unitary, so a nonzero rational scalar remains nonzero with the same norm.

For the second call, the coefficient of `epsilon^-1` has source logical
inputs `x_i=y_i=-N_(2,i) D_1 Q^-1 Y_i`. Choosing
`Y_i=Q D_1^-1 delta_0` makes both equal `-delta_0`. Its unscaled main-X
output is `D_2 Q N_(2,i)^-1 dx_i / epsilon`. Thus the upper-call prefix
sets `X_i=Y_i` and the suffix observes only source logical X and all helpers.
The common initial minus sign is immaterial to a nonzero pole witness.

Each chosen original input has norm one. The same proof holds at every
fiber count by tensoring the address vectors; the rational coefficients
do not depend on the fiber count.

## Exact prefix/suffix census

For a paid site on register `a`, let `p_a` be the row mapping the 112
chosen original-Y inputs to that logical register immediately before the
site. Let `s_a` be the column mapping an injected error on that register
immediately after the site to the selected final observations. The exact
first variation is the outer product `eta s_a p_a / epsilon`.

The checker computes `p_a` by the literal forward scalar program and `s_a`
by its transpose in reverse event order. A `clear a` sets its backward
column to zero. For `copy a=b`, the column of `a` is added to `b` and then
deleted. Thus neither erased data nor arbitrary helper state is silently
reversed. A nonzero row and column give an explicit nonzero matrix entry.
Every recorded witness coefficient has absolute value at least `1/8`.

The split profile is a disjoint accounting of actual split jobs. A scalar
relative error in any one split factor produces the same scalar error in
the whole transport, so its site witness transfers to each split factor.
The receipt retains event indices, owners, full source events, separate
prefix/suffix coefficients, main/helper visibility and the resulting pole.
It additionally compares selected witnesses against independent direct
finite-fault executions at `eta=1/8,-1/4`, and rejects changed source bytes,
a singular warp, removal of the last owned clear, and a Boolean substituted for an actual paid rank integer.

## Conditional precision tariff, and helper rescaling

Fix a uniform output tolerance `tau=2^-k`, and one choice of epsilon for
the whole word. To approximate the declared exact diagonal target, the
ideal border residual already forces `epsilon <= tau/2`. The actual retained
rank-one `cgate` has eigenvalues `1,i`, so `Q_f=Q_1^(tensor f)` has a `-1`
eigenvalue for every `f>=2`; no unrestricted formal-q specialization is
being assumed. For a uniform independent per-site operator tolerance
`|eta_j|<=2^-w_j`, the guarantee must hold for both signs of a fault. Their
output difference is `2 eta_j s_a p_a/epsilon`, whereas the sum of their
allowed errors is at most `2 tau`. This also avoids any possible cancellation
with the ideal border residual. A witness of coefficient at least `1/8` forces

`2^-w_j <= 8 tau epsilon <= 4 tau^2`, hence `w_j >= 2k-2`.

This is a worst-case independent-error guarantee. It is not a claim about
adaptive per-input numerical errors or a correlated implementation.

For pricing, explicitly suppose the raw paid invoice corresponds to
`w_j=k+o(k)` and its leading cost is linear in `w_j`. Under that policy,
each witnessed job needs one additional copy of its leading rank tariff.
Any inherited constant precision inflation or a different cost law must
be analyzed separately; it is not silently equated to this policy.

Charging **only** the 3,608 main-visible rank-one jobs gives:

| Quantity | Rank mass |
|---|---:|
| Target `{4:56,7:14,8:94,9:652,17:224}` | 10,750 |
| Baseline split paid `{1:4656,2:920,3:1386}` | 10,654 |
| Paid after just 3,608 extra H1 charges | 14,262 |

For every concave power `0<=t<=1`, all target ranks are at least four and
all paid ranks at most three. Therefore

`T_t <= 4^(t-1) 10750`, and `P_t >= 3^(t-1) 14262`, so

`T_t/P_t <= (4/3)^(t-1) * 5375/7131 <= 5375/7131 < 1`.

This proves failure of every such moment under the stated precision tariff,
including `C=.0034`, `t=1-C`; no delicate decimal comparison is needed.
It says precisely why the unfunded raw margin, about 28.656 at that C,
cannot absorb this independent-error policy.

Every main-only witness initializes all helper inputs to zero and observes
no helper output. Conjugating the independent helper boundaries by any
nonzero scalar rescalings leaves these witnesses unchanged. Such boundary
rescaling alone cannot repair the stated policy. Internal chart changes
or correlated faults are different premises.

## Scope and next questions

The census leaves open structured correlated errors. In particular, each
source center macro captures an unchanged source `x`, computes the same
deterministic paid map `A(x)`, adds it into other registers, and clears its
owned buffer. Its inverse can recompute the **same** `A(x)`, negate those
additions and clear again, even for a rounded A when the additions are exact.
That fact does not by itself produce the opposite-query/fresh-D interface
required by this Laurent word. It is a concrete route for a separate audit.

Remaining questions are whether a complete implementation supplies the
needed correlated inverse interfaces, whether scalar rounding preserves
the cancellation, and what its actual uniform precision/space invoice is.
The independent-error result does not exclude such a construction. It also
does not establish a new complex or BIT multiplication bound.

The underlying border idea and recovery questions follow Dillon (@dillona),
PR4623 head `fd5d3be12b9d6ee92c8fa089d95bd529c3236563`. The two-full Laurent
identity and strict split invoice are the earlier Yiyang handoff at
`https://github.com/Lyy-iiis/integer-mult-bounds/tree/e0bebf54d8cf8549ead24aef929fc40e44313bc0/research/two-full-laurent-border`.
Native-word and retained-wrapper authorship remains with the pinned source
packages; this contribution adds the source-level error census and its
explicit conditional precision consequence.
