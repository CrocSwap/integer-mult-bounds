# Independent exact audit of the P112 off-pattern two-sink unit

**Research note / independent verification. No new κ or complete supplier is claimed.**

## Finding

This package independently reconstructs the `d0=76` member of the asymmetric
P112 unit recorded in [`format-limits` C.6](../format-limits/README.md#c6-asymmetric-pairing-uniqueness-at-the-e8-pattern-c6_asympy).
It checks the full 112-by-112 support identity with Python's standard library:

- the pairing window is 9;
- the shared extra total reads 24 source ports and has COPY rank 1;
- the eight coordinate totals each have COPY rank 8, so the reported total
  copy-rank charge is 65;
- the two modified decoder rows each have 28 off-diagonal correction
  positions, compared with 52 in the corresponding coordinate rows;
- two negative controls, changing one sink label or one row coefficient, fail
  the exact support condition.

The complete witness parameters, 24 source labels, correction and rank counts,
source pins, and canonical hashes of the exact matrices are in
[`CERTIFICATE.json`](CERTIFICATE.json). [`PROOF.md`](PROOF.md) states the
identity and the limits of this check.

This verifies one finite decoder unit. The scalar correction-support decrease
does not by itself give a cheaper paid recursive profile: the extra total,
frames, source access, realization and restoration still need a complete
supplier contract and invoice.

## Reproduce

From the repository root, with Python 3.10 or later and no third-party
dependencies:

```sh
python3 -I -O -B research/p112-off-pattern-unit-audit-seed52/verify.py
```

Expected final line:

```text
PASS_P112_ASYMMETRIC_UNIT_AUDIT seed=52 d0=76 ports=112 entries=12544 window=9 extra_sources=24 copy_ranks=8x8+1 copy_cost=65 corrections=28+28 baseline=52+52 controls=2 no_new_kappa
```

This command checks the pinned predecessor files, regenerates the E8/Hamming
geometry and binary labels, checks all 12,544 matrix positions, recomputes the
F2 ranks and correction supports, and compares the result with the committed
certificate. It does not call the SAT solver used in the predecessor's
separate pairing-classification checks.

## Assignment and overlap

OS random integer: `3423301012`; assignment seed: `52`; track: structural
decoder. Seed 52 selected the middle `d0` value, 76, from the predecessor's
three recorded values 75, 76 and 77. The other considered tasks and current
overlap evidence are in [`CLAIM.md`](CLAIM.md). The claim was posted to the
pinned coordination discussion [#1163](https://github.com/CrocSwap/integer-mult-bounds/discussions/1163#discussioncomment-18910869).

The exact base is `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`. Source hashes and
the originating task card are pinned in [`SOURCES.json`](SOURCES.json) and
[`TASK.json`](TASK.json). The selected frontier at the base remains the
conditional finite construction κ=`836330098538459/500000000000000000` from
PR #1094, with the complex supplier binding. This audit does not alter it.

## Open next questions

Can this two-sink unit be embedded into a legal stage with a net improvement
after charging the extra total, frame changes, source access and restoration?
The first step is to write that typed entry/exit contract and full paid profile
for one invocation. The current note provides only the decoder identity and
COPY-rank submatrix counts; no complete implementation contract is available.

## Credit and license

Credit DreamingOfClouds, PR #595, for the `format-limits` C.6 witness and
analysis; PR #717 for the P112 model; and PR #446 for the inherited decoder
format. The E8/Hamming construction follows the source-pinned
`research/format-limits/scripts/e8units.py`. The check and note are by Cinna
Davis with substantial OpenAI Codex assistance. New work is Apache-2.0; no
predecessor source file was modified.
