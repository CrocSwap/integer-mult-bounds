# Rank-seven helper408 extraction is impossible at the fixed terminal cut

For both PR2894 parent providers carried by PR2908, arbitrary allowed scalar
input and output basis changes cannot isolate helper408 at its original
rank-seven last frame. Two independent exact implementations produce small
invertible forbidden-input restrictions. The conclusion covers all rational
scalar changes in the declared support class, hence all dyadic ones. It is a
scoped obstruction, with **no new supplier or kappa**.

The question comes from the paired extraction mechanism in
[Discussion2612](https://github.com/CrocSwap/integer-mult-bounds/discussions/2612)
and [PR2908](https://github.com/CrocSwap/integer-mult-bounds/pull/2908). That
predecessor succeeds at rank eight. This package tests whether its first
helper408 extraction could instead stop at rank seven; the ongoing second
and subsequent rank-eight extraction work is a separate question.

## Fixed model and decisive witnesses

Freeze PR2908 at `51309592971e3b5be935599eed2a95404dc7781e`, carrying PR2894
at `18d03c447886895ef9abf888398178e0428533ca`. All data and helper values are
arbitrary. The map `M` contains the 4,583 non-target gates after the prelude,
including all 72 middle warps. Input scalar changes act only on the 226
unprotected zero-frame helpers `H`; zero frame does not mean zero value.
Targets, existing cold entrances, nonzero entrances and initial-correction
sources stay protected.

The complete relaxed terminal support at
`E7=(256,128,66,36,22,8,1)` is

```
R = (105,307,309,314,369,371,373,378,408,572,573).
```

This generously includes nine existing cold helpers and data register105.
For the forbidden input coordinates

```
J    = (14,307,309,314,369,371,373,378,41,572,573),
Jinv = (551,307,309,314,369,371,373,378,550,572,573),
```

the exact restrictions are

```
M[R,J]         = diag(-1/2,1,1,1,1,1,1,1,1/2,1,1),
(M^-1)[Jinv,R] = I_11.
```

Both `J` and `Jinv` are outside `H`. A scalar row supported on `R` whose
pullback is supported on `H` must therefore vanish. Independently, a scalar
terminal column on `R` whose inverse image is supported on `H` must vanish.
Either conclusion contradicts the unit pairing needed to obtain both an
identity row and column in `T M S`. The scalar minors are units over
`Z[1/2]` and survive every representation of this frozen operator word.

[BOUNDARY.md](BOUNDARY.md) derives the full frame eligibility, forward
operator and diagonal minor. [INDEPENDENT.md](INDEPENDENT.md) independently
reconstructs inverse columns and chronological row pullbacks. Both find
zero-dimensional rank-seven spaces in both providers. The complete middle
operators have 11,912 terms and identical canonical SHA256
`d1c29a23fbe07da932c44d9e9b1467ab866894faac115d456eae8e42069aec68`.

The known rank-eight pair passes both implementations. The independent
checker also verifies the literal input/terminal composition, `C S` target
compensation, and reverse-inverse cleanup recipe with 73 private buffers.
Admitting the unavailable rank-eight register42 restores a nonzero pair.
Coefficient, support, compensation, chronology, cleanup and forbidden target
dependency controls distinguish actual defects from source hash failures.

## Favorable budget and why the search stops

The candidate was motivated by removing the original rank-two end climb and
narrowing helper408. Its necessary boundary condition fails, so none of the
following hypothetical saving is realized. Against the actual PR2908 word:

| Item | Actual rank eight | Ideal rank seven hypothesis |
| --- | --- | --- |
| Local child histogram | `{1:2407,2:640,3:262,4:128,5:26,8:8}` | `{1:2404,2:641,3:262,4:128,5:26,8:8}` |
| Helper408 width | 8 | 7 |
| Private cleanup buffers | 73 | 73 |
| Physical families | 66,795 | 66,795 if no further scratch is needed |

`check_budget.py` reconstructs the complete actual and hypothetical profiles
from all 271,728 roles in the pinned 666-call T74 fill. It verifies capacity,
non-overlap, complete role coverage, original compact prefixes and the full
published profile. Let `k_b` be the number of helper408 roles sharing owner
bin `b`, and `r_b` its actual idle rank. Compacting within that bin after
shrinking those widths leaves idle rank `r_b+k_b`, not just `r_b+1`.
For `0<p<1`, the complete raw rank-moment difference is

```
Delta(p) = 666*(-3 + 2^p) + sum_b((r_b+k_b)^p - r_b^p)
         <= 666*(2^p - 2) < 0,          sum_b k_b = 666.
```

The inequality uses concave increments bounded by `k_b`. Every unchanged
local child, all eight center children, bridges and every owner residue are
included. Both profiles have rank mass `65088*74 = 4,816,512`. The full stock
charge is `66304+408+8+73+2 = 66795`.

This is an optimistic ledger, conditional on the original owner's temporal
and family legality, which this checker does not independently re-prove.
Additional frame climbs, scalar compensation, native lowering, cleanup,
routing, precision and outer obligations are unconstructed. The ideal
screen gives them zero additional cost only as a relaxation; it admits
nothing. The exact algebraic obstruction closes this fixed-boundary route
before further synthesis or owner optimization.

## Reproduction and evidence

From the repository root, with Python 3.12 and only the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/helper408-rank7-pairing
```

Each scientific entrypoint is also standalone and uses explicit checks that
remain active under optimization:

```sh
python3 -I -O -B research/helper408-rank7-pairing/verify_boundary.py
python3 -I -O -B research/helper408-rank7-pairing/check_independent.py
python3 -I -O -B research/helper408-rank7-pairing/check_budget.py
```

The checked stdout receipts are in `evidence/`. `SOURCE-PINS.json` binds the
vendored source bytes by SHA256 and Git blob ID; no predecessor executable
is imported. `SOURCES.json` binds the scientific base, selected-record
provenance and priority-revision-5 task catalogue. The selected record is
unchanged. This is finite exact symbolic replay with a written all-basis
implication in the stated model, not formal-kernel proof or full native,
all-size or selected-frontier replay.

## Open next questions

1. Can a paid recovery change the forbidden-input restriction? An explicit
   changed middle or entrance contract could invalidate this obstruction.
   First recompute the eleven coefficients, target compensation and inverse
   cleanup for one concrete new word. No such word, native realization or
   complete invoice is supplied here.
2. Can additional rank-eight paired extractions improve the complete
   supplier? Follow the active Discussion2612 construction with its own
   source pins and owner/admission checks. This rank-seven result does not
   constrain that investigation.

## Attribution

Jeremy Diviney owns PR2908's paired extraction and rank-eight construction;
Jeremy Kothe owns the PR2894 parent word. The earlier input/preload and
exact/native lineage is retained in [NOTICE.md](NOTICE.md) and
[sources/CREDITS.md](sources/CREDITS.md). PR2904's fixed-gate screen is a
different scoped predecessor. This contribution is the rank-seven boundary
obstruction, independent inverse witness and source-bound optimistic ledger.
Prepared for Ross Richardson with substantial OpenAI Codex assistance;
no independent human or formal-kernel review is claimed. Apache-2.0.
