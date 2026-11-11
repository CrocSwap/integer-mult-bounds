# No retained warp opcode changes dimension

This is a scoped proof about one recorded alphabet. The selected value stays
`363005817/100000000000`. The impossibility is the chart-image law on this
alphabet. Every other warp alphabet stays outside the statement.

The word is the pinned round-three centre word
`research/sol1337-contact-frontier/inputs/round3-native.json.gz`, SHA-256
`7679daa4ec6a40f56fc7f0202379a6f454310e94945aba4f48beaaaafb838d05`, the same
bytes `retained_verify.SOURCE_HASH` names. Cao Yifan / intqwq, PR #4610, is
the source of the word. The open question is the second question of PR #7102:
the 240 emitted warps preserve dimension, and a dimension-changing warp would
be a different alphabet. This note answers that question for the alphabet the
word already records.

## Hypotheses

The ambient space is `GF(2)^9`. `canonical["h"]` is 9. Every chart basis
vector is an integer in `0..511`, and the retained span test makes the basis
independent. The dimension of a chart is the length of that basis.

The recorded alphabet is `canonical["warps"]`. It is a list of 72 records
whose `op` fields are exactly `1..72` in that order. Record `k` stores a
source chart `from_frame`, a destination chart `to_frame`, and nine columns
`G_columns`. Those columns define the linear map `G_k` by

```text
G_k(x) = xor of column i over each bit i set in x.
```

The retained inverse opcode `-k` is the column-wise inverse used by
`model.inv`: the unique vectors sent to the standard basis. The emitter and
`model.graph` both keep these 144 signed maps. A free-word symbol, including
the dual label that adds `1000000` in `retained_verify.emit`, is not another
spatial map.

The chart-image law is the native monomial rule. Opcode `σ` admits an ordered
pair of charts `(A, B)` only when `G_σ` carries the span of `A` onto the span
of `B`. That is the check `model.build` states as “original native warp is
monomial”, and the check `model.build_pauli` states as “native chart image”.
`retained_verify.replay` does not apply this law: after editing the free word
it assigns the role’s chart to the event’s destination. An assignment that
fails the chart-image law is outside the alphabet. This note does not
construct one.

## The dimension lemma

Let `G` be a bijective linear map on `GF(2)^9`, and let `v_1, ..., v_d` be a
basis of a subspace `V`. If a subset of `G(v_1), ..., G(v_d)` sums to 0, apply
`G^{-1}`: the same subset of `v_1, ..., v_d` sums to 0, so the subset is
empty. The image vectors are therefore independent, and they span `G(V)`.
Hence `dim G(V) = dim V`.

Every subspace is covered, including a chart that is not a recorded endpoint
and a chart that none of the 240 emitted warps uses.

## Census of the 72 maps

The checker evaluates each of the 72 column lists on all 512 vectors. Each
list is additive, has column rank 9, and has 512 distinct images, so each
`G_k` is a linear automorphism. Each inverse agrees with `model.inv`, is a
two-sided inverse, and is an automorphism as well. The domain of this census
is the whole list `canonical["warps"]`. The opcode check rejects any proper
sublist, so a sample of the records is not this census.

Opcode 1 is the named map. Its columns are

```text
[1, 2, 4, 8, 64, 19, 104, 197, 325].
```

It joins frame 292 to frame 293. Both charts have dimension 4, and `G_1`
carries the span of frame 292 onto the span of frame 293. The two spans are
distinct: their Fourier rank, in the sense of `model.fourier_rank`, is 4.
Opcode 1 changes the chart and preserves the dimension.

The same endpoint check on all 72 records gives 50 opcodes of dimension 4 and
22 of dimension 5. Every recorded pair is a chart image, so the monomial
Fourier rank between the image and the destination is 0. No recorded opcode
has unequal endpoint dimensions.

## Unequal pairs are inadmissible

Suppose `G_σ(span A) = span B` for a retained signed opcode. The lemma gives
`dim A = dim B`. An unequal pair fails the chart-image law for every retained
opcode.

Frame 1 is the unique dimension-9 chart, and its span is the whole space.
Roles `112..223` end on 112 distinct charts of dimension 8, each a strict
subspace of frame 1. The Fourier rank of any such chart against frame 1 is 1,
the same width a transport would pay. For every one of the 144 signed maps and
every one of these 112 charts, the image has dimension 8 and Fourier rank 1
against frame 1, so the image is not frame 1. No retained opcode admits a
warp from a Y exit onto frame 1.

The 240 emitted events never use a dimension-8 chart. Their source-dimension
multiset is `{0: 72, 1: 24, 4: 50, 5: 22, 9: 72}`. Looking at some of those
events cannot see a dimension-8 pair. The prohibition on that pair is the
lemma, applied to the census of the 72 maps.

## Products

A composite of bijective linear maps is bijective and linear, so the lemma
applies to every finite product of retained opcodes and inverses. Along a walk
whose steps are admitted chart images, the dimension is constant. No such walk
carries a dimension-8 Y exit onto frame 1. The checker evaluates the composite
`G_1 ∘ G_2` as a fixture of that lemma. It does not enumerate the group
generated by the 72 maps.

## The emitted events, recomputed

This recount is an exhaustive census of a second finite list. It is the list
PR #7102 already used. It is recorded so the off-endpoint uses are visible,
and it is not the reason an unused unequal pair is forbidden.

There are 240 emitted warp events, each on a live role. Each opcode is one of
the 144 signed retained maps, each event preserves dimension, and each event
is a chart image of its opcode. Of the 240, 72 land on that opcode’s oriented
recorded endpoints. Those 72 are exactly the events of dimension 4 or 5.
The other 168 land on other charts, with source dimensions
`{0: 72, 1: 24, 9: 72}`. The alphabet is used at dimensions other than its
recorded endpoint dimensions.
`canonical["warp_edges"]` is exactly the set of those 240 events collapsed to
180 classes `(sign, opcode, source, destination)`, and each class preserves
dimension.

## What this statement leaves open

The selected frontier stays `363005817/100000000000`. Opcode 1 is a chart
change inside one alphabet, not a selected-word decoder and not a new κ.

The restored Y-exit round trip priced by PR #7102 is unchanged. Accepting the
one-way move onto frame 1 as an endpoint is a different contract. Same-
dimension relocation of a Y exit, by a retained opcode whose image happens to
be another rank-8 chart, is still open; the lemma says the image has dimension
8 and says nothing further about which chart it is.

A warp alphabet other than these 72 maps and their inverses can still contain
a dimension-changing map. The free-word replay can still be given a chart
assignment that ignores `G`. Both of those objects are outside the hypotheses.
