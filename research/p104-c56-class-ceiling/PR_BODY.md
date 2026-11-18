P104: a class junk floor |J| ≥ 4166 at owned mass 56 and κ ≤ .0122445 for the C = 56 flag class (Lean + certificate, no κ claim)

Lean plus an external exact certificate. No κ claim.

**Result.** In F1's C = 56 flag model the minimum junk count |J| lies in **[4166, 4216]**. Lower end: a Lagrangian dual certificate (frozen multipliers, exact per-chain flag DP over Q, all 8 configurations; two independent checkers agree). Upper end: a witness of 4216 cells (two configurations; odd cells and diagonal constraints met, rank 55/56). With `hJ : 4166 ≤ |J|`, the ceiling functional of `ceiling_native` gives F(1 − t) < 0 on [.0122445, 1] (`CongestionNative.ceiling_c56`, kernel-only), so κ ≤ .0122445 for any word satisfying the named hypotheses. `.0122444` fails at the point, so .0122445 is the tightest certified 7-digit value of this piece set. For comparison the old class bound |J| ≥ 1936 gave .0136564.

**What this is not.** The frontier words are NOT in this class. They have rank 11 and multi-dimensional lifetimes (their junk count, 4962, is computed, not a point of this model); they are covered by #7668 and #7678. This package is a structural statement about what C = 56 flag decoders must pay, not a bound on any current word.

**Scope hypotheses (all in `PROVED.md`; none proved in Lean).**
- The certificate is computer-certified outside Lean. Lean takes `hJ : 4166 ≤ J.card` as a hypothesis; the DP is not formalised.
- Rank-8 Y-plane rows with C = 56 in one of F1's 8 configurations; the rigidity of the row factorisation is numerical and quoted.
- Monotone frame chains with any step sizes (multi-dimensional steps are dominated by a refinement; proved on paper in the audit, so not a hypothesis).
- **No split gathers and no split reads.** One piece per gather and per read, per chain. This is a real hypothesis, not a technicality: with split gathers a non-forced chain contributes an unbounded prefix sum and the bound for multi-chain cells fails; only the single-chain 1936 survives splits, and no cost rule excludes splits.
- Plane separation (no second owned plane carries plane-1 X content).
- Not covered: decoders with 9 or more rows, network decoders, owned mass above 56, public-layer cancellation of arrival junk. The ceiling also inherits the premises of `ceiling_native` (`hcong`, `hdist`, `hspMono`, `hcstMono`, the spF / cst brackets).
- The upper end 4216 is an exhibited witness that was re-verified exactly; its data is not in this package, so only the lower end is reproducible from the files here. The true minimum is not claimed.

**Contents.** 10 new Lean modules (`CongestionC56*`) on top of 36 unchanged ones (46 in the closure, rebuilt fresh, CHECK.txt; axioms propext, Classical.choice, Quot.sound; no sorry, no native_decide). `certificate/`: frozen multipliers with SHA-256, geometry data, two checkers (`jr_lagx.py`, `aud_cert.py`), their logs. The multiplier search and table-generation scripts are not included.

DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
