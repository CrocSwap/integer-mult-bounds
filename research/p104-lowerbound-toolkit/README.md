# p104-lowerbound-toolkit: kernel-checked lower-bound and rung lemmas for P104 (theory and tooling, no kappa claim)

**What it is.** 92 new Lean modules (about 2.6 MB) on top of the earlier P104 Lean library, which is carried unchanged
(259 modules, byte-identical to the library shipped with our CERTKIT package, which is itself the one from #7796 plus the
crossing statements). Every module is kernel-checked: no `sorry`, `native_decide`, `axiom` or `extern`; finite facts use
`decide +kernel`. Every declaration printed by `lean/Check.lean` (247) depends only on `propext`, `Classical.choice`,
`Quot.sound` (`CHECK-axioms.txt`). The package makes no kappa claim.

Labels: **[P]** proved in Lean from the stated hypotheses; **[C]** a finite computation checked by the kernel
(`decide +kernel`); hypotheses are listed per row. **Wall56** is the tier-1 premise
"every legal P104 word pays D >= 56 and R >= 56 per call" (and **Wall56@Q96** its form on the 96-port Q96 sector).
It is a premise wherever it appears below; nothing here proves it.

## Results

| # | Statement (module) | Premise | Status |
|---|---|---|---|
| 1 | Half-integer **linear** decoders: if the row-pair matrix M = (alpha_j . p_k) is invertible on n = 2g rows and labels carry no extra quadric (HInj), then C >= rho_A + rho_B >= 2 C(n,2) = 2g(2g-1) (`LinOrd`, `LinCore`, `LinFinal`; Rado with deficiency, ordering lemma, existence form of Cauchy-Binet in `LinCB`) | linear class; M invertible; HInj | [P] |
| 2 | P104: C >= 56 for every Z/4-linear half-integer decoder, without the extra hypothesis hMu (`LinP104Free`, `LinP104FreeInst`, `LinKbar*`, `LinP104*`; mod-2 kernel of the decoder law is {0, B}, certified by the kernel) | Z/4-linear decoders | [P] + [C] (finite kernel facts) |
| 3 | Halving / doubling laws for half-integer decoders: rank Yhat + rank Zhat <= C = sum rank Q_k; Z/4 halving potential (`Doubling`, `HalvingLaw`, `TensorPot`) | none beyond the decoder identity | [P] |
| 4 | Network form: for a Z/4 network with drops d_k, n <= sum_k [C(d_k+1,2) + iota_k d_k (h - dim a_k)] (`NetNG`); at n = 104, h = 9 this gives D >= 21. F2 potential rank(Q o GNF) <= D and its port-doubled master form (`NetDoubling`); bowtie and tight-chain contraction (`NetBowtie`, `NetContract`) | model hypotheses of each file (DAG, charts b_k <= a_k, N = (1-H)^-1) | [P] |
| 5 | Node-restricted level cut: rank M_l <= |C_l| and sum_l rank M_l <= D for relays of any slack; NET8 corollary: with exactly 8 gathering and 8 depositing descents, D >= 56 (`LevelCutRelay`, `Net8`, `Net8Cut`); downward-crossing cut DX: sum_l rank M*_l <= D (`LevelCutDX`) | NET8 uses the P104 net model | [P] |
| 6 | Future-attribution cancellation law, its transpose for the R side, and the price bound rank <= lifetime cost for runs of class F (`FutureAttr`, `FutureAttrT`, `PriceLemma`); carrier-tree runs (`CarrierTree`); chain law and epoch facts, hot intake as a legal relay inside class CF, with the Q5 and E8 instances (`CFChain`, `CFRelay`, `CFRelayQ5`, `CFRelayE8`; R >= 56 in the rank-8 sector) | class F / CF (cold intake or hot intake inside CF) | [P] |
| 7 | Lemma T (odd-cell identity forces a contradiction on three ports), all-or-nothing law for blocking sections, chart-clean lemma, PRICE7 reduction (`LemmaT`, `AllOrNothing`, `ChartClean`, `Price7`) | the named hypotheses of each statement (H_frame, H_FS4, A inside Lam) | [P] |
| 8 | P104 frame data: all 1152 frame-blocking 7-dim sections satisfy H_frame (`FrameCert`); completeness of that list among all 43435 two-dimensional normal subspaces (`BlockComplete`); block laws (`BlockLaw`, `BlockLaw2*`) | frames = the 759 frames as data, labels as data | [C] |
| 9 | Caller side: signed-Gram normal form P_k = 1 + A H B^T and rank K + n <= |iota| (`CallerSGram`); relay-cut law RC2, pair form (`CallerRC2`) | field of characteristic /= 2 for the forward law | [P] |
| 10 | Port-general word rung: kappa < kbar from a caller certificate, the per-call rung invoice and walls (`WordRungPort`); the walls enter only through the aggregate premise Sum(D+R) >= 112 per call on average (`WordRungJoint`) | **Wall56** (D, R), caller certificate | [P] reduction |
| 11 | Rung at label rank h: molecule price discharged for every h >= 3 (`PriceH`, `PriceHRung`, `PriceHI4`..`PriceHI19`); instances h = 7, 8, 9 (`PriceHMain`); height-cut contract at any label rank, derived from the port-row shape (`HCutGen`, `HCutGenMain`); word-shape lemma at any label rank (`WordShapeH`, `WordShapeHToy`); budget premise proved for h = 7 and 8 with kbar >= 146/15625 (`BudH`, `BudH7Cert`, `BudH8Cert`); chain from a legal word (`RungWordH`) | **Wall56** (aggregate form), caller certificate | [P] + [C] (budget certificates) |

