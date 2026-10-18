# Independent audit: alternating scale-dependent full moments

This audit covers only the abstract recurrence in the predecessor's Theorem 1
and its unqualified Cesaro conclusion. Predecessor: philippeVV, expXB
`single-letter/README.md`, exact head
`ed21d6245f8ce1a62e21205be7bedc24271dd772`. The source snapshot is preserved in
the trial run directory. This independent audit was prepared with GPT-6.1 Sol
assistance; it imports neither the predecessor's code nor this package's main
verifier. It does not certify supplier feasibility or a multiplication bound.

## Exact model and conclusion

Take `T(x)=sum_r (H[r]/W) T(rx/m)`, with `T(x)=1` for `x<=1` and zero toll.
Both profiles have `m=256`, `W=1`, positive integer coefficients, and full
histograms

```
A: H[16]=1, H[1]=2;   p_A=1/4.
B: H[16]=4, H[1]=32;  p_B=3/4.
```

The root identities are exact: `1/2+2/4=1` and `4/8+32/64=1`.
At `x=16^i`, select A when i is odd, B when i is even. Writing `T_i=T(16^i)`
gives

```
T_i = T_(i-1) + 2 T_(i-2)       (i odd),
T_i = 4 T_(i-1) + 32 T_(i-2)   (i even),
T_i = 1                        (i <= 0).
```

Thus `T_0,...,T_5 = 1,3,44,50,1608,1708`. The ordered two-level transfer is

```
[T_(2k)  ]   [36  8] [T_(2k-2)]
[T_(2k-1)] = [ 1  2] [T_(2k-3)].
```

Its characteristic polynomial is `lambda^2-38 lambda+64`. Its positive dominant
root is `lambda_+=19+3 sqrt(33)` and its other root is
`lambda_-=19-3 sqrt(33)`, with `1<lambda_-<2<36<lambda_+<37`.
The matrix has positive eigenvector `(lambda_+-2,1)`, and the boundary vector
`(T_0,T_-1)=(1,1)` has a nonzero positive dominant component. More explicitly,

```
T_(2k) = A lambda_+^k + B lambda_-^k,
A = (44-lambda_-)/(lambda_+-lambda_-) > 0,
B = (lambda_+-44)/(lambda_+-lambda_-).
```

The odd subsequence obeys the same second-order equation, starting with 3,50,
and also has positive dominant coefficient. Consequently, for all grid indices,

```
T(16^i) = Theta((16^i)^p_eff),
p_eff = log_256(19+3 sqrt(33)),
5/8 < p_eff < 2/3.
```

The lower exponent bound follows from `lambda_+>32=256^(5/8)`; the upper follows
from `lambda_+<37` and `37^3<256^2`. In particular `p_eff>1/2`, although the
arithmetic and equal-log-cell averages of the seed roots both equal `1/2`.
This is an all-depth written counterexample to dropping the error term.

The grid rule can, if needed, be extended to every real `x>1`: use the parity
of `ceil(log_16 x)`. Division by 16 or 256 decreases this integer by 1 or 2
exactly, so the same `T_i` is constant on each cell
`16^(i-1)<x<=16^i`. Thus the same exponent applies off-grid as well; the
log-integral of this piecewise-constant root is `(1/2) log x+O(1)`.

## Sharp two-phase moment equation

Put `t=16^-p` and seek positive phase amplitudes `c_E,c_O` in
`T_i ~ c_(i mod 2) 16^(pi)`. The recurrence requires

```
c_E = 32 t^2 c_E + 4 t c_O,
c_O = t c_E + 2 t^2 c_O.
```

Hence the sharp phase moment condition is

```
rho([[32t^2,4t],[t,2t^2]]) = 1,
(1-32t^2)(1-2t^2)-4t^2 = 1-38t^2+64t^4 = 0.
```

The positive-amplitude branch has `t^2=1/lambda_+<1/32`. The other algebraic
root gives no positive amplitude vector. At the proposed averaged `p=1/2`,
`t=1/4`; the phase moment matrix has determinant zero and Perron value `17/8`,
strictly above 1. This retains each rank's destination phase and multiplicity.

## Relation to the predecessor's error-qualified theorem

The predecessor states
`log T(x)=log Phi(x)+E(x)`, retaining an oscillation contribution
`sum_j L_max,j omega_j`. This audit does not refute that displayed comparison.
For the piecewise-constant alternating extension, each profile's maximum jump
is `2 log 16`, and the root oscillation in a full level window is `1/2`.
The worst chain can take rank 16 at every step, giving linearly many windows.
The stated oscillation allowance is therefore of order `log x`, not `o(log x)`.
Indeed along `x=256^k`,

```
log T(x) - (1/2) log x
  = (p_eff-1/2) log x + O(1),
```

which is positive and linear in `log x`. With `a=1-p`, the exact corollary
identity `a_eff=bar a-E/log x` is harmless; identifying the limiting saving
with `bar a` requires an additional sublinear-error hypothesis. This audit does
not independently establish the full general error theorem, its additive-toll
term, or the predecessor's separate summability claim.

## What remains true for a finite catalogue

