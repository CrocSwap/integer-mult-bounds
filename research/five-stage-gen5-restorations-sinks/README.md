# five-stage-gen5-restorations-sinks

**Conditional κ = 745513573133379 / 10¹⁸ = 7.45513573133379·10⁻⁴** (+0.1073% over #290's 7.44714499357628·10⁻⁴;
+0.187% over PR #287's 7.44120696397042·10⁻⁴).

This is the #290 package (PR #285's gen5 bit word, PR #287's 904-gate descent and 220 target squares, 450 collective
kernel entries) with the complex supplier swapped to the PR #233 word (complex coarse 7.54736·10⁻⁴, so the bit side
keeps binding with room), and two bit-side levers of the gen4 lineage ported to gen5 as transcript stages after the
kernel stage:

* **440 early helper restorations** (PR #280's mechanism, utcorvusvolat-dotcom; endpoint-aware banking as in PR #283):
  at the first cleanup ADD, 440 rank-20-entrance helpers have a single remaining incidence a −= b with b untouched on
  the crossed interval; the shear is executed there inside the exact rank-23 join E of the two frames and the helper
  ends at E instead of FULL. Residual P_E − P_σ (rank 3), completion P_σ + I − P_E, banks re-tiled
  ((3⁴⁰) 531 → 1,191, (4³⁰) −880 per stage), 440 new exact charts. Local delta {1: +1,320, 2: −880}; **+0.0750%**.
* **8 terminal sinks** (PR #283's mechanism, Dugongue): zero-to-full helpers whose value only cancels in their targets;
  forward writes redirected to a pivot target, setup/restore target shears inserted, the helper register deleted
  (R 15,886 → 15,878). 16 helpers have the gen4 shape on gen5; 8 collide with #287's target squares and are excluded.
  Local delta {3: −8, 21: −8}; **+0.0323%** on top.
* PR #280's third lever, transported dirty entrances, has no useful gen5 analogue (8 candidates, φ −68.8, ≈ +0.006%;
  most targets are read by #287's target squares) and is not shipped.

| one invocation, m = 120 | #290 | + restorations | + sinks (this package) |
| --- | ---: | ---: | ---: |
| literal stock, 60 replicas | 1,244,515 | 1,243,415 | **1,242,935** |
| helper registers R | 15,886 | 15,886 | **15,878** |
| bit coarse saving | 7.45270·10⁻⁴ | 7.45829·10⁻⁴ | **7.46070·10⁻⁴** |
| κ | 7.44714499357628·10⁻⁴ | 7.45272862652714·10⁻⁴ | **7.45513573133379·10⁻⁴** |

Every value was predicted exactly by the deficit-fixed φ ledger (discovery/coll/pack.py's model) before the stages
were built. The bit side binds (complex coarse 7.54736·10⁻⁴). Conditional finite construction under the retained public
all-size hypotheses of the source527 lineage (no Lean certificate); #285, #287, #280, #283 and #233 are inherited, not
re-proved. Mechanisms, integer arguments and checks: [LEVERS-PROOF.md](LEVERS-PROOF.md).

## Verify

    python -m pip install -r requirements.txt    # sympy 1.14.0
    python3 -B verify.py --output /tmp/gen5-restorations-sinks-verification   # about 4 minutes; not under -I

All stages run fresh (virtual, raw, bit with descent/target/kernel/restore/sink stages, kernel, restore, sink, scalar,
primes, banks, complex, math, finite) with twelve omitted-stage negative controls; every literal the new stages change
is re-pinned in `expected/kernel-pins.json` (pins.py refuses a name recorded with two values; verify.py refuses
recording mode).

## Files

#290's package plus: `restore_transform.py`, `restore-selection.json`, `sink_transform.py`, `sink-selection.json`,
`LEVERS-PROOF.md`, `discovery/build_restore_selection.py`, `discovery/build_sink_selection.py`; modified
`portable_bit.py`, `raw_ledger.py` (rebind_restore, rebind_sink), `code/global_lowering.py` (completion with endpoint,
R = 15,878), `code/geometry527.py`, `bank_template.py`, `bank_check.py`, `scalar_check.py`, `math_check.py`,
`finite_check.py`, `pins.py`, `verify.py`, `discovery/generate_pins.py`, `expected/kernel-pins.json`; the #233 complex
supplier files (`code/complex_labels.py`, `code/complex_splice.py`, `code/complex_scalars.py`, `portable_complex.py`,
`inputs/complex/source-pins.json`, `inputs/complex/gcert1-p11-pr233-flow.json.gz`). #290's README/PROOF are kept as
`README-PR290.md`, `PROOF-PR290.md`.
