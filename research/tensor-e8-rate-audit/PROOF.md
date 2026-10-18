# Quantitative audit of the tensor E8 paid moment

This audits sections 4.2, 8 and 9 of PR647's `PROVIDER-PROOF.md` at
`956bb581e7f97328e1b53baa5aca3d2490f2f607`. It corroborates the stated leading
constant and adds explicit finite-depth bounds and a first correction term.
It assumes the provider's listed register paths and three-stage assembly.
It does not independently prove their scalar, frame, RAM or Fourier realization.

Let architecture depth n >= 1, h=9^n, v=120^n, r=8^n,
R=(885v-1081r)/14, W=R+2v, m=3h and D=2v-3hr. Let H(s) be the complete
global paid histogram. Define

    Phi(k) = sum_s H(s) (s/m)^(1-k).

The root k_n of Phi(k_n)=W is a supremum for this profile's strict moment
condition, not an admitted equality witness or a multiplication exponent.

## Independent accounting

`lifetime_profile` aggregates chronological dimension changes for outputs,
pair routes, consumed inputs, gathers, decoders and returned child outputs.
It counts eight equal recursive subtrees by multiplicity. Root input loads,
root output finishes, both data endpoints, every copied-center descent and
the final two pivot lines are separately paid. These are dimension invoices;
checking a dimension path does not establish the actual frame inclusions.

An independent expression unrolls the recursion by level. At an internal level
j=0,...,n-2, put d=9^j and c=v/15^j. The **local** contributions are:

| Rank | Count |
| --- | ---: |
| h-d | c |
| d | 113c |
| h-2d | 56c |
| 8d | 2c |
| h-9d | 2c |
| 9d | 2c/15 |

At the terminal level d=h/9, c=v/15^(n-1), they are
(d,112c), (7d,56c), (8d,2c), (h,c/15).
Finally add (1,2v), (h-1,2v), (h,r). Multiply the local histogram by three,
then add (2,2v) for the global endpoints. Equal ranks are combined.
The terminal level must be treated separately: it has no decoder subtree.

The helper allocations obey R_1=6968 and R_n=59*120^n+8R_(n-1).
Summing the displayed counts and their ranks, or summing the register paths,
gives the source identities

    S = (1334v-1726r)/7,
    sum H = 3S+2v = (4016v-5178r)/7,
    sum sH(s) = mW-D.

These follow for every n by geometric sums/induction. The executable comparison
covers every integer n from 1 through 66. Finite agreement is additional evidence,
not a proof by enumeration of the universal identities.

Since D/v=2-3(3/5)^n >= 1/5, Phi(0)<W. All ranks satisfy 0<s<=h<m,
so Phi is strictly increasing. The child-count formula gives Phi(1)>W.
There is exactly one k_n in (0,1).

## A root enclosure without root finding

Write

    M = Phi'(0)/v = sum_s [sH(s)/(mv)] log(m/s),
    delta = (W-Phi(0))/v = D/(mv),
    A = h*delta = D/(3v),    U = log(m).

For 0<=z<1, z <= exp(z)-1 <= z/(1-z). Therefore

    delta/(M+delta*U) <= k_n <= delta/M.                 (1)

For the upper endpoint, Phi(k)-Phi(0) >= v*k*M holds for every k>=0.
For the lower endpoint k=delta/(M+delta*U), kU<1, and

    (Phi(k)-Phi(0))/v <= k*M/(1-kU) = delta.

Thus there is no numerical root-search stopping condition hidden in (1).
With rational bounds M_lo<=M<=M_hi and U<=U_hi, the reported interval is

    A/(M_hi+(A/h)*U_hi) <= h*k_n <= A/M_lo.              (2)

Logarithms use the atanh series after reducing the argument to [1,2), with a
geometric remainder. Specifically, for u=(x-1)/(x+1),

    2 sum_(j=0..63) u^(2j+1)/(2j+1) <= log x
    <= that sum + 2u^129/[129(1-u^2)].

Binary reduction also needs the same formula for log 2. Endpoints are rounded
outwards to multiples of 2^-180. All subsequent arithmetic is rational. The
36-place decimal strings in the receipt are floors for display; the fraction
fields, not those strings, are the certified endpoints.

## An explicit error bound for the asymptotic derivative

Let t=3/5, L=(913/14)log 3 and B_n=sum_(j=0..n-2)t^j, with B_1=0.
The following bounds hold for every n>=1:

    L-E_high <= M <= L+E_low,

    E_high = [131 B_n + 113 t^(n-1) + 2]/h
             + (87/14) log(3) / 15^(n-1),

    E_low = [(651/5) B_n + (603/5)t^(n-1) + 10/3] log(3h)/h
            + log(3)/15^n.                             (3)

Here is a direct derivation. Put f(x)=x log(1/x). Assign the output rank h-d,
pair rank h-2d, internal input/decoder ranks h-9d, and root data rank h-1 to
the high-rank group. At the terminal level assign one of the two 8d entries
to that group (the output); assign the other (input growth) to the low group.
Every high-rank x=s/(3h) lies in [7/27,1/3]. On this interval
0<f'(x)=log(1/x)-1<1, so replacing x by 1/3 changes f by at most 1/3-x.

The ideal high-rank counts per v, summed to infinite depth, are
3*59*sum_(j>=0)15^-j+6=2739/14. Their f(1/3) contribution is L.
The high-rank distance losses are at most
[131 B_n+113t^(n-1)+2]/h. At the terminal level the two h-9d entries
are absent; adding these plus the infinite tail costs
[2+59/14]log(3)/15^(n-1). This gives E_high.

All remaining terms are nonnegative. Bounding every log(3h/s) by log(3h),
their internal rank coefficients are 113+2*8+(2/15)*9=651/5 and their
terminal coefficients are 112+8+9/15=603/5. Root rank-one loading and the
global rank-two endpoints contribute 2+4/3=10/3. The copied-center term
is exactly log(3)/15^n. This gives E_low. Thus (3) does not rely on an
unquantified dominated-convergence argument. It also handles n=1.

Combining (2) and (3), M=L+O(n/9^n). The gap between the two exact-log
bounds in (2) is O(n/9^n), because A is bounded, M is bounded away from
zero eventually, and U=O(n). Consequently the refined expansion is

    9^n k_n = [28/(2739 log 3)] [1 - (3/2)(3/5)^n]
              + O(n/9^n).                             (4)

In particular the leading coefficient asserted in PR647 is correct under
its paid profile. The copied-center correction decays as (3/5)^n, much
more slowly than n/9^n. The ordinary exponent itself still tends to zero.
No search for an improved provider or new multiplication kappa is implied.

## Scope and failure detection

The executable checks all 66 profiles, their counts, masses, analytic
bounds (3), and rational root brackets. At depth 66 it certifies

    0 < (C-9^66 k_66)/C < 4*10^-15,
    C = 28/(2739 log 3).

Omitting the centers or rank-two endpoints fails at depths 1,2,6,66.
A separate mutation replaces one rank-1 and one rank-9 child by one rank-2
and one rank-8 child at depth two. It preserves both child count and rank
mass, but changes the logarithmic derivative and fails the histogram
comparison. Thus mass-only validation would be insufficient.

This is a mathematical profile audit and analytic consequence. The pinned
source's all-size RAM theorem, physical program and supplied-root cyclic
transfer remain outside this audit; it is not a proof-assistant result.
