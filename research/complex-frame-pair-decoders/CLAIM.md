# Local sprint claim (no pinned coordination issue exists)

- Recorded: 2026-10-13T14:55Z (approx.)
- Track: 40-49, structural decoder research. Assignment seed **47**, drawn once with
  `python -c "import secrets; print(secrets.randbelow(100))"` (OS randomness) at 2026-10-13T14:12:28Z.
- Base commit: `47481c89fd30a43f8f882eb4b391e89c29273fd0` (main, "Record publication and merge
  confirmation for all eighteen PRs"). Selected kappa 0.001661957774647029 (PR890, complex-bound).
- Object: exact 8-term complex decoders (D = R A, T = R A^-T) in PR717's B14 decoder model
  (E8 root lines, labels in F2^9, Theorem C pairing-rank cost), on punctures of the 120 lines.
  This is the copied-information cost of the binding complex supplier (P112, cst 64).
- Question: what mechanism produces PR717 D3's P111 = 63 and P104 = 56 hits, which punctures
  attain it, and what is the copy-ratio floor cst/v for exact 8-term decoders below a stated
  puncture threshold?
- Method: pairing-rank linear algebra over F2^9; exhaustive violator census over the 8
  W(E8) hyperplane-flat types and all 511 hyperplanes / 43,435 codimension-2 subspaces of F2^9;
  exhaustive frame-pair census; exact integer verification of explicit decoders; favorable-budget
  pricing on the selected T21 profile with the pinned moment engine, including the bit-supplier cap.
- Candidates considered and not chosen: (1) mixed-beta n >= 9 decoders on P112 (PR717 open problem 1;
  SAT attempts already killed, high risk); (2) non-B_K stage schedules (format-limits "not covered";
  legality not modelable without new spec work); (3) a further bit-side puncture census (crowded:
  #631, #761, #875, #939, and the bit side does not bind).
- Expected deliverable: research note / scoped structural result. No kappa claim.
- Expected finish: same day.

## Result (2026-10-13)

- Delivered as `research/complex-frame-pair-decoders/` (research note / scoped structural result, no kappa claim).
- Mechanism: a term costs 7 exactly when its row and column normals are an odd root pair with both lines
  punctured; PR717's D3 hits all have this form.
- Theorem (exact 8-term decoders, punctures p <= 24): cst >= 72 - p for p <= 15 and cst >= 56 for p <= 24,
  both attained at every p; copy ratio >= 7/13, equality only at p = 16 (frame pairs; 896 of 1260 frames).
- Favorable budget (PR717 P1 knobs, pinned engines), first on T21 and after rebase on T37: P111 +0.67% b;
  P104 +5.51% b, capped by the PR589 bit supplier at kappa 0.001730427469823602 (+4.12%).
- Rebased at 15:15Z onto bbc600db2fc15007b7c914f4f2b2ed55fa909c87 (T37 selected, PR942).
- Reproduce: `python3 -I -B research/complex-frame-pair-decoders/verify.py` (48 PASS, ~30 s, stdlib only).
- Submitted: https://github.com/CrocSwap/integer-mult-bounds/pull/968 (status: research note / scoped structural result).
