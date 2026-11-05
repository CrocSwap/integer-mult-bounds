# An explicit all-rank majorant for the fixed-height raw-p7 flow

This is a scoped analytic theorem about the exact scalar recurrence of
`research/direct-mixed-flow/flow.py`, with its original default height and
the historical raw-p7 inventories below. It makes the upper-bound onset in
`research/direct-flow-exponent-gate/PROOF.md` effective. It is not a new
integer-multiplication exponent, a physical supplier, or a discharge of any
of the selected result's five framework assumptions.

## 1. Statement and exact source

Use the literal inventories

```text
P = {1:37305, 2:10695, 3:3360, 4:1530, 5:300,
     8:1464, 16:448, 32:448, 48:448},
T = {5:420, 6:270, 7:840, 8:1395, 9:3195,
     25:448, 41:448, 57:448, 121:224}.
```

Put `m=121`, `a=log(5)`, and let `P(s)` and `T(s)` denote the corresponding
power sums. For every integer `N>=121`, use exactly
`Flow(T,P,N).merged()`, with `extra_height=0` and the default `height_base=5`.
Write its complete source histogram as `c_z` and complete exit histogram as
`d_e`, retaining every multiplicity and every unmatched boundary exit. Define

```text
C_N = sum_z c_z,
L(0) = 0,       L(n) = n for 1 <= n < 121,
L(N) = [sum_z c_z L(N-z) + sum_e d_e L(e)] / C_N  for N >= 121.
```

The source is finite and `C_N>0`. Every source satisfies
`N/121 < z <= N`; every exit satisfies `1 <= e <= 48N/121 < N`. Thus the
recurrence is well-defined by strong induction. These facts concern the
actual default-height flow, not a modified terminal cutoff.

**Theorem.** Set

```text
s = 99739/100000,
n_LLT = 2^(10^12),
G_0 = 2*n_LLT + 2,
N_0 = 121 * 5^G_0.
```

Then the exact scalar recurrence above satisfies the explicit all-rank bound

```text
L(n) <= N_0^(1-s) * n^s        for every integer n >= 1.
```

The threshold is deliberately enormous. Its role is to replace an
existential onset and unspecified initial-range constant by explicit
expressions. None of these enormous integers or their associated flows
needs to be materialized to check this proof.

The source identities used below are the complete mirror decomposition and
finite conservation identity in the pinned predecessor
`research/direct-flow-exponent-gate/PROOF.md`, sections 2 and 4, themselves
derived from the exact flow of zxv's #4436 and the mirror argument of
Ryanson Jonathan / pinterbanget's #4459. Their finite source-reading checks
are inherited, not claimed as a new independent operator audit here.
Section 2 below states the decomposition precisely so that the analytic
application is reviewable. The probability estimate is supplied and proved
separately in [LOCAL_LIMIT.md](LOCAL_LIMIT.md).

## 2. Tilted law and the exact finite decomposition

Let `alpha` be the unique solution of `P'(alpha)/P(alpha)=a`. Define

```text
A = P(alpha),       D = T(alpha),       J = A-D,       q = D/A,
Pr(X=log r) = P_r*r^alpha/A,
Pr(Y=log k) = T_k*k^alpha/D,
sigma^2 = Var(X),   c_sigma = sigma*sqrt(2*pi),   tau = s-alpha.
```

All copies of `X` and `Y` below are independent. The exact interval checks
for this package establish the following conservative inequalities:

```text
0 < alpha < 1,       a < 2,             log(121) < 5,
2 < sigma^2 < 5/2,   c_sigma < 4,
0 < q < 247/250,     0 < J < 2000,
tau > 3/400,        P(s)/121^s < 2000.
```

The bound for `c_sigma` follows also from `sigma^2<5/2` and `pi<16/5`.
All numerical premises here and the strict margin in section 3 are
certified by outward rational intervals; diagnostic floating values are
not acceptance gates.

For a fixed integer `N>=121`, put

```text
G = floor(log_5(N/121)),
B = log(N/121) = G*a + delta,       0 <= delta < a.
```

`Flow` uses the integer cap `floor(N/121)`. Since every product considered
by the flow is an integer, its cap test is exactly equivalent to comparison
with `exp(B)=N/121`; no approximation to the floor is made here.

The complete finite mirror decomposition is as follows. Ordered target and
paid words carry the product of their letter multiplicities; equal products
are combined by adding those multiplicities.

* Root sources have ranks `k*z` for every allowed product `z` of `G` target
  letters with `z<=exp(B)`, with the corresponding target-word multiplicity
  multiplied by `T_k`.
* Leaf exits have ranks `r*z` for every allowed product `z` of `G` paid
  letters with `z<=exp(B)`, with multiplicity multiplied by `P_r`. Every
  terminal `r` is retained: the terminal leaf rank is not capped again.
