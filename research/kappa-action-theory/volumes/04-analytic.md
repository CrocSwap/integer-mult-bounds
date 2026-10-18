# Volume A — Admission and uniform transfer for changed contracts

This volume supplies quantitative admission and all-size transfer theorems for explicitly changed contracts. It does not claim another optimization of the fixed words closed by PR #2863. A numerical profile is never an implementation: native correctness, dirty-state restoration, label compatibility and a physical caller remain distinct input certificates supplied by the other volumes or a future construction. The conclusions below are exactly the stated sufficient bounds, not an unproved multiplication algorithm. No exact new κ is evaluated.

Uncounted setup: all profiles are finite nonnegative weighted lists H=(h_r) of positive ranks 0<r<m. The live normalization W and parent width m are positive. For 0≤a<1 put p=1−a and Φ_H(a)=Σ_r h_r(r/m)^p/W. Additional charges are included as further paid rows or as an explicitly bounded nonnegative normalized toll. Natural multiplicities are required for actual callers; real weights are allowed only in amortized arithmetic certificates. A fully specified native or physical rewrite must already preserve its declared input/output interface before any profile comparison is applied. The symbolic cost c_p of a fixed paid row list C is Σ C_r r^p. Γ denotes a claimed strictly positive complete saving in these raw units. Vector norms are Euclidean unless explicitly marked ∞; matrix and bilinear norms are induced by the specified vector norms. No statistical independence is assumed for correlated input blocks.

Precedents: prior atlas PR #2849, especially D011–D040, is background and is not recounted as new generic moment or norm theorems. PR #2857 and #2863 motivate changed-contract budgets after exact fixed-word packing attainment. The inspected local IntegerKappaRecursion, IntegerKappaToolkit, IntegerTensorBlockNorm and CommunityPrecisionProfile sources supply scoped precedents; they were read, not freshly kernel-checked. Each counted result adds a quantified admission, error, resource or uniformity consequence to its stated contract.


<a id="a001"></a>

### A001 — Theorem: A portfolio of charged native substitutions

**Statement.** Fix a complete admitted profile H with Φ_H(a)≤1−η, η≥0. For finitely many interface-correct substitutions, let R_j be the removed rows and C_j all added native, transport, cleanup and retained-workspace rows. If removals are disjoint and g_j=Σ(R_j)_r r^p−Σ(C_j)_r r^p satisfy Σ_j g_j>0, the simultaneous complete profile has Φ_new(a)≤1−η−Σ_j g_j/(Wm^p).

**Proof.** Disjoint removals let us form the nonnegative list H_new=H−Σ_j R_j+Σ_j C_j. Its raw p-cost is exactly the old cost minus Σ_j g_j, since each physical row has been charged once. Divide by the positive Wm^p. Interface correctness is an explicit input, so this arithmetic does not silently supply a caller or a restoration step. The displayed positive sum gives a strict normalized margin even if the original margin η is zero.

**Action.** For independently proved native rewrites, enter every added stage in C_j and add their certified gains; this produces a strict caller-admission margin without summing unrelated κ decimals.

**Frontier target.** complete changed-contract paid moment.

<a id="a002"></a>

### A002 — Theorem: A compensating-operation allowance for a two-child merge

**Statement.** Let a,b>0, 0<p<1 and a+b<m. Replacing paid ranks a,b by a+b and adding rows of raw cost c_p≤p(1−p)ab(a+b)^(p−2)/2 lowers complete raw cost by at least p(1−p)ab(a+b)^(p−2)/2.

**Proof.** For f(t)=t^p and positive lower integration cutoff, the mixed fundamental theorem of calculus gives f(a)+f(b)−f(a+b)=p(1−p)∫_0^a∫_0^b(x+y)^(p−2) dy dx. The improper integral converges because its value is the finite left side; alternatively take positive cutoffs and pass monotonically to the limit. Throughout the rectangle, x+y≤a+b, so the integrand is at least (a+b)^(p−2). The saving is therefore at least p(1−p)ab(a+b)^(p−2). Subtract the allowed positive compensation cost.

**Action.** After a native or tensor construction licenses a real merge, this explicit lower bound is a spendable allowance for its corrective consumer; do not count an unpriced merge.

**Frontier target.** complete changed-contract paid moment.

<a id="a003"></a>

### A003 — Theorem: An additive allowance for a merge tree

**Statement.** For positive ranks a_1,…,a_k with k≥2 and S=Σa_i<m, replacing all k children by rank S saves at least p(1−p)S^(p−2)Σ_{i<j}a_i a_j. Any complete adapter cost strictly below this amount leaves a strict gain.

**Proof.** Merge a_1 and a_2, then their sum with a_3, and continue. A002 before its half-budget deduction bounds the j-th merge saving below by p(1−p)(Σ_{i<j}a_i)a_j(Σ_{i≤j}a_i)^(p−2). Since each partial sum is at most S and p−2<0, replace its power by the smaller S^(p−2). Summing gives the displayed pair sum. Intermediate p-costs cancel exactly, so the total bound is independent of whether those intermediate merge nodes are separately materialized. A physical construction must choose which paid adapters actually occur.

**Action.** Price a multi-output fusion against one total allowance and select a merge tree whose actual adapters fit it; the total budget includes every intermediate operation.

**Frontier target.** complete changed-contract paid moment.

<a id="a004"></a>

### A004 — Theorem: A paid width-reduction rule

**Statement.** If a correct helper replacement reduces one recursive width r to r−d, where 0<d≤r<m, it may add any rows of raw cost at most (p d r^(p−1))/2 and still save at least (p d r^(p−1))/2.

**Proof.** Integrating f′(t)=p t^(p−1) from r−d to r gives r^p−(r−d)^p. Because p−1<0 and t≤r, the integrand is at least p r^(p−1). This proves a raw saving at least p d r^(p−1), including d=r by continuity at zero. Subtract the stated complete added-row budget. If r−d=0, omit that zero child rather than evaluating it as a nonpositive-rank row.

**Action.** For a new dirty-helper contract, convert a proved width reduction into a concrete maximum charge for compensation and cleanup.

**Frontier target.** complete changed-contract paid moment.

<a id="a005"></a>

### A005 — Theorem: Transport-paid concentration with a quantitative gap

**Statement.** Let 0<r≤s, 0<d≤r and s+d<m. Replacing ranks (r,s) by (r−d,s+d) saves at least G=p(1−p)d(s−r+d)(s+d)^(p−2). Thus a valid physical redistribution with complete transport cost below G is strictly favorable.

**Proof.** The raw saving equals ∫_0^d[p(r−t)^(p−1)−p(s+t)^(p−1)]dt. Writing the difference of derivatives as p(1−p)∫_{r−t}^{s+t}u^(p−2)du bounds it below by p(1−p)(s−r+2t)(s+d)^(p−2). Integrate in t. The endpoint r=d follows by a limit from smaller d. Subtracting any transport cost less than G preserves strict positivity. This theorem neither splits unsplittable helpers nor creates temporal windows.

**Action.** Use G as a ceiling on the actual movement bill of a proved whole-role redistribution in a changed template; frozen PR #2863 packing alone is not reopened.

**Frontier target.** complete changed-contract paid moment.

<a id="a006"></a>

### A006 — Theorem: Simultaneous shrink-and-enlarge helper accounting

**Statement.** Suppose a valid rewrite shrinks widths r_i by d_i∈[0,r_i], enlarges widths s_j by e_j≥0, and adds raw overhead c_p, with all final widths below m and every s_j>0. Its gain is at least Σ_i p d_i r_i^(p−1)−Σ_j p e_j s_j^(p−1)−c_p. Positivity of this explicit expression suffices.

**Proof.** The shrink terms obey A004 before its half-budget deduction. For an enlargement, (s+e)^p−s^p=∫_s^{s+e}p t^(p−1)dt≤p e s^(p−1), because the derivative decreases. Add these lower and upper estimates with their correct signs and then subtract every overhead row. The resulting bound does not assume that all helper changes have the favorable sign.

**Action.** Screen a coupled native redesign that narrows some helpers but widens others; retain the enlarged-helper penalty instead of advertising only the narrowed quartet.

**Frontier target.** complete changed-contract paid moment.

<a id="a007"></a>

### A007 — Theorem: A parent-width redesign threshold including all added work

**Statement.** Let an old profile satisfy Σh_r r^p≤(1−η)Wm^p, with 0≤η<1. A correct new parent geometry with live count W′>0, parent width m′>max r and the same rows plus raw added cost c_p is admitted whenever (1−η)Wm^p+c_p<W′(m′)^p. In particular m′>[( (1−η)Wm^p+c_p)/W′]^(1/p) is a sufficient explicit target.

**Proof.** The old raw upper bound plus the added rows bounds the entire new raw numerator. Division by W′(m′)^p gives a quantity below one under the displayed inequality. Taking a positive p-th root preserves order. W′ counts actual live families in the new source contract; it cannot be increased by naming unused scratch live. This restriction belongs to the declared geometry input.

**Action.** Before building a changed coverage or source-width contract, solve this threshold with its full adapter cost to specify the width and live-stock target it must actually realize.

**Frontier target.** changed coverage/source geometry admission.

<a id="a008"></a>

### A008 — Theorem: Robust admission under an operation-price box

**Statement.** Let d_j be the old-minus-new count of each explicitly priced primitive, and suppose its price w_j lies in [l_j,u_j], 0≤l_j≤u_j. A gain of at least G=Σ_{d_j≥0}d_j l_j+Σ_{d_j<0}d_j u_j holds for every allowed price. If G>0, the rewrite is strictly favorable throughout the box.

**Proof.** When d_j≥0, multiplication preserves w_j≥l_j; when d_j<0, multiplication reverses w_j≤u_j. Add the resulting lower bounds for d_jw_j. Equality is attained at an endpoint of each independent interval, so the bound is exact for the declared box, although it may be conservative if prices are constrained jointly. All scalar, frame and movement primitives must appear as separate coordinates if their prices differ.

**Action.** Produce one safe native-rewrite decision valid over unresolved but bounded transport or precision tariffs, without assuming the cheapest endpoint for every unfavorable operation.

**Frontier target.** native/physical tariff uncertainty.

<a id="a009"></a>

### A009 — Theorem: Signed profile gains certified on an exponent interval

**Statement.** For 0<r<m let q_r=r/m. Let d_r=h_old,r/W−h_new,r/W be signed normalized count differences and 0≤a_0≤a_1<1. Then the complete gain on every a∈[a_0,a_1] is at least G=Σ_{d_r≥0}d_r q_r^(1−a_0)+Σ_{d_r<0}d_r q_r^(1−a_1). If G exceeds any uniformly bounded added toll, the redesign improves every exponent in that interval.

**Proof.** For q∈(0,1), q^(1−a) increases with a. A positive coefficient is therefore bounded below at a_0, while a negative coefficient is bounded below at a_1. Adding these separate term bounds proves the assertion, including zero coefficients. An added toll is subtracted once from this complete signed lower bound. Different live normalizations can first be absorbed into the signed coefficients as written.

**Action.** Validate an entire proposed exponent window from two endpoint evaluations and a complete signed profile, avoiding a floating-point optimum at a single guessed exponent.

**Frontier target.** uniform symbolic paid-moment margin.

<a id="a010"></a>

### A010 — Theorem: A higher-rank decoder pays its own conversion

**Statement.** Let 0<u<v<m and let M>0 satisfy M/u and M/v integral. Replacing M/u rank-u children by M/v rank-v children saves at least M(1−p)(v−u)v^(p−2). A correct decoder with all added conversion rows below that bound strictly improves the profile.

**Proof.** The two raw costs are M u^(p−1) and M v^(p−1). Their difference is M(1−p)∫_u^v t^(p−2)dt, which is at least M(1−p)(v−u)v^(p−2) because p−2<0. The integrality hypotheses ensure the displayed replacement lists can be actual multiplicities, though the endpoint correctness still comes from a decoder construction. Subtract its full conversion cost to obtain the strict conclusion.

**Action.** Target fewer, larger paid children in a genuine changed decoder; the formula gives an explicit budget for the basis conversion and final readout.

**Frontier target.** rank-shape decoder/consumer interface.

<a id="a011"></a>

### A011 — Theorem: A strict paid margin yields an explicit exponent interval

**Statement.** Assume 0<Φ_H(a)≤1−η with 0<η<1 and let L=max_{h_r>0}log(m/r). For 0≤h<min(1−a,log(1/(1−η))/L), the same complete profile satisfies Φ_H(a+h)<1.

**Proof.** Each term q_r^(1−a−h) is q_r^(1−a)exp(h log(m/r))≤q_r^(1−a)e^(hL). Summing gives Φ_H(a+h)≤(1−η)e^(hL), strictly below one by the stated upper bound on h. L>0 because every active rank is strictly below m. The restriction a+h<1 keeps the declared exponent domain. This is an interval output from a concrete complete margin, with no numerical new saving evaluated.

**Action.** Turn a proved changed-contract margin from A001–A010 into an open admissible exponent interval for the caller.

**Frontier target.** complete changed-contract paid moment.

<a id="a012"></a>

### A012 — Theorem: One margin can finance both exponent gain and an added stage

**Statement.** Under A011 with 0<η≤1/2, take 0<h≤min(η/(4L), (1−a)/2). If a new required stage has normalized cost at a+h at most η/4, the complete augmented profile at a+h is at most 1−η/2.

**Proof.** For 0≤x<1, e^x≤1/(1−x), by comparing their power series coefficientwise. Hence the old profile at a+h is at most (1−η)/(1−η/4). Its distance below one is (3η/4)/(1−η/4)≥3η/4. Adding the fully priced stage costs at most η/4 and leaves a margin at least η/2. The smaller-domain bound on h ensures a+h<1; no independence between the old work and the new stage is needed for this additive upper bound.

