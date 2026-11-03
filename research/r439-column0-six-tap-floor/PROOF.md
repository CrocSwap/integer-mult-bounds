# Complete finite five-tap exclusion

This proof and its finite verifier were produced by Nick Petalas.

## Frozen linear interface

Use the compressed PR1062 source word pinned in SOURCES.json. Extract the
306 target-only gates after the last helper-to-target read. Delete gates
31, 51 and 52, using zero-based indices, and keep the remaining order.
This is the `ideal303` order of PR2440. Each remaining gate is

    x[d] <- x[d] + x[s]   over F2.

Let L=303. Cuts are c=0,...,L, immediately before gate c when c<L and
after the last gate when c=L. Let U_c be the product of gates c,...,L-1
acting in chronological order, and let e_i be target basis vector i.
The response of a tap into target i at cut c is U_c e_i.

Let S be the original word's scatter matrix, with 111 rows and nine columns.
Column zero is the target

    t = sum_(i: 0 in scatter[i]) e_i
      = 0x61bc96f1867a6f8ccf267ff0dc3c.

The unchanged undo restores the original target data. Linearity therefore
requires the taps of copied source column zero to have total response t.
The nine retained sources are independent, so taps of other source columns
cannot supply a missing coefficient of column zero. These are the source
model and response reduction of PR2356/2407/2440, not a new supplier contract.

## Relaxation and complete search

Define the finite set

    A = { U_c e_i : 0 <= c <= 303, 0 <= i < 111 }.

The verifier computes all 33,744 indexed responses in two ways. The first
maintains suffix columns backwards; across gate (d,s), column s gains
column d. The second injects each basis bit at each cut and executes the
remaining gates literally. Every indexed response agrees. Removing duplicate
values gives exactly 412 elements of A.

Grant every value in A simultaneously, without enforcing COPY intervals.
This is a relaxation of the fixed-order one-slot schedules. If two taps
have the same response, their sum is zero; deleting such a pair preserves
the endpoint and reduces the tap count. Consequently any representation
with at most five taps reduces to a subset of at most five distinct values
of A. A legal schedule with five taps would in particular give such a subset.

Let P_2 be the set of XOR sums of subsets of A of sizes zero, one and two.
Every subset of size at most five can be partitioned into a subset of
size at most two and another of size at most three. Thus a five-tap
representation exists exactly when

    t + xor(B) belongs to P_2

for some subset B of A of size at most three. Allowing overlap between the
two halves causes no false exclusion: common values cancel, leaving at
most five distinct values. This equivalence also covers shorter words.

The verifier materializes all 82,435 distinct elements of P_2. It tests,
without an early cutoff or random sampling, the complete right-hand domain:

    C(412,0)=1
    C(412,1)=412
    C(412,2)=84,666
    C(412,3)=11,571,020.

There are zero hits. Membership uses exact Python integers encoding F2
vectors, not digest comparisons. The set implementation's hash collisions
are resolved by integer equality. The generated receipt binds the complete
input and code; it is not a formal proof-kernel certificate.

This exhausts every representation with at most five taps in the relaxed
dictionary. Therefore column zero requires at least six taps in every
schedule satisfying the declared fixed-order tap contract.

## Complete scatter consequence

PR2440 already gives lower bound four for column 3 and five for each of
the other eight columns. Use those bounds as credited premises. Replacing
only column zero's five by the new six gives

    6 + 4 + 7*5 = 45.

This is a lower bound, not an attaining construction or the exact optimum.
PR2440's upper bound remains 84. No new computation in this package rechecks
its earlier lower bounds or its construction. No complete multiplication
theorem follows, and no inference transfers to a different order, source
mixing alphabet or physical supplier.
