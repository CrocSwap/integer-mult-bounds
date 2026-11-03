# Scope and composition proof

Let W be the pinned PR6030 event list. The prefix interval is [1,9896), at frame 3. The suffix interval is [17461,20431), at frame 127. These are zero-based, half-open intervals in W, before either replacement. Each interval contains only ADD and SCALE.

For each interval, the checker forms the union of all touched roles. It starts with a full identity matrix on those roles. It executes the original and replacement lists with dense integer rows and one binary denominator per row. Exact normalization makes their matrix equality decisive. Roles outside that union are fixed. Therefore each replacement gives the same map for every possible entry vector; no entry is assumed zero. The prefix check includes owned role 778.

The intervals are disjoint. Replace them in reverse order so their original indices stay valid. The first equality preserves the state at the first exit and every later protected event. The second equality has the same property at its exit. Their composition therefore preserves all protected observations and the endpoint. This argument holds for Hilbert-valued entries in a common scalar chart. It retains the source native chart-change premise; it does not prove a new native operator.

The independent whole-word checker verifies chronological charts, legal owned lifetimes, all endpoint rows and every paid and productive rank. A separate reverse-chronological dense integer calculation checks all 799 columns. Scalar allowances are recomputed from the literal coefficients, with COPY and owned initialization and erasure charged. No scalar operation is omitted from the comparison.

# Precision qualification

Assume each initial public vector has norm at most B. MOVE has a local defect at most u times its actual input norm. ADD has a defect at most u times the sum of its actual destination norm and the absolute coefficient times its source norm. SCALE has a defect at most u times the absolute coefficient times its input norm. COPY, INIT and CLEAR are exact. Native chart changes are unitary. Set u=2^-g.

The pinned ideal checker computes each exact ideal row and its l1 norm. For each defect site, the causal checker adds its ideal local allowance to the current signed error-row norm, with the same source and destination weights as the operation. It multiplies this nonnegative bound by u and rounds up on the 96-bit grid. Linear coefficient rows remain exact, so cancellation of earlier defects is retained. The triangle inequality and induction give the reported bound for every permitted defect sequence. The receipt checks the entire final vector and the largest prefix score.

All four words pass g=16 and fail g=15 in this sufficient model. The joined word has a smaller final bound than the prefix-only word. The ideal norm is at most 850 B; with the reported error, ten range bits suffice. Raising every guard by t makes each causal defect bound at most 2^-t times its g=16 upper bound: apply induction to the ideal term and prior nonnegative defect magnitudes. The original upward-rounded certificate remains an upper bound after this scaling. Thus the final public error is less than B times 2^-t.

This is a sufficient precision construction. A failed guard, a smaller operation count or a fixed-grid bound is not a lower bound on the precision of an actual backend. A physical implementation and its complete cost are not supplied.
