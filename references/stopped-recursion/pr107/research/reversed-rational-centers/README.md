# Reversed pair-star orders on PR104

Under **all of PR104's inherited and newly proposed interfaces**, this finite
refinement gives conditional **κ = 7798412662809/10^17 = 7.798412662809×10⁻⁵**,
about **0.04686049% above PR104** at commit
`854ba7dca98651eab2050402384e1a7784534f0a`.

For each pair `(a,b)`, sort the other coordinates by
`((i ^ 1) in (a,b), -i)` instead of `((i ^ 1) in (a,b), i)`.
This reverses the order within each of the two aligned groups. It preserves
the scalar identities, rank-label rules and legal carrier matching algorithm,
while changing the distribution of paid child widths.

The h24 producer still has 44,918 roles and 8,966 matches. Its new strict
complex saving is `7799647191/10^14`. The h23 stopped bit construction,
ordinary leaf, fixed divisor 21, copied-center corrections and three nested
row reserves are unchanged. The complete cost profile is regenerated; no
endpoint gates or cleanup calls are removed.

```sh
python3 research/reversed-rational-centers/verify.py
python3 research/reversed-rational-centers/test_controls.py
make verify
```

The focused verifier reproduces PR104's exact certificate, rebuilds both
the parent and selected scalar/frame producers, recompiles the inherited
matcher, checks every histogram entry, then checks all 47 strict constraints,
seven margins and two next-grid exclusions. Five adversarial controls reject
unpaid cleanup, omitted retained loss, reuse of the old profile, and excessive
complex/final exponents. Full repository verification is pending.

PR104 changed `Makefile`, `README.md` and `NOTICE` without refreshing
the inherited joint source fingerprints. This branch refreshes only those
three pins. The affected independent h23/h25 physical replay passed;
its derived certificate and receipt differ only in source/checksum metadata.
No mathematical inputs or checks were changed. Full verification remains pending.

This is a small finite refinement, not a proof of global optimality or a
practical runtime claim. In particular, **the new opposite-bank factorization,
stopped atom streaming and odd-denominator grid interfaces in PR104 remain
written proof dependencies, not independently established theorems here**.
See [the argument and scope](proof.md).

Credit icekylinx for PR104 and its stopped product-ring/rational-center
construction; Zhihao Chen for the semantic/bulk assembly; RaD/hipotures for
its analytic interfaces; Aurel Prosz/Paureel and the credited two-stage
contributors; eumemic and the retained paired-circuit contributors;
Douglas Colkitt, OpenAI, David Harvey, Joris van der Hoeven, and all
predecessors credited in PR104's `NOTICE` and `SOURCES.json`.
Original notices and licenses are retained. This order refinement was
prepared by Rohan Arun with OpenAI Codex assistance, under Apache-2.0.
