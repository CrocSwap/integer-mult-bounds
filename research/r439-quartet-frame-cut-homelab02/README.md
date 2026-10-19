# One frame-available cut in the PR941 R439 four-helper word

**Scoped chronological/frame audit; no supplier, paid-profile, or κ claim.**
This note checks one implication for the winning quartet in
`research/r439-helper-quartets-seed07`: after its dependent helper preparation,
are the four current helper values still present at frame 0 when the compiled
middle injection begins?

## Exact scope and result

The pinned predecessor uses quartet indices `[114,126]`, helper labels
`[269,88,288,153]`, and preparation word
`a ^= b; c ^= d; b ^= c`. With `v=111`, those are register IDs
`[491,310,510,375]`. In the constructed D section:

- the three quartet gates are D indices **114–116**;
- all 200 helper preparations and 306 target preparations finish before the
  compiled middle injection, which starts at D index **506**;
- none of the four selected helpers is written again between the last quartet
  preparation and that cut;
- each selected helper is read by the 111 middle-injection gates (respectively
  9, 11, 8, and 15 times); and
- all D gates use frame 0. The four helpers and the targets start at frame 0,
  so the selected operands are at frame 0 throughout this prefix and at the
  injection cut.

On arbitrary four-register input `(a,b,c,d)`, the prefix states are
`(a+b,b,c,d)`, `(a+b,b,c+d,d)`, then `(a+b,b+c+d,c+d,d)`. Its exact row masks
are `[3,14,12,8]`, matching the pinned certificate. The literal reverse word
restores the four initial values after the injection and target cleanup.

The frame check is necessary but does not make the word order optional. A
control that swaps `c ^= d` and `b ^= c` remains frame-0 legal, but changes the
matrix to `[3,6,12,8]`. Holding the compiled injection fixed, the dirty input
with only helper 153 set changes the target output. In the 111-bit target
basis, the expected output is `0x4001480001100e2040150e2110`; the reordered
output is `0x4041402001008a6004150c2118`; their XOR is supported at target
indices `[3,17,34,38,46,50,55,60,77,83,94]`.

This establishes one cut-local fact for this finite word: the altered helper
values are chronologically retained and frame-available at the middle
injection, while the dependent preparation order is semantically material.
It does **not** discharge the complete replacement for H2/K. The predecessor's
syntactic `H2_D_frame0_targets_from_helpers` and `K_equals_D` flags remain
false. This audit does not re-run the 661-column whole-word verifier, recompute
the paid profile, or assess hosting, supplier adoption, the selected result,
or the multiplication theorem.

## Reproduction

From the repository root, with Python 3.12 or later and the pinned inputs
present:

```sh
python3 -I -B research/r439-quartet-frame-cut-homelab02/verify.py
python3 scripts/research_package.py --package research/r439-quartet-frame-cut-homelab02 --check-only
```

The first command checks the 46 declared input pins (including the
predecessor's 43-file source closure), rebuilds only the named candidate (not
its GL(4,2) search), verifies the preparation/cleanup cut and D frames, checks
the exact four-register matrix, and checks the 16 local dirty-input cases plus
the reordered control. Expected output is:

```text
PASS_R439_QUARTET_FRAME_CUT prep=114:117 injection=506 helpers_frame0=true helper_reads=9,11,8,15 local_inputs=16 reorder_failures=8 reorder_witness=153 delta_support=3,17,34,38,46,50,55,60,77,83,94 no_supplier_claim
```

## Source and credit

The task runs on base `20ecf2891d80b5acf18d980b2164fb44ea7faa90`, priority
revision 6. The quartet construction is Sagar Thakrar's merged
[PR #1045](https://github.com/CrocSwap/integer-mult-bounds/pull/1045), current
head `b4610c1c0ba67111c156bc56e9f16a4aab0fe613`, with package source base
`2921874911956718fcaaaf9396fe8267b3cfa9f0`. It uses the PR941 matching and
PR915 target basis, with the earlier PR915/926/941 and PR555/589 lineage
credited in that package. The exact files and hashes checked here are
in [SOURCES.json](SOURCES.json); the task card, selected record, and catalogue
are pinned as provenance by [TASK.json](TASK.json).

Prepared by Codex agent `homelab-02` with substantial OpenAI Codex assistance.
New work is under the repository's Apache-2.0 license. The predecessor's
attribution and source licenses are retained.

## Open next questions

No further quartet or supplier-admission question is opened by this one-cut
audit. A broader replacement contract would need its own complete boundary,
paid-profile, and consumer ledger under the family expansion gate; this result
alone supplies no reason to start another construction round.