Here is a weaker all-parameter comparison theorem, independent of Cesaro
averaging. Let a finite catalogue have positive coefficients `c_(s,j)`
(positive rationals suffice), ratios
`0<delta<=q_(s,j)<=rho<1`, and zero toll. Let each root `p_s>=0` solve
`M_s(p_s)=sum_j c_(s,j) q_(s,j)^p_s=1`, and take boundary `T=1` for `x<=1`.
For any scale-dependent seed choice, even if different nodes may choose
different seeds, put `alpha=min_s p_s`, `beta=max_s p_s`. Then

```
x^alpha <= T(x) <= delta^-beta x^beta    (x>1).
```

Proof: the recursion tree is finite since every child contracts by at most rho.
Every terminal argument y lies in `(delta,1]`. At exponent alpha the outgoing
tilted mass `sum_j c q^alpha` at every internal node is at least 1. Summing over
the finite tree gives terminal tilted mass at least 1. Since
`T(x)=x^alpha sum_leaves (product c q^alpha) y^-alpha` and `y^-alpha>=1`, the
lower bound follows. At beta each outgoing tilted mass is at most 1 and
`y^-beta<=delta^-beta`, proving the upper bound. This is the complete induction,
including the boundary overshoot cost.

Equivalently, for any `P>=beta`, the power `C x^P` with
`C=delta^-P` is a common supersolution on all reachable arguments `x>=delta`:
the internal inequality is precisely `M_s(P)<=1` and the boundary inequality
is `1<=C y^P` for `delta<=y<=1`. For any chosen single seed s, applying both
bounds with `alpha=beta=p_s` yields `T_s(x)=Theta(x^p_s)`. Thus no unconstrained
mixture in this finite catalogue beats the best fixed seed's growth exponent
`alpha`; that narrower conclusion survives without the false averaging law.
It does not determine the exponent of an arbitrary mixture between the extrema.

The restriction `p_s>=0` can be dropped if the lower constant is replaced by
`min(1,delta^-alpha)` and the upper constant by `max(1,delta^-beta)`.
No integrality assumption beyond positivity is used in the proof. Positive
rational coefficients need not correspond to a physically implementable seed.

This theorem excludes overheads, seed-construction cost, approximation/precision,
restoration, stock, layouts, source access, stateful feasibility constraints and
bit/complex assembly. Nonnegative overheads preserve the lower bound but can
invalidate the upper bound and any attained runtime claim. Infinite/growing
catalogues without uniform ratio bounds need a new argument. Tensor-product
single-letterisation is another obligation and is not checked here.

## Independent finite evidence

Run `python3 -I -B research/scale-dependent-seed-moment-audit/independent.py`.
Only integer and Fraction arithmetic is used, with a separate integer-square-root
enclosure for the algebraic root. The replay enumerates every binary rank history
for the periodic schedule through index 20, and every schedule of length 0..9
with every binary rank history in each schedule. Histories retain their exact
multiplicity products; no rank is discarded or replaced by its mean. It also
checks the two-step recurrence through index 120 and the catalogue bounds on
every enumerated schedule.

Three semantic controls deliberately remove rank 1, reverse the phase, or replace
the recurrence by the averaged-root power. Each differs from the correct replay
at an explicit early value. Reversing the phase has the same asymptotic eigenvalue
because AB and BA share eigenvalues, so its detection relies on exact boundary
values and matrix order, not a claimed exponent difference.

These are finite exhaustive checks at the stated limits. The matrix argument and
finite-tree comparison above are written all-depth proofs. No formal-kernel proof
or new kappa claim is supplied.

## Final cross-review of PROOF.md and verify.py

Verdict: the displayed mathematical claims pass this bounded independent
cross-review. Both `verify.py` and `independent.py` were rerun successfully.

The continuous scale-cell map is correct: for every real `x>0` and integer d,
`ceil(log_16(x/16^d))=ceil(log_16 x)-d`, including endpoints. The periodic grid
solution therefore gives the claimed all-real-scale exponent up to constant
factors. The positive eigenvector sandwich is also correct: with
`w=(lambda-2,1)`, `w/(lambda-2)<=(1,1)<=w`, positivity of P gives the stated
even-coordinate bounds; its second coordinate or the next odd recurrence gives
the same exponent on odd indices.

The added unit-toll claim holds at every depth. The lower bound `u_i>=t_i`
follows by positivity. If every child satisfies
`u_j<=(3t_j-1)/2` and the selected profile has coefficient sum S, then

```
u_i <= (3t_i-S)/2+1 = (3t_i-1)/2+(3-S)/2 <= (3t_i-1)/2,
```

because `S=3` for A and `S=36` for B; the base case has equality. This proves
the claimed constant-factor comparison without an asymptotic toll estimate.

The finite-catalogue comparison correctly allows node-wise seed choices,
requires positive coefficients and nonnegative scalar roots, and obtains
uniform positive lower/upper child-ratio bounds from finiteness. Its terminal
overshoot factor is retained. The theorem concerns the zero-toll recurrence;
only the lower bound is extended to arbitrary nonnegative extra work.

PROOF.md correctly scopes the finding to the unqualified Cesaro implication and
explicitly retains the predecessor's error-qualified Theorem 1 as unaudited.
The all-depth arguments and finite replay remain distinguished. The verifier reports `homogeneous_cases=240` across two 120-index fixtures
and `homogeneous_max_index=120`; the maximum checked index in each
homogeneous fixture is 120.
