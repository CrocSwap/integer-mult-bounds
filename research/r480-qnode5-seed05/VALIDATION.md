# Verification record

Environment: CPython **3.12.14**, Windows 11, standard library only for the new package and all three invoked inherited Python checks. Base and refreshed origin/main both **`abdc6a7002abdbcd9e21bfc5e1a795784deacfdf`**. No consumed dependency or selected-record change was found on refresh.

Completed commands from the repository root:

```sh
python3 -I -B research/r480-qnode5-seed05/search.py
python3 -I -B research/r480-qnode5-seed05/verify.py --replay-search
python3 -I -B research/r480-qnode5-seed05/test_package.py
python3 -B scripts/verify_selected_result.py
python3 -B -m unittest discover -s tests -p test_selected_result.py
git diff --cached --check
```

The search completed 2,000 trajectories; 9 candidates were fully priced; two had 41 gates; trial 1897 won by the specified complete-payload tie-break. Regeneration matches `CANDIDATE.json` byte for byte (SHA-256 `ca8cd1ad1911815db7ac7c90800c46b99f650916ba519f6d5ff2fbeb5f4c08e2`). This is completed coverage of that deterministic heuristic, not exhaustive coverage of all circuits.

The independent verifier passes the complete exact certificate: 4,096 block inputs; 720 arbitrary-dirt columns; complete ADDs 33,958 -> 33,938; rank mass 5,592; all 720 per-register frame paths; full positive payload 102 bits; 5/9/11-stage finite scalar schedules on both words; 93 rejected controls. The reference xcheck validates 120 E8 labels and all 672 closed frames, original H1-H5 and U/J/K/restoration conclusions. The PR425 checker passes unchanged. Independently reconstructed literal raw records equal the unchanged exporter byte for byte.

Five package test groups pass, including a minimal relocated checkout under `python -I -O -B`, complete search regeneration, and adversarial source/candidate corruption rejected with optimization enabled. Five selected-record test groups pass and the accepted kappa remains unchanged. The new verifier uses explicit exceptions for acceptance conditions, so optimization cannot erase them; inherited assertion-based checkers run in unoptimized subprocesses.

A development test exposed that Python's integer histogram keys were compared with JSON's string keys. This caused a safe certificate-drift rejection, not a false acceptance. Report keys were canonicalized and the complete normal and relocated/optimized runs were repeated successfully. No failed receipt was edited into a pass.

Final staging exposed Windows text-mode CRLF output in the witness generator. Output is now explicitly LF, the witness SHA pin is updated to those portable bytes, and a minimal checkout reconstructed from the exact Git index (18 files) passes complete verification and byte-identical search regeneration. The frozen input files are copied from their exact staged blobs; no line-ending relaxation is used in acceptance.

`make verify` was attempted once and could not start: **`make` is not installed/on PATH**. No C++ compiler was available on PATH, so the native C++ legality/5/9/11-stage executables were not built or run. The corresponding finite schedule rule is pinned and replayed by the new Python engine; this does not imply a native, repository-wide, remote CI, hosted-parent, selected-frontier cold replay, or full theorem pass. No selected construction or shared generator was changed, and no unrelated artifacts were regenerated.

Final metadata was refreshed through open PR **#1086**. All-state R480 results still include PR1003's Q-node2 and PR1027's quad12; their heads are unchanged. The explicit `Q-node5` query had zero results. The quoted `Q-node 5` query returned unrelated PR5 (a GitHub search tokenization false positive), which is not treated as evidence of circuit overlap. [OVERLAP.json](OVERLAP.json) preserves the concrete query/results snapshot. No priority, newest-record, or best-known-circuit claim is made.

The final quarter of the actual work is reserved for verification, refresh and handoff. The local claim will be updated once with the submitted result and PR link. Contributor and AI-assistance disclosure are in README/CLAIM. New files are Apache-2.0.