**Action.** Reserve a quantified share of a native saving for an unavoidable consumer instead of spending the entire margin on a larger exponent.

**Frontier target.** complete changed-contract paid moment.

<a id="a013"></a>

### A013 — Theorem: A certified neighborhood of a contract parameter

**Statement.** Let valid complete contracts depend on θ in a specified box, with normalized bill F(θ) satisfying |F(θ)−F(θ₀)|≤Σ_j K_j|θ_j−θ₀,j| there. If F(θ₀)≤1−η and Σ_j K_j|θ_j−θ₀,j|≤η/2, every such contract is admitted with margin at least η/2.

**Proof.** Add the Lipschitz bound to F(θ₀)≤1−η. The result is F(θ)≤1−η+η/2. When F is differentiable on a convex parameter box and |∂_jF|≤K_j, the required Lipschitz hypothesis is itself proved by integrating the derivative of F along the straight line from θ₀ to θ. Validity of endpoint/ownership interfaces throughout that box is a separate explicit hypothesis and cannot be inferred from continuity of the bill.

**Action.** Convert rigorous derivative bounds for precision, scalar tariffs or a parameterized valid caller into a safe search region, rather than recomputing the full bill at every nearby choice.

**Frontier target.** robust changed-contract parameter selection.

<a id="a014"></a>

### A014 — Theorem: A finite number of good blocks finances bad boundary blocks

**Statement.** At one exponent, suppose a valid block type has normalized bill at most 1−g, g>0, and a boundary type at most 1+b, b≥0, under the same normalization per block. For any prescribed number B≥1 of boundary blocks, using G> B b/g good blocks yields a strict complete average below one, provided all cross-block work is already counted.

**Proof.** The total excess above the number of blocks is at most −Gg+Bb. The displayed strict integer inequality makes it negative. Division by G+B>0 gives the normalized average. An explicit valid choice is G=⌊Bb/g⌋+1. If a cross-block adapter is not counted in either block type, add its normalized total to Bb before applying the same argument; the theorem never treats that adapter as free.

**Action.** Choose a finite repetition count that absorbs a bounded startup/termination defect around a profitable native/consumer block.

**Frontier target.** finite block assembly with explicit boundary charges.

<a id="a015"></a>

### A015 — Theorem: Coupled complex and bit margins give one common gain window

**Statement.** Let two complete primitive bills Φ_C and Φ_B have margins 0<η_C,η_B<1 at a common a, and active rates bounded by L_C,L_B>0 as in A011. Every 0<h<min(1−a,log(1/(1−η_C))/L_C,log(1/(1−η_B))/L_B) is simultaneously admissible for both.

**Proof.** Apply A011 to each finite positive profile using the same h. Both resulting inequalities are strict, so their conjunction holds on the intersection of the two explicitly displayed open intervals. There is no addition of the separate saving parameters and no assumption that an improved complex profile moves an unchanged bit boundary. Any further outer conversion must be applied only within this common interval and must pay its own declared losses.

**Action.** After changing the binding complex supplier, retain a certified common interval with BIT before claiming that an outer transfer can use the new margin.

**Frontier target.** joint complex/BIT admission.

<a id="a016"></a>

### A016 — Theorem: A curvature-aware advance with a reserved remainder

**Statement.** At a with Φ(a)≤1−η let D=Φ′(a)>0, Q=Φ″(a)>0 and L be the largest active rate. If 0<h<1−a, hL≤1/2, hD≤η/2 and h²Q≤η/4, then Φ(a+h)≤1−η/4.

**Proof.** Taylor with integral remainder gives Φ(a+h)=Φ(a)+hD+∫_0^h(h−t)Φ″(a+t)dt. Every second-derivative summand grows by at most e^(Lt)≤e^(1/2)<2. Thus the integral is at most h²Q. Substitute the three bounds to obtain 1−η+η/2+η/4. An entirely explicit choice is any positive h bounded by min((1−a)/2,1/(2L),η/(2D),sqrt(η/(4Q))). Positive-profile derivatives exist because the sum is finite.

**Action.** Use the actual complete profile curvature to choose a safer, often less conservative admissible advance while retaining a quantified unused margin.

**Frontier target.** strict symbolic exponent continuation.

<a id="a017"></a>

### A017 — Theorem: Logarithmic rank bins preserve a quantified admission margin

**Statement.** Partition active ratios q=r/m into bins [l_j,u_j] with 0<l_j≤u_j<1 and log(u_j/l_j)≤d. For weights n_j=Σ_bin h_r/W, let U=Σn_j u_j^p and L₀=Σn_j l_j^p. Then L₀≤Φ≤U≤e^(pd)L₀. Thus U<1 is a rigorous sufficient admission certificate after compression.

**Proof.** The map q↦q^p increases, so termwise bin endpoints bound each original contribution. Also u_j^p≤e^(pd)l_j^p from the logarithmic width restriction. Multiply by nonnegative n_j and sum to prove every displayed inequality. This compression does not alter the physical profile: it only supplies a conservative finite upper bill. A claimed margin η survives whenever the computable U is at most 1−η.

**Action.** Compress a large changed-contract histogram into a small auditable exponent certificate with a known multiplicative loss.

**Frontier target.** large-profile exact admission certificates.

<a id="a018"></a>

### A018 — Theorem: A derivative-capped one-step admission certificate

**Statement.** Let Φ(a)≤1−η, and suppose a bound M≥Φ′(t) is certified for t∈[a,a+b], b>0, a+b<1. Every h∈[0,b] with hM≤η/2 leaves Φ(a+h)≤1−η/2. One computable choice is M=L e^(Lb)Φ(a).

**Proof.** Integrate Φ′ over [a,a+h] to get Φ(a+h)−Φ(a)≤Mh. For the stated computable cap, each derivative term has its rate at most L and grows by at most e^(Lb) from its value at a, so Φ′(t)≤L e^(Lb)Φ(a). The result uses a whole-interval derivative bound rather than an uncertified Newton tangent, which would underestimate a convex function.

**Action.** Turn a symbolic Newton-style continuation proposal into a rigorous lower advance that can be entered in the outer admission ledger.

**Frontier target.** certified continuation rather than floating root search.

<a id="a019"></a>

### A019 — Theorem: A local subtree improvement has an exact caller weight

**Statement.** Consider a normalized two-level profile with parent contributions c_i>0 and complete child bills B_i≥0, so its recursive part is Σ_i c_i B_i. Replacing one child contract j by an interface-correct complete bill B′_j≤B_j−σ lowers the caller bill by at least c_jσ. If extra caller adapters cost at most c_jσ/2, the complete saving is at least c_jσ/2.

**Proof.** Every unchanged summand cancels in the old-minus-new difference. The remaining difference is c_j(B_j−B′_j), at least c_jσ. Subtract the stated caller adapter charge. This formula remains valid when child work is amortized, because c_j is its actual nonnegative occurrence weight. A change of labels or output ABI must be licensed by the declared interface correctness; otherwise there is no valid substitution.

**Action.** Prioritize a genuinely improved local consumer by its actual outer occurrence weight and reserve half its benefit for caller integration.

**Frontier target.** consumer replacement inside a retained recursive caller.

<a id="a020"></a>

### A020 — Theorem: A finite outer ledger survives a quantified joint perturbation

**Statement.** Let strict outer constraints be g_i(x)>0 on a convex box, with g_i(x₀)≥η_i>0 and |∂_j g_i|≤K_ij throughout. Any x in the box satisfying Σ_j K_ij|x_j−x₀,j|≤η_i/2 for every i satisfies every strict constraint with margin η_i/2.

**Proof.** Parameterize the line x₀+t(x−x₀). The fundamental theorem of calculus and triangle inequality give |g_i(x)−g_i(x₀)|≤Σ_jK_ij|x_j−x₀,j|. Subtract this bound from g_i(x₀). The finite family of inequalities therefore remains positive simultaneously. All altered parameters, including normalization, precision and restoration costs, must be coordinates of x; leaving one out invalidates the supplied derivative certificate.

**Action.** Carry a proved primitive improvement through a fully specified finite outer slack ledger symbolically, without evaluating a new κ or assuming unchanged secondary inequalities.

**Frontier target.** modern outer transfer with all inequalities retained.

<a id="a021"></a>

### A021 — Theorem: An explicit batch size absorbs sublinear integration work

**Statement.** Suppose B copies of a correct profitable module save raw cost Bg, g>0, and the complete additional integration bill is at most c B^θ, c≥0 and 0≤θ<1. Every integer B>(2c/g)^(1/(1−θ)) retains a total gain greater than Bg/2.

**Proof.** The displayed inequality implies B^(1−θ)>2c/g, hence cB^θ<Bg/2. Subtract this upper bound from the actual total saving Bg. The requirement θ<1 is essential to choosing a finite threshold. All fixed endpoint and coefficient-preparation charges must be included in cB^θ, or added explicitly before this argument; a setup cost is not erased by the word amortized.

**Action.** Choose a finite replication scale for a changed contract with a proved sublinear boundary bill, rather than treating its boundary as asymptotically free.

**Frontier target.** batch implementation of a new native/consumer contract.

<a id="a022"></a>

### A022 — Theorem: A rooted-tree potential accounts for every internal restoration

**Statement.** On a finite rooted execution tree let the actual nonnegative node cost c(v) obey c(v)≤b(v)+P(v)−Σ_{u child of v}P(u), with P≥0 and nonnegative benchmark b. Then the complete cost is at most Σ_v b(v)+P(root). If this upper bound is below a reference bill, the whole tree is strictly cheaper.

**Proof.** Sum the node inequalities over the finite tree. Every potential of a nonroot vertex occurs once positively in its own inequality and once negatively in its parent inequality, so it cancels. The only remaining potential is P(root). This cancellation includes leaf inequalities: omitting a leaf restoration would omit its inequality and leave an unjustified negative credit. No sign condition on individual potential differences is needed.

**Action.** Prove a uniform recursive amortization invariant that pays a dirty workspace exactly when its final consumer closes it.

**Frontier target.** recursive restoration/retention ledger.

<a id="a023"></a>

### A023 — Theorem: Finite-state cycle certificates construct amortized potentials

**Statement.** Let a finite directed graph have edge costs e(u,v), and fix c such that every directed cycle has total e-cost at most c times its length. Define P(u) as the largest total weight of a path starting at u for weights e−c, allowing the empty path. Then P is finite, computable from simple paths, and every path of L edges costs at most cL+P(start)−P(end).

**Proof.** A repeated vertex in a path encloses a cycle of nonpositive e−c weight. Removing that cycle cannot decrease the path weight. Thus the maximum P(u) is achieved by a simple path, of length at most the number of vertices minus one, and is finite. Concatenating edge (u,v) with a maximizing path from v proves e(u,v)−c+P(v)≤P(u), since the concatenated walk is bounded by P(u). Summing along a path telescopes. Enumerating simple paths is an explicit finite construction, not a polynomial-time claim.

**Action.** Convert a finite library of fully priced frame/consumer transitions into an all-length upper bill with a bounded endpoint debt.

**Frontier target.** finite-state uniform caller cost.

<a id="a024"></a>

### A024 — Theorem: Exact two-level fusion with an integration allowance

**Statement.** Let parent and child complete profiles have normalizations (W₁,m₁),(W₂,m₂). Their Cartesian product list contains rank rs with multiplicity h_r k_s and has normalization (W₁W₂,m₁m₂), so its moment is Φ_H(a)Φ_K(a). If these are at most 1−η₁ and 1−η₂, additional normalized integration work below η₁+η₂−η₁η₂ leaves strict admission.

**Proof.** Expand the finite double sum: Σ_{r,s}h_rk_s(rs/(m₁m₂))^p/(W₁W₂) factors into the product of the two sums. Every product ratio is positive and below one. The product bound is (1−η₁)(1−η₂)=1−η₁−η₂+η₁η₂. Subtracting from one gives the precise available integration allowance. A physical tensor/caller construction must supply the product list and charge shared interfaces separately.

**Action.** Use a proved tensor or two-level consumer construction to buy a nonzero restoration/transport allowance from both complete primitive margins.

**Frontier target.** tensor/block recursive composition.

<a id="a025"></a>

### A025 — Theorem: An acyclic contract library yields an explicit least-cost caller

**Statement.** Let vertices of a finite acyclic graph be fully specified boundary interfaces. Each edge carries a correct native word between its endpoints and a complete nonnegative cost. A cheapest source-to-target path, if one exists, is constructible by topological dynamic programming; concatenating its words preserves the endpoint interface and has the sum of its edge costs.

**Proof.** Initialize distance zero at the source and infinity elsewhere. In topological order, update each outgoing edge by d(v)≤d(u)+cost(u,v), recording a predecessor when improved. Inductively every path into u has already been considered, so the maintained distance is the least path cost. Following predecessors from a reachable target reconstructs a finite path. Each word ends in exactly the next word’s declared interface, giving correctness by substitution; all edge costs add because every used primitive belongs to one edge. Exact cost comparisons must be certified, not rounded in the wrong direction.

**Action.** Assemble a cheaper complete caller from independently proved alternative consumer/frame contracts, with a reconstructible witness rather than a lower-cost relaxation alone.

**Frontier target.** constructive caller selection from verified local contracts.

<a id="a026"></a>

### A026 — Theorem: A recursive integration toll is bounded by a geometric bill

**Statement.** Consider a finite expansion tree with root weight 1 and nonnegative child weights summing to at most ρ times the parent weight, 0≤ρ<1. If each expanded node pays extra integration cost at most ε times its weight, the total extra normalized bill is at most ε/(1−ρ), regardless of tree depth.

