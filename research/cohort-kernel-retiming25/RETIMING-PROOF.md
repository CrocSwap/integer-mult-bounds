# Common-frame retiming and exact paid composition

This note adds only the 25 frame substitutions. The pinned inner sources
retain the source527, PR249 entrance and PR254 response-kernel arguments.

## Local admissibility

Consider a surviving ADD `a += c*b` at common address frame F. Let La,Lb be
the preceding required frames on its two physical roles, and Ua,Ub the next
required frames (including COPY requirements and fixed endpoints). An allowed
replacement F' satisfies

```
span(La union Lb) <= F' <= Ua intersection Ub.
```

It must also be nondegenerate for the retained address form `G = I - J/9`.
The frozen selection in `source/extra-retiming-selection.json` records the
actual input transcript SHA256, record index, scalar operands/coefficient/tag,
old basis SHA256 and explicit integer basis for F'. Every selected frame here
is a maximal-frame change with F contained in F'.

`source/code/extra-retiming.py` checks those frozen identities, reconstructs
all MOVEs from the required ADD/COPY frames and fixed initial/final frames,
and rejects any retreat. A second census ignores the emitted MOVEs and
reconstructs every role's paid path from its requirements. Equality of those
censuses is checked. Exact annihilator inclusions and complementary dimension
differences check both reflected ledgers. Every used basis has a freshly
computed nonzero cleared Gram determinant; the finite excluded factors are
checked against the retained prime range. Independent native chronological
legality is then rerun on the final physical transcript.

The full scalar/COPY projection is compared byte-for-byte before and after
retiming. It includes all ADD operands, coefficients and categories and all
COPY/ERASE instructions in order. Therefore the already checked local forward
and inverse scalar maps and their arbitrary-dirt restoration are unchanged.
The final word is additionally replayed through all five global stages on
all 23,627 formal F2 columns. COPY source requirements and lifetimes remain
fixed throughout; they are not free temporary storage.

## Complete paid ledger

For 24 ADDs, the net paid change per gate is `(5,5) -> (4,6)`. For the
additional read it is `(2,2,11,17) -> (13,13,6)`. The combined local delta is

```
rank:    2    4     5    6   11   13   17
delta:  -2   24   -48   25   -1    2   -1
```

The rank-weighted sum is zero; the multiplicity sum is -1. Multiplying by
five stages and 40 replicas removes 200 literal positive-rank children and
preserves rank mass. The native finite invoice reads the final records rather
than importing this delta as its inventory. Input/output frames and entrance
families are unchanged, so the admitted literal bank stock and the actual
role/replica/stage assignment stay byte-identical to PR254's allocation.
Normalized pricing divides literal stock and child multiplicities by five.

For `0 < a < 1`, the function `r^(1-a)` is strictly concave. Consequently each
`(4,6)` pair costs strictly less than `(5,5)`. The additional read and every
other paid child are included in the exact combined moment; no standalone
estimated gains are added to obtain the reported saving.

The native exact checker prices that complete profile, retaining the bad-case
envelope, ordinary bootstrap and outer assembly. It obtains

```
kappa = 71046804825911 / 100000000000000000
```

Two independent Python moment engines using different interval expansions
reconstruct the profile from the final physical word and actual bank receipt,
verify the same coarse grid point, and reject its successor. The independent
outer assembler checks all 47 strict constraints and seven margins and rejects
the next kappa grid point. The finite invoice retains selector, routing,
boundary, signed-prefix and cutoff charges. Its counted primitive coefficient
has 56 bits; the payload prefix bound has 95 bits below its 104-bit guard.

## Limits

The local frame and paid-composition checks do not reprove the inherited
all-size compiler, common weighted chart, routing, prime supply, complex
recovery, symbolic or analytic interfaces. New recursive children use those
same retained interfaces. This is a finite exact conditional contribution,
not an unconditional multiplication theorem or Lean/kernel certification.
