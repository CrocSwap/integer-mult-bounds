# YRelay.lean: JUNKLB3 L2 (Y-relay) + YRELAY necessary condition. No sorry, ~6 s, 1.7 GB RSS
Lane LEAN-NEXT11, Nov 16. Sources: cards/WILD/BIG/JUNKLB3/THEORY.md §L2, cards/WILD/BIG/YRELAY/RESULT.md.
Axioms: [propext, Quot.sound] (+ Classical.choice for the cone and the ℚ counterexamples). Op model: TokenCancel's.

**L2, relay pair.** `relay`: Y_q reads −c·Y_p at chart 0 (add q p (−c)), the window `mid` runs, then Y_q reads +c·Y_p at chart F.
- Hypothesis `Quiet q` on every window event: nobody reads Y_q, and Y_q is written only by ADDs. Y_q's own ADD-reads are allowed.
- Conclusion: the end state is the relay-free run's end state with c·(row_p(t2) − row_p(t1)) added to row q. Every other row and every location is unchanged. Later events then propagate this one-row difference linearly (SwapWord.run_diff).
- `win_delta`: if Y_p is written only by ADDs in the window, and every row it ADD-reads lies in N, then row_p(t2) − row_p(t1) ∈ N.
- `relay_no_token`: with N = `tokFree T`, T = {e_p, x_p}, Y_q's net change has no e_p and no x_p coefficient ("no net token").
- **Precise "no crossing arrival in between"** = `Win p (tokFree {x_p, e_p})` on the window [chart-0 read, relay read]:
  - Y_p is written only by ADDs (no SCALE/CLEAR/COPY/INIT of Y_p);
  - every row Y_p ADD-reads has zero x_p and e_p coefficients.
- The cleaning case ("Y_p reads −J_p, so Y_q receives −c·J_p") is `relay` with row_p(t2) − row_p(t1) = −J_p.

**Findings (prose too strong, minimal fixes).**
- `scale_leak`: a SCALE of Y_p in the window leaks e_p into Y_q (here the window has no read into Y_p, yet the e_p coefficient is 1). Fix: Y_p written only by ADDs in the window. "The order of Y_p's own reads is irrelevant" is true for reads only.
- `read_leak`: if any register reads Y_q in the window, it keeps −c·e_p. Fix: Y_q is quiet in the window (not read; written only by ADDs).
- JUNKLB3 states neither hypothesis.

**YRELAY necessary condition.** `coneStep`/`coneRun` build each Y main's reach cone forward in time:
- its own birth token;
- non-Y rows it reads (at read time);
- at a meeting chart (`Meet`), the cone of the Y main it reads (a COPY replaces the cone).
`cone_inv`: every Y main's row lies in cone ⊔ G, provided `HubGRun`: every Y-Y read at a non-meeting chart carries only G-content. This is the formal form of "the {0} hub fixes G0 tokens only". With Meet = every chart the hypothesis is vacuous.
`not_reach`: content outside cone ⊔ G cannot be that Y main's final row.
So a relay copies only content some Y main already holds, along time-ordered Y-Y meetings. This is RESULT's reach test, sound as a necessary condition.
