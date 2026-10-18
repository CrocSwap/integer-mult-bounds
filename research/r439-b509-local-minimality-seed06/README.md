# R439 frame 509: exact local ADD minimum

**Scoped optimality proof; no new κ.** For the fixed four-register Boolean endpoint used by Hanson's PR #1221, the minimum is exactly three scalar ADDs in the one-destination model. The PR #1221 witness attains the lower bound. Concurrent PR #1344 independently verifies the same maps and full splice, but does not claim local minimality. This package adds only the local minimum and shortest-word classification; it does not duplicate that splice replay, certify the minimum cost of the full frame-509 block, or change the selected supplier.

The destination lower bound is support-independent: the block endpoint changes three distinct output registers, while each scalar ADD writes one destination. An exact four-register census gives a separate reproducible check: among the 12 directed CNOT gates there are 1, 12, 97 and 626 distinct maps at lengths 0, 1, 2 and 3, respectively; the target has no representative below length 3 and exactly three length-3 words.

## Reproduce

From the repository root, with Python 3.12 or later and the standard library:

```sh
python3 -I -O -B research/r439-b509-local-minimality-seed06/verify.py
python3 -I -O -B research/r439-b509-local-minimality-seed06/test_package.py -v
```

Expected verifier marker:

```text
PASS_R439_B509_LOCAL_MINIMALITY minimum=3 length3_words=3 maps=1,12,97,626 boolean_inputs=16 integer_delta=2e_h_e_a no_new_kappa
```

The registered package check is:

```sh
python3 scripts/research_package.py --package research/r439-b509-local-minimality-seed06 --check-only
```

Expected: `PASS_PACKAGE_METADATA_AND_PINS (not a mathematical acceptance check)`. Local replay used Python 3.14.7. The package's registered Python 3.12 replay was not run locally because Python 3.12 is not installed in this environment.

The proof and exact scope are in [PROOF.md](PROOF.md). [TASK.json](TASK.json) records the catalogue scope change; [SELECTION.md](SELECTION.md) records the three alternatives and live overlap decision. Base inputs are pinned in [SOURCES.json](SOURCES.json); the open predecessor is pinned separately in [PREDECESSORS.json](PREDECESSORS.json).

The package does not replay PR #1221's full word, rerun the selected cold replay, or claim H1–H5 admission, hosted adoption, a changed paid profile or a new κ. The current selected conditional result remains κ = `836330098538459/500000000000000000`; the complex supplier binds.

## Open next questions

- **Question:** Is the full post-splice 20-ADD frame-509 block minimum under the original 11-register integer-add model?
- **Why it matters:** That would distinguish a local Boolean cancellation floor from a lower bound on further improvements to the selected bit word's full block.
- **First step:** Extract and pin the exact 11-by-11 integer block map, then prove a destination/support lower bound before considering a bounded factorization search.
- **Blocked by:** The four-register endpoint proved here does not cover rewrites that change other block coordinates or use a different boundary map.

## Credit and disclosure

Credit Hanson Sun (@bbMisk), PR #1221, for the three-ADD witness; Cinna Davis (@1337isnot1337), PR #973, for the 21-ADD parent; DreamingOfClouds, PR #589; and eumemic, PR #555, for the selected R439 supplier. This package was prepared with substantial OpenAI Codex assistance; no human independent review is claimed. New work is Apache-2.0.
