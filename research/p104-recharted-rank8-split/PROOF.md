# A recharted input enables a further independent helper split

The complete nine-file export of Rohan Arun's #7122, head
`98aad9eb0e7d7f985622a35c7981695fe680c68a`, is frozen in `INPUTS.json`.
It retains the entire #7121 export and all nested source notices. The replay
reconstructs #7121's word `0a27f1224fdb196602d52d4170bc12b8bde0b9818809e73ecdbdaaa5d3b7adbc`
and the exact #7122 word `880a2402e01a6a92ce8bfde2046fa6375014b16ca4f89d6cc6f5cead621e54f8`.
The copied `rechart.py`, `RECHART.json` and `PEER-EARLY.json` must be byte-identical
to their credited files in that public export. Its early receipt does not
claim a completed physical/application replay.

Rohan Arun's rechart changes seven helper input frames and 22 public scalar
contact frames. Scalar coefficients and order are retained. The constructor
rebuilds every public causal transport and retains each owned transition and
lifetime. Every contact is cocharted, every public transition is nested and
increasing, and every helper target is strictly productive. Formal MOVE
operations are identities, so the unchanged scalar word has the same
arbitrary-input coefficient operator. The new physical interpretation and
costs still require the complete chart/caller checks in APPLICATION.md.
No free transport or credit from a zero-initialized public helper is assumed.

In particular, input 1445 moves from chart 105 to chart 3. Its target remains
246, so it can now share a boundary basis with independent helpers
454,1208,1461 in group 3→246, dimensions zero and eight. This basis was not
legal on #7121, where 1445 started at 105. That changed interface is the
reason for this follow-up; the global rechart itself is Rohan Arun's result.

## Exact causal cut

Use cut 40552 of the exact #7122 program, just before event 40552. Advance
role 454's single rank-one MOVE, event 42238 from 757 to 924, to this cut.
The declared interval [40015,42239) contains that MOVE and no scalar contact
or source read of 454. Chart dimensions are 6→7. The checker verifies every
role event, source read, interval boundary and old/new paid histogram.
This retiming preserves the scalar operator and the entire paid Counter.
All cut fields and the pivot now occupy chart 924, a strict intermediate
between 3 and 246.

Writing P for the retimed prefix and S for the suffix, exact rational checks
on every public input and owned row establish

```
a = e1461ᵀ − e1208ᵀ/4,
b = e454/3 − e207/3 + 4e1208/3 + 4e1461/3,
c = e1461ᵀ − e1208ᵀ/4 + e454ᵀ − e1445ᵀ/2,
d = e454/3 + 2e1445/3 + 4e1208/3 + 4e1461/3,
aP = c,  Sb = d,  ab = cd = 1.
```

Only c and d must lie in the common helper boundary group. The cut vectors
may also use main role 207, whose chart availability is checked explicitly.
The attributed Ali Romman routine emits these bases:

```
G at chart 3:
  x454 *= 3
  x1208 -= 4x454/3
  x1445 -= 2x454/3
  x1461 -= 4x454/3
  x454 -= x1208/4
  x454 -= x1445/2
  x454 += x1461

J at chart 924:
  x454 *= 3
  x207 += x454/3
  x1208 -= 4x454/3
  x1461 -= 4x454/3
  x454 -= x1208/4
  x454 += x1461
```

They satisfy row454(G)=c, Gd=e454, row454(J)=a and Jb=e454.
Their inverses reverse instruction order and invert each operation. Every
scalar in both directions is in the retained 2,3,5-smooth alphabet.

Apply G⁻¹ at the input boundary, followed by P and J. Coordinate 454 equals
its original independent input because aPG⁻¹=cG⁻¹=e454ᵀ. Retire this field
at 924 and replace its continuation by a fresh arbitrary input z, role 1490.
After J⁻¹, S and G at output boundary 246, the output change is
GSb(z−x454)=Gd(z−x454)=e454(z−x454). Every other endpoint is unchanged.
This uses neither P⁻¹ nor S⁻¹ and retains the owned initialization/erasure
assumptions. The continuing pivot is relabelled to 1490, and owned labels
are shifted by one to preserve disjoint inventories.

The retained target is 3→924 of rank 7 and the fresh target is 924→246 of
rank 1. Relative to #7122, the split adds 22 ADDs and four SCALEs, with no
added paid positions. The whole combined word has 73,720 events, 1,491
public fields and 1,091 independent helpers; all 54 owned lifetimes, peak
43, and 23 rises of mass 56 remain unchanged. Its canonical hash is
`34cc0c51ca9eaaf2bf3789b8ea2c92f0837b4be9f0fedb22a6150169038e8c38`.

## Complete invoice obligation

For H_r=r^(1−κ), the incremental signed gain over #7122 is H7+H1−H8>0
for 0<κ<1. Relative to #7122, ΔP={} and ΔT={1:+1,7:+1,8:−1} per native.
Relative to the fully retained #7121 word, the combined changes are
ΔP={1:−6,2:+1,3:+1,4:−8,5:+8} and
ΔT={1:+1,4:−2,5:+2,8:−4,9:+4}. The signed 17-stage caller multiplies these
changes by 17. Its surplus remains 1424 and empty credit is zero.

The new scalar bases, fresh input, odd conversions, complete envelopes,
physical maps and ordinary/fixed-tape costs are charged in APPLICATION.md.
The full replay recounts #7121, #7122 and the candidate rather than importing
the peer's reported gain as a cost certificate. A positive local tariff is
not by itself a completed component application or a multiplication theorem.

Credit 1337isnot1337/OpenAI Codex for the fresh-helper-boundary alpha-expansion
method used by Rohan Arun; credit Rohan Arun for #7122's rechart and #7113's signed caller/application;
Ali Romman for the independent helper and basis identity; Jerry Chen/CubeJerry
for causal/native/invoice/compiler tools; Matarener for complete discovery
kernels and pairing; ToikY for the retained chart-120 pattern, signed sources
and subsequent independent chart-259 reproduction; DreamingOfClouds,
Douglas Colkitt/#7000 reviewers and every retained source notice. This added
split was prepared for dillona with substantial OpenAI Codex assistance;
no subagents. Apache-2.0.
