# Rank-gap-aware demotion and finite physical allocation

Frozen round: public PRs through #1120, with #1117 the largest reported conditional value in that snapshot. This file proves sufficient transformations and exact pricing rules; it does not claim an implemented new kappa before the complete changed word, table, charts and invoice are checked.

## 1. A strict extension of PR1111's construction

PR1111 reverses the entrance promotion on helpers 635,637,638,639. Its local paid-child change is

    L = -8 H1 + 8 H2 + 4 H3 - 4 H4.

The four helpers each gain one unit of width. Preserve the actual local recipe admission, pair the four widened roles bijectively with four width-four donor positions, and require that the receiving pending children have at least one remaining axis each. Keep the old call times and retain every other role. Rebuild offsets chronologically, actual physical charts and every pending remainder.

The general exact complete-profile change in one changed call with donor remainders r1,r2,r3,r4 is

    Delta = L + sum_j (H_(rj-1) - H_rj), with H0 = 0.

All rank mass is preserved: L contributes four units and the four remainders each lose one. Call-wise family uniqueness and actual windows are still required; rank-gap counts alone do not authorize a placement.

**Theorem.** Each of the following three legal donor remainder patterns gives a strict complete moment saving for every 0 < b <= 1/500:

    (1,1,1,1): Delta0 = -12 H1 + 8 H2 + 4 H3 - 4 H4;
    (1,1,1,2): Delta2 = -10 H1 + 7 H2 + 4 H3 - 4 H4;
    (1,1,1,3): Delta3 = -11 H1 + 9 H2 + 3 H3 - 4 H4.

Thus a donor search limited to four rank-one gaps misses two additional sufficient classes. The latter two remove three complete remainder children, rather than four. No new child is omitted from the invoice.

**Proof.** Put a=1-b and f(r)=r^a, f(0)=0. The price of a signed histogram is its signed sum of f(r); the actual m=73 moment differs by the common positive factor 73^b. Define

    D0(a) = -12 + 8*2^a + 4*3^a - 4*4^a;
    D2(a) = -10 + 7*2^a + 4*3^a - 4*4^a;
    D3(a) = -11 + 9*2^a + 3*3^a - 4*4^a.

Each Dk(1)=0. Using ln4=2ln2, their derivatives at 1 are

    D0'(1) = 12 ln3 - 16 ln2;
    D2'(1) = 12 ln3 - 18 ln2;
    D3'(1) =  9 ln3 - 14 ln2.

The rigorous elementary bounds ln3>1.0986 and ln2<0.6932 give derivative lower bounds 2.092, 0.7056 and 0.1826 respectively. On a in [499/500,1], use 2^a<=2, 3^a<=3, 4^a<=4 and ln2<0.7, ln3<1.1, ln4<1.4. Absolute second derivatives are at most

    53.72, 52.74, 51.07 respectively.

By the fundamental theorem of calculus, the derivatives throughout that interval are therefore at least

    1.98456, 0.60012, 0.08046 respectively.

Consequently D0(1-b)<=-1.98456*b, D2(1-b)<=-0.60012*b and D3(1-b)<=-0.08046*b, all strictly negative. The logarithm bounds can be established directly with the positive series ln x=2 sum_(k>=0) t^(2k+1)/(2k+1), t=(x-1)/(x+1), and a geometric upper bound for the tail; no numerical solver is needed. This proves the complete rank-price saving, conditional only on the literal physically admitted recipe and allocation described above.

For any number of distinct changed calls, add these signed histograms to the complete baseline profile and reprice that single resulting profile. Never add advertised kappa gains. The negative complete-moment change is strict even if some individual changes appear locally more expensive.

## 2. Two actual mechanisms from the registered OpenAI sources

### A. Species-preserving exact allocation

Source:

    D:/proof/external/openai-math/lean/OAI/Computability/BinPacking/Inventory/SpeciesAllocation.lean

Declarations `allocation`, `allocation_species`, `exists_allocation`, lines 13-31, namespace `OAI.BinPackingGap.SpeciesAllocation`.

Fixed statement: for a finite type Slot, request:Slot->Species and stock:Species->Nat, if for every species s the cardinality of {b:Slot | request b=s} equals stock(s), there is a bijection

    e : Slot <-> Sigma s, Fin(stock(s))

with first component e(b) equal to request(b). The proof factors through the fibers of request and finite ordinal enumerations.

Application: form eligibility types from actual width, provider, complete call window and per-call exclusion signature. Only group physical donor positions when their entire eligibility signatures agree. Equal finite type counts then give a literal deterministic bijection (stable list order is one implementation), rather than an unproved allocation oracle. Directly verify family uniqueness and rebuild physical charts after the lift. In particular, demotion donor permutations preserve all unaffected roles; the four changed widths are individually matched with larger exact residual capacities. This theorem justifies quotienting by complete eligibility types, not by rank alone.

### B. Exact coordinate-exchange census with polynomial generation

