# Full fixed-height direct-flow limits

This is a scoped analytic theorem about the **historical raw-p7**, default-height
flow of #4436. It determines the asymptotic scalar leaf-count exponent, not a
physical compiler replacement or a new multiplication exponent. The changed-height
compiler of #4483 is outside the theorem.

## 1. Law, source, and statement

Let

```
P = {1:37305,2:10695,3:3360,4:1530,5:300,8:1464,16:448,32:448,48:448},
T = {5:420,6:270,7:840,8:1395,9:3195,25:448,41:448,57:448,121:224},
m = 121, a = log 5,
P(s) = sum_r P_r r^s, T(s) = sum_k T_k k^s.
```

For integer N>=m take the exact `Flow(T,P,N).merged()` in
`research/direct-mixed-flow/flow.py`, with its defaults: G=floor(log_5(N/m)),
B=log(N/m)=Ga+delta, 0<=delta<a. Write S_N(s), E_N(s), and L_N(s) for the
power-s potentials of its complete sources, complete exits, and leaf exits.
All multiplicities are retained; a final leaf rank is not truncated a second
time. Boundary exits have potential E_N(s)-L_N(s).

Let alpha solve P'(alpha)/P(alpha)=a and let t be the raw crossing T(t)=P(t)
identified by #6118. Set

```
A=P(alpha), D=T(alpha), q=D/A, sigma²=(log P)''(alpha),
J=A-D,
S(s)=sum_(k>r) P_r T_k [r^alpha k^s-k^alpha r^s],
E(s)=sum_(r>k) P_r T_k [k^alpha r^s-r^alpha k^s].
```

The new exact certificate independently bounds
alpha in [0.98981438244597,0.98981438244599],
t in [0.99731351095114,0.99731351095116], and
q in [0.987128605365,0.987128605366]. Thus J>0 and t>alpha.
Uniqueness of alpha follows from positive tilted variance; the source's
nonlattice and positive-variance properties are recalled below. The raw-root
uniqueness on [0.99,1] is inherited from #6118, not inferred from a bracket alone.

**Theorem.** For each fixed real s>alpha, write tau=s-alpha and

```
C_G(s,delta)=exp(tau B) A^G / (tau sigma sqrt(2 pi G)).
```

As G tends to infinity, uniformly for delta in [0,a] in the fixed-depth
family,

```
S_N(s)/C_G -> S(s)/J,
(E_N(s)-L_N(s))/C_G -> E(s)/J,
L_N(s)/C_G -> P(s).
```

The fixed-depth family at delta=a retains G; actual integer ranks always
have delta<a. In particular, along **every** sequence of integer N tending
to infinity,

```
E_N(s)/S_N(s) -> R(s) = [J P(s)+E(s)]/S(s),
L_N(s)/E_N(s) -> J P(s)/[J P(s)+E(s)].
```

This resolves the relative source/boundary/leaf masses left open by #6118 and
#6125. The proof uses their paid-law local-limit framework and #4459's mirror
identity. The new step sums **all mixed target/paid base layers**, with a
uniform domination argument rather than assuming stable shares.

## 2. Exact decomposition of all source and exit histograms

Let P_j(z) count ordered j-letter paid words of product z, including the
product of their multiplicities; define T_j similarly, with P_0(1)=T_0(1)=1.
Nonnegative log ranks imply that the final cap also enforces every earlier
paid-prefix cap. The target multinomial u(a) in #4436 counts ordered target
words with the same letter multiplicities. Equal products are combined only
by addition of multiplicities.

The root source histogram consists of every rank k z with multiplicity
T_k T_G(z), for z<=N/m. The leaf histogram consists of every rank r z with
multiplicity P_r P_G(z), for z<=N/m, **with all terminal r allowed**.

For each h=0,...,G-1 use a common base of h target letters and G-1-h paid
letters. Let z be its product and mu its multiplicity. A pair (r,k) issues
rank rkz with multiplicity mu P_r T_k. Its two relevant presence tests are
kz<=N/m for the parent and rz<=N/m for the child. Hence:

- If rz<=N/m<kz, this is an inner source (necessarily k>r).
- If kz<=N/m<rz, this is a boundary exit (necessarily r>k).
- If both are present, the matching cancels this contribution.
- If neither is present, there is no contribution.

