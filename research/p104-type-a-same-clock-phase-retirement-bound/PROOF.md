# Same-clock Type A phase retirement

The signed Type A caller from #7113 in the #7334 comparison witness
has 4,783 events, including all 17 J stages, and 36 Type A roles.
Specialize all 17 bodies to 1 and q to +1 or −1. The original
specialized endpoints are I and −I respectively. The four QUERY
indices are 1516, 1580, 1659 and 1721, zero-based in the full stream.

A phase retirement leaves the target at I for q=+1. At q=−1 it
changes one diagonal sign of −I for each retired phase. For the
erased word, use q-even coefficients s₁,…,s₄ at the four old QUERY
clocks, so each coefficient is the same at the two signs. The
argument grants any rational values for these coefficients. Keep
all other literal specialized actions fixed.

## Rank budget and the fixed all-plus control

At either sign, split the corrected and erased words into products
at all correction sites. A changed factor differs from its erased
version by a matrix of rank at most one. An inserted factor uses
the identity at the corresponding erased position. Telescoping the
difference of products gives one term per correction, multiplied
on both sides by surrounding factors. The difference between target
and erased endpoints must have rank at most the number of such
corrections. This allows arbitrary correction directions and clocks
as long as erasing their differences gives the stated erased word.

For the fixed s=(1,1,1,1) word at q=−1, the rows (0, 1, 18, 19)
and columns (2, 9, 20, 27) of target minus erased endpoint give

```text
[-6 -2  0  0]
[-4  0  0  0]
[ 0  0 -6 -2]
[ 0  0 -4  0]
```

The row and column sets are disjoint, so this submatrix is common
to every diagonal target. Both 2×2 blocks have determinant −8
and the full determinant is 64. The fixed all-plus erased word
therefore needs at least four corrections for every diagonal
target. The proposed target with roles 0 and 18 retired has
exact residual rank four for this word.

## Reduction of arbitrary even coefficients

Fix q and write dⱼ=sⱼ−q, with D the diagonal matrix of these four
differences. Take U to have columns equal to the original suffix
transport of the four QUERY output directions. Take V to have
rows equal to the original prefix transport of the four QUERY
source covectors. For input x, the actual QUERY source values z
satisfy z=Vx+LDz, where the strictly lower triangular matrix L
transports earlier QUERY differences to later source reads. The
difference of endpoint matrices from the original is therefore

```text
U D (I−LD)⁻¹ V.
```

The inverse exists because LD is strictly lower triangular. When
U is injective and V is surjective, this expression has rank
equal to the number of nonzero dⱼ. This also holds after taking
output rows R and input columns C if U[R,:] and V[:,C] have
full rank.

At q=+1 the opposite-constant control s=(−1,−1,−1,−1)
has full difference rank four. The independent reverse
calibration records a nonzero 4×4 determinant of 16. This
forces full rank of U and V. At q=−1 the all-plus calibration
has determinant 64 on the disjoint rows and columns above.
This forces full rank of the projected factors. A diagonal
target contributes zero on those disjoint rows and columns,
so any residual with a diagonal target has rank at least
the number of nonzero dⱼ at q=−1.

If two corrections suffice at both signs, at most two coefficients
differ from +1 and at most two differ from −1. Each of the four
coefficients differs from at least one sign, and a coefficient
outside {−1,+1} differs from both. Therefore exactly two coefficients
are +1 and two are −1. The rational-coefficient search has six
balanced sign patterns. The residual ranks for the 0/18 target
at q=−1 are 3, 3, 3, 3, 4, 4 in the order of lexicographic +1
position pairs.

## All pairs from diagonal anchors

For each of the six patterns let A=E−(−I), where E is the
q=−1 erased endpoint. Both exact engines reconstruct rank two
for each A. Let B=E−T for a proposed diagonal target T.
Then A and B agree off the diagonal.

Fix a role i. Suppose two rows R and two columns C are disjoint,
all avoid i, and det A[R,C] is nonzero. If rank B were at most
two, the 3×3 determinants on rows (R,i) and columns (C,i) of
both A and B would vanish. Their difference is

```text
(B[i,i]−A[i,i]) det A[R,C].
```

Every other entry is off the diagonal. Thus this anchor
forces B[i,i]=A[i,i] and leaves the target at −1 on role i.

The engines agree on the missing-anchor sets [18], [18], [18],
[0], [], [] in the six-pattern order. For each pattern there is
at most one unanchored role. Every target changing two or more
diagonal entries of −I changes an anchored entry and has residual
rank above two. In particular, all 630 distinct pairs are covered
by 216 pattern and role checks, without enumerating new literal
caller words for each pair. The directly tested alternate pair
0/17 has residual ranks 4, 4, 4, 3, 4, 4 on the same six words.

A single unanchored role in a pattern remains open under arbitrary
rank-one differences. If every allowed correction preserves the
specialized determinant, such as a unipotent shear inserted
against identity, an odd number of sign flips is also excluded.
The target determinant would be −1. Every allowed factor product
has determinant +1. This argument needs the determinant hypothesis.

## Directed whole-profile prices

The two most favorable ranks are 137 and 137 at roles 0 and 18.
The next price tier is 137 and 73, checked at roles 0 and 17.
For ranks r≥1 the tariff r^(1−κ) has decreasing increments,
so retiring one phase from a higher rank loses less productive
moment. For a 137/137 edit over 96 ports the proposed changes
are ΔP1 = −192, ΔT137 = −192, ΔT136 = +192. The
signed rank surplus remains 1,424. At the upper endpoint of the
old crossing the directed gross is below 4.099242419852824 raw
units. At the inherited exact probe the relaxed complete margin
is above 4.098855957122750 raw units. An optimistic two-pair
gross relaxation is below 8.198484839705648 raw units.

The 137/73 edit moves 96 targets from 137 to 136 and 96 from
73 to 72, and removes the same 192 paid rank-one calls. Its
directed gross is below 3.882211372694752 raw units at the old
crossing upper endpoint, and its relaxed complete margin at the
probe is above 3.881824851665655. One extra rank-one field per
port exceeds either pair's gross. Both price calculations grant
unchanged setup, routing, ownership, restoration, grid, precision
and tape costs. The quoted savings are unbuilt.

## Scope

All scheduled coefficient words and role checks were covered within
their caps. The result uses a necessary unit-body specialization
of the signed endpoint contract. The test leaves changed clocks,
J stages, ordinary wrappers, a different erased endpoint, or
higher-rank corrections open. Full signed bodies, arbitrary-input
physical execution, ownership and restoration would still need
independent verification for a future candidate.
