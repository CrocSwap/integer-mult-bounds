# Six kernel frame coalescences

Conditional **κ = 0.001601661522127798**, with conservative rounded-invoice
κ = 0.001601661519340063. This is a finite witness in the repository's
conditional multiplication model, not a proof of κ = 1 or an unconditional
integer-multiplication algorithm.

PR579's added-kernel provider admits six further frame coalescences in its A
prefix. They replace 12 rank-1 payments by six rank-2 payments per call. All
scalar operations, source/target boundaries, helper widths, and physical owners
are preserved. The 48 added-kernel calls and 24 plain joint-prefix calls remain
exactly PR579's dispatch.

The new local profile is `{1:2408, 2:570, 3:320, 4:192, 5:56, 6:56, 8:8}`.
The independently recounted global profile is
`{1:171264, 2:37440, 3:27686, 4:13824, 5:4032, 6:4032, 8:576, 30:1, 48:1817}`.
Its rank mass is 520704, live width 7168, and physical width 7682.
The native rate lower endpoint is
`1604230957124431220769/1000000000000000000000000`.

Run from an unchanged source tree with Python 3.11 or newer, standard library
only, assertions enabled, and an absent external output directory:

```sh
python3 -B research/kernel-frame-coalescing/verify.py --work /tmp/kernel-frame-cold
```

The verifier rebuilds the complete pinned PR579 witness, including its PR575
and PR558 ancestry. It then applies the six literal frame changes, checks their
individual exact profile savings and 12 negative controls, and freshly verifies
all scalar columns, monotone native frames, both reflected programs, residual
wrappers, all 3015 phase edges and 224 endpoints. It reconstructs the complete
owner map and finite invoice, runs both rational models, and checks physical,
assembly, timing, recompression and content-identity mutations.

`MANIFEST.json` binds every source file. `SOURCE-PINS.json` additionally binds
all 293 vendored PR579 files to their original Git blobs at
`970d38a3862ee35064a827b671d196744ee2a928`. No optimization, network access, or
witness discovery occurs during replay. Negative searches in the working
research directory are not needed by this proof.

Cold replay receipts are published in the sibling
`kernel-frame-coalescing-validation` directory. They distinguish locally
completed checks from GitHub CI status. The unchanged repository baseline test
groups are reused with explicit provenance from PR572; they are not counted as
fresh tests of this package.
