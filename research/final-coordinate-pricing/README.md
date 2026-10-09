# Price carriers in their final coordinates

Conditional κ = **26395730811851/500000000000000000 = 5.2791461623702×10⁻⁵**, approximately **0.0006927669% above PR95**. Bit saving: **6599281088677/125000000000000000**. Under the inherited analytic and fixed finite-alphabet multitape hypotheses, T(n)=O(n(log n)^(1−κ)).

The h25 carrier oracle now prices transitions in the final PR95 coordinates, including the subsequent PR93 and PR95 relabelings. Previously the producer chose legal carriers using an earlier coordinate order, before the word was relabeled. All choices still pass the unchanged compiler's independence and physical-word checks. The h23 word is PR95's unchanged word.

Roles remain 26,387 and 34,772, with width W=130,417,912 and total recursive rank 74,988,452,500. The gain comes from a different complete internal child profile. All exteriors, early/late restoration gates, copied-center charges and side growth remain paid. The finite bridge and complex layer are unchanged.

This is a small improvement found during a 16-experiment bounded exchange study. No proposed long cycle was accepted. Recompiling with the pristine inherited engine and final coordinate prices must reproduce the selected word byte-for-byte; long-cycle code is not needed for this witness.

```sh
python3 research/final-coordinate-pricing/verify.py
python3 research/final-coordinate-pricing/test_controls.py
# Also regenerate the complete inherited producer chain:
python3 research/final-coordinate-pricing/verify.py --regenerate
make verify
```

Full verification passed on research commit `f07c7db7d1fd378b0deae68e33b53421456319ae` in 6,633.390 seconds, completed 2026-10-09 00:33:40 UTC: `make -j1 verify` (92 isolated test modules and 20 historical patch checks), both parent control suites, complete producer-chain regeneration and six own controls. All 57 research-head GitHub checks passed. There was no source drift. See [validation.json](validation.json) for commands and evidence hashes. The earlier independent focused run also passed in 92.777 seconds.

The certificate checks exact and independent moment enclosures, 47 constraints, seven margins, both next-grid rejections and exclusion of PR95's complete profile at the new saving. See [PROOF.md](PROOF.md) for the general parameter-transfer argument and complete costs. No optimality, new Lean proof or practical speedup is claimed.

Credit Chafik Boukhalfa for PR91's aligned compiler, Maxime Fleury with Codebuff assistance for PR94, Rohan Arun for PR93/95 and coordinate-aware pricing, Alejandro Zarzuelo Urdiales for bounded exchanges, Thomas DiFiore, Dominik Scholz, eumemic, Avi Eisenberg, Rohan Garg, icekylinx, James Chang, Zhihao Chen, Aurel Prosz/Paureel, Swapnil Jain, RaD/hipotures, Douglas Colkitt, OpenAI and all predecessors. Original source and notices are preserved.

Prepared by Rohan Arun with OpenAI Codex assistance.
