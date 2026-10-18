# Minimum source repair for a changed connector chart

Let B0,B1:X->Z be linear maps over any field, with finite dimensions n,m.
Let U,V be their row spaces in X*, with dimensions r0,r1 and intersection
dimension c. A chart is an arbitrary invertible linear map R:Z->Z. The
residual source correction is Delta=B1-R B0. Then

    min_(R invertible) rank(Delta) = max(r0,r1)-c.             (1)

This is a rank statement, not a minimum scalar circuit cost or a theorem
about a restricted native chart alphabet. The familiar equal-kernel criterion
in the credited predecessor is exactly the zero-residual case. The new
interface permits and charges the residual when kernels differ.

## Lower bound

The row space of R B0 is U. Modulo V, its rows equal the negatives of the
rows of Delta; therefore the image of row(Delta) in X*/V contains the image
of U, which has dimension r0-c. Likewise modulo U the rows of Delta project
onto the image of V, of dimension r1-c. Hence rank(Delta) is at least both
r0-c and r1-c, proving the lower bound in (1).

This does not merely count unequal ranks. Two equal-rank maps can have
different row spaces and a positive minimum. For example the two rank-one
functionals x0 and x1 need one independent correction.

## Attaining chart

Choose a basis S of U intersect V, extend it by A to a basis of U, and by B
to a basis of V. The union S,A,B is independent: a relation between A and B
would put their common combination in U intersect V, contradicting either
extension. Choose invertible row-operation matrices Q0,Q1 taking B0,B1 to

    Q0 B0 = [S; A; 0],          Q1 B1 = [S; B; 0].

Their common S rows occupy the first c positions; pair the exclusive rows in
the following positions, padding the shorter list with zeros. Set
R=Q1^-1 Q0. Then

    Q1 Delta = [0; B-A; unmatched rows; 0].

There are max(r0-c,r1-c) nonzero rows and they are independent by the
independence of S,A,B. Since Q1 is invertible, Delta attains (1). The same
argument covers zero maps, zero source dimension, full rank and unequal ranks.
It uses no generic-position, infinite-field or characteristic assumption.

The binary constructor implements this argument by tracked elimination. It
extracts the common row basis from relations among independent bases of U,V,
extends that basis in each row space, solves for its preimages in the original
rows and appends the full relation basis. These preimages plus the relation
basis form the invertible Q matrices. The finite oracle independently forms
actual GL3 orbits rather than trusting the constructed R.

More generally, consider any finite internal transport composed only of
invertible charts and additive source injections C_j x, with no intervening
output observation or source mutation. Its endpoint has the form R z+E x;
E is a sum of invertibly transported C_j. Thus rank(E)<=sum rank(C_j).
If it carries B0 x to B1 x, E=B1-R B0, so the same quantity in (1) lower-bounds
the **total injected rank**. One residual injection attains it. This statement
does not price the charts or the implementation of an injection.

## Dirty endpoint and compulsory restoration

Let x,z,y0,y1 be distinct arbitrary input rows, x immutable. A0,A1 are fixed
linear readers and can be singular, noncommuting and different. Complete
queries preserve every other row, private scratch and required head positions;
their increment is independent of the old target. Reserve z throughout.
For general characteristic execute, chronologically:

    y0 -= A0 z
    z  += B0 x
    y0 += A0 z          # first output delivered; never changed again
    z   = R z
    z  += Delta x      # one paid source correction
    y1 += A1 z
    z  -= B1 x
    y1 -= A1 z          # second output delivered
    z   = R^-1 z

After the first delivery z=z_initial+B0 x. Chart plus correction makes it
R z_initial+B1 x. The second read/close/read adds A1 B1 x to y1 and leaves
z=R z_initial. The final inverse restores z exactly. Thus both outputs receive
their desired increments and all source/connector dirt restores. Nothing
requires R to fix the initial dirt. The source correction is cancelled by
the actual B1 close; it is not an unpaid obligation deferred to a consumer.
Reversing the word and inverting each complete operation gives its inverse.

## Complete comparison and what rank does not buy

For sign-symmetric complete query prices, or upper bounds valid in either
orientation, the two separately closed echoes cost

    C_closed = I0+P0+D0 + 2(c_B0+c_B1+c_A0+c_A1).

The transported pair costs

    C_repair = I1+P1+D1 + c_B0+c_B1+2(c_A0+c_A1)
               + c_R+c_Rinv+c_Delta.

I,P,D charge admission/layout/reservation, preparation/synthesis and remaining
instruction/control work. Each complete c includes its real source/coefficient
access, arithmetic, scratch restoration, routing, frame obligations and heads.
For asymmetric signs or ports, sum the actual word prices instead. A saving
requires

    c_R+c_Rinv+c_Delta + (I1+P1+D1-I0-P0-D0) < c_B0+c_B1.

A rank-r factorization Delta=UV does **not** implement U(Vx) for free.
Its observations, intermediate storage, dirty cancellation and restoration
must be included in c_Delta. Likewise arbitrary invertible R in (1) is a
mathematical search domain, not a free physical gate. Rank-minimizing R can
lose at actual tariffs; the receipt includes an explicit contrary tariff.

The binary pilot uses B0=(7,6,1), B1=(1,6,5), R=(3,2,4), with bit j denoting
column j in each row. Delta=(0,0,4), a single source-coordinate XOR into the
third connector coordinate. The map ranks are2 and3, c=2, so this rank1 repair
is minimal. The identity chart leaves rank2. R and R^-1 are each the one-XOR
shear z0+=z1. With identity readers, all required source/read/chart/correction
operations are literally emitted:26 XORs versus34 for the separately closed
queries. There are no additional rows. The full4096 dirty states and inverses
pass, with first-output delivery checked at its actual cut.

This is a fixed-call comparison. Opening the matrices and directly updating
the two outputs uses only11 XORs; that excluded-alphabet control is retained
and prevents a claim of general circuit optimality. The pilot therefore
demonstrates a complete adapter identity and price, not a practical optimizer.
Its same scalar gates act independently on length-L coordinate blocks, giving
26L versus34L scalar XORs; physical instruction/address costs still need a
backend. The fixed-port one-bit tariff explicitly counts movement plus five
units per XOR, matching the predecessor convention, without claiming a native
Turing-machine implementation.

## Revision-5 expansion decision

Declared milestone: **local module**. Retain the rank criterion and restored
adapter; narrow work to this single proof and discriminating example. General
native chart/repair prices, selected ownership, precision and a selected caller
remain unknown, not zero. Do not start a dependent optimization round until a
pinned caller supplies a strict complete allowance and legal connector lifetime.
The exact scope/boundary/cost ledger and reopening condition are in TASK.json.

Credit woklerx's retained equal-kernel chart interface, Ross Richardson's PR943
dirty-query accounting and the elementary row-space method. No priority claim
is made for rank inequalities or change of basis. The contribution is their
source-pinned residual-repair interface and executable evidence. Prepared by
ywz65 with substantial OpenAI Codex assistance; Apache-2.0.
