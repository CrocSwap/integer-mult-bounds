# Two more staged quartets on PR2863's shared-kernel words

**Conditional κ = 0.001720184528377469533074 − 10⁻⁴⁶ − 10⁻⁷⁰** (exact in `CLAIM.json`): +8.37229605836×10⁻⁸ over PR2875, over PR2863 and +8.790×10⁻⁸ over PR2857.

**Credit first:** PR2863 (Dugongue), PR2857 / PR2848 (Lyy-iiis), PR2843 (mdumitrean), PR2853 (philippeVV). **Ours** (Jeremy Kothe, jeremykothe2, with AI assistance): the two extra staged quartets via preload re-synthesis, and the residue-free T74 fill. See `CREDITS.md`, `CONSTRUCTION.md`.

Paid profile per call {1:2404, 2:642, 3:262, 4:128, 5:26, 8:8}, inventory {4:26, 5:2, 7:62, 8:86, 9:232}; fill profile {1:1618380, 2:427572, 3:180819, 4:85248, 5:25863, 8:5328, 48:26825} over 74 replicas.

Fast check (standard library): `python -B tools/verify_package.py --work <fresh dir>`. Full replay: `reproduce.py --source <PR2833 source from tools/materialize_source.py> --work <fresh dir>` (fresh retained bootstrap, declared stage with independent review, two fresh native chains, complete admission, outer release); `verify_release.py` runs everything. On Windows `reproduce.py` gives its subprocesses an LF `Path.write_text`.

Scope: conditional; inherited all-size hypotheses remain; no optimality certificate for the new inventory; the fill is a literal solver output. Evidence of the recorded run is in `evidence/`; `evidence/pr2863/` is the inherited predecessor record.
