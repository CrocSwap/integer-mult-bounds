# Exact rank of a paid connector chart repair

The retained dirty connector chart interface can move B0 x to B1 x without
another source observation exactly when the two maps have the same kernel.
This package permits a **paid residual source injection** Delta x and determines
its minimum rank:

    min_(R invertible) rank(B1-R B0)
      = max(rank B0,rank B1) - dim(row B0 intersect row B1).

The theorem holds over every field, including singular and unequal-rank maps.
A constructive change-of-basis proof supplies R and Delta. The same quantity
lower-bounds the total injected rank of any internal sequence of invertible
charts and additive source corrections without intermediate observations.
It does not minimize chart cost, scalar work or a physical native tariff.

This extends woklerx's [equal-kernel chart criterion](../dirty-connector-chart-transport/README.md)
within Ross Richardson's [dirty-query model](../universal-connector-boundary/README.md).
Their boundary contracts, cancellation and price conventions retain credit.
The contribution is the residual-rank interface, its constructive certificate
and the restored/charged example; no novelty claim is made for elementary
row-space inequalities or change of basis.

## Complete dirty-state example

Read matrix rows as binary masks:

    B0=(7,6,1), B1=(1,6,5), R=(3,2,4), Delta=(0,0,4).

The paid chart is z0+=z1 and its inverse is the same shear. The correction
is one XOR from source coordinate2 into connector coordinate2. It has rank1,
the proved minimum; the identity chart would leave rank2. Four distinct
three-bit rows x,z,y0,y1 are all arbitrary. Every source, chart, readout,
correction and final inverse is emitted explicitly; no extra row is needed.

| Fixed one-bit implementation | XORs | Reads | Writes | Head moves | Declared tariff |
|---|---:|---:|---:|---:|---:|
| Two closed queries |34|68|34|444|614|
| Repaired chart pair |26|52|26|368|498|
| Direct matrices, outside this query alphabet |11|22|11|204|259|

The tariff puts the12 bits at consecutive positions, starts/returns the data
head one cell before bit0, and charges `2*(max(source,target)+1)+5` for each
scalar XOR. Its five units are two reads, one write, XOR and dispatch. This
declared interpreter tariff is not a native tape-compiler certificate.
The11-gate direct control is deliberately retained:26 is **not** a minimum
over arbitrary circuits. No selected caller is claimed to need this alphabet.

The first output is delivered before the chart change and never rewritten.
After the paid correction the connector is R z_initial+B1 x. The second
read/close/read cancels the charted dirt, and the final R inverse restores the
actual connector. The source correction is cancelled by the closing B1 call;
it is not deferred to a later consumer. [PROOF.md](PROOF.md) gives the exact
word over general characteristic and the full comparison, including admission,
preparation, instruction work and complete prices of all child operations.

## Reproduce

```sh
python3.12 scripts/research_package.py --package research/connector-chart-rank-repair
python -I -O -B research/connector-chart-rank-repair/verify.py
```

The external finite oracle enumerates all168 GL3 charts and their complete
orbits, then checks every262,144 pair of binary3-by-3 maps. It agrees with the
formula's minimum-rank histogram `0:40916, 1:187376, 2:33516, 3:336`.
The independent constructive method emits8,192 charts across all16 row-space
classes and512 destinations. No predecessor executable is imported.

All4,096 dirty pilot inputs, literal inverses and first-output cuts pass.
Four altered programs fail semantically. A separate ordinary-matrix control
over F3 checks6,561 arbitrary dirty banks and inverses with noncommuting
readers, and rejects the wrong closing sign. Zero maps, unequal ranks,
equal-rank unequal kernels and an adverse chart tariff are explicit controls.
Four export groups cover Git-free read-only replay, source drift, typed/duplicate
receipt corruption and exclusive regeneration.

Native CPython3.12.7 registered checks and optimized3.14.5 primary replay pass.
A separate OpenAI Codex agent checked the proof and independently minimized
4,454 smaller binary map pairs plus all168 charts for the pilot. Evidence is
finite where described; the all-field theorem relies on the written proof,
not on extrapolation from the finite checks. No human or formal-kernel review
or hosted CI result is claimed.

## Expansion decision and limits

Milestone: **local module**. The initial revision4 assignment was preserved
when main advanced to revision5 (`b4560d9e7216f72b73c5aa940ac099c05e33ccf9`).
The new family gate was read and the checkout fast-forwarded before packaging;
scientific predecessor blobs were unchanged. TASK.json contains the five-point
boundary/obligation ledger and the decision to **narrow** to this proof.

A small rank is not a free observation or a cheap circuit. The general native
cost of R, R inverse and Delta, dynamic synthesis, selected ownership, precision
and an actual selected consumer remain unknown. Unknowns are not zero. The
complete improvement condition is that chart, inverse, correction and changed
admission/preparation/control cost less than the removed B0 and B1 calls.
No supplier, recursive contraction, selected-result change or new kappa follows.
Do not expand the family without a concrete consumer and that strict allowance.

## Open next questions

1. Find a pinned caller with this legal connector lifetime, actual source maps
   and a favorable complete native repair invoice. Hosting and precision must
   be included before using this module in a supplier.
2. For that caller only, optimize within its legal chart alphabet and actual
   prices. The unrestricted rank optimum may be unavailable or more expensive.

Prepared by ywz65 with substantial OpenAI Codex assistance. Apache-2.0.
