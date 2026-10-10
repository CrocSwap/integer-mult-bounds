# Collective response kernels on the gen5 word, after the descent and target stages

**Claim.** On PR #285's gen5 bit word in the five-stage completed banks, with PR #287's 904-gate descent retiming and
220 target-prefix squares applied first, the rewrite of 450 response-kernel entries with per-entry cuts (260 twin pairs,
190 multi-donor families; pivot response = XOR of the donors' responses, common nondegenerate entrance of dimension
1–18, donors shared along nested chains) is a legal word of the same model with literal stock 1,244,515 and
κ = 186178624839407/(25·10¹⁶) = 7.44714499357628·10⁻⁴, checked by every stage of #287's verifier with the changed
literals re-pinned.

The mechanism is PR #254's response-kernel pair generalised as in PR #259/#272 (several simultaneous zero-response
directions): for a family (p; d₁..d_k) with R_p = ⊕ R_{d_j} and a common nondegenerate E inside all members' first
required frames, the pivot starts at E with its compensation reads deleted, each donor is moved to E at the cut and
absorbs p there (Q = I + Σ e_{d_j} e_pᵀ), the old word resumes, and Q⁻¹ is paid at the full frame; the omitted response
cancels against the induced one. The stage is the one of PR #282 (gen4), re-derived on gen5: the cuts differ per entry
because the compensation reads are chronological, and the members are plain dirty helpers, disjoint from the targets
whose reads #287's squares delete and from its retimed source-pair mixes.

The construction, the censuses, the selection, the tiling and the complete list of re-pinned values are in
[KERNEL-PROOF.md](KERNEL-PROOF.md).

Not claimed: no Lean certificate; the public all-size interfaces retained by #276/#285 remain hypotheses; #285's word
and #287's stages are inherited, not re-proved. Pivots of residual width 3 or 4 (entrance rank 21 or 20) are not
supported by the tiling generator and none is selected.