**Proof.** Induction on levels bounds the sum of weights at depth d by ρ^d: sum the child-weight inequalities over that level. The total integration cost is at most ε times the sum of all node weights, hence at most εΣ_{d≥0}ρ^d=ε/(1−ρ). The infinite geometric series bounds every finite stopped tree and therefore does not assume that an infinite physical execution is run. The tree must include all real branches; an omitted sibling cannot be assigned zero weight.

**Action.** Bound repeated consumer/precision integration work at every recursive node, so a local toll is not mistaken for a one-time setup charge.

**Frontier target.** all-level overhead admission.

<a id="a027"></a>

### A027 — Theorem: Rounding a fractional contract mix gives a finite sufficient design

**Statement.** Let k valid equal-normalization module types have complete bills f_j∈[0,M]. For any probability vector λ and integer B≥1, one can choose nonnegative integers n_j with Σn_j=B such that |Σ(n_j/B−λ_j)f_j|≤kM/B. Thus a fractional margin η is preserved whenever B>2kM/η.

**Proof.** Take n_j=⌊Bλ_j⌋ initially. The integer deficit is less than k; add one to that many coordinates. Each final |n_j/B−λ_j| is at most 1/B. The triangle inequality bounds the bill error by Σ M/B=kM/B. If Σλ_jf_j≤1−η and the error is below η/2, the chosen finite list has average below 1−η/2. The bound concerns actual counts of the listed valid types; it neither rounds an arbitrary packing relaxation into a causal packing nor removes cross-module costs.

**Action.** Realize a promising mix of genuinely different native contracts by finitely many whole modules, with a quantified rounding loss.

**Frontier target.** finite realization of a changed-provider mix.

<a id="a028"></a>

### A028 — Theorem: Conditional expectation derandomizes a complete finite bill

**Statement.** Let a finite product of allowed design choices have a rational complete bill F under a rational probability distribution, and suppose its exactly computed expectation is below B. A deterministic sequence of allowed choices can be selected with final bill below B by retaining at each step a choice whose conditional expectation is no larger than the previous one.

**Proof.** The current conditional expectation is a convex combination of the finitely many next-choice conditional expectations. At least one is no larger than that combination. Select such an option and repeat. After the last choice the conditional expectation equals the actual bill, so it is still below the initial B. Computing conditional expectations may be expensive; the theorem promises a finite construction, not a uniform polynomial-time synthesis algorithm. Every allowed choice must preserve the specified interface, and F must include integration and endpoint costs.

**Action.** Turn a rigorously priced randomized contract-mixture argument into a concrete candidate word or caller that can be independently checked.

**Frontier target.** constructive selection of a complete finite redesign.

<a id="a029"></a>

### A029 — Theorem: A pessimistic estimator produces simultaneous resource feasibility

**Statement.** For finitely many rational complete resource quantities X_i of a finite design with rational probabilities, rational targets b_i and rational t_i>0, suppose E[Σ_i exp(t_i(X_i−b_i))]<1. Then conditional-expectation selection constructs a design with X_i<b_i for every i.

**Proof.** The initial estimator expectation is strictly below one. At any partially fixed design with conditional expectation below one, at least one positive-probability next choice also has conditional expectation below one, because the current expectation is their convex combination. Each such expectation is a finite rationally weighted sum of exponentials of rational numbers; rational Taylor bounds with remainder provide certified intervals to arbitrary precision. Refine these intervals in parallel until an option has upper bound below one, and select it. Strict existence guarantees termination without a real-comparison oracle. Repeat to a fully chosen design with estimator F<1. If some X_i≥b_i its exponential term is at least one, a contradiction. This proves simultaneous strict feasibility; it does not assert polynomial synthesis time.

**Action.** Choose one actual redesign that simultaneously fits paid moment, bank stock and precision reserves, when a rigorous finite estimator is available.

**Frontier target.** joint resource-feasible native/caller synthesis.

<a id="a030"></a>

### A030 — Theorem: Optimal continuous precision allocation with a bounded integer loss

**Statement.** Let a_i,w_i>0, A=Σa_i and ε>0 satisfy a_i ε≤A w_i for all i. For real precisions b_i≥0 constrained by Σw_i2^(−b_i)≤ε, the minimum Σa_i b_i occurs at b_i*=log₂(Aw_i/(a_iε)). Rounding every b_i* upward preserves the error bound and adds less than A to the weighted precision cost.

**Proof.** The stated b_i* are nonnegative and give individual errors a_iε/A, whose sum is ε. For any feasible b, put t_i=w_i2^(−b_i)/(a_iε/A)>0 and α_i=a_i/A. Feasibility says Σα_it_i≤1. Since log t≤t−1, Σα_i log t_i≤0. But log t_i=−(b_i−b_i*)log 2, so Σa_i b_i≥Σa_i b_i*. Rounding up only decreases errors, and each added bit is less than one; multiply by a_i and sum.

**Action.** Allocate precision to expensive versus error-sensitive native stages with an exact optimality proof and a fully priced integer rounding overhead.

**Frontier target.** uniform precision allocation rather than uniform overprecision.

<a id="a031"></a>

### A031 — Theorem: A sufficient coverage deficit for any declared minimum rank

**Statement.** Let a complete profile have every active rank in [u,m), u>0, and rank mass M=Σh_r r=Wm−D≥0. If D>Wm−Wm^p u^(1−p), then Φ_H(a)<1; with a margin target η∈(0,1), D≥Wm−(1−η)Wm^p u^(1−p) yields Φ_H(a)≤1−η.

**Proof.** Since p−1<0 and r≥u, r^p=r r^(p−1)≤r u^(p−1). Sum to bound the raw numerator by (Wm−D)u^(p−1). Substitute either displayed deficit threshold and divide by Wm^p. This is a sufficient worst-case profile bound, not a claim that the required deficit is attainable. The profile must already include every added decoder and adapter; omitting rank-one cleanup can falsify the asserted minimum rank.

**Action.** Specify a quantitative unpaid-coordinate target for a changed coverage law whose full child ranks are controlled, before synthesizing a new source template.

**Frontier target.** changed coverage-law sufficient target.

<a id="a032"></a>

### A032 — Theorem: Adding live families has a fully priced normalization rule

**Statement.** Let an admitted source have W live families and bill at most 1−η. Suppose an actual extension adds s whole live families, each with raw complete profile cost at most (1−ζ)m^p, and pays a further boundary cost C_p. Its bill is at most 1−[Wη+sζ−C_p/m^p]/(W+s). Thus C_p<m^p(Wη+sζ) suffices.

**Proof.** The old raw numerator is at most Wm^p(1−η). The added families contribute at most sm^p(1−ζ), and the boundary contributes C_p. Divide their sum by the actual new normalization (W+s)m^p and rearrange. A family counts in s only if the source’s declared live-input and coverage conditions actually hold for it; calling a spare physical row live does not supply such a certificate. Negative ζ is permitted algebraically and correctly reduces the reserve.

**Action.** Price live-stock enlargement, including its new recursive work, instead of obtaining an artificial gain by changing the denominator alone.

**Frontier target.** physical/live-stock normalization of a changed source.

<a id="a033"></a>

### A033 — Theorem: A block-weight certificate gives a replica-independent precision envelope

**Statement.** For block operators x′_i=Σ_j M_ij x_j let ||M_ij||≤S_ij≥0. If v_i>0, ||x_i||≤C v_i and Σ_jS_ijv_j≤λv_i, then ||x′_i||≤λC v_i. For a sequence satisfying the same v-certificate with factors λ_t, every coordinate at every prefix is bounded by C max_i v_i times the largest prefix product Πλ_t, including the empty product 1, independently of the number of blocks.

**Proof.** The triangle inequality gives ||x′_i||≤Σ_jS_ij C v_j≤λC v_i. Iterate this componentwise implication through the finite sequence. A coordinate’s magnitude is bounded by its block Euclidean norm, so the same bound controls every stored coordinate without summing norms over unrelated blocks. All endpoint/frame maps must be included among the M_t; a nonunitary gauge cannot be discarded. Correlations among initial blocks do not enter any inequality.

**Action.** Construct a weighted all-prefix magnitude invoice for interleaved tensor replicas without paying a spurious factor from the total number of unrelated blocks.

**Frontier target.** uniform hosted precision and correlated-block inputs.

<a id="a034"></a>

### A034 — Theorem: Per-block grids meet a common propagated error budget

**Statement.** Let a rounded block have d_i real coordinates, each rounded to nearest mesh 2^(−b_i), and let its subsequent linear map have norm at most L_i>0. For any ε_i>0, b_i≥max(0,ceil(log₂(L_i sqrt(d_i)/(2ε_i)))) guarantees a propagated error at most ε_i. The stored grid-fraction bits are exactly Σ_i d_i b_i before sign/exponent fields. A zero suffix map needs no propagated-accuracy bits.

**Proof.** Nearest rounding incurs at most 2^(−b_i)/2 in each coordinate. Its Euclidean norm is at most sqrt(d_i)2^(−b_i)/2; multiplying by the later norm L_i proves the bound. If the logarithm is negative, b_i=0 still meets it. The grid count follows by assigning b_i fraction bits to each of the d_i coordinates. Coordinate-magnitude/sign storage is separate and must be supplied by a prefix bound such as A033.

**Action.** Assign different precisions to blocks according to actual size and downstream amplification, then enter the exact summed storage/rounding charge.

**Frontier target.** nonuniform physical precision invoice.

<a id="a035"></a>

### A035 — Theorem: A complete word has explicit suffix-weighted rounding budgets

**Statement.** Assume L≥1. For an exact word x_t=M_t x_{t−1}, suppose the implementation obeys x̃_t=M_t x̃_{t−1}+e_t with x̃₀=x₀. Set P_t=Π_{s=t+1}^L||M_s||, taking an empty product as 1. If ||e_t||≤ε/(L P_t) whenever P_t>0, with arbitrary errors allowed when P_t=0, then ||x̃_L−x_L||≤ε.

**Proof.** Expand the error recurrence by substitution: the final difference is Σ_t M_L⋯M_{t+1}e_t. The norm of term t is at most P_t||e_t||. If P_t=0, at least one later factor is the zero operator, so that term is exactly zero. Every other term contributes at most ε/L. Sum the at most L contributions. This argument prices every rounding event, even inside a word whose exact endpoint is the identity.

**Action.** Derive stage-by-stage grid targets from the actual full native/cleanup word, instead of pricing only its final operator norm.

**Frontier target.** all-prefix native rounding contract.

<a id="a036"></a>

### A036 — Theorem: Exact inverse cancellation still has a nonzero precision price

**Statement.** If an invertible linear map M is applied and then inverted, with forward error η and inverse-stage error ξ, the final error is M^(−1)η+ξ. Thus ||η||≤ε/(2||M^(−1)||) and ||ξ||≤ε/2 suffice for final error at most ε, regardless of M’s exact cancellation.

**Proof.** The implemented states are ỹ=Mx+η and z̃=M^(−1)ỹ+ξ. Substitute to obtain z̃=x+M^(−1)η+ξ. Apply submultiplicativity and the triangle inequality to get the displayed sufficient budget. The inverse norm is positive for a nonzero-dimensional invertible map; the zero-dimensional case has no coordinates or error. The identity endpoint alone does not remove either error term.

**Action.** Price paired encoder/decoder or compute/uncompute stages correctly when exact restoration is used to justify a consumer interface.

**Frontier target.** precision of restored native scratch.

<a id="a037"></a>

### A037 — Theorem: Arbitrary dirty scratch gives an explicit intermediate magnitude bill

**Statement.** Let S(x,y)=(x+Ay,y), with ||A||≤M, ||x||≤X and ||y||≤D. Both the forward word and its exact inverse use only intermediate block bounds X+MD and D. Hence a signed integer magnitude field of more than log₂(1+max(X+MD,D)) bits provides sufficient range for the magnitude part of a fixed-point representation of these intermediates. Fraction bits, a separate sign bit and rounding error are charged separately. Here a shear update is one abstract block operation. A scalar evaluator for Ay requires its own intermediate-magnitude certificate, whose possibly larger envelope is charged in addition.

**Proof.** The triangle inequality gives ||x+Ay||≤X+MD. The y block is unchanged. Applying S^(−1) subtracts Ay and restores x; its computed target is either x+Ay or x, so no larger bound is needed for the exact two-step path. Every coordinate is bounded by its block norm. A magnitude field whose range exceeds 1 plus that bound cannot overflow on these exact coordinates; finite-grid representability is a separate requirement and rounding effects must be added using A035 or A036. D is arbitrary and is not silently set to zero.

**Action.** Use this envelope for the declared block endpoints of a dirty helper. Combine it with the actual matrix-vector evaluator’s prefix bound before choosing the native word’s magnitude field; the operator norm alone does not bound an arbitrary evaluator’s internal accumulators.

**Frontier target.** arbitrary-dirt magnitude/precision contract.

<a id="a038"></a>

### A038 — Theorem: Coefficient perturbations of a whole native word have a product bound

**Statement.** For ||M_t||≤b_t and ||E_t||≤d_t, b_t,d_t≥0, one has ||Π_t(M_t+E_t)−Π_t M_t||≤Π_t(b_t+d_t)−Π_t b_t, in the same fixed order. If b_t>0 and Σ_t d_t/b_t≤γ, the right side is at most (e^γ−1)Π_t b_t.

**Proof.** Expand the finite ordered product by choosing either M_t or E_t at every position. Remove the term with no E. Each remaining product has norm at most the product of its chosen b and d bounds; adding all such scalar products gives exactly Π(b+d)−Πb. No commutation of matrices is used. For the second bound factor out Πb and use Π(1+d_t/b_t)≤exp(Σd_t/b_t), which follows from log(1+x)≤x.

**Action.** Translate bounded coefficient quantization errors into a complete word-level error allowance before choosing the coefficient precision.

**Frontier target.** uniform coefficient approximation without free operator cancellation.

