# The punctured E8 floor for any number of factor-linear terms

PR968/PR1077's eight-term cost floor also holds for any finite number of active
terms **when both factor matrices stay in the live root code**. For every
puncture of p<=24 lines, the total copied-information rank is at least
max(72-p,56), over arbitrary complex coefficients and ordinary transpose.
The prior eight-term attaining examples remain optimal within this larger
class. The minimum ratio stays 7/13, and the standard P112 minimum stays 64.

The new proof combines a rank bound on unreduced columns with a positive
inverse-Gram diagonal obstruction for the only exceptional case, p=8,m=9.
An explicit nine-term exact identity with columns outside the root code shows
why the restriction cannot be dropped. No unrestricted overcomplete barrier
or new kappa is claimed.

From the repository root, Python3.10+ standard library:

```sh
python -I -O -B research/e8-factor-linear-overcomplete47/verify.py
python -I -O -B research/e8-factor-linear-overcomplete47/test_package.py
```

Expected main marker:
`PASS_FACTOR_LINEAR_OVERCOMPLETE examples=4 punctures=25 root_pairs=1024 outside_code_rank=9 controls=5`.
The package test prints `PASS_FACTOR_LINEAR_PACKAGE relocation=1 mutations=6`.
Default replay writes nothing. `--write` explicitly regenerates EXPECTED.json.

The checker replays the inherited finite geometric premises with assertions
enabled, then checks four complex overcomplete examples on all root pairs and
25 punctures, 16 exact inverse-Gram certificates, 1024 root-pair costs and the
112-row outside-code identity. The standard real-flat classification remains
an inherited mathematical premise, clearly separated in PROOF.md.

Base: c0e3631dc24e3c24a861f7d3d79e0608481cccec. Seed47 is the original OS draw;
new repository task guidance was read without rerolling the assigned track.
Selected PR1094, conditional kappa 836330098538459/500000000000000000, remains
unchanged. This package changes only its own research directory.

PR968 by themilkman216, PR1077 by woklerx, and the DreamingOfClouds/Joel Pulikkan
model and geometric lineage retain credit. See NOTICE.md and exact source pins.
Prepared with substantial OpenAI Codex assistance; Apache-2.0.
