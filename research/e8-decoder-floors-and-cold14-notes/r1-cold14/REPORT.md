# R1 resume (record track) — no strict gain yet
Worktrees: ~/imb-r1 (branch research/cold14-e2, base pr615, WIP commit with tools in research/r1-wip-tools/),
~/imb-r1b (branch research/cold14-b3-r1, base pr617, unchanged). Sources: ~/imb-src/pr{568,569,571,575,583}.
Verify: PATH=$SP/venv/bin:$PATH sh research/<pkg>/verify.sh WORK ~/imb-src  (system python3 is too old). #615 baseline PASS kappa 0.001626010676080313 (615 s).
Tools ($SP/r1/tools == research/r1-wip-tools): price.py (exact b via PR568 moment.certify), V.json/V617.json (mass-neutral 1e-9 b per rank-r child),
nulls.py/broad2.py/hypsurvey.py/cands.py (cone capacity), coal.py/coalf.py/movecoal.py (frame-coalescence scans), aglp*.py (aggregate LP), mip617.py + expand617.py (free-dispatch MIP -> OWNERS/PLAN).
## Findings (on #615 words; #617 keeps E1)
- e2 infeasible: for all 3 Lean pairs (E=[30],[6],[24] raw) left-nullity of row-cone matrix over same-E helpers == #already-ended (12/24/12) on jp8 and atm3. Cold-mixing directions exist only via cold helpers 542/543/554/555 (E30), 566/567/578/579 (E24) but their column cone is unfixable (col-null space has no vector on them); other violators (315,347, data ports) are blocked by monotonicity.
- Cold dim-8 (bot,U) extras: best single end net -5.67 (V units), all negative.
- E1 partners 438/440 cannot be replaced by already-lifted registers (nullity drops 12->11 per dropped partner).
- Frame coalescence (PR583-type) on jp8 joint-prefix word: 0 single-gate (incl. final frames), 0 with commuting moves W=6 (validation on atm3 reproduces PR583's 6).
- #615 owner/dispatch: aggregate LP (any remainders, even unlimited windows) == current solution -> no owner/dispatch gain on #615.
- #617 (kappa 0.001635183729255778): its MIP hit time limit with remainders {1:24,2:2,3:2,7:2}. My LP (any remainders) bound is +119.3e-9 b over #617's map at fractional dispatch jp8 60.9/atm3 11.1 -> an integer perfect packing at jp8x61/atm3x11 would be ~+115e-9 b (~+1.1e-7 kappa). THIS IS THE NEXT LEVER.
## Resume
cd $SP/r1/tools && ../../venv/bin/python mip617.py 3 1800 ../m617   # free-dispatch Hall-mask MIP (was running, 900 s)
mkdir ../m617-out && ../../venv/bin/python expand617.py ../m617.pkl ../m617-out
../../venv/bin/python price.py "$(cat ../m617-profile.json)"   # compare to b of #617 = 0.0016378619344417451
Then: copy OWNERS/PLAN into ~/imb-r1b/research/complex-571-cold14-b3/data, update SPEC.json (data hashes, dispatch, expected global_profile/provider_counts/kappa/idle remainders), WITNESS/EXPECTED (spec.py generate), MANIFEST, rerun verify.sh with --reuse-baseline/--reuse-local from $SP/r1/b3-base for iteration, then full fresh run.
