# Independent adversarial review of the fixed-height flow proof

**Disposition: PASS for the stated scalar recurrence theorem; no blocking
mathematical gap located.** No new multiplication exponent or physical supplier
claim is accepted by this review.

Reviewer: the separate `asymmetric_phase` Codex research worker, who did not
participate in the flow theorem's derivation or complement extension. Prepared
for @CubeJerry with substantial OpenAI Codex assistance, 2026-10-31. This is
an AI-assisted mathematical review, not human or proof-kernel acceptance.

Reviewed source/local commit: `f921d11738c1c190ee229eaf3101c75c4846ec8e`.
Published exact-tree-equivalent commit: `f728e60a1f0a3db3a95aea0dbd5dafd40d59e98c`.
Canonical source base: `a7638a4ce2a29947457ae8d6bf8cd70a234dfeac`.

Reviewed package bytes at those commits (the later README review link is a
documentation-only addition; the proof and source manifest remain unchanged):

| File | SHA256 |
|---|---|
| PROOF.md | `c6c2a52e2424186db09c28792b6956aa349ad2716ea8c81bf1f0faea875be0e4` |
| README.md | `d0a416ba098b2a214985758ea4d49a72367d0dd4883729f775af9059ec39f130` |
| SOURCES.json | `9a64ef594e180197822035dc6c5446a9204d70bf5d2658add67369a9b54c507a` |

All six declared source records matched their SHA256 and Git-blob hashes.
The review read the frozen `Flow.merged()` implementation, the mirror identity
from #4459, and the leaf-law theorem from #6118. It did not import or replay the
new certificate engine. Its purpose is an independent challenge to the all-N
reasoning, not another execution of finite tests or verification of numerical
interval endpoints.

## 1. Source decomposition and integer caps

I reconstructed the mirror windows from `Flow.merged()` and Pascal's identity.
For a target multi-index b of degree G-d, the uncapped multinomial count equals
the sum of its eligible predecessor terms T_k u(b-e_k). Each term corresponds
to the common base z=rho*c(b-e_k), with d paid letters and G-1-d target letters.
The supply presence test is kz<=N/m; the demand component test is rz<=N/m.
This gives rank rkz and exactly the source/boundary windows stated in the proof.
It also explains why several target words with equal product must add their
multiplicities rather than create an extra matching rule.

All factors are positive integers at least one. Therefore a final cap implies
every paid-prefix cap. The exact integer test z<=floor(N/m) is equivalent to
z<=N/m; no approximation of the cap is used. Also
floor(log_5(floor(N/m)))=floor(log_5(N/m)), because the intervening thresholds
are the integers 5^G. Thus the declared real offset describes the actual code.

The fixed-depth extension at delta=a is a limiting family, not the default
flow at that endpoint. The proof explicitly distinguishes this. All actual
integer flows have delta<a, which is what the strict source-rank lower bound
uses in the induction.

## 2. Mixed-layer local limit, without a triangular-array assumption

Let h be the target-letter count, l=G-1-h, and H the sum of the l paid and h
target log ranks under their alpha-tilted laws. For a compactly supported
Riemann-integrable kernel f(y), undoing the tilt gives the exact base-count
expression

```
A^(G-1) q^h exp(-alpha B) E[exp(alpha(B-H)) f(B-H)].
```

For fixed h, the target sum has finite support. The shift from the paid mean
is B-la=(h+1)a+delta. It is bounded uniformly over delta in [0,a], including
after conditioning on any point of that finite target support. The stated
uniform interval local-limit theorem therefore gives the constant density
1/(sigma sqrt(2 pi)) after multiplication by sqrt(G). No local-limit theorem
for h growing with G is assumed.

The interchange of the h-sum and limit is justified as follows. If h<=G/2,
then l>=G/2-1, and the uniform paid interval concentration bound, preserved
by convolution with any independent target sum, bounds the normalized kernel
by a constant independent of h, G, and delta. The multipliers q^h are summable
because the exact gate establishes 0<q<1. If h>G/2, the bounded kernel gives
a tail bounded by a constant times sqrt(G) sum_(h>G/2) q^h, which vanishes.
Consequently the total mixed base count divided by F_G tends to
integral exp(alpha y) f(y) dy. The factor is A/J, arising from summing q^h;
combined with A^(G-1), it is exactly the stated F_G, not an extra A or J.

Open/closed window endpoints do not change this limit. The maximal paid atom
is o(l^(-1/2)), by taking arbitrarily small fixed intervals in the stated
local-limit theorem. Fixed-h endpoint contributions vanish, and the same
h-tail domination controls the rest. The argument is uniform in the offset.

