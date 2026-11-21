# GIBBS8 (Nov 20, Sonnet lane): mod-8 Gibbs/SA search for a quarter counter-decoder to the MERGEROWS level-1 bound
Differs from TAU gibbs.py (mod 4, measures rho) and MERGEROWS (Gram class only): exact Z/8 resampling of one port row of W or V, then nf.py normal form + gauge climb of alpha+beta.
Model [C]: W,V n x m residues mod 8, (W V^T) o Q = 4 I mod 8 (DEN4 quarter validity), checked after every burst. Support of a column = nonzero residues (relaxation: C_mod8 <= any lift's C).
Lift to rationals w = W col, u = V col / 4: sum w u = I mod 2 on Q-cells, which is all that alpha+beta <= C(NF) needs (G00 = 0 for e' >= 1). m5's pipeline runs on the lift (exact check replaced by the mod-2 check).
Move: pick port t, side, column subset J (|J| 2..m), solve A x = c over Z/8 exactly (Smith-type solver, uniform over the coset), draw K candidates, pick by Boltzmann(-beta dC) (beta 0.5..5). SA on screened NF-S1 (gauge climb 300 x 1 seed; full 800 x 2 if < thr+3), C-cap per run.
Starts: HS64 D8-frame (C 48, m 8), E7 decoders m3_E7s_3_{1,9,13,21,25} (C 49, m 7; only e<=2 decoders embed in mod 8); also m padded by 2-4 zero columns and random GL_m(Z/8) mixing, and a dense random-GL start.
Files: g8lib.py (solver, Dec, lift, pipeline), g8run.py (driver), summ.py, run_*.log (one line per eval), batch{1,2,3}.sh.

## Result [C]: 10,974 NF-pipeline evaluations (HS64 4,852; E7 6,122), 24 runs x 240 s, 1 process, threads=1 (~1.7 CPU-h)
| set | thr | min C seen | min NF S1 | S1 percentiles (0/5/25/50/75%) | closest approach |
|---|---|---|---|---|---|
| HS64 | 38 | 48 (the start; 0 states below) | 42 | 42/42/44/48/56 | 42 at C=48 (400 visits), 43 at C=50..54, 44 at C=58 (m=10) |
| E7   | 41 | 49 | 49 | 49 everywhere | S1 = C(NF) on every one of 6,122 states (C-S1 slack 0): all-saturated after NF |
- Counter-decoders to the merge route (NF S1 < thr): NONE. C below thr: NONE (so nothing LOUD).
- HS64: slack C - S1 >= 6 in every state (min at the optimal frame 48 vs 42). Moves away from C=48 only raise C and S1 together (50-54 -> 43; dense saturated C=64 -> 56, which NF merges into one 8-class).
- E7: every reachable state (incl. m=9,10 padded and mixed) normal-forms to the saturated 7-class; S1 = C >= 49.
- Dense random GL starts do not descend (stay C=64 / S1=56 for HS64, C=62-69 for E7 padded); the cost-tilted Gibbs cannot find sparse structure from dense. Evidence is therefore about the neighbourhood of the optimal (and near-optimal) decoders, not the whole mod-8 space.
## Scope / caveats
- Only decoders with e <= 2 embed (the e=3..6 MERGEROWS lows are out of the mod-8 model). E7+A1 not run (h=7 same label rank; the A1 port has an all-ones Q row; S1(E7+A1) >= S1(E7) is not tested here).
- Relaxed object (M = I mod 2 only, zero residues = absent): a flag there would still need a lift to an exact decoder; none occurred, so moot.
- Chains were adversarial only through screened NF-S1 (SA T 1-6); no cap-free run (dense states are all-saturated => trivial by MERGEROWS (f)).
## Next
- Chains stay in the orbit of the C=48 frame (S1 42 plateau). A real rigid-low search needs structured proposals that keep unsaturated rows with distinct supports (e.g. moves that swap supports between rows) rather than coset resampling; or a mod-16 sampler to reach the e=3..6 lows.
