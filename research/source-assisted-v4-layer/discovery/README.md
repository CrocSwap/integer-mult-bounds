# Discovery (not run by verify.py)

The physical layer of the certified package is PR #168's operation frames with PR #200's late compensated reuse
pairing (`physical_opt.py:pairs`, the maximum-weight pairing of `pairs_mw.py` (transversal-matroid greedy with augmenting paths, donor weight the gain heuristic of PR #200)). `flow_frames.py` runs `harness.descend` on the source-aligned cache of
PR #194's pipeline with all frame moves frozen (`DESCENT_LIGHT_ROUNDS=1 DESCENT_FREEZE_FRAC=1.0 --light
--seed-frames`), recomputes the pairs and prices the layer with PR #184's `complex_frame_flow.py`:

    SA_TREE=<PR202 tree> SA_PY=<python with numpy/scipy> DESCENT_LIGHT_ROUNDS=1 DESCENT_FREEZE_FRAC=1.0 \
      python3 -B flow_frames.py --aligned <aligned tree> --seed-frames --light --mw 1 --keep out/

Float flow roots: PR #168's pairing 7.00918e-4; PR #200's default pairing (donors ordered by the gain heuristic)
7.09765e-4; donors ordered by widest end frame with recipients in reverse chronology (`PAIR_ORDER=wide
PAIR_RECIPIENTS=reverse`) 7.09882e-4; the maximum-weight pairing (`--mw 1`, `pairs_mw.py`, every donor-weight variant
tried) 7.09907e-4, the certified layer; random donor orders 6.4e-4 to 6.6e-4. With frames also descended: full cycle
7.08613e-4, one light round 7.0950e-4, 98% of operations frozen 7.09767e-4; a screen over every single endpoint move
on top of PR #168's frames (`flow_moves.py`) finds no improving move, so the frames are left untouched. The matching
itself is PR #168's frozen carrier matching (`matching.py`, `extend.py` are needed only to import `harness`).
Prepared by Chafik Boukhalfa with Anthropic Claude and OpenAI Codex assistance; Apache-2.0.