<a id="a039"></a>

### A039 — Theorem: Acyclic error propagation is computed by reverse path weights

**Statement.** For a finite acyclic linear computation, let an edge u→v have operator norm at most a_vu≥0. Put W_out=1 and compute W_u=Σ_{u→v}a_vu W_v backward from one output, with zero contribution from vertices not reaching it. If a local error e_u is inserted after node u, output error is at most Σ_u W_u||e_u||.

**Proof.** Substitute each node’s linear expression in topological order. An error at u reaches the output through every directed path from u; the coefficient operator is the sum of ordered edge products along those paths. Triangle inequality bounds its norm by the sum of the products of the a’s. Backward distributivity is precisely the recurrence defining W_u, so W_u equals that finite path sum. Summing contributions from all errors proves the bound, without independence or cancellation assumptions.

**Action.** Compute exact error sensitivities for a shared DAG consumer, where one bank or tensor block feeds several later uses; assign local grids against these weights.

**Frontier target.** shared-consumer precision DAG.

<a id="a040"></a>

### A040 — Theorem: A coupled feedback certificate closes simultaneous error bounds

**Statement.** Let e,b be finite nonnegative vectors on a nonempty index set with e≤Fe+b for F≥0. If w_i>0 and Fw≤ρw with 0≤ρ<1, then e_i≤w_i max_j(b_j/w_j)/(1−ρ). In particular b_i≤(1−ρ)τw_i implies e_i≤τw_i for every i.

**Proof.** Set E=max_i e_i/w_i and B=max_i b_i/w_i. The component inequalities imply e_i/w_i≤Σ_jF_ijw_j E/w_i+b_i/w_i≤ρE+B. Taking the maximum gives E≤ρE+B. Since 1−ρ>0, E≤B/(1−ρ), proving the coordinate bounds. This is a direct finite feedback closure; it does not assume an unproved convergence of a numerical solver or independent errors in different banks.

**Action.** Close a multi-bank all-cut error ledger with an explicit positive-weight certificate, retaining cross-bank feedback in the required input grid.

**Frontier target.** uniform all-cut coupled precision sufficiency.

<a id="a041"></a>

### A041 — Theorem: A complete supplier moment closes a normalized floor recurrence

**Statement.** Let s>0, m≥2, ranks 0≤r_i<m and a_i≥0 have ρ=Σa_i(r_i/m)^s<1. Suppose T:ℕ→[0,∞), T(0)=0, T(n)≤B n^s for 1≤n<N, and for n≥N≥m, T(n)≤Σa_i T(r_i⌊n/m⌋)+c n^s. Then T(n)≤K n^s for K=max(B,c/(1−ρ)).

**Proof.** Use strong induction on n. Each child is at most (r_i/m)n<n, so its inductive cost is at most K(r_i/m)^s n^s; zero children cost zero. Adding gives T(n)≤(Kρ+c)n^s≤K n^s. The finite base is covered by B. For normalized precision-work in a supplier, a_i is its actual per-live-unit occurrence weight; this theorem does not identify that normalized work with serial integer multiplication time.

**Action.** Attach a uniform normalized-work recurrence to a changed complete profile and close it with a concrete coefficient K, including its local toll c.

**Frontier target.** uniform recursive primitive implementation.

<a id="a042"></a>

### A042 — Theorem: Ceilings and bounded address tails preserve a strict recurrence

**Statement.** Let child sizes k_i(n) be integers with 0≤k_i(n)≤q_i n+b_i, 0≤q_i<1, b_i≥0. Choose explicit q′_i∈(q_i,1) with ρ′=Σa_i(q′_i)^s<1, s>0, and N≥max_i b_i/(q′_i−q_i). With T(0)=0, a finite base below N and recurrence T(n)≤Σa_iT(k_i(n))+c n^s for n≥N, one has T(n)≤max(B,c/(1−ρ′))n^s.

**Proof.** For n≥N, b_i≤(q′_i−q_i)n, hence k_i(n)≤q′_i n<n. Strong induction now gives the same estimate as A041 with q′_i instead of r_i/m. The required q′ can be found near q because the finite sum is continuous and its value at q is strictly below one, whenever that latter strict certificate is given. The theorem asks for explicit chosen q′ so neither a hidden limit nor a monotonicity assumption on T is used.

**Action.** Carry a strict profile margin through literal ceiling, alignment and bounded-tail costs in a uniform implementation.

**Frontier target.** rounding/address-aware recursive transfer.

<a id="a043"></a>

### A043 — Theorem: Partitioning inputs has an explicit concave work penalty

**Statement.** Let 0<s<1, k≥1 and nonnegative subproblem sizes x_1,…,x_k satisfy Σx_i≤n. If each complete subproblem costs at most C x_i^s, their sum costs at most C k^(1−s)n^s. Consequently a caller whose previous recursive coefficient is ρ remains contractive after such a partition whenever ρ k^(1−s)<1, with all partition adapters charged separately.

**Proof.** Concavity of t^s gives (1/k)Σx_i^s≤((Σx_i)/k)^s. Multiply by kC and then use Σx_i≤n. Zero parts are permitted by continuity. If the caller multiplies this subproblem bound by its existing nonnegative coefficient ρ, the new recursive coefficient is at most ρk^(1−s). A strict value below one permits the recurrence closure, while the adapter bill enters its toll. Partitioning is not free merely because sizes add.

**Action.** Choose the number of decoder panels or tensor partitions without losing a primitive margin to an uncounted fragmentation factor.

**Frontier target.** partitioned decoder/recursive caller.

<a id="a044"></a>

### A044 — Theorem: A finite remainder algorithm has a uniform priced toll

**Statement.** Fix m≥2 and suppose a recurrence has proper-rank children r_i⌊n/m⌋ plus one remainder computation T(n mod m). If all remainder costs are at most R, and the other nonrecursive toll is c n^s, s>0, then replacing c by c+R closes the recurrence by A041 whenever its complete proper-rank coefficient ρ<1.

**Proof.** For every n≥1, n^s≥1, so T(n mod m)≤R≤R n^s. Thus the full right side is at most the proper-rank child sum plus (c+R)n^s. The finite list of m remainder inputs provides an explicit maximum R, rather than an asymptotic notation with an unknown dependence on n. Apply the strong-induction proof of A041 using this enlarged toll and the actual finite base.

**Action.** Keep short-tail multiplication, decoding or source alignment in a finite auditable table and include its maximum cost in the all-size recurrence.

**Frontier target.** literal short tails in uniform implementations.

<a id="a045"></a>

### A045 — Theorem: Adaptive valid providers preserve a uniform margin

**Statement.** Let each size n choose any one of a family of valid complete recursive profiles. Suppose every chosen profile has child ratios below one, normalized s-moment at most 1−η for a fixed η>0, and nonrecursive toll at most c n^s. With a common finite base coefficient B and T(0)=0, T(n)≤max(B,c/η)n^s even when choices depend on prior data.

**Proof.** Strong induction at n uses only the actual chosen profile at that node. Its child inductive contributions sum to at most K(1−η)n^s, and the toll contributes at most c n^s. Taking K≥c/η closes the inequality. No probability distribution or fixed provider frequency appears. Child sizes must be strictly smaller and all source-dependent choices must themselves meet the same cost/interface certificate; otherwise the uniform hypothesis has not been established.

**Action.** Use a data- or size-dependent menu of genuinely valid native contracts without requiring a single fixed provider, while preserving one common recursive budget.

**Frontier target.** uniform heterogeneous-provider selection.

<a id="a046"></a>

### A046 — Theorem: An individually expensive level can be paid by a two-level contract

**Statement.** Suppose alternating correct recursion levels have moments ρ_A,ρ_B≥0 at s>0, with ρ_Aρ_B<1, and respective complete tolls c_A n^s,c_B n^s. If all children shrink and compositions preserve interfaces, two-level expansion costs at most K n^s for K≥(c_A+ρ_Ac_B)/(1−ρ_Aρ_B), together with a sufficient finite two-level base coefficient.

**Proof.** Expand the A recurrence and then the B recurrence at each A child. Child ratios multiply, so the two-level recursive coefficient is ρ_Aρ_B. The B tolls appear at A child sizes; their s-powers sum with weights to ρ_A n^s, giving total toll (c_A+ρ_Ac_B)n^s. Strong induction on the strictly smaller two-level descendants now closes the bound with the displayed K. This may hold even when ρ_A≥1. Every seam adapter between A and B belongs in one of the complete tolls.

**Action.** Admit a coupled production/consumer pair whose profitable unit is two levels, rather than rejecting its producer from a one-level bill or ignoring its consumer.

**Frontier target.** changed two-pass recursive boundary.

<a id="a047"></a>

### A047 — Theorem: Window contraction bounds a nonperiodic recursion tree

**Statement.** At depth d let total weighted s-mass multiply by at most ρ_d≤R, R≥1. Suppose every consecutive L-depth product is at most θ<1. If all node tolls and leaf costs are bounded by c and B times their weighted s-mass respectively, any finite stopped tree rooted at size n costs at most (B+c)L R^(L−1)n^s/(1−θ).

**Proof.** At depth d, partition its prefix product into complete L-blocks and a remainder of fewer than L factors. The product is at most θ^⌊d/L⌋ R^(L−1). The sum of weighted s-masses over all depths is therefore at most n^s L R^(L−1)Σ_{j≥0}θ^j. Every real toll and every stopped leaf cost is bounded by (B+c) times the corresponding node mass; summing this deliberately conservative bound gives the result. Early stopping only deletes nonnegative contributions.

**Action.** Prove an all-size bill for a nonperiodic sequence of native/consumer modes using bounded-window certificates, without requiring each level to be profitable alone.

**Frontier target.** nonperiodic coupled recursive schedules.

<a id="a048"></a>

### A048 — Theorem: Finitely many costly repair levels have a bounded exponent-neutral price

**Statement.** Let normal levels multiply weighted s-mass by at most ρ<1, and suppose at most J exceptional depths multiply it by at most R≥1. With toll/leaf coefficient B+c, the complete stopped-tree cost is at most (B+c)R^J[J+1/(1−ρ)]n^s.

**Proof.** At depth d there are at most J exceptional factors and at least max(0,d−J) normal factors. Their product is at most R^Jρ^max(0,d−J). Sum over d≥0: the first J depths contribute at most J R^J and the remaining geometric tail contributes R^J/(1−ρ). Bound all actual toll and leaf costs by (B+c) times node mass as in A047. J must be uniform in input size; allowing it to grow would change this conclusion.

**Action.** Pay a uniform finite set of exceptional endpoint, field-change or repair levels explicitly while preserving the target recursion exponent.

**Frontier target.** uniform finite exception handling.

<a id="a049"></a>

### A049 — Theorem: A normalized logarithmic recurrence implies a bit-time bound

**Statement.** Let T(n)≥0 be an actual bit-time bound, set F(x)=e^(−x)T(ceil(e^x)) for x≥1, and fix 0<q_i<1. Suppose for x≥X≥1/min q_i one has F(x)≤Σa_iF(q_i x)+c x^s with ρ=Σa_i q_i^s<1, s>0; suppose F(x)≤B x^s on [1,X]. Then T(n)≤K n(log n)^s for integers log n≥1, with K=max(B,c/(1−ρ)).

**Proof.** Expand the recurrence until every branch argument lies in [1,X]. For a nonleaf x≥X, its children are at least min q_i X≥1 and at most q_max x, so this expansion has finite depth. Backward induction closes F(x)≤Kx^s exactly as in A041. At x=log n, ceil(e^x)=n and e^(−x)=1/n, proving the stated bit-time bound. This theorem requires the displayed uniform implementation recurrence; a finite profile or tensor identity by itself does not establish that premise.

**Action.** Prove the exact normalized log-scale implementation implication needed to turn a primitive saving into an actual n times log-power time bound, without claiming that the remaining compiler premise is already true.

**Frontier target.** sufficient uniform primitive-to-bit-time transfer.

<a id="a050"></a>

### A050 — Theorem: Fixed synthesis cost is a genuine constant, size-dependent advice is not

**Statement.** Let one fixed finite program be synthesized in P steps independently of input size, and suppose its verified execution costs at most C n(log n)^s for n≥2, s≥0. Including synthesis gives total cost at most [C+P/(2(log 2)^s)] n(log n)^s. The same conclusion holds for a fixed finite family by using its maximum P and C.

**Proof.** The function n(log n)^s increases for n≥2, so it is at least 2(log 2)^s. Therefore P≤[P/(2(log 2)^s)]n(log n)^s. Add the execution bound. A fixed finite family has finite maximum constants and may be selected by a separately charged rule. If synthesis or advice depends on unbounded input size, P is not fixed and this argument cannot be applied; that observation defines the theorem’s hypothesis rather than concealing an oracle.

**Action.** Use finite expensive design or certificate search offline only after fixing its resulting program and proving one uniform execution contract.

**Frontier target.** uniformity of offline-designed native/caller families.

<a id="a051"></a>

### A051 — Theorem: A positive type vector closes a heterogeneous caller recurrence

**Statement.** For finitely many types i, let T_i(0)=0 and let every recursive child have integer size at most q_ijk n<n. Put M_ij(s)=Σ_k a_ijk q_ijk^s, with a_ijk≥0 and s>0. If a positive vector v satisfies M(s)v≤(1−η)v, η>0, tolls are at most c_i n^s, and the finite bases at most B_i n^s, then T_i(n)≤K v_i n^s for K≥max_i(B_i/v_i,c_i/(ηv_i)).

**Proof.** Strong induction on size applies simultaneously to all types. At a node of type i, the children contribute at most K n^s Σ_jM_ijv_j≤K(1−η)v_i n^s. The toll is at most Kηv_i n^s by choice of K, closing the induction. Finite bases satisfy the same bound. This permits producer, consumer, field and bank states to carry different weights; their off-diagonal recursive transitions are not discarded.

