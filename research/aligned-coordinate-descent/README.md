# Coordinate descent beyond PR93 and PR94

Conditional **κ = 329944349403/6250000000000000 = 5.279109590448e-5**, bit saving **52793882951577/10^18**. The gain over PR94 is about **0.000299%**; this is a small finite refinement, not a breakthrough or practical speedup.

Starting with PR93's complete physical words, reverse final coordinates 0 through 3 at h23 and swap 5/6 at h25. Roles 26,387/34,772, physical width 130,417,912 and total rank 74,988,452,500 are unchanged. All slot operations, XORs, copy/cleanup costs and inherited data-growth costs stay paid; every frame/source/output/scatter label moves consistently.

The 32 bounded Daytona workers tried four move families (swaps, three-cycles, interval reversals and coordinate insertion), four seeds each in two dimensions, with 16 greedy proposals per worker. Numerical scores chose candidates. Complete selected physical profiles were then combined in 289 exact paid comparisons including the parent. This is not a global optimum claim.

```sh
python3 research/aligned-coordinate-descent/verify.py --regenerate
python3 research/aligned-coordinate-descent/test_controls.py
make verify
```

The verifier independently regenerates the parent chain, replays all selected dirty basis columns in both orientations, freshly profiles complete transitions, checks independent rational moment bounds, both next-grid exclusions, 47 strict constraints and seven margins, and excludes PR93 and PR94 complete paid profiles at the new saving. PR94's arithmetic bound is independently reproduced; its producer is not recompiled. Full repository verification passed on research commit `ea640ec01daf16ebe9d3d0a6ca9e47bd7f8b7dd8`: 92 isolated test modules, 20 historical patch checks, parent and own six-control suites, and fresh complete producer/profile regeneration. All 54 GitHub checks passed on that commit. See `validation.json` for timing and evidence hashes. Six controls test invalid/inverse coordinate maps, omitted charges, stale bridge/exponent, serialization and disabled assertions.

This remains conditional on inherited analytic, all-size ordered residual compilation, routing, scalar overhead, prime selection, recovery and fixed-tape hypotheses. The inherited Lean certificate concerns the older PR91 exponent; no new Lean certificate is claimed.

Credit Maxime Fleury with Codebuff assistance for PR94's independently discovered h25 refinement; Chafik Boukhalfa PR91, Thomas DiFiore PR74, Rohan Arun PR78/85/93, eumemic, Rohan Garg, Avi Eisenberg, Dominik Scholz, Alejandro Zarzuelo Urdiales, and all inherited contributors and OpenAI. Preserved licenses and assistance disclosures remain applicable. Prepared by Rohan Arun with OpenAI Codex assistance.
