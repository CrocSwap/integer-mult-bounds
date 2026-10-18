# S2 report: cheaper decoder on the E8 unit (stopped early, budget)

Work dir: $SP/s2/work (scripts; python = $SP/venv/bin/python). No package/verify.sh written yet. No kappa claim.

## Results (own runs, exact unless noted)
1. **P111 (shipped bit puncture 39,52,57,71,76,78,103,109,114): 9-total F2 decoder unique (= B0|live) and c=8 UNSAT** (CaDiCaL, no proof log). `uniq.py <P>` -> `uniq111.log`. So every 9-total decoder on P111 is a label decoder.
2. **Theorem C floor = star floor on the realised units (label-decoder family, any number of totals):**
   - P120 bit: all 511 reader sets R(p) span Q^8 (`t1.py`), so every 9-total decoder costs exactly 72 under pairing rank (= star).
   - P111 bit: 9 deficient functionals (the punctured labels); pair costs 6 (44 ordered orthogonal punctured pairs), 7, 8 (`p111c.py`). Exact SAT over all decompositions I_9 = sum p_j q_j^T (n<=10 suffices for cost<=62): **cost <= 62 infeasible** (all cost-62 type combos UNSAT; calibration at 63 SAT) (`run62.py <P> 62|63`, `dec9sat.py`). Theorem C min = 63 = star; no slack.
   - P112 complex, frame decoder: ThmC 64 = star 64 (`cxp.py`; 2025 frames enumerated).
   - Slack mechanism identified: bit side only when a total's readers lie in a hyperplane (drop to g = <y_a>, cost 6 for orthogonal punctured pairs); complex side also via degenerate source spans. Realizability caveats: reader frame chains, copy terminal frame g != 0 (restoration), (B2) common cut.
   - Random search over other 9-line punctures for ThmC <= 62: 1 tested before stop, none found (`search62.py`).
3. **Deep punctures with label (bit) decoders:** SA over p=9..26 (star, `sa_bit.py`) never below cst 63 (x 63/111 best). Sub-root-system units (`subsys.py`): D8 57/56, E7+A1 50/64, A8 63/36 etc. — all far worse; label decoders degrade with depth. Not an exhaustive result.
4. **Mixed units (bit, non-root Q-label):** hyperplane census by type (`hyper.py`, exact W(E8) orbits: E7 120, D7 1080, E6+A1 3360, A7 8640; 8 types). Adding a non-root port needs >= 14 punctured lines (`addports.py`, sampled normals); D8-axis construction (`mixed_d8.py`) gives x >= 0.67. No gain.
5. **Asymmetric sinks (complex P112):** no free sink relaxation (0 of 28,560 (t,w) pairs, float rank; `asym.py`). Rank-1 shared extra total reproduces C.6 (2 sinks / copy unit, `asym2.py`); per-target two-hyperplane covers abundant (target 75: 263,014 covers, 146 sinks, `covers.py`). Local search for >2 targets per rank-1 total (`asym_ls.py`) stopped without improvement over 2. Pricing: break-even needs (sinks/unit) x (helpers/sink) >= ~20 at 0.14% b; with 2 sinks/unit and <= 4.4 shipped helpers per target (496/112), max ~1.2% b vs 2.82% cost -> net negative (argued, optimistic bound).
6. SAT for 10-total P120 decoders with >=9 E7-hyperplane-cheap totals (`sat_cheap.py 10 1|0`): unresolved after ~40 min, killed.

## Next steps to resume
- Run `search62.py` over many 9-line (and 10-12 line) punctures; if any ThmC<=62 found, build explicit drop-to-<y_a> copy tree and check chain/restoration.
- Finish asym rank-1/rank-r group search (vectorise node enumeration) to bound sinks per copy unit.
- Package: README table + verify.sh from the scripts above.
