# Fixed p16 FULL / QUERY domain: equations frozen before the screen

This is a source-bound, necessary-model screen. It changes at most two of the 33 existing stage modes. Pair locations, backward flags, all scalar bridges/exchanges, retained-idle mask and both scalar boundary matrices/programs remain frozen. A stage changes between its existing oriented FULL interface and that orientation's existing QUERY interface. It does not transpose a word, change native relations, or fuse queries.

On each of 112 independent port copies, with column vectors (X,Y), the literal maps are

- forward QUERY: `(X,Y) -> (X,Y+Q^-1 X)`;
- backward QUERY: `(X,Y) -> (X-Q Y,Y)`;
- FULL: apply that same shear, then multiply both components by the commuting stage factor `D_s`.

Thus FULL is `D_s I_2` times its oriented shear, not `D_s Q` or an unoriented letter. In particular Q^-1 is not identified with Q. A forward QUERY requires one owned copied stream, one paid rank-one Q^-1 request and charged add/erase/route. Backward changes sign and side exactly as above. Neither receives helper productive credit. Forward FULL uses the source forward word; backward FULL uses the physically checked #5383 backward word. Every FULL occurrence has a fresh independent helper bank. The owned field is separately returned and never credited.

Let S be the stages retaining FULL. Reconstruct the original p16 retained idle windows from the source keep-mask. For each such window with stage set J, apply `product_(s in J intersect S) D_s` to both fields. An empty product is the identity and costs no recursive job, while its scalar/routing treatment remains a separate finite cost. Removing/adding D_s at a local call also removes/adds that factor at every retained idle mentioning it. This includes the fifteen retained middle windows that are invisible identity events in the published thinned word and reappear if an even stage becomes FULL.

Let A_S(Q,D) be the exact chronological 32 by 32 Laurent matrix and let L,R be the frozen rational scalar boundaries. Only if `L A_S R` is diagonal, with each diagonal entry exactly one monomial of coefficient +1, central Q exponent in {-1,+1}, and each selected stage exponent in {0,1}, is the source rank normalization admitted. The main rank on that independent field is `1+8*sum(stage exponents)`, repeated 112 times. Squared factors, off-diagonal residues, sums, wrong central powers and signs are rejected, not silently normalized. D0 is the source nine-axis multiplier times Q^-1; the source +/-1 central normalization accounts for its overlap. Fresh stages s>0 are separate eight-axis blocks. Thus the formula is tied to this normalization and is not applied to arbitrary Laurent endpoints.

Given an admissible endpoint, define oriented source local histograms H_b,P_b,H_f,P_f from the independently derived invoice. The complete recursive histograms are

`T_S = main(endpoint) + n_b(S)*H_b + n_f(S)*H_f`,

`P_S = n_b(S)*P_b + n_f(S)*P_f + 112*(33-|S|)*H_1 + sum_(retained idle J, J intersect S nonempty)224*H_(8*|J intersect S|)`.

There is no per-letter reward for a non-diagonal endpoint, no retained helper from a removed FULL call, no credit for owned copies, and each main/helper is counted once. Summing r*T[r]-r*P[r] is an independent rank-mass check, not a substitute for the Laurent endpoint. At saving c the necessary favorable moment is `sum_r(T[r]-P[r])*r^(1-c)`. Scalar preparation, query COPY/CLEAR, movement, stocks, precision, completion and compiler reserves are not inserted as raw rank jobs; they can only reduce the funded region. This screen gives candidates zero additional nonrecursive penalty, so a failed moment is a favorable-cap exclusion. A passing moment does not establish funding.

The baseline is independently cold-admitted #5377 at .00302235. Competitive screens additionally use #5383's .00302666 and #5387's .003026674765, with their different admission statuses retained. This bounded domain is not a universal controller bound. Any surviving candidate would need actual changed calls, a literal physical endpoint, fresh ownership/ordinary/stock/precision closure and exact completion/compiler/outer tests before native synthesis or funding.