**Action.** Build one exact positive-vector certificate for the actual stateful producer/consumer recursion, rather than pricing each type as an independent successful supplier.

**Frontier target.** multitype uniform caller/consumer transfer.

<a id="a052"></a>

### A052 — Theorem: A two-state primitive has an explicit rational type certificate

**Statement.** For a nonnegative two-state moment matrix M=[[a,b],[c,d]], assume a<1, d<1 and D=(1−a)(1−d)−bc>0. Set v=(1−d+b,1−a+c) and η=D/max(v_1,v_2). Then v>0 and Mv≤(1−η)v, so A051 applies with explicitly known weights and margin.

**Proof.** Direct multiplication gives (I−M)v=(D,D). Each coordinate of v is positive because 1−a and 1−d are positive. Since Mv≥0, D≤v_i and thus 0<η≤1. The identity Mv=v−D·1 implies D≥ηv_i for each i, which proves the displayed inequality. If a,b,c,d are rational, every quantity used here is rational except any separately bounded rank powers entering them.

**Action.** Certify a coupled two-pass producer/consumer budget by four actual moment entries, paying both cross-couplings instead of comparing diagonal bills alone.

**Frontier target.** two-state producer/consumer admission.

<a id="a053"></a>

### A053 — Theorem: A one-way consumer dependency has an explicitly scaled reserve

**Statement.** Let M=[[A,B],[0,D]] be nonnegative, Av≤ρ_Av and Dw≤ρ_Dw for positive v,w. For any ρ>max(ρ_A,ρ_D), choose t≥max_i (Bw)_i/((ρ−ρ_A)v_i), t>0. Then M(tv,w)≤ρ(tv,w).

**Proof.** The lower block is Dw≤ρ_Dw≤ρw. The upper block is tAv+Bw≤tρ_Av+Bw≤tρ_Av+t(ρ−ρ_A)v=tρv. This explicitly prices a feed-through consumer even when B is large: its cost is reflected in the required scaling t. When ρ<1, this gives an A051 contraction certificate; when no such ρ can be chosen from the supplied bounds, this theorem makes no successful admission claim.

**Action.** Integrate a valid downstream consumer by enlarging the producer’s potential coefficient exactly enough to cover its one-way work.

**Frontier target.** triangular typed caller composition.

<a id="a054"></a>

### A054 — Theorem: A cyclic sequence of state transitions has constructive weights

**Statement.** For k≥2 types suppose the only transition from type i goes to i+1 modulo k, with positive moment coefficient c_i. If Π_i c_i<1, choose (Πc_i)^(1/k)<ρ<1, set v_1=1 and v_{i+1}=ρv_i/c_i for i<k. Then Mv≤ρv.

**Proof.** For i<k, the definition gives c_iv_{i+1}=ρv_i exactly. At the last row, c_kv_1≤ρv_k is equivalent, after substituting the product definitions and multiplying by positive factors, to Π_i c_i≤ρ^k, which follows strictly from the choice of ρ. Every weight is positive. The state cycle therefore closes with one common potential even when some individual c_i exceed one.

**Action.** Price a complete cyclic production/consumption protocol by its closed cycle, including expensive intermediate states that are repaid later.

**Frontier target.** closed multistage recursive contracts.

<a id="a055"></a>

### A055 — Theorem: A finite-power row test constructs the type reserve

**Statement.** For M≥0, suppose M^L1≤θ1 for an integer L≥1 and 0≤θ<1. Put v=Σ_{j=0}^{L−1}M^j1 and η=(1−θ)/max_i v_i. Then v≥1 and Mv≤(1−η)v. The finite matrix-power data are a sufficient exact certificate for A051.

**Proof.** Telescope Mv−v=M^L1−1≤−(1−θ)1. Because v_i≤max v, one has ηv_i≤1−θ, giving Mv≤v−ηv. Nonnegative powers and the j=0 term give v_i≥1, so η is positive and at most one. All operations are finite additions and multiplications. No floating spectral-radius estimate or uncomputed infinite Neumann series is needed to produce the certificate.

**Action.** Convert a bounded-depth multitype cost computation into an explicit all-depth positive-vector proof.

**Frontier target.** finite certificates for uniform typed recursion.

<a id="a056"></a>

### A056 — Theorem: A type certificate has a quantified adapter allowance

**Statement.** If Mv≤(1−η)v, v>0, and all new interface adapters have nonnegative moment matrix E satisfying Ev≤εv with 0≤ε<η, then (M+E)v≤(1−η+ε)v. Thus the redesigned complete caller retains margin η−ε.

**Proof.** Add the two coordinate inequalities Mv≤(1−η)v and Ev≤εv. The sum is exactly the new matrix’s action on v. Positivity of η−ε makes the retained margin strict, and A051 gives the corresponding uniform coefficient with this smaller margin. E must include every changed cross-type transition, including an adapter that returns to a producer type rather than terminating locally.

**Action.** Spend a controlled part of a multitype native saving on the exact boundary adapters needed by a new consumer.

**Frontier target.** paid multitype interface integration.

<a id="a057"></a>

### A057 — Theorem: A common type potential licenses adaptive switching

**Statement.** Let a set of valid complete typed contracts have matrices M_j with M_jv≤ρv for one positive v and one ρ<1. Any size- or data-dependent switching among them satisfies the same bound A051, provided child sizes shrink and the tolls/bases have a common coefficient bound.

**Proof.** At every recursive node use the inequality for the actually selected M_j. Strong induction on child size gives a recursive contribution at most Kρv_i n^s for its current type i, independently of past or future choices. The uniform toll contributes at most K(1−ρ)v_i n^s. A single v is what permits composition across choices; separate unrelated potentials would require an additional priced change of metric.

**Action.** Allow a controller to select among profitable native/consumer modes safely, using one shared type certificate.

**Frontier target.** adaptive stateful callers with a shared budget.

<a id="a058"></a>

### A058 — Theorem: Eliminating auxiliary state pays its full return coupling

**Statement.** For nonnegative vectors T,S and matrices A,B,C,D, suppose T≤AT+BS+c and S≤CT+DS+d. If D has a positive weight contraction certificate, N=Σ_{k≥0}D^k exists entrywise and S≤NCT+Nd. Consequently T≤(A+BNC)T+c+BNd.

**Proof.** Iterate the second inequality K times: S≤Σ_{k=0}^{K−1}D^k(CT+d)+D^KS. A positive contraction weight bounds D^KS coordinatewise by a constant times ρ^K for some ρ<1, so this remainder tends to zero. The same bound proves convergence of the nonnegative series. Substitute the resulting upper bound for S into the first inequality. The term BNC is the complete cost of arbitrary auxiliary excursions and return; dropping it would not follow from these hypotheses.

**Action.** Eliminate a bank, decoder or consumer state from a cost system without silently losing the work that returns to the main state.

**Frontier target.** closed auxiliary-state/consumer accounting.

<a id="a059"></a>

### A059 — Theorem: Tensor composition preserves typed reserves with a priced interaction

**Statement.** If Mv≤ρv and Nw≤σw for nonnegative matrices and positive vectors, then (M⊗N)(v⊗w)≤ρσ(v⊗w). If the actual product caller adds E≥0 with E(v⊗w)≤ε(v⊗w) and ρσ+ε<1, it has a complete positive-vector contraction certificate.

**Proof.** At coordinate (i,j), the Kronecker action factors as (Mv)_i(Nw)_j, at most ρσv_iw_j. Add the explicit interaction bound for E. The product type weight is positive, so A051 applies to the actual combined recursion once its child-size and finite-base conditions are supplied. This certificate prices cross-factor interfaces through E rather than assuming the physical tensor construction has no extra routing or precision work.

**Action.** Combine two proved typed tensor contracts while reserving an exact budget for their common-label or physical interaction.

**Frontier target.** stateful tensor-contract composition.

<a id="a060"></a>

### A060 — Theorem: A strict real type certificate can be made rational

**Statement.** Let M≥0 be rational and v>0 satisfy μ_i=v_i−(Mv)_i>0. Write S_i=Σ_jM_ij. Choose an integer Q>max(2/min_i v_i, max_i 2(1+S_i)/μ_i), and put u_i=⌊Qv_i⌋/Q. Then u>0 and u_i−(Mu)_i≥μ_i/2>0, yielding a finite rational certificate.

**Proof.** Each |u_i−v_i|<1/Q. Thus |(u−Mu)_i−(v−Mv)_i|≤(1+S_i)/Q<μ_i/2. Also u_i≥v_i−1/Q>v_i/2>0 by the first Q bound. Every entry of u and Mu is rational and can be checked exactly. This construction validates a nearby certificate; it does not validate the approximate v merely because a numerical eigensolver produced it.

**Action.** Replace floating positive-vector output by exact rational weights and explicit slack before using it in a uniform caller proof.

**Frontier target.** exact finite certificates for multitype recursion.

<a id="a061"></a>

### A061 — Theorem: A tight sufficient active-grid coefficient is explicit

**Statement.** Let m>r≥0 be integers and stop≥m. Suppose A(n)≥0 obeys A(n)≤B n below stop, and above stop A(n)≤A(r⌊n/m⌋)+s⌊n/m⌋+E with s,E≥0. Every C≥max(B,(s+E)/(m−r)) gives A(n)≤C n for all n.

**Proof.** Use strong induction on n. For n≥stop set q=⌊n/m⌋≥1; the proper-rank child rq<n. The inductive bound gives A(n)≤Crq+sq+E≤(Cr+s+E)q≤Cm q≤Cn. The second inequality uses q≥1, the third the choice of C, and the last m⌊n/m⌋≤n. Base cases use C≥B. This is an active-path grid certificate; work on sibling branches is not folded into A unless its definition actually requires that.

**Action.** Compute the smallest coefficient supplied by this linear reserve argument for an exact-grid caller, rather than automatically doubling all local charges.

**Frontier target.** all-size active common-exponent reserve.

<a id="a062"></a>

### A062 — Theorem: Strict stopping gives an explicit precision-depth invoice

**Statement.** Suppose an active branch above threshold N>0 has child size at most q times its parent, 0<q<1. From n≥N it has fewer than or equal to k=floor(log(n/N)/log(1/q))+1 active descents. If each descent adds at most b grid bits and the leaf needs B bits, B+bk suffices along that branch.

**Proof.** After j descents the size is at most q^j n, by induction. The definition of k gives k>log(n/N)/log(1/q), so q^k n<N and the branch must already have stopped. Adding the per-descent bit charges gives at most bk, then add the leaf reserve B. This argument controls one active dependency path; a simultaneous caller uses the maximum over its paths, or a separately proved aggregation, rather than multiplying by the number of replicas.

**Action.** Convert the actual active shrink factor into a finite precision depth and retain a strict stop at exact powers of the shrink ratio.

**Frontier target.** uniform stopping and precision depth.

<a id="a063"></a>

### A063 — Theorem: The complete half-rank precision bill has an exact parity formula

**Statement.** For integer ranks r and multiplicities h_r≥0, let M=Σh_r r and O=Σ_{r odd}h_r. For an integer field width f≥1, P(f)=Σh_r ceil(rf/2) equals [fM+(f mod 2)O]/2. Thus even f removes the entire per-field parity term without changing the profile.

**Proof.** For every integer z≥0, 2ceil(z/2)=z+(z mod 2). Apply this with z=rf, multiply by h_r, and sum. If f is even, every rf is even. If f is odd, rf has the parity of r, so the sum of the parity remainders is precisely O. Divide the integer identity by two. Every paid child, including cleanup and movement children, must be included in h before using M or O.

**Action.** Compute an exact all-field-width precision invoice from the complete current or changed profile, retaining the odd-width tax explicitly.

**Frontier target.** uniform completed-child precision accounting.

<a id="a064"></a>

### A064 — Theorem: An even field width buys a prescribed fixed-overhead margin

**Statement.** With A063 and a fixed complete per-field setup charge C≥0, normalize by Wf, W>0. If M/(2W)≤1−η, η>0, then every positive even integer f≥4C/(Wη) satisfies [P(f)+C]/(Wf)≤1−3η/4. An explicit choice is f=2max(1,ceil(2C/(Wη))).

**Proof.** At even f, A063 gives P(f)=fM/2. The normalized bill is M/(2W)+C/(Wf). The width bound makes the second term at most η/4, yielding the stated margin. The explicit f is positive, even and meets the width threshold. Any cost that grows with f belongs in M or in a separately bounded f-dependent toll; it cannot be placed in the fixed C.

**Action.** Choose one finite, parity-correct field width that actually absorbs fixed source/precision setup, instead of taking an unpriced infinite-width limit.

**Frontier target.** finite uniform field-width selection.

<a id="a065"></a>

### A065 — Theorem: A dyadic computation DAG has a least grid assignment

**Statement.** In a finite acyclic linear computation, let each coefficient on edge u→v lie in 2^(−k_vu)ℤ with integer k_vu, and let input u lie on grid 2^(−E_u)ℤ. Assign each internal E_v=max(0,max_{u→v}(E_u+k_vu)), including the grid exponents of constant inputs. Then every exact value at v lies on grid 2^(−E_v)ℤ; this is the least nonnegative assignment satisfying these edge inequalities.

**Proof.** Induct in topological order. Multiplying an incoming grid value by its dyadic coefficient puts that summand on grid exponent E_u+k_vu; any finer nonnegative grid with exponent E_v represents it exactly. A sum of values on this common grid stays on it. For minimality, any assignment satisfying the edge inequalities is at least the prescribed input exponents, and induction makes its value at each later vertex at least the displayed maximum. Zero coefficients may be omitted from the graph.

