# B244 VERDICT: NO GAIN. Realised Δκ = 0 (bound +1.3149e-5, +0.787%); 0 of 78 splits merged. No word built, no ship candidate.
Ship bar now #1065 κ 1.672644568760139e-3 (card said #1031); nothing near it.

## Blocking class (structural, all 78): PARTNER END CAP
classify.py (splits.json): every one of the 78 mergeable splits is a T->E split (the register's tail-gate climb followed by its own end climb; d1,d2 = (1,5)x32, (1,1)x22, (2,1)x16, (3,1)x8). In every case the gate partner is a low-end helper (helper_final, end 8 or less) while the split register ends full (9). Merging = running the gate at the register's end frame, which would raise the capped partner beyond its end (frame must stay inside end). lift.py: lifting any single gate (to full / its end / later joins) is legal for only 2 of 116 gates, both profile-neutral (Δκ 0).
Hence "frames alone give 0" is explained, not just asserted: the cap, not laziness, blocks it.

## Scalar rewrites tried (exact algebra, frame-profile priced by price.py, 0.5 s/eval)
- Commutator relay E_tr(x)E_rs(c/x)E_tr(-x)E_rs(-c/x), both orders, ALL 700 relay registers r, per-op frame choice (ops not touching the capped partner may be lifted to full): relay2.py, first 3 splits (stopped by the SYN-23 stop rule; ~16.8k evals, 3 distinct profiles, all WORSE: -1.1e-7, -1.8e-7, -2.0e-7). A relay raises all three registers to span(t,r,s), never less than the plain gate; the partner restore of the relay register needs the capped register again while the relay is above the cap.
- Order permutations of the tail (all commuting single moves) and adjacent-pair reassociation with a Steinberg corrector gate: 0 distinct profiles (all identical to base) - search.py order/assoc.
- Information argument (not a rigorous proof): once the capped partner's content is copied into a register that later reaches frame 9, only ops among frame-9 registers can remove it, an invertible transform that cannot zero it; so no relay chain can avoid touching the capped register at <= its cap on the way back.
- Not done: SYN-23 extras (coded y+=y target edges at frame 0 / free target-basis choice, cgx_leaver.py:244-249,:433-435) - these change the B-side target ladders (a different word, not a tail rewrite); per the stop rule they are the likely remaining route ("needs a different target ladder" / lowering the partner caps, which is +1 mass per capped helper ~ -2.8%, not mass-neutral). The wider per-split CP-SAT search was not built since a relay/reorder/reassociation sweep is exhaustive for the 4-op commutator class and found nothing; general programs were not enumerated.
- Bug note: search.py relay mode crashes on 'scale' ops in the tail (18 of 116); relay2.py only touches add gates.

Files: ev.py (tail profile evaluator, reproduces 1.67166528321877e-3 exactly), classify.py, lift.py, relay2.py, search.py, splits.json, res_*.json. Audits (value replay, audit_local, exact κ) not run: no candidate word.