* For each `h=0,...,G-1`, take a common base with `h` target letters and
  `G-1-h` paid letters. If its product is `z`, each pair `(r,k)` has rank
  `rkz` and multiplicity equal to the base multiplicity times `P_r T_k`.
  It is an inner source when `rz<=exp(B)<kz`, a boundary exit when
  `kz<=exp(B)<rz`, and otherwise is matched or absent.

This preserves the chronological layer index and all multiplicities. With
`u=B-log z`, the source window is exactly `[log r,log k)` when `k>r`,
and the boundary window is exactly `[log k,log r)` when `r>k`. The endpoint
conventions are important at finite ranks and are retained throughout.

For the `h`th mixed layer set

```text
ell = G-1-h,
u_h = B - sum_(i=1)^ell X_i - sum_(j=1)^h Y_j.
```

For leaves set `u_leaf=B-sum_(i=1)^G X_i`. Undoing the tilt multiplies a
mixed base probability by `A^(G-1) q^h exp(-alpha*B) exp(alpha*u_h)`;
for a leaf base the factor is `A^G exp(-alpha*B) exp(alpha*u_leaf)`.

## 3. A positive finite capacity margin is enough

Define the dimensionless finite capacity margin

```text
D_N(s) = sum_z c_z [1-(1-z/N)^s] - sum_e d_e (e/N)^s.
```

The normalized child power is

```text
H_N(s) = [sum_z c_z (1-z/N)^s + sum_e d_e (e/N)^s] / C_N
       = 1-D_N(s)/C_N.
```

Thus `D_N(s)>0` is exactly the inequality needed for the power majorant.
There is no need to estimate the source count or divide two approximate
limits. Root-source capacity is nonnegative because every source fits in
its parent; discarding it gives a valid lower bound for `D_N`.

For each pair use the nonnegative kernels

```text
f^+_(r,k)(u) = exp(alpha*u) [1-(1-(rk/121)exp(-u))^s],
    log r <= u < log k,                         when k>r;

f^-_(r,k)(u) = (rk/121)^s exp(-tau*u),
    log k <= u < log r,                         when r>k.
```

Each is zero off its stated window. Let

```text
f(u) = sum_(k>r) P_r T_k f^+_(r,k)(u)
     - sum_(r>k) P_r T_k f^-_(r,k)(u),
g(u) = exp(-tau*u) 1_(u>=0),
F_G = A^G exp(-alpha*B) / (J*c_sigma*sqrt(G)),
B_leaf = J*P(s)/121^s < 4*10^6.
```

For `G>0`, the exact decomposition gives

```text
D_N/F_G >= (1-q) sum_(h=0)^(G-1) q^h
                   [c_sigma*sqrt(G) E f(u_h)]
            - B_leaf [c_sigma*sqrt(G) E g(u_leaf)].       (1)
```

The inequality in (1) discards only the nonnegative root capacity; every
boundary and leaf exit remains charged.

Write

```text
M = integral_R f(u) du,
D_full = M - B_leaf/tau.
```

This `D_full` is exactly `K(s)-V(s)` from the predecessor's section 6:
the source kernels give `K(s)`, the negative mixed kernels give its
boundary-exit integral, and `B_leaf/tau` is its full leaf-exit integral.
At `s=99739/100000`, the exact positive-binomial capacity calculation with
its proved positive tail gives

```text
D_full > 40000.                                             (2)
```

This is the only numerical limiting-margin decision needed below.

## 4. An interval bound transfers to the kernels without a mesh

For `0<s<1`, put `Q_s(x)=1-(1-x)^s` on `[0,1]`. It is convex, vanishes
at zero, and satisfies `x Q_s'(x)>=Q_s(x)` for `0<x<1`. Inside a source
window, with `x=(rk/121)exp(-u)`,

```text
d/du [exp(alpha*u) Q_s(x)]
    = exp(alpha*u) [alpha Q_s(x)-x Q_s'(x)] <= 0.
```

The inequality uses `alpha<1`. The kernel extends continuously to a window
endpoint with `x=1`, even though its derivative there can be unbounded.
Every source kernel and every boundary kernel is therefore nonnegative,
continuous and decreasing on its own window. Each window has length less
than 5, lies in `[0,5)`, and has left-end value at most 121.

If a signed measure differs from Lebesgue measure by at most `d` on every
subinterval of such a window, integration against a decreasing continuous
kernel `v` differs by at most `d*v(left)`. Indeed write the integral as
`v(right)` times the whole-window mass plus the Stieltjes integral of
initial-subinterval masses against `-dv`. This remains valid at the
endpoint singularity and for atomic probability measures. The half-open
window convention is used in those initial intervals.

