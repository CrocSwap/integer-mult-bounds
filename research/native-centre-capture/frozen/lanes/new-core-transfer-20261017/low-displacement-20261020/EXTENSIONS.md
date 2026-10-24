# Reciprocal and odd-grid extensions

These are two separate extensions of the frozen native paths.
The first realizes the reciprocal response on the 48 paired ports.
The second lowers the full correction rank from thirty to sixteen
by permitting odd denominators in later scalar inverse codes.
The original rank-thirty packets remain unchanged.

## A native reciprocal response on the large sector

Replace the six-mode matrix B by B^-T on the 48 paired ports.
Both matrices have zero diagonal, so every new nonzero coefficient
has its own existing cyclic transfer event. Keep the small
fourteen-clique response C.

The new complete response is

```text
A = E48^-T direct_sum C.
```

The raw backward native call therefore gives

```text
x <- x - (E48^-1 direct_sum C) y.
```

This proves native reciprocal access on the large sector. It does
not prove a reciprocal response on all 112 ports, because C^-1 has
nonzero diagonal and is not emitted by the small-clique paths.

Every native frame, edge, recipe, and endpoint adapter is identical
to the frozen rank-thirty path. Only scalar coefficients and their
nonzero event positions change. The full response, its inverse, all
640 input columns in both directions, and all four common-frame
scalar codes are checked. Every scalar code costs 3210. The native
invoice remains 5288 real scalar primitives and

```text
1036 H1 + 48 H3 + 55 H4 + 55 H5 + 9 H6 + 9 H7.
```

The original selected block L and the ordinary principal unit are
preserved. The forward prefix row one-norm is 30; the backward
bound is 46. The proof uses the 1141 frozen native phase records
and 224 frozen endpoint records, with exact binary-frame matching.

## Sixteen correction coordinates with odd-grid inverses

The actual small-port orthogonality graph has a disjoint partition
into eight eight-cliques. The literal partition is in the payload.
The checker verifies every pairwise orthogonality equation and the
complete disjoint cover.

At each large vertex use

```text
B_v = I6-d_v d_v^T,
B_v^-1 = I6-d_v d_v^T/5,
```

where d_v is the same sign vector used for the selected-compatible
rank-two block. Conjugate by the actual physical pair code H.
The physical large response has eight correction coordinates.
Equivalently, let K contain the eight signed twelve-port rows
d_v^T H. Then

```text
K K^T = 12 I8,
E48 = I48-K^T K/2,
E48^-1 = I48-K^T K/10.
```

On each small eight-clique use

```text
C8 = I8-J8,
C8^-1 = I8-J8/7.
```

Each clique contributes one correction coordinate. The full
response E is symmetric, has determinant 35^8, and satisfies
rank(E-I)=16. The payload contains exact factors U,V with
E-I=UV and ranks sixteen. Both full inverse products are checked.

The selected block of E remains the previous L. However, the
selected block of E^-1 is (4I+L)/5. Therefore

```text
det(E_U,U) = 7^8 * 31^4 / 16,
((E^-1)_S,S)^-1 = 10(4I-L)/31.
```

The payload includes the new ordinary inverse and checks both of
its 104-column inverse products. This exposes the factor 31 needed
by the selected ordinary normalization. A controller with no
selected split can avoid that additional principal-inverse
requirement. It still needs its own complete code and terminal
construction.

The inverse coefficients 1/5 and 1/7 are not ordinary dyadic unit
scales. Their exact implementation needs the retained odd-grid
contract, conversion of all relevant root streams including
borrowed streams, a bound on odd denominator height, complete
native-child endpoint closure, and exact final conversion. Those
obligations belong to the separate odd-grid packet. This native
packet neither prices those divisions as free nor assumes them to
be forbidden.

## Literal native implementation and invoice

All native transfer coefficients in the rank-sixteen word are signed
integers of absolute value one. The large sector uses the frozen
six-mode cyclic paths, with all 240 off-diagonal coefficients.
Its pair-code cost is 1880 and its transfer cost is 1920.

For each eight-clique, use the same cyclic line-flag construction as
in NATIVE.md, now with depths one through seven. The source and
target flags are equal at each transfer and remain nested. A source
finishes with rank two after its rank-seven flag. A target finishes
with rank one in its own rank-eight hole.

Each small port contributes fourteen H1 children and one H2 child.
The complete local word has the following invoice in either
direction:

| Quantity | Count |
| --- | ---: |
| Rank-one children | 1520 |
| Rank-two children | 64 |
| Rank-three children | 48 |
| All native children | 1632 |
| Native mass | 1792 |
| Real scalar primitives | 7384 |
| Endpoint adapters | 224 |
| Native side-map upper bound | 3264 |

The small transfer cost is 448 unit ADDs, or 3584 real primitives.
The complete scalar count is 1880+1920+3584=7384. This is the
native word's scalar count only.

The phase table contains 685 entries inherited by exact frame-pair
identity and 876 new entries. Each new entry is compiled and checked
with the independent Pauli and exact Gaussian-state interpreter.
The 224 endpoint adapters are unchanged. Both providers have the
same actual data directions and receive the complete checked word.

Every output is replayed on all 640 independent input columns.
The 416 other fields remain arbitrary and unchanged. No owned or
private field is used. The complete prefix row one-norm is at most
22 in either direction. Every native child still has a Gaussian
dyadic endpoint. This last statement does not replace the global
odd-grid precision proof.

The exact physical conventions remain X=Qx at entry and
(F9 x', F9 Q^-1 y') at exit. No changed-exit W48/I64 histogram is
claimed in this packet. No source response is moved through Q.

## Reproduction and scope

Run emit_followthrough.py with --kind reciprocal-large or
--kind odd-grid-rank16, and --out naming a new directory. Repeat
with optimized Python and a different new directory. The expected
statuses are PASS_RECIPROCAL_LARGE and PASS_ODD_GRID_RANK16.
The final v2 outputs must be byte-identical between the two modes.

The earlier extension directories are retained as drafts. Their
scalar/native maps passed, but their copied matrix metadata included
an old ordinary inverse. The final emitter constructs a new model
from only valid shared geometry, computes the new inverse, and
checks both inverse products. Only the v2 outputs are frozen.

The rank-sixteen extension changes the allowed representation. It
does not contradict a dyadic-only obstruction. Its native child
distribution also differs from the rank-thirty and matching words;
mass alone is not a recursive price comparison.

The generic current-cut controller still leaves the ordered code
E2 E1^-T E0 and the physical conjugation Q(...)Q^-1. Native local
correctness does not supply access to that code's queries or
scatters. Helper progress, recursive hosting, the complete precision
bound, terminal removal, and the final supplier bound remain open.

The root identified odd-grid admission as the relevant escape. The
native-escape lane is responsible for that contract. The root's
reciprocal matrix, the independent-review cyclic flag family, and
the earlier pair-code and common-frame scalar constructions are
the other predecessors. AI assistance was used. No publication is
authorized. Before any future PR description, read
/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md.
