# Response-kernel twin pairs on the gen4 word, with the descent retiming

**Claim.** On PR #276's gen4 bit word in the five-stage completed banks, with PR #279's 880 concave-descent gate
retimings applied first, the rewrite of 424 twin dirty-helper pairs with per-pair cuts (pivot entering at a rank-one
line, donor paying the setup and restore gates) is a legal word of the same model with literal stock 1,281,975 and
κ = 180985932153783/(25·10¹⁶) = 7.23943728615132·10⁻⁴, checked by every stage of #276's verifier with the changed
literals re-pinned; without the retiming, κ = 7.23241244294406·10⁻⁴.

The construction, the per-pair cuts, the selection, the bank tiling and the complete list of re-pinned values are
in [KERNEL-PROOF.md](KERNEL-PROOF.md). The mechanism is PR #254's response-kernel pair (two untouched dirty helpers
with identical complete F₂ target responses; the pivot's compensation reads are replaced by the donor's absorbed
copy at a common nondegenerate entrance and undone at the full frame), in the form eumemic's PR #268 gave it for this
pipeline, adapted to cuts that differ per pair because gen4's compensation reads are chronological.

Not claimed: no Lean certificate; the public all-size interfaces retained by #276 remain hypotheses; #279's stage is
vendored and not re-proved. Not exploited: the response matrix of the 13,944 plain helpers has F₂ nullity 12,184, so
collective kernels (several simultaneous zero-response directions, PR #259/#272) and shared donors have ample room on
this word; the 144 admissible pairs beyond the 424 are net-negative under the φ ledger.
