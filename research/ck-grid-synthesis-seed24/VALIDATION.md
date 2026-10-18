# Validation and handoff

2026-10-13, macOS, bundled CPython 3.12.14, standard library only.
Base `ba82555c64e1879e4b7decce28186f208fcb8262`.

Passed:

```sh
python3 -B -I research/ck-grid-synthesis-seed24/verify.py --write-certificate
python3 -B -I -O research/ck-grid-synthesis-seed24/verify.py
python3 -B -I research/ck-grid-synthesis-seed24/independent.py
python3 -B -I -O research/ck-grid-synthesis-seed24/test_package.py
```

- Both complete literal primitive streams, all 725 formal columns, exact
  endpoints, 492 restored helpers, private cleanup and unchanged paid profiles.
- All 103 magnitudes, 16,251 graph vertices and 96,929 labelled edges; separate
  BFS and synchronous Bellman engines agree on every distance and signed witness.
- Nine graph and six macro controls; two complete-word controls reject a wrong
  target sign and omitted work clear; two admission controls reject altered
  source semantics and an understated certificate cost. Gzip repackaging passes.
- Isolated optimized replay from a minimal offline relocated checkout whose
  path contains spaces, invoked from a different working directory, passes.
- Current selected certificate SHA256 and exact kappa agree with the record.
  This small check is explicitly **not** the complete selected-record source
  inventory check; the sparse research checkout omits unrelated packages.
- Staged whitespace and one-package scope checked before commit.

No new dependency, native supplier regeneration, complete selected cold replay,
full repository suite, hosted CI, Lean or physical runtime benchmark was run.
Those passes are not claimed. The prefix/grid claim combines exact local macro
checks with the written substitution argument and reconstructed pinned original
envelopes; it is not an independent full physical precision certificate.

The immediate overlap refresh through PR1113 is recorded in OVERLAP.json.
The closest input/comparison heads remained unchanged. No pinned coordination
issue existed. A local claim result will record the single published PR link.
