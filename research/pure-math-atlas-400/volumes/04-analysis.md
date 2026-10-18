# Volume IV — Finite moments, operator energy, and constructive analysis

This volume contains 100 proved informal statements. Most ingredients are classical; the contribution here is a self-contained chain of sufficient tools, with the hypotheses needed to connect them. No assertion of global novelty is made. Conjectures in the other volumes are separate from these proofs. All sums are finite unless explicitly stated otherwise. Hilbert spaces are finite dimensional over C, adjoints are denoted by *, and operator norms are Euclidean unless another norm is specified.

**Local precedents.** [L1: HankelMoments](../sources/04-sources.json) supplies the weighted Vandermonde factorization and its distinct-node rank hypotheses; L2 is `OddMoments.lean`; L3 is `IntegerKappaMomentTransfer20261015.lean` (concave concentration with its sign restrictions); L4 is `IntegerTensorBlockNorm20261015.lean` (pointwise energy recurrences); L5 is `TotalPositivity.lean`. Exact paths, source hashes, and declaration inventories are in that manifest. These are inspected source precedents, not new formal verifications of this volume. Historical DAG hits are separately recorded in `04-dag.json`.

External precedents include [Boyd–Vandenberghe, Convex Optimization](https://web.stanford.edu/~boyd/cvxbook/), [Potts–Tasche, approximate Prony reconstruction](https://www-user.tu-chemnitz.de/~potts/paper/prony.pdf), and [Curto–Fialkow, truncated moment extensions](https://arxiv.org/abs/math/0507067). The arguments below are independently written derivations, not quotations. Elementary calculus, finite-dimensional spectral theory and polynomial division are background facts.

## 1. Finite exponential families and quantitative convexity

For D001–D010 let p_i>0, sum p_i=1, and x_i be real, on a nonempty finite index set. Put Z(t)=sum p_i exp(t x_i), F(t)=log Z(t), and p_t(i)=p_i exp(t x_i)/Z(t).

<a id="d001"></a>

### D001 — Lemma: an exact curvature identity
**Statement.** For every real t,
$$
F''(t)=\frac12\sum_{i,j}p_t(i)p_t(j)(x_i-x_j)^2.
$$
Consequently F is convex, and strictly convex precisely when the x_i are not all equal.
**Proof.** Differentiating the finite positive sum gives F'=Z'/Z and F''=Z''/Z-(Z'/Z)^2. The latter is E_t(x²)-(E_t x)². Expanding the displayed double sum and using sum p_t=1 gives the same expression. Every weight in it is positive. It vanishes if and only if every difference x_i-x_j vanishes. Thus unequal support gives F''>0 at every t. **Use.** A strict moment-root or interpolation argument must obtain curvature from actual unequal support, not from the name “log-sum-exp.”

<a id="d002"></a>

### D002 — Lemma: differentiation of a tilted observable
**Statement.** For any fixed real g_i,
$$
\frac d{dt}E_tg=\operatorname{Cov}_t(g,x)
 =\frac12\sum_{i,j}p_t(i)p_t(j)(g_i-g_j)(x_i-x_j).
$$
If g_i=h(x_i) for a nondecreasing h, E_tg is nondecreasing.
**Proof.** The quotient rule gives derivative E_t(gx)-E_tg E_tx. Expand the double sum as in D001. When h is nondecreasing, each pairwise product has nonnegative sign. Thus the derivative is nonnegative, and integration proves the assertion. **Use.** This transports order information through a changing exponential measure without assuming that its weights stay fixed.

<a id="d003"></a>

### D003 — Lemma: a dimension-free variance bound
**Statement.** If a≤x_i≤b, then 0≤F''(t)≤(b-a)²/4 for every t.
**Proof.** Let μ=E_tx. The pointwise inequality (x_i-a)(b-x_i)≥0 yields E_tx²≤(a+b)μ-ab. Subtracting μ² gives Var_t x≤(μ-a)(b-μ). Since μ lies in [a,b], the product is at most (b-a)²/4, by completing a square around (a+b)/2. The lower bound follows from D001. **Use.** A support interval alone controls all tilted curvatures; a bound based on the number of atoms is unnecessary.

<a id="d004"></a>

### D004 — Theorem: the bounded-range exponential estimate
**Statement.** If x_i∈[a,b] and μ=sum p_ix_i, then for every real t,
$$
\sum_i p_i e^{t(x_i-\mu)}\le e^{t^2(b-a)^2/8}.
$$
**Proof.** Define G(t)=F(t)-tμ. Then G(0)=G'(0)=0 and D003 gives G''≤(b-a)²/4. Taylor's integral identity, valid for either sign of t, is G(t)=t²∫_0^1(1-u)G''(ut)du. It gives G(t)≤t²(b-a)²/8. Exponentiating proves the claim, including the degenerate case a=b. **Use.** A fully quantitative concentration input follows from support data, with no distributional approximation.

<a id="d005"></a>

### D005 — Theorem: a variance-sensitive exponential estimate
**Statement.** If Y has finite distribution, EY=0, |Y|≤b with b>0, and EY²=σ², then for 0≤t<3/b,
$$
\log E e^{tY}\le\frac{\sigma^2t^2}{2(1-bt/3)}.
$$
**Proof.** For k≥2, |EY^k|≤b^{k-2}σ². Also k!≥2·3^{k-2}: equality holds at k=2,3 and induction multiplies by k+1≥3. Absolute convergence of the exponential series therefore gives E e^{tY}≤1+(σ²t²/2)sum_{j≥0}(bt/3)^j. The geometric sum converges by the stated restriction. Apply log(1+u)≤u for u≥0. If σ=0, Y=0 on its positive-probability support and the same conclusion holds. **Use.** Small variance can improve a range-only bound substantially.

<a id="d006"></a>

### D006 — Lemma: a finite Chernoff certificate
**Statement.** For t≥0 and any real u,
$$
\sum_{x_i\ge u}p_i\le e^{F(t)-tu}.
$$
Every explicit t thus gives a sufficient upper bound on the upper tail.
**Proof.** For x_i≥u, e^{tx_i}≥e^{tu}. Summing only these nonnegative terms gives Z(t)≥e^{tu}sum_{x_i≥u}p_i. Divide by e^{tu}>0. The case t=0 is included; an empty event has probability zero. Taking the infimum over chosen admissible t preserves the bound. **Use.** This is the exact inequality that turns D004 or D005 into a tail estimate.

<a id="d007"></a>

### D007 — Theorem: the finite entropy variational formula
**Statement.** With 0 log 0=0 and KL(q||p)=sum q_i log(q_i/p_i),
$$
F(t)=\max_{q_i\ge0,\,\sum q_i=1}\{t\sum_iq_ix_i-\mathrm{KL}(q\Vert p)\},
$$
with unique maximizer q=p_t.
**Proof.** Direct substitution of p_t gives KL(q||p_t)=KL(q||p)-tE_qx+F(t). Relative entropy is nonnegative: apply log u≤u-1 to u=p_t(i)/q_i on the indices q_i>0, multiply by q_i, and sum. Equality requires q_i=p_t(i) there and no mass of p_t outside that set, hence q=p_t. This proves both the upper bound and its equality case. **Use.** A moment bound has a dual interpretation as an entropy penalty for moving mass toward expensive support points.

<a id="d008"></a>

### D008 — Theorem: total variation is controlled by entropy
**Statement.** For a probability vector q and strictly positive p,
$$
\frac12\sum_i|q_i-p_i|\le\sqrt{\mathrm{KL}(q\Vert p)/2}.
$$
**Proof.** Let A={i:q_i≥p_i}, s=q(A), r=p(A). The left side equals s-r. Grouping terms on A and its complement and applying nonnegativity of conditional relative entropy (D007's proof) gives KL(q||p)≥s log(s/r)+(1-s)log((1-s)/(1-r)). If q≠p, A is proper and nonempty, so 0<r<1. As a function of s, the binary expression and its first derivative vanish at r, and its second derivative is 1/[s(1-s)]≥4. Twice integrating gives a lower bound 2(s-r)²; endpoint values follow by continuity. The case q=p is immediate. **Use.** This converts an entropy certificate into a metric stability statement.

<a id="d009"></a>

### D009 — Lemma: entropy-stable expectations
**Statement.** If g_i∈[a,b], then
$$
|E_qg-E_pg|\le(b-a)\sqrt{\mathrm{KL}(q\Vert p)/2}.
$$
**Proof.** Subtract a from g, which does not change the difference of expectations. The positive and negative parts of q-p have equal mass d=(1/2)sum|q-p|. A function in [0,b-a] has expectation difference between -(b-a)d and (b-a)d. Apply D008. If a=b the difference is zero. **Use.** A reconstructed or approximated distribution can be substituted in any bounded observable with an explicit error budget.

<a id="d010"></a>

### D010 — Theorem: concentration of independent finite sums
**Statement.** Let independent finite-valued X_j satisfy X_j∈[a_j,b_j], and set V=sum_j(b_j-a_j)². If V>0 and u>0,
$$
\Pr\{\sum_j(X_j-EX_j)\ge u\}\le e^{-2u^2/V}.
$$
**Proof.** Independence factors the exponential moment into a product of the individual moments. D004 bounds this product by exp(t²V/8). D006 bounds the desired tail by exp(-tu+t²V/8). At t=4u/V this is exp(-2u²/V). When V=0, the sum is identically zero and its upper tail at u>0 is empty. **Use.** This supplies a sufficient sampling size for approximate finite identities; it does not turn a sampled observation into an exact identity.

## 2. Strict roots, perturbations, and finite certificates

For D011–D019 let Z(t)=sum_i a_i e^{b_it}, with finitely many a_i>0 and b_i>0, unless a different hypothesis is explicit.

<a id="d011"></a>

### D011 — Theorem: existence and uniqueness of a positive moment root
**Statement.** If A=sum a_i<1, there is exactly one τ>0 with Z(τ)=1.
**Proof.** Z is continuous, Z(0)=A<1, and Z(t)→∞ as t→∞ because any one positive summand diverges. The intermediate value theorem gives a positive crossing. Its derivative sum a_i b_i e^{b_it} is strictly positive for every t, so two crossings cannot occur. **Use / precedent.** This is a sufficient analytic closure for a finite positive exponential profile; L3 supplies the related finite-weight accounting, not an automatic root certificate.

<a id="d012"></a>

### D012 — Lemma: explicit support-only root brackets
**Statement.** Under D011, with b_min=min b_i and b_max=max b_i,
$$
\frac{\log(1/A)}{b_{\max}}\le\tau\le\frac{\log(1/A)}{b_{\min}}.
$$
**Proof.** For t≥0, A e^{b_min t}≤Z(t)≤A e^{b_max t}. Substituting t=τ and Z(τ)=1 gives both inequalities after taking logarithms and dividing by positive rates. Equality throughout is possible when all rates coincide. **Use.** This gives a finite search interval before invoking any numerical root-finding routine.

<a id="d013"></a>

### D013 — Theorem: sensitivity to a coefficient perturbation
**Statement.** Suppose a_i(s)>0 are C¹ near s_0, sum a_i(s)<1 there, and the rates are fixed. The positive root τ(s) is C¹ and
$$
\tau'(s)=-\frac{\sum_i a_i'(s)e^{b_i\tau(s)}}{\sum_i a_i(s)b_ie^{b_i\tau(s)}}.
$$
**Proof.** Let H(s,t)=sum a_i(s)e^{b_it}-1. Its t derivative is positive. The implicit function theorem therefore supplies a local differentiable root, which is the unique root from D011. Differentiate H(s,τ(s))=0 and divide by its positive t derivative. **Use.** A proposed profile change improves the root precisely when its exponentially weighted first-order cost is negative; raw item count alone is insufficient.

<a id="d014"></a>

### D014 — Theorem: the inverse moment is increasing and concave
**Statement.** For every B>0 there is a unique real T(B) with Z(T(B))=B. It satisfies T'(B)=1/Z'(T(B))>0 and T''(B)=-Z''(T(B))/Z'(T(B))³<0.
**Proof.** As t runs from -∞ to ∞, the positive-rate sum Z runs continuously and strictly increasingly from zero to infinity. Thus it has an inverse on (0,∞). Differentiating Z(T(B))=B once and twice proves the formulas; Z''>0 because every summand a_i b_i² e^{b_it} is positive. **Use.** Increasing a budget gives diminishing root improvement, a useful quantitative distinction from coefficient scaling.

<a id="d015"></a>

### D015 — Lemma: root stability from a slope certificate
**Statement.** Suppose continuous Z,W have roots Z(τ)=W(σ)=1 in an interval J, Z is differentiable there with Z'≥m>0, and |Z-W|≤ε on J. Then |τ-σ|≤ε/m.
**Proof.** Since W(σ)=1=Z(τ), |Z(σ)-Z(τ)|=|Z(σ)-W(σ)|≤ε. The mean value theorem, or integration of Z'≥m between the two roots, gives |Z(σ)-Z(τ)|≥m|σ-τ|. Divide by m. No derivative bound on W is required once its root lies in J. **Use.** A separate existence bracket plus a certified approximation error gives a rigorous root interval.

<a id="d016"></a>

### D016 — Lemma: error propagation through a finite exponential sum
**Statement.** If x_i,y_i≤M_i and a_i,\widetilde a_i are real, then
$$
|\sum a_ie^{x_i}-\sum\widetilde a_ie^{y_i}|
\le\sum_i e^{M_i}(|a_i-\widetilde a_i|+|\widetilde a_i|\,|x_i-y_i|).
$$
**Proof.** Split a_i e^{x_i}-\widetilde a_i e^{y_i} as (a_i-\widetilde a_i)e^{x_i}+\widetilde a_i(e^{x_i}-e^{y_i}). The mean value theorem bounds the second exponential difference by e^{M_i}|x_i-y_i|. Apply the triangle inequality and sum. **Use.** Coefficient, logarithm and exponent errors can be paid separately before using D015; their signs need not be guessed.

<a id="d017"></a>

### D017 — Theorem: amortizing a positive residue strictly improves a root
**Statement.** Let P,Q be continuous on an interval J, Q>0 there. Suppose every f_T=P+Q/T, for T>0 under consideration, is strictly increasing on J and has a root τ_T at level one. If S<T, then τ_S<τ_T.
**Proof.** At τ_S, f_T(τ_S)=1-Q(τ_S)(1/S-1/T)<1. A strictly increasing function crosses level one only to the right of any point at which it is below one. Hence τ_T>τ_S. **Use / precedent.** This abstracts a positive-residue argument without asserting the existence of any physical or combinatorial realization for every T.

<a id="d018"></a>

### D018 — Theorem: the first two amortization corrections
**Statement.** Let P,Q be C³ near t_0, P(t_0)=1 and p=P'(t_0)>0. The nearby solution of P(t)+uQ(t)=1 has expansion
$$
t=t_0-\frac{Q(t_0)}p u+
\left(\frac{Q'(t_0)Q(t_0)}{p^2}-\frac{P''(t_0)Q(t_0)^2}{2p^3}\right)u^2+O(u^3).
$$
**Proof.** The implicit function theorem gives a C³ solution t(u) near zero. Write t=t_0+cu+du²+O(u³), substitute Taylor expansions of P and Q, and compare coefficients. The u coefficient is pc+Q=0. The u² coefficient is pd+P''c²/2+Q'c=0. Solving gives the displayed values; bounded third derivatives on a smaller neighborhood justify the remainder. **Use.** With u=1/T, the formula quantifies both the ceiling and the next-order improvement; it is not an existence theorem for a discrete construction.

<a id="d019"></a>

### D019 — Lemma: coupling ordered rates orders the roots
**Statement.** Fix positive a_i with sum a_i<1. If b_i≥c_i>0, then the roots τ_b,τ_c of sum a_i e^{b_it}=1 and sum a_i e^{c_it}=1 obey τ_b≤τ_c. If at least one inequality is strict, so is the root inequality.
**Proof.** For t≥0, each b summand is at least its c counterpart. At t=τ_c>0, their sum is therefore at least one, and strictly greater if one rate inequality is strict. Strict monotonicity and D011 place the b root no farther right, with strictness in the latter case. **Use.** A coupling of support points gives a sufficient comparison even when solving either root explicitly is impossible.

<a id="d020"></a>

### D020 — Theorem: rational logarithm and exponential enclosures
**Statement.** For rational r≥1 put z=(r-1)/(r+1). For N≥1,
$$
0\le\log r-2\sum_{j=0}^{N-1}\frac{z^{2j+1}}{2j+1}
\le\frac{2z^{2N+1}}{(2N+1)(1-z^2)}.
$$
For rational x≥0 and integer m≥0 with x<m+2,
$$
0\le e^x-\sum_{k=0}^m\frac{x^k}{k!}
\le\frac{x^{m+1}}{(m+1)!}\frac1{1-x/(m+2)}.
$$
**Proof.** Integrating 2/(1-z²)=2sum_{j≥0}z^{2j} gives the logarithm series. In its tail replace every denominator by the first omitted denominator and sum a geometric series. For the exponential, all terms are nonnegative and the ratios after its first omitted term are at most x/(m+2)<1. Sum that geometric majorant. All endpoints are rational. **Use.** Together with D016 these produce strict finite certificates, rather than conclusions based on a floating-point display.

## 3. Concavity, transport, and extremal finite profiles

<a id="d021"></a>

### D021 — Lemma: a reverse averaging move decreases concave cost
**Statement.** Let f be concave on [0,U]. If 0≤d≤x≤y and y+d≤U, then f(x-d)+f(y+d)≤f(x)+f(y).
**Proof.** Put c=x-d and e=y+d. If c=e all quantities coincide. Otherwise x and y are the two complementary convex combinations of c,e: their coefficients lie in [0,1] and x+y=c+e. Apply concavity to each combination and add. Each endpoint value then has total coefficient one. **Use / precedent.** This is the full-hypothesis form of L3's concave concentration move; it permits strict cost improvements only when f has appropriate strict curvature and the move is nonzero.

<a id="d022"></a>

### D022 — Theorem: majorization gives a sufficient concave-cost comparison
**Statement.** Let decreasing real vectors x,y of length n lie in an interval, have equal sum, and satisfy sum_{i≤k}x_i≥sum_{i≤k}y_i for every k. For every concave f on that interval, sum f(x_i)≤sum f(y_i).
**Proof.** Induct on n. If x_1=y_1, discard these coordinates. Otherwise choose k<n with x_k≥y_1≥x_{k+1}; such k exists because x_1>y_1≥the common average≥x_n. Replace x_k,x_{k+1} by y_1,w=x_k+x_{k+1}-y_1. Complementary concavity gives f(x_k)+f(x_{k+1})≤f(y_1)+f(w). The remaining decreasing vector is x_1,...,x_{k-1},w,x_{k+2},.... Its first j entries majorize y_2,...,y_{j+1}: for j<k each is at least y_1; for j≥k the assertion is the original (j+1)-prefix inequality minus y_1. Apply induction. Constant-vector endpoint cases are immediate from the common sum. **Use.** Prefix inequalities become a universal certificate for all concave costs at once.

<a id="d023"></a>

### D023 — Theorem: exact minimum under one mass constraint and a cap
**Statement.** For x∈[0,U]^n, U>0, with sum x_i=M, a minimum of sum f(x_i), for concave f, is attained by k=floor(M/U) entries U, at most one entry r=M-kU∈(0,U), and all remaining entries zero.
**Proof.** If two coordinates are strictly between zero and U, order them x≤y and move d=min(x,U-y)>0 from the smaller to the larger. D021 does not increase cost and puts at least one coordinate at an endpoint. Repeating terminates after finitely many moves because the number of interior coordinates decreases. The conserved mass forces the stated k and r. Every admissible vector has thus been moved to the displayed multiset at no greater cost. The cases M=0 and M=nU contain no interior entry. **Use.** This constructs the optimum and retains the residual r rather than silently deleting it.

<a id="d024"></a>

### D024 — Theorem: a concave minimum has few interior coordinates
**Statement.** Let P={x∈[l,u]^n:Ax=b} be nonempty, with l<u and rank A=k. Every continuous concave function on P has a minimizer with at most k coordinates strictly between their bounds.
**Proof.** Compactness gives a minimizer. Choose one with the largest possible number of endpoint coordinates. If more than k coordinates are interior, the corresponding columns of A are dependent. There is a nonzero vector v supported on them with Av=0. Extend x+tv in both directions until its first contact with an additional bound. These two endpoints lie in P and x is their strict convex combination. Concavity makes at least one endpoint's value no larger than the minimum, so it too minimizes, with more endpoint coordinates. This contradicts the choice. **Use.** Several exact conserved quantities still leave only a bounded number of fractional coordinates to repair.

<a id="d025"></a>

### D025 — Theorem: the complementary maximum is uniform
**Statement.** If f is concave on an interval and x_1,...,x_n lie there, n≥1, then sum f(x_i)≤n f((sum x_i)/n). For strictly concave f, equality holds exactly when all coordinates are equal.
**Proof.** Finite Jensen follows by induction: combine the mean of the first n-1 coordinates, with weight (n-1)/n, with the final coordinate of weight 1/n, and use the induction hypothesis inside the first mean. Strictness follows at the first combination joining unequal values; equivalently group one value differing from the mean of the others. If all values are equal every step is equality. **Use.** D023 and D025 bracket every mass-constrained profile between explicitly constructed extremes.

<a id="d026"></a>

### D026 — Theorem: curvature pays a quantitative majorization margin
**Statement.** Suppose f is C² on [l,u], f''≤-c with c≥0, and x majorizes y as in D022. Then
$$
\sum f(y_i)-\sum f(x_i)\ge\frac c2\left(\sum x_i^2-\sum y_i^2\right).
$$
**Proof.** The function g(t)=f(t)+(c/2)t² has g''≤0 and is concave. Apply D022 to g and rearrange its two quadratic sums. In particular the right side is nonnegative, since applying D022 to -t² proves sum x_i²≥sum y_i². **Use.** A geometric spread improvement can finance an explicitly positive additional cost instead of merely giving a weak comparison.

<a id="d027"></a>

### D027 — Theorem: a finite convex-order test
**Statement.** Let X,Y have finite real distributions and equal means. Then Eφ(X)≤Eφ(Y) for every convex φ if and only if E(X-t)_+≤E(Y-t)_+ for every real t. It suffices to check t in the union of their supports.
**Proof.** Necessity uses the convex hinge φ(x)=(x-t)_+. For sufficiency, list the union of supports in increasing order. Linear interpolation of the values of any convex φ at these points has nondecreasing successive slopes. Hence on that finite support it equals an affine function plus a nonnegative linear combination of hinges at interior support points. Equal means cancel the affine part and the assumed hinge inequalities control the rest. Finally, the difference of the two expected hinges is affine between consecutive support points and zero beyond the upper support, while equal means make it zero below the lower support. Endpoint checks therefore suffice. **Use.** A continuum of convex tests reduces to finitely many exact linear inequalities.

<a id="d028"></a>

### D028 — Lemma: fractional powers are mixtures of capped linear functions
**Statement.** For 0<p<1 and x≥0,
$$
x^p=p(1-p)\int_0^\infty\min(x,t)t^{p-2}\,dt.
$$
Consequently equal-mean convex order X≤cxY implies EX^p≥EY^p for nonnegative finite X,Y.
**Proof.** For x>0 split the integral at x. Its two pieces are x^p/p and x^p/(1-p), respectively, whose sum becomes x^p after multiplication by p(1-p). For x=0 the integrand is zero. Also min(x,t)=x-(x-t)_+. D027 therefore orders the expected capped functions in the reverse direction. Integrating their nonnegative finite expectations proves the consequence; the displayed integrals converge by 0<p<1. **Use.** Hinge certificates control an entire family of noninteger power costs.

<a id="d029"></a>

### D029 — Theorem: concave sums have an ordered assignment optimum
**Statement.** Let a_1≤...≤a_n and b_1≤...≤b_n, with all relevant sums in the domain of a concave f. Among permutations π, sum_i f(a_i+b_{π(i)}) is minimized by the same order and maximized by reverse order.
**Proof.** For a≤a' and b≤b', the pair (a+b,a'+b') is more spread than (a+b',a'+b), with the same sum. D022 for two coordinates gives f(a+b)+f(a'+b')≤f(a+b')+f(a'+b). If π has an inversion, swapping that pair removes the inversion and cannot increase cost. A finite sequence of such swaps reaches the identity. The same inequality, swapping concordant pairs in the opposite direction, reaches reverse order without decreasing cost. **Use.** This gives a sufficient assignment rule when pair cost has this additive concave form; it does not assume the rule for unrelated cost tables.

<a id="d030"></a>

### D030 — Theorem: a global fractional-power perturbation bound
**Statement.** If 0<p≤1 and x,y∈[0,∞)^n, n≥1, then
$$
|\sum x_i^p-\sum y_i^p|\le\sum|x_i-y_i|^p
\le n^{1-p}(\sum|x_i-y_i|)^p.
$$
**Proof.** For p<1, the derivative of (s+1)^p-s^p is nonpositive for s>0, so this difference is at most its value one at s=0. Rescaling proves (a+b)^p≤a^p+b^p. Applying this with the smaller of x_i,y_i and their difference gives |x_i^p-y_i^p|≤|x_i-y_i|^p. Sum and use D025 for t^p on the n nonnegative differences. For p=1 all the intermediate inequalities reduce to the triangle inequality. **Use.** Unlike a derivative bound, this remains valid when a coordinate approaches zero.

## 4. Block operators and complete-boundary energy

<a id="d031"></a>

### D031 — Theorem: the sharp norm of a scalar shear
**Statement.** On H⊕H for a nonzero finite-dimensional Hilbert space H, let S_a(x,y)=(x+ay,y), a≥0. Then
$$
\|S_a\|=\frac{\sqrt{a^2+4}+a}{2}.
$$
**Proof.** In any orthonormal basis of H the operator is an orthogonal sum of identical 2×2 matrices. The positive matrix S_a* S_a has entries [[1,a],[a,1+a²]], trace 2+a² and determinant one. Its larger eigenvalue is (2+a²+a sqrt(a²+4))/2, the square of the displayed value. An eigenvector in one basis-coordinate pair attains this norm. **Use.** A shear's exact amplification is available when a coarse factor two spends too much reserve. This strengthens the elementary sufficient energy estimate in L4.

<a id="d032"></a>

### D032 — Theorem: tensor products multiply Hilbert operator norms
**Statement.** For finite-dimensional Hilbert operators A,B, ||A⊗B||=||A||·||B||.
**Proof.** Singular-value decompositions write A=UΣV* and B=WΓZ*. Tensor products of the unitary factors preserve inner products on simple tensors, hence on their span, which is the entire tensor product. The middle tensor Σ⊗Γ has singular values all pairwise products of the singular values of A and B. Their maximum is the product of the two maxima. If one operator or one relevant domain is zero-dimensional, both sides are zero. **Use.** An identity spectator tensor costs no extra norm factor, but an arbitrary invertible change of basis need not have norm one.

<a id="d033"></a>

### D033 — Lemma: direct-sum norm accounting needs no independence
**Statement.** For a finite nonempty family T_i:H_i→K_i, the operator ⊕T_i on Hilbert direct sums has norm max_i||T_i||.
**Proof.** For x=(x_i), sum||T_ix_i||²≤(max||T_i||)²sum||x_i||². This gives the upper bound. Choose an index achieving the finite maximum and a unit vector attaining its operator norm, and put zero in all other coordinates. This gives equality. Zero-dimensional blocks may be omitted; the all-zero operator has norm zero. No probabilistic assumption on the coordinates was used. **Use.** Correlation among input blocks does not invalidate a direct-sum estimate.

<a id="d034"></a>

### D034 — Theorem: growth is charged per persistent block
**Statement.** Suppose A_s=⊕_i A_{s,i} are composable operators on a fixed Hilbert block decomposition and ||A_{s,i}||≤a_{s,i}≥0. Then
$$
\|A_{m-1}\cdots A_0x\|^2\le
\sum_i\left(\prod_{s<m}a_{s,i}\right)^2\|x_i\|^2.
$$
In particular the product norm is at most max_i product_s a_{s,i}.
**Proof.** Matrix multiplication preserves the block decomposition. Repeated submultiplicativity bounds each block product by its own product of factors. Sum the squared coordinate inequalities; D033 gives the final norm statement. Empty products equal one. **Use / precedent.** This is the operator version of L4's energy recurrence. Isometries on an inactive block may be assigned factor one even while other blocks are active.

<a id="d035"></a>

### D035 — Theorem: a weighted Schur test for operator blocks
**Statement.** Let T=(T_ij), c_ij≥||T_ij||. If positive u_i,v_j and R,C≥0 satisfy sum_j c_ij v_j≤R u_i and sum_i c_ij u_i≤C v_j, then ||T||≤sqrt(RC).
**Proof.** Write z_j=||x_j||. Weighted Cauchy–Schwarz gives (sum_j c_ij z_j)²≤(sum_j c_ij v_j)(sum_j c_ij z_j²/v_j). The norm of the i-th output block is no larger than the unsquared sum. Summing the squared inequalities and applying both displayed hypotheses yields sum_i||(Tx)_i||²≤RC sum_j z_j². This proves the claim, including the case R or C is zero, when positivity forces the corresponding blocks to vanish. **Use.** Explicit row/column certificates replace an assumption that weakly coupled blocks are completely independent.

<a id="d036"></a>

### D036 — Theorem: a constructive positive weight for a stable nonnegative matrix
**Statement.** For a positive-size finite square entrywise nonnegative matrix C with spectral radius ρ(C)<1, w=(I-C)^(-1)1 is well-defined, w_i≥1, and Cw=w-1. Thus ||Cx||_w≤r||x||_w for ||x||_w=max_i|x_i|/w_i and r=max_i(1-1/w_i)<1.
**Proof.** Jordan normal form bounds powers of C by a polynomial times q^n for some ρ(C)<q<1. Thus sum_{n≥0}C^n converges and multiplying its partial sums by I-C proves it is the inverse. Its terms are entrywise nonnegative, so w≥1 and Cw=w-1. Finally |Cx|≤C|x|≤||x||_w Cw≤r||x||_w w. **Use.** A spectral stability hypothesis supplies an explicit coordinate weighting and an inspectable contraction certificate.

<a id="d037"></a>

### D037 — Theorem: a forced nonnegative recurrence has a uniform bound
**Statement.** If u_n,d_n are nonnegative vectors, u_{n+1}≤Cu_n+d_n coordinatewise, C≥0, Cw≤rw for w>0 and 0≤r<1, and ||d_n||_w≤D, then
$$
\|u_n\|_w\le r^n\|u_0\|_w+D\frac{1-r^n}{1-r}.
$$
**Proof.** Positivity and the defining inequality for w give ||Cu||_w≤r||u||_w on nonnegative vectors. The recurrence therefore implies a_{n+1}≤ra_n+D for a_n=||u_n||_w. Induction yields a_n≤r^na_0+Dsum_{j=0}^{n-1}r^j, and the finite geometric sum gives the formula. **Use.** Persistent small errors can be included in a sufficient stability theorem rather than discarded at a supposedly clean boundary.

<a id="d038"></a>

### D038 — Theorem: acyclic coupling has a finite path certificate
**Statement.** If C is an entrywise nonnegative strictly upper triangular n×n matrix, then (I-C)^(-1)=sum_{k=0}^{n-1}C^k. Each inverse entry is the sum of products of edge weights over all directed paths between the corresponding vertices, including the empty path on the diagonal.
**Proof.** Induction on k shows (C^k)_ij sums weights of length-k walks. A strictly increasing sequence of vertices has fewer than n edges, so C^n=0. Multiplication telescopes (I-C)sum_{k<n}C^k=I. The walk interpretation and acyclicity give the path formula. **Use.** Even very large individual couplings admit an exact finite propagation bound; the resulting weights may be large, so the theorem does not claim uniform conditioning.

<a id="d039"></a>

### D039 — Theorem: local prefix norms compose with boundary norms
**Statement.** Let complete boundary states be x_s=A_{s-1}...A_0x_0 with ||x_s||≤B_s||x_0||. Suppose each observable intermediate state during step s is P_{s,r}x_s with ||P_{s,r}||≤M_s. Then every such observable has norm at most (max_s M_s B_s)||x_0||.
**Proof.** For each s,r, submultiplicativity gives ||P_{s,r}x_s||≤M_s||x_s||≤M_sB_s||x_0||. Take the finite maximum. If private coordinates are used to define P_{s,r}, their initial values must either be part of x_s or be explicitly reset; without this hypothesis the displayed linear map would not describe the actual state. **Use.** A large intermediate prefix is paid once at its own step, rather than multiplied at all unrelated complete steps.

<a id="d040"></a>

### D040 — Theorem: coherent isometric gauges preserve block growth bounds
**Statement.** Let U_s be unitary identifications and let A_s=U_{s+1}D_sU_s^(-1), where every D_s uses one fixed block decomposition. Then ||A_{m-1}...A_0||=||D_{m-1}...D_0||, so D034 applies.
**Proof.** Consecutive U_s^(-1)U_s cancel, leaving U_m(D_{m-1}...D_0)U_0^(-1). Multiplication on either side by a unitary preserves operator norm: this follows directly by changing unit vectors in the defining supremum. **Use.** Moving labels or origins is harmless when the identifications match at every boundary. The explicit matching condition excludes an unjustified inference from arbitrary unrelated changes of block decomposition.

## 5. Lyapunov metrics, switching, and exact cancellation

<a id="d041"></a>

### D041 — Theorem: discrete variation of constants
**Statement.** If E_s,b_s≥0, a_s≥0 and E_{s+1}≤(1+a_s)E_s+b_s, then
$$
E_n\le E_0\prod_{s<n}(1+a_s)+\sum_{j<n}b_j\prod_{j<s<n}(1+a_s)
\le E_0e^{\sum a_s}+\sum_{j<n}b_je^{\sum_{j<s<n}a_s}.
$$
**Proof.** Induction expands the recurrence: multiplying the bound for E_n by 1+a_n extends every existing product, and the new forcing b_n has an empty following product equal to one. This gives the first formula at n+1. The second uses 1+a≤e^a separately in each nonnegative product. **Use.** Error introduced late in a process is amplified only by subsequent steps, a distinction lost in a single global worst-case factor.

<a id="d042"></a>

### D042 — Lemma: adjustable quadratic splitting
**Statement.** In a Hilbert space, for ε>0,
$$
\|x+y\|^2\le(1+\varepsilon)\|x\|^2+(1+\varepsilon^{-1})\|y\|^2.
$$
If x,y are nonzero, minimizing the right side over ε gives (||x||+||y||)².
**Proof.** Nonnegativity of ||sqrt(ε)x-ε^{-1/2}y||² gives 2 Re〈x,y〉≤ε||x||²+ε^{-1}||y||². Add ||x||²+||y||². The variable part ε||x||²+ε^{-1}||y||² is at least 2||x||||y||, because (sqrt(ε)||x||-ε^{-1/2}||y||)²≥0, with equality at ε=||y||/||x||. Zero-vector cases follow directly or by limits. **Use.** Different energy scales can be balanced before summing a coupled recurrence.

<a id="d043"></a>

### D043 — Theorem: a common quadratic metric controls arbitrary switching
**Statement.** Let Q>0 and r≥0, and suppose every operator in a family satisfies A*QA≤r²Q. Every length-n product P of operators from that family obeys
$$
\|P\|\le\sqrt{\lambda_{\max}(Q)/\lambda_{\min}(Q)}\,r^n.
$$
**Proof.** The assumed semidefinite inequality means ||Ax||_Q≤r||x||_Q, where ||x||_Q²=x*Qx. Apply this successively to each chosen factor, then use λ_min(Q)||x||²≤||x||_Q²≤λ_max(Q)||x||² at the two ends. No commutation among the factors is required. **Use.** This is a sufficient stability theorem for every switching schedule; the conditioning factor is explicitly paid.

<a id="d044"></a>

### D044 — Theorem: repeated one-direction shears grow only linearly in their parameter
**Statement.** For nonzero Hilbert spaces H,K and A:K→H, let S_A(x,y)=(x+Ay,y). For every integer n≥0,
$$
S_A^n(x,y)=(x+nAy,y),\qquad
\|S_A^n\|=\frac{\sqrt{n^2\|A\|^2+4}+n\|A\|}{2}.
$$
**Proof.** Write S_A=I+N, with N(x,y)=(Ay,0). Since N²=0, multiplication or the binomial expansion gives S_A^n=I+nN. Singular-value decomposition of A reduces this operator to scalar shear blocks with parameters n times its singular values and possible identity blocks. D031's formula is increasing in its nonnegative parameter, so the largest singular value yields the displayed norm. **Use.** Charging the norm of each identical shear separately can produce a fictitious exponential loss when the exact product has only linear growth.

<a id="d045"></a>

### D045 — Theorem: a paired shear has an explicit invariant metric
**Statement.** For real |a|<2, set
$$
T=\begin{pmatrix}1-a^2&a\\-a&1\end{pmatrix},\qquad
Q=\begin{pmatrix}1&-a/2\\-a/2&1\end{pmatrix}.
$$
Then T^TQT=Q and, for every integer n, ||T^n||≤sqrt((1+|a|/2)/(1-|a|/2)).
**Proof.** Matrix multiplication gives T^TQT=Q. The eigenvalues of Q are 1±|a|/2, both positive. Also det T=1, so the same identity implies (T^{-1})^TQT^{-1}=Q. Thus every positive or negative power preserves the Q norm. Comparing the extreme eigenvalues of Q proves the uniform bound. **Use.** An explicit paired cancellation can replace repeated independent norm estimates. The condition |a|<2 is essential for this positive metric, not a cosmetic endpoint convention.

<a id="d046"></a>

### D046 — Theorem: the Hermitian part controls an exponential
**Statement.** For any square complex matrix A, put μ=λ_max((A+A*)/2). Then ||e^{tA}||≤e^{tμ} for t≥0.
**Proof.** For y(t)=e^{tA}x, differentiation gives d||y||²/dt=y*(A+A*)y≤2μ||y||² by the spectral theorem. Differentiating e^{-2μt}||y(t)||² shows it is nonincreasing. At t=0 it equals ||x||². Take square roots and then the supremum over unit x. **Use.** Dissipative structure can give a contraction even when the crude bound e^{t||A||} is large.

<a id="d047"></a>

### D047 — Theorem: a stable matrix admits a constructive quadratic metric
**Statement.** If ρ(A)<1, the series Q=sum_{k≥0}(A*)^k A^k converges, Q≥I, and Q-A*QA=I. Consequently A is a strict contraction in its Q norm.
**Proof.** Jordan form gives ||A^k||≤C k^m q^k for some q<1, so the series of norms of (A*)^kA^k is summable. Every term is positive semidefinite and its first term is I. Multiplying partial sums by A* and A shifts the index; the limit yields Q-A*QA=I. Since I≥Q/λ_max(Q), we have A*QA≤(1-1/λ_max(Q))Q, with coefficient strictly below one. **Use.** This explicitly produces the metric needed for D043 for a single stable operator.

<a id="d048"></a>

### D048 — Theorem: a quadratic stability margin survives perturbations
**Statement.** Suppose Q>0, ||A||_Q≤r, and ||E||≤ε in Euclidean norm. Then ||A+E||_Q≤r+ε sqrt(κ(Q)). In particular this is a contraction when ε<(1-r)/sqrt(κ(Q)).
**Proof.** For any x, ||Ex||_Q≤sqrt(λ_max(Q))||Ex||≤ε sqrt(λ_max(Q))||x||≤ε sqrt(κ(Q))||x||_Q. Add the bound for Ax by the triangle inequality in the Q norm and take the supremum. **Use.** A strict analytic margin can absorb a certified numerical or algebraic reconstruction error without assuming exact equality.

<a id="d049"></a>

### D049 — Theorem: finite observability gives exact and stable recovery
**Statement.** Let O:x↦(Cx,CAx,...,CA^{m-1}x) and G=O*O. Then G>0 if and only if the only x with CA^kx=0 for 0≤k<m is zero. If G≥γI>0, the map G^{-1}O* recovers x from Ox and has norm at most γ^{-1/2}.
**Proof.** The identity x*Gx=sum_{k<m}||CA^kx||² makes its kernel exactly the stated intersection. Positive definiteness is equivalent to trivial kernel. The proposed left inverse satisfies G^{-1}O*O=I. Its product with its adjoint is G^{-1}O*OG^{-1}=G^{-1}, whose norm is at most 1/γ. Taking square roots proves the stability bound. **Use.** A supplied family of observable moments gives a sufficient recovery theorem with a condition number, rather than a dimension count alone.

<a id="d050"></a>

### D050 — Theorem: every finite-group representation can be isometrized
**Statement.** For a representation ρ of a finite group by invertible complex matrices, define Q=|G|^{-1}sum_g ρ(g)*ρ(g). Then Q>0 and ρ(h)*Qρ(h)=Q. If M=max_g||ρ(g)||, then M^{-2}I≤Q≤M²I.
**Proof.** Right multiplication permutes group elements, proving invariance of the sum. Every summand is positive definite, hence Q>0. Because inverses also occur in the group, ||ρ(g)^{-1}||≤M. Thus M^{-1}||x||≤||ρ(g)x||≤M||x|| for every g. Squaring and averaging gives both bounds. **Use.** The construction supplies a genuine isometry in an explicit metric; converting back to Euclidean norm can cost up to sqrt(κ(Q)), which must not be erased.

## 6. Hankel structure and exact finite recovery

Write m_k=sum_{i=1}^N w_i λ_i^k, with 0^0=1. Let H_M=(m_{r+s})_{0≤r,s<M} and V_{i,r}=λ_i^r. The source precedent is L1, with its transpose orientation and distinctness hypotheses retained. All results in this section are finite algebraic statements unless positive measures are expressly mentioned.

<a id="d051"></a>

### D051 — Lemma: the weighted Hankel factorization
**Statement.** Over any commutative ring, H_M=V^T diag(w)V.
**Proof.** The (r,s)-entry on the right is sum_i λ_i^r w_i λ_i^s=sum_i w_iλ_i^{r+s}=m_{r+s}. Equality of all entries proves equality of matrices. The row index of V is the node, not the exponent; this fixes the transpose orientation. **Use / precedent.** This reconstructs L1's `hankel_eq_conj` and connects a structured matrix to ordinary rank and positivity tools.

<a id="d052"></a>

### D052 — Theorem: positive nodes weights give the exact Hankel rank
**Statement.** If the λ_i are distinct real numbers, w_i>0, and M≥N, then H_M is positive semidefinite of rank N.
**Proof.** D051 gives c^TH_Mc=sum_i w_i(sum_r c_rλ_i^r)²≥0. Its kernel is exactly ker V, since every w_i is positive. The first N columns of V form a nonsingular Vandermonde matrix: its determinant is a nonzero product of pairwise node differences. Hence V has row rank N, so ker V has dimension M-N. Rank-nullity gives rank H_M=N. **Use.** Positivity prevents cancellation of nonzero weights; repeated or signed nodes require the separate treatment in D053.

<a id="d053"></a>

### D053 — Theorem: repeated nodes must first be aggregated
**Statement.** Over a field, aggregate equal nodes by adding their weights and discard nodes with aggregate weight zero. If q distinct nodes remain, then rank H_M=q whenever M≥q.
**Proof.** Aggregation does not change any moment. The factorization gives rank H_M≤q. Its leading q×q block is the product of an invertible Vandermonde transpose, an invertible diagonal matrix of nonzero aggregate weights, and the Vandermonde matrix. That block has rank q, so the full matrix has rank at least q. If q=0 all moments vanish and the conclusion is immediate. **Use.** This is the exact signed-weight correction to a support-count argument; counting labels rather than aggregated nodes can be wrong.

<a id="d054"></a>

### D054 — Theorem: the annihilating polynomial is recovered from finitely many moments
**Statement.** For N distinct real nodes and positive weights, the monic polynomial P(t)=product_i(t-λ_i) is the unique monic degree-N polynomial satisfying L(t^jP)=0 for 0≤j<N, where L(t^k)=m_k.
**Proof.** Write P=t^N+sum_{k<N}c_kt^k. The N conditions form H_N c=-(m_N,...,m_{2N-1})^T. D052 makes H_N invertible, so they have a unique solution. The actual product polynomial vanishes at every node, hence satisfies all those conditions, and must be that solution. **Use.** The proof specifies exactly which 2N moments are needed and gives a linear reconstruction step before root extraction.

<a id="d055"></a>

### D055 — Lemma: an annihilator supplies a recurrence at every later index
**Statement.** If P(t)=sum_{j=0}^N c_jt^j vanishes at every λ_i, then sum_{j=0}^N c_jm_{k+j}=0 for every integer k≥0.
**Proof.** Substitute the finite moment sum and interchange the two finite sums. The expression becomes sum_i w_iλ_i^k sum_j c_jλ_i^j=sum_iw_iλ_i^kP(λ_i)=0. No nonzero-node hypothesis is needed because k=0 uses the stated convention 0^0=1. **Use.** Once a finite support has been recovered, all future exact moments follow by recurrence rather than by repeated nonlinear fitting.

<a id="d056"></a>

### D056 — Theorem: the recurrence order counts the surviving nodes
**Statement.** If distinct nodes have nonzero weights over a field, the smallest degree of a monic polynomial giving the recurrence of D055 for every k≥0 is N.
**Proof.** The product polynomial gives order N. Conversely, if a polynomial R gives the recurrence, its equations for k=0,...,N-1 are V_N^T(w_iR(λ_i))_i=0. The Vandermonde transpose is invertible, so every w_iR(λ_i)=0. Nonzero weights force N distinct roots of R, whence deg R≥N. **Use.** This distinguishes a genuine reduction of moment complexity from an accidental cancellation of only a few leading entries.

<a id="d057"></a>

### D057 — Theorem: the generating function records reciprocal poles
**Statement.** As a formal power series,
$$
\sum_{k\ge0}m_kz^k=\sum_i\frac{w_i}{1-\lambda_i z}.
$$
If all nodes and weights are nonzero and nodes are distinct, the reduced denominator has degree N and roots 1/λ_i.
**Proof.** Expand each formal geometric series; finitely many i make coefficient comparison valid without analytic convergence. With common denominator D=product_i(1-λ_i z), the numerator evaluated at 1/λ_i is w_i product_{j≠i}(1-λ_j/λ_i), which is nonzero. Thus no factor cancels. A zero node contributes a polynomial constant rather than a reciprocal pole, so it is expressly excluded from the denominator-degree assertion. **Use.** This is a finite rational-function conclusion, not a meromorphic claim about infinitely many accumulating poles.

<a id="d058"></a>

### D058 — Theorem: 2N moments uniquely recover an N-atom positive measure
**Statement.** The moments m_0,...,m_{2N-1} of N distinct real nodes with positive weights determine those nodes and weights uniquely, up to permutation, among positive representations with at most N atoms.
**Proof.** H_N is positive definite, so any competing representation has at least N atoms by D051's rank bound. D054 recovers the same monic P from the shared moments. For the competing N-atom representation its product polynomial also solves these equations, so its nodes are precisely the roots of P. Once the nodes are fixed, the first N moment equations form an invertible Vandermonde transpose system for the weights. **Use.** The restricted comparison class matters: more-atom measures can share truncated moments unless an additional flatness condition is supplied.

<a id="d059"></a>

### D059 — Theorem: a flat positive Hankel extension gives a representing measure
**Statement.** Let N≥1 and real m_0,...,m_{2N} satisfy H_N>0, H_{N+1}≥0 and rank H_{N+1}=N. Then there is a unique positive Borel representing measure for these moments; it has exactly N real atoms.
**Proof.** Write b=(m_N,...,m_{2N-1})^T and a=H_N^{-1}b. The rank and positivity conditions give the zero Schur complement m_{2N}=a^TH_Na. On R^N with inner product u^TH_Nv, define J e_k=e_{k+1} for k<N-1 and J e_{N-1}=a. The Hankel identities and H_Na=b show J is self-adjoint. The vector e_0 is cyclic, because J^ke_0=e_k for k<N. Its spectral decomposition therefore has N distinct real eigenvalues λ_i and positive weights w_i=||projection_i(e_0)||²: a missing projection or a higher-dimensional eigenspace would contradict cyclicity. For r=u+v≤2N, 0≤u,v≤N, the identities including the Schur complement give m_r=〈J^ue_0,J^ve_0〉=sum_iw_iλ_i^r. This proves existence. The monic polynomial P(t)=t^N-sum_{k<N}a_kt^k satisfies L(P²)=0. Any positive representing measure must be supported on its zeros, since P²≥0. These are the N recovered eigenvalues, and Vandermonde uniqueness fixes the weights. **Use / attribution.** This is a fully explicit one-variable flat-extension construction in the classical Curto–Fialkow moment tradition, not a claimed new multivariable moment theorem.

<a id="d060"></a>

### D060 — Theorem: separated nodes give an explicit weight-recovery bound
**Statement.** Let real nodes satisfy |λ_i|≤R and |λ_i-λ_j|≥δ>0 for i≠j. If fixed-node weights w,\widetilde w have first N moment vectors m,\widetilde m, then
$$
\|w-\widetilde w\|_\infty\le
\left(\frac{1+R}{\delta}\right)^{N-1}\|m-\widetilde m\|_\infty.
$$
**Proof.** For the node-by-power Vandermonde V, the j-th column of V^{-1} consists of the coefficients of the Lagrange polynomial product_{i≠j}(t-λ_i)/(λ_j-λ_i). The sum of their absolute values is at most product_{i≠j}(1+|λ_i|)/product_{i≠j}|λ_j-λ_i|≤((1+R)/δ)^{N-1}. Hence ||V^{-1}||_1 obeys that bound. As m=V^Tw, the inverse transpose has induced infinity norm equal to ||V^{-1}||_1. Apply it to m-\widetilde m. For N=1 the empty products equal one. **Use.** This pays the separation dependence that an exact Vandermonde invertibility statement alone does not quantify.

## 7. Positive functionals, quadrature, and resolvent recovery

<a id="d061"></a>

### D061 — Lemma: positivity supplies a Cauchy–Schwarz inequality
**Statement.** Let L be a real linear functional on polynomials of degree at most 2d and suppose L(p²)≥0 for every p of degree at most d. Then |L(pq)|²≤L(p²)L(q²) for such p,q.
**Proof.** The quadratic L((p+tq)²)=L(p²)+2tL(pq)+t²L(q²) is nonnegative for every real t. If L(q²)>0 its discriminant is nonpositive, giving the inequality. If L(q²)=0, nonnegativity of this affine expression in t forces L(pq)=0, and the same conclusion holds. **Use.** Positive moment data define a genuine seminorm and support quotient-space constructions without assuming a representing measure in advance.

<a id="d062"></a>

### D062 — Theorem: positive odd-degree data have a Gaussian representation
**Statement.** If real m_0,...,m_{2N-1}, N≥1, have H_N>0, there are N distinct real nodes and positive weights reproducing every given moment.
**Proof.** Set b=(m_N,...,m_{2N-1})^T and choose m_{2N}=b^TH_N^{-1}b. The block matrix H_{N+1}=[[H_N,b],[b^T,m_{2N}]] has zero Schur complement, is positive semidefinite, and has rank N: its quadratic form is (x+tH_N^{-1}b)^TH_N(x+tH_N^{-1}b). D059 now constructs the N-atom measure, which certainly reproduces the original, shorter list of moments. **Use.** This proves a sufficient quadrature theorem directly from a finite positive-definiteness condition.

<a id="d063"></a>

### D063 — Theorem: a signed quadrature error is controlled by one even derivative
**Statement.** Let μ be a positive finite measure on [a,b], and let positive nodes-and-weights quadrature with N distinct nodes λ_i∈[a,b] be exact for polynomials of degree at most 2N-1. Put P(t)=product_i(t-λ_i). For f∈C^{2N}[a,b],
$$
|\int f\,d\mu-\sum_iw_if(\lambda_i)|
\le\frac{\|f^{(2N)}\|_\infty}{(2N)!}\int P(t)^2\,d\mu(t).
$$
If f^{(2N)}≥0 the error on the left before absolute value is nonnegative.
**Proof.** There is a unique polynomial H of degree below 2N matching f and f' at the nodes: the homogeneous interpolation map is injective since a nonzero polynomial of that degree cannot have N double roots, and equal dimensions imply surjectivity. For each nonnode t, subtract cP² from f-H with c chosen to make its value at t zero. Repeated Rolle's theorem, counting the double node zeros, yields c=f^{(2N)}(ξ)/(2N)! at some ξ∈[a,b]. Thus f(t)-H(t)=f^{(2N)}(ξ)P(t)²/(2N)!. At nodes the same bound is zero. Integrate and use exactness on H. **Use.** A quadrature rule becomes a rigorous inequality when the derivative sign is available.

<a id="d064"></a>

### D064 — Theorem: the Christoffel minimizer is explicit
**Statement.** Let H_N>0 be the Gram matrix of a polynomial functional L on degrees below N, and v(x)=(1,x,...,x^{N-1})^T. Among polynomials p of degree below N satisfying p(x)=1,
$$
\min L(p^2)=\frac1{v(x)^TH_N^{-1}v(x)}.
$$
The minimizing coefficient vector is H_N^{-1}v/(v^TH_N^{-1}v).
**Proof.** If c is the coefficient vector, Cauchy–Schwarz in the H_N metric gives (c^Tv)²≤(c^TH_Nc)(v^TH_N^{-1}v). The denominator is positive since v has first entry one and H_N^{-1}>0. Equality is attained by the displayed c, whose value at x is one. **Use.** This constructs the least-energy polynomial that singles out a potential atom.

<a id="d065"></a>

### D065 — Theorem: a moment matrix bounds every atom weight
**Statement.** In D064, if L is represented by a positive measure with an atom of weight w at x, then w≤1/(v(x)^TH_N^{-1}v(x)). If the measure has exactly N distinct atoms, equality holds at each atom.
**Proof.** For any p with p(x)=1, positivity of all other contributions gives L(p²)≥w. Minimize and use D064. For an N-atom measure, its Lagrange polynomial at x has degree N-1, is one at x and zero at every other atom, hence has energy exactly w. This proves the reverse inequality for the minimum. **Use.** Positivity yields both a necessary weight bound and a constructive exact selector when the finite-support hypothesis is met.

<a id="d066"></a>

### D066 — Theorem: Gaussian resolvents have an exact positive error formula
**Statement.** Under D063, for real z>b,
$$
\int\frac{d\mu(x)}{z-x}-\sum_i\frac{w_i}{z-\lambda_i}
=\frac1{P(z)^2}\int\frac{P(x)^2}{z-x}\,d\mu(x)\ge0.
$$
**Proof.** As a polynomial in x, (P(z)²-P(x)²)/(z-x) has degree 2N-1. Apply quadrature exactness to it. At every quadrature node its value is P(z)²/(z-λ_i). Expanding the integral side and dividing by P(z)² gives the identity. All denominators in the final integral are positive. **Use.** A finite recovered measure supplies a certified lower resolvent, with an exact expression for what remains.

<a id="d067"></a>

### D067 — Lemma: truncated moments control an exterior resolvent
**Statement.** Suppose positive finite measures μ,ν are supported in [-R,R], have masses M_μ,M_ν, and moment differences Δm_k. For z>R and integer K≥0,
$$
|S_\mu(z)-S_\nu(z)|\le\sum_{k=0}^K\frac{|\Delta m_k|}{z^{k+1}}
+\frac{(M_\mu+M_\nu)R^{K+1}}{z^{K+1}(z-R)},
\quad S_\mu(z)=\int(z-x)^{-1}d\mu.
$$
**Proof.** The finite geometric identity gives (z-x)^{-1}=sum_{k=0}^K x^k/z^{k+1}+x^{K+1}/[z^{K+1}(z-x)]. On the support the last term has absolute value at most R^{K+1}/[z^{K+1}(z-R)]. Integrate separately against each positive measure, subtract and apply the triangle inequality. **Use.** Approximate low moments yield a sufficient analytic approximation away from the support, with a visible truncation error.

<a id="d068"></a>

### D068 — Theorem: compression gives a variational inverse bound
**Statement.** Let M>0, b be a vector, and V have full column rank. Then
$$
b^*V(V^*MV)^{-1}V^*b\le b^*M^{-1}b.
$$
**Proof.** Complete the square:
2 Re(b*x)-x*Mx=b*M^{-1}b-||x-M^{-1}b||_M². Its maximum over all x is b*M^{-1}b. Restricting x to Vy and completing the smaller square gives maximum b*V(V*MV)^{-1}V*b. The maximum over a subspace cannot exceed the unrestricted maximum. **Use.** A computable compressed system supplies a rigorous one-sided inverse quadratic-form certificate.

<a id="d069"></a>

### D069 — Theorem: the compression error is exactly an energy projection error
**Statement.** In D068, x_*=M^{-1}b and x_V=V(V*MV)^{-1}V*b satisfy
$$
b^*M^{-1}b-b^*x_V=\|x_*-x_V\|_M^2.
$$
Moreover x_V minimizes this error over range V, and if M≥aI>0 with residual r=b-Mx_V, then ||x_*-x_V||_M≤||r||/sqrt(a).
**Proof.** Multiplication gives V*M(x_*-x_V)=0. Thus the error is M-orthogonal to range V. Pythagoras proves minimality and the identity, using x_V*Mx_V=b*x_V. Also x_*-x_V=M^{-1}r, so its squared energy is r*M^{-1}r≤||r||²/a. **Use.** A computed residual certifies accuracy without requiring the unknown exact solution.

<a id="d070"></a>

### D070 — Theorem: a Krylov subspace gives an exponential energy-error bound
**Statement.** Let aI≤M≤bI, 0<a≤b, and let x_m be the energy projection of M^{-1}v onto span(v,Mv,...,M^{m-1}v), m≥1. With κ=b/a,
$$
\|M^{-1}v-x_m\|_M^2\le4\left(\frac{\sqrt\kappa-1}{\sqrt\kappa+1}\right)^{2m}\|M^{-1}v\|_M^2.
$$
**Proof.** If a=b the one-dimensional trial space recovers the solution exactly. Otherwise set q_m(t)=T_m((b+a-2t)/(b-a))/T_m((b+a)/(b-a)), where T_m(cos θ)=cos(mθ). Then q_m(0)=1 and |q_m|≤2r^m on [a,b], r=(sqrt κ-1)/(sqrt κ+1); the latter follows from T_m((s+s^{-1})/2)=(s^m+s^{-m})/2 with s=r^{-1}. The vector (I-q_m(M))M^{-1}v lies in the stated trial space because (1-q_m(t))/t is a polynomial of degree at most m-1. Diagonalizing M bounds its squared energy error by max|q_m|² times the initial solution energy. D069's minimality proves the claim for x_m. **Use.** Low-degree moment/Krylov data suffice for a quantitative approximation of an inverse, not just for a rank test.

## 8. Intertwiners, polar repair, and finite symmetry

<a id="d071"></a>

### D071 — Lemma: an approximate intertwiner has a controlled power defect
**Statement.** For square A,B of compatible sizes and rectangular X, if ||AX-XB||≤ε, then
$$
\|A^nX-XB^n\|\le\varepsilon\sum_{k=0}^{n-1}\|A\|^{n-1-k}\|B\|^k
$$
for n≥1.
**Proof.** The exact identity is A^nX-XB^n=sum_{k=0}^{n-1}A^{n-1-k}(AX-XB)B^k. Expand its right side: all intermediate terms cancel. Submultiplicativity and the triangle inequality give the bound. For n=0 the defect is zero. **Use.** A single checked covariance residual controls every prescribed finite iterate, with the growth dependence explicit.

<a id="d072"></a>

### D072 — Theorem: spectral separation makes a Sylvester equation coercive
**Statement.** If A,B are normal and |λ-μ|≥δ>0 for every λ∈spec A, μ∈spec B, then ||X||_F≤δ^{-1}||AX-XB||_F.
**Proof.** Unitary diagonalizations reduce the equation to entries (λ_i-μ_j)Y_ij. The Frobenius norm is unchanged by the two unitary factors. Each squared entry of Y is at most δ^{-2} times the corresponding squared defect entry. Sum and take square roots. **Use.** This gives a constructive uniqueness and stability bound for a linear matrix equation. It is a Frobenius-norm statement; no unproved dimension-free operator-norm version is substituted.

<a id="d073"></a>

### D073 — Theorem: separated spectral clusters admit a nearby block-respecting map
**Statement.** Let normal A,B have mutually orthogonal spectral-cluster projections P_i,Q_i summing to identity. Suppose spectra of A on P_i and B on Q_j are δ-separated whenever i≠j. Then X_0=sum_iP_iXQ_i satisfies
$$
\|X-X_0\|_F\le\delta^{-1}\|AX-XB\|_F.
$$
**Proof.** In simultaneous eigenbases for each normal matrix, X-X_0 consists precisely of entries between unmatched clusters. Each such entry is bounded through its nonzero eigenvalue difference exactly as in D072. Orthogonality makes the squared Frobenius norms add, giving the inequality. **Use.** The conclusion is a block-respecting map, not an exact intertwiner within each cluster; that remaining algebraic distinction is explicit.

<a id="d074"></a>

### D074 — Theorem: the rectangular polar factor is the closest isometry
**Statement.** Let X:C^m→C^n, n≥m≥1, satisfy ||X*X-I||≤η<1. Then X has full column rank and U=X(X*X)^(-1/2) is an isometry. If σ_1,...,σ_m>0 are its singular values, then among all isometries V:C^m→C^n,
$$
\min_V\|X-V\|=\max_j|\sigma_j-1|,\qquad
\min_V\|X-V\|_F^2=\sum_j(\sigma_j-1)^2.
$$
U attains both minima and uniquely attains the Frobenius minimum. Moreover ||X-U||≤η/(1+sqrt(1-η)). If n=m, U is unitary, X is invertible and ||X^(-1)||≤(1-η)^(-1/2).
**Proof.** The spectral bound puts all σ_j in [sqrt(1-η),sqrt(1+η)], so they are positive. In a thin singular decomposition write X e_j=σ_j u_j for an orthonormal domain basis e_j and orthonormal codomain vectors u_j. Then Ue_j=u_j; this is also the displayed inverse-square-root formula. For any isometry V, the reverse triangle inequality gives ||(X-V)e_j||≥|σ_j-1|, proving the operator-norm lower bound. Choosing V=U makes the differences orthogonal, so its norm is exactly the maximum. For the Frobenius objective,
$$
\|X-V\|_F^2=\sum_j(\sigma_j^2+1-2\sigma_j\operatorname{Re}\langle u_j,Ve_j\rangle)
\ge\sum_j(\sigma_j-1)^2,
$$
since both vectors inside each inner product are unit vectors. Equality holds only if Ve_j=u_j for every j, because each σ_j is positive; hence U is the unique Frobenius minimizer. Both spectral endpoint deviations are at most 1-sqrt(1-η)=η/(1+sqrt(1-η)), proving the quantitative bound. In the square case full rank makes U unitary and the smallest singular value gives the inverse estimate. **Use.** This supplies a variationally optimal rectangular recovery, beyond a square polar error estimate; it also identifies the unique least-squares repair rather than merely producing one candidate. Classical polar/Procrustes attribution is recorded in the literature ledger.

<a id="d075"></a>

### D075 — Theorem: polar correction preserves an exact self-adjoint intertwiner
**Statement.** If A,B are self-adjoint, X is invertible and AX=XB, then U=X(X*X)^{-1/2} is unitary and AU=UB.
**Proof.** Taking adjoints gives X*A=BX*. Multiplying the two intertwining identities shows X*X B=B X*X. A function of a positive definite matrix, in particular its inverse square root, is a polynomial in that matrix by interpolation on its finite spectrum; hence it also commutes with B. Therefore AU=XB(X*X)^{-1/2}=UB. Directly U*U=I, and square invertibility makes U unitary. **Use.** This is a sufficient, explicit recovery step from linear equivalence to unitary equivalence under stated self-adjoint hypotheses.

<a id="d076"></a>

### D076 — Lemma: polar repair has a controlled covariance loss
**Statement.** Suppose X is square, ||A||,||B||≤1, ||AX-XB||≤ε and X satisfies D074. Its unitary polar factor obeys ||AU-UB||≤ε+2η/(1+sqrt(1-η)).
**Proof.** Write AU-UB=(AX-XB)+A(U-X)-(U-X)B. The three norms are at most ε, ||U-X|| and ||U-X||. Apply D074. **Use.** A numerical near-isometry and a numerical near-intertwiner together give an explicit approximate unitary intertwiner; exact equality is not inferred from a small residual.

<a id="d077"></a>

### D077 — Theorem: finite averaging constructs an exact nearby intertwiner
**Statement.** For finite-group representations ρ,σ by invertible complex matrices and a compatible X, put X_0=|G|^{-1}sum_gρ(g)^{-1}Xσ(g). Then ρ(h)X_0=X_0σ(h). If all group defects ||ρ(g)X-Xσ(g)||≤ε and M=max_g||ρ(g)^{-1}||, then ||X-X_0||≤Mε. In equal dimensions X_0 is invertible whenever the least singular value of X exceeds Mε.
**Proof.** In ρ(h)X_0 reindex g=kh; then ρ(h)ρ(g)^{-1}=ρ(k)^{-1} and σ(g)=σ(k)σ(h), proving the identity. Also X-ρ(g)^{-1}Xσ(g)=ρ(g)^{-1}(ρ(g)X-Xσ(g)); average the norm bound. Finally ||X_0v||≥(||Xv||-||(X_0-X)v||)≥(σ_min(X)-Mε)||v||. Strict positivity gives injectivity and hence invertibility in equal dimensions. **Use.** This is an actual sufficient equivalence-recovery theorem, not a premise that a correction gadget exists.

<a id="d078"></a>

### D078 — Theorem: a nearly invariant positive metric can be repaired
**Statement.** Let Q>0 and η=||Q^{-1/2}(A*QA-Q)Q^{-1/2}||<1. There is B with B*QB=Q and
$$
\|A-B\|\le\sqrt{\kappa(Q)}\frac\eta{1+\sqrt{1-\eta}}.
$$
**Proof.** Put T=Q^{1/2}AQ^{-1/2}. Its defect T*T-I is exactly the matrix defining η. D074 gives a unitary polar factor U with the stated unweighted distance. Define B=Q^{-1/2}UQ^{1/2}; direct multiplication proves B*QB=Q. Conjugating T-U back multiplies its norm by at most ||Q^{-1/2}||||Q^{1/2}||=sqrt κ(Q). **Use.** This repairs an explicit metric defect and shows exactly where conditioning enters.

<a id="d079"></a>

### D079 — Theorem: finite unitary averaging is a positive orthogonal projection
**Statement.** If ρ is a finite-group unitary representation, E(X)=|G|^{-1}sum_gρ(g)Xρ(g)* is the Frobenius-orthogonal projection onto its commutant. It is unital, trace preserving, completely positive, and contractive in every unitarily invariant norm.
**Proof.** Reindexing shows E(X) commutes with every ρ(h), and already commuting matrices are fixed. Thus E²=E with the stated range. Its Frobenius adjoint averages inverse conjugations, the same sum, so it is self-adjoint and therefore orthogonal. Each summand preserves I and trace and preserves positivity after tensoring with any identity, proving complete positivity of the average. Norm contraction follows from the triangle inequality and invariance under unitary conjugation. **Use.** Symmetry reduction preserves positivity and supplies a genuine projection, not merely a formal invariant expression.

<a id="d080"></a>

### D080 — Theorem: commutator defects measure distance to the commutant
**Statement.** With E from D079,
$$
\|X-E(X)\|_F^2=\frac1{2|G|}\sum_g\|X-\rho(g)X\rho(g)^*\|_F^2.
$$
In particular an average squared commutator defect at most ε² implies distance at most ε/sqrt 2.
**Proof.** Expand each squared norm. Unitary invariance makes its first two terms 2||X||_F²; the averaged cross term is 2 Re〈X,E(X)〉=2||E(X)||_F² because E is orthogonal. Pythagoras gives ||X||_F²-||E(X)||_F²=||X-E(X)||_F². Also ||X-ρ(g)Xρ(g)*||_F=||Xρ(g)-ρ(g)X||_F. **Use.** The formula gives an exact least-squares correction error for finite symmetry, useful when upgrading approximate covariants to exact ones.

## 9. Matrix functions and explicit approximation margins

For matrix-function background, see [Al-Mohy–Higham, the Fréchet derivative of the exponential](https://eprints.maths.manchester.ac.uk/1218/) and [Blanes–Casas–Murua, splitting methods](https://arxiv.org/abs/2401.01722). The finite-dimensional bounds here are derived directly; no assertion about unbounded operators is intended.

<a id="d081"></a>

### D081 — Theorem: a matrix exponential is locally Lipschitz with an explicit bound
**Statement.** For square A,B and t≥0,
$$
\|e^{tA}-e^{tB}\|\le t\|A-B\|e^{t\max(\|A\|,\|B\|)}.
$$
**Proof.** Differentiate e^{(t-s)A}e^{sB} and integrate from 0 to t to obtain e^{tA}-e^{tB}=∫_0^t e^{(t-s)A}(A-B)e^{sB}ds. The exponential series gives ||e^C||≤e^{||C||}. Thus the integrand has norm at most ||A-B|| exp((t-s)||A||+s||B||), bounded by ||A-B||e^{t max(||A||,||B||)}. Integrate. **Use.** Replacing a generator by a certified approximation has a controlled effect on a finite evolution.

<a id="d082"></a>

### D082 — Theorem: skew-adjoint evolution has no exponential perturbation loss
**Statement.** If A*=-A and B*=-B, then ||e^{tA}-e^{tB}||≤t||A-B|| for t≥0.
**Proof.** Differentiating (e^{tA})*e^{tA} shows it is constant I, so these exponentials are unitary; the same holds for B. In D081's integral identity, both exponential factors now have norm one. The integrand is bounded by ||A-B|| and integration gives the result. **Use.** Exact isometry hypotheses remove a large conditioning factor that a generic perturbation estimate would retain.

<a id="d083"></a>

### D083 — Theorem: the Lie product has a commutator-controlled local error
**Statement.** For skew-adjoint A,B and t≥0,
$$
\|e^{t(A+B)}-e^{tA}e^{tB}\|\le\frac{t^2}{2}\|[A,B]\|.
$$
**Proof.** U(s)=e^{sA}e^{sB} solves U'=(A+e^{sA}Be^{-sA})U. Comparing this with the unitary evolution generated by A+B and applying the same differentiated-product argument as D081 bounds the error at t by ∫_0^t||e^{sA}Be^{-sA}-B||ds. Differentiating the conjugated B expresses the inner difference as ∫_0^s e^{rA}[A,B]e^{-rA}dr. Its norm is at most s||[A,B]||. Integrating s proves the bound. **Use.** Commuting generators have zero splitting error, a structural fact missed by a bound depending only on their separate norms.

<a id="d084"></a>

### D084 — Theorem: repeated Lie splitting has an explicit global error
**Statement.** Under D083, for n≥1,
$$
\|e^{t(A+B)}-(e^{tA/n}e^{tB/n})^n\|\le\frac{t^2}{2n}\|[A,B]\|.
$$
**Proof.** Put h=t/n, X=e^{h(A+B)}, Y=e^{hA}e^{hB}. Both are unitary. The telescoping identity X^n-Y^n=sum_{j=0}^{n-1}X^{n-1-j}(X-Y)Y^j gives a norm bound n||X-Y||. Apply D083 at h and substitute n h²=t²/n. **Use.** This converts a local structural estimate into a sufficient step count for a prescribed total error.

<a id="d085"></a>

### D085 — Theorem: a direct local bound for symmetric splitting
**Statement.** Let M=||A||+||B||, h≥0 and S_h=e^{hA/2}e^{hB}e^{hA/2}. Then
$$
\|S_h-e^{h(A+B)}\|\le\frac{(hM)^3e^{hM}}3.
$$
**Proof.** Multiplying the absolutely convergent exponential series shows that coefficients of h^0,h^1,h^2 in S_h equal I, A+B and (A+B)²/2. At degree k the sum of norms of the product-series coefficients is at most the degree-k coefficient of e^{h||A||/2}e^{h||B||}e^{h||A||/2}=e^{hM}. The other exponential has the same majorant. Therefore the difference is bounded by 2sum_{k≥3}(hM)^k/k!. Since (j+3)!≥3!j!, this tail is at most (hM)³e^{hM}/3. **Use.** An elementary, nonoptimal but explicit order-three local certificate is available without a formal commutator expansion.

<a id="d086"></a>

### D086 — Theorem: symmetric unitary splitting has second-order global accuracy
**Statement.** If A,B are skew-adjoint, M=||A||+||B||, t≥0, and n≥1, then
$$
\|S_{t/n}^n-e^{t(A+B)}\|\le\frac{t^3M^3e^{tM/n}}{3n^2}.
$$
**Proof.** Each S_{t/n} and each exact step is unitary. Apply the same n-term telescoping identity as D084 and then D085 at h=t/n. The resulting factor n h³ equals t³/n². **Use.** This supplies an explicit sufficient accuracy guarantee for a symmetric construction; it does not claim optimal constants or validity for unbounded generators.

<a id="d087"></a>

### D087 — Lemma: a finite Taylor polynomial has a certified matrix remainder
**Statement.** For m≥0,
$$
\left\|e^A-\sum_{k=0}^m\frac{A^k}{k!}\right\|
\le\frac{\|A\|^{m+1}e^{\|A\|}}{(m+1)!}.
$$
**Proof.** Submultiplicativity bounds the tail by sum_{k≥m+1}||A||^k/k!. Write k=m+1+j and use (m+1+j)!≥(m+1)!j! to factor out ||A||^{m+1}/(m+1)!, leaving an exponential series. **Use.** A polynomial matrix computation can be converted into a rigorous matrix-function certificate with a finite error budget.

<a id="d088"></a>

### D088 — Theorem: log determinants have a spectral-floor stability bound
**Statement.** If A,B are n×n positive definite Hermitian matrices with A,B≥aI>0, then |log det A-log det B|≤(n/a)||A-B||.
**Proof.** H(s)=(1-s)A+sB remains ≥aI. Differentiating the determinant by multilinearity gives d log det H(s)/ds=tr(H(s)^{-1}(B-A)). This trace equals that of the Hermitian matrix H(s)^{-1/2}(B-A)H(s)^{-1/2}, whose norm is at most ||B-A||/a. The absolute trace is at most n times this norm. Integrate over s∈[0,1]. **Use.** A positive lower spectral bound turns approximate matrix reconstruction into an explicit determinant-error certificate.

<a id="d089"></a>

### D089 — Theorem: diagonal dominance certifies a positive spectral floor
**Statement.** For a Hermitian matrix A define a=min_i(A_ii-sum_{j≠i}|A_ij|) and b=max_i(A_ii+sum_{j≠i}|A_ij|). Then aI≤A≤bI. In particular a>0 is a sufficient positive-definiteness certificate.
**Proof.** Expand z*Az. Each off-diagonal pair has absolute contribution at most 2|A_ij||z_i||z_j|≤|A_ij|(|z_i|²+|z_j|²). Subtracting these bounds from the diagonal terms yields z*Az≥sum_i(A_ii-sum_{j≠i}|A_ij|)|z_i|²≥a||z||². Adding them proves the upper bound. **Use.** Explicit entrywise bounds provide the spectral floor required by D069, D070 and D088.

<a id="d090"></a>

### D090 — Theorem: inverse reconstruction by a finite Neumann polynomial
**Statement.** If α>0 and q=||I-αA||<1, then A is invertible and
$$
\left\|A^{-1}-\alpha\sum_{k=0}^m(I-\alpha A)^k\right\|
\le\frac{\alpha q^{m+1}}{1-q}.
$$
For aI≤A≤bI, 0<a≤b, the choice α=2/(a+b) gives q≤(b-a)/(b+a).
**Proof.** The geometric matrix series converges in norm. Multiplying its partial sums by αA=I-(I-αA) telescopes, so its limit is the inverse. Bound its tail by a geometric scalar series. In the Hermitian case the norm equals max_{λ∈spec A}|1-αλ|, bounded by the two interval endpoints; the stated α balances these endpoint magnitudes and gives the displayed q. If the spectrum does not attain the endpoints, the actual q can be smaller. **Use.** This is a constructive sufficient inverse certificate with a computable truncation degree.

## 10. Bridges between moments, positivity, and harmonic analysis

<a id="d091"></a>

### D091 — Theorem: generalized Vandermonde matrices are strictly positive
**Statement.** For r≥1, if 0<x_1<...<x_r and α_1<...<α_r are real, then det(x_i^{α_j})_{i,j=1}^r>0.
**Proof.** Put x_i=e^{t_i}. A nonzero combination of r exponentials e^{α_jt} has at most r-1 distinct real zeros: multiply by e^{-α_1t}, differentiate, and apply Rolle's theorem and induction to the r-1 remaining exponentials. A zero derivative leaves a nonzero constant, not an exception. Thus the displayed determinant is never zero on the connected chamber t_1<...<t_r, so its sign is constant there. To determine it, set t_i=t+εs_i with s_i strictly increasing and ε>0 small. Taylor expansion of the columns shows the first nonzero term is
$$
e^{t\sum\alpha_j}\varepsilon^{r(r-1)/2}
\det(s_i^{k-1})_{i,k=1}^{r}\det(\alpha_j^{k-1})_{k,j=1}^{r}/\prod_{k=0}^{r-1}k!.
$$
Both ordinary Vandermonde determinants are positive. Hence the constant sign is positive. **Use.** Ordered nodes and ordered powers produce strict minors, not merely a nonzero determinant.

<a id="d092"></a>

### D092 — Theorem: positive moment sequences have strict ordered minors
**Statement.** If 0<λ_1<...<λ_N, w_i>0 and m_k=sum_iw_iλ_i^k, then for strictly increasing nonnegative integer lists r_1<...<r_q and c_1<...<c_q, q≤N,
$$
\det(m_{r_i+c_j})_{i,j=1}^q>0.
$$
**Proof.** Factor the matrix as U^T diag(w)V, where U_{s,i}=λ_s^{r_i} and V_{s,j}=λ_s^{c_j}. Expanding the determinant by multilinearity and alternating signs, equivalently the finite Cauchy–Binet identity, expresses it as a sum over q-element node subsets S of (product_{s∈S}w_s)det U_S det V_S. Each product is strictly positive by D091, and at least one subset exists. **Use / precedent.** This strengthens the rank information in L1 to a family of positivity certificates; it is a classical total-positivity consequence, not a priority claim.

<a id="d093"></a>

### D093 — Theorem: localizing matrices put recovered atoms in an interval
**Statement.** Given real m_0,...,m_{2N-1}, let H=(m_{i+j})_{i,j<N}>0 and X=(m_{i+j+1})_{i,j<N}. If aH≤X≤bH, then the N-node positive representation in D062 is supported in [a,b].
**Proof.** The multiplication matrix used in D059/D062 is J=H^{-1}X: its first N-1 columns shift the monomial basis, and its last column is H^{-1}(m_N,...,m_{2N-1})^T. It is similar to the Hermitian matrix H^{-1/2}XH^{-1/2}, which lies between aI and bI by congruence. Every eigenvalue therefore lies in [a,b]. The construction in D059 takes exactly those eigenvalues as its nodes. **Use.** Finite matrix inequalities give a sufficient support-constrained moment representation without presupposing one.

<a id="d094"></a>

### D094 — Theorem: finitely many odd moments certify reflection symmetry
**Statement.** Let d_1,...,d_N be distinct positive real numbers. A measure with respective weights u_i,v_i at d_i,-d_i is reflection invariant if its odd moments of orders 1,3,...,2N-1 vanish; the converse also holds.
**Proof.** Put c_i=(u_i-v_i)d_i and λ_i=d_i². The vanishing equations are sum_i c_iλ_i^r=0 for r=0,...,N-1. The λ_i are distinct, so an invertible Vandermonde transpose gives c_i=0. Positivity of d_i yields u_i=v_i. These equalities immediately make every odd moment vanish and the measure reflection invariant. **Use / precedent.** This makes L2's finite odd-moment rigidity into an explicit sufficient symmetry test, with the nonzero and distinct-square assumptions visible.

<a id="d095"></a>

### D095 — Theorem: finitely many Laurent moments certify inversion symmetry
**Statement.** Let μ be a nonzero finite atomic positive measure on (0,∞), and let S be the union of its support and its reciprocal support, q=|S|. If m_r=m_{-r} for r=0,...,q-1, then μ is invariant under x↦1/x. The converse holds for every integer r.
**Proof.** The signed difference μ-(x↦1/x)_*μ is supported on the q distinct nonzero nodes in S. Its first q ordinary moments are exactly m_r-m_{-r} and vanish. Vandermonde inversion forces every signed coefficient to vanish. Thus the two measures coincide. Conversely, changing variables under an invariant finite measure gives the equality of Laurent moments, all of which are finite because its support avoids zero. **Use.** A finite exact identity list suffices for a multiplicative symmetry conclusion; an infinite moment assumption is unnecessary.

<a id="d096"></a>

### D096 — Theorem: strict polynomial positivity eventually has positive Bernstein coefficients
**Statement.** Let p(t)=sum_{j=0}^d a_jt^j satisfy p≥ε>0 on [0,1]. For integers n≥max(1,2d) with n>d²sum_j|a_j|/ε, every degree-n Bernstein coefficient of p is positive.
**Proof.** In the basis B_{k,n}=binom(n,k)t^k(1-t)^{n-k}, the coefficient is b_{k,n}=sum_j a_j(k)_j/(n)_j, with (k)_j=0 for k<j. This identity follows by expanding the binomial sum for t^j. If k≥j, compare the products of (k-r)/(n-r) and k/n for r<j; each factor lies in [0,1] and differs by at most 2r/n, so their product difference is at most j(j-1)/n. If k<j, (k/n)^j≤j/n≤j²/n gives the same weaker d²/n bound. Thus |b_{k,n}-p(k/n)|≤d²sum|a_j|/n<ε, proving positivity. Constant polynomials are immediate. **Use.** Strict positivity has an explicit finite coefficient certificate; no analogous assertion is made for polynomials touching zero.

<a id="d097"></a>

### D097 — Lemma: Bernstein degree elevation preserves certified bounds
**Statement.** If p=sum_{k=0}^n b_k B_{k,n}, its degree-(n+1) coefficients are c_0=b_0, c_{n+1}=b_n and c_k=(k/(n+1))b_{k-1}+(1-k/(n+1))b_k. Hence any common interval containing the b_k also contains every c_k.
**Proof.** The binomial identities give B_{k,n}=((n+1-k)/(n+1))B_{k,n+1}+((k+1)/(n+1))B_{k+1,n+1}. Substitute into the expansion and collect each coefficient. The interior formulas are convex combinations and the endpoints are unchanged. **Use.** A strict sign or interval certificate remains valid under refinement, allowing D096's certificate to be reused at every higher degree.

<a id="d098"></a>

### D098 — Theorem: finite group convolution has a universal norm certificate
**Statement.** For a finite group G, Hilbert-valued functions f, and coefficients a_g, define T_af(h)=sum_g a_g f(hg). Then ||T_a||_{2→2}≤sum_g|a_g|. If a_g≥0, equality holds whenever the value space is nonzero.
**Proof.** Each right translation f(h)↦f(hg) is unitary because h↦hg is a bijection. The triangle inequality for the Hilbert direct-sum norm gives ||T_af||_2≤sum|a_g|||f||_2. If the coefficients are nonnegative, any nonzero constant function is an eigenvector with eigenvalue sum a_g, attaining this bound. **Use.** An average of arbitrary translations is a contraction when its coefficient absolute sum is at most one; no independence of its input entries is involved.

<a id="d099"></a>

### D099 — Theorem: characters give an exact finite abelian norm test
**Statement.** Let G be a product of finite cyclic groups. For T_a in D098 acting on complex scalar-valued functions, and each character χ, put α_χ=sum_g a_gχ(g). Then ||T_a||=max_χ|α_χ|. It is unitary exactly when every |α_χ|=1, and a contraction exactly when all are at most one.
**Proof.** On a cyclic factor the geometric sum of a nontrivial root of unity is zero; multiplying these identities over factors shows the normalized characters are orthonormal. Their number is |G|, so they form a basis. Since χ(hg)=χ(h)χ(g), T_aχ=α_χχ. Diagonalization in this orthonormal basis gives its norm and both equivalences. The same conclusions hold for functions valued in a nonzero complex Hilbert space: expand in the finite character basis with Hilbert-valued coefficients, and use a nonzero character times a fixed nonzero vector to attain each multiplier norm. **Use.** This supplies a complete, inspectable contraction test rather than inferring a full regular-representation norm from one selected character.

<a id="d100"></a>

### D100 — Theorem: a lazy generating convolution has a quantitative mixing bound
**Statement.** In D099 let a be a symmetric probability vector, a_g=a_{g^{-1}}, with a_e>0 and support generating G. For nontrivial G set η=max_{χ≠1}|α_χ|. Then η<1, and for every mean-zero f,
$$
\|T_a^nf\|_2\le\eta^n\|f\|_2.
$$
Also (1/2)sum_g a_g||f(\cdot g)-f||_2²=〈f,(I-T_a)f〉≥(1-max_{χ≠1}α_χ)||f||_2².
**Proof.** Symmetry makes every α_χ real. It is a convex average of unit complex numbers χ(g). Equality |α_χ|=1 requires all positively weighted phases to be equal. The positive identity weight makes that common phase one; the generating support then forces χ trivial. Finitely many remaining characters give η<1. A mean-zero function has no trivial-character component, so D099's diagonalization proves the power bound. Expanding the squared translation differences and using symmetry gives the Dirichlet identity; diagonalization gives its lower bound. The trivial group has only the zero mean-zero function and can be treated separately. **Use.** The stated elementary support hypotheses construct a strict contraction on a specified subspace, not merely a necessary spectral obstruction.

## How these tools fill specific gaps

The sufficient bridges are: finite support and curvature to strict moment roots (D001–D020); conserved quantities to constructive concave-cost minima (D021–D030); exact block geometry to norm bounds without independence assumptions (D031–D050); moment positivity to explicit recovery and approximation (D051–D070); approximate linear data to genuine symmetry or isometry (D071–D080); and finite coefficient/error data to analytic certificates (D081–D100). Each bridge includes its own conditioning or support assumptions. Applications beyond these assumptions remain separate mathematical questions in the companion volumes.

