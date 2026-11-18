# Floor-rounding contract for the three-field scalar repair

## Exact scope

This theorem concerns the common-coordinate scalar core extracted from
PR #7669 at `95d476623f1468822057554475dc8badb19bfa44`. The full candidate
has canonical SHA256
`ee251f6005d2a92b887c5b804bd7aac05989d278b2c9ccb3c3091b50d533b08d`.
The verifier reconstructs it from the pinned K372-2 word and all twelve
edit blocks. It then reads the literal old and new local event windows.
No copied source byte is changed.

Set x=role236, y=role544, z=role1000. In this theorem, x,y,z are arbitrary
integer ticks in one common coordinate system. Each ADD writes the
mathematical floor of its complete rational result. There is no overflow.
The native MOVE instructions are removed only for this stated scalar
model. The actual charts 265,751,927 have different bases. This theorem
does not assume that their physical transports commute with rounding.
It is not an error bound for the complete native or sixteen-call caller.

The source's rational identity is an existing result. The new result is
the exact floor-rounding law, exactness domain and sharp local error.
It answers whether that rational identity alone proves equality after
rounding each scalar ADD. The answer is no, even in common coordinates.
The source's fine exact grid can still satisfy the stronger domain.

## Literal programs and rational identity

The old source window is `[97747,97753)`. The candidate window is
`[97842,97851)`. Each ends immediately before the external read
`ADD 544 972 1/2 927`. Their three and six scalar operations are:

```text
Old:
  y <- y - 2x
  z <- z + 2y
  x <- x + z/4

New:
  x <- x + z/4
  z <- z - 2x
  y <- y + z/2
  z <- z + 2y
  y <- y - x
  x <- x + y/2
```

Without rounding, both tapes have the matrix

```text
M = [ 0   1/2   1/4 ]
    [-2    1     0  ]
    [-4    2     1  ].
```

The exact matrix check does not include the native chart transports.
The source's separate native proof and evidence remain necessary for
that composition. In particular, the old and new x fields leave this
local window in charts 751 and 927 respectively.

## Complete all-integer law

Let A and B be the old and new tapes with floor rounding. Set
`h = floor((z mod 4)/2)`, where `z mod 4` is in `{0,1,2,3}`, including
for negative z. Then, for every integer triple,

```text
A(x,y,z) = (floor((2y+z)/4), y-2x, z+2y-4x).
B(x,y,z) = A(x,y,z) + (0,h,2h).
```

For the old tape, only its last operation can lose a fractional part.
The two earlier operations are integral, which gives A directly.

For the new tape, write `z=4q+r`, with `0<=r<4`, and let `h=floor(r/2)`.
Its successive changed values are

```text
x1 = x+q
z1 = 2q+r-2x
 y1 = y+q-x+h
z2 = z+2y-4x+2h
 y2 = y-2x+h
x2 = q+floor((y+h)/2).
```

For each r in `{0,1,2,3}`,
`floor((y+h)/2)=floor((2y+r)/4)`. This proves the formula for B.
The two rounded outputs are equal exactly when `z mod 4` is 0 or 1.
This equality domain is a union of two residue classes; it is not the
same as either tape's no-rounding domain.

The verifier also checks a second completeness argument. The translations
`(1,0,0)`, `(0,2,0)` and `(0,0,4)` produce integral translations after
every exact prefix of both tapes. Floor commutes with each such integral
translation. Each integer triple therefore reduces to exactly one of
the eight cases `x=0, y in {0,1}, z in {0,1,2,3}`. The receipt records
all prefix translations and all eight outputs.

## Exactness domains

Every old division is exact if and only if

```text
2y+z = 0 mod 4.
```

Every new division is exact if and only if

```text
z = 0 mod 4 and y = 0 mod 2.
```

Necessity follows from the first quarter division and final half division
of the new tape. Under these conditions the middle half is also exact.
The old domain is a lattice of index 4 in the integer triples. The new
domain is a sublattice of index 8, hence has index 2 in the old domain.
For both tapes these domains also characterize exact final output Mv.

For example, take `(x,y,z)=(0,1,2)`. Then `Mv=(1,1,4)` and the old tape
returns that exact value. The new tape returns `(1,2,6)`. All inputs,
intermediate stored integers and outputs fit in the signed four-bit
interval `[-8,7]`. Thus this witness does not depend on overflow. It is a
local scalar witness; reachability at the complete caller is not proved.

## Sharp output errors

Let `theta=((2y+z) mod 4)/4`. Relative to the common exact map M,

```text
A(v)-Mv = (-theta,0,0).
B(v)-Mv = (-theta,h,2h).
B(v)-A(v) = (0,h,2h).
```

For Euclidean norm on one real triple, the sharp bounds are

```text
||A(v)-Mv|| <= 3/4.
||B(v)-Mv|| <= sqrt(89)/4.
||B(v)-A(v)|| <= sqrt(5).
```

The first bound uses `theta<=3/4`. The second uses
`theta^2+5h^2<=9/16+5=89/16`. The input `(0,0,3)` attains both error
bounds and the difference bound. Its complete stored path also fits in
four signed bits. The receipt checks all eight residue cases, so there
is no independent-noise relaxation in these constants.

For a grid spacing Delta, multiply the three bounds by Delta. For N
complex coordinates, apply the law independently to 2N real triples.
The sharp Euclidean bounds are respectively
`3sqrt(2N)Delta/4`, `sqrt(178N)Delta/4`, and `sqrt(10N)Delta`.
Repeat the real maximizing triple in both components of every coordinate
to attain them. These vector bounds still use common coordinates; they
do not include chart transport or caller propagation.

## Evidence and remaining obligations

The verifier uses independent rational and integer arithmetic on all
6859 triples in `[-9,9]^3`. It also checks the eight-case complete residue
quotient, exact rational matrices, all prefix translations, the two
exactness domains, attainment, complete source reconstruction and the
first later external read. Three coefficient/sign mutations and signed
truncation toward zero fail the claimed law. Checks use explicit
exceptions and remain active under optimized Python.

This proof requires a chosen common grid and floor semantics. Other
rounding rules need their own law. Signed range for arbitrary inputs,
the actual native chart maps, reachable caller residues, inherited
approximation before the block, later error propagation, physical
conversion costs and the full sixteen-call precision theorem remain
open. In particular, no error was exhibited on the source's recorded
fine exact grid. The conditional kappa, all five framework assumptions
and the selected frontier are unchanged.
