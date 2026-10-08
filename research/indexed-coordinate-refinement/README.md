# Coordinate refinement of the indexed two-cycle witness

Conditional **κ = 10454438533673/200000000000000000 = 5.2272192668365e-5**, with bit saving **13068731298371/250000000000000000**. This is approximately **0.00173% above PR #84**, pinned at `88ca39571907343a49e97f328971ec7bcd26fbfd`.

Exchange coordinate labels 3 and 4 (zero-based) in both complete PR84 axis words. The role counts, scalar circuit, XOR count, matching, frame inclusions, width 132466108 and total recursive rank 76166165200 stay the same. The fixed-coordinate residual child-size histograms change. Fresh profiles and exact arithmetic give the improvement; no uncharged operation or smaller assumed width is used.

```sh
python3 research/indexed-coordinate-refinement/verify.py --regenerate
python3 research/indexed-coordinate-refinement/test_controls.py
make verify
```

`verify.py --regenerate` first invokes PR84's complete physical compiler, checks the pinned parent words, then checks the new coordinate words, all arbitrary dirty basis vectors in both orientations, every transition and three-prime profiles. The exact certificate checks both grid exclusions, independent rational moment bounds, all 47 strict constraints and seven margins, and excludes PR84's complete child list at the new saving. Full repository verification passed, including 84 isolated test modules and 20 historical patch checks; see `validation.json` for the source timeline, log hash and corrected-verifier coverage.

The finite search examined identity and every adjacent-coordinate exchange in each axis, 48 proposals total. This is not a global optimality or mathematical priority claim. These bounds retain all inherited analytic, all-size compiler, residual, tape, routing, prime-selection and recovery hypotheses; passing tests does not prove those hypotheses.

See `PROOF.md` for the coordinate transport argument. This refines Chafik Boukhalfa's PR84 construction and builds on Thomas DiFiore's PR74 coordinate relabeling and Rohan Arun's PR78 flag search. All PR84 and earlier contributor credits and preserved licenses remain applicable: eumemic, Rohan Garg, Avi Eisenberg, Dominik Scholz, Alejandro Zarzuelo Urdiales, Chafik Boukhalfa, Thomas DiFiore, Rohan Arun, OpenAI, and all predecessors. Prepared by Rohan Arun with OpenAI Codex assistance.
