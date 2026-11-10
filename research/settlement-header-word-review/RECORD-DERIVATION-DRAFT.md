# Abstract derivation of the zero-charge settlement price

## Verdict, role and scope

The supplied charge-settlement and anchored full-affine-family implications follow in the stated field/transvection model. This is a target-known written derivation for external review of PR6712, not a new h-Z theorem, partition count, physical price or census. The source and classical methods retain priority.

The coordinator supplied the h-Z target, operation model, anchor requirement and proposed subset-DP association. Before sealing this note I did NOT read the current6712 PROOF, settlement/code, peer or coordinator draft. Historical common-image/law context and earlier source exposure in other rounds are not excluded; this is not blind discovery. No source/new scientific program, field test, DP, constructor, import, compilation, experiment, census or kernel was executed. Only this written argument and metadata hash/time were authored. Actual source binding remains a post-seal obligation.

## 1. Exact charge model

Let K be a field, let m be a finite number of labeled slots, let u be a column in K^m and W a matrix with m columns W_i in a fixed finite-dimensional vector space E over K. Assume

    W*u=sum_i y_i=0,    y_i=u_i*W_i.

Let A={i:y_i!=0}, h=|A|. Initial zero-charge indices remain genuine available slots; they are not deleted from a prospective algorithm. Their u_i or W_i may be nonzero even though the product is zero.

Free headers are permutations and invertible diagonal matrices, acting COUPLEDLY as u←P*u, W←W*P^-1. A paid primitive is a row addition P=I+a*E_(i,j), i!=j and a!=0 in K, with that same coupled action. Every such coefficient is available at unit paid cost. Arbitrary general linear mixing is NOT free, and a restricted coefficient alphabet or coefficient-dependent physical cost is a different problem.

For h>0, let Z be the maximum number of blocks in a partition of the LABELED active set A into nonempty zero-sum subsets. Such a partition exists because sum_A y_i=0. For h=0 use the empty partition and Z=0. A single nonzero charge cannot have total zero, so h=1 does not occur under these premises. Repeated equal vector values are still distinct labels.

The settlement objective is to make every individual charge zero. The count-law/header-passing objective needs the extra affine/anchor conditions in Section5; it must not be silently identified with settlement for an arbitrary family.

## 2. Local conservation and a lower bound including zero helpers

For a paid addition i←i+a*j, the updates are

    u_i'=u_i+a*u_j,      W_j'=W_j-a*W_i,

with u_j and W_i unchanged and all other components unchanged. Therefore

    y_i'=y_i+a*u_j*W_i,
    y_j'=y_j-a*u_j*W_i.

Only those two charges can change, and their vector sum is conserved. This remains true when either initial/current charge is zero. In particular a zero-charge helper can acquire a nonzero charge; ignoring such slots in the lower bound would be invalid.

Trace labeled strands through every free permutation; free diagonal scaling leaves each charge unchanged. Equivalently, conjugating a transvection by a monomial matrix merely changes its distinct indices and nonzero coefficient, so one may track/normalize free monomial actions without granting additional mixing. Draw an undirected edge between the tracked labels for each paid primitive. Multiple/ineffective edges still cost; they do not weaken the bound.

Within any connected component of this paid-operation graph, its final charge sum equals its initial sum. If all final charges are zero, each component containing active labels therefore determines a nonempty zero-sum subset of the initial A. Those subsets partition A. Let their number be C. Then C<=Z.

A component with a active labels and any additional zero-charge helpers needs at least a-1 edges: a connected graph on all its vertices needs at least vertices-1, which is no smaller. Sum over the C active components; ignore components with no initial active label. Any settling word of length L satisfies

    L>=sum_components(a-1)=h-C>=h-Z.

This covers arbitrary intermediate charge creation/cancellation, initial zero helpers, repeated charges, and free monomial normalization. It is not merely a statement that one operation can remove at most one nonzero charge; an operation can remove two opposite charges at once, and the component/zero-sum partition is what accounts for that.

