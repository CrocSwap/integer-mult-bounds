# A complete finite curvature calculus for profile comparison

This is an elementary discrete-concavity theorem, proved here for the supplier interface. We do not claim it was unknown in mathematics. Its useful application is a proof certificate for an entire continuum of recurrence exponents and for every compatible future controller, rather than a floating-point price at one chosen exponent.

## Theorem (curvature cone and constructive completeness)

Let H and H' be finite nonnegative rank histograms supported on the integers 1,...,R. Set delta_r=H'_r-H_r. Assume both child count and rank mass agree:

    sum delta_r=0,   sum r delta_r=0.

For j=1,...,R put C_j=sum_{r<j}(j-r)delta_r. Then C_1=C_R=0, and with exterior C_0=C_(R+1)=0 we have

    delta_r = C_(r-1) - 2 C_r + C_(r+1).

The following are equivalent:

(A) every C_j is nonnegative;
(B) sum H'_r f(r) <= sum H_r f(r) for every discrete concave f on 1,...,R.

Moreover the difference is exactly

    sum delta_r f(r) = sum_{j=2}^{R-1} C_j [f(j-1)-2f(j)+f(j+1)].

If any C_j>0 and f is strictly concave at that index, the inequality is strict. This is a sufficient, explicitly computable criterion. It does not require knowing the eventual exponent or querying an optimization oracle.

Proof. Difference the defining prefix sums twice to get the reconstruction formula. The mass and count identities give C_R=0 and the two right boundary identities. Substitute that second-difference expression into sum delta_r f(r), shift the finite summation indices, and cancel the zero boundary terms. Concavity proves A implies B. Conversely, fix an interior j and choose the concave function f_j(r)=-max(j-r,0). Its second difference is -1 at j and zero elsewhere. The displayed identity gives sum delta_r f_j(r)=-C_j. Property B therefore implies C_j>=0 for every j. All identities are finite exact rational arithmetic. QED.

## Algebra of certificates

Histograms compose by disjoint union. Thus a nonnegative integer sum of certified deltas has certificate equal to that same sum of their C vectors. If H0->H1 and H1->H2 are certified, H0->H2 is certified by C01+C12. A width-preserving provider substitution in N complete compatible contexts multiplies C by N. This gives a cone closed under program composition and substitution. It turns an optimizer's proposal into a short independently checkable quantitative proof.

The theorem compares costs; it does not manufacture a legal word. The trace-refinement constructor and physical checks separately prove realizability. In particular C>=0 alone cannot replace a source-word, memory, ownership or scalar-prefix audit.

## Strict improvement for the published recurrence interface

Fix the same W,m and child count for both suppliers, with every used rank smaller than m. For 0<a<1 let f(r)=r^a. Its discrete second difference is strictly negative. The curvature certificate therefore proves a strict reduction of sum H_r(r/m)^a/W whenever C is nonzero. The published bad-class envelope is proportional to child count, so its contribution is unchanged. The entire fallback-augmented moment, not only its main term, strictly decreases.

Writing a=1-b, each positive-rank term is strictly increasing in b because r/m<1. Hence, whenever both moments have their specified positive crossing of one, the new root is strictly larger. The actual rational bound is still computed by the two pinned interval engines. This order statement is independent of the decimal grid and bootstrap tuning.

## Concrete application to preload60

The actual new scalar word has local delta=60(e1-2e2+e3), including the unchanged nine rank8 copy children in both profiles. Its unique certificate is C2=60 and all other C_j=0. At 9 stages and32 replicas, the owner-checked global delta is17280(e1-2e2+e3), so C2=17280. We check this reconstruction against both actual full profiles, including idle remainders.

The new endpoint has the same480 width8 residuals,30720 live registers,9984 deficit and child count as PR510. Rank distribution changes even though rank mass and deficit do not. Thus deficit-only comparison misses the improvement, whereas the curvature certificate detects it for every0<a<1.

## Source relationship and scope

The quantitative Jensen-gap viewpoint in the source-read OpenAI OAI/InformationTheory/SoftChannel/JensenGaps.lean informed retaining an exact signed gap instead of entropy approximations. The proof above is independent and finite; no Lean import, kernel certificate, global originality claim or unconditional multiplication theorem is asserted. The source hash and declarations are in CONTEXT-SOURCES.json.