This is the complete mirror identity from #4459, expressed with ordered-word
convolutions. The eligible-parent sum in Pascal's identity yields exactly
these terms even when several target letters lead to the same product.
There is no cross-round matching or omitted unmatched job.

Equivalently, for the base log product H, an inner-source pair k>r has
B-log k < H <= B-log r; a boundary pair r>k has
B-log r < H <= B-log k. The endpoint conventions will not affect the limit,
but the exact finite verifier retains them.

The package independently assembles these four histograms and compares every
entry with the frozen `Flow.merged()` on 26 finite fixtures, including the raw
p7 and two overlap controls. This is finite corroboration of the source
reading, not the proof of the limiting assertion.

## 3. The mixed-layer limit and its domination

Use paid probabilities p_alpha(r)=P_r r^alpha/A and target probabilities
v_alpha(k)=T_k k^alpha/D. Let X be the paid log rank and Y the target log rank.
Then E X=a and Var X=sigma²>0. The paid support contains 0,log2,log3, so it is
nonlattice: a lattice would force log2/log3 rational, contrary to unique
factorization. Centering and tilting preserve that property.

We use precisely the nonlattice interval local-limit theorem and its uniform
concentration consequence stated in #6118, PROOF.md §3. The external source
is C. Stone, *A local limit theorem for nonlattice multi-dimensional
distribution functions*, Ann. Math. Statist. 36(2), 546–551 (1965),
[DOI 10.1214/aoms/1177700165](https://doi.org/10.1214/aoms/1177700165),
Corollary 1 equation (7), with the paper's uniformity convention. Its required
specialization is

```
sup_x |sqrt(l) Pr(sum_(i=1)^l(X_i-a) in [x,x+b))
        - b/(sigma sqrt(2pi)) exp(-x²/(2l sigma²))| -> 0
```

for every fixed b>0. In particular there is a finite constant K_b such that
sqrt(l) Pr(sum X_i in [x,x+b))<=K_b for all l>=1 and all real x. This bound
is existential; it supplies no effective convergence rate. Convolving with
an independent target sum preserves it, since the bound holds at every x.
The maximum paid atom is o(l^(-1/2)), obtained by bounding an atom with any
fixed-width interval and then sending that width to zero. Thus open versus
closed endpoints in §2 have vanishing normalized contribution.

Fix s>alpha. For fixed h, put
H=sum_(i=1)^(G-1-h) X_i+sum_(j=1)^h Y_j. Undoing the tilt in the base
measure multiplies expectations by

```
A^(G-1-h) D^h exp(tau B) = A^(G-1) q^h exp(tau B).
```

For any fixed bounded interval I of u=B-H, the interval theorem and finite
step-function approximation give, uniformly over bounded delta,

```
sqrt(G) E[exp(-tau u) 1_(u in I)]
  -> (1/(sigma sqrt(2pi))) integral_I exp(-tau u) du.
```

For fixed h the target sum has finite support, and the paid centering differs
from B by only a bounded shift depending on that support and delta. This is
why the Gaussian density tends to its value at zero uniformly in delta.

It remains to justify summing h, rather than treating it as fixed. Split at
h<=G/2. For sufficiently large G this part has G-1-h>=G/2-1 paid letters.
Uniform concentration, also after convolution with the target sum, bounds
the displayed expectation multiplied by sqrt(G) by a constant independent
of h,G,delta on each fixed interval I. Its geometric multiplier q^h is
summable. For h>G/2, use the crude bound
exp(-tau u)1_I<=sup_I exp(-tau u); after the same normalization the full tail
is at most a fixed constant times sqrt(G) sum_(h>G/2)q^h, which vanishes.
These bounds justify dominated summation and give the factor 1/(1-q).
The same bounds with one extra bounded factor u justify log-moment limits.

Consequently the full base potential in a window
B-log v < H <= B-log u, 0<u<v, is asymptotic to

```
C_G(s,delta) * [u^(-tau)-v^(-tau)]/J.
```

Multiplying by P_r T_k (rk)^s and summing the finitely many pairs gives the
inner-source constant S(s)/J and boundary constant E(s)/J.

## 4. Root sources, leaves, and the complete ratio

The all-target root-source potential is bounded by
T(s) exp(tau B) D^G: below the cap, exp(tau H)<=exp(tau B). Dividing by C_G
bounds it by tau sigma sqrt(2pi G) T(s) q^G, which tends to zero uniformly.
For its normalized log-depth, H>=G log5 implies B-H<=delta<=a, so the same
bound handles the required bounded log factor. This is why root sources are
not silently discarded in the exact decomposition but vanish in the limit.

The leaf limit is #6118's weighted paid local limit, including its uniform
exponential-tail domination, or #6125's finite power-tariff factorization:

```
sum_z P_G(z) z^s 1_(z<=exp B) ~ C_G(s,delta).
```

The unconditioned terminal r multiplies this by P(s). The denominator
constants S(s) and J are positive for s>alpha, so dividing limits proves §1.
The full unit column moment U_N(s) is a mixed sum with h target and G-h
paid letters for h=0,...,G, over the half-line below the cap. The same
uniform concentration, geometric h domination, and exponential tail bounds
show U_N(s)/C_G -> A/J. The finite all-potential identity in #4436 is

```
S_N(s)-E_N(s)=[T(s)-P(s)] U_N(s).
```

Differentiating this **finite sum identity** at t gives the exact log gap

```
g_N = S_N'(t)/S_N(t)-E_N'(t)/E_N(t)
    = [T'(t)-P'(t)] U_N(t)/S_N(t).
```

No derivative of a limiting expression is taken. The unit and source limits
therefore give

```
g_infinity = A[T'(t)-P'(t)]/S(t).
```

Direct algebra also gives S(s)-E(s)=A T(s)-D P(s), hence
R(s)=1+A[P(s)-T(s)]/S(s), consistently with R(t)=1.

The exact certificate encloses the leaf fraction at t in
[0.898921196162,0.898921196179] and g_infinity in
[120.3700305164,120.3700305182]. The previously heuristic full-flow shares
and log gap have now been replaced by source-bound limits.

## 5. What the induction threshold does, and does not, prove

The named sufficient single-step test in #4405/#4459 compares
E_N(s)/S_N(s) with eta(s)=s m^(s-1). It is stricter than the exact complete
complement-plus-exit recurrence. Our limit settles its eventual strict sign
at any fixed s where R(s)!=eta(s).

For this p7 law, exact rational interval calculations prove R'(s)<0 on all
of [0.9973,1] by 27 covering intervals. Since
eta'(s)=m^(s-1)[1+s log m]>0, eta-R is strictly increasing there. Two exact
endpoint signs locate its unique root s_d in

```
0.99743801995 < s_d < 0.99743801998,
0.00256198002 < 1-s_d < 0.00256198005.
```

For t<=s<s_d the sufficient test eventually fails; for s_d<s<=1 it eventually
passes, uniformly across offsets. At equality this proof determines only the
limit and makes no finite-depth sign assertion. It provides no explicit onset
rank. The threshold is **not** the exponent of L(N), a necessary condition
for all majorants, or a universal obstruction to direct compilers. In
particular #4483's different height is unaffected. An explicit finite onset and physical funding
would still be needed for a constructive uniform supplier claim. No new κ follows.

**Scalar recurrence corollary.** For every fixed s with s_d<s<1, the exact
normalized rank-one leaf recurrence of #4436 satisfies L(N)=O(N^s).
In particular the exact certificate verifies the positive limiting margin at
s=0.99744, so L(N)=O(N^0.99744), a scalar saving of 0.00256.
This is a statement about the counted scalar recurrence, not about integer
multiplication or admitted physical cost.

Indeed choose N_0 so the sufficient test holds for all N>=N_0. Every source
rank z lies in (N/m,N], every exit e<N, and every complement N-z<N.
For 0<s<1, concavity gives

```
N^s-(N-z)^s >= s N^(s-1) z >= s m^(s-1) z^s = eta(s) z^s.
```

Sum over every source with its multiplicity and use
E_N(s)<=eta(s)S_N(s). The complete complement-plus-exit sum is at most
(source count) N^s. Select a finite constant K at least
max_(1<=n<N_0) L(n)/n^s, with L(0)=0. Strong induction in the exact recurrence
then gives L(N)<=K N^s for all N. The proof establishes existence of N_0 and K;
it computes neither. The default depth and all unmatched jobs stay unchanged.
The changed-height near-root theorem in #4483 remains a distinct, stronger
construction with explicit certificates. The new corollary closes a useful
part of the original fixed-height question without replacing that work.

## 6. Exact complements determine the scalar recurrence exponent

The preceding sufficient test discards some complement capacity. Retaining
every complement gives a stronger result for the **same original height**.
For alpha<s<=1 define

```
I0 = sum_(k>r) P_r T_k integral_(log r)^(log k) exp(alpha y) dy,
K(s) = sum_(k>r) P_r T_k integral_(log r)^(log k)
         exp(alpha y) [1-(1-(rk/m)exp(-y))^s] dy,
V(s) = [J P(s)+E(s)] / [(s-alpha)m^s],
F_G = A^G exp(-alpha B) / [J sigma sqrt(2pi G)].
```

Here y=B-log z for a mixed base z, so the source rank is **rkz**, its
fraction of N is x=(rk/m)exp(-y), and log r<=y<log k for k>r.
In particular x ranges from r/m to k/m, inside (0,1]. Leaving out the
factor r would price a different recurrence.

Let C_N be the total source count and define the exact normalized child
power for the recurrence in #4436 by

```
H_N(s) = [sum_sources c_z (1-z/N)^s + sum_exits c_e (e/N)^s]/C_N.
```

The mixed-layer proof in §3 applies to each bounded kernel
exp(alpha y), exp(alpha y)[1-(1-x)^s] on its fixed window: approximate it
by step functions and use the same uniform concentration bound. The
all-target source **count** is negligible too: its alpha-tilted bound is
T(0) D^G exp(-alpha Ga), whose ratio to F_G is O(sqrt(G)q^G), uniformly
over delta. Its complement kernel is at most one. The complete exit-power
limit follows directly from §1 after division by N^s=(m exp B)^s. Hence

```
C_N/F_G -> I0 > 0,
sum_sources c_z [1-(1-z/N)^s]/F_G -> K(s),
sum_exits c_e (e/N)^s/F_G -> V(s),
H_N(s) -> H(s)=1-[K(s)-V(s)]/I0.
```

All limits are uniform over bounded offsets, for each fixed s>alpha. Thus
they hold eventually for **every** integer N, not just a favorable subsequence.
No derivative or numerical extrapolation of the finite recurrence is used.

Put D_full(s)=K(s)-V(s). This function is continuous and strictly increasing
on (alpha,1]. The source capacity K increases strictly: for 0<x<1,
1-(1-x)^s increases strictly in s, and a positive pair window has positive
length. For the exit term, its integral representation is

```
V(s) = J sum_r P_r integral_0^infinity
                 exp(alpha y) [(r/m)exp(-y)]^s dy
     + sum_(r>k) P_r T_k integral_(log k)^(log r)
                 exp(alpha y) [(rk/m)exp(-y)]^s dy.
```

Every displayed exit fraction is at most 48/121<1, so V strictly decreases.
Continuity on compact subintervals of s>alpha follows by dominated convergence
with the leaf envelope exp(-(s-alpha)y). At s=t, the exact conservation
identity gives V(t)=S(t)/[(t-alpha)m^t], whereas
1-(1-x)^t<x^t for 0<x<1 and 0<t<1. Thus D_full(t)<0. At s=1,

```
D_full(1)=A[T(1)-P(1)]/[(1-alpha)m]>0,
T(1)-P(1)=608.
```

There is consequently a unique s_star in (t,1) with H(s_star)=1.
The rational interval certificate proves

```
0.99738855928 < s_star < 0.99738855931,
0.00261144069 < 1-s_star < 0.00261144072.
```

**Scalar exponent theorem.** With the exact source and exit histograms and
the original default depth of #4436, define L(0)=0, L(n)=n for 1<=n<m,
and for n>=m use its complete recurrence

```
L(n) = [sum_sources c_z L(n-z) + sum_exits c_e L(e)] / C_n.
```

Then log L(n)/log n tends to s_star; equivalently L(n)=n^(s_star+o(1)).
In particular L(n)=O(n^0.99739), with scalar saving 0.00261.

To justify both sides, all source ranks satisfy n/m<z<=n, all exits satisfy
1<=e<=48n/121<n, and C_n>0. For root sources the lower bound follows from
z>=5^(G+1)>n/m; for mixed sources it follows from kz_base>n/m and r>=1.
The upper source bound follows from rz_base<=n/m and k<=m. For boundary
exits kz_base<=n/m and r<=48; leaves have z_base<=n/m and r<=48. The
all-rank-one leaf gives a positive exit at every n, so induction gives
L(n)>0 for n>=1.

For any fixed s with s_star<s<1, uniform convergence gives H_n(s)<1 for
all n>=n_0. Choose a finite C at least max_(1<=n<n_0) L(n)/n^s.
Strong induction on the exact recurrence gives L(n)<=C n^s. For any fixed
s with t<s<s_star, H_n(s)>1 eventually; choose positive c at most the
same finite minimum, and strong induction gives L(n)>=c n^s. At child
zero both comparisons use L(0)=0. Sending s to s_star from both sides
proves the claimed logarithmic exponent. This establishes an actual scalar
lower bound, unlike failure of the sufficient test in §5. It does **not**
prove a lower bound for another compiler or for integer multiplication.

The proof supplies existence, but no effective n_0 or constants C,c. It
neither materializes a physical recursive supplier nor eliminates the
selected theorem's five inherited assumptions. The changed-height result
of #4483 can approach the better raw root t; our original fixed-height
exponent is strictly larger. **No new κ.**

### Exact complement series and certified tail

For 0<s<1 put b_1=s and b_(j+1)=b_j(j-s)/(j+1). The binomial identity
1-(1-x)^s=sum_(j>=1)b_j x^j has positive terms for 0<=x<=1, including
x=1 by monotone convergence. Termwise integration is therefore justified:

```
K(s)=sum_(j>=1) b_j B_j,
B_j=sum_(k>r)P_r T_k
       [r^alpha(k/m)^j-k^alpha(r/m)^j]/(j-alpha).
```

After M terms let tail_M=product_(j=1)^M(1-s/j). The exact telescoping
identity sum_(j>M)b_j=tail_M gives, pointwise,
0<=sum_(j>M)b_j x^j<=tail_M x^(M+1). Consequently the integrated
remainder lies in [0,tail_M B_(M+1)]. This remains valid at x=1 and
requires no special-function library or quadrature error estimate.
`complement.py` computes all powers by exact interval multiplication of
rational bases and groups equal bases without changing the pair sum.
M=512 certifies the two displayed endpoints and the rational upper exponent
0.99739. Independent controls at s=1/2 use exact square-root values; dropping
the positive tail is deliberately rejected. These checks corroborate the
series evaluator; the written positive-series argument proves its tail bound.

## 7. Exact computation and proof boundary

`certificate.py` uses only integer/Fraction intervals. Logarithms use 64 terms
of 2 atanh(y) after power-of-two reduction to [1,2], where 0<=y<=1/3; the
positive omitted tail is bounded by 2 y^129/[129(1-y²)]. Exponentials reduce
to |x|/16<=5/16, sum terms through degree 40, and bound the next and later
terms by their first omitted term divided by 1-(5/16)/42, then square four
times. Every operation is rounded outward to a 2^-128 grid. Negative
exponents use monotonicity and reciprocal intervals. Neither floats nor
numerical fitting decide any acceptance gate.

The finite proof checks cover complete source, leaf and boundary histograms,
four integer-power identities per fixture, coefficient conservation,
root/tilt signs, geometric summability, shares, log gap and the entire stated
derivative interval. Altered terminal truncation, missing target layers,
missing multiplicities, reversed windows and omitted root sources are
rejected. These are computational evidence for finite identities and
numerical hypotheses. The all-N convergence rests on the written proof and
the cited classical interval theorem, not on the finite enumeration.

Credit zxv (#4436/#4483), Ryanson Jonathan / pinterbanget (#4459/#4465/#4467),
DLamdata (#6118), Nick Petalas (#6125/#6128), Cinna Davis / 1337isnot1337
(#4405 and the p7 controller), Jacob Alan Sussman (lockstep compiler), Stone,
and all retained native/precision/analytic predecessors. New full-flow
summation, proof and verifier prepared for @CubeJerry with substantial
OpenAI Codex assistance. Apache-2.0; no independent human or proof-kernel
acceptance is claimed.