Sources:

    D:/proof/external/openai-math/lean/OAI/Combinatorics/ContingencyTables/Transport/IntegerExchangeArithmetic.lean
    D:/proof/external/openai-math/lean/OAI/Combinatorics/ContingencyTables/Sampling/ProfileExchangeCandidates.lean

Fixed statements:

- `OAI.ContingencyTables.IntegerWeightedTransport.adjacent_iff_arithmetic`: two natural profiles are an integer unit-exchange edge iff there exist distinct coordinates i,j with positive source count X(j), and Y is obtained by transferring one count from j to i.
- `OAI.ContingencyTables.ProfilePrograms.mem_allExchanges_ofFn`: membership in the generated exchange list is equivalent to one of these ordered coordinate updates.
- `allExchanges_length`: the generated list has exactly n^2 entries for a length-n profile.
- `polynomial_allExchanges`: the concrete binary list generator has polynomial-time realization.

Application: derive all remainder/profile candidates arithmetically first, reject moment-losing candidates, and then lift only exact eligibility-preserving physical realizations. This is a complete profile-level screening rule with explicit finite output; physical lifting is checked separately. For the present construction, the signed profile is derived from the literal four width increases and the four actual recipient remainders, yielding the three exact deltas above. This avoids copying old receipts and avoids a heuristic entropy-only claim. The universal negative moment theorem permits three rank-one gaps plus a rank-two or rank-three gap as actual sufficient candidates, beyond PR1111's four-unit-gap admission rule.

Source reading is reuse of mathematical mechanisms, not fresh Lean certification of this adaptation. The downloaded OAI statements have not been recompiled in this round.

## 3. Required concrete admission

The highest public #1117 word additionally changes ends on different helpers 574/575. A joint word must check both changes together: disjoint register numbers alone do not prove propagated frame compatibility. The full scalar, frame/cap, phase, arbitrary-dirt and residual contracts must be replayed on the mixed literal word. Every widened helper must retain its actual complete-call window and must not alias another helper in that invocation. All pending axes, wrappers, residual factors, remaining children and row/prefix charges must be rebuilt. Existing sufficient owner-replacement semantics then apply to the literal replacement table. No unknown gadget or oracle is assumed.

A finite table plus those actual checks realizes a better complex supplier; its final moment and outer grid must still be computed exactly through the pinned engine. No all-size/compiler, physical/common-label, analytic or unconditional multiplication claim is made beyond the retained inherited interfaces.

## 4. Uniform saving for the whole exponent interval

The preceding small-b estimates give explicit margins, but the three sufficient patterns in fact improve every exponent 0<b<1. This stronger proof was contributed by the owner worker after the initial pattern extension was communicated.

Put u=2^(1-b), so 1<u<2, and p=ln3/ln2. Then 14/9<p<2: the lower bound is the exact integer inequality 3^9>2^14. The three deltas become

    h0(u)=-12+8u+4u^p-4u^2,
    h2(u)=-10+7u+4u^p-4u^2,
    h3(u)=-11+9u+3u^p-4u^2.

For 1<u<=2, p(p-1)u^(p-2)<2. Thus each h has strictly negative second derivative. Their derivatives at the right endpoint are respectively 6p-8, 6p-9 and (9/2)p-7, all positive. Since the derivatives decrease, they are positive throughout [1,2]. Each h(2)=0, so h(u)<0 for every 1<u<2. This proves strict complete moment saving throughout 0<b<1, with no approximation or solver.

## 5. Several independent demotion groups, with actual joint words

The current candidate uses the prefix order of register groups 635,603,611,619,627. The corresponding helper-index quadruples are [411,413,414,415], [379,381,382,383], [387,389,390,391], [395,397,398,399], [403,405,406,407]. Variant k applies the first k groups together.

The implementation must prove the joint variant profile L*k from that actual word; disjoint register names do not on their own prove independent propagated frame paths. For each actually selected k, recount every canonical frame transition, derive all 480 endpoint widths, bind the fresh scalar/native restoration receipt, and check the changed Clifford phases. Only then assign that variant to literal calls whose exact donor allocation supplies all 4k extra axes.

After this joint admission, different calls compose directly using the complete-call identity and their literal event windows. Each widened helper remains a distinct input stream, with its own exact physical chart; every pending child remains the tensor product of chronologically reserved disjoint factors and the explicitly paid remainder. Dispatch is a finite table of concrete admitted variants, not an unknown solver or gadget. Source-event ordering and the private workspace namespace are unchanged. Applying all 359 nominated groups yields the single complete histogram update

    356*Delta0 + Delta2 + 2*Delta3 + (H1 - 2H6 + H11).

The last term is a separately checked three-role owner-cycle concentration. Its moment improves by strict concavity. All four summands are strict savings once their actual physical witnesses and joint local variants pass. Final pricing uses the complete resulting histogram, rather than adding exponent gains.