**Action.** Construct an exact common-denominator schedule for a shared native/consumer DAG and charge only the maximum incoming exponent at each addition.

**Frontier target.** exact dyadic-grid compiler schedule.

<a id="a066"></a>

### A066 — Theorem: A finite bootstrap survives a fully priced per-round loss

**Statement.** Let 0<s<1 and x_{j+1}≥s x_j+b−ε with a uniform complete loss bound ε≥0. Put L=(b−ε)/(1−s). If x₀<L, then x_j≥L−s^j(L−x₀). Every target x* with x₀<x*<L is reached after any integer j>log((L−x₀)/(L−x*))/log(1/s).

**Proof.** The affine map y↦sy+b−ε fixes L. Subtract L from the recurrence and induct to obtain x_j−L≥s^j(x₀−L), which is the first conclusion. The strict iteration bound is equivalent to s^j(L−x₀)<L−x*, proving x_j>x*. The recurrence is a hypothesis about already established, fully charged finite bootstrap steps; the theorem does not supply an unproved compiler step or justify letting its loss vanish.

**Action.** Specify a finite number of valid bootstrap rounds and a maximum allowable round loss before expanding an asymptotic transfer campaign.

**Frontier target.** finite charged exponent-bootstrap interface.

<a id="a067"></a>

### A067 — Theorem: Ordering fixed bootstrap losses has an optimal constructive rule

**Statement.** For x_{j+1}=s x_j+b−ε_j, 0<s<1 and a fixed multiset of K nonnegative losses, placing larger losses earlier maximizes x_K among all orders. The conclusion assumes the corresponding complete rounds may actually be reordered without changing their interfaces or costs.

**Proof.** Expansion gives x_K=s^Kx₀+bΣ_{j=0}^{K−1}s^j−Σ_{j=0}^{K−1}s^(K−1−j)ε_j. The loss weights increase with j. If two consecutive losses are in increasing order u<v, swapping them reduces the weighted loss by s^(K−2−j)(1−s)(v−u)>0. Repeatedly remove such inversions to put the losses in decreasing order. The resulting finite sequence attains the least loss sum and hence the largest x_K.

**Action.** When correct bootstrap rounds are interchangeable, spend costly preparation/precision rounds early, where their effect on the final certified saving is discounted most.

**Frontier target.** cost-aware finite bootstrap scheduling.

<a id="a068"></a>

### A068 — Theorem: Geometrically improving round accuracy has an exact residual bound

**Statement.** Under x_{j+1}≥s x_j+b−ε_j, 0<s<1, suppose 0≤ε_j≤c t^j with 0<t<1. Relative to the zero-loss K-round value, the final deficit is at most c(s^K−t^K)/(s−t) if s≠t, and cK s^(K−1) if s=t; in both cases this bound tends to zero.

**Proof.** Expand the recurrence as in A067. The loss contribution is at most cΣ_{j=0}^{K−1}s^(K−1−j)t^j. Multiplying this finite sum by s−t telescopes to s^K−t^K, proving the first expression; equality s=t gives K identical summands. For unequal s,t both numerator powers tend to zero; at equality, K s^(K−1) tends to zero, for example by comparison with a geometric sequence of ratio sqrt(s) for all sufficiently large K.

**Action.** Choose a concrete round-precision growth schedule and carry its entire residual loss into a finite bootstrap certificate.

**Frontier target.** uniform finite precision in repeated transfer.

<a id="a069"></a>

### A069 — Theorem: A periodic producer/consumer bootstrap has a priced fixed point

**Statement.** For a cycle of k fully established maps x↦s_jx+b_j−ε_j, with 0<s_j<1, put S=Πs_j and B=Σ_{j=1}^k(b_j−ε_j)Π_{i=j+1}^k s_i. One cycle is exactly x↦Sx+B. Repeating it reaches every target strictly between the initial x₀ and B/(1−S), when x₀ lies below that fixed point, in finitely many cycles. Every asserted affine map must be valid on all intermediate exponents actually traversed; this theorem does not extend its domain of validity.

**Proof.** Compose the affine maps by substitution. The multiplier of x is the product S, and the j-th additive term is multiplied by every later s_i, yielding B. Since 0<S<1, subtracting the fixed point L=B/(1−S) gives x_n−L=S^n(x₀−L). The same explicit logarithmic iteration bound as A066 now proves finite attainment of every smaller target. All k losses remain in B; a consumer round cannot be removed from the cycle bill.

**Action.** Analyze an alternating production/consumption/field-transfer cycle as a complete finite unit instead of combining its separately advertised gains.

**Frontier target.** coupled periodic transfer contracts.

<a id="a070"></a>

### A070 — Theorem: A monotone outer conversion has a spendable gain allowance

**Statement.** For f(a)=a/(1+a), suppose 0≤a_old<a_new≤A and a_new−a_old≥δ>0. Then f(a_new)−f(a_old)≥δ/(1+A)^2. If a separately established outer theorem subtracts complete losses ℓ_old,ℓ_new with ℓ_new−ℓ_old<δ/(1+A)^2, the resulting converted parameter strictly increases.

**Proof.** Differentiate f: f′(a)=1/(1+a)^2≥1/(1+A)^2 on the interval. Integrate from a_old to a_new to get the first inequality. Subtract the extra outer loss to obtain strict positivity of the final difference. This is an arithmetic consequence conditional on the actual outer theorem and its hypotheses; it does not assert that this simple limiting conversion replaces the retained finite outer ledger.

**Action.** Budget the increased compiler/precision/analytic loss that a better primitive may tolerate, using a symbolic strict allowance and no new numerical κ.

**Frontier target.** fully priced outer conversion of a primitive improvement.

<a id="a071"></a>

### A071 — Theorem: A nonlinear rounding invariant closes a quadratic error recurrence

**Statement.** Let e_{t+1}≤α+βe_t+γe_t² with e_t≥0, α,γ≥0, 0≤β<1 and 4αγ≤(1−β)². For γ>0 put R=2α/[1−β+sqrt((1−β)²−4αγ)]; for γ=0 put R=α/(1−β). If e₀≤R, every e_t≤R.

**Proof.** The displayed R is the smaller nonnegative root of R=α+βR+γR²; its rationalized formula includes α=0 without cancellation ambiguity. The polynomial α+βx+γx² is nondecreasing for x≥0. Therefore e_t≤R implies e_{t+1}≤α+βR+γR²=R. Induction proves the invariant. A one-time inequality e≤α+βe+γe² would not by itself imply the small-root bound, so the initial invariant and iterative hypothesis are retained.

**Action.** Prove an all-prefix precision invariant for a nonlinear or bilinear consumer with quadratic error feedback, without selecting the small root of a circular inequality unjustifiably.

**Frontier target.** nonlinear consumer error closure.

<a id="a072"></a>

### A072 — Theorem: A weighted quadratic box controls interacting bank errors

**Statement.** For nonnegative bank errors suppose e′_i≤b_i+Σ_jF_ij e_j+Σ_{j,k}G_ijk e_j e_k, F,G≥0. If w>0 satisfies b_i≤αw_i, (Fw)_i≤βw_i and ΣG_ijkw_jw_k≤γw_i, and R obeys α+βR+γR²≤R, then the box 0≤e_i≤Rw_i is invariant.

**Proof.** Substitute the coordinate bounds e_j≤Rw_j into every nonnegative term. The right side is at most [α+βR+γR²]w_i≤Rw_i. This proves one-step invariance; induction gives it at every executed prefix. A071 constructs a usable R from scalar discriminant data, while the present theorem converts actual cross-bank coefficient tensors into those data. Every coupling appears in G, including errors from a consumer that reuses a producer’s dirty response.

**Action.** Close a simultaneous weighted error ledger for interacting dirty banks using finite inequalities that can be checked exactly.

**Frontier target.** coupled nonlinear dirty-bank precision.

<a id="a073"></a>

### A073 — Theorem: Local precision estimates remain valid inside a proved domain

**Statement.** Let exact states x_t lie in a domain containing the open radius-R ball about every x_t, for a fixed R>0. On that domain let a nonlinear step F_t be L_t-Lipschitz, and let local implementation error be at most δ_t. If the recursively computed E₀=0, E_{t+1}=L_tE_t+δ_t all satisfy E_t<R, then every approximate state stays in the domain and its error is at most E_t.

**Proof.** Induct on t. The exact state is R inside the domain and the approximate error is below R, so the approximate input is also in the domain where the stated Lipschitz and local-error bounds apply. Triangle inequality gives ||x̃_{t+1}−x_{t+1}||≤L_t||x̃_t−x_t||+δ_t≤E_{t+1}. This closes both the error estimate and the validity of its local hypotheses, rather than applying a bounded-domain derivative estimate to an uncontrolled approximate path.

**Action.** Prove that a chosen native/consumer rounding grid actually keeps every prefix inside the magnitude region used to price its error.

**Frontier target.** noncircular all-prefix precision proof.

<a id="a074"></a>

### A074 — Theorem: A bilinear consumer has an explicit two-input error allowance

**Statement.** Let B be bilinear with ||B(x,y)||≤L||x||||y||, L>0, and inputs bounded by X,Y. If each input error is at most δ=min(1,ε/[L(X+Y+1)]), then the output error is at most ε, for any ε>0.

**Proof.** Bilinearity expands the error into B(u,y)+B(x,v)+B(u,v). Their norms sum to at most L(δY+Xδ+δ²)=Lδ(X+Y+δ). Since δ≤1 and δ≤ε/[L(X+Y+1)], the result is at most ε. This keeps the product-of-errors term, which cannot be dropped in an all-input sufficient bound. Additional local output rounding is a separate charge and must consume a separate part of the final allowance.

**Action.** Choose explicit input precisions for a source-consuming bilinear decoder or tensor product stage, including its error cross term.

**Frontier target.** precision at bilinear/native consumer boundaries.

<a id="a075"></a>

### A075 — Theorem: A bilinear computation DAG has constructive error propagation

**Statement.** For a finite acyclic circuit of additions and bilinear gates of known norms, let exact input magnitudes and input-error bounds be known. At an addition use magnitude X+Y and error E+F+δ; at a bilinear gate of norm L use magnitude LXY and error L(XF+YE+EF)+δ, where δ bounds local error. These topological recurrences bound every exact and approximate-output error.

**Proof.** At an addition, triangle inequality gives both the magnitude sum and the error sum, with δ added for local rounding. At a bilinear gate, the exact magnitude bound is its stated norm inequality, and expanding perturbations gives exactly the three terms used in A074; add δ. Induct in topological order. Shared subexpressions keep their own single certified error bounds and may feed several later nodes; no independence is assumed. The resulting finite upper computation includes all paths through the actual DAG.

**Action.** Generate a complete symbolic precision invoice for a shared nonlinear consumer, rather than extrapolating a linear-word estimate past a bilinear stage.

**Frontier target.** uniform precision of shared bilinear consumers.

<a id="a076"></a>

### A076 — Theorem: An iterative linear consumer has a paid exact-integer termination rule

**Statement.** Let A=I−E, ||E||≤ρ<1, and suppose x=A^(−1)b is an integer vector with ||b||≤B. Starting y₀=0, implement y_{j+1}=b+Ey_j+e_j with ||e_j||≤δ. If ρ^kB/(1−ρ)<1/4 and δ/(1−ρ)<1/4, rounding y_k coordinatewise to the nearest integer recovers x exactly. The execution uses k applications of E, k additions of b and final rounding.

**Proof.** The convergent Neumann series gives ||x||≤B/(1−ρ). Subtract the fixed point equation x=b+Ex to get ||y_k−x||≤ρ^k||x||+δΣ_{j=0}^{k−1}ρ^j<1/2. Every coordinate error is then below 1/2, proving exact integer recovery by nearest rounding. The formula counts every iteration; operator application, storage, coefficient precision and any physical frame adapters must be priced by the caller, rather than replacing this algorithm by an oracle inverse.

**Action.** Construct an actual finite approximate-to-exact consumer from a certified contraction, with an explicit iteration and grid budget.

**Frontier target.** constructive well-conditioned integer recovery.

<a id="a077"></a>

### A077 — Theorem: Balanced quantization controls every accumulated prefix

**Statement.** Given real scalars x_1,…,x_n on an available exact input grid and a coarse mesh h>0, set S_k=Σ_{i≤k}x_i and y_k=h[round(S_k/h)−round(S_{k−1}/h)], S₀=0. Then every y_k lies on hℤ, each |y_k−x_k|≤h, and every prefix-sum error is at most h/2. Construction uses n exact additions, n nearest roundings and n differences.

**Proof.** The prefix sum of the y’s telescopes to h round(S_k/h), whose error from S_k is at most h/2. The individual error y_k−x_k is the difference of two such prefix errors, hence at most h in magnitude. The stated operations directly construct the list. Exact prefix sums may require the original input grid and log n extra magnitude bits; those working costs are not replaced by the coarse output precision.

**Action.** Prepare coarse aggregate records with a length-independent total-error allowance for a consumer that only needs their prefix sums.

**Frontier target.** aggregate-record precision before a common-label consumer.

<a id="a078"></a>

### A078 — Theorem: A borrowed residual bank can coarsen all but one exact aggregate record

**Statement.** Assume n≥1. Let inputs x_i and arbitrary initial residual r₀ be on a fine grid, and let h be a coarser grid. For i=1,…,n−1 emit y_i=h round((x_i+r_{i−1})/h) and set r_i=x_i+r_{i−1}−y_i. Emit the final fine record y_n=x_n+r_{n−1}−r₀, then restore the residual by subtracting r_{n−1}−r₀. The bank returns to r₀ and Σy_i=Σx_i exactly; after each coarse step |r_i|≤h/2.

