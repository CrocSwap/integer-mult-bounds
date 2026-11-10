# A square-root two-band prime producer

This scoped construction and proof were produced by Nick Petalas. Apache-2.0.

## Contract and theorem

Let ell>=3, r=2^ell, D=d-1>=1, and d<=r. There are D target flags,
each zero or one, with the last flag implicitly one. Flag zero means target
t=r/2 and flag one means t=r. The D-1 supplied flags occupy a borrowed,
read-only binary tape. Parameters are borrowed binary words. Output is an
owned, initially blank tape containing exactly D consecutive ell-bit
little-endian source words. All heads return to their origins and all
producer scratch is blank at successful return. Erasure is ordinary
irreversible erasure, with the same contract as PR4029, not reversible
uncomputation of arbitrary dirty inputs.

For each scale t with nonzero quota q_t, assume at least q_t primes in

    I(t,d) = (t(1-1/(3d)), t(1-1/(4d))].

Then a uniform deterministic fixed-tape producer chooses distinct odd source
primes in these bands, in the original flag order, using

    O((r/d+1) sqrt(r) ell^2 + D ell) symbol operations
    O(D ell+ell) visited backing cells.

The number of tapes is an absolute constant, independent of D and ell.
The constants include ordinary binary arithmetic, endpoint setup, counters,
table production, output, table/scratch erasure and all head returns. This
is a constructive complexity proof, not a literal instruction trace.

ToikY's PR4029 proves the required abundance for ell>=2^32 and
2<=d<=ell^334. Its theorem is a cited premise. In that domain d<=r:
at ell=2^32, 334 log2(ell)=10688<ell, and log2(x)/x decreases for
x>=2^32. Also d<=r means every dimension/quota counter has O(ell) bits.
Consequently the theorem applies throughout the source domain. Since r/d>=1,
its search term can be written O(r^(3/2) ell^2/d). This improves PR4029's
written O(r^2 ell^2+D ell) producer bound. Neither its analytic cutoff nor
the prime-band or tensor-guard hypotheses change.

## Explicit construction

Count the two quotas in one forward pass through the supplied flags, adding
the implicit final one, and return that head. This costs O(D ell+ell^2), using
ordinary O(ell)-bit counters. Compute each pair of integer endpoints

    lo(t,d) = t-ceil(t/(3d))+1,
    hi(t,d) = t-ceil(t/(4d)).

These are floor(t(1-1/(3d)))+1 and floor(t(1-1/(4d))). Thus their
inclusive integer range is exactly I(t,d). A zero quota needs no scan.

For each nonzero quota, advance a candidate counter from lo to hi once.
For a candidate n, start divisor v=2. Compute v*v. If v*v>n, accept n.
Otherwise compute n modulo v; reject n if the remainder is zero, or
increment v and repeat. Stop the scale scan when its quota is reached.
Accepted n are copied as ell-bit words to the next unused cell of that
scale's owned table. The two tables are sequential tapes, not D tapes or
a random-access dictionary. A finite request without enough primes signals
exhaustion; the theorem assumes abundance rather than inferring it from a
finite search. After selection, rewind both table heads to their origins;
this adds D ell moves to table preparation.

Read the original flags again, synthesizing the last flag one. For each flag,
copy the next ell bits of its table to the output. Each table head moves
only forward during this pass. The quota counts ensure every table word is
consumed exactly once. Return the borrowed flag head. Walk each table head
backwards, erasing every bit, and return the output head. Clear the constant
number of arithmetic work words and return their heads. Borrowed parameters
and flags retain their values.

## Correctness

A composite n has a divisor between 2 and floor(sqrt(n)). Indeed n=ab with
2<=a<=b implies a^2<=n. The scan checks every such divisor before accepting.
Conversely a prime has no zero remainder in that range and is accepted.
The inclusive square test is essential for n=49 and n=121. Hence the
accepted increasing list is exactly the first q_t primes in its band.

Within each scale, increasing scans ensure distinctness. Between scales,
the half-scale band lies below r/2, whereas the full-scale band lies above
5r/6 because d>=2. Thus the tables cannot share a prime. Since ell>=3,
every band element is above 2, so every selected prime is odd. Sequential
table consumption produces the stipulated flag order, including nonmonotone
flags and the implicit final full-scale axis.

PR4029 supplies the consequences for production_axis, the separate period
premise, and the full product ratio. Those are cited consequences of the
unchanged bands, not new proof obligations checked here. This construction
does not call production_common or claim complete numerical tensor recovery.

## Complete cost and backing

An interval of real width t/(12d) has at most t/(12d)+1 integer members.
Even scanning both bands completely therefore visits at most

    C <= (r+r/2)/(12d)+2 = r/(8d)+2

candidates. Quota stopping only decreases C. For n<r the divisor loop makes
at most ceil(sqrt(r)) square comparisons and at most that many remainder
computations. In particular no square-root oracle is invoked. A deliberately
loose bound on each kind of operation over the whole search is

    (r/(8d)+2) ceil(sqrt(r)).

Candidate/divisor increments and early rejection add only a constant amount
per iteration. Multiplication, comparison and binary long division on a
constant number of O(ell)-bit words take O(ell^2) symbol operations on a
fixed inventory of tapes. This bound includes scanning and returning their
heads, and clearing local arithmetic scratch after each use. Products have
at most 2ell+O(1) bits. The words 3d and 4d also have O(ell) bits. The
two endpoint divisions cost O(ell^2). Counters never exceed r or D, apart
from the next loop sentinel, which needs only one additional bit.

Accepted-table writes cost O(D ell). Flag counting, output copying and
clearing/rewinding all tables cost O(D ell+ell^2). There are only two table
heads and one output head. No scan searches through previous choices and no
primality scan is repeated for a different axis. These observations prove
the stated time bound, including failed candidate tests and successful return.

For a successful return the stream-copy phase alone uses exactly
4D ell+2(D-1) head moves under the explicit convention of verify.py:
D ell table moves and D ell output moves during copying, D ell moves
while blanking/returning tables, D ell output-return moves, and two traversals
of D-1 supplied flag cells. Table writes during selection and arithmetic
heads are paid separately above. This count is not a complete machine step
count or a runtime benchmark.

The two tables together have D ell bits. The output has D ell bits and
the flags D-1 bits. Arithmetic uses a constant number of O(ell)-bit words.
Thus even counting output and borrowed flags gives O(D ell+ell) backing.
The procedure's loops have explicit finite candidate and divisor bounds;
there is no recursion and no unpriced primality or random-access operation.

## Evidence boundary

verify.py is a bounded host reference for ell<=16 and D<=32. Its complete
Eratosthenes oracle and integer cross-product band oracle are newly written
checks of this producer. No predecessor executable, scientific receipt or
analytic theorem is replayed. The reference explicitly copies and blanks
bit-cell table pages and counts the stream head moves. Python integers,
allocations and high-level arithmetic do not constitute a literal fixed-tape
lowering. The universal time/backing conclusions rest on this written
construction. Finite counts only corroborate the bounded implementation.

The source's setup was already 2^o(p)=o(V). This reduction does not alter
that qualitative conclusion, a dominant transform cost, or kappa. Emitted
encoded instructions, a complete TensorPlan consumer, physical reserve,
Gaussian approximation, precision, compiler closure, exact recovery and
supplier admission remain open. Independent human and formal proof-kernel
review are unclaimed.