For the half-line needed for leaf powers and unit potentials, the weight is
exp(-(s-alpha)y), with s-alpha>0. Partition into unit intervals: uniform
concentration bounds the tail by a convergent geometric series, uniformly in
G, h<=G/2 and delta. For h>G/2 the kernel is bounded and the earlier q-tail
applies. These are the needed two distinct dominations; neither weak
convergence alone nor a fixed-height statement alone would have sufficed.

The paid support contains 0, log2, log3 and has positive finite variance.
Its nonlattice argument is valid. I checked the applicability and use of the
precise Stone theorem stated in the pinned #6118 proof. The original paper's
page/equation transcription was not independently reauthenticated here; the
classical interval theorem remains an explicit inherited mathematical input.
No effective local-limit rate is obtained by this argument.

## 3. Exact complements and the rk/m factor

For an inner-source pair k>r, y=B-log z lies in [log r,log k), and its source
rank is rkz. Thus

```
x = rkz/N = (rk/m) exp(-y),       r/m < x <= k/m <= 1.
```

The factor r is mandatory. A concrete semantic check is the depth-one source
pair r=8, k=9, base z=1, N=8*121: its source rank is 72 and its fraction is
9/121. Omitting r instead gives 9/(8*121), a different recurrence. This is a
check of the exact source reading, not an empirical asymptotic argument.

Applying the compact-kernel result to f=1 and to
f=1-(1-x)^s produces I0 and K(s). The kernel is continuous up to x=1 for
s>0; its unbounded derivative there is irrelevant to step approximation.
The all-target root count divided by F_G is O(sqrt(G)q^G), uniformly in delta,
using alpha>0 and H>=Ga. Its complement capacity is at most one, so it is also
negligible in the capacity numerator.

Dividing the complete exit-power limit by N^s gives exactly
V(s)=[J P(s)+E(s)]/[(s-alpha)m^s]. The exit integral fractions are all at most
48/121<1, for both leaves and boundary exits. Hence V strictly decreases,
whereas K strictly increases on a positive-length source window. The claimed
strict increase of D_full=K-V follows without differentiating any limit.

At t, conservation gives V(t) equal to the limiting source t-power. Strict
concavity gives 1-(1-x)^t < x^t for interior source fractions, so D_full(t)<0.
At one, direct algebra gives A[T(1)-P(1)]/[(1-alpha)m]>0. These signs, continuity,
and strict monotonicity prove uniqueness of s_star. The positive binomial
series and tail estimate are also correct: for j>M and 0<=x<=1,
x^j<=x^(M+1), including x=1. The integral formula for B_j retains rk/m and
has denominator j-alpha>0. Numerical endpoint enclosures are left to the
separately run rational certificate, not inferred from this review.

## 4. Both induction directions give the logarithmic exponent

Every child is strictly smaller than its parent. For root sources,
z>=5^(G+1)>N/m because actual delta<a. For mixed sources kz_base>N/m and r>=1
imply rkz_base>N/m; rz_base<=N/m and k<=m imply rkz_base<=N. Thus complements
are nonnegative integers below N. Boundary exits and leaves lie between one
and 48N/121<N. The all-rank-one paid path supplies a positive leaf exit at
every rank, so the finite positive base values inductively imply L(n)>0.
The denominator C_n is positive because the all-minimal target root exists.

For each fixed s>s_star, uniform offset convergence supplies H_n(s)<1 for
all sufficiently large integer n. A finite upper constant over the smaller
positive ranks then gives L(n)<=C n^s by strong induction. For each fixed
s in (t,s_star), H_n(s)>1 eventually, and the positive finite minimum gives
L(n)>=c n^s. Child zero causes no obstruction: both comparisons use L(0)=0
and s>0. The recurrence is finite and well founded even if L(n) is nonintegral.

Finally, taking arbitrary fixed exponents approaching s_star from either
side squeezes log L(n)/log n. No uniformity in s is needed; the proof needs
uniformity in the height offset for each fixed s, which was established.
It does not need an eventual sign at s_star itself, monotonicity of L(n),
a computable onset, or a convergence rate. These possible hidden assumptions
were specifically challenged and are not being used.

## Limits of the disposition

The exact scalar recurrence and its original default height are essential.
This is not a lower bound for other compilers, and the changed-height #4483
construction is unaffected. The proof establishes existence of constants
and onset ranks, not constructive bounds for them. This review does not
independently validate the numerical interval engine, physical implementation,
restoration or precision costs, or the selected multiplication theorem.
All selected assumptions and kappa remain unchanged.
