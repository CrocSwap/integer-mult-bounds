# Fixed-channel terminal-broadcast limit

This result applies to a specified compiler class. Each scalar channel
has a distinct zero-entry terminal role in a signed DAG. Each terminal
reads at one fixed maximal common cap of its served target group. The
target decoder retains its basis and uses scalar reads in time order.
Parity and channel reads can interleave. This result does not apply to
copied broadcasts,
smaller caps, a changed decoder, channel fusion, or time reuse of a role
for a different scalar channel.

## Target frames

Let the five-cube selector be e in F2^5. Write its root as

    q(e) = q(0) + sum_i e_i d_i,

where d_i is the sum of the two coordinate axes in pair i. The d_i are
independent and even. The vector q(0) is odd. Let c be an affine selector
coset of ker S, where S has rank d. Its root span is

    U_c = span(q(c), D(ker S)),      dim U_c = 6-d.

Its maximal common cap is U_c^perp, of dimension h-6+d. The odd part of
U_c is exactly the root set of that coset. Thus different cosets have
different caps. No root of a different coset lies in U_c. No root of a
different five-cube lies in U_c either: all odd vectors in U_c select
one coordinate from each of this cube's five pairs.

If a terminal reaches U_c^perp, it cannot serve any target outside c.
Indeed, U_c^perp is contained in q(t)^perp if and only if q(t) lies in
U_c. Later target-frame growth cannot change that condition. This
prevents one terminal from serving two current cosets or two cubes.

A new parity normal refines each current coset into two cosets. The
source parity frame joins the old cap to exactly the new cap. If the
normal already lies in S, it does not refine the groups. The independent
check uses literal twenty-coordinate roots to check this join for every
subspace, coset, nonzero normal of weight one through four, and served
parity.

## Exact root count

For overlap r from one through four, the reduced parity kernel is

    A_r(t,s) = -(r-dist(t,s)-1)(r-dist(t,s)-3)/8.

Its nonzero Walsh coefficients per parity block have multiplicities
1, 2, 3, 3. Each target coefficient is a nonzero signed character on its
parity half. Thus each target must read m(a) channels for normal a,
with m(a) given by these four multiplicities. This count uses the fixed
channel outputs in the compiler class above.

For one target, its cap history defines a monotone normal-span history.
After a channel with normal a is read, that span must contain a. Refine
this history to a complete subspace flag. Move each channel read to the
first flag subspace that contains its normal. This can only reduce the
rank of the cap at that read.

For a fixed flag, process all available channels in each span before
the next extension. The weighted cost of an extension from S to S' is

    2^rank(S') * sum_{a in S' minus S} m(a).

A target read at a cap with normal-span rank d has charge 2^d/32. A
terminal at that fixed cap can serve at most 2^(5-d) targets. Thus the
total charge assigned to one terminal is at most one. The flag DP gives
a per-target charge of at least q/32. The 32 targets in each cube require
at least q terminals. This argument permits arbitrary channel read
orders and different span histories for different targets. It does not
assume one global normal span.

A forward shortest-path computation over the 374 subspaces of F2^5
gives these exact minimum terminal demands per target cube:

| Pair count p | Available overlap | Parity roots | Disjoint roots | Total |
|---|---|---:|---:|---:|
| 8 | 2, 3, 4 | 1326 | 0 | 1326 |
| 9 | 1, 2, 3, 4 | 1454 | 0 | 1454 |
| At least 10 | 0, 1, 2, 3, 4 | 1454 | 1 | 1455 |

The computation allows only actual positive-weight normals as flag
extensions. It also checks that allowing all nonzero normals gives the
same answer. The disjoint channel can run first and needs one terminal.
The receipt contains flags that attain every count.

## Retained endpoint ceiling

Assume the retained endpoint format has m=Lh, L=2K+1 with K>=1, V ports,
copied rank C, T replicas, and deficit

    D = T[2KV - LC].

Let R be the number of zero-entry terminal roles per replica. Their
rank increments are at most h and sum to h per role. Therefore their
rank-weighted entropy is at least LTRh log L. The root-count result gives

    R >= q*binom(p,5) = qV/32.

For a supplier exponent b, the moment uses the factor
exp(b log(m/r)). The inequality exp(x)>=1+x gives b*entropy<D as a
necessary condition. It follows that

    b < 32/(hq) * [(1-1/L)-C/V] / log L.

The function (1-1/L)/log L decreases for L>1. Its derivative has the
sign of log L-L+1, which is negative. The positive atanh series gives
log 3>13/12>1. On dropping C and using L>=3, one obtains

    b < 64/(3hq).

The exact rational ceilings are 2/1989 for p=8, 16/19629 for p=9,
and 16/21825 for every p>=10. For p from five through seven, C>=V,
so the stated deficit is negative for every K. These facts exclude
b=1/99, and therefore kappa=0.01, for this compiler class. They do not
exclude another construction or decoder for the paired-five family.

The primary script's comment log(1+b)>=b is false. The entropy argument
above uses exp(x)>=1+x instead. The primary numeric screens agree with
the correct necessary condition.

## If a terminal reads at several growing caps

The charge bound above requires one read cap per terminal. It does not
apply to a fixed scalar role that reads at several successively larger
caps. Each fixed scalar channel still requires at least one zero-entry
terminal per target cube. The channel counts are 130, 140, and 141 for
p=8, p=9, and p>=10. No terminal can read a different cube after its
first maximal-cap read, by the cross-cube exclusion above.

Use these smaller counts in the same entropy inequality. For p=8,
retain C/V=1348/1792 and use the bounds log L>1 and
(1-1/L)-C/V<1-C/V. This gives b<111/29120. For p=9 and p>=10, drop C
as before. This gives b<8/945 and b<16/2115. All three bounds are below
1/99. Thus this weaker argument still excludes kappa=0.01 for the
zero-entry fixed-channel class if roles can read at growing maximal
caps. It still does not bound a changed decoder or channel fusion.
