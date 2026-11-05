# Cross-review of the common-image count law

**Verdict: PASS for the count-law scope.** The actual source's initial count-law sections match the proposition supplied before my derivation, and the sealed source-proof-unexposed derivation establishes that same law. No gauge, flag, rank-inversion or domain mismatch was found. This is written review of an existing SHIN09-git result, not a new law or an executed count.

Post-seal reads: the actual package `inputs/PROOF.md`, peer `LAW-ADVERSARIAL-DRAFT.md`, and `COORDINATOR-PRE-SOURCE-SKETCH.md`. The source read returned later pencil/sign/flat/determinant text as well; it was visible after sealing, but those claims were not reviewed or accepted here. No source/code program, import, compilation, kernel, census or numerical experiment was executed. No sealed file, input or package file was edited.

My original derivation remains `4e58b7a075a6580a3d009276816bb6d80e705d06e78a9953f2af9451149900ef`; the peer and coordinator hashes are verified below by metadata-only hashing. The distinction between target-known derivation and source-proof-unexposed derivation remains essential: I knew the claimed formula and prior6701/6703/4807 methods before deriving it.

## Agreement with the actual source and adversarial note

The actual law permits a nonempty row list, repetitions, dependencies and k>m; its true rank is r=dim(im(V)), not k. It fixes the embedded image S in K^k and endpoint t, counts normalized vector tuples, and divides the exact passing-tuple count by D_r. These are exactly the hypotheses and objects used in my sealed proof. Every row remains normalized by v_i*u=1, so the full-support transformation cannot be applied to a space omitting t.

The source's words about a fixed initial vector representative do not mean that the transformed u' is held fixed in the orbit denominator: u'=G*u ranges over all q^m-1 nonzero vectors. Its fixed-vector stabilizer does not acquire a q-1 factor. If one instead quotients by common-image-line representatives, both the passing and total tuple counts are divided by q-1. The peer states this explicitly and consistently with the source. The terminal q-1 comes from actual nonzero last-coordinate choices, a separate operation.

The source and peer correctly use the auxiliary basis sending a fixed u' last **only to count the unrestricted denominator**. It cannot simplify the passing predicate in the original coordinate flag. The chronological numerator uses every actual proper prefix. In particular u'_m=0 would force the final proper prefix to equal t and fail, while free columns at earlier zero u'_a remain necessary for exact rank. These two different zero-coordinate cases are not conflated.

The numerator retains h(L) as a coordinate full-support count in the actual embedded L. A basis of S chosen to prove transitivity does not turn that number into a function of dimension alone. The peer's concern and hand control are warranted. Rank enters only after the contained-image count is split according to its unique exact image. Restricting the bottom to<t> leaves the interval[L,S] unchanged, so the exponent c=r-dim(L), including the q factor at codimension2, is correct.

The Gaussian-binomial product identity in the actual source is the same interval zero-sum identity established in my derivation. Repeated rows and k>m change the coordinate embedding/support geometry, but do not invalidate orbit transitivity or inversion. At r=1 the product is empty; at r=m the kernel block is empty and the product is still positive. No hidden independent-row, distinct-row or odd-characteristic hypothesis has been introduced.

The peer's written controls are consistent with the law. They are not observed mutant outcomes. They distinguish fixed-vector versus line normalization, counting-basis versus actual-flag use, the last proper prefix, free zero-coefficient columns, contained versus exact image and the non-Boolean Möbius coefficient. No actual counterexample to the stated source law results from those altered claims.

## Coordinator's independent-row specialization

For full row rank k, S=K^k. With the standard nondegenerate coordinate pairing, the map U->U^perp reverses inclusion and bijects subspaces U<=t^perp with subspaces L>=<t>. Its dimensions satisfy dim(L)=k-dim(U). Thus the sketch's coefficient

    (-1)^dim(U) q^[dim(U)(dim(U)-1)/2]

is precisely mu(L,S). Its A(L) is the same h(L), not a second invariant. The relation-space formulation and the source's image-space formulation are therefore the same inversion in opposite coordinates.

The sketch uses x=H^-1*u and Y=V*H. Setting G=H^-1 gives exactly the source action x=G*u, Y=V*G^-1. Inversion permutes complete uniform GL_m, so their measures agree. This is a change of the uniformly chosen header variable, not an arbitrary flag-preserving basis change and not a claim for restricted measures.

Its support-first aggregation is consistent with the transfer derivation: for s nonzero coordinates of x with x_m!=0, there are m-s proper zero coordinates with q^dim(L) free column choices, and s-1 proper nonzero coordinates with h(L) next-safe-prefix choices. There are binom(m-1,s-1)(q-1)^s such vectors. Summing gives (q-1)lambda(L)^(m-1), with no extra initial or terminal h factor. Its denominator is the same D_r at r=k. The exploratory note clearly records prior duplicate discovery and does not relabel this as a new source theorem.

## Hand fixture q=3,m=3,k=3 — not an execution

Here S=F_3^3, t=(1,1,1), and r=3. Full support in S gives h(S)=2^3=8, so lambda(S)=27+2*8=43. There are four planes through<t>, corresponding to the four lines in the two-dimensional quotient.

Three planes impose one specified coordinate equality. In each, the repeated coordinate value and the remaining coordinate value have two independent nonzero choices, giving h=4 and lambda=9+2*4=17. The remaining plane is x1+x2+x3=0. Among triples of nonzero elements of F3, only the all-one and all-minus-one vectors have zero sum, so its h is2 and its lambda is13. Finally the line<t> has h=2 and lambda=3+2*2=7. Its codimension-two Möbius coefficient is3; each plane's coefficient is-1.

Thus the stated hand numerator is

    2*(43^2-3*17^2-13^2+3*7^2)
      = 2*(1849-867-169+147) = 1920.

The normalized-vector orbit has r=m, hence fiber one, and

    D_3=|GL_3(F3)|=(27-1)(27-3)(27-9)=11232.

Dividing both integers by96 gives20/117. This verifies the coordinator's hand calibration under the proved general law, without obtaining a new observed census or recomputing a source receipt.

If all four planes were incorrectly assigned h=4 merely from their common dimension, the corresponding numerator would be

    2*(43^2-4*17^2+3*7^2)=1680,

which is different. The example therefore concretely discriminates an invalid dimension-only collapse. It is not a counterexample to the actual source, which retains the true support geometry.

## Remaining scope and attribution

No count-law correction is requested. Preserve in publication: the source theorem belongs to SHIN09-git6710; the coordinator's earlier potential-new-theorem proposal was withdrawn as duplicate; my target formula was known before derivation; actual source-proof/peer exposure happened only after sealing; and all present checks were written/static or provenance-only.

Pencil/triple signs, full-flat formulas, asymptotics, fixed-determinant strata, source census/control receipts, implementation correctness and physical/native/caller costs are outside this cross-review. Nick Petalas and6701/6703 retain their predecessor scopes; classical rank-one determinant, orbit-stabilizer, rank and Möbius methods retain their credit. No selected-framework admission, new kappa or frontier change is inferred.
