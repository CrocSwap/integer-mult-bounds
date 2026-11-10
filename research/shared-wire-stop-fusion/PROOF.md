# From relocated scalar contacts to a strict recursive gain

## Exact source edits

Indices are zero-based in the exact #7000 word. The insertion point is
immediately before the indicated original event.

| Role | Old MOVE indices | Charts | ADD index | Insert before | New ADD chart |
|---:|---|---|---:|---:|---:|
| 444 | 42729, 43417 | 930 → 246 → 127 | 42730 | 44026 | 127 |
| 448 | 42564, 44023 | 902 → 246 → 127 | 42566 | 44024 | 127 |
| 655 | 33974, 33991 | 3 → 106 → 1052 | 33989 | 33971 | 3 |
| 671 | 33683, 33731 | 3 → 105 → 1048 | 33730 | 29913 | 3 |
| 1306 | 30801, 33977 | 3 → 106 → 1052 | 33976 | 30798 | 3 |

The exact event literals in `EDITS.json` are authoritative. The generator
checks every old MOVE and ADD against the pinned word, enumerates every
intermediate contact with the moved role, and verifies the insertion chart
and operand chronology in the combined edited word.

## Arbitrary-input identity and retained interfaces

Express the value of a field in chart A as its normalized coordinate
vector obtained by applying the inverse of the chart operator `C_A`.
Every MOVE is the identity on this normalized vector. An ADD at a common
chart is `I + a E_ij` on the normalized fields. Two such ADDs commute if
neither writes the other's source. This follows from
`E_ij E_kl = δ_jk E_il`. Events on disjoint fields commute. The relocation
certificate checks every reversed relative order. The eight crossed
overlapping scalar events are all commuting ADDs. No crossed noncommuting
source write, SCALE, COPY, INIT or CLEAR is permitted. The exact grid audit
also compares every affected scalar source row and all 54 owned CLEAR rows
between the source and candidate. Each moved coefficient is a unit ±1.

After each stop contact moves, the intermediate chart has no use on that
field. The two chart transitions compose exactly to `C_C C_A^-1` because
the adjacent `C_B^-1 C_B` cancel. The spans strictly nest `A ⊂ B ⊂ C`, so the
direct MOVE lowers to a positive child of rank `dim C − dim A` with the
retained rank-zero adapters. The four distinct direct maps have their
signed Pauli action, absolute phase and all 512 exact Gaussian columns
checked. The normalized proof acts on arbitrary vectors in every factor
under the retained all-column contract. The finite width-512 replay is a
separate control. No main endpoints, helper credit, owned lifetime, operand
alphabet, caller event or BIT source changes.

## Complete price

The paid rank delta per LOCAL is `{1:−7, 2:+2, 4:−3, 5:+3}`. The complete
delta is 18 times this vector. The sum of paid ranks and all target counts
are unchanged, so the complete rank-mass surplus stays 1,520. For
`p = 1−κ` with `0 < p < 1`, the increase in target-minus-paid moment is

```
18 · [2(2 − 2^p) + 3(1 + 4^p − 5^p)] > 0.
```

Strict subadditivity of `r^p` proves the sign for each fusion. The two
rational checkers use the full literal paid and target profiles. The new
invoice has 23,392 productive targets and 117,522 paid requests. The 90
removed routes reduce #7000's conservative ordinary invoice by 90,000.
The scalar and adapter tariffs retain #7000's units and the proof makes
no new physical conversion assumption.

The tested rational price is 0.00363166992007, with compiler gap
`1/100000000000000`. At this price, the directed enclosures give
`alpha < 1−10^-27`, `gamma < 31/32` and `delta < 31/32`. The written
logarithm power is 2,229, with threshold 14,181,100,000,000,000,000.
The exact input-lift, outer stock and 54+4 ledger inequalities pass.
The complex tested price lies strictly below the retained conservative BIT
pin 0.00376669, which in turn lies below the paired E-free BIT 0.00385248.
The candidate's prefix grid still passes at `S=1125`, with the same source
majorant parameters and an authenticated replay of the attributed envelope
engines. The five framework assumptions and specific source contracts in
the README apply throughout.
