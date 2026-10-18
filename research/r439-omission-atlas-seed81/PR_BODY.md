PR967's restored-helper D circuit has 5,563 elementary ADDs. This independent finite census replays every single-ADD omission on all 661 symbolic input columns and verifies a separately computed prefix/suffix rank-one fault formula. Every full-boundary syndrome is nonzero and distinct, while target-only observation misses exactly the 221 final helper restorations. The certificate includes an explicit singleton input and changed helper outputs for every missed fault. All ones alone misses 1,522 omissions.

Reproduce from repository root:

```sh
python -I -B research/r439-omission-atlas-seed81/verify.py
```

Expected: `PASS_R439_OMISSION_ATLAS gates=5563 target_invisible=221 unique=5563 controls=7 no_new_kappa`.

The package pins exactly two consumed predecessor inputs, compares the complete baseline D matrix with PR589, rejects seven controls and canonical certificate drift, and imports no predecessor code. It credits PR967's already verified construction, PR589's supplier, and PR762's earlier R420 coefficient-fault testing work. This is a complete census only for one omitted elementary ADD in the frozen D phase. It does not claim a new circuit, new kappa, a defect in PR967's full-boundary checks, multi-fault coverage, native/whole-word validation or unrestricted fault tolerance.

Prepared for @woklerx with substantial OpenAI Codex assistance. New files are Apache-2.0 and confined to research/r439-omission-atlas-seed81/.
