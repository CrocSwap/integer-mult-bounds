# Complete cap-safe hybrid triple decoder

2026-10-09. New sufficient universal scalar/address construction; no Lean formalization and no final paid kappa claim. The accompanying C++ checks are exact decoder and incidence checks, not a substitute for full dirty-channel/rank assembly.

## Exact input family and root

Take p=12 physical coordinate pairs, h=24, with endpoint basis e_(i,0), e_(i,1). Let d_i=e_(i,0)+e_(i,1). Old good labels choose one endpoint in each of three distinct pairs:1760 labels. Add every missing triple z(i,j,e)=d_i+e_(j,e), i!=j:264 labels. These2024 labels are exactly all three-element subsets of the24 coordinates.

The actual rational address metric is G=I-J/9. Every label chi has weight3, so its read covector is c_chi=3chi-1, proportional to Gchi. Therefore a source label lies in a target read cap exactly when |source intersect target|=1. This uses rational addresses/local odd-prime rings; it is not a substitution of F2 addresses. The payload decoder itself is binary.

Let B be the coordinate-by-label incidence matrix. Define H[target,source]=1 if their intersection has size1, else0. Then over every characteristic-two ring,

    B^T B + H = I.

Indeed for intersection sizes0,1,2,3 the left entry is respectively0,0,0,1; intersection3 means equality of the three-element labels. This proves the complete desired fresh decoder, not merely a necessary condition. The old good-good side and local partner terms already implement the corresponding H block. Keep them exactly; append the three missing blocks below and enlarge the centre stars to the full family. Every term in the partitions below is an exact integer indicator of H, and every delivered individual source has intersection1 with the target. No cancellation of forbidden reads is assumed.

Define U_a=sum_(b!=a,e) z(a,b,e), V_(b,e)=sum_(a!=b)z(a,b,e). Here sums mean the corresponding source payload values.

## Bad source to good target

Let target T have three distinct pair indices I={a,b,c} and endpoint selectors epsilon_b. Deliver:

1. For each a in I, sum z(a,k,e) over k outside I and both e.
2. For each b in I, sum z(k,b,epsilon_b) over k outside I.
3. For every ordered distinct a,b in I, the individual source z(a,b,1-epsilon_b).

These disjoint source sets are exactly those missing labels intersecting T once. There are three U two-hole roots, three V two-hole roots, and six local single-source deliveries. Their actual source-span ranks are18,9,1. A U root can deliver to all eight good selectors of the same cube; a V root to the four having the specified selector. All targets therefore have true common-cap membership.

## Bad source to bad target

For target t=z(i,j,e), deliver:

1. sum z(j,a,f) over a outside {i,j}, both f;
2. sum z(a,i,f) over a outside {i,j}, both f;
3. sum z(a,j,e) over a outside {i,j}.

The ranks are20,11,10. These sets are disjoint and exactly enumerate all missing sources with intersection1. Implement the middle term as TWO V channels, V_(i,0) excluding a=j and V_(i,1) excluding a=j. This avoids the potentially degenerate combined W frame altogether, without changing the decoder.

## Good source to bad target

For target t=z(i,j,e), deliver these disjoint subsets of good sources:

1. all good cube totals having pair i and excluding pair j;
2. all good star sources having endpoint (j,e) and excluding pair i;
3. all good sources having pair i and endpoint (j,1-e), with the third pair arbitrary outside {i,j}.

Each source intersects t once. The ranks are21,20,21. This is a cap-compatible decomposition of the algebraic expression U_good_i+S_good_(j,e)-2P_good_(i,j,e); the expression alone would have forbidden intermediate reads, which are absent in this actual partition.

The upper-rank constraints are explicit: set excluded coordinate pairs to zero; for family1 sum outside pair i equals twice the sum on pair i; for family2 set the opposite j endpoint to zero and sum outside j equals twice its retained coordinate; for family3 the sum on pair i equals the retained j coordinate and the sum on all other pairs equals it too. These give h-3,h-4,h-3. Independent endpoint-difference vectors give every free pair toggle. Their pair-sum quotient vectors e_i+e_a+e_b, e_j+e_a+e_b and e_i+e_j+e_k span the remaining dimensions, proving equality when p>=5.

## Literal U/V span and prime guard

For s distinct U sources with the same doubled pair a, G-Gram is I_s+J_s: diagonal2, off-diagonal1. Its determinant s+1 is nonzero, and the s source labels are independent. For s V sources with the same endpoint (j,e), doubled pairs are distinct and intersect only that endpoint: G-Gram=2I_s, determinant2^s. Thus all support-subset U/V intermediate frames are nondegenerate, with fixed small denominator/factor primes. This is a universal elementary argument, not an observed numerical rank. Relevant U s<=22 and V s<=11 avoid every prime q>2^80.

By contrast, combining both V selectors over k doubled pairs has basis z(a,i,0) and e_(i,1)-e_(i,0), Gram[[2I,-1],[-1^T,2]], determinant2^(k-1)(4-k). It degenerates at k=4. The implementation explicitly retains the two safe V channels instead of hiding a chart repair.

## Concrete finite arithmetic

hybrid-cap.cpp enumerates the full family and all target/source entries. HYBRID-CAP-CHECKS.txt records998976 cross/missing block entries,319440 literal cap memberships, and4096576 full-decoder entries, all passing. Modular1000003 ranks are lower bounds overQ; the explicit span constraints above give matching upper bounds. Its tests use C++ only.

The structural/retrieval workers provide fully specified support-disjoint11-input two-hole DAGs and literal acyclic carrier schedules; every intermediate support lies inside each output reached from it. These are actual finite programs, not an assumed query solver. Last-use copying, nested rational frames, source/target timing, old/new centre wiring, gauge placement, dirty adjoint correction and complete bank/rank/stock cost must all be included by the hybrid compiler lane before any new exponent is asserted.

## What remains inside this construction

Full stars now span h-1=23 instead of22. A uniform good-style source path would give delta=2*2024-3*24*23=2392; this is only an optimistic bill. If new bad sources require the older ordinary path, their actual additional deficit may instead be one per source, giving delta2128 before further changes. Neither number is a proved paid supplier profile here. The source, target, root and dirty compiler must derive the true histogram and pass the strict moment and47-constraint root assembly. The proven result is the complete decoder together with explicit cap-safe query partitions and nondegenerate U/V source-support frames.