## 3. A legal attaining word with a nonzero donor component

Take a partition into Z zero-sum blocks. In each block B choose one collector/donor j. Since its INITIAL charge is nonzero, u_j!=0. For each i in B except j, apply

    i <- i - (u_i/u_j)*j.

The coefficient is nonzero: before its elimination, that u_i is its unchanged initial nonzero value, and u_j stays nonzero. The operation sets u_i to0 and transfers its entire current charge to j:

    y_i' =0,    y_j'=y_j+y_i.

The collector's u_j is never changed by these operations. Even if its CHARGE happens to cancel at an intermediate stage, u_j remains nonzero and the next division is still legal. No assumption that its W_j or charge stays nonzero is needed.

After |B|-1 operations all charges of B are zero because its initial sum was zero. Other blocks and all initial zero-charge helpers were untouched. Thus h-Z legal row additions settle every charge, matching the lower bound. This is an algebraic operation count under the full nonzero-field coefficient alphabet, not a bit/arithmetic/route/storage tariff. The chronological header product uses the same coupled W inverse at every step; it is not permissible to update u alone.

## 4. Zero-prefix subset DP and partition backtracking

For S subset of A let Y(S)=sum_(i in S)y_i. Define D(empty)=0 and, for nonempty S,

    D(S)=max_(i in S) D(S\{i}) + indicator[Y(S)=0].

Interpret D(S) as the maximum number of NONEMPTY zero-sum cumulative prefixes along an ordering of S. This interpretation follows by the last-element recurrence: all earlier prefixes form an ordering of S\{i}, and the new final prefix contributes precisely the displayed indicator. It does not require Y(S)=0 at intermediate subsets.

For an ordering of the full A, its total sum is zero. Cut at every nonempty zero-prefix endpoint, including the last. Differences of two zero cumulative sums give nonempty consecutive zero-sum blocks covering A. Hence its number of counted endpoints is at most Z.

Conversely order the blocks of any Z-block zero-sum partition, with their labels in any within-block order. Every block end is a zero-prefix endpoint, so the maximum is at least Z. Together these observations prove D(A)=Z. They also explain why maximizing the count, rather than minimizing it, gives the least settlement price h-D(A).

Store one actual maximizing last-label choice at each subset. Backtrack from A to empty and reverse the removed-label sequence. Its zero-prefix boundaries give an actual labeled partition; the star-donor construction of Section3 then supplies an attaining word. No numerical field/DP enumeration is needed for this proof. If a code instead deduplicates equal charge values, counts the empty prefix, changes zero tests to approximate tests or reconstructs labels in the wrong direction, it no longer follows this association. The exponential subset state space is a source implementation consideration, not a practical scalability claim proved here.

## 5. Full affine-family guards: necessity and anchored sufficiency

Now let b be a row with b*u=1, assume W*u=0, and consider the FULL affine family

    v_lambda = b + lambda*W,    lambda in E^*,

where all coefficient rows are available, not an arbitrary subset. Under a header transform u,b,W together. For prefix j put

    s_j=sum_(i<=j)b_i*u_i,    z_j=sum_(i<=j)u_i*W_i.

The rank-one determinant identity gives the complement's leading minor as

    1-s_j-lambda*z_j.

For z_j!=0, the map lambda↦lambda*z_j is onto K (choose a nonzero coordinate and solve). Thus some family member has a zero minor at that prefix. If ALL members pass ALL proper prefixes, necessarily z_j=0 for j=1,...,m-1, and also s_j!=1. Since z_0=z_m=0, differences force every individual charge y_i=0, including the final one. Therefore any passing header pays at least the settlement lower bound. The lambda that fails can depend on j; no single lambda failing every prefix is required.

Settlement alone does not automatically satisfy the scalar prefix conditions s_j!=1. For an attaining upper bound assume an ANCHORED scalar carrier c:

    u_c!=0,    W_c=0,
    b_i=0 for i!=c,    b_c*u_c=1.

