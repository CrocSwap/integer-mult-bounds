# Sharp denominator-capped error of a rounded dirty commutator

This contribution was produced by Nick Petalas. Apache-2.0.

**Scoped written proof with exact finite corroboration; no new κ.** For the
rounded two-factor scalar model in Ali Romman's [Discussion #5257](https://github.com/CrocSwap/integer-mult-bounds/discussions/5257),
the exact maximum absolute completed-target error, when both contractive rational
coefficients have reduced denominators at most the integer D, is

```text
D = 1:  0
D >= 2: 3(D-1)/(2D) grid units.
```

This answers the denominator-restriction part of that discussion's next question.
Its residue law and its limiting 3/2-error family are predecessor results.
The new step is the sharp finite-cap upper bound, attainment at every cap
including even caps, and explicit finite source/dirt bounds for the attainer.
No predecessor census or numerical kernel is replayed.

For example, denominator cap two gives exactly 3/4 rather than the unrestricted
3/2 bound. Restricting both coefficients to dyadic denominator dividing 2^p
gives exactly `3(1-2^-p)/2` for p>=1, and zero for p=0. This follows because
that class lies within the cap 2^p and contains its attaining pair.

## Model and theorem

Let `R(t)=floor(t+1/2)` (nearest, ties toward positive infinity), and let
`a,b` be rationals with `|a|,|b|<=1`. Their reduced positive denominators
are at most D. For arbitrary integer registers x,y,z execute chronologically

```text
z += R(a*x)
y += R(b*z)
z -= R(a*x)
y -= R(b*z)
```

The inverse calls subtract the same rounded quantity. Independently rounding
a negative coefficient is a different operation at half ties. Coefficient
products are exact; there is no overflow or internal rounding of multiplication.
The source and borrowed connector return exactly for every incoming value.
The target increment is `F=R(b(z+r))-R(bz)`, where `r=R(ax)` and z is incoming
connector dirt. The claimed error is `|F-abx|`, uniform in all x,y,z.

On a grid of spacing h>0, replace R by `R_h(t)=h R(t/h)` and require the three
registers on hZ. Dividing the literal word by h gives the integer model, so the
maximum is h times the displayed bound. This is a completed-target statement,
not an internal-state, bit-width or whole-program precision guarantee.

## Proof of the upper bound

Write b=u/v in lowest terms, v>0. Divide `ur=kv+q`, with `0<=q<v`.
Integer translation of R gives

```text
F-br in {-q/v, 1-q/v}; if q=0, F-br=0.
```

Indeed, adding q/v<1 to the argument of a floor changes it by zero or one.
Thus for v>=2, `|F-br| <= (v-1)/v`. This elementary residue observation is
the one used in #5257; its full distribution is not a new claim here.
Since `|r-ax|<=1/2`,

```text
|F-abx| <= |b|/2 + (v-1)/v.
```

Reduced b with v>=2 cannot equal either endpoint ±1. Contractivity therefore
implies `|u|<=v-1`, giving

```text
|F-abx| <= 3(v-1)/(2v) <= 3(D-1)/(2D).
```

This applies to both signs of a,b,x,z and to ties. If v=1, the outer operation
is exact on integer arguments and the error is at most 1/2, below the bound
for every D>=2. Finally D=1 makes both coefficients integers, so every shear
and the full product increment are exact. This proves all upper bounds.

## An attainer at every cap

For each D>=2 choose

```text
a = 1/2, b = (D-1)/D,
x = 2D-3, z = -floor((D-1)/2), and arbitrary y.
```

The fractions are reduced and admitted, and `r=R(ax)=D-1`.
If D=2m, the two outer rounded values at z and z+r are `1-m` and m.
If D=2m+1, they are -m and m. These follow by substitution into R, including
the exact half tie in the even case. In either case the target increment is
D-1 and

```text
F-abx = (D-1) - (D-1)(2D-3)/(2D) = 3(D-1)/(2D).
```

This also establishes that the cap maximum is attained, rather than approached
only as the input or dirt tends to infinity. The same maximum already occurs
under the additional restrictions `|x|<=2D-3` and
`|z|<=floor((D-1)/2)`. These are sufficient witnessing bounds; no minimality
of either magnitude bound is asserted. y can be any integer. For D=1 every
input attains the zero maximum.

## Reproduce

