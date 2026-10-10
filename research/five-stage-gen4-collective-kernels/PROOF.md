# Collective response kernels on the gen4 word, with the descent retiming

**Claim.** On PR #276's gen4 bit word in the five-stage completed banks, with PR #279's 880 concave-descent gate
retimings applied first, the rewrite of 695 response-kernel entries with per-entry cuts — 416 twin pairs on lines,
24 twin pairs on 16-dimensional entrances, 255 multi-donor families (pivot response = XOR of the donors' responses,
common nondegenerate entrance of dimension 1–18, donors shared along nested chains) — is a legal word of the same model
with literal stock 1,277,965 and κ = 724733001963261/10¹⁸ = 7.24733001963261·10⁻⁴, checked by every stage of #276's
verifier with the changed literals re-pinned.

The mechanism is PR #254's response-kernel pair generalised as in PR #259/#272 (several simultaneous zero-response
directions): for a family (p; d₁..d_k) with R_p = ⊕ R_{d_j} and a common nondegenerate E inside all members' first
required frames, the pivot starts at E with its compensation reads deleted, each donor is moved to E at the cut and
absorbs p there (Q = I + Σ e_{d_j} e_pᵀ), the old word resumes, and Q⁻¹ is paid at the full frame; the omitted
response cancels against the induced one. eumemic's PR #268 gave the stage its form in this pipeline; here the cuts
differ per entry because gen4's compensation reads are chronological, and the entrance may have any dimension.

The construction, the censuses, the selection, the bank tiling for the 17 new residual widths and the complete list
of re-pinned values are in [KERNEL-PROOF.md](KERNEL-PROOF.md).

Not claimed: no Lean certificate; the public all-size interfaces retained by #276 remain hypotheses; #279's stage is
vendored and not re-proved. Residual widths 3 and 4 (e = 20, 21) are not supported by the tiling generator and no
entry needs them; quintuples are never net-positive under the φ ledger (a fourth donor outweighs the pivot).
