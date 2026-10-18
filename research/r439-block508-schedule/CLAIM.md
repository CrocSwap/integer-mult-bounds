# Sprint claim (local; no pinned coordination issue exists)

- Track: bit supplier (00-19). OS-random assignment seed: **5**
  (RNGCryptoServiceProvider, mod 100). A non-crypto shell draw returned 76
  first and was discarded in favor of the OS-random draw per the task spec.
- Base commit: `f567884aeb8851b6e794af1184119a3bfbe1e631`
- Object: tuned R439 phase-B block at frame 508 (`B[205:242]`, 37 gates,
  registers `[19, 27, 35, 43, 57, 65, 66, 74, 89, 97, 466]`).
- Method: exact whole-block single-write rescheduling; forward discovery DP
  plus independent backward-DP minimum certificate; full local exact
  verification (integer maps, Boolean tables, splice + literal cleanup,
  frame paths, paid profile, 661-column endpoint, H1-H5, exported bills).
- Deliverable: `research/r439-block508-schedule/` with `verify.py` (one
  reproducible command, stdlib only).
- Expected finish: within the session; status: **complete**.

## Selection trail (three candidates, seed-diversified)

1. Block 522 (43 gates): single-write class infeasible (outputs 29/106
   exclude the hub total while every shareable compound includes it), so no
   layered rescheduling can realize it; beating 43 requires multi-write
   interleaving. Not pursued as a construction.
2. Block 521 (47 gates, largest): same infeasibility result. Not pursued.
3. Block 508 (37 gates): whole-block single-write minimum is 30 with an
   achieving witness. **Selected.**

The choice pivots once, on this evidence, from the seed-shortlisted block 522
to block 508. Related open work inspected before claiming: #843 (frame 509
sum reuse), #844 (block 4 fixed-factor schedule), #857 (block 8 integer
factorization), #728/#792 (phase-A mini-nodes, different section; their
frame-507/508 no-improvement statement covers mini-nodes only), #867
(selected-source coverage audit, different track). None covers the B-section
block at frame 508.

## Result

Construction complete, no new kappa: 37 -> 30 block additions, 24,305 ->
24,291 complete ADDs, forward positive bound equal (49,347), reverse bound
reduced (1,113,070 -> 1,086,054), payload 93 bits, paid profile and rank mass
unchanged, minimum 30 certified by two independent DP implementations.
`verify.py` passes in normal, optimized (`-O`) and isolated (`-I`) modes.
Native C++ replay, hosted invoice, global assembly, Lean and remote CI remain
open obligations, recorded in README.md.
