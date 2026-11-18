# Credit and source roles

Ali Romman supplied the source-specific general factorization proof, exact
Hurwitz row reducer, inverse and denominator certificates, and separate
rational block-rank checks, with substantial OpenAI Codex assistance in
research, implementation, verification and writing. Apache-2.0.

Nick Petalas supplied the integral channel-gap response, proof, verifier and
explicit general dyadic-factorization handoff in
[PR #7745](https://github.com/CrocSwap/integer-mult-bounds/pull/7745), head
`b92ecb5f9579215dda5832fe604f4124b0198cde`. Its
[proof and next question](https://github.com/petalas/integer-mult-bounds/blob/b92ecb5f9579215dda5832fe604f4124b0198cde/research/lipschitz-channel-gap/README.md)
and all five package files are retained unchanged. The original basis,
parity and norm-two-divisor checks run unchanged. The separate certificate
checker also calls the retained multiplication formula. His source credits
Machiavelo and Roçadas for the classical nonassociate norm-two example;
that predecessor credit remains in the retained source.

Dugongue supplied the odd-response factorization interface, split dyadic
comparison and nonsplit question RQ10 in
[PR #5803](https://github.com/CrocSwap/integer-mult-bounds/pull/5803), head
`0acda5ab421d28b98fdf916968696c8f9453376f`. The complete
[algebra volume](https://github.com/CrocSwap/integer-mult-bounds/blob/0acda5ab421d28b98fdf916968696c8f9453376f/research/frontier-mathematical-atlas/volume-algebra.md)
is retained byte for byte, including its attribution and physical limits.
R03-R07 and RQ10 are the relevant sections. We do not claim to review the
whole atlas or to supply its missing physical caller.

The Hurwitz order, its half-integer lattice, Euclidean division and elementary
row reduction are classical. John Voight's
[The Hurwitz order](https://link.springer.com/chapter/10.1007/978-3-030-56694-4_11),
chapter 11 of *Quaternion Algebras* (2021), gives the order in section 11.1
and left/right norm-Euclidean division in section 11.3, Lemma 11.3.2.
Paragraph 11.3.1 and Exercise 11.7 state the one-half squared covering bound.
The proof here derives that bound and the left-operation convention directly.
No global novelty is claimed for this classical algebra or its usual rank
factorization consequence. The contribution answers the repository's exact
open coefficient question and supplies a reproducible attaining algorithm.

The external chapter is a mathematical reference, not executable input.
All six retained repository files have Git-blob and SHA-256 pins. The base
manifest records provenance only; no unmerged dependency ancestry is asserted.
Separate computational paths are not independent human or formal-kernel
acceptance. All source-specific notices and licenses remain in force.