Consequently the error for the complete signed kernel `f` is at most `Q*d`,
where the following integer is a deliberately loose bound on its total
weighted left-end values:

```text
Q = 121*(sum_r P_r)*(sum_k T_k)
  = 121*55998*7688
  = 52092027504.
```

Also `sup |f|<=Q` and `|M|<=5Q`. Cancellation between different windows is
never assumed in these estimates.

## 5. The effective local bound and the first 3001 mixed layers

[LOCAL_LIMIT.md](LOCAL_LIMIT.md) proves, for

```text
epsilon = 10^-8,
Z_ell = sum_(i=1)^ell (X_i-a),
```

that for every integer `ell>=n_LLT`, every interval with left endpoint `x`
and length `0<=b<=5000`, and every choice of open or closed endpoints,

```text
|c_sigma*sqrt(ell) Pr(Z_ell in I)
       - b exp(-x^2/(2*sigma^2*ell))| <= epsilon.          (3)
```

It is a uniform finite-length estimate, not an asymptotic statement with
an unspecified threshold. Reflection or an atom exactly on a cap does not
require changing (3).

Assume henceforth `G>=G_0`. In particular `G>=10^18`. Set `H=3000` and
first consider `0<=h<=H`. Then `ell=G-1-h>=G-H-1>=G/2` and
`ell>=n_LLT`. Conditional on the target sum,

```text
u_h = v-Z_ell,
v = (h+1)a + delta - sum_(j=1)^h Y_j.
```

Because `a<=Y_j<5` and `0<=delta<a<2`, one has `-5h<=v<4`.
For any subinterval of a mixed window, reflection therefore gives an
interval in `Z_ell` with length `b<=5` and left endpoint of absolute value
at most 15010. Put `R=15010` and `rho=sqrt(G/ell)<=2`. From (3),
`1-exp(-w)<=w`, `sigma^2>2`, and
`rho-1<=(G-ell)/ell`, the interval discrepancy after scaling by
`c_sigma*sqrt(G)` is at most

```text
rho*epsilon + b*(rho-1) + rho*b*R^2/(4*ell)
 <= 2*epsilon + [30010+5*15010^2]/G
 < 2*epsilon + 2*10^9/G
 < 3*10^-8.                                               (4)
```

The estimate is uniform in the conditional target sum and in `delta`, so
it survives averaging over that sum. Section 4 gives

```text
|c_sigma*sqrt(G) E f(u_h) - M| < Q*3*10^-8 < 1563.         (5)
```

Multiplication by `(1-q)q^h` and summation over `h<=H` cannot increase
this error, since those nonnegative weights sum to at most one.

## 6. Every later mixed layer remains accounted for

For `H<h<=floor(G/2)`, we have `ell>=G/2-1>=n_LLT` and
`sqrt(G/ell)<=2`. On any mixed window (3) bounds the scaled probability
mass by `2*(5+epsilon)<12`. Thus

```text
|c_sigma*sqrt(G) E f(u_h)| <= 12Q.
```

The omitted part of the infinite geometric weighting of `M` has magnitude
at most `5Q q^(H+1)`. Together, the middle finite layers and this limiting
tail cost at most

```text
17Q q^(H+1) < 17Q exp(-36) < 17Q/10^15 < 1/1000.         (6)
```

Here `q<1-3/250` gives `q^v<=exp(-3v/250)`. The elementary integer check
`(8/3)^36>10^15`, together with `exp(1)>8/3`, proves the displayed
exponential estimate; no tiny floating number is used.

For `h>floor(G/2)`, the paid sum can have fewer than `n_LLT` letters or
even zero letters. No local-limit estimate is invoked there. The trivial
bound `sup|f|<=Q` and `c_sigma<4` give, after summing all their weights,

```text
tail <= 4Q sqrt(G) q^(G/2)
     <= 4Q G exp(-3G/500)
     <= 8Q / [(3/500)^2 G]
     < 1.                                                (7)
```

The penultimate step uses `exp(x)>=x^2/2`; the last is an exact rational
comparison at `G>=10^18`. Thus even the no-paid-letter end layer is covered.

Combining (5)--(7), the full mixed sum in (1) differs from `M` by less
than `1563+1/1000+1`.

## 7. The leaf half-line, including its entire tail

For leaves `ell=G` and `u_leaf=delta-Z_G`. On any subinterval of
`[0,5000)`, reflection has interval length at most 5000 and left endpoint
of absolute value below 5002. Therefore (3) and `sigma^2>2` give discrepancy
from Lebesgue measure at most

```text
epsilon + 5000*5002^2/(4G) < 5*10^-8.                    (8)
```

