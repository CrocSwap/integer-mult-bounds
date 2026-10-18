# Validation

Validated 2026-10-14 UTC on Linux x86_64 with Python 3.12.3 and Python 3.14.4,
standard library only. Research base is
`bce54fb3f895cbe5cd4c0eb477c3afeed100190f`. Main advanced during the pass to
`cd91ac8e2652bfee6bf09da3b8724253bcf78f5f`; all four live source files are
byte-identical there, as are the assignment and relevant replay instructions.
The original assignment/provenance pins remain historical at the research base.

## Recorded commands and results

The required starting example completed:

```
python3 -B research/r439-bsection-stars-seed01/verify.py
PASS_R439_BSECTION_STARS blocks=10 gates=388->254 ADDs=11783->11515->11500 guard_rejections=24->0 columns=661 controls=8 no_new_kappa
```

This is source-bound orientation, not new evidence or a new construction.

The full registered package command passed on Python 3.12.3:

```
/usr/bin/python3.12 -I -B scripts/research_package.py --package research/projected-cleanup-fibers
PASS_ALL_DIMENSION_CONSTRUCTOR states=4716 parabolic_matrices=12630
PASS_SELECTED_PR589_PROJECTED_CLEANUP_COUNTEREXAMPLE
PASS_PROJECTED_CLEANUP_FIBERS receipt_sha256=0afacad9740685e504cedfd9b81d85c702ae53ada78795a3662b4523f5a8e50d
PASS_REGISTERED_RESEARCH_PACKAGE research/projected-cleanup-fibers outcome=completed
```

The same registration also ran all seven test groups successfully. They cover
complete literal words through length four on three wires, omissions from both
loop types, the clean-helper blind spot, missing constructor hypotheses, the
selected-word dirty witness and raw-loop mutation, strict JSON/typed receipt
rejection, isolated read-only optimized export/source corruption, and existing
output preservation. The first standalone test run also passed.

A separate export containing all package runtime files and four declared inputs
was made read-only (0444 files, 0555 directories), then run from `/tmp`:

```
python3 -I -O -B /tmp/math-pass28-readonly/export/research/projected-cleanup-fibers/verify.py --work /tmp/math-pass28-readonly/work
```

Python 3.14.4 produced the identical complete canonical receipt above. All 16
files in that runtime export remained byte-identical. Later submission,
attribution, overlap and validation metadata are editorial; code and live input
bytes are unchanged. The retained exporter runs in an isolated subprocess with
assertions enabled even when the parent uses `-O`.

## Coverage

* Complete paired-state counts: 12, 672 and 4,032; 28,248 transitions. Independent
  packed-row and literal-permutation engines agree on every shortest distance,
  covering 37,680 literal assignments. The 4,032-state case is PR1105's result,
  reproduced with attribution.
* The constructor attains all 4,716 paired states and all 12,630 small parabolic
  matrices, the latter checked on every Boolean input. Thirty-nine larger
  fixtures through 64 registers pass independent input-column replay.
* All 144 ordered two-gate products on four labels are classified; their
  97 products give 1,044 projected-relation checks. The two-row length-five
  lemma is also checked on all 63 literal words. These support, rather than
  replace, the written all-dimension sharpness argument.
* Three complete selected-word variants each have all 661 dirty columns checked
  forward and backward with literal COPY/ERASE. Baseline and neutral-loop
  control pass; the compiled projected-cleanup variant fails exactly at helper222.
* The pinned owning checker independently reproduces the frame/lattice checks
  and dirty rejection. Raw U/J/K, all frame paths, rank mass 5,129, all nine
  COPY/ERASE pairs and the scalar 104/192-bit guards are checked as documented.
  The independently expanded stream matches every exported opcode.

The full certificate is EXPECTED.json. Source bytes, source formula ASTs,
matrices, distances, generated words and record streams are bound by explicit
checks and hashes. The source word and all frozen packages remain unchanged.

## Limits

The new program fails the proposed weakened contract's desired complete dirty
boundary; this is an intentional negative witness. The original production
checker rejects it. No native 5/9/11-stage, owner/window, hosted supplier or
outer-assembly replay was performed. Scalar positive envelopes do not establish
new packed precision/tape or all-size physical realization. The uniform theorem
concerns the explicit scalar XOR alphabet and is not a theorem that arbitrary
physical frame programs have the same joint range. The proof is written, not
Lean-checked. Hosted CI and maintainer review are separate from these local checks.
