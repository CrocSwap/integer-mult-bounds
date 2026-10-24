# Universal sufficient suffix-error bound

## Model and scope

Let V be a real or complex normed vector space, with its usual scalar absolute value. Represent each free warp generator by a linear isometry, and its inverse by its inverse isometry. The retained ideal program is linear: ADD, SCALE, CLEAR and COPY have their stated linear actions; warp changes the named register by its operator; chart transports are represented as logical identity maps with their retained tags. Arbitrary data and owned initial values are allowed. Physical adapter annotations are the exact ideal annotations of this model, not independently rounded arithmetic operations.

At a supported event e, permit an arbitrary additive defect η_e in that event's target register **after** its ideal action. Supported classes are scalar opcode, warp, and paid rank for climb/center. Defects may depend on the entire previous approximate trajectory; independence or random noise is not assumed. A claimed norm bound on each defect must be in these logical coordinates. No physical implementation contract is supplied by this definition.

## Theorem 1: exact suffix expansion

Let L_e be the ideal register map for event e and E_t the insertion into its target t. With the same initial state, the final error is exactly

Δ = Σ_e (L_N ··· L_(e+1)) E_t η_e.

Proof. At each event the approximate error satisfies d_e=L_e d_(e−1)+E_t η_e. Substitute repeatedly, starting from d_0=0. The formula is algebraic and remains valid for state-dependent η_e. If initial data also differ by d_0, add the term (L_N ··· L_1)d_0. ∎

Write the output-j response of the suffix to an injection in t as a reduced free-word sum Σ_w a_(j,e,w) W_w. Every word W_w is an isometry. Therefore

‖Δ_j‖ ≤ Σ_e Σ_w |a_(j,e,w)| ‖η_e‖.

Only adjacent inverse cancellation is used; unrelated warp symbols never commute.

## Theorem 2: exact reverse recurrence and sufficient class budgets

Maintain C_t, the column giving all final output responses to an injection at the current register t. Start with C_t equal to its output identity column. Immediately before reversing event e, C_t is its **post-event** injection response. Record its absolute coefficients by final output and event class, then reverse the ideal event:

- ADD t ← t + q s: C_s ← C_s + q C_t; C_t stays.
- SCALE t ← q t: C_t ← q C_t.
- CLEAR t ← 0: C_t ← 0.
- COPY t ← s, distinct roles: C_s ← C_s + C_t, then C_t ← 0.
- Warp t ← W t: right-compose every term in C_t by W. Free words append on the right and cancel at their last letter.
- Logical chart-only transport leaves these columns unchanged.

Proof. These are the columns of the suffix matrix multiplied on the right by the event's linear map. In particular warp composition is on the right, whereas forward signal propagation prepends on the left. Reverse induction gives every exact C_t and every recorded coefficient of Theorem 1. ∎

For event class c define B_(j,c)=Σ_(e in c) Σ_w |a_(j,e,w)|. If every class-c defect satisfies ‖η_e‖ ≤ d_c, then

max_j ‖Δ_j‖ ≤ max_j Σ_c B_(j,c) d_c.

This is a universal sufficient bound for every permitted defect trajectory. It is not a sharpness claim for simultaneous noise in a particular representation. The API requires all class budgets explicitly and rejects negative or omitted values. A class omitted from the physical model is an unclosed implementation obligation, not an implied zero budget.

The exact reverse endpoint check also shows that the full original and rewritten maps are the expected identity shear with all helpers restored and the owned initial C input erased. Their induced persistent-register maximum norm is at most 2. Thus initial persistent errors of norm at most E₀ contribute at most 2 E₀; initial owned-C differences contribute zero to the ideal endpoint. No additional private input or clean-entry assumption is used.

## Corollary 3: certified scalar defect tolerances

In the full source-bound computation, max_j(B_(j,ADD)+B_(j,SCALE)) equals 1,328 forward and 4,879 backward, for both original and rewritten words. Hence, when all other modeled classes are exact and each ADD/SCALE defect is at most δ, the persistent output error is at most 1,328δ or 4,879δ.

Since 1,328 < 2^11 and 4,879 < 2^13, entire-field absolute logical defect tolerances δ ≤ 2^−(b+11) and δ ≤ 2^−(b+13), respectively, suffice for output error ≤ 2^−b. If initial persistent input error is also ≤ δ, replace the constants by 1,330 and 4,881; the same extra-bit allowances suffice. These are logical defect tolerances, not machine mantissa widths or a claim about dimension-dependent rounding. ∎

The row-specific coefficients can increase while the worst coefficient is unchanged. The rewritten ledger has maximal row increases 2 forward and 12 backward. It does not establish coordinatewise domination or unchanged bounds under every unequal defect budget. The explicit weighted evaluator must be used for such budgets.

## Theorem 4: sufficient feedback closure from supplied recursive contracts

Suppose the actual implementation supplies, for every supported class c, a post-event defect bound

‖η_e‖ ≤ u (α_c B + β_c E),

where u, α_c, β_c, B are nonnegative and E is the maximum final persistent error. Start from exact persistent inputs. Set A=max_j Σ_c B_(j,c) α_c and D=max_j Σ_c B_(j,c) β_c. If uD < 1, then

E ≤ u A B / (1 − uD).

In particular uD ≤ 1/2 implies E ≤ 2uAB.

Proof. Theorem 2 gives E ≤ uAB+uDE. Rearrange (1−uD)E ≤ uAB and divide by the positive denominator. Under uD ≤ 1/2, its inverse is at most 2. This matches the feedback-absorption pattern of MathProof's IntegerKappaBorrowFeedback20261014.lean, without asserting that a new physical implementation satisfies its premises. ∎

This is a sufficient assembly theorem, not a list of necessary conditions. The remaining work is to prove the concrete physical/recursive defect contracts in the chosen norm and discharge any missing annotation errors. No bound on u, α or β for the actual all-size recursion is invented here, and no new κ is derived.

## Finite certificate and controls

Every source byte is pinned; the rewritten word is regenerated from the exact #4505 patch rules, whose local maps and field inventory are checked. Complete reverse endpoints cover all 633 independent variables. Eight whole-word suffix impulses and 720 all-event impulses on small noncommuting programs agree with an independent forward oracle using the retained source helper functions. Whole-word class ledgers and maxima are computed in exact rational arithmetic and committed for replay. The finite computations specialize the universal algebra above; they are not Lean kernel certificates or an independent human review.
