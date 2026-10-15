# Selected BIT controlled ADDs on complete streams

We execute the selected rank-42 normalizer's variable-coefficient ADDs as
sequential payload permutations. We compute coefficients from full parent
matrix headers, preserve unused child stock, and supply a common adapter
schedule with **15,332f ordered shifts and zero ordinary interchanges**.
The caller still supplies one weighted child of width 42f.

This follows the physical execution handoff in
[commdata2338's PR2160](https://github.com/CrocSwap/integer-mult-bounds/pull/2160),
head `3ad4f746258a36c80db5869d7beb0f88c71a350e`. That author supplies the
selected residual binding, normal-form algebra and child-weight rule.
The retained ordered-affine lemma supplies the generic split/merge method.
We add the physical continuation, full-prefix evaluation, fixed instruction
slots and a preparation-sensitive cost argument. We claim no supplier or
exponent improvement.

## Selected object and result

We bind idle child 6, copy 213, replica 0, pair 0, side 1, port 102, physical
family 213. The retained template leaves its 42 axes 22 through 63 unhosted,
so its local projector is `P0=diag(0_22,I_42)`. During this idle operation
the current physical header is g, and the projector is `g P0 g^-1`.
We keep g fixed while moving records in the head/tail address fields.

The selected finite template names an orthogonal cover. We retain the
stopped-GL chart as an explicit implementation domain, with its full
invocation bridge still open. This package does not establish that bridge.

For a concrete family of full GL64 headers agreeing modulo 5, the selected
cross-shear coefficient takes these values:

| High parameter t | Pivot `1+5t mod25` | `K[63,42] mod25` |
|---:|---:|---:|
|0|1|1|
|1|6|21|
|2|11|16|
|3|16|11|
|4|21|6|

For source address 1 and target address 0, we move the payload to target 21
when t=1. A low-only coefficient would move it to target 1. We also execute
the zero/nonunit arm `K[21,0]=5t`; an ordered ADD remains a permutation when
its coefficient is zero or a nonunit.

The adapter schedule retains all row, column and cross-shear slots,
including zeros. Its shape depends on dimension, rank and f; it does not
depend on high matrix values or weights. Every target follows its source,
so the adapters need no ordinary interchange. We leave variable diagonal
units in the one weighted child.

## Evidence and reproduction

We check 51 full address fixtures, including dense GL64 matrices, against
a direct weighted-projector formula. We also check all 128 columns of one
dense weighted operator. The physical stream tests move
**1,277,550 positive-case payload bits** through complete source/target
fibers with unused-stock and middle spectators. We include width one,
where the atom field still has q values and the shift remains active.

The two-level weight evaluator reads older full matrix headers at ancestor
column widths 4 and 2, then computes the current weights through the retained
flat-index rule. At atom 42 it obtains `1*6*11=16 mod25`. Its physical test
preserves three unused-stock classes and rejects low-only ancestor
evaluation. Separate controls reject a low-only current coefficient and
the resulting wrong complete normalizer endpoint.

Use Python 3.12 and the standard library, from the repository root:

```sh
python3.12 scripts/research_package.py --package research/selected-bit-controlled-streams
python3 -I -O -B research/selected-bit-controlled-streams/verify.py
```

For the common f=1 instruction list, including its single weighted child:

```sh
python3 -I -B research/selected-bit-controlled-streams/verify.py --emit-schedule
```

The verifier authenticates retained inputs and reads no predecessor code.
It writes no repository artifacts. The physical simulator counts payload
reads, writes, head moves and scratch erasure; it reports ring operations
and copied control cells separately. These counters are not measured
Turing-machine time. [PROOF.md](PROOF.md) charges arithmetic, control access
and cleanup, then states the root-width condition for absorbing preparation.
We test a five-point affine line of full matrix headers, not an enumeration
of the entire GL64 high fiber. The written argument covers arbitrary
permitted prefixes and complete target fibers.

## Open next questions

1. Extend the explicit weight evaluator to one mixed good/bad ancestor
   path. Begin with one child from
   [Ross Richardson's PR2159](https://github.com/CrocSwap/integer-mult-bounds/pull/2159)
   and retain its paid child count. We implement good ancestors with explicit
   coordinate-projector labels here. Binding further local-frame labels and
   fallback descriptors remains open.
2. Realize one complete selected local invocation per low cover class,
   including correlated hosted helpers and COPY/ERASE lifetimes. Begin by
   checking same-family helper footprints within one low class. The full
   stopped-GL domain bridge remains outside this adapter result.

We retain the weighted recursive callee, general mixed-ancestor access,
complete hosting, fresh-field cylinder and outer-transfer obligations.
[TASK.json](TASK.json) records the changed scope and
[SOURCES.json](SOURCES.json) pins source bytes and predecessor heads.

Prepared by Jose Manuel (`@jmbarrancoml`) with substantial OpenAI Codex
assistance. We credit commdata2338's PR2160, the retained source527 and
ordered-affine proofs, Ross Richardson's fallback schedule, Nick Petalas's
carry/stock work, Adam Gall's fresh-field and stock analysis, and the
selected BIT construction lineage: eumemic, DreamingOfClouds, DaysSky,
Zhihao Chen, Dylan Crow and Jacob Sussman. Apache-2.0; no independent
human review or full multiplication theorem claimed.
