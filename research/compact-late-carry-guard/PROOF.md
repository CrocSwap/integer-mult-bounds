# Later-source repair with inactive saturated temporary digits

This is a scoped all-size implication for Douglas Colkitt's unchanged
compact-control address word. It extends PR1247's sufficient later-source
guard using the saturation/carry insight of PR1475. The original construction
and both predecessor guards remain correct. No new kappa is claimed.

## Domain and raw word

Fix integers `n>=1`, `G>=1`, `K>=G+1`, and `0<=rho<K`. Put
`B=2^G`, `A=2^(K-1)`, `R=2^K`. Remove only the unchanged low `rho`
target bits. Retain every upper target bit in the quotient modulus
`Y=2^((n+1)K-rho)>=2R^n`. The two compact fields have modulus `C=B^n`.
The source's `n` processed bits `c_i` are independent binary values.

Write the processed target digits as `2g_i+a_i`, with `0<=g_i<A` and
`a_i` binary, and the dirty compact digits as `0<=t_i,u_i<B`. Let
`p_i=u_i mod 2`, `q_i=p_i OR c_i`, and define

```
mask(z) = sum_i z_i R^i
pack(y) = sum_i bit_(iK)(y) B^i
load(c) = sum_i c_i B^i.
```

For a fixed bit vector z, the earlier-source raw permutation P_z is

```
y1 = y + 2 sum_i z_i t_i R^i               mod Y
t1 = t + pack(y1)                         mod C
y2 = y1 + sum_i z_i(1-2 digit_i(t1)) R^i   mod Y
t2 = t1 - pack(y2 XOR mask(z))            mod C.
```

The later-source raw map S applies `P_p`, adds `load(c)` to u modulo C,
applies P with the new u parities, then subtracts `load(c)` from u.
The intended map is `T(y,t,u,c)=(y XOR mask(c),t,u,c)`. Each raw rotation
is independent of its target, so S is a permutation even at bad addresses.
The physical swap sandwiches restore the arbitrary back field. Source,
spectator, and low-rho bits are unchanged. The highest selected bit is
completed separately by the retained elementary XOR.

## The sufficient guard H

Compute compact carries from the ORIGINAL target parities:

```
d_0 = 0
d_(i+1) = floor((t_i+a_i+d_i)/B).
```

Every d is zero or one. Admit an address precisely when

```
q_i=1 implies d_i=0 and t_i<=B-2         for every i<n
u_i+c_i<B                              for every i<n-1
g_i+q_i*t_i<A                          for every i<n-1.       (H)
```

Saturated digits `t_i=B-1` are permitted at q_i=0, provided their carry
does not reach a later active digit. Final outgoing compact and wide-target
carries are allowed. The upper target coordinates stay in modulus Y;
they are not discarded in the check.

**Claim.** S=T on H, H is invariant under T and S, and therefore the
retained current-address exceptional correction `T S^-1` is supported on
the complement of H. This holds for all parameters in the stated domain.

First prove a sufficient earlier-source fact. Suppose z_i=1 implies
`d_i=0,t_i<=B-2`, and `g_i+z_i*t_i<A` for i<n-1. The first target rotation
has no carry entering any processed target digit: starting at carry zero,
an inactive digit cannot produce a carry, and an active interior digit
stays below R. Its last outgoing carry may be nonzero. Consequently
`pack(y1)=pack(y)`. The digits of t1 are

```
t_i+a_i+d_i-B*d_(i+1).
```

At every active digit both d_i and d_(i+1) are zero, so its digit is
`t_i+a_i`. Adding both target offsets gives
`sum_i z_i(1-2a_i)R^i` modulo Y, exactly the intended XOR. Its unload
uses `pack(y2 XOR mask(z))=pack(y)`, restoring the COMPLETE t field,
including inactive saturated digits and final modular overflow.

For the later-source word, the no-interior-u-carry condition makes the
new u parities `p_i XOR c_i`. A final carry is discarded modulo C and does
not change any processed parity. Both p and p XOR c are supported on q.
Thus H gives the sufficient earlier-source conditions for the first call.
After that exact call the target parities are `a_i XOR p_i`; g,t,u,c
are unchanged until the source load. The compact carry recurrence has
the same states as before: at q_i=0 the parity is unchanged; at q_i=1,
incoming carry zero and nonsaturation force outgoing carry zero for either
parity. The sufficient conditions therefore also hold for the second call.
Its XOR combines with the first to give c. The source load and unload
restore all of u, and both calls restore all of t.

To show T-invariance of the predicate itself, use the same carry induction
with `a_i XOR c_i` in place of `a_i XOR p_i`. Since c is supported on q,
the carry states coincide on H. The other two conditions depend on g,t,u,c,
which T fixes. Hence `T(H) subset H`; T is an involution, giving equality.
Since S agrees with T on H, `S(H)=H`. Bijectivity of S then preserves its
complement, proving the current-address repair claim.

