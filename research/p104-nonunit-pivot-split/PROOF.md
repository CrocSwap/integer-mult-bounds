# A nonzero unit pivot recovers an exact helper split

The source is the complete 30-file export of #7123 at
`020d581d9856b6db83e448c3f20418bc63b72c34`, authenticated by `INPUTS.json`.
The replay reconstructs its entire nested source chain and every byte of its
native word, SHA256
`34cc0c51ca9eaaf2bf3789b8ea2c92f0837b4be9f0fedb22a6150169038e8c38`.
This retains Rohan Arun's #7122 global input rechart, the earlier independent
helper splits, and the exact #7113 signed caller. Frozen evidence is unchanged.

## Exact cut and constructor obstruction

Take the source cut immediately after event 37583, at chart 1027, dimension
5, with pivot 639. The discovery witness describes a neutral placement of
role 643's MOVE from 3 to 1027, at event 37583, over interval [37583,37584).
Removing and reinserting that event at this same cut leaves the source
program byte-identical. The constructor checks the complete interval and
source-read conditions anyway. There is no added MOVE or paid-rank change.
The helper boundary group is 3→127, dimensions 0 and 9.

`WITNESS.json` gives the complete rational vectors a, b, c, d. They have
7, 11, 76 and 347 nonzero entries. With P the prefix through event 37583
and S the suffix, exact arithmetic checks every public input and owned row:

```
aP = c,  Sb = d,  ab = cd = 1.
```

Both c and d use only independent helpers with the common boundary 3→127.
All cut coordinates in a, b, and the pivot are at 1027. The cut vectors are

```
a = e643ᵀ + e640ᵀ/2 + e641ᵀ/3 + 2e1298ᵀ/3
    + e639ᵀ/6 − 17e1300ᵀ/6 − 14e1383ᵀ/3,
b = e643/4 + e641/8 − e1298/16 − e642/8 − e1300/4
    − 3e639/8 − 3e640/8 − 3e645/8 − e1383/16 − e644/4 − e646/8.
```

The original Ali Romman basis routine, including the #7112 zero-pivot
repair, would retain nonzero d639=−7867/16. Normalization then emits
SCALE −16/7867, outside the allowed ring Z[1/30]. That is a failure of this
pivot choice, not a proof that the rational split has no legal scalar basis.
The same direction has d802=3, a unit in Z[1/30]. Both coordinates are in
the same helper boundary group, so the following ordinary cocharted scalar
instructions swap their values even when both entries are nonzero:

```
x639 += x802
x802 -= x639
x639 += x802
x802 *= −1
```

They map (x639,x802) to (x802,x639). Normalization can now scale coordinate
639 by 1/3. The remainder of the attributed elimination routine is unchanged.
The emitter keeps an existing pivot only when its entry is already a unit;
otherwise it selects a unit by the same size/role ordering used in #7112.
Every resulting coefficient is checked: ADD coefficients are in Z[1/30],
SCALE coefficients and their inverses are units, and |q|+1<2^16.
This does not enlarge the instruction alphabet or grant free physical transport.

## Independent arbitrary-input replacement

The emitter produces a boundary basis G of length 426 and a cut basis J of
length 17. Exact row/column elimination gives

```
row639(G)=c,  Gd=e639,  row639(J)=a,  Jb=e639.
```

G is applied at chart 3 and its output-boundary counterpart at chart 127;
J is applied at 1027. Inverses reverse the instruction order and invert each
scalar operation. The complete G/J vectors and programs are reproducible from
`WITNESS.json` and `split.py`, without the discovery search.

Apply G⁻¹, then P and J. Coordinate 639 equals its independent input because
aPG⁻¹=cG⁻¹=e639ᵀ. Retire this field at 1027 and replace its continuation by
a fresh arbitrary input z, new public role 1491. After J⁻¹, S and G, the
output change is GSb(z−x639)=Gd(z−x639)=e639(z−x639). Every other output
is unchanged. The continuing pivot is relabelled to 1491, and owned labels
are shifted by one to keep the inventories disjoint.

This argument uses neither P⁻¹ nor S⁻¹. It retains the source's explicit
initialization and owned-erasure assumptions, including erasure of correlated
nonzero owned content. The fresh public helper is independent, not zeroed.

The retained target is 3→1027 of rank 5; the new target is 1027→127 of rank 4.
The two G/J traversals add 880 ADDs and 6 SCALEs. There are 74,606 events,
1,492 public fields and 1,092 helpers. All 54 owned lifetimes, peak allocation
43, and 23 rises of total mass 56 remain unchanged. The canonical word hash is
`a32696e806c5cde0510cdf2f494e1f14ebb01e73d4ec577413fd7e7c0d9d68b2`.

## Complete application obligation

Relative to #7123, ΔP={} and ΔT={4:+1,5:+1,9:−1} per native invocation.
For H_r=r^(1−κ), the local difference H5+H4−H9 is positive for 0<κ<1.
The signed 17-stage application has ΔT={4:+17,5:+17,9:−17}, unchanged
paid positions and surplus, and no empty credit.

The exact native grid derivation requires 1125/F25; F24 is rejected.
`APPLICATION.md` carries this changed binary height, all basis operations,
independent inputs, odd conversions, forward/adjoint envelopes and physical
and fixed-tape costs into the full application. A positive local difference
alone is not a complete conditional multiplication theorem.

Credit Ali Romman for the helper identity and basis algorithm; dillona/OpenAI
Codex #7112 for the earlier zero-pivot smooth swap; Jerry Chen/CubeJerry for
causal/native/invoice/compiler tools; Matarener for complete kernels/pairing;
Rohan Arun for #7122's rechart and #7113's signed caller; 1337isnot1337/OpenAI
Codex for the alpha-expansion rechart method; ToikY for the retained signed
sources, chart-120 lead and independent chart-259 reproduction; DreamingOfClouds,
Douglas Colkitt/#7000 reviewers and all nested source notices. This nonzero
nonunit-pivot repair was prepared for dillona with substantial OpenAI Codex
assistance; no subagents. Apache-2.0.
