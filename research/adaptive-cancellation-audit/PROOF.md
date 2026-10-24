# Sharp cancellation audit and exact extremisers

This is a scoped independent written proof audit of PR4483, PROOF.md Section 4, equations (10) and (11). It is not a formal-kernel proof. The algebraic optimisation below is elementary and carries no priority claim. Its value is the precise source-bound sharpness statement, zero-mass handling and discriminating controls for the adaptive compiler.

## Statement

Fix real numbers 0 <= beta < eta < 1. Let I,B,F,A be nonnegative and satisfy I=B+F+A and B<=beta I. These are respectively the inner-source, boundary-exit, leaf-exit and net-production potentials of the source argument. For fixed A,F with A+F>0, the largest permitted value of (B+F)/I is

    (beta A + F)/(A+F).

It is attained at I=(A+F)/(1-beta), B=beta I. Consequently the condition

    (eta-beta) A >= (1-eta) F

is sufficient, and is necessary for a uniform guarantee over every admissible boundary mass at those fixed A,F. This is not claimed necessary for each individual flow, whose mirror slack can make its exit fraction smaller.

## Independent slack certificate

Using I=B+F+A gives the exact identity

    (1-beta) [eta I-(B+F)]
      = (eta-beta) A-(1-eta) F + (1-eta) [beta I-B].

Under the displayed threshold and mirror inequality the right side is nonnegative. Since 1-beta>0, the desired contraction B+F<=eta I follows. This proves the implication without division by a possibly zero leaf mass or inner potential. If A=F=0, then I=B and B<=beta I force I=B=0, so the conclusion still holds.

For sharpness, with A+F>0 the constraint is (1-beta)B<=beta(A+F). The fraction (B+F)/(B+A+F) is nondecreasing in B, with derivative A/(B+A+F)^2. The endpoint above is therefore a maximiser, also when A=0. Substitution yields the claimed maximum and the exact threshold. Equality occurs when the threshold is tight and the mirror is saturated. Strict contraction follows if at least one of the two nonnegative terms in the slack identity is positive.

## Binding to PR4483

The source defines A=(T_t-P_t)H_t-R_t. Its exact potential cancellation is I+R=B+F+(T-P)H, hence the premise I=B+F+A. Source equations (3) and (9) bound F<=P_t^(G+1) and A>=D_ell(t) P_t^(G+1). Since eta>beta and eta<1, the source threshold

    (eta-beta)D_ell(t) >= 1-eta

implies the inequality above. In particular it forces D_ell>=0. The signs and the subtraction of root potential are load-bearing. The proof does not require the old invalid assertion that leaf ranks are uniformly sublinear.

No better universal threshold can be inferred from only these inequalities. Actual flow correlations or a strictly better mirror or leaf bound can still improve the conclusion. The statement is a ceiling on this scalar inference, not on the compiler family, native word, rank bound or multiplication exponent.

## Failure controls

Take beta=1/4, eta=1/2, F=1, gross production (T-P)H=2 and root debit R=1/2. Then A=3/2, I=10/3 and B=5/6 satisfy exact cancellation and saturate the mirror. The actual exit fraction is 11/20>1/2. Ignoring R falsely passes the gross threshold with equality. Thus the root term cannot be discarded. Similarly A=0,F=1 gives exit fraction 1, while a test that drops the leaf mass would accept A>=0. Both are counterexamples to weakened tests, not to PR4483, whose correct guards reject them.

The checker uses exact Fractions for 6,120 cases, 1,800 attained extremisers, 120 zero-mass endpoints and four invalid-premise controls, plus both omission examples and nine linear coefficient checks. Finite cases corroborate implementation and failure boundaries; the all-real proof is the identity and extremal argument above. No predecessor acceptance function is imported.

## Remaining obligations

The Chernoff bounds producing D, the pointwise mirror certificate, funded logarithmic majorant, integer chronological realisation, native adapters, physical tape costs, precision/stock and outer transfer are not proved by this lemma. The newer PR4529 gate checks and PR4532/4533 work are complementary, not evidence that this package audits the entire compiler. Exact source bytes are checked by the Git blob pin in verify.py and declared as a live replay input.

Credit zxv for PR4483 and the sharp cancellation already used there, Jacob Alan Sussman's compiler, Ryanson Jonathan's corrected mirror and gate work, Dillon's broader gate-existence analysis, and the retained native/outer contributors. Prepared for Chris R / Clear1nsight with substantial OpenAI assistance; Apache-2.0.
