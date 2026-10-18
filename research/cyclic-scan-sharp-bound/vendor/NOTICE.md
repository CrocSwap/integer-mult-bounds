# Attribution and scope

Ali Romman's PR621, exact head 520774462b19b29af41554b74def31f9d01e997e,
supplies the prime-power kernel circle bound. Its kernel attribution is
OpenAI's exact-DFT preprint at adc7f1241b42e322a6451854ab7e4b4c146bf78a
(`loc:newton`, `loc:fourier-factorization`) and classical q-Pochhammer/Newton
factorization, including Alexey Kuznetsov's cited q-calculus work. This
package does not claim to originate those constructions.

Pan's approximate-factorization theorem is used in the form stated by
Mehlhorn, Sagraloff and Wang; Brent's work supplies fast elementary-function
evaluation. Causal/anticausal recursive filtering is standard, as illustrated
by the Briand-Davy source listed in SOURCE.json. Sources are cited for these
specific tools, not as proofs of this package's complete claim.

The scan rounding analysis, explicit budget composition, interval and
factor certificates, routed reference execution, and packaging were
prepared with substantial OpenAI Codex assistance for chafreaky. The dense
matrix solver and algebraic coefficient crosschecks provide independent
computational paths, not human peer review or formal Lean verification.

No new multiplication exponent, literature priority, maintainer acceptance,
physical tape execution, or production performance result is claimed.
The code and documents use the repository's Apache-2.0 license.