The function `exp(-tau*u)` is decreasing and has left-end value one.
Stieltjes integration as in section 4 bounds the error of its integral on
`[0,5000)` by the same quantity. After multiplication by `B_leaf<4*10^6`,
this contributes less than `1/5`.

For the remaining half-line partition into intervals
`[5000+j,5001+j)`, `j>=0`. Their scaled probabilities are at most
`1+epsilon<2` by (3), uniformly in location. Hence

```text
c_sigma*sqrt(G) E[exp(-tau*u_leaf) 1_(u_leaf>=5000)]
    <= 2 exp(-5000*tau)/(1-exp(-tau)) < 3*10^-14.         (9)
```

Indeed `tau>3/400` implies `5000*tau>37.5`, and
`exp(-37.5)<10^-16`: use `exp(1)>163/60` and the exact integer comparison
`(163/60)^37>10^16`. Also

```text
1-exp(-tau) >= tau/(1+tau) > 3/403.
```

The Lebesgue tail is bounded separately:

```text
integral_5000^infinity exp(-tau*u) du
    = exp(-5000*tau)/tau < 2*10^-14.                    (10)
```

Thus the total leaf error, comparing with the *whole* limiting integral
`1/tau`, is less than

```text
B_leaf * (5*10^-8 + 5*10^-14) < 1/5 + 2*10^-7.          (11)
```

The terminal paid rank was already summed in `P(s)`; (9) is a log-base
tail bound and does not truncate terminal ranks.

## 8. Uniform onset and an explicit initial-range constant

Combining (1), (2), (5)--(7), and (11), for every integer `N` with
`G>=G_0`, uniformly in its actual offset `delta`,

```text
D_N/F_G > D_full - 1600 > 38400 > 0.
```

Since `F_G>0` and `C_N>0`, this proves `H_N(s)<1`. The condition
`G>=G_0` holds for every integer `N>=N_0=121*5^G_0`, not merely a
subsequence of ranks or a favorable offset.

It remains to make the strong-induction constant explicit. At exponent one,
the exact finite conservation identity is

```text
sum_z c_z z - sum_e d_e e
    = [T(1)-P(1)] U_N(1)
    = 608 U_N(1) > 0,
```

where `U_N(1)` is the positive complete unit-column moment. Indeed
`P(1)=131115` and `T(1)=131723`. Therefore the complete recurrence sends the
test function `n` to at most `n`. Starting from its prescribed base values,
strong induction gives `L(n)<=n` for every `n>=0`.

For `1<=n<N_0`, this implies

```text
L(n) <= n <= N_0^(1-s) n^s.
```

For `n>=N_0`, all nonzero children are smaller than `n`. Assuming the
claimed bound at those children and using `L(0)=0`, the exact recurrence
gives

```text
L(n) <= N_0^(1-s) n^s H_n(s) <= N_0^(1-s) n^s.
```

This finishes the proof without evaluating any initial-rank flow below
`N_0`. It supplies a sufficient threshold, not the first successful rank
and not a practical cost estimate.

## 9. Scope, dependencies, and credit

The predecessor establishes the exact scalar recurrence and its limiting
exponent `s_*` in `(0.99738855928,0.99738855931)`. The result here retains
its already-proved upper exponent `0.99739`; its contribution is the explicit
all-rank onset and majorant constant. It neither improves `s_*` nor changes
the source height, source matching, boundary exits or terminal leaf rule.

The finite identities and strict complement margin are inherited at exact
source pins and checked where declared by this package. The new universal
argument is the quantitative local-limit estimate, its finite-layer/tail
propagation above, and the explicit initial-range bound. Finite controls
corroborate these calculations; they are not a substitute for the written
analytic proof, independent human acceptance or proof-kernel verification.

The historical raw-p7 law is not the currently selected P104 supplier.
The selected conditional `kappa=0.003125804`, its admitted BIT budget, and its
five framework assumptions are unchanged. No physical native, ownership,
precision/tape, compiler-cost or integer-recovery claim follows from this
scalar recurrence theorem.

Credit zxv (#4436/#4483), Ryanson Jonathan / pinterbanget (#4459 and the
mirror-flow lineage), DLamdata (#6118), Nick Petalas (#6125/#6128), the
full-flow exponent contribution prepared for @CubeJerry, Cinna Davis /
1337isnot1337 and the historical p7 controller, Jacob Alan Sussman's
lockstep compiler, and the retained native/precision/analytic contributors.
The Fourier approximation used in LOCAL_LIMIT.md retains its classical
Selberg/Beurling/Vaaler attribution. This successor proof was prepared for
@alephnan with substantial OpenAI Codex assistance, including separate
derivation and adversarial review. Apache-2.0.
