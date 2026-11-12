# PROOF_MAP: claim -> check (anything not listed is CONDITIONAL or OPEN in the README)
| Claim | Status | Check (all run by `verify.sh`; log names in `OUT/logs/`) |
|---|---|---|
| Lemma 6.1 (per-term fitting minrank = mr2 on R∩A) | PROVEN (README §1) | exercised on every `mr2` in `brute_agree`, `d4`, `e7`, `d6`, `e8orth` |
| Lemma 6.2 (normal-pair reduction) | PROVEN (README §1) | consumed by Theorem 6's type enumeration (`orbA`, `orbB`, `cmp`) |
| Lemma 6.3 (orthogonal-set deletion) | PROVEN (README §1) | consumed by Cor 6.4 (P112/P104 scopes); no separate script |
| 440 880 hyperplanes, 4022 non-orthogonal + 318 orthogonal types, min \|D\| = 30 | CHECKED, two implementations | `orbA`, `orbB`, `cmp` (`checks/orbits_a.py`, `orbits_b.py`, `compare_orbits.py`) |
| CNF writers agree with exhaustive minrank over all fitting B | CHECKED | `brute` (`brute_agree.py`: 60 instances, both writers, DRAT + decoded SAT models) |
| Theorem 6: all 4022 types UNSAT at rank <= 8, DRAT VERIFIED | CHECKED | FULL=1 steps `FULL writer A`, `FULL writer B` (`solve_types.py ... chunk:i/4`); default: fixed 32-type sample `solA`, `solB` (14 smallest \|D\| plus 18 spread) |
| E8 >= 72 (every term x·y≠0 has rank >= 9, any fitting B) | PROVEN given Theorem 6 | as above |
| P112 >= 64, P104 >= 56 (floor T·r_min, not per-term dense value) | PROVEN given Theorem 6 + Lemma 6.3 | as above; frames asserted in `dec` |
| D4 >= 12 (192 D-sets, mr2 >= 3) | CHECKED | `d4` (`small.py D4`) |
| Sharp: E8 72, P112 64, P104 56 exact decoders | CHECKED | `dec` (`decoders.py`) |
| E8 orthogonal normals: \|D\| = 24, mr2 = 6 (dense block 9) | CHECKED | `e8orth` (`counter_e8orth.py`) |
| D6: \|D\|=7 mr2=3; \|D\|=10,15,16,19 mr2<=4 (scan \|D\|<=19 only) | CHECKED (default: one witness per size; FULL: complete scan, 240 sets of \|D\|=7) | `d6` (`small.py D6 [full]`) |
| E7: \|D\| = 11 type mr2 = 5 | CHECKED | `e7` (`small.py E7`) |
| No decoder below any floor is shown | SCOPE STATEMENT | README §4 |
| Overcomplete (48 types at 8, 19 undecided), E7/D6 square, gap (ii), D6 shared-B test | OPEN / CONDITIONAL | not checked |
