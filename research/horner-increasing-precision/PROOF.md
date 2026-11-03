# Increasing-precision fixed-source Horner evaluation

This scoped written theorem and construction were produced by Nick Petalas.
The fixed-source inverse evaluator and disk-grid contract are Hanson Sun's
[PR1430](https://github.com/CrocSwap/integer-mult-bounds/pull/1430).
Variable-precision iteration, Horner evaluation and geometric error damping
are classical. The new step is the explicit schedule and precision-volume
improvement under that rounded-oracle interface.

## Statement and changed premise

Use the maximum complex-coordinate norm. Let E be a complex linear map with
norm at most c=21/50. Let D_q consist of complex vectors with coordinates in
2^-q Z[i] and norm at most one. For each integer q>=101, suppose an oracle
T_q:D_q -> D_q satisfies

    ||T_q(z)-Ez|| < (q/3) 2^-q, for every z in D_q.

No linearity, homogeneity, oddness, consistency between precisions or
correlation of oracle errors is assumed. Supplying this whole oracle family
is an additional premise compared with access to only one fixed T_p.

For any integer p>=102 and u in D_p, set

    q_j = max(101,j+3),                       j=0,...,p-1,
    v_j = componentwise inward rounding of u/2 to grid 2^-q_j,
    y_0 = v_0,
    y_j = v_j - T_(q_j)(y_(j-1)),            j=1,...,p-1.
    w = componentwise inward rounding of y_(p-1) to grid 2^-p.

Coarser dyadic values embed exactly in every finer grid. The subtraction
is exact on that grid. Every oracle input and every y_j belongs to D_(q_j).
The final output w belongs to D_p and obeys

    ||w - (I+E)^(-1)u/2||
      < [25(2p+13)/96 + 137/58] 2^-p
      < p 2^-p.                                             (1)

The working computation uses two final guard bits; the last inward rounding
returns the original p-bit output format. Its error and work are charged.

There are exactly p-1 complete oracle calls. The sum of their requested
precision parameters is exactly

    V(p) = sum_(j=1)^(p-1) q_j
         = (p^2+5p)/2 + 4750 < p(p-1).                        (2)

Thus the same p-term fixed-source evaluation can retain its published
p*2^-p error allowance with a strictly smaller oracle precision volume.
This is a deterministic instruction-parameter count, not a runtime
measurement or a complete bit-cost saving. It approaches half the fixed
p oracle volume as p tends to infinity. Optimality is not claimed.

## Disk and grid invariants

Inward componentwise rounding cannot increase the modulus, so ||v_j||<=1/2
and ||v_j-u/2||<sqrt(2)*2^-q_j<(3/2)*2^-q_j. Both complex
components are charged, including when q_j is coarser than p. The sequence
q_j is nondecreasing.
Therefore a y_(j-1) in D_(q_(j-1)) is an exact valid grid input at q_j.
For q>=101,

    1/2 + c + (q/3)2^-q < 1.

It suffices to check q=101 because q*2^-q decreases. Induction gives
||y_j||<1 and grid membership at every iteration. Oracle outputs belong
to D_(q_j) by the supplied contract. Every subtraction is between two
values on that grid; the norm estimate bounds its result before it is
used again. No uncharged projection is used to repair the invariant.

## Rounded error and inverse tail

Set x_0=u/2 and x_j=u/2-E x_(j-1). Then

    x_(p-1) = (1/2) sum_(a=0)^(p-1) (-E)^a u.

Writing d_j=||y_j-x_j||, the input rounding and oracle contract give

    d_0 < (3/2)2^-q_0,
    d_j < c*d_(j-1) + (3/2+q_j/3)2^-q_j.

Put Q=p+2. For d=p-1-j, q_j>=Q-d and q_j<=Q. Including the initial
error with the same larger coefficient gives

    d_(p-1)
      < (3/2+Q/3) 2^-Q sum_(d=0)^(p-1) (2c)^d
      < (3/2+Q/3) 2^-Q / (1-2c)
      = 25(2p+13) 2^-p / 96.                               (3)

This estimate allows arbitrary errors at each precision and every repeated
use of T_101. In particular it assumes no cancellation between calls.

Since c<1/2, E^p has norm at most c^p<2^-p. The inverse exists by the
convergent Neumann series, and its omitted tail has norm less than

    2^-p / (2(1-c)) = (25/29)2^-p.

The final inward projection costs less than (3/2)2^-p and cannot increase
the norm, so w belongs to D_p. Adding (3), the inverse tail and this last
rounding proves the first inequality in (1), since 25/29+3/2=137/58.
The second is equivalent to 1334p>16001, which holds for all p>=102.

## Exact precision count

The p-1 calls have indices j=1,...,p-1. Relative to the baseline ramp
j+3, the floor at 101 adds

    sum_(j=1)^97 (98-j) = 97*98/2 = 4753.

Also sum_(j=1)^(p-1)(j+3)=(p^2+5p)/2-3. This proves the equality in (2).
The baseline difference is

    p(p-1)-V(p) = (p^2-7p-9500)/2.

It is 95 at p=102 and increases by p-3 on replacing p by p+1. This proves
strict improvement for every p>=102 without a finite extrapolation.
At p=128 the exact volumes are 16256 and 13262. At p=256 they are
65280 and 38158. These count requested precision bits across calls,
excluding the dimension multiplier and all implementation tariffs.

## Wrapper and scope obligations

The algorithm retains the original input u, the current state and one oracle
result. It prepares v_j at each iteration, rather than rounding u/2 once.
All those source roundings and source reads are additional explicit work.
Embedding a coarser numerator at a finer grid uses a shift, and subtraction
needs a sign/carry bit before the proved disk bound is applied. The largest
requested grid precision is p+2. In a sequential binary fraction layout,
preparation, embedding, subtraction and head returns use O(s*q_j) bit work
per iteration for s complex coordinates, plus O(sp) initial/final work,
including the charged final projection to the original p-bit grid.
This statement counts these wrapper operations; it does not provide a
source-bound multitape implementation or a favorable complete constant.

No extra bank is provided free. Read buffers, oracle workspace, cleanup and
arbitrary productive dirty inputs need their actual caller contracts.
The norm proof alone does not authorize replacing precision in an emitted
native word. An actual Gaussian T_q family, its preparation/analytic error,
source streaming, grid conversions, final output use, stock, restoration and
the complete physical bill remain obligations. The five selected framework
assumptions and the selected frontier are unchanged. No new kappa, complete
multiplication theorem, human review or formal-kernel proof is claimed.
