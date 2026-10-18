# Native payload accounting for the paired-plane identity

PR2126's scalar identity is correct. Its 56 rank-two coefficient blocks do not,
under the inherited one-array copy interface, give 56 rank-two native child
occurrences. Each block carries two independent arrays. This package supplies
an exact native implementation on the selected planes and counts both uses:
**112 rank-two private drops, copy mass 224**.

The direct implementation fails the favorable two-unpaid-coordinate coverage
screen already at zero saving: **293/292 > 1**. No new supplier or kappa is
claimed. Shared fractional decoders and different multi-array interfaces remain
open.

## What is added

The naive profile `{7:224, 2:112}` and its failure were already reported by
ctoth's team in [Discussion1587](https://github.com/CrocSwap/integer-mult-bounds/discussions/1587#discussioncomment-18914510).
Philippe Van Velzen subsequently proved the stronger 224 floor for 2-integral
one-total decoders. Neither result is claimed new here.

This artifact connects the identity fit in [PR2126](https://github.com/CrocSwap/integer-mult-bounds/pull/2126),
head `06be72298adf84f3eef0e36f54ac31c357956417`, to native operators, private
lifetimes and an occurrence invoice on all 56 selected matched planes. PR2126
leaves physical execution and application multiplicity open; this resolves that
interface for its direct, independently implemented blocks.

## Exact local word

For a matched pair, `E = span(q,r)`, where `q.q = r.r = 1`, `q.r = 0` over F2.
Let `C_E = C_q C_r`, `F = C_all`, and `Gamma_U` be the retained canonical frame.
Two independent source arrays enter at `C_E`; two arbitrary dirty targets enter
at identity. Output charts are `F` and `F C_E^-1`, respectively.

For each source/target pair, sequentially:

1. Apply the checked monomial source adapter to enter `Gamma_E`.
2. Allocate an owned zero private array at that chart and copy the source.
3. Advance the source `E -> FULL` (rank seven).
4. Descend the private copy `E -> 0` (rank two).
5. Add it to the target at the common zero chart; dispose of the owned copy.
6. Advance the target `0 -> E^perp` (rank seven) and apply the checked monomial
   adapter to `F C_E^-1`.

The logical endpoint is `X_i -> X_i`, `Y_i -> Y_i + X_i`. Private storage is
reused only after disposal and reinitialization: one array at peak, two lifetimes
per block, 112 over all ports. Disposal uses the inherited owned-copy contract,
not reversible uncomputation of live data. No arbitrary dirty helper is cleared.

The four-column symbolic identity, with the checked native operators for every
matched plane, covers all 224 public input-array columns. The compiler emits
280 listed recipes, five per plane including monomial adapters. Positive ranks
are `7,2,7`; each recipe is used for both independent ports. The occurrence
profile is `{7:224, 2:112}`, mass 1792, not `{7:224, 2:56}`.

The separate retained Gaussian interpreter checks every signed Pauli tableau
and a nonzero exact state column, fixing global phases. All 512 state columns
are also compared for the first private descent. On all 112 ports, converting
the old line entrance `C_q` to `Gamma_E` has rank one: a plane entrance cannot
be silently substituted into an unchanged line-port invocation.

## Payload lower bound within the independent-block interface

Consider one block implemented by scalar linear totals, each carried through
a one-array copy tree. Both sources have frame `E`, both targets have cap
`E^perp`. Nondegeneracy prevents any drop-free source-to-target path. Each copied
total contributes an outer product of rank at most one to the 2-by-2 transfer
matrix. The required `I_2` has rank two, so at least two independent totals are
needed. Equivalently, for actual address dimension d, one array has capacity d,
whereas `I_2` on two arbitrary arrays has rank 2d.

For every nonzero total in this block, its source-plane and reader-plane spans
are both `E`. Their pairing has rank two. The inherited one-total copy-tree
tariff charges at least two per total, hence four per block. The explicit word
attains four. Scratch reuse reduces peak storage, not transform multiplicity.

A constructive positive control uses one private rank-two descent to broadcast
`X0+X1` to both targets. It preserves both sources and arbitrary target dirt,
but its transfer matrix is the all-ones rank-one matrix, not `I_2`. The verifier
accepts its `{7:4, 2:1}` invoice for that endpoint and rejects it as an identity
implementation. Thus the checker distinguishes sharing one payload from
delivering two independent ones.

This argument retains independent matched blocks and the scalar-total
interface. Separate block floors cannot be summed for a decoder that jointly
mixes different planes. Nor does this price a hypothetical primitive acting
jointly on two full arrays; that needs a new physical contract and bill.

PR2126's `rank_F2 B0[{i,j},{i,j}] = 2` is a correct geometric rank. A rank-two
coefficient block carries two independent totals; the geometric rank alone
does not count their native uses. Plane-port totals are priced on complete
plane spans, not just the original singleton labels. Even a single source's
plane pairing already has rank two.

## Cost decision

Grant the proposed coverage law, ideal hosting and zero extra overhead. For
four pairs, nine stages and 112 ports, `W=896`, `N=9`, `m=73`, `C=224`:

```
mass = 71 W + C N = 65632
capacity = 73 W = 65408
mass/capacity = 293/292
deficit per call = 2(896/9) - 224 = -224/9.
```

For `0 < r < m` and `a >= 0`, `(r/m)^(1-a) >= r/m`. Failure at zero saving
rules out positive saving under this favorable coverage contract regardless
of idle packing. This does not assert that global hosting or the changed
coverage law has been implemented.

## Replay and limits

```sh
python3.12 -I -O -B research/paired-plane-native-payload/verify.py
python3.12 scripts/research_package.py --package research/paired-plane-native-payload
```

The standard-library verifier authenticates inputs before importing them,
reconstructs operators and occurrences, and compares the entire receipt with
`EXPECTED.json`. `--output NEW.json` refuses to overwrite an existing path.
Eight controls cover wrong phase, one-direction drop, stale payload reuse,
missing second payload, disposing of public dirt, missing drop, combined
payload and a half-counted invoice. Input hashes are in `SOURCES.json`.

This is a finite native word and scoped interface/cost audit. Global routes,
a backward interface, chronological owners, all-size lifting, precision/tape,
bit supplier and the selected cold replay are not supplied or rerun. Selected
records and frozen predecessors are unchanged.

## Credit

Cinna Davis / PR1825 and PR2126 supply the matching, endpoint and identity-fit
proposal; Adam Gall / PR1889 supplies the masked scalar target. Credit ctoth's
team for the plane contract and naive baseline, and Philippe Van Velzen for the
one-total model and 2-integral floor at
[pinned fork commit 0e1ecb64](https://github.com/philippeVV/integer-mult-bounds/tree/0e1ecb64d957842954df7639500a7ca96e78da8d/research/plane-port-decoder-screens).
Native machinery derives from Chafik Boukhalfa / PR1991, Ali Romman / PR1862,
icekylinx's retained compiler, and the selected Rohan Arun / Jeremy Kothe lineage.

Scientific base: `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority four.
Overlap and limits are in `TASK.json`. Prepared for Jeremy Diviney with
substantial OpenAI Codex assistance. No independent human or formal-kernel
review is claimed. Apache-2.0.

## Open next questions

The next useful construction is a shared fractional fitting decoder with every
payload priced, or a demonstrably cheaper multi-array primitive. Start with its
complete scalar matrix and actual message factorization before native lowering.
Storage, source access, dirty restoration and hosting must all be included.
Precise next questions and blockers are in `TASK.json`.
