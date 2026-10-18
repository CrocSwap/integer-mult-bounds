# Complex coefficients do not escape the exact eight-term decoder floor

PR968 defines its exact eight-term decoder theorem for real matrices.
This note extends its bound to **arbitrary complex coefficients** with
ordinary transpose: for every puncture of `p<=24` root lines and every
exact all-pairs decoder `D T^transpose=2G`, the copied-information cost is
at least `max(72-p,56)`. Existing real constructions remain sharp over
the choices at each puncture size, so the best ratio stays `7/13`.

The extension needs care. PR968's cross-term nonparallel observation is
true over R but fails for complex isotropic normals. The package supplies
an exact Q(i) counterexample to that verbatim extension. The proof repairs
the bridge: every reduced side at `p<=15` is complex proportional to a
real root or D7 normal and is therefore nonisotropic. Only these reduced
directions need the nonparallel property in the count.

This is a scoped structural negative result, not a correction to PR968's
real theorem or a new supplier. It retains PR968's real hyperplane-flat
classification premise F6. The quantified statement is proved in
[PROOF.md](PROOF.md); finite examples are verification evidence.

From the repository root, Python 3.10+ and the standard library:

```text
python research/complex-decoder-field-extension-seed44/verify.py
```

Expected final line:

```text
PASS_COMPLEX_DECODER_FIELD_EXTENSION_S44 p=0..24 examples=3 attaining=25 pairing=14400 controls=7
```

The command replays the exact predecessor facts used by the proof,
constructs the E8 model independently, checks all 14,400 pairing entries,
and validates Q(i) examples with integer denominator clearing. It also
checks all 25 phase-scaled attainments and seven negative controls.
`CERTIFICATE.json` stores the full deterministic evidence;
`verify.py --write` regenerates it. The predecessor replay runs in a
separate non-optimized process so its assertions remain enabled even
when the new checker is invoked with `-O`.

No new copy or physical operation is proposed, so there is no supplier
invoice to replace. The claim concerns only the exact eight-term,
all-pairs identity with the retained label cost; nine or more terms,
masked identities and p>=25 remain excluded. No new kappa, native
admission or all-size theorem is claimed. The selected PR942/PR589
construction and every predecessor file are unchanged.

See [NOTICE.md](NOTICE.md), [OVERLAP.json](OVERLAP.json) and
[VALIDATION.md](VALIDATION.md). Prepared for @woklerx with substantial
OpenAI Codex assistance; Apache-2.0.