Non-vacuity instances are included for the statements that carry hypotheses (toy networks, `LinToy`, `CFRelayE8`,
`WordShapeHToy`, `nonvac_*` in `HCutGenMain`, `PriceHMain`, `LemmaT`, `AllOrNothing`).

## Not covered

- Hot intake outside class CF (the carrier-run results are for class F / CF runs only).
- Network-coding gain: the NET-D56 core statement (D >= 56 for networks with arbitrary relay structure) is not proved; rows 4 and 5 give D >= 21 and the 8-descent corollary only.
- Decoders with denominator > 2 beyond the linear class.
- Callers with k > 71 (the caller-side results here do not reach them).
- Wall56 and Wall56@Q96 themselves; every rung statement above takes them as hypotheses.

## Layout and checking

- `lean/Nov15/` 351 modules (build order in `lean/build-order.txt`, root `lean/All.lean`), `lean/Check.lean`
  (`#print axioms` of the 247 declarations the new modules print), `CHECK-axioms.txt` (result of loading the built closure).
- `tools/framecert/`, `data/frame/`: generator and inputs of `FrameCert.lean`; `python3 -I tools/framecert/asm.py OUT.lean`
  rebuilds it byte-identically (checked in `verify.py`).
- `verify.py`: package integrity (sha256 pins both ways, token bans outside comments, topological build order equal to
  the import closure, Check.lean / CHECK-axioms.txt consistency, toolchain and Mathlib pins, FrameCert regeneration).
  `verify.sh` runs it and then `lean/check.sh` (guarded sequential build, per-file RSS cap, then the axiom audit;
  needs elan with the pinned toolchain and `lake exe cache get`).

## Open next questions
- Wall56 and Wall56@Q96: the rung chain (rows 10 and 11) takes D >= 56 and R >= 56 per call (aggregate form: Sum(D+R) >= 112 per call on average) as a premise. First step: the NET-D56 core, i.e. D >= 56 for networks with arbitrary relay structure; rows 4 and 5 only give D >= 21 and the 8-descent case.
- Hot intake outside class CF, denominators above 2 beyond the linear class, and callers with k > 71 are outside the statements above.

Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code. Apache-2.0.

Note: `Price7.lean` here imports `Nov15.PriceLemma` instead of embedding a verbatim copy of it, so that the two modules load together; the added part (`rank_ge`, `price7_core`, `price7`, `price7_sevendim`) is unchanged.
