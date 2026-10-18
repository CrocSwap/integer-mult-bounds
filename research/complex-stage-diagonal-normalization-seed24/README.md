# Selective stage diagonal consolidation, seed 24

For the actual PR1042 R480 word archived at base `ba82555c64e1879e4b7decce28186f208fcb8262`, consolidate existing SCALEs on 41 A-stage and 22 B-stage registers. The complete scalar stream saves **540 real scalar primitive operations per complex invocation in either orientation** under the stronger retained PR696 lowering, including coefficient preparation, private clearing, and every boundary restoration. This combines both real and imaginary components: the saving is 270 per component. Every paid climb and other non-scalar event is unchanged.

| Complete emitted scalar stream | Original | Candidate | Saving |
| --- | ---: | ---: | ---: |
| Forward, PR696 lowering | 149002 | 148462 | 540 |
| Backward, PR696 lowering | 149018 | 148478 | 540 |
| Forward, original Horner lowering | 198766 | 198426 | 340 |
| Backward, original Horner lowering | 198814 | 198474 | 340 |
| Scalar macros, either orientation | 19693 | 19631 | 62 |

The unchanged paid-frame profile is `2412 H1 + 418 H2 + 432 H3 + 142 H4 + 82 H5 + 8 H8`. Frame costs are retained separately; they are not omitted costs being claimed as savings. Exact matrix replay checks every one of the 704 arbitrary input columns in both complete orientations, as well as the two replaced stage maps independently. Each of 326 distinct lowered ADD coefficients is checked on arbitrary target, source, and private work input.

The positive primitive-prefix bounds, including the coefficient work register, stay `2765345294379392599/1024` (52 bits) forward and `14824960514781440791821/64` (68 bits) backward. These are finite growth checks against the retained 192-bit allowance, not a new all-size precision theorem or native-hosted admission.

From repository root:

```text
python -I -B research/complex-stage-diagonal-normalization-seed24/verify.py
python -I -O -B research/complex-stage-diagonal-normalization-seed24/verify.py
```

Expected: `PASS_COMPLEX_STAGE_DIAGONAL_S24 registers=41+22 gain_real_per_orientation=540 Horner_gain=340 controls=10`.

`CANDIDATE-PROGRAMS.json.gz` contains both complete emitted programs. `CERTIFICATE.json` records all individual selection scores, register lists, boundary gates, complete costs, growth bounds, matrix digests, and controls. The verifier rebuilds these artifacts from five mandatory pinned sources, then compares the entire receipt and candidate payload. `--write` is the explicit regeneration mode.

Blanket consolidation is a useful negative control: deleting 290 macros nevertheless increases the forward strong count from 149002 to **153266**. No optimality is claimed for the selective subset, and no savings are inferred from macro count alone.

This is a source-bound finite construction on the historical selected PR1042 word. Current PR1094 selection is separate overlap context. It does not update the selected result, kappa, hosted assembly, or native implementation. The frame replay checks the retained scalar/label/wrapper contract, and is not a new proof of physical or Clifford realizability. See PROOF.md, OVERLAP.md, and VALIDATION.md.

Prepared for @woklerx with substantial OpenAI Codex assistance. Apache-2.0; source lineage and attribution are in NOTICE.md.
