# Cube recurrence with balanced core pairs and deferred readouts

Conditional κ = **49349675169/500000000000000 = 9.8699350338×10⁻⁵**, approximately **4.17409% above PR114** (9.4744627892×10⁻⁵). The strict complex saving is 98718939/10¹²; the retained stopped bit saving is 1240189553/10¹³.

This composes icekylinx's PR115 pair-first cube recurrence with eumemic's PR114 balanced core-aware pair subproblems, Rohan Arun's PR111 dual-suffix pair stars, and Avi Eisenberg's PR110 lifted/deferred compiler. The cube recurrence replaces the entire triple-exclusion recurrence. Its outputs are assembled from the same disjoint coefficient partitions, so the existing producer checks all scalar supports and frame inclusions. The selected circuit has 70,252 additions, 8,120 roots, 42,694 legal matched carriers, 35,678 roles and 4,909 deferred roles. PR114 has 37,859 roles; a smaller role count alone is not used to claim improvement.

The bit supplier is unchanged. All copied-center transforms, auxiliary exteriors, source and target fronts, data residuals, endpoint corrections, scalar work and three row reserves remain paid. In particular, this retains PR114's conservative expanded-readout scalar charge. The complete complex histogram and exact moments determine the comparison.

The implementation deliberately preserves the tested producer's two construction phases: the initial CubeTriple output construction uses PR114 core-pair/vector overrides; after the overrides are removed, the retained center outputs use the inherited CubeTriple/IntervalTriple methods. Both sets of selected roots are checked together by the complete scalar and frame compiler.

```sh
python3 research/cube-deferred/verify.py
make verify
```

Full verification passed on research commit `97750ec74fc714638c0aa4f31aaa880e56cb8b4d`: `make -j1 verify`, package verification and 14 controls completed in 3733.46 seconds with no source drift. All 42 GitHub checks on that research commit passed. See [validation.json](validation.json) for commands, log/archive hashes and scope. The inherited general interfaces remain conditional. No claim of an unconditional theorem, global optimality or measured runtime improvement is made.

See [PROOF.md](PROOF.md). Credits: icekylinx (PR115 cube recurrence; PR104 stopped products), eumemic (PR114 balanced core pairs, independent reflection verifier and conservative scalar accounting), Avi Eisenberg/ikeboy (PR62/110 primitives and deferred compiler, Claude assistance), Rohan Gupta/gupt1156 (PR55 dual-suffix identity), Rohan Arun (PR111/113, Claude assistance), Swapnil Jain (frozen round-seven deferred bit word), Zhihao Chen/jacklightChen, RaD/hipotures, Aurel Prosz/Paureel, Douglas Colkitt, OpenAI and all inherited contributors. Imported Apache-2.0 code retains original notices. This integration was prepared by Rohan Arun with OpenAI Codex assistance.