PR1247's guard H0 requires all t_i<=B-2 plus the same u and target conditions.
All its compact carries are zero, so H0 is contained in H. Inclusion is
strict: for every allowed geometry, the zero source, even u, zero target
parities and a saturated inactive t digit satisfy H but not H0. This gives
a positive complete-rectangle enlargement, not just a sampled improvement.

## Exact all-n density

There are `4AB^2` equiprobable choices of `(g,a,t,u,c)` per digit. Index
row and column by incoming/outgoing compact carry d=0,1. Put `Z=AB/2` and

```
M = [[Z(2B-1) + (3B/2-1)[2A(B-1)-(B-1)(B-2)], Z],
     [Z(2B-3),                                   3Z]]

N = [[Z(2B-1) + 3AB(B-1), Z],
     [Z(2B-3),           3Z]].
```

Then the exact good fraction on every complete rectangle is

```
Pr(H) = (1,0) M^(n-1) N (1,1)^T / (4AB^2)^n.                 (1)
```

For q=0, `(p,c)=(0,0)`, giving B/2 choices of u. No target guard applies,
and every g is allowed. Counting `(t,a)` carry transitions gives
`[[2B-1,1],[2B-3,3]]`, multiplied by Z. For q=1, only transition 0->0
is admitted. At an interior digit the no-u-carry restriction gives
`B/2+B/2+(B/2-1)=3B/2-1` choices of `(u,c)`. For each t<=B-2 there
are two parities and A-t target guards, totaling
`2A(B-1)-(B-1)(B-2)`. At the last digit there is no u or target guard,
so there are 3B/2 choices of `(u,c)` and `2A(B-1)` of `(g,a,t)`.
This proves M,N and (1); it accounts for the correlation of p with u.
Unused source bits, low target bits, all upper target digits and the back
field contribute equal factors to numerator and denominator.

For `n=2,K=6,G=2`, M=`[[1378,64],[320,192]]` and
N=`[[1600,64],[320,192]]`, giving

| Guard | Complete-rectangle good fraction |
|---|---:|
| PR1247 nonsaturated H0 | 1971/4096 |
| This sufficient carry guard H | 9085/16384 |
| Gain | 1201/16384 |

## Exact maximality for one processed digit only

For n=1, nonsaturated t always gives S=T. If `t=B-1`, an active
earlier-source call sends y to y+1 when a=0, and to y+2B-1 when a=1;
the temporary is restored in both cases. An inactive call is identity.
With c=0, both controls equal p: p=0 is identity, while p=1 makes two
active calls and changes y by 2B. With c=1, exactly one call is active,
and full-map agreement holds exactly at a=0. The discrepancy 2B cannot
vanish modulo Y because `Y>=2R>=4B`.

Thus the full agreement set E is

```
t<=B-2 OR [t=B-1 AND ((c=0 AND p=0) OR (c=1 AND a=0))].
```

For any involution T the largest T-invariant subset of E is
`E intersect T(E)`: the intersection is invariant, and every invariant
subset of E lies inside it. Here this removes the c=1 saturated cases,
leaving exactly H. Therefore `Pr(H)=1-3/(4B)` is the sharp invariant
guard fraction for this word when n=1. The larger agreement fraction is
`1-1/(2B)` and is unsafe for current-address repair. No maximality is
asserted for n>1: H excludes internal source-load carries and may exclude
cancellation between two individually inexact subcalls.

## Full cost and remaining obligations

The word retains all twelve compact swaps and ten controlled rotations,
both source accesses, arbitrary dirty-field restoration, and the highest-bit
completion. H uses one pass of digit comparisons and a single carry bit;
with n<=L and L-bit addresses this fits the retained O(L^3) descriptor
allowance. For M records, payload width P, address width L, and V=MP,
retain the complete correction bill

```
O(V + M L^3 + delta M L(P+L)),   delta=1-Pr(H).
```

This includes extraction, full inverse-address computation on current
controls, destination keys, sorting complete records, reinsertion, rewinds
and clearing. Since H contains H0, its bad fraction is no larger; under
the retained `G=4 ceil(log2 p)+6`, `n+1<=p`, `K/log p -> infinity`,
`L=O(p)`, and superpolynomial payload assumptions, the earlier O(V) repair
bound remains sufficient. No smaller asymptotic exponent follows.

The proof assumes complete independent address fields and the retained
controlled-rotation and repair interfaces. This is not a construction of
the full fixed-tape machine. Recursive field reservation, physical hosting,
compiler, precision, analytic transfer and the multiplication theorem are
not discharged. Finite verification supports the written proof and does
not formalize it. New material Apache-2.0; substantial OpenAI Codex assistance.
