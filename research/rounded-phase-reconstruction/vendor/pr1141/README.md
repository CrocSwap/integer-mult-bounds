# Linear scalar work for reversible dirty phases

This package replaces PR1038's per-site Machin/Taylor evaluations with a
reversible quadratic phase stream. It generates
`D_j=exp(2 pi i a j^2/m)` for every integer `a`, positive integer `m`, and
finite positive length `L`. It uses two complex phase states, bounded
three-shear rotations, and `W+2 bit_length(L+1)+20` state bits for data
precision `W`. It stores no phase array.

Every data pass runs the phase state backward after use. The state and
seed coefficients clear exactly. Both directions of the data map use
the same coefficient stream. The dirty source and all borrowed arrays
therefore restore exactly. The four phase passes around a complete dirty
factor word keep PR1038's error bound, data-tape bill, and original
`ceil(log2 n)` borrowed arrays.

The stream costs `O(L)` scalar operations. Exact rational seed preparation
and erasure cost `O(P)` operations on polynomial-width operands, where
`P=W+O(log L)`. The elementary bit bound is
`O((A+V)^2+P S^2+L T^2)`, with `S=16(P+V+1)^2`, original numerator width
`A`, modulus width `V`, and stream/data width `T`. The exact seed series
can be costly for short streams. This is not a uniform runtime speedup
or a near-linear bit-arithmetic claim. [PROOF.md](PROOF.md) gives the full
uniform error, cleanup, workspace, tape, and dirty-conjugation argument.

Run with standard-library Python 3.11 or later:

```sh
python3 -I -O -B research/dirty-stride-fast-phases/verify.py
python3 -I -O -B research/dirty-stride-fast-phases/test_package.py
```

The main check covers 98 phase cases, 1,474 independent rational interval
samples, 16 dirty leaf/factor words, three same-input PR1038 work comparisons,
and seven invalid-input or lifecycle controls. It executes and reverses
every step of a 16,384-site stream; it samples 65 phase values in that long
case. The other 1,409 phase samples cover every site in their cases.
Inputs include negative numerators, 161-bit moduli, chart boundaries,
rounded-zero angles, odd lowest grid bits, and dirty values through `2^80`.

The interval oracle is the pinned PR1038 oracle. It uses direct quadratic
residues and full-angle interval series. It does not use the new recurrence
or the production chart. Dirty calls are compared with finite geometric
sums. The checks are separate computational paths, not independent human
review or a formal multiplication proof. The package test adds semantic
faults and a complete replay from a relocated package with read-only sources.

The exact base is `abdc6a7002abdbcd9e21bfc5e1a795784deacfdf`. The direct
dependency is PR1038 at `99c71d385171480ecc2c43287aa4a04e1027fcd9`.
[SOURCE.json](SOURCE.json) pins all retained files. [NOTICE.md](NOTICE.md)
gives credit and discloses substantial AI assistance. [CLAIM.md](CLAIM.md)
records the three candidate approaches and chosen scope.

[VALIDATION.md](VALIDATION.md) records completed checks, the intermediate
stop, and the same-input baseline. [BENCHMARK.json](BENCHMARK.json) retains
all final timing trials. Seed setup makes the new reference slower in
the two shorter measured cases. The last case has a lower median; the
shared-host timings do not establish a general speedup.

Status: **enabling construction**. No new kappa is claimed. The selected
frontier, its supplier invoices, and `upstream/` are unchanged. PR1054's
precision improvement and PR1025's analytic root bound are not imported.
Fast bit compilation, multi-axis phases, factor production, full transform
composition, common-label realization, and physical supplier hosting remain
separate obligations.
