# Exact forward/inverse contract clarification

2026-10-08. This clarification supersedes the ambiguous sentence in PROOF.md’s complex boundary section; no arithmetic or cost changes.

A forward primitive call returns the exact selected-axis C tensor on EVERY original role, with identity on all spectator/control coordinates. An inverse primitive call returns the corresponding exact inverse tensor on EVERY original role, with the same spectator identity. The wrapped inverse is implemented with the retained unit-phase/sign identity C^{-1}=−i Z C Z, applied to the complete selected-axis call. It is not described as returning the forward C operator.

Both completed maps have the same Gaussian-dyadic denominator and absolute row-sum bounds used in the semantic guard, and the same complete recursive child widths/volumes. Unit wrappers are included in the conservative local-work charge. Source/target bank exchange in a local two-shear construction is distinct from this completed-primitive inversion contract.

The independent reviewer requested this wording clarification. The candidateκ, all47constraints,7margins, moments, W/rank/G and row stock are unchanged.