Use CPython 3.12 and the standard library, from the repository root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/denominator-capped-commutator/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/denominator-capped-commutator/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/denominator-capped-commutator
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/denominator-capped-commutator --check-source-history
```

Other hosts may substitute their installed CPython 3.12 path. The direct marker
is `PASS_DENOMINATOR_CAPPED_COMMUTATOR`. The verifier writes nothing; redirect
stdout outside the checkout to retain its generated receipt, which binds all
five package files by SHA256. No result receipt is handwritten.

The fixed finite check enumerates all 2,025 signed contractive reduced coefficient
pairs through denominator eight and all 384,085 source/dirt residue inputs. It
also checks 375 attaining caps (1,125 executions), including dyadic caps through
2^128, and 1,323 signed period fixtures. Normal and optimized commands each
took about 2.1 seconds locally on CPython 3.12.15, below the registered 120-second
limit. These timings are execution-budget evidence, not a performance claim.
For a=u/s and b=v/t, the error has source period st and dirt period t:
translation by st changes r by ut and F and abx by the same integer uv;
translation by t shifts both outer round arguments by v. Thus the finite
coefficient-domain maxima cover arbitrary signed integer inputs, not a chosen
magnitude window. The universal all-cap theorem still rests on the proof above.
Literal Fraction-based four-shear execution is compared at every visited input
with a separately written integer quotient formula. Additional checks cover the
all-cap attaining family, large dyadic caps, signed period identities, integer
coefficients, contractivity/denominator escapes, half ties, inverse semantics,
dirt-dependent output, invalid caps and exact dirty return. No external executable
or predecessor verifier is imported.

## Scope, sources and credit

The [advance CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19601567)
preceded the new verifier. Canonical base is
`e54523517d0f03e58352e647c403a5af3e525a57`, priority revision 8. The selected
record is #7000, κ=0.00363005817; the catalogue's #5599 headline is historical.
Selected source-binding orientation passed; it is not a supplier replay.
The original `uniform-transfer-audit` card changes to this local precision side
result. No selected assumption is discharged and the selected frontier is unchanged.

Credit Ali Romman / aliromman for Discussion #5257's exact residue law,
unrestricted sharpness family and explicit bounded-denominator question.
The construction here specializes that credited family at a finite cap and
extends its stated odd-denominator parameter range to every D>=2; it is not a
new commutator mechanism. Adam Gall / adamgall #2067 supplies the deterministic
correlation question and independent-defect context. Chafik Boukhalfa / chafreaky
#628 supplies the dirty commutator; its retained nonlinear-restoration and
numerical/kernel predecessors keep their credit. Classical floor/residue and
triangle inequalities retain their usual mathematical credit. No broad
literature-priority claim is made. The question URL, author and body SHA256
at retrieval are recorded in TASK.json. The Adam Gall README, catalogue and
selected record are historical Git provenance only, with no runtime dependency.

Live open/account PR lists, recent handoff/active claims, local reservations,
distinctive main-tree terms and merged-PR searches were checked. No matching
cap theorem was found in that coverage; sparse notes, arbitrary diffs and
unpublished work remain limitations. ToikY #6685 studies a refined-helper ABI
with an integer source injection and a fixed coarse output grid, building on
Ali Romman #1135 and Nick Petalas #6666. It does not impose this contractive
rational-pair denominator cap or compute this quantity. Nick Petalas #5931
changes dirty-word split trees under independent defects; its construction is
not used here. Their results are cited without being audited.

## Limitations

This is the specified scalar model and half-up rounder. It does not identify
PR1054's numerical leaf with a single scalar shear, install an actual production
coefficient cap, cover arbitrary rounding conventions, larger trees, approximate
coefficient multiplication, overflow, intermediate magnitude, physical tape
movement, native frames, dirty allocation or a complete paid supplier invoice.
All five selected framework assumptions remain. The selected cold replay,
Lean and Docker are unrun. Independent human and formal proof-kernel review
are unclaimed.

The verifier has no recursion, subprocess, network, dynamic code or writes.
Its scientific loops have fixed finite domains; cap/witness helpers validate
positive integer caps below 2^256. Each function stays below 60 physical lines.
Explicit checks remain active with `-O`. Python Fractions and containers allocate
dynamically, a managed-runtime deviation from fixed allocation; the complete
fixed driver and 256-bit cap restriction bound live data. Only the five named
local files are read for hashes. A fixed-storage implementation would be needed
to remove that deviation. Warning-strict normal/optimized commands are registered;
no separate static type checker is configured.

## Open next questions

For one named production leaf, which coefficient-denominator and input/dirt bounds
can actually be proved? Start by pinning its rounding convention, coefficient
table and entrance grids. Then derive its reduced denominators and pay every
conversion, inverse, temporary, source read, storage and routing operation. The
missing kernel identification and complete bill block any production precision
or multiplication claim. Smaller simultaneous magnitude boxes and larger trees
are left to separate investigations.
