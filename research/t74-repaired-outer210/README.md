# T74 repaired outer210 finite witness

Conditional kappa is given exactly in CLAIM.json. This is an arithmetic-only refinement of PR1536: 82 bootstrap steps, eta=beta=10^-220, target backoff10^-223 and final grid10^-210. The 1e-200 native/conservative endpoints and all physical words, owners, paid profiles, invoices and supplier interfaces are unchanged. This is not a practical speedup or new multiplication algorithm.

From the repository root, with Python3.14, NumPy and SymPy available:

```sh
python -B research/t74-repaired-outer210/verify.py --work /path/to/new/output
```

The default runs the complete immutable PR1536 verifier with fresh native providers. Optional `--base-native-from` and `--extra-native-from` accept completed source-bound native directories through the parent's unchanged validation. The verifier then independently derives both positive-margin outer witnesses, recomputes both repaired exact moment engines, checks all 47 strict inequalities and adjacent-grid rejection, and calls the unchanged original strict assembly on the actual new owner/invoice receipts. The retained independent closed-form checker rejects five mutations. Assertions are required. No discovery mode or weakened predicate is used. Source and package manifests are checked before and after.

The corrected fine Mercator engine sums 830 even terms. The parent's independent exact atanh oracle checks76 inputs/152 enclosures and is mandatory. The historical odd-term bug is credited to philippeVV/PR1519; PR1536's repair and oracle are retained unchanged.

Contributor: dataisfire. Substantial OpenAI Codex assistance in search, derivation, implementation, verification and prose. Credit Jeremy Kothe / PR1536 and PR1519's finding; Rohan Arun / PR1485's checker and PR1424/1319/1297/1286; Jeremy Kothe / PR1274; Jeremy Diviney / PR1193; Thomas DiFiore / PR1148; Hao Yan, eumemic, icekylinx/Zhihao Chen, DreamingOfClouds and every retained supplier predecessor in the parent package. Existing techniques are applied, not claimed as new inventions. New files are Apache-2.0. The copied checker changes only its prior-SPEC input location; all checking logic is retained.

Conditional finite construction only. Compiler/all-size, common-label/mutable-source, whole-call hosting, precision/tape, recovery, analytic-transfer, PR559 and PR589 H1-H5 obligations remain. No unconditional theorem, full Lean proof, independent human review or global optimum is claimed. Hosted CI is separate.

Open next questions: change the fully admitted paid profile or decoder; further digit refinements have negligible mathematical headroom for this fixed primitive. The P111 early-merge pilot still needs a complete compensated decoder, temporary lifetime charges, phases and hosting before adoption.
