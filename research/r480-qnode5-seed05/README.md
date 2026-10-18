# Finite R480 Q-node 5 construction (no new kappa)

The historical PR503/510 R480 word's zero-based Q-node **5**, frame **487**, has a **41-XOR** fixed-output replacement for its original **51-XOR** circuit. Rebuilding the required literal reverse cleanup reduces complete local ADDs from **33,958 to 33,938**. The twelve source registers, all 480 arbitrary dirty helpers, all 720 register frame paths, nine COPY/ERASE pairs and paid recursive profile are preserved. This package is a finite bit-circuit construction, not a selected supplier or a new exponent claim.

| Complete local quantity | Frozen original | Replacement |
|---|---:|---:|
| Q-node XORs | 51 | 41 |
| ADDs including cleanup and scatter | 33,958 | 33,938 |
| Forward positive bound F | 176,135 | 176,135 |
| Reverse positive bound B | 3,751,204 | 3,714,396 |
| `64 F^3 B^2` bit length | 102 | 102 |
| Paid rank mass | 5,592 | 5,592 |

The paid histogram remains `{1:1200, 2:1440, 4:180, 6:120, 8:9}`. The replacement preserves the full Boolean map on each physical output register; **positive integer-transfer equality with the original is not asserted**. The complete chronological precision bound, rather than a local gate-count comparison, admits the replacement under the inherited strict `64 F^3 B^2 < 2^104` rule. [PROOF.md](PROOF.md) explains the finite substitution and its limits.

## Reproduction

From the repository root, with Python 3.11+ and its standard library:

```sh
python3 -I -B research/r480-qnode5-seed05/verify.py --replay-search
```

Expected final line:

```text
PASS_R480_QNODE5_SEED05 gates=51->41 ADDs=33958->33938 columns=720 payload_bits=102 controls=93 rank_mass=5592 no_new_kappa
```

The command verifies source pins and the exact certificate, regenerates the bounded search into a temporary file, compares its bytes with `CANDIDATE.json`, and runs the pinned inherited checkers unchanged. `--output /absolute/path/outside/package` retains the rebuilt word, literal raw records, checker logs and report. Without it, a temporary output directory is created. Generated gzip containers are compared through canonical decompressed word content; the committed source gzip is an immutable input and has an exact SHA-256 pin.

Validation covers all **4,096 Boolean block inputs** and their inverse, a signed integer forward/inverse identity for the replacement alone, complete **720-column arbitrary-dirt** endpoints by a new set-valued engine and the inherited `xcheck_p.py`, every frame climb and paid rank, byte-identical raw records against the unchanged exporter, H1-H5 and PR425 hypotheses, and literal **5/9/11-stage** Boolean scalar schedules on both words (**960/1,440/1,680 columns**). The 93 controls reject all 41 single-gate omissions, a bad frame, missing dirt compensation, endpoint-valid stale cleanup, endpoint-valid precision overflow, and all 48 candidate bridge omissions. This new Python schedule implementation follows the pinned C++ rule; native C++ execution is **not** claimed.

## Search domain and completed coverage

Assignment seed **5** was drawn once from OS randomness, selecting the bit-supplier track and zero-based object 5. The search fixes twelve registers and all twelve ordered output values. It runs exactly **2,000** trajectories with `random.Random(2026101305)`, using strictly weight-decreasing left/right Boolean eliminations, randomized sparse pivot choices, and paid three-XOR permutation repair. Trial **1897** supplies the selected precision-admitted 41-gate program; two 41-gate programs were encountered. The complete gate-count histogram and number of priced candidates are in `CANDIDATE.json`. Selection is by gate count, then full precision payload, then lexicographic program order. There is no early success stop.

This is a bounded heuristic in a specified class, not an exhaustive search of all XOR circuits. It proves neither that 41 gates are minimal nor that a better supplier is impossible. No previously exhausted selected-profile search is reopened.

## Pins, overlap and attribution

Exact base: **`abdc6a7002abdbcd9e21bfc5e1a795784deacfdf`**. The consumed source word, unchanged checker/exporter sources, precision/schedule reference sources and selected record are bound in [SOURCES.json](SOURCES.json). Exact witness and finite receipt are [CANDIDATE.json](CANDIDATE.json) and [CERTIFICATE.json](CERTIFICATE.json). The selected record at this base remains Jonathan Capalbo's #942 conditional **kappa 0.001661960547713947**, with DreamingOfClouds' unchanged #589 bit supplier on eumemic's #555.

Credit eumemic for PR493's mutable-source skeleton; DreamingOfClouds for PR503/510's R480 totals/hosting and PR589; Dylan Crow for the literal record/export and formal-column contracts; DaysSky for PR363's bridged schedule; Zhihao Chen for PR425's mutable-source interface; and the retained E8 construction lineage. Jeffrey Cox's PR754 and Hao Yan's PR823 precede local circuit resynthesis. ToikY's pending **PR1003**, head **`b0eda846c34413dabd1e75402b8ad730f8940ff2`**, already establishes a 52-to-43 Q-node **2** replacement and the complete-prefix admission precedent; its implementation is not imported. PR1027, head `ebc027e26a7018b73a5a452eae269a9bfeaabce9`, concerns **quad12** integer-transfer minima. This contribution adds another object, its witness and independent finite evidence; their savings are not composed. The overlap search and local claim are recorded in [CLAIM.md](CLAIM.md).

Prepared for **@martinxxx9** with substantial **OpenAI Codex assistance** in mathematics, implementation, verification and writing. The search and verifier were written separately by the same AI agent; no separate-agent or independent human peer review is claimed. New material is **Apache-2.0**, under the repository license; predecessor notices and sources remain unchanged.

## Remaining obligations

No selected-record edit, whole-hosted parent invoice, supplier binding, moment-root improvement, outer assembly, native C++ run, Lean proof, remote CI pass or measured multiplication speedup is claimed. A full hosted adoption and assembly would be separate work. All inherited all-size/compiler, common-label and mutable-source realization, correlated whole-call hosting, physical projector/routing, precision/tape/recovery and analytic assumptions remain. Finite replay is not formal verification of the multiplication theorem. `upstream/` and all consumed predecessor packages are unchanged.
