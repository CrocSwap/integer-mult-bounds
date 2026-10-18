# Attribution

Prepared for **Rafael Guevara (@alephnan)** with substantial **OpenAI Codex
assistance** in choosing the approach, mathematical derivation, source
research, implementation, verification, and writing. No sub-agents were
used. No independent human review or proof-assistant formalization is claimed.

**Ali Romman**, incorporated PR621, supplies the prime-power polynomial,
all-embedding nonvanishing argument, quantitative resultant/cofactor circle
bound, and cyclic-operator setting. Its proof and original attribution
notice are preserved byte for byte under `vendor/`. This package relies
on that circle theorem rather than reproducing its foundation arithmetic.

Our prior unpublished weighted-Fourier audit (local commit
`4c0004759b0ac8e2db1a1afd9fff690270786dfe`) is a comparison baseline. Its
proof and notice are retained unchanged. Its analytic bound is superseded
here for the admitted prime-power family; the prior result remains valid.

Root reflection using finite Blaschke products and Hardy's coefficient
inequality are classical. The rational arc-length inequality is credited
to **E. P. Dolzhenko** and **M. N. Spijker**, following the historical
discussion in **Anton Baranov and Rachid Zarouf**, arXiv:1310.1182v1,
Section 1.2.2. That paper was inspected for the normalized statement and
attribution. **Yuichi Kanjin and Kunio Sato**, "Hardy's inequality for
Jacobi expansions" (2004), opening page, also records the classical Hardy
coefficient inequality. Neither paper is redistributed. The elementary
proofs and nonoptimal constant four are written out for review here.
No novelty claim is made for those classical tools or their general
combination in rational function theory.

The finite-geometric inverse is standard. **Joshua Snider / jsnider3**,
PR692, already uses it for weighted-stride closure and bilinear-dual
verification. Our small Gaussian-rational implementation is newly written;
no PR692 code is consumed. **Chafik Boukhalfa / chafreaky**, PR628, and
**Charles Bethin / cbethin**, PR764, supply distinct rounded-scan results.
**Jason Willems / at1as**, PR666, supplies composite lifting and finite
certificates. Their results do not become discharged implementation
obligations of this analytic note. PR736's elimination optimization is
also distinct.

The underlying kernel and OpenAI exact-DFT preprint provenance remain
as recorded in the preserved PR621 notice. The selected-result snapshot
retains the #626/#543 contributor lineage. It is historical context, not
evidence of a new exponent.

New text and code are Apache-2.0. The unchanged upstream license is included.
