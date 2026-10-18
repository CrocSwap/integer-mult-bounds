# PR803 source and analytic proof audit

This continues the [review comment](https://github.com/CrocSwap/integer-mult-bounds/pull/803#issuecomment-6160966501)
on source head `d213ac12d4a1ab8f717d942e844df318ceb395fb`.
It addresses the analytic proof of

\[
 \|1/P\|_W\le (1+4m)(1+4n)/\delta\le(1+4n)^2/\delta,
\]

for every nonzero degree-n complex polynomial with |P|>=delta>0 on
the entire unit circle; m counts interior roots with multiplicity.
The conclusion of this author/AI audit is that the stated proof chain
supports the bound. The revision makes the source normalization and
previously compressed implications explicit. It changes neither the
bound nor the admissible operators, and does not claim independent
human review, formal verification, or maintainer acceptance.

## Sources actually checked

| Source and locator | What was checked | Role and limit |
| --- | --- | --- |
| [Baranov-Zarouf, arXiv:1310.1182v1](https://arxiv.org/pdf/1310.1182v1), Section 1.1, p. 1; Section 1.2.2, p. 3, (1.3) | Rational degree is the maximum of numerator and denominator degrees; poles on the circle are excluded; Lebesgue measure is normalized. Their derivative L1 bound is degree times the circle supremum. | Matches `PROOF.md` (5), including poles inside the disk. Also supplies historical attribution to Dolzhenko. Dolzhenko's original article was not independently inspected. |
| [Spijker, BIT 31 (1991), 551-555](https://www.researchgate.net/publication/227228151_On_a_conjecture_by_LeVeque_and_Trefethen_related_to_the_Kreiss_matrix_theorem), author-uploaded original full text, p. 552 (4), pp. 552-554 Lemma 2 | The original inequality uses unnormalized arc length with factor 2 pi times degree. Lemma 2 establishes constant gamma=1 by projection and a degree-2n level polynomial. | Dividing by 2 pi gives (5). The local projection derivation follows this classical proof; it is not a new proof method. DOI: [10.1007/BF01933268](https://doi.org/10.1007/BF01933268). |
| [Kanjin-Sato, Mathematical Inequalities & Applications 7 (2004), 551-555](https://files.ele-math.com/articles/mia-07-56.pdf), opening of p. 551 | The classical Hardy coefficient inequality is stated with an unspecified constant and an unnormalized H1 integral. | Background attribution only. It does not supply the normalized constant four used here. That constant is derived in `PROOF.md` Section 1. |
| [Ali Romman's PR621](https://github.com/CrocSwap/integer-mult-bounds/pull/621), head `520774462b19b29af41554b74def31f9d01e997e`; local `vendor/prime-power-proof.md` | The declared kernel, n=r-1, D=phi(r), H=2^r-1, delta=(2rn H^(nD-1))^-1, and original norm expression agree with the application. | Only source identity and the specialization interface are covered here. Its nonvanishing/resultant theorem remains the inherited foundation; no new foundation replay or full re-audit is claimed. |

These readings were made on 2026-10-14 UTC (2026-10-13 in the contributor's
America/Mexico_City timezone). Papers are cited, not redistributed. The
Leiden-hosted Spijker PDF returned HTTP 404; the inspected original text
is the author-uploaded version linked above. Exact local source SHA-256
and Git-blob pins remain in `SOURCES.json`; none of its six immutable
source/context files changed.

## Analytic implication audit

Read the revised [PROOF.md](../PROOF.md) in the following order. Each row
is a mathematical argument, not an inference from a finite verifier.

| Step | Analytic obligation and resolution |
| --- | --- |
| Section 1, (3)-(4) | The explicit positive second derivative proves the midpoint bound, including its integrable endpoint at zero. The weighted Cauchy-Schwarz argument is first applied to finite truncations, with a uniform bound four. Multiplicity-matched Blaschke removal gives a zero-free analytic quotient on a slightly larger disk, where an analytic logarithm supplies its square root. Parseval then bounds the coefficient convolution. The proof takes finite truncations before the monotone limit; boundary zeros are handled by radial dilation avoiding the finitely many zero radii and uniform convergence. |
| Section 2, (5)-(5a) | The padded reciprocal polynomials give the exact level equation of degree at most 2d without losing conjugation or requiring equal numerator/denominator degrees. A constant projection contributes zero variation. Otherwise the level polynomial cannot be identically zero, and a real analytic projection has finitely many critical points per period. The monotone-interval count holds off finitely many critical/endpoint levels. Integration over projection angles and division by 8 pi yield the normalized derivative bound. |
| Section 3, (6) | The coefficient identity for R' cancels the weight in (3). The degree used in (5) is that of R, not R'. Cauchy's constant-coefficient estimate supplies the remaining term. Both R and R' are analytic on a neighborhood of the closed disk; this lemma is not applied directly to 1/P with interior poles. |
| Section 4, (7) | Reflection gives the rational identity P=JQ. The roots of J's numerator are inside and its denominator roots outside, so no cancellation invalidates degree m. Zero roots contribute z to J and 1 to Q. Repetition changes multiplicity but not the argument. The two analytic factors have l1 coefficients; their absolutely convergent double series identifies both Fourier directions of 1/P and bounds their sum by the product of the two norms. No root-distance estimate is introduced. |
| Section 5 | Completeness of the bounded-operator algebra and the bound on every signed power give an absolutely convergent series S. The finite polynomial identity yields coefficient-wise convolution with the unit sequence. Absolute convergence permits regrouping the operator series, producing both P(U)S=I and SP(U)=I. Thus invertibility of P(U) is proved, not assumed from its spectrum. |
| Section 5, application | A unit-modulus monomial matrix and its inverse are infinity-norm isometries; length, stride and repeated eigenvalues introduce no extra factor. Merely having unit-circle spectrum is insufficient, as the displayed 2-by-2 Jordan example shows. The inherited norm constant rewrites exactly as A(1+4X^2). The strict comparison uses n,D>=2 and H^(nD/2)>=H^2>4n+2. |
| Section 6 | P_epsilon(z)=z-(1+epsilon) has circle minimum epsilon and inverse norm epsilon^-1 at U=I. Multiplying by z^(n-1) preserves both facts for any fixed n>=1. This proves necessity of the inverse-gap exponent, not optimality of the degree factor. |

The remaining basic tools are the fundamental theorem of algebra,
removable singularities, analytic logarithms on simply connected zero-free
domains, Parseval/Cauchy coefficient formulas, polynomial root counting,
and absolute/monotone convergence. No root separation, finite sample
coverage, diagonalization, or unproved numerical limit is a premise.

## Attribution correction and overlap

[PR692](https://github.com/CrocSwap/integer-mult-bounds/pull/692), head
`c5b53a5e80372a1fae9830d8dcf21aaabce3f729`, identifies **Ryan Pinto
(@Ambassators)** as its contributor. The previous PR803 prose incorrectly
credited Joshua Snider / jsnider3 for that PR. `README.md`, `NOTICE.md` and
`SOURCES.json` now carry the verified credit. No PR692 code is consumed.

[William Lawyer's PR852](https://github.com/CrocSwap/integer-mult-bounds/pull/852),
head `aa26b2ad761aa3bac76670e4749f53d2dafb3fea`, treats PR803's analytic
bound as an explicit inherited premise. Its weighted-cycle power results
therefore do not independently certify this proof. Its scope differs
from this assigned continuation. The overlap helper's cached PR and
discussion coverage, freshness limits, and the live head checks are
recorded in `TASK.json`; no novelty claim follows from that search.

## Retained evidence and revision checks

The [batch disposition](https://github.com/CrocSwap/integer-mult-bounds/blob/main/research/community-efficient100-audit/DISPOSITIONS.json)
marks PR803 partially reviewed. Its [source packet](https://github.com/CrocSwap/integer-mult-bounds/blob/main/research/community-efficient100-audit/packets/803.json)
records 20 added paths and an empty `checks` list; it does not claim an
independent maintainer replay of this package. The contributor's earlier
finite evidence remains in `../evidence/` and `../EXPECTED.json` unchanged.

The new evidence is the source comparison and expanded analytic reasoning.
The existing verifier and eight package controls are rerun only to check
the revised package and regenerated manifest, with results in
[VALIDATION.json](VALIDATION.json). No new finite domains or tests are added,
and these regression checks do not certify an analytic theorem. The
original `CLAIM.json`, all vendored files, both executable scripts, and
the earlier test receipts are preserved byte for byte at the reviewed head.

## Open next questions

1. **Independent acceptance of this proof.** A reviewer can start with the
   implication table above and verify (3)-(7) in the revised proof, especially
   the padded level polynomial and the two absolute-convergence arguments.
   No independent human review or proof-assistant certificate is supplied.
2. **A paid rounded implementation.** Pick a specific precision recurrence
   and prove its preparation, propagation, restoration and routing obligations
   using the new bound. The all-length exact-operator estimate alone does not
   pay for that implementation or change the selected multiplication exponent.

Prepared for Rafael Guevara (@alephnan) with substantial OpenAI Codex
assistance in source checking, mathematical review and writing. No sub-agents
were used. This is a contribution-side audit, not a maintainer disposition.
