# Proof and scope

## 1. The register model

Let `x_0,...,x_111` be independent scalar inputs. Input `x_i` has binary
label `p_i` in `GF(2)^9`. A register has a scalar value and a binary frame.
Its clean row is the coefficient row of the x inputs after all other
arbitrary inputs have been set to zero. The support hull of that row is
the span of the labels with nonzero coefficients.

Initially, the 112 source rows are the coordinate rows and their frames
contain the corresponding labels. All other clean rows are zero. A
scalar ADD uses two distinct registers at a common frame that contains
both preceding frames. A scale leaves its row support unchanged. Frames
can grow but cannot decrease. No operation injects a new source form
through a cut or a private descending query. Target registers are not
available as extra registers in this class.

These rules imply that each clean support hull lies in its register's
frame. This follows by induction on the scalar gates. Cancellation can
remove support, but cannot add a label outside the common frame.

The coefficients can be arbitrary elements of a characteristic-zero
field. The gate count, order, intermediate rows, coefficient size, and
mixing between the 14 blocks are unrestricted. In particular, the proof
does not use the fixed-operation-multiset hypothesis of PR899. It does
not assume the shipped end-of-A frames for individual helper registers.
It does retain the value/frame demands below.

## 2. First formation and the antichain bound

Suppose a required value has support hull `F`, with `dim(F)>=2`, and must
occur in a register whose frame is contained in F. Select the first time
in the whole computation that any clean row with support hull F occurs
at a frame contained in F.

That event is an ADD. It cannot be an initial row or a scale. Neither
operand already has support hull F: its frame was contained in F before
the event, which would contradict the choice of the first time. The
resulting row has support hull F. Thus the common ADD frame contains F.
It is also contained in F, so it equals F. Both distinct operand
registers reach F at this event.

Let A be a set of pairwise incomparable required frames. Assign the two
registers from the preceding argument to each F in A. One register
cannot be assigned to two different frames in A. Its frame can only
grow, so those two frames would have to be comparable. Therefore:

```text
number of registers >= 2 * |A|.
```

The certificate derives the demands from the 14 pinned packet programs.
For each of the eight all-K cells, the omitted face operations expose
leaver operands at rank two. Across the six K blocks, these give 48
leaver values at 24 distinct frames. The retained faces give 144 values
at 144 distinct rank-three frames. The checker tests every pair of the
168 frames and finds no containment in either direction.

The checker then replays the actual final seven-slot word. It finds all
192 required clean rows, up to nonzero scale, at their specified frames
in A or B. Each witness records the phase, event, register, exact row,
and frame. No value is inferred from a helper name or a reported count.
The source clean rows do not depend on the omitted target cut because
the word has no target feedback into source-side registers in A or B.

It follows that at least 336 registers are needed for this interface.
Only 112 are input registers, so at least 224 extra registers are needed.
The 14 packet programs each use eight input registers and 16 helpers.
They supply all the specified forms at their frames. Thus 224 is sharp
for the clean formation interface. This upper witness does not assert
an independently optimal complete dirty-word implementation.

The bound concerns the total available registers for this interface.
Helpers from a different stage count if that stage lends them. The proof
does not add 224 to a separate lower bound for another stage unless the
two resource uses are independently shown to be disjoint.

## 3. Whole-block target borrowing

The final frame of target t is `H_t={z:z dot p_t=0}`. A register with
monotone frames can reach a frame F only if `F` is contained in its final
frame. For each of the eight rank-four cold-block frames and each of the
112 targets, the certificate gives an explicit vector in F with odd
pairing against `p_t`. It checks all 896 cases. No whole block can use a
target register, regardless of scalar cancellation or later restoration.

The same check applies to all eight rank-eight center-query frames.
It rejects all 896 center/target pairs. Thus a target cannot hold a
complete retained center query or participate at that query's full frame.
Earlier staged reads at smaller frames are outside this statement.

The scalar restoration check is separate. It starts with the full
704-by-704 identity matrix, replays A over exact rationals, then applies
the recorded low tails for each group of four cold helpers. All four
helper rows return to their exact input rows. These helpers have no B
uses. A missing-tail control fails restoration. This is a scalar fact,
not a claim that an altered native schedule has been admitted.

