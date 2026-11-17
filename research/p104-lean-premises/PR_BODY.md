Lean-only package, part 3 (combined). No κ claim.

Kernel-checked Lean (Lean 4.33.0-rc1, pinned Mathlib; propext, Classical.choice, Quot.sound only; no `sorry`, no `native_decide`) with named hypotheses, in four groups.

**1. Premise narrowing for #7620** (the premises on which our #7623/#7630 κ is conditional). CLEAR certificates are sound and complete and every CLEAR is lossless (`ClearCert`); owned ascent is priced symmetrically, earns no credit, and relaxed-class floors imply strict-class floors (`OwnedAscent`); exact rows are equivalent to all columns (`NativeColumns`); the 981-pair census is a delta census, with kernel-checked inheritance from #7623 (`CensusComplete`); E1, E2 and E3 (flat and tree, under atomic calls) hold for the real owned skeleton of #7630 (`OwnedSkeleton`, `OwnedTree`). `PREMISES.md` lists per premise what is now a kernel fact and what is still assumed.

**2. Ceilings.**
- Caller side: cost closed form and the #7113 caller invoice (`CallerCost`); κ ≤ .0419448764 for rho = 2 two-arm callers under named hypotheses, with fully kernel-checked 2|2 (t ≥ 141/4096) and 1|1 (t ≥ 176/4096) bounds (`JointCeiling`).
- Whole word: **κ ≤ .0204110965 over legal (nested) words** (`WholeFloorNest.kappa_whole_floor_nested`). Hypotheses: Theorem Y (`h_Y`), slack-rank independence (`Indep`), the F-currency pricing link (`hF`) and `Priced`; the numeric cover is discharged in the kernel (`WholeFloorCover`, `NumCertK`). The verifier's nesting rule is what rules out lateral owned MOVEs (see FALSE.md item 11).
- **κ ≤ .0060197405 for class K(S22)** (`FloorK22`, `NumCertK22`), hypotheses: the rank input `ClassK22.rank_ge`, the cost-model links, and the caller-log input.
- **κ ≤ .0183952347 and κ ≤ .0134769139 for the restricted class M_V** (`CongestionI3*`), the second with descent mass ≥ 56. Hypotheses: the I3 path bound, the flag-DP minima, rank-8 decoders with C = 56 (exactly), and the public-provenance law. No known native lies in M_V, so these bound the restricted class, not the native class.
- Supporting: the 780-stop class-K LP certificate checked by `decide +kernel` (`FloorCert*`), descent pricing, helper D0 ≥ 2 ln 2 per paid stay (`FloorD0`).

**3. Word structure.** `Shadow` (the twin has the same net invoice, hence the same S, F, D0, κ), `Annihilator` (served ports ≤ descending owned rank), `Delivery` (net delivery needs two contacts with different courier rows; three genuine hops cost ≥ f(3); direct-read capacity), `DesignLaws`, `SharedCourier`, `PsiLaw`, `WordDuality` (legal words map to legal words, the Theorem-K invoice and roots are unchanged, P104 boundaries are self-dual), `PlaneLaws` (SPLIT for any n; QUARTER an exact partition for any n and block B containing 1; counts kernel-checked on E7 only), with `HubSettle`, `RankLaw`, `RankLawC`, `FrameSep`.

**4. Spec-break kills and small lemmas.** The rank, Gram and involution lemmas behind the kill arguments (`SpecTS`, `SpecGC`, `SpecRankP`, `SpecRankP2`, `SpecLemmaU`, `SpecLemmaU2`, `Spec6`, `PadLift`, `Spec0Sym`, with `SpecTSUR`, `SpecINV`, `CallerBorrow`), `LemmaW`, and `SmallRoots` (kernel checks of three small-caller roots). `Spec0K0_ABCEDF_s0..s6` are PARTIAL: certificates for 60 of 68 targets of one class; 8 targets are not certified.

`PROVED.md` gives every theorem with its exact hypotheses. `FALSE.md` lists the statements Lean refuted or corrected, among them: the lateral-move floor (a counterexample, repaired by the nesting rule), the three-genuine-hop bound 3.30 (needs genuine hops), ONE-READ (needs descent), two span/obstruction statements, the "same invoice" claim for the twin (only the net is equal), a rounded recipe (off by 0.13), an arm-of-1 overcharge that withdrew an earlier ceiling, a false composition law for caller cost, and "COPY becomes ADD" under the duality (false as matrices). `CHECK.txt` has the compile table and axioms.

Not wired into any build or verifier (unregistered, like the other Lean packages). Not included: scripts, generators and source data; the generated Lean data files are included and their fidelity rests on reading.

The premises under study are SYLforge's (#7616, #7620); the caller is rohanarun's (#7113). DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
