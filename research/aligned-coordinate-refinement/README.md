# Coordinate refinement of aligned frame composition

Conditional **κ = 13197726684911/250000000000000000 = 5.2790906739644e-5**, with bit saving **52793693766767/10^18**. This is approximately **0.002443% above PR #91**, pinned at `264f202b52edc04d0c72ca9cb3138282ca68b9ad`.

Swap final coordinate labels 5 and 6 in the complete h23 word, and 22 and 23 in h25 (zero-based). This keeps PR91's role counts 26,387 and 34,772, all physical slot operations, XOR counts and width W=130,417,912. It improves the residual child-size distributions after fresh profiling. The total recursive rank remains 74,988,452,500.

```sh
python3 research/aligned-coordinate-refinement/verify.py --regenerate
python3 research/aligned-coordinate-refinement/test_controls.py
make verify
```

The verifier independently regenerates both PR91 compiler words, checks canonical byte equality, transports every coordinate label, replays arbitrary dirty basis columns in both orientations and regenerates complete CRT profiles. Exact rational moment bounds, independent enclosures, both next-grid exclusions, 47 strict constraints and seven margins are required. PR91's complete child list is excluded at the new bit saving. Source manifests pin all inherited artifacts and local inputs.

Full repository verification remains pending. The inherited Lean companion certifies PR91's arithmetic; it is not a Lean certificate of this new exponent. This package checks its new arithmetic with exact Python rational enclosures.

The discovery scan considered identity and every adjacent transposition in both axes, 48 finite candidates. It proves no global optimum. All inherited analytic, ordered residual compiler, all-size recursion, scalar overhead, routing, prime-selection, recovery and finite-alphabet multitape hypotheses remain assumed. See PROOF.md for the coordinate transport and complete paid-cost argument.

Credit Chafik Boukhalfa's PR91 aligned composition, Thomas DiFiore's PR74 coordinate construction, Rohan Arun's PR78/85 flag refinement and all inherited contributors, including eumemic, Rohan Garg, Avi Eisenberg, Dominik Scholz, Alejandro Zarzuelo Urdiales, icekylinx, James Chang, Zhihao Chen, Aurel Prosz/Paureel, Swapnil Jain, RaD/hipotures, Douglas Colkitt, OpenAI and predecessors. Prepared by Rohan Arun with OpenAI Codex assistance. Preserved third-party code retains its original licenses.
