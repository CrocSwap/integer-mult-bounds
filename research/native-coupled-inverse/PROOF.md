# A native inverse with the same paid Gaussian profile

This construction inverts the coupled provider from
[PR #5402](https://github.com/CrocSwap/integer-mult-bounds/pull/5402), at
`3348fccea855082786d5f0fc5558b73d4974e745`. It preserves all 632 original
input directions. Nine temporary fields can start with arbitrary values and
finish zero. No new Gaussian child is needed. The inverse needs additional
ordinary operations, which are counted below.

This is an enabling construction. It gives no new kappa, complete caller,
autonomous credit for the eight coupled outputs, or selected-result change.
The physical source implementation and its interpretation at every positive
fiber width remain inherited premises. The source replay is run again.

## Exact physical map

Use the source notation. Q is the central Gaussian, D is the product on the
eight other axes, and R = DQ. W and Z are the specified ordinary maps between
112 main fields and eight mode fields. They satisfy ZW = 14I, WZ = I - C,
RW = WR, and RZ = ZR, with the appropriate domain on each side. Do not commute
W or Z through D or Q separately.

The source map is

```text
X = D x - R y + R W h
Y = D y
H = D(h - Z y).
```

Its inverse is

```text
y = D^-1 Y
h = D^-1 H + Z D^-1 Y
x = D^-1 X + Q C D^-1 Y - Q W D^-1 H.
```

The first two equations give y and h. Substitution in the X equation gives
the third equation, since C = I - WZ. This derivation retains operator order.
It proves the map is invertible; it does not alone give a native schedule.
The schedule below supplies that missing implementation. The other 400 fields
undergo the inverses of their original autonomous helper maps.

## Remove the unused center accumulator

The changed source word has no paid operation on C0. Its live center uses have
this form, in the same chart:

```text
CLEAR C0
COPY C0, Ck
ADD Lr, C0, -1
CLEAR C0
```

Replace the live ADD by `ADD Lr, Ck, -1`. Delete all scalar writes to C0.
Before each replaced center, the old accumulation in C0 is erased without a
read. In total, 176 ADDs, eight COPYs and 24 CLEARs are removed. The eight
source sites and their cache fields are in RESULT.json. One entry CLEAR keeps
the unused C0 field zero under the retained nine-field temporary interface.

The source interpreter checks every endpoint row, every persistent/cache
exit chart, and every paid call before and after this change. The final chart
of the unused zero C0 field is immaterial; no original field is excluded.

The remaining word consists of invertible ADDs, nonzero SCALEs, native maps,
paid children, eight initial cache CLEAR/COPY pairs, and eight retags of
identically zero persistent fields. Each retained cache is read but not
changed until the final whole-field swap.

## Reverse the complete word

Reverse the physical output boundary first. Clear the nine temporary fields.
Undo each final whole-field swap, including its chart. Apply the inverse cache
normalizer and its inverse scalar. The original persistent mode field is now
zero, while the cache contains the corresponding independent output input.
Apply the inverse output helper basis, then run the reduced native word in
reverse order:

- Negate an ADD coefficient and invert a nonzero SCALE coefficient.
- Invert a native map and reverse its chart transition.
- Invert a paid child and reverse its chart transition. Keep its rank.
- Reverse a zero retag only after its row is proved zero.
- Replace a cache COPY by subtraction of its restored source field.
- At an initial cache CLEAR, verify that its row is zero and do no operation.

Finally invert the input helper basis and the physical input boundaries.
All eight inverse COPY operations return their cache rows to zero. Clear
the eight owned cache returns after this check. C0 stays zero. The verifier starts with 641 distinct formal input columns, erases only
owned entry dirt, and checks both compositions against the identity on the
632 original columns. It also checks the inverse endpoint against a separate
closed formula in the source scalar coordinates:

```text
y = Y
h = H + M^T Y
x = X + (I - M M^T/4) Y - M H/4.
```

Here M has 112 rows and eight columns. The source file stores its transpose.
The physical boundary maps convert this formula to the ordered physical
inverse above. All 464 boundary adjoints are checked with both signed
Clifford tableaux and absolute phase. Source adapter and phase annotations
retain their physical interpretation in reverse order; they are not new
scalar row operations. Internal native maps use their actual inverses.

For a positive rank-r Gaussian child G, `G^-1 = X G`, where X translates the
r active bits. Thus a descending child needs one rank-r positive call and at
most one additional ordinary translation. The verifier checks the exact phase
identity for ranks 1 through 9. Tensoring this identity gives the same result
at every positive fiber width. Scalar coefficients in the owner program are
applied once; the program does not tensor a sum over owners.

Every other operation is reversed literally. The free-group row proof holds
for each evaluation of the native maps by invertible operators. This proves
the all-width inverse within the inherited native implementation model.
No formal proof kernel or independent human review is claimed.

## Complete local bill and limits

Both directions use the paid profile
`{1:2193, 2:412, 3:510, 4:127, 5:40}`: 3,282 child calls and rank mass 5,255.
The 400 autonomous helper jobs retain inverse Gaussian ranks
`{4:28, 7:7, 8:47, 9:318}`. The remaining eight fields are coupled; they get
no autonomous target credit.

| Explicit operation | Reduced forward | Inverse |
|---|---:|---:|
| ADD | 17,741 | 17,749 |
| SCALE | 1,204 | 1,204 |
| COPY | 8 | 0 |
| CLEAR | 17 | 17 |
| Whole-field SWAP | 8 | 8 |
| Physical boundary monomial maps | 464 | 464 |
| Additional child-inverse translations | 0 | at most 3,282 |

The CLEAR count includes eight terminal owned clears in each direction.
They act on certified zeros in the exact model.

The native word's 240 internal warp records remain. Its 448 adapter and ten
phase annotations retain their source semantics. RESULT.json records their
full census. The table does not turn these inherited operations into zero
work and does not give a complete machine/compiler tariff.

A direct product of scalar operator-norm bounds gives an inverse suffix bound
of `2^18812`. Gaussian and monomial maps have norm one. A local schedule with
m errors of norm at most epsilon therefore has output error at most
`m * 2^18812 * epsilon`. This is a conservative fixed-template bound.
The complete caller, recursive error allocation, movement, storage, compiler,
BIT supplier and outer recovery still need explicit funding. In particular,
unchanged Gaussian counts do not imply unchanged ordinary/compiler costs.

## Verification and next use

The registered verifier runs the frozen predecessor replay, reconstructs the
changed word, checks both all-column compositions and the separate inverse
formula, and checks owned cleanup, charts, exact paid counts, boundary phases
and inverse child phases. Mutations of inverse COPY sign, reverse zero-retag
input and boundary phase must fail.

The next use is one chronological caller that retains useful progress in the
eight mode fields. Its full invoice must include every helper transfer and
all additional queries. A local inverse, a favorable cost estimate or a
finite failed control search does not establish that caller.
