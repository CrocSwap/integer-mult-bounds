# Opcode 1's dimension-8 images of the Y exits

This is an exhaustive finite census on one recorded alphabet. The selected
value stays `363005817/100000000000`. A chart-image hit is not a warp event
in the word, not a paid-moment change, and not a new κ.

The word is the pinned round-three centre word
`research/sol1337-contact-frontier/inputs/round3-native.json.gz`, SHA-256
`7679daa4ec6a40f56fc7f0202379a6f454310e94945aba4f48beaaaafb838d05`, the same
bytes `retained_verify.SOURCE_HASH` names. Cao Yifan / intqwq, PR #4610, is
the source of the word. The span operation is `model.span` from the
contact-graph model. The question is the first open question of PR #7219:
which dimension-8 charts opcode 1 carries a Y-exit chart onto. PR #7219
proves that the image has dimension 8, and stops before naming the chart.

## Hypotheses

The ambient space is `GF(2)^9`. Opcode 1 is the first record of
`canonical["warps"]`. Its columns are

```text
(1, 2, 4, 8, 64, 19, 104, 197, 325).
```

The map is `G(x) = xor of column i over each bit i set in x`. The native
chart-image law admits an ordered pair of charts `(A, B)` for this opcode
only when `span(G(basis of A)) = span(basis of B)`.

The Y-exit charts are `final[112]` through `final[223]`. On this word those
112 values are the frames `142` through `253`, in that role order, and each
basis is independent of length 8. Frame 1 is the unique dimension-9 chart,
and each Y-exit span sits strictly inside it.

A recorded chart can equal a dimension-8 image only if its own basis has
length 8. There are 4429 recorded frames, and 162 of them have basis length
8. Those 162 spans are pairwise distinct, so each image subspace equals at
most one of them.

## Dimension

`G` is additive and sends the 512 vectors of `GF(2)^9` to 512 distinct
images, so `G` is a linear automorphism. The image of an independent set of
size 8 is independent of size 8: a linear dependence among the images would
pull back, under `G^{-1}`, to a dependence among the inputs. Every Y-exit
image therefore has dimension 8, and none of them is frame 1.

## The census

The domain is the 112 Y-exit charts. For each one the checker builds
`span(G(basis))` with `model.span` and compares that set with the 162
dimension-8 spans. The comparison is exhaustive: every source and every
dimension-8 chart is visited, and no other recorded chart has a
dimension-8 span. The classes below are a partition of the 112 roles.

Four images equal the source chart itself.

```text
certificate fixed role=129 source=159
certificate fixed role=189 source=219
certificate fixed role=208 source=238
certificate fixed role=209 source=239
```

Twenty-four images equal a different Y-exit chart. The destination role is
`destination frame - 30`, because Y-exit frame `142 + t` belongs to role
`112 + t`.

```text
certificate y-to-y role=116 source=146 dest=147
certificate y-to-y role=117 source=147 dest=146
certificate y-to-y role=119 source=149 dest=228
certificate y-to-y role=137 source=167 dest=224
certificate y-to-y role=144 source=174 dest=173
certificate y-to-y role=164 source=194 dest=192
certificate y-to-y role=165 source=195 dest=191
certificate y-to-y role=166 source=196 dest=195
certificate y-to-y role=167 source=197 dest=194
certificate y-to-y role=171 source=201 dest=207
certificate y-to-y role=172 source=202 dest=206
certificate y-to-y role=185 source=215 dest=210
certificate y-to-y role=186 source=216 dest=211
certificate y-to-y role=187 source=217 dest=214
certificate y-to-y role=188 source=218 dest=217
certificate y-to-y role=192 source=222 dest=167
certificate y-to-y role=198 source=228 dest=151
certificate y-to-y role=206 source=236 dest=235
certificate y-to-y role=207 source=237 dest=236
certificate y-to-y role=210 source=240 dest=242
certificate y-to-y role=220 source=250 dest=248
certificate y-to-y role=221 source=251 dest=247
certificate y-to-y role=222 source=252 dest=251
certificate y-to-y role=223 source=253 dest=250
```

Eleven images equal a recorded dimension-8 chart that is not a Y exit.
None of those eleven frames occurs in `start` or `final`.

```text
certificate non-y role=124 source=154 dest=3445
certificate non-y role=125 source=155 dest=3438
certificate non-y role=128 source=158 dest=624
certificate non-y role=147 source=177 dest=3453
certificate non-y role=156 source=186 dest=281
certificate non-y role=168 source=198 dest=3450
certificate non-y role=202 source=232 dest=4425
certificate non-y role=203 source=233 dest=4427
certificate non-y role=213 source=243 dest=4377
certificate non-y role=214 source=244 dest=4381
certificate non-y role=219 source=249 dest=3449
```

The other 73 images are dimension-8 subspaces that equal none of the 162
recorded dimension-8 spans. Role 112, frame 142, is in this class: its image
equals none of the 112 Y-exit spans and none of the 162 recorded
dimension-8 spans.

```text
certificate unrecorded count=73
```

Two of the Y-to-Y rows are mutual. Opcode 1 carries frame 146 onto frame 147
and frame 147 onto frame 146. It likewise exchanges frames 235 and 236.
The other Y-to-Y rows are not mutual. Frame 149 goes to frame 228, and frame
228 goes to frame 151.

## What the census does not say

The chart-image law admits the 4 + 24 + 11 ordered pairs above for opcode 1.
Admitting a pair does not insert a warp into the recorded program, does not
delete a transport, and does not change a paid histogram. The 73 misses say
only that opcode 1 does not carry that Y exit onto a recorded dimension-8
chart. They do not say that some other retained opcode misses it, and they
do not say that the inverse opcode `-1` misses it.

The selected frontier stays `363005817/100000000000`.

## Open next questions

1. Does any of the 24 Y-to-Y chart images occur as a warp event that leaves
   the paid transport count unchanged? The first step is the mutual pair of
   frames 146 and 147. Nothing in this census edits the word.
2. Which of these 112 charts does the inverse opcode `-1` carry onto a
   recorded dimension-8 chart? The inverse is a different signed map. This
   census does not evaluate it.
