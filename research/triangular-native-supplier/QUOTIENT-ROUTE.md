# Routing the unitriangular quotient on tapes

Let R be the integers modulo 3^u. Let L be the group of lower unitriangular
N-by-N matrices over R. Each left L-orbit in GL_N(R) has one representative
of the following form. In row order clear all earlier pivot columns. Then
choose the first column whose entry is a unit. Subtracting a multiple of a
previous row cannot change its earlier zeros. The cleared entries determine
the subtraction coefficients uniquely, in pivot order. The residual row
must contain a new unit since the original matrix is invertible modulo 3.
This proves existence and uniqueness by induction. It also computes the
actual lower matrix T in gS=Tg' each time the native word asks for S.

There are d=N-i free columns before the pivot in zero-based row i is chosen.
Their low vector can be any nonzero vector over the ternary field. Every
one of their high digits ranges independently over M=3^(u-1). Thus there
are exactly Q=product_(d=1..N) (3^d-1) low tuples and M^q high tuples
per low, q=N(N+1)/2. All Q M^q slots have arbitrary payloads.
The old full group
has exactly Q 3^k M^(N²) slots with k=N(N-1)/2. The ratio is
3^(u k). This ratio is exact for these bank formats.

## Bijection on a fixed high packet

Process one source low at a time. Its destination low comes from precisely
the same pivot rule applied modulo 3. Apply the full right word once. If
the caller supplies a body operation, visit each original high tuple
before rearranging these records. This gives it the actual T at the
old representative. Zero ranges and coincident values do not influence
the schedule.

In row i let E be the source free-coordinate submodule, the rows that
vanish on all earlier source pivots. Its direct complement is the span of
the earlier source rows. Row reduction gives this decomposition,
and triangularity makes it unique. The destination has the corresponding
decomposition E' and earlier span V'. Right multiplication by S maps
the earlier source span onto V'. Follow it by reduction to E'. On E the
result is a linear isomorphism A:E→E'. Indeed the map induced on the
two quotients is an isomorphism and restriction to each row complement
is its coordinate representation. Its entries are obtained by applying
the reduction to the selected rows of S. The program knows the complete
earlier *destination* rows. They suffice for this operation.

If l and l' are the low row coordinates before and after the map, write
the input as l+3x. The output high coordinates satisfy

    x' = A x + ((A l - l') mod 3^u)/3   (mod M).

Division here is an exact division of the chosen representatives of the
differences. Each difference is a multiple of 3. All earlier output high coordinates
form the exposed prefix. This makes A and the offset independent of the
remaining free digits.

Reduce A to identity over the local ring of size M. Each pivot column
has a unit after the previous column operations, since the residual
square matrix is invertible modulo 3. Invert the row-reduction word in
reverse order. Swap whole free digits, perform ordinary row additions,
and scale single free digits by the executed local-ring units. The
single-field scaler below handles every such unit. Translations apply
the corresponding integral carry. These operations give the actual orbit
action, so the inverse word returns every representative.

## A unit scale on one digit field

