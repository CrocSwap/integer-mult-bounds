# Congruent splits with geometric prices and null-circuit clearing

**Conditional κ = 26222540409037/500000000000000000 = 5.2445080818074×10⁻⁵**, approximately **0.0250% above PR87**. Bit saving: 52447831448991/10^18.

Compose @gupt1156's PR87 congruent `[4,4,1]` split patterns on both axes with PR86's final-coordinate oracle prices, inherited PR75 null-circuit clearing, and bounded two/three-carrier exchanges. All physical operations and endpoint corrections remain paid. Roles are **26695 at h23 and 35132 at h25**, versus PR87's 26705/35137.

All eight cloud experiments passed. Exact complete-profile comparison included their 25 pairings and the independent 48 coordinate-only proposals. The selected pair is a finite search result, not a global optimum or an exact weighted-matching claim.

## Validation

Both cloud words passed scalar checks, arbitrary-dirty physical replay in both orientations, fresh CRT profiles, independent exact moments, next-grid rejection, 47 constraints and seven margins. Independent local compiler regeneration and nine focused controls passed. Full `make -j1 verify`, both inherited and new compiler regenerations, seven inherited controls and nine new controls passed on research commit `b2df9de3147006cb6a652e5409ce2f44bbd71926` in 3367.923 seconds (56 minutes 8 seconds), including 84 isolated test modules and 20 historical patch checks. The checkout had no source drift; all 48 GitHub checks passed on that research commit. See [validation.json](validation.json) for timings, commands and evidence hashes. Only this validation documentation and receipt changed afterwards.

```sh
python3 research/congruent-geometric-pricing/verify.py --regenerate
python3 research/congruent-geometric-pricing/test_controls.py
make verify
```

The package retains all inherited analytic, uniform compiler and fixed finite-alphabet multitape hypotheses. It is not an unconditional multiplication theorem or a measured practical speedup.

## Attribution

@gupt1156 (#87 congruent split patterns); Chafik Boukhalfa (#84 indexed compiler); Rohan Arun (#86 coordinate-aware prices and bounded carrier cycles); the preserved PR75 null-circuit implementation; Thomas DiFiore (#74), eumemic, Dominik Scholz, Rohan Gupta, Alejandro Zu, icekylinx, James Chang, Zhihao Chen, Aurel Prosz/Paureel, Swapnil Jain, Avi Eisenberg, RaD/hipotures, Douglas Colkitt, OpenAI and all predecessors. Original licenses, sources and AI-assistance notices are retained.

Prepared by Rohan Arun with OpenAI Codex assistance.