The frame result is not based on rational orthogonality of complementary
root tetrads. The retained binary Gram relation has a constant term:
`p_s dot p_t = 1 + (root_s dot root_t / 2) mod 2`. The finite cap check
uses the actual binary labels and does not omit that term.

## 4. Splits and a boundary counterexample

Project a cold block onto its eight independent source inputs. Each
target cap admits either none or four of these source labels. Across
all 112 targets there are 15 different masks. The nonempty masks form
seven complementary pairs.

Restrict the split mechanism to two disjoint support masks whose union
is the block. Every carrier is assigned to one of the two masks. Other
block columns can be present, but are removed by projection here. On
each side, the carriers must span the restriction of the four coordinate
totals to that side. Their number is at least the rational rank of that
restriction. The checker computes these ranks by exact elimination.
Six complementary pairs have ranks 3 and 3. The last pair has ranks 4
and 4. This proves the six-carrier minimum in the two-cap class, with
eight needed for the last partition. It covers all possible target
choices, not a sampled set.

That restriction matters. Write the four coordinate rows as a,b,c,d.
The four rows `a+b`, `a-b`, `c+d`, and `c-d` each fit an allowed rank-three
target cap. They are independent and recover a,b,c,d by sums and
differences divided by two. The certificate gives distinct target
choices for all eight blocks. Hence a claim that every split needs six
carriers would be false. These four algebraic carriers still need a
scalar circuit with arbitrary target dirt, valid frame paths, restoration,
and a complete supplier invoice. They do not constitute such a circuit.

## 5. Cost of descent between local formation jobs

This subsection uses an additional restriction. Each demand still has
its first formation inside its own frame, as in section 2. Descents are
allowed only to reuse registers between these local formation jobs.
This excludes forming a query above its delivery frame and descending
a private copy. The native center mechanism uses that excluded behavior.

There are 336 assigned register/frame occurrences. With delta fewer
registers, at least delta transitions on reused registers go from one
antichain frame to another. Such a transition has at least one downward
rank step. Total frame variation equals final rank minus initial rank
plus twice the total downward rank. Therefore this reuse adds at least
`2*delta` paid rank above the same endpoint rises.

For a limited invoice screen, retain all other paid and idle charges.
Grant each removed helper the largest possible width, nine. Grant that
all nine of its paid ranks were rank-one children, and return those nine
ranks as idle work at the full parent rank m. Both grants favor removal.
With `w_r(b)=r*(m/r)^b`, the largest saving is

```text
9 * (m^b - 1)
```

per removed helper. The extra two ranks cost at least two because every
allowed child rank is at most m. At stage counts 9 and 37, m is 73 and
297. For `0<b<=1/32`, the exact integer checks

```text
73  * 9^32 < 11^32
297 * 9^32 < 11^32
```

give `9*(m^b-1)<2`. Even the favorable returned-idle grant cannot pay for
the forced descent. Extra copies, private queries, scalar access, or
restoration only add expense in this screen. The result applies per
call and per orientation, so summing calls preserves the strict loss.

This is not a bound on arbitrary new paid profiles. If the mechanism
also removes other charges, changes the demanded forms, changes the
query interface, or uses a different endpoint contract, its complete
invoice must be recalculated. No such changes are priced as free here.

## 6. Consequences and unresolved work

The complex supplier still limits the pinned assembly. The first
theorem rules out a smaller pure-source factory with this exact
value/frame interface, even after arbitrary new scalar operations.
The cap theorem rules out whole-block relabeling into targets. The
descent screen rules out paying for local-job reuse by the deleted
helper width alone at the two specified controller ranks.

The results do not prove the 480-helper word optimal, do not prohibit
same-count profile improvements, and do not give an upper bound on
kappa. Joint source/target circuits, mixed-cap carriers, new private
queries, helper sharing with other stages, and changed endpoints remain
open. PR1107 changes endpoints, so it is not excluded. The finite checks
do not prove the all-size compiler, common-label and mutable-source
realization, hosting, precision and tape, exact recovery, analytic
transfer, or bit H1-H5 assumptions.
