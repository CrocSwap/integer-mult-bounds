# Closed head-move bill for one six-tape subtraction

The tape rules are the pinned `Tape` object in
`research/qq16-gaussian-axis-tapes/tapes.py`: a head reads or writes only the
cell it occupies, a move changes that head by exactly one cell, and the cell
one past the owned interval may be occupied but not read or written. Finite
control may hold a borrow in `{0,1}`. No second head, random access, or free
relocation is available.

## Placement

Let \(N=2^n\) with \(n\ge 1\) and let \(W\ge 1\). Write \(L=NW\). The six
lengths are the kernel's lengths \((L,L,L/2,L/2,L/2,L/2)\).

| Tape | Contents | Cells |
| --- | --- | ---: |
| data0 | real part of L546, coordinates \(0..N-1\), little-endian | \(L\) |
| data1 | imaginary part of L546 | \(L\) |
| scratch0 | real part of L561, coordinates \(0..N/2-1\) | \(L/2\) |
| scratch1 | imaginary part of L561, coordinates \(0..N/2-1\) | \(L/2\) |
| scratch2 | real part of L561, coordinates \(N/2..N-1\) | \(L/2\) |
| scratch3 | imaginary part of L561, coordinates \(N/2..N-1\) | \(L/2\) |

Every cell is a payload bit. The two complex registers occupy \(4L\) cells and
the six tapes have exactly \(4L\) cells, so this is a capacity-tight packing
of those lengths. Heads start at the origin of each interval, which is cell 0.

## Program

On each coordinate, subtract the \(W\)-bit two's-complement integer on the
source tape from the integer on the destination tape. The borrow resets at
every coordinate boundary, so it does not cross from scratch0 to scratch2.
Process the first \(N/2\) coordinates, step each data head one cell onto the
second half, process the remaining coordinates, then walk every head back to
its origin. Source cells are read and not written.

The forward scan of a tape of length \(L_t\) makes \(L_t-1\) moves and finishes
on the last cell. The return makes another \(L_t-1\) moves. Data tapes are one
interval of length \(L\), so the single step between the halves is one of those
\(L-1\) forward moves, not an extra crossing. The move total is

\[
\sum_t 2(L_t-1) = 2\bigl(2(L-1)+4(L/2-1)\bigr) = 8L-12 = 8NW-12.
\]

Each of the \(4L\) payload cells is read once, and each of the \(2L\)
destination cells is written once. So READ \(=4NW\), WRITE \(=2NW\), and the
cell-action total is \(14NW-12\).

## Matching lower bound

Work in the model above, with heads required to start and end at cell 0.

Changing any one payload bit changes the coordinatewise difference in
\((\mathbb{Z}/2^W\mathbb{Z})^2\). A cell that is never read cannot affect a
later write, so every payload cell is read. The output bit string is not a
function of the minuend alone, so every destination cell must be written:
otherwise that cell would keep a bit that is not always the difference bit.
Therefore every cell of every tape is visited.

On one tape the farthest cell is \(L_t-1\). A unit-step walk from 0 to \(L_t-1\)
and back to 0 has length at least \(2(L_t-1)\), and that shortest walk already
visits every earlier cell. Summing over the six lengths gives at least
\(8NW-12\) moves. The program meets the bound, so the closed-return move count
is sharp for this placement.

The same counting gives READ at least \(4NW\) and WRITE at least \(2NW\). Both
are achieved. Stepping one past the last cell, as the axis kernel does, would
add two moves per tape and is not required here.

## What is not charged

Copying L561 onto the scratch windows, returning those bits to a native home,
zeroing scratch for a later kernel, the preceding axis factor (MOVE \(=20NW\)
in the pinned kernel), frame climbs, and the four scalar-work steps of the
same-frame coefficient count are outside this bill. \(W\) is the component
width of the placement. This note does not claim that event 9895 uses a
particular \(W\), including the \(W=5\) kernel fixture.
