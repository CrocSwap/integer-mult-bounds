# Batched-recursion review guide

The claim is a conditional bound with
`kappa = 6149999/50000000000000 > 2^-23`.
The [source pins](../../SOURCES.json) identify the retained manuscript and PR7.

## Proof obligations

| Obligation | Source |
| --- | --- |
| Large-projector factorization | [projector-batching.tex](../../notes/projector-batching.tex) |
| Common controlled basis and aligned corner | [controlled-projector-basis.tex](../../notes/controlled-projector-basis.tex) |
| Three rank classes | [batched-bit-rank-accounting.tex](../../notes/batched-bit-rank-accounting.tex) |
| Integer widths and bounded row padding | [batched-bit-rows.tex](../../notes/batched-bit-rows.tex) |
| Dependency paths and whole residuals | [batched-path-budget.tex](../../notes/batched-path-budget.tex), [bulk-complex-guard.tex](../../notes/bulk-complex-guard.tex) |
| Complex weighted recursion | [batched-complex-rows.tex](../../notes/batched-complex-rows.tex) |
| Assembly | [batched-assembly.tex](../../notes/batched-assembly.tex) |
| Constructive interchange specification | [batched-algorithms.tex](../../notes/batched-algorithms.tex) |

## Corrected inherited precision bound

The retained Gaussian input generator approximates
`2^-B exp(pi alpha^2 beta_j^2)` before shifting by `B=ceil(1.14 alpha^2)`.
The shift amplifies absolute error by `2^B`. The former choice
`F=exp(pi alpha^2/4)` bounded exact magnitude but did not uniformly bound this
amplified error.

The corrected proof uses `F=2^B`. Its required precision is at most
`32.14p+11 < 34p` for integer `p>100`, preserving the existing budget and all
exponents. See [the correction](../../notes/chirp-scaling-correction.tex) and
[the amended retained proof](../../notes/fast-gaussian-resampling.tex).
Both the standalone note and the combined manuscript include the correction.

## Verification scope

`make verify` includes the new certificates, negative exponent controls,
Gaussian precision checks, and source integration checks, together with the
retained producer validation. The numerical guard assumes the dependency-path
topology proved in the notes; a boolean certificate field does not prove that
topology. The large common rational basis is established by the existence
argument, not by materializing every h28 factorization.

The prior scoped review found no blocking defect in the new batching arguments.
This is not a formal verification or execution of the complete fixed-tape
multiplication machine. Existing upstream assumptions remain explicit.
