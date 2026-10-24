# Independent review of the literal rank-thirty capture word

The literal common-chart word passes this review. Both scalar
directions, both complete response chains, all stated costs, and
all stated prefix bounds agree with independent exact checks.
There is no material finding.

Each direction uses 2,910 old real scalar units and 44 real
fixed-odd scans. It uses no new field, no native child, and no
address map inside the common chart. These are local scalar costs.
A physical source cut, its views, and its native controller are
not admitted by this review.

The review binds `CAPTURE-WORD.md` at SHA256
`29386ef90deb1eff60f88a42d74b35d9474fad73a50e540485b212bdb3f9891a`.
The literal payload has SHA256
`8761a302a154e4e19fedb22a9ccfe1db710ce16b3edf2a0e3704a6d0b837d303`.
`SOURCE-MANIFEST.json` gives the complete input paths and hashes.
No producer module was imported or executed.

## Independent operator checks

The checker uses two methods.

- Forward replay carries 640 formal input columns through every
  event. It checks exact division and each stored prefix.
- Backward accumulation carries each output linear form through
  the events in reverse order. It gives a second complete
  operator calculation on all 640 roles.

The target capture and inverse are reconstructed from the actual
U, V, U_A, and B0. The checker verifies both selected-minor inverse
orders and VU=B0. It compares the resulting matrices with the
separately reviewed unnormalised-code payload.

The two methods agree on the full capture and the full generic
inverse. Both inverse composition orders are the identity. Both
complete scalar chains agree directly with the actual source
`response` and `response_inverse` matrices:

```text
Csum^-1 diag(G0,I_O) Csum = E,
Csum^-1 diag(G0^-1,I_O) Csum = E^-1.
```

Every event reads and writes only indices 0 through 111. All 528
other rows are unchanged and all 528 other input columns are
absent from the data outputs. These roles are arbitrary formal
inputs. There is no zero-state assumption.

The 550-event inverse is exactly the reverse of the 550-event
capture, with each gate inverted. No field is cleared or replaced
by an assumed zero.

## Four exact blocks

The independent backward calculation checks each block against
its source matrix before it checks the full word.

| Block | Events | Old real scalar units |
| --- | ---: | ---: |
| Selected U_A inverse | 102 | 498 |
| Complement scatter | 252 | 1,248 |
| B0 | 76 | 204 |
| V_O gather | 120 | 960 |
| Total | 550 | 2,910 |

The selected-minor word has 49 unit ADDs, 39 signs, and 14 binary
scales. Its endpoint is the exact source U_A inverse on all
selected columns. The pair transforms, signed permutation, and
three coefficient-two shears preserve all ordinary fields.

The complement block contains all 124 actual U_O terms: 64 have
absolute coefficient one half and 60 have absolute coefficient
one. The checker parses each temporary source scale and requires
its opposite scale immediately after the ADD. Thus the source is
restored before the next term. The final gather contains exactly
the 120 actual V_O unit terms.

The complete capture has 309 ADDs, 69 signs, 150 one-bit binary
scales, and 22 complex odd multiplications. The inverse has the
same first three counts and 22 complex odd divisions. The old
scalar sum is

```text
309*8 + (69+150)*2 = 2910.
```

There are eleven complex operations with factor three and eleven
with factor five in each direction. Each complex operation acts
on two real fields. Thus capture has 22 real multiplications by
three and 22 by five; decode has the corresponding divisions.

Either complete capture, centre action, and decode chain costs
6,090 old units. It has 22 real multiplications and 22 real
divisions for each of three and five. The centre action or its
inverse contributes 270 old units.

## Prefix precision and exact division

The following independently computed bounds equal the producer
receipt. Row norms refer to the maximum absolute input component.
The ADD bound is the sum of both operand norms before the ADD.

| Execution | Stored row norm | ADD operand norm | Binary height | Odd height |
| --- | ---: | ---: | ---: | --- |
| Capture | 15 | 21 | 1 | 0 |
| Generic inverse | 9 | 13 | 2 | 1 at three and five |
| Inverse on Csum a, relative to a | 15 | 21 | 1 | 0 |
| Capture, G0, decode | 44 | 52 | 1 | 0 |
| Capture, G0 inverse, decode | 44 | 66 | 2 | 0 |

For each valid execution, every coefficient before an odd division
has denominator coprime to the divisor and numerator divisible by
the divisor. The checker tests this before each of the 22 complex
divisions. All prefixes remain dyadic. The proof applies to
arbitrary dyadic real and imaginary input components by linearity.

The same binary grid must include the stated fractional-bit
guard. With that guard, each corresponding integer numerator is
divisible by the odd divisor. The valid executions need no odd
root scale. This does not remove their stored-value and
temporary-operand guards.

The generic inverse has a different contract. As a separate exact
check, the checker starts every one of the 640 input roles at
60 times its formal integer value. All generic inverse prefixes
are then integral, all odd divisions are exact, and all 528
unrelated roles retain that same common scale. Here

```text
60 = 2^2 * 3 * 5.
```

This is a local sufficient grid for the generic inverse. It is
not a recursive denominator theorem. Generic inverse input is
not assumed to satisfy the valid-code conditions.

A complete valid encode, centre action, and decode returns to
the dyadic representation on all roles. Such completed chains
have no residual odd height to charge to a later sibling.
A recursive caller must still establish each valid input type
and its complete precision bound.

## Fixed-odd scan charge

The review binds both the retained A8 scan proof and the general
fixed-odd carry extension in `CLIQUE-CODE-GRID.md`. The A8 proof
has SHA256
`e0210105ba6c6246f1f84c8ce2d92cfd07aa6cc8a161ca27d7fcc8e0183cfb01`.
The general extension has SHA256
`c06fab014b9dee89b45b1c18c7e3c8a3140a04416f3c63fe52a3f39ac0159639`.

For fixed odd d, the in-place low-to-high division uses

```text
a = (b-c) mod 2,
c' = (c+d*a-b)/2.
```

It keeps 0<=c<d. Summation gives the unsigned identity
dQ=N+2^w c_final. The signed exactness condition is
c_final=d s_Q-s_N. The fixed multiplier has the corresponding
finite-carry recurrence and a signed overflow check. The guarded
width must make that check pass.

The four head passes cover at most 4(w_g+1) arithmetic-head
steps per real record and scan. Therefore 44 scans cost at most
176 n(w_g+1) such steps for n records per real field. Either
complete scalar chain has the bound 352 n(w_g+1).
The coefficient four excludes descriptor and counter work.
Their separate linear charge remains due. No extra numerical
field is used by the finite carry.

## Physical boundary and reproduction

The interfield ADDs require the stated common linear frame.
Their scalar matrices then commute with that common frame.
They do not commute with arbitrary independent frames on the
112 fields. No common chart at a native source cut was checked.

The formal entry code Csum Q^2 has 112 input-side translations.
Its inverse puts those translations after Csum^-1. The order
follows from matrix inversion. This review does not emit those
translations, check their physical source views, or price their
address maps. It does not supply the odd transported code for
free.

Normal and optimized independent runs have identical receipts:

```text
python3 -I -B check_review.py --out fresh-normal
python3 -I -O -B check_review.py --out fresh-optimized
```

Both return `PASS_INDEPENDENT_CAPTURE_WORD_REVIEW`.
The checker also checks equality of the producer's normal and
optimized outputs. All pinned inputs are hashed before and after
the computation. Their bytes are unchanged. No native supplier
was replayed; the 640-column checks are checks of this scalar
word.

No PR, commit, push, or publication is authorized. Before any
future PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
