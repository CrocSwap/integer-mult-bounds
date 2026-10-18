# Independent complementary-block nullity verification

This package corroborates the **valid local inverse-block argument** in
Douglas Colkitt's `research/kappa-nine/MIXED-RANK-TEST.md`. It uses an
explicit kernel isomorphism in place of the source's Schur calculation and
independently checks the actual six-by-six rational control. The underlying
nullity identity is classical; no new theorem or missing-proof correction
is claimed.

The source matrix has exact block ranks **(2,4,2,4)**. All **4,096** of its
rectangular row/column subblocks pass rational kernel transport, including
empty/full blocks. Separately, all **11,232** invertible three-by-three
matrices over F3 pass **404,352** complementary-block comparisons, using
adjugate inverses and direct minor ranks. Deterministic trace digests and
complete histograms bind both computations.

The precise identity, its field-independent kernel proof, and the local
application are in [PROOF.md](PROOF.md). The inverse block must exchange
the two complements, and unequal block dimensions require a rank offset.
Controls catch both errors and the loss of a required invertibility
hypothesis.

From the repository root, with Python 3.10+ and standard library only:

```sh
python -I -O -B research/complementary-nullity-audit75/verify.py
python -I -O -B research/complementary-nullity-audit75/independent.py
python -I -O -B research/complementary-nullity-audit75/test_package.py
```

Expected lines:

```text
PASS_COMPLEMENTARY_NULLITY_F3 matrices=11232 block_pairs=404352 no_new_kappa
PASS_COMPLEMENTARY_KERNEL_SOURCE block_pairs=4096 ranks=2,4,2,4 no_new_Fano_exclusion
PASS_COMPLEMENTARY_NULLITY_CONTROLS mathematical=8 package=5
```

Add `--write` to either of the first two commands to regenerate its exact
receipt. Normal replay compares every field, preserving JSON scalar types.
The engines share source-pin and literal readers, but neither uses the
predecessor arithmetic; the rational kernel engine does not call the finite
engine's adjugate inverse or minor rank calculations.

[SOURCES.json](SOURCES.json) has an exact required inventory, with text
hashes normalized CRLF to LF. The actual source note, implementation,
control receipt and attribution are pinned at base
`2921874911956718fcaaaf9396fe8267b3cfa9f0`. BASE-SELECTED.json freezes
context without following a future moving selected pointer.

This supplies independent verification of the local algebra and control,
not another Fano exclusion or a new bit/complex supplier. All surviving
global branches stay open. No native, hosted CI, cold supplier or Lean
execution is claimed. Selected kappa and predecessor files are unchanged.
See [VALIDATION.md](VALIDATION.md) and [OVERLAP.json](OVERLAP.json).

Credit: Douglas Colkitt for the source mixed-rank investigation, with its
original OpenAI Codex disclosure. The classical nullity identity is not
claimed as novel. Audit contributor @woklerx with substantial OpenAI Codex
assistance; Apache-2.0 under the repository license.
