# Prove the exact Gaussian rounding threshold on the radius-five lattice ball with a compact Hall obstruction

## Exact result

For the complete radius-five ball in Z4, the minimum possible maximum
outward norm increment of an injective integer-output approximation to
H4/2 with pointwise Euclidean error at most 1 is exactly
`sqrt(21)-sqrt(19)`. A full 3,121-input injection attains this value.
The explicit signed-permutation identity `H4=L(2C+)R` transfers the result
to the actual ideal Gaussian pair from #6509 and to its conjugate C-.

The lower bound has a short, independently checkable form. Let B19 be the
integer points of squared norm at most19. Remove the complete signed
coordinate orbits with sorted absolute coordinates(0,0,3,3) and(0,1,3,3),
obtaining N with 1,777 points. Add the 32 positive-product signed permutations
of(2,2,2,3), obtaining T with 1,809 points. Every error-one neighbor of T
whose outward increment is strictly below `sqrt(21)-sqrt(19)` lies in N.
Hall's inequality therefore fails by 32.

## Why this advances the question

#6619 asks about outward slack for rational orthogonal rounding; #2589
provides its finite-sphere predecessor and #6509 supplies the Gaussian pair
and a global error-one construction. This package proves an exact finite
optimum and a necessary global lower bound without a period or conserved-sum
premise. The compact lower proof uses 38 signed-coordinate representatives,
rather than trusting a long list of witness inputs or search exclusions.

The global infimum at error cap 1 is only bracketed here by
`[sqrt(21)-sqrt(19),1]`. The upper endpoint uses the inherited #6509 global
construction. A finite injection does not construct a global rounder at the
lower endpoint. The selected exact-layer multiplication route is not rejected.

## Reproduction and independent verification

Canonical base: `e54523517d0f03e58352e647c403a5af3e525a57`.

```sh
python3 -I -W error -B research/sharp-finite-gaussian-outward-slack/verify.py
python3 -I -O -W error -B research/sharp-finite-gaussian-outward-slack/verify.py
python3 -I -W error -B research/sharp-finite-gaussian-outward-slack/compact-hall/check.py
python3 -I -W error -B research/sharp-finite-gaussian-outward-slack/compact-hall/orbit_cut.py
python3 -I -W error -B research/sharp-finite-gaussian-outward-slack/review/check_full_matching.py
```

Default runs are read-only and require only the Python standard library.
The primary checker validates the exact compressed certificate, complete
3,121-input injection, original strict Hall neighborhood and native transfer.
It detects corruption, duplicate output, omitted neighbors, erroneous strict
error and incorrect threshold ties. The standalone compact checker reads no
matching or Hall-list certificate. A separate orbit flow and an independent
full-vertex matching implementation agree on strict optimum 3,089 and the
deficit 32. Including beta equality restores a full matching.

Exact source pins, output receipts, search domain and untouched regions,
proofs and independent review are included. The original proof and checker
remain available alongside the compact supplement.

## Limits, kappa and credit

This is a precision/analytic rounding obstruction, not a new complete
multiplication coefficient or an unconditional multiplication theorem.
**No new kappa; all five framework assumptions remain.** The selected
conditional kappa remains `0.00363005817`. Other radii/error caps, global
attainment, physical caller admission and complete numerical recovery are
outside this package's claim.

Prepared for @CubeJerry with substantial OpenAI Astra/Sol/Luna assistance
in candidate construction, proofs, code and independent review. Credit Nick
Petalas (#6619), ywz65 (#2589), Ali Romman (#6509), and the source authors
identified in SOURCES.json and NOTICE.md. Independent AI implementations
are distinguished from human review or formal-kernel acceptance.
