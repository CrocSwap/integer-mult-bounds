# Volume II self-review

Status: author review complete; independent peer review still required. This is an informal mathematical volume. No Lean proof generation, compilation, Jev, daemon action, or canonical source edit occurred.

## Inventory and scope

The draft has exactly B001–B100, in order:93 proved entries and7 explicitly conjectural entries. Every proved entry has an explicit statement, a proof, and a use/dependency paragraph. The main dependencies are finite-dimensional spectral decomposition, Gram–Schmidt, finite-field arithmetic and contraction mapping; none is an assumed MUB-existence oracle. The source ledger records bounded canonical-DAG FTS retrieval, exact local source hashes and qualified declarations. Retrieved source declarations are not fresh kernel/transitive-axiom evidence.

The volume reconstructs classical mathematics and derives local consequences; it claims neither100 new discoveries nor a general solution to a MUB problem. Its constructive chain includes finite-field spreads→actual Weyl operators→all prime-power complete MUBs, and independent defect/channel/border/exact-root sufficient criteria. Dimension six has a supplied three-basis construction only. All proposed stronger dimension-six statements remain conjectural.

## Mathematical checks and repairs

- B007/B068–B070 include characteristic two without inserting an invalid division by two. Only B062–B065 use the odd-characteristic Gauss substitution.
- B010 extends one isotropic subspace; it does not pretend to extend an arbitrary partial spread.
- B013 gives recovery with Fisher's rank bound; B015/B016 require actual net/Latin data and construct all vector coordinates.
- B023/B041 explicitly require N≥1; this removes the empty-family exception to the rank/equality comment.
- B031 now explicitly requires c>0, avoiding a degenerate zero-bound family being called a frame.
- B032 gives a finite compression/rotation induction rather than assuming the general Schur–Horn theorem. B033's common-norm completion uses both trace and rank conditions, which are sufficient by that argument.
- B037's row-budget proof uses the ≥2 condition precisely when borrowing from the next untouched row; the last remaining budget is integral by trace.
- B043/B044/B047 normalization constants were cross-checked by trace and by their scalar/traceless eigenvalues.
- B052/B053 exclude d=1, where repeated one-dimensional bases defeat the usual MUB count convention.
- B058 uses d−1 independent commuting Hermitian residual matrices; B060 uses d independent Hermitian channel generators plus unitality, fixed-generator and trace equations. No generator existence is assumed as an already solved construction.
- B060 specifies real linear independence and real Hermitian diagonal span; no ambiguity of scalar fields is needed for its proof.
- B072 explicitly needs positivity: diag(2/3,2/3,−1/3) records why trace and square-trace alone are insufficient.
- B078 now explicitly assumes N≥2; the order-one zero conference matrix would otherwise refute its evenness conclusion.
- B083 retains every cross-overlap hypothesis and preserves all old columns. B084 preserves the conjugation field. B097 now proves the stronger prime-root alphabet completion using a separate cyclic autocorrelation argument; the statement is not extended to composite alphabets.
- B090 requires invertible J and explicit polynomial identities expressing every omitted full geometric residual in the selected square system. It does not use a left inverse to infer an overdetermined system has a root.

## Conjecture checks and limitations

B091–B093 are classical research directions with primary-source precedents, not newly announced open problems. B095, B096, B099 and B100 are precise atlas proposals; their global literature status has not been established by this bounded search. B094 was replaced by a full Paley-construction proof to avoid duplicating the all-order Hadamard conjecture in Volume III. B097 was upgraded to a proved prime-phase completion: the p−1 root counts have cyclic autocorrelations forcing each count to be zero or one. B098 was replaced by a proved deficiency-one completion: counting holes in each hole-orthogonal hyperplane forces all holes to be pairwise orthogonal, hence a Lagrangian. These two arguments were developed during atlas review, with no global novelty claim. No failure of a restricted search is described as a proof of nonexistence.

B096 proves only its stated qualitative compactness evidence; its exponent is conjectural. B099 uses normalized Hilbert–Schmidt norm and allows all three matrices to move. The August2026 primary1/3 result adds a pinning condition; neither its constrained sharpness nor an operator-norm counterexample is falsely imported. B100 deliberately does not conjecture generic O(d²) design existence, which the current primary sources already address; it asks for the sharper unweighted distinct-ray cardinality≤d(d+1).

The source ledger clearly labels abstract/metadata literature checks. No full-paper validation or exhaustive current-literature scan is claimed. Exact local hashes bind inspected files, but their imported dependencies were not audited. The pure mathematics proofs in the draft stand independently of those Lean artifacts.

## Independent-review corrections incorporated

The peer reviewer requested an explicit finite-group hypothesis in B028 and a complex-linear extension step in B055. Both are present. The author also checked B094's quadratic-character correlation by counting factorizations of a nonzero square, B097 at p=2 as well as odd p, and B098 at n=1 and in characteristic two. These are mathematical checks only; no new formal verification is claimed.

Cross-volume review replaced B030’s overlapping rank-one inverse update with weighted minimum-noise reconstruction. Its exact covariance decomposition proves a constructive sufficient optimum, including correlated noise and uniqueness; it introduces no existence assumption beyond full row rank and positive definite covariance.
