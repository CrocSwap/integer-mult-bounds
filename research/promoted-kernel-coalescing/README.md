# Promoted kernel providers with six frame coalescences

Conditional **κ = 0.001602080856660739**, with conservative rounded-invoice
κ = 0.00160208085385131. This is a finite witness in the repository's conditional
multiplication model. It does not establish κ = 1 or an unconditional theorem.

PR582's literal allocation uses 66 added-kernel calls (`ck`), five calls with
forty additional entrance promotions (`atm3`), and one plain joint-prefix call
(`jp8`). Each of its two kernel providers admits six further A-frame
coalescences. Each set replaces 12 rank-1 payments with six rank-2 payments.
All scalar operations, helper entrances and widths, call assignments, and
physical owners remain those of PR582. The resulting global profile is:

```
{1:173688, 2:40490, 3:23928, 4:14024, 5:4038,
 6:4032, 8:576, 30:1, 48:1857}
```

The native rate lower endpoint is
`1604651638332121038073/1000000000000000000000000`.
Dimension 73, live stock 7168, physical stock 7682, deficit 2560 and rank mass
520704 remain unchanged. All 36,288 helper roles, 6,710 actual owner charts,
29,283 cross-replica roles and 2,808 positive idle remainders are reconstructed.

Run with Python 3.11 or newer, assertions enabled, the standard library, and an
absent external output directory:

```sh
python3 -B research/promoted-kernel-coalescing/verify.py --work /tmp/promoted-kernel-cold --jobs 3
```

The frozen verifier rebuilds the complete pinned PR558 baseline and all three
PR582 provider construction chains, including their omission and coverage
controls. It applies both literal six-frame recipes before independently
rebuilding native programs, wrappers and all exact phase recipes for the final
providers. It then reconstructs the full physical word and finite invoice,
checks both rational models, and runs assembly, phase-timing and actual
recompression/content controls. There are no reused local proofs in this cold
run, no solver dependency, and no discovery mode.

`MANIFEST.json` binds the entire source tree. `SOURCE-PINS.json` additionally
binds all 259 vendored files to original Git blobs. PR568 is bundled in full;
the additional PR569/571/575 sources include the exact manifest-pinned files
used by PR582 and their notices. The original PR582 package and selected PR583
verification sources are also retained unchanged in `vendor/`.

The sibling `promoted-kernel-coalescing-validation` directory contains cold
replay receipts and proof-content comparisons. GitHub CI is reported separately.
The unchanged repository baseline reuses the explicitly identified PR572
18-group passing evidence, including `gen4-bank-verify`; it is not counted as a
new aggregate baseline run.