**Proof.** Each step preserves the invariant Σ_{j≤i}y_j+r_i=Σ_{j≤i}x_j+r₀, obtained by substituting the update. The nearest-rounding definition bounds r_i independently of i. At the last step the fine record cancels r_{n−1}−r₀, so the aggregate identity is exact. Subtracting that same known difference from the current residual restores r₀. A retained copy or equivalent read access to r₀, its preparation and its final use are explicit required resources; the last record pays fine precision and may contain magnitude proportional to |r₀|.

**Action.** Offer a real dirty-bank aggregate consumer n−1 coarse outputs plus one fully priced fine tail, rather than pretending the lost residual disappears.

**Frontier target.** source-consuming aggregate with exact dirty-bank restoration.

<a id="a079"></a>

### A079 — Theorem: Only consumer-visible directions need an accuracy target

**Statement.** Let C:V→Y be linear and V=U⊕K with K⊆ker C. If an implementation changes u+k to u+e+k′, u,e∈U and k,k′∈K, its consumer error is exactly Ce and is at most ||C|_U||||e||. Thus visible dimension dim U, not dim V, governs a grid error budget once a paid decomposition and compatible consumer are supplied. Any use of the displayed Euclidean grid estimate requires orthonormal visible coordinates; a general supplied basis instead carries its actual synthesis-operator norm.

**Proof.** Apply C to the exact and implemented states. Both K-components vanish, so their difference is C(u+e)−Cu=Ce. The restricted operator-norm bound gives the inequality. A grid in a specified orthonormal basis of U with d=dim U real coordinates and mesh h has ||e||≤sqrt(d)h/2 by the coordinate rounding estimate. Consequently h≤2ε/[||C|_U||sqrt(d)] is sufficient, with the zero-map case requiring no visible accuracy. Decomposition, reconstruction and storage costs are separate physical rows.

**Action.** Formulate a replacement precision interface in a proved consumer quotient, allowing arbitrary irrelevant dirt while pricing every basis conversion.

**Frontier target.** consumer-compatible dirty-response precision.

<a id="a080"></a>

### A080 — Theorem: A bilinear consumer factors through two priced visible quotients

**Statement.** Let B:X×Y→Z be bilinear, K_X⊆X and K_Y⊆Y satisfy B(K_X,Y)=0 and B(X,K_Y)=0, and choose complements U_X,U_Y. Arbitrary changes to the kernel components leave the output unchanged. If visible perturbations have norms ε_X,ε_Y and visible exact magnitudes X₀,Y₀, the output error is at most L(Y₀ε_X+X₀ε_Y+ε_Xε_Y), where L bounds B on U_X×U_Y.

**Proof.** Write each input as its complement and kernel components. Expand B bilinearly; every term containing a kernel component vanishes by the two annihilation hypotheses. The output is therefore exactly B(u_X,u_Y), even after arbitrary kernel changes. Expand the two visible perturbations as in A074 and apply the restricted bilinear norm L. The separate left and right annihilation assumptions also kill the kernel-kernel term; no unsupported one-sided claim is used.

**Action.** Prove a source-consuming bilinear boundary that tolerates uncomputed dirt in both inputs, with an explicit precision bill on only the visible quotient coordinates.

**Frontier target.** two-sided dirty-response consumer interface.

<a id="a081"></a>

### A081 — Theorem: Rational trial exponents admit finite algebraic gain certificates

**Statement.** Let p=A/B∈(0,1) with positive integers A,B, and let G=Σ_j c_j r_j^p−d with rational c_j,d and positive rational ranks r_j. If a proved bound G≥η>0 is available, finitely many rational bisections of the roots z_j^B=r_j^A produce a strictly positive rational lower bound for G.

**Proof.** Choose rational initial brackets for every positive root, for example [0,1+r_j^A]. Bisection is exact because comparison of a rational midpoint’s B-th power with r_j^A is rational arithmetic; monotonicity keeps a valid bracket. Let C=Σ|c_j|. If C=0 the sign is rational already. Otherwise bisect until every root interval has width below η/(2C). Evaluate positive coefficients at lower endpoints and negative ones at upper endpoints. The resulting lower G differs from the true G by less than η/2, hence is positive.

**Action.** Certify a proposed complete paid-profile improvement at a rational symbolic trial exponent using only exact rational operations, not trusted floating powers.

**Frontier target.** strict paid-gain certificate construction.

<a id="a082"></a>

### A082 — Theorem: A nonzero rational-power gain has an explicit separation bound

**Statement.** Let integer ranks satisfy 1≤r_j≤m, integer coefficients c_j,d, and p=A/B∈(0,1). If G=Σ_{j=1}^k c_j r_j^p−d is nonzero, put D=B^k and H=max(1,|d|+mΣ|c_j|). Then |G|≥H^(−(D−1)). This is an explicit, possibly large, certificate-resolution bound.

**Proof.** Each r_j^(A/B) is an algebraic integer because it satisfies the monic integer polynomial z^B−r_j^A. They generate a field of degree at most B^k by the tower bound. Thus G is a nonzero algebraic integer of degree e≤D. Every conjugate of each radical has absolute value r_j^p≤m, so every conjugate of G has magnitude at most H. The nonzero constant coefficient of its monic minimal polynomial is an integer of magnitude at least one and equals the product of its e conjugates up to sign. Isolating the chosen |G| gives |G|≥H^(−(e−1))≥H^(−(D−1)).

**Action.** Choose a finite exact-comparison resolution for a nonzero native gain; the exponential dependence is explicit and is not advertised as an efficient large-instance algorithm.

**Frontier target.** termination bound for exact native-profile comparison.

<a id="a083"></a>

### A083 — Theorem: Affine dirty-endpoint correctness has a complete finite test

**Statement.** Let a declared finite native word act affinely on all data and dirty scratch coordinates, W(z)=Az+b, over a field, and let the required endpoint be V(z)=Cz+d. If W and V agree at zero and at every coordinate basis vector, they agree on every input, including arbitrary correlated dirt. Prefix costs and admissibility must still be proved for the actual word.

**Proof.** Agreement at zero gives b=d. Agreement at e_i then gives Ae_i=Ce_i after subtracting b=d. The matrices have identical columns, hence A=C. For arbitrary z, linearity now gives W(z)=Cz+d. Testing only the clean-data subspace would not compare the scratch columns, so all declared dirty coordinates are included. This finite test proves the endpoint at the stated dimension, not a uniform compiler for unstated larger dimensions.

**Action.** Give a complete algebraic endpoint certificate for a proposed arbitrary-dirt native rewrite rather than checking only clean fixtures.

**Frontier target.** exact arbitrary-dirt native boundary certificate.

<a id="a084"></a>

### A084 — Theorem: A polynomial contract family has a complete finite parameter certificate

**Statement.** Let every entry of an endpoint defect matrix be a polynomial of degree at most D_j in parameter t_j over a field. If it vanishes on a Cartesian grid of D_j+1 distinct values in each coordinate, it vanishes identically and the endpoint is correct at every parameter value.

**Proof.** For one variable, a nonzero polynomial of degree at most D has at most D roots, proved by successively factoring distinct linear factors. For several variables, fix all but the last grid coordinate. The resulting univariate polynomial vanishes identically, so each coefficient polynomial vanishes on the smaller Cartesian grid. Induct on the number of variables. Apply this argument entrywise to the defect matrix. Degree bounds must be derived from the actual word; reusing a bound after adding a multiplication gate is not justified.

**Action.** Prove a whole parameterized native identity from a complete exact finite grid, with explicit degree and field-size hypotheses.

**Frontier target.** uniform parameter families of exact native contracts.

<a id="a085"></a>

### A085 — Theorem: A noncommutative parameter family has a sufficient differential certificate

**Statement.** Let invertible differentiable matrices M_1(t),…,M_L(t) define P(t)=M_L⋯M_1 on a real interval. Put Q_j=M_L⋯M_{j+1}. If Σ_j Q_j(M′_jM_j^(−1))Q_j^(−1)=0 throughout the interval, then P is constant. A known endpoint P(t₀) therefore certifies the full family.

**Proof.** The ordered product rule gives P′=Σ_j M_L⋯M_{j+1}M′_jM_{j−1}⋯M_1. Multiply on the right by P^(−1)=M_1^(−1)⋯M_L^(−1). Factors cancel in their written order, leaving P′P^(−1)=Σ_jQ_j(M′_jM_j^(−1))Q_j^(−1). The hypothesis gives P′=0; integrating each matrix entry on the interval proves constancy. There is no commutation assumption between factors, and no scalar phase may be removed before forming P.

**Action.** Construct endpoint-preserving parameter deformations of a native word using an exact noncommutative identity, then separately price their frame and compensation changes.

**Frontier target.** new native families beyond commuting rewrite grammars.

<a id="a086"></a>

### A086 — Theorem: Clipped water filling constructs the full continuous precision optimum

**Statement.** For a_i,w_i>0 and 0<ε<Σw_i, choose λ>0 so that b_i=max(0,log₂(λw_i log 2/a_i)) satisfies Σw_i2^(−b_i)=ε. Such λ exists, and these b minimize Σa_i b_i among b_i≥0 with that error bound. It can be found by sorting the thresholds a_i/(w_i log 2) and solving the resulting one-variable pieces.

**Proof.** For fixed λ, the convex scalar function a_i b+λw_i2^(−b) on b≥0 is minimized where its derivative vanishes, clipped to zero, giving the stated b_i. The total error is a continuous nonincreasing function of λ, starts at Σw_i and tends to zero, so an equality solution exists. On each fixed active set it equals a constant from inactive indices plus (Σ_active a_i)/(λ log 2), making it explicitly solvable. Summing the scalar minimization inequalities for any feasible competing b and using the active constraint proves optimality.

**Action.** Allocate precision when some stages legitimately need zero fraction bits, instead of applying an interior formula outside its hypotheses.

**Frontier target.** complete nonuniform precision allocation.

<a id="a087"></a>

### A087 — Theorem: Unit-price integer precision has an exact greedy construction

**Statement.** For positive weights w_i, integer b_i≥0 and unit cost per bit, choosing at each step the largest current error reduction w_i2^(−b_i−1) minimizes Σw_i2^(−b_i) after any fixed number K of bits. Stopping at the first error below a target gives a minimum-bit feasible assignment.

**Proof.** The successive reductions available at index i are w_i/2,w_i/4,w_i/8,…, a decreasing chain. Any allocation of K bits selects K terms, necessarily a prefix from each chain. The K globally largest terms can be selected with this prefix property, breaking ties in favor of earlier terms. Their sum is at least that of any other K terms. Greedy merges these decreasing chains and selects exactly this set. Hence no smaller K can have crossed a target that greedy had not yet reached.

**Action.** Find a minimum-bit discrete precision schedule for equally priced scalar lanes, including the full error target rather than rounding every continuous allocation blindly.

**Frontier target.** exact integer precision selection.

<a id="a088"></a>

### A088 — Theorem: Weighted integer precision has a finite exact dynamic program

**Statement.** Let w_i,ε>0 be rational and bit prices a_i positive integers. Given any feasible integer precision plan of cost U, an optimal plan has 0≤b_i≤floor(U/a_i). On those finite ranges choose L clearing all w_i and ε denominators, and B=max_i floor(U/a_i). Then a multiple-choice dynamic program on the integer error ticks L2^B w_i2^(−b_i) constructs a globally minimum-cost feasible plan.

**Proof.** An optimum costs no more than the supplied feasible U, so each coordinate price a_i b_i≤U gives the stated cap. Since b_i≤B, every error tick is an integer after denominator clearing. Process coordinates one at a time, storing the least cost for each attainable summed tick count and a predecessor. For each allowed b_i update by adding its exact tick and cost. Induction on processed coordinates proves the table includes every capped plan with least cost. Selecting the least-cost sum at most L2^Bε and backtracking gives the global optimum. This is pseudo-polynomial in the tick range, not a strongly polynomial claim.

**Action.** Optimize actual block-weighted grid storage exactly when independent integer round-up loses too much of a narrow primitive margin.

**Frontier target.** weighted discrete physical precision budget.

<a id="a089"></a>

### A089 — Theorem: Two simultaneous precision obligations admit a finite dual certificate

**Statement.** Let a_i,w_i,v_i>0. Suppose λ,μ≥0 with λ+μ>0 produce b_i=max(0,log₂((λw_i+μv_i)log 2/a_i)), with both error constraints Σw_i2^(−b_i)≤ε and Σv_i2^(−b_i)≤δ, and complementary equalities λ(Σw_i2^(−b_i)−ε)=μ(Σv_i2^(−b_i)−δ)=0. Then b minimizes Σa_i b_i under both constraints.

**Proof.** For each coordinate, b_i minimizes the convex function a_i b+(λw_i+μv_i)2^(−b) over b≥0, by the derivative calculation of A086. Sum those scalar inequalities for any feasible alternative. Its two weighted error sums are bounded by ε and δ, while complementary equalities make the candidate’s weighted sums attain those bounds whenever their multiplier is positive. Moving these terms to the other side gives Σa_i b_i≤Σa_i b′_i. Zero multipliers require no equality for their inactive constraints.

**Action.** Certify one precision plan meeting both forward-consumer and restoration/error obligations, instead of optimizing one while ignoring the other.

**Frontier target.** joint forward/cleanup precision optimization.

<a id="a090"></a>

### A090 — Theorem: Shared-field precision constraints can be reduced exactly

**Statement.** Partition scalar lanes into groups G, each physically forced to share one fraction precision b_G. With lane error weights w_i and bit prices a_i, the complete error and precision cost are exactly Σ_G W_G2^(−b_G) and Σ_G A_Gb_G, where W_G=Σ_{i∈G}w_i and A_G=Σ_{i∈G}a_i. Therefore A086 or A088 applied to these grouped data constructs an optimum within the actual shared-field constraint.