The anchor is not active. The attaining word in Section3 uses only initially active indices, hence avoids c, preserves u_c and W_c, and preserves b because its transvection targets have b_i=0. All charges become zero with exactly h-Z paid operations while the scalar carrier survives. A final free permutation places c last. Every proper prefix then has z_j=0 and s_j=0, so every full-family proper minor equals1. This proves the same price for the anchored full-family passing problem, without an extra paid scalar-settlement step.

The lower bound allowed arbitrary paid words, including use of zero helpers or the anchor. The upper construction preserves the anchor. Thus allowing additional such words cannot beat the lower bound, and no restriction that all hypothetical words preserve the anchor was needed. Conversely without the anchor premise this upper construction does not establish the same guard price.

## 6. Written weakening controls — UNEXECUTED

1. **Forget zero helpers in the lower bound.** A paid move can create a charge at an initially zero slot while moving it from another. Track every paid edge/label, including those helpers; only then do connected components conserve their initial sums and bound the operation count. A proof based only on the number of currently nonzero slots is insufficient.
2. **Lose the coupled inverse.** Update u by a row addition but leave W fixed. The displayed two-charge transfer and component conservation no longer hold. A charge can then disappear for reasons outside this header model.
3. **Permit arbitrary free GL.** A free general basis change can align a nonzero u with the last coordinate; W*u=0 then puts its last image column at zero and settles all charges for free. Restricting free headers to monomial matrices is essential to the h-Z price.
4. **Restrict the paid alphabet silently.** The attaining coefficient is -u_i/u_j. If a fixed language disallows that field element, or charges for its arithmetic/precision, h-Z is not automatically its operation price. The theorem uses all nonzero field coefficients at unit abstract cost.
5. **Confuse charge zero with donor component zero.** The collector's charge may cancel before all transfers, but u_j remains nonzero. Stopping on that charge, or dividing by a W component instead of u_j, can wrongly reject a legal attaining construction.
6. **Deduplicate labels or count the empty DP prefix.** Repeated equal nonzero charges are separate input slots (for example four identical charges over F2 can split into two opposite-in-characteristic-two pairs). Empty-prefix counting would shift D by one and falsely reduce the predicted paid price. Zero-prefix endpoints must reconstruct nonempty blocks covering all active labels.
7. **Replace full family by a subfamily.** Over F3, take m=3,u=(1,1,1), W=(1,-1,0), b=(0,0,1). The singleton lambda=0 passes every proper prefix at the identity although charges are not settled. The full affine family includes a member failing a prefix. Necessity of settlement is a quantified all-lambda statement, not a statement for arbitrary named guard subfamilies.
8. **Drop the scalar anchor.** Over F2, take m=4,u=(1,1,1,0), b=(1,1,1,0), W=(0,0,0,1). Then b*u=1, W*u=0 and all charges are zero, so settlement costs0. But scalar products b_i*u_i are three ones and one zero. Under any free monomial header they merely permute, so the first one occurs at a proper prefix and gives a failed minor. Thus the unanchored full-family guard price is not automatically h-Z. This is a changed-premise hand control, not a counterexample to the anchored source claim.

These are mathematical deductions, not executed tests, new source fields or observed source failures. No DP value, h/Z statistic, header census or physical cost was computed by a program.

## Credit and remaining source binding

The source6712 owns h-Z and its stated applications/certificates. Zero-sum partitioning, component bounds, row elimination and rank-one determinant arguments are classical principles; this review does not claim their invention. Prior common-image family/row-dependency work remains distinct. Substantial OpenAI Codex assistance produced this target-known note without a blind/human/kernel claim.

Post-seal review must bind the actual source definition of active charges, free/paid alphabet, anchor, DP and returned header convention to these hypotheses. The note supplies no arbitrary-subfamily/unanchored price theorem, physical coefficient/route/owner/tape/retained restoration invoice, selected assumption discharge, new count or kappa/frontier/adoption change.