Here a digit field has v ternary places. Let a be any unit modulo 3^v.
For v=1 it is identity or interchanges one and two.
For v=2t write x=hB+l, B=3^t, 0<=h,l<B. Start with the two existing
limbs in the physical order h,l. Apply diag(a⁻¹,a) modulo B to this pair.
For any unit c, four additions give diag(c,c⁻¹). Apply them in this order,
l←l−ch, h←h+(c⁻¹−1)l, l←l+h, and h←h+(c−1)l.
Choose c=a⁻¹. Recursively scale only the new h by a² modulo B.
The two limbs now contain ah mod B and l'=al mod B. Interchange their
positions. For each exposed l' rotate the high limb by
floor(a (a⁻¹l' mod B)/B) mod B, then restore their positions.
This supplies the exact carry from the original low limb without
requiring an extra full digit or a precomputed table.

For odd v>1 write x=3y+t. Recursively scale y modulo 3^(v−1), with t
untouched. Split the resulting stream into three sequential buckets.
Place the old t bucket under at mod 3 and rotate its y blocks by
floor(at/3) mod 3^(v−1). Interleave all three returned streams.
This takes a bounded number of full traversals. In both cases, a
later scalar coefficient reads only the existing exposed prefix.
The recurrence terminates because an odd step is followed by an
even step at the next smaller width. All output addresses equal ax
modulo 3^v. Any complement and arbitrary payload remain in their
original order within each moved block.

Each even step has at most six preceding-service calls at half width.
For an earlier price K V (1+t^(1-b)), with 0<=b<=1/2, their sum over
all positive half widths is at most 12 K V v^(1-b)/(2^(1-b)−1).
All other traversals use O(V(1+log(v+1))) cells of work. The carry
amount needs a single inverse per prefix and O(v²) elementary
arithmetic steps per exposed limb with grade-school multiplication.
Each of its rotations contains B=3^t full records. The ratio v²/B
has an absolute upper bound at even v=2t. The per-prefix inverse cost
is polynomial in v and the enclosing field has 3^v records. A streamed
odometer advances across each unchanged suffix. This pays generation
and movement at O(V(1+v^(1-b))) including the preceding service.

## Physical work

A shift of an exposed earlier digit into a later target visits that
whole suffix in cyclic order. If the source comes later, first interchange
the two complete equal-width digits by the preceding ordinary service and
restore them after the shift. The scaler's trit negation reverses the
order of its nonzero opaque blocks while preserving their contents. All
source highs, remaining free digits, body and older data remain present.
If a row has d remaining positions, its controller uses at most d-1
swaps of those positions, d scales and d(d-1) row additions. The
earlier-ordinary calls outside unit scaling therefore number at most
2d(d-1)+d. Add d single-field unit scales with the explicit bound
above. Summation over d and disjoint equal-coordinate prefixes gives
O(N³ V(1+(u−1)^(1-b))) for all high routing. Each pass includes
rewinds, bounded-length temporary tape walks and erasure. The scaler
emits one sequence of passes on reusable spools. Recursive control
has logarithmic depth in u and holds only integer descriptors. No
ancestor scale retains a full data tape of its own.

The low odometer has one nonzero ternary row ordinal per free row.
It reconstructs its pivots in row order. Its explicit mixed-radix
counter creates exactly Q low cases with no call stack indexed by N.
Keep the destination's N²-trit tag once per packet on a separate tape.
Collect both tags and full packets by each ternary digit, starting
from the last. Concatenate the three buckets in increasing order.
Stable radix sorting gives canonical row-major low order, even when
the next free columns depend on the previous pivot. The N² passes
take O(N² V + N⁴ Q) cells of work per group of volume V. The tag
backing is O(N² Q) in addition to a constant number of full-volume
tapes. The group router, packet router, affine router, limb scaler and
trit-bucket step use respectively at most 10, 2, 3, 3 and 7 work
spools. Outside the separately charged body and preceding services,
25V + 10N²Q bytes bounds their additional payload and tag extents.
This includes temporary backing visited and erased. Each mathematical
descriptor and the fixed program have their own charges.
For the actual native suffix there are at least 3^(2Nfw)
independent addresses at f>=1. This pays all tags. The coefficient
arithmetic visits polynomially many cells in N and u per exposed
prefix or chart, including the conditional triangular body matrix.
The complete application separately charges that body action, the
production geometry, and the fixed program.

The tape checker compares each target record against an independent
construction by pivot minors. Its independent coordinate encoder checks
the lexicographic high ordinal. A separate input vector changes according
to the actual lower matrix at each source record. The complete inverse
word then restores the original records. A second test checks unit
scaling against direct modular address multiplication on 174,648 records
at eight widths. These finite computations test the tape program.
The uniform statements above are written proofs.