**Proof.** Substitute b_i=b_G into each original finite sum and regroup by G. The resulting expressions are identities, and the map between group assignments and feasible original assignments satisfying the shared-field rule is bijective. Thus any optimality or feasibility result on the grouped problem transfers exactly, with no relaxation that permits independently chosen lane precisions. Magnitude fields, common-label adapters and field preparation remain additional costs outside these two sums.

**Action.** Optimize the precisions the physical compiler can really choose, rather than counting a saving from lane-specific grids forbidden by a common field.

**Frontier target.** common-label/shared-field precision contract.

<a id="a091"></a>

### A091 — Theorem: A shared error-symbol representation can reduce paid fraction bits

**Statement.** Let a computed endpoint error be exactly Ez, where z has coordinates |z_j|≤δ_j and E=Σ_t P_t B_t is known, because event t introduces B_t z and its exact suffix map is P_t. Then ||Ez||∞≤max_i Σ_j |E_ij|δ_j. In particular, cancellation in E may be used before allocating precision, rather than replacing E by Σ_t |P_t B_t|. The implementation must reuse the same stored error symbol z_j at each declared occurrence.

**Proof.** Expand the linear error recurrence by substitution and collect coefficients of each identical symbol. This gives the stated E without any statistical assumption. For each output coordinate apply the triangle inequality to Σ_j E_ij z_j, then take the maximum. Coefficient cancellations are exact algebraic equalities. If two events round independently, their symbols are distinct and their columns cannot be combined. Computing or storing the shared rounded quantity and its coefficients is included in the caller bill.

**Action.** When a native inverse pair or compensated bank reuses a rounded response, combine its signed suffix coefficients first. Choose each fraction field from the resulting row sums; this can lower the paid precision while retaining a deterministic worst-case bound.

**Frontier target.** correlated dirty-bank precision.

<a id="a092"></a>

### A092 — Theorem: Lattice coordinates preserve exact interface constraints during rounding

**Statement.** Let B be a rational d×k matrix with AB=0, and let x₀ satisfy Ax₀=b exactly. Suppose an actual caller represents x=x₀+Bt. Rounding t coordinatewise to a grid h_j gives x̂=x₀+B t̂ with Ax̂=b exactly and ||x̂−x||∞≤max_i Σ_j |B_ij|h_j/2. The representation, multiplication by B and exact representation of x₀ and B must be included in the cost.

**Proof.** The difference is B(t̂−t). Its j-th coordinate coefficient is bounded by h_j/2; rowwise triangle inequalities give the claimed error. Applying A gives Ax₀+AB t̂=b, so no accumulated residual is hidden in a later correction. Rational B does not imply a particular machine grid: the common denominators required to represent B t̂ must be charged. Taking B as an explicitly supplied basis for an interface kernel makes this construction executable by ordinary matrix-vector operations.

**Action.** Round independent kernel coordinates instead of every lane of a constrained helper bank. This preserves the exact conservation equation at every checkpoint, with a stated distortion and a fully priced coordinate adapter.

**Frontier target.** conservation-compatible precision.

<a id="a093"></a>

### A093 — Theorem: Bipartite controlled rounding preserves all integer bank margins

**Statement.** Let X be a nonnegative rational m×n matrix whose row and column sums are integers. There is a constructible nonnegative integer Y with the same row and column sums and floor X_ij≤Y_ij≤ceil X_ij. A finite integral augmenting-path flow computation on at most m+n+2 vertices and mn+m+n edges constructs Y.

**Proof.** Write X=F+Z with F=floor X and 0≤Z_ij<1. Its residual row sums r_i and column sums c_j are nonnegative integers. Build a bipartite flow network with source capacities r_i, sink capacities c_j, and a capacity-one edge i→j exactly when Z_ij>0. The fractional flow Z saturates every source edge, so every cut has capacity at least Σr_i. Integral augmenting paths start at zero and increase flow by an integer until a maximum is reached; finite integer capacities ensure termination, and the absence of an augmenting path certifies a minimum cut by reachable vertices. The minimum cut bound forces value Σr_i. Set Y=F+the integral middle-edge flow. Each middle edge is zero or one, and support excludes already integral cells. All margins and pointwise bounds follow.

**Action.** Convert a rational bank allocation with integral total ownership on both sides into literal integer lanes without losing either family total. Charge exact flow synthesis and all resulting movement; this theorem does not imply integral packing for unrelated constraints.

**Frontier target.** integer lane allocation with two margin systems.

<a id="a094"></a>

### A094 — Theorem: Known-denominator output recovery turns a norm budget into an exact endpoint

**Statement.** Let a finite output vector y have coordinates in Q⁻¹ Z for a known positive integer Q. If a computed vector z obeys ||z−y||∞<1/(2Q), then rounding Qz to nearest integers and dividing by Q recovers y exactly. If a preceding word has a proved error bound C·2⁻ᵇ with C>0, any integer b satisfying 2ᵇ>2QC is sufficient. Integer multiplication and rounding by Q, and the storage of Q, are part of the output adapter.

**Proof.** Write y_i=a_i/Q with a_i integral. The error bound gives |Qz_i−a_i|<1/2, so a_i is the unique nearest integer. The same holds for every coordinate, including negative values. The precision criterion is exactly Q C 2⁻ᵇ<1/2. A floating-point guess for Q or an unproved denominator bound cannot replace the stated known denominator; the adapter performs the actual scaling and rounding on its declared representation.

**Action.** Where a changed block consumer produces a rational grid output, choose fraction bits from its true output denominator rather than a generic integer-output assumption, and price the reconstruction before claiming a saving.

**Frontier target.** exact output-grid adapter.

<a id="a095"></a>

### A095 — Theorem: Nilpotent feedback permits large local error gains without a contraction

**Statement.** Let e,b be finite nonnegative vectors and F a nonnegative matrix satisfying e≤Fe+b. If Fᴸ=0 for some positive integer L, then e≤Σ_{j=0}^{L−1}Fʲb. Thus any chosen b satisfying Σ_j Fʲb≤τ gives the coordinatewise error target τ, even when ||F|| is greater than one.

**Proof.** Substitute the inequality into itself L times. Nonnegativity preserves the inequality and yields e≤Fᴸe+Σ_{j=0}^{L−1}Fʲb. The first term vanishes. Matrix powers and the finite sum can be computed exactly from the actual dependency coefficients. An acyclic bank dependency graph gives such an L after topological ordering, since a product of L edges cannot exist once L exceeds the longest directed path. This argument needs no convergence limit or independence assumption.

**Action.** For a triangular consumer, use the finite path sum to allocate rounding budgets. Do not pay for a global contraction that the actual acyclic dependency does not need.

**Frontier target.** triangular bank precision closure.

<a id="a096"></a>

### A096 — Theorem: Exact scratch scheduling for a two-child out-of-place operation

**Statement.** Consider a binary expression tree with no shared subexpressions. At a node the child outputs have retained sizes r₁,r₂, child peak requirements S₁,S₂, and the parent operation needs an additional fresh output/work area t after both children finish. Among schedules which finish one child subtree before beginning the other, the exact minimum peak is min{max(S₁,r₁+S₂,r₁+r₂+t), max(S₂,r₂+S₁,r₁+r₂+t)}. All sizes include each child’s own inputs and live temporary blocks consistently.

**Proof.** If child 1 finishes first, its own evaluation reaches peak S₁. Its r₁-unit retained output remains during child 2, giving peak r₁+S₂. The parent operation requires both outputs and the additional t units. These are all execution stages, so their maximum is both achieved and necessary for this order. Interchanging the children gives the second expression. There are exactly two orders in the declared schedule class. Apply the same calculation inductively down the tree and retain the minimizing order. Aliasing, interleaving and shared-subexpression schedules are outside this exact-minimum claim.

**Action.** Compile a tree-shaped recovery or contraction into an explicit low-peak bank schedule before quoting memory or hosting costs. Include the chosen order in its contract certificate.

**Frontier target.** consumer scratch and tape budget.

<a id="a097"></a>

### A097 — Theorem: Sequential shrinking recursion has a geometric live-space certificate

**Statement.** Suppose an actual recursion evaluates its children sequentially, each of size at most qn with fixed 0<q<1. At every active node all live parent inputs, retained earlier child outputs, adapters and local work occupy at most cn units outside the active child. If base calls use at most Bn and every nonbase integer child is strictly smaller, then peak live space is at most K n, where K=max(B,c/(1−q)).

**Proof.** Induct on the integer problem size. A base case satisfies the bound. During an active child of size s≤qn, the outer live state uses at most cn and the child at most Ks, so the combined space is at most (c+Kq)n≤Kn. Between children there is no active child; all retained outputs and local state are already covered by cn. Sequential reuse of the same child workspace is part of the stated execution. If retention grows with the number of completed children, its maximum must be included in c rather than omitted.

**Action.** Supply a literal linear-space schedule for a changed recursive consumer. This is useful only when the profile gain survives the extra operations of sequentialization and the declared hosting/tape simulation.

**Frontier target.** uniform recursive live-space.

<a id="a098"></a>

### A098 — Theorem: Fixed dyadic words across logarithmic depth have explicit bit growth

**Statement.** Let B,f,d,c₀ be nonnegative integers and c≥0. Consider a branch of at most L=⌈c log₂ n⌉+c₀ dyadic linear gates, n≥2. Each row has absolute coefficient sum at most M≥1, every coefficient denominator divides 2ᵈ, and initial coordinates have magnitude at most 2ᴮ and fraction denominator dividing 2ᶠ. Exact intermediate coordinates have magnitude at most 2ᴮ Mᴸ and denominator dividing 2^(f+dL). A signed fixed-point format therefore needs at most B+⌈L log₂ M⌉+f+dL+3 bits per coordinate. Initial dirty banks are included in the initial magnitude and grid bounds.

**Proof.** One gate multiplies the maximum coordinate magnitude by at most its absolute row sum M. Induction gives 2ᴮMᴸ. On the denominator side, multiplying dyadic coefficients increases the denominator exponent by at most d; adding terms introduces no larger denominator. Induction gives f+dL. Reserve one sign bit and sufficient integer range for the magnitude, plus the stated fraction exponent; the extra constant absorbs endpoints and zero. These are exact arithmetic bounds, independent of cancellation or probabilistic assumptions. Gate count, row sparsity and the bit cost of arithmetic are separate charged resources.

**Action.** For a fixed native word expanded along logarithmic recursion depth, derive its actual B+f+O(log n) coordinate sizes before applying a bit-time or tape theorem. This does not prove that an arbitrary tensor certificate has such an expansion.

**Frontier target.** uniform dyadic native-word size.

<a id="a099"></a>

### A099 — Theorem: Disjoint rewrite selection with resource caps has an exact finite optimizer

**Statement.** For k genuinely disjoint rewrite sites, let each have a finite menu of fully executable alternatives with exact rational savings and nonnegative integer charges in d resource dimensions. Include an identity alternative of zero saving and zero charge. For finite integer caps U₁,…,U_d, dynamic programming on the prefix of sites and the used resource vector returns an executable combination with maximum total saving among those menus, using at most Σ_i |menu_i|·Π_j(U_j+1) transitions.

**Proof.** Let D_i(u) be the largest total saving attained by the first i sites using exactly u, with unattainable states −∞ and D₀(0)=0. For every alternative a at site i update D_i(u+c(a)) by D_{i−1}(u)+g(a) when all caps hold. Induction shows that every actual prefix choice is represented by its final alternative and an earlier state, and every update is an actual choice. Backpointers reconstruct the maximizing word combination. Exact rational comparison decides ties without numerical ambiguity. Disjointness must include helper ownership, interface compatibility and additive charges; otherwise this dynamic program is not a valid model.

**Action.** Choose the best admitted mixture of proved local rewrites under bank, movement and precision caps, rather than maximizing a scalar ADD saving. This is a finite synthesis theorem, not a claim that current frozen packing has an undiscovered gain.

**Frontier target.** charged multi-resource portfolio.

<a id="a100"></a>

### A100 — Theorem: A complete changed-contract package gives a symbolic all-size admission theorem

**Statement.** Fix s>0. Suppose a completely specified uniform exact multiplication implementation has a finite set of typed states, legal integer children strictly smaller than the parent, all bases explicitly implemented, and the actual normalized work recurrence T_i(n)≤c_i nˢ+Σ_e a_ie T_(j(e))(s_ie(n)), with a_ie≥0 and s_ie(n)≤q_ie n. Define M_ij=Σ_{e:j(e)=j} a_ie q_ieˢ. Suppose a supplied positive vector v satisfies Mv≤(1−η)v with η>0. All adapter, recovery, precision, restoration, source-access and hosting costs must be included in c or M, with fixed effective constants. Then T_i(n)≤K v_i nˢ for K=max(max_i base_ratio_i, max_i c_i/(ηv_i)). Any previously established outer theorem whose complete hypotheses match this exact implementation may use this bound; no new numerical κ is asserted.

**Proof.** The construction of the implementation is an explicit input, not supplied by its profile. Because all children are smaller, strong induction is valid. For each state, substitute the inductive child bounds into the actual recurrence. The result is at most c_i nˢ+K(Mv)_i nˢ≤[c_i+K(1−η)v_i]nˢ≤K v_i nˢ. The base_ratio includes every base size in its declared state and is finite by the implemented base table. Exact correctness, uniformity and all outer hypotheses remain those explicitly proved for this same implementation; the induction does not manufacture a missing compiler or reduction. Thus the stated implementation receives the bound without any unpaid oracle or asymptotic transition.

**Action.** Assemble a future native/physical/tensor construction only after its concrete costs form one compatible typed recurrence. A positive symbolic reserve then pays the complete all-size bound. This collection supplies components and admission tools; it does not instantiate a better multiplication exponent.

**Frontier target.** complete symbolic admission and honest outer use.

