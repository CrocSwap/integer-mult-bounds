# Early restorations and terminal sinks on the gen5 kernel word

**Claim.** On PR #285's gen5 bit word in the five-stage completed banks, after PR #287's descent and target stages and
#290's 450 kernel entries, executing 440 single-incidence helper restorations early (helpers end at a rank-23 join E;
residual P_E − P_σ) and deleting 8 terminal-sink helper registers is a legal word of the same model with R = 15,878,
literal stock 1,242,935 and κ = 745513573133379/10¹⁸ = 7.45513573133379·10⁻⁴, checked by every stage of the verifier
with the changed literals re-pinned; the complex supplier is the PR #233 word (coarse 7.54736418878859·10⁻⁴), so the
bit side binds.

Details: [LEVERS-PROOF.md](LEVERS-PROOF.md); the kernel stage: [KERNEL-PROOF.md](KERNEL-PROOF.md), [PROOF-PR290.md](PROOF-PR290.md).

Not claimed: no Lean certificate; the public all-size interfaces retained by #276/#285 remain hypotheses; #285's word,
#287's stages, #233's complex word and the #280/#283 mechanisms are inherited, not re-proved.
