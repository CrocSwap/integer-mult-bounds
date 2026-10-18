# B105: opening miner on #656 canonical word. VERDICT: 0 priced-positive openings (rigidity fact). ship=false. No heavy jobs, no kappa claim.
Tool: work/miner.py (reusable: W(path) loads any CANONICAL-WORD with A,B,cut,centers,start,final,frames; tail optional). run1.py/run1b.py (cat1 uncompute+rename gates), run5.py (cat5), usage `python3 -I run5.py WORD [sample]`. Base: forward join cascade on unmodified word = 0 violations (also on #646 ck/jp8 words; miner runs there too).
Lifetime = first TOUCH (zero-reads/dummy cold ops carry frames) to last touch in A,cut,B,tail. First attempt used first nonzero row: gave 39 "nested" pairs, all dead because b's earlier zero-touch ops hit a (B99 pitfall; fixed).
## Counts (raw / cascade-clean / value-checked+priced-positive)
- Cat1 lifetime pairs (helpers): 4708 disjoint ordered pairs; 0 frame-nested (0 growth); 58 with growth 1 dim. All 58 fail cascade on RENAME ALONE (no uncompute): 7-8 target end frames forced 8->9. => 0 / 0.
- Cat1 (loose, first-nonzero lifetime): 39 nested, uncompute-alone clean for ~9 (a=370,402,545,568,569,578,585,586,590 with 'all' sources), every rename fails (7-8 target caps). 0 clean.
- Cat2 idle: 1016 gaps >=400 ops between touches; 44 helpers idle at final frame >=400 ops before last use. Hosting inside a gap (b's span inside a's gap, frames nest): 0 raw. (Hosting a nonzero a would also need dirty restore, #665 >=5x.)
- Cat3 slack: stored op frames above operand join: 251 ops (pre-raises). Lowering them ALL makes the profile worse (units 2542->2582, w2 414->886, w3 434->154): shipped pre-raises are coarsening, not slack; mass invariant 5568. End slack 508 regs = cleanup climbs (not true slack). B98d suggestion (433/435 -> wide kept regs): 433 equals 432 only in ops 3609-3642 (frames equal) yet 433 is read through tail (6043) with changed content => not replaceable; 20=442 equal in 3618-3643 only. No clean candidate.
- Cat4 near-disjoint (<=2 interleaved touches, frames nest): 0 raw.
- Cat5 role swaps: 982 equal-content pairs (1179 intervals; H-H 422, L-H 332, T-T 216, T-H 12); 988 intervals start with equal frames. Sampled 900 swap moments: 657 cascade-clean (pure relabel), but swapping creates 0 new nested pairs (growth-1 count stays 58, all still fail). NOT value-checked: a swap changes the x,y end rows unless equal at end, so no swap counts as an opening.
- Copy elision (5c, y's writes dropped, reads redirected to x equal in [t0,t1)): 16 raw (tail copies 519,536,548,552...), 0 clean (2-4 target end frames 8->9).
- Twin elimination (all touches inside equality interval): 6 raw, all need dropping the copy op; folded into 5c.
## Interpretation
Shipped frames are tight against target perp(port) caps: ANY change giving a helper-register a frame different from its shipped history, even +1 dim, pushes 2-8 targets 8->9. Frame-nested disjoint pairs do not exist at all. Consistent with B99/B98c/B100.
## Not done
#664 word not rebuilt (heavy.sh BUSY, 3/3; rebuild ~10 min); miner is ready for it. Value replay (judge rule) never reached because no candidate passes the frame cascade; add exact Fraction row check (rows_at) before pricing for any future pass.
