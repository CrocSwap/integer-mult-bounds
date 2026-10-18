# Completing binary callees over arbitrary spectator ranges

This is an adapter lemma for a completed ordinary exchange, not for a weighted
primitive that reads individual ancestor coordinates during the exchange.
The distinction prevents silently giving a black-box callee additional access.

## Contract and quantified statement

Suppose a fixed binary algorithm B exchanges two complete E-bit fields, E>=1,
in a stream of shape

    [2^p] x [2^E] x [2^g] x [2^E] x [2^s].

Zero spectator widths are allowed by omitting a singleton field. For every
nonnegative p,g,s and every arbitrary Boolean payload, the completed endpoint
is the ordinary exchange. It fixes the three spectator coordinates pointwise,
restores heads and parked caller contents, clears its work, and costs at most
C V E^(1-a), with 0<=a<1. C is uniform in p,g,s, parked contents and origin.
Internal borrowing needs no external row factor. These are hypotheses about B.

Assume the retained stream model permits locally confined sequential padding,
restriction, erasure and incremental counters at linear charged scan cost.
Cardinality descriptors are binary integers and preprocessing is polynomial
in their total bit length; no per-ancestor scan charge is silently omitted.

Then B extends to complete shape

    [P] x [Q] x [G] x [Q] x [S],

for all integers P,G,S>=1 and Q>=2. It uses the same fixed callee tape set
plus a fixed adapter set, preserves every spectator coordinate, and costs

    O(V (ceil(log2 Q))^(1-a)),   V=P Q^2 G S,

uniformly in P,G,S. The full temporary volume is strictly less than 32V.
If Q is already binary-complete, the volume is strictly less than 8V.

## Aggregate before padding

Each of the three spectator regions may itself contain arbitrarily many
contiguous complete fields. Its mixed-radix lexicographic index is a single
coordinate in the product of their cardinalities. This is an interpretation
of the existing order, not a payload permutation. For radices r_1,...,r_d,
the index is the ordinary Horner value

    (((x_1*r_2+x_2)*r_3+x_3)*...)*r_d+x_d.

It bijects the original tuples with [product r_i] in exactly their existing
lexicographic order. Original schema metadata is parked once and restored;
the black-box B needs only the three aggregate widths. It must not evaluate
an incoming weighted coefficient that depends on an original inner coordinate.
In the PR2399 application, the ordinary exchange is the black-box call and
weighted coefficients are evaluated outside it after restriction.

For positive integer x define x^+=2^ceil(log2 x). One has x<=x^+<2x,
including x=1. Pad the five fields to

    [P^+] x [Q^+] x [G^+] x [Q^+] x [S^+].

The genuine rectangle consists of coordinates below the original bounds.
Sequentially traverse the padded lexicographic order. At a genuine coordinate
copy the next input bit; at other coordinates write an owned zero. Genuine
coordinates appear in the original order, so input is read once forward.
The product of the five strict inequalities gives V^+<32V. Only three
nontrivial factors remain if Q is binary-complete, yielding V^+<8V.

This is independent of d. Padding every one of d ternary ancestor fields
instead has volume ratio (4/3)^d, which is unbounded. For d=10 this already
exceeds 8. An analysis that charges a fresh factor per ancestor therefore
does not establish the uniform completed-callee contract.

## Chronology and endpoint

Call B once on the entire padded stream, with active width
E=ceil(log2 Q). Let J exchange the two active coordinates. The genuine
rectangle R is J-invariant because the two active genuine bounds are equal;
all spectators are fixed. Hence, for zero extension i and restriction r,

    J i = i J_Q,     r J i = J_Q.

Every original bit occurs once at its exchanged address with its original
spectator tuple. All dummy positions again contain owned zeros at the
completed endpoint. Restriction now removes only those positions. It may
not run at an intermediate callee cut: a valid implementation can move a
genuine bit into a dummy cell temporarily, later returning it correctly.
The finite excursion control swaps one such pair and demonstrates loss if
restriction occurs at that cut, then checks the completed inverse excursion.

After B returns, restrict by one forward scan, erase owned adapter work and
restore the adapter heads. The assumed callee locality and restoration allow
the same parked caller to survive. No original low/high coefficient ring is
changed outside this one completed exchange. In particular, padding is closed
before the next original-ring ADD in PR2399's leaf or header word.

This argument does not verify B's internal cleanup, locality or time. A clean
identity is a counterexample to weakening its endpoint to "restored work".
Unequal active cardinalities are outside the lemma because their genuine
rectangle is not invariant under the same equal-field exchange.

## Uniform cost and descriptor boundary

The callee costs C V^+ E^(1-a)<32 C V E^(1-a). Padding, restriction and
cleanup cost C_pad V^+ plus cardinality setup. Aggregate counters are advanced
incrementally; a binary counter's flips sum to O(number of increments plus
bit length). Nested lexicographic scans initialize at their block boundaries,
so the standard charged scan assumption gives a constant number of linear
passes, not a fresh full-width comparison per payload bit.

The sum of aggregate bit lengths is O(1+log V). Any fixed polynomial in that
quantity is bounded by a finite multiple of V over V>=1. One elementary
bound for integer t>=1 and fixed k is

    t^k <= k! * binom(t+k-1,k),
    sum_(t>=1) binom(t+k-1,k) / 2^t = 2^k.

Thus setup has a uniform linear-volume overcharge; its constant is not a
measured implementation constant. Supplying individual ancestor descriptors
whose total length is unbounded independently of V is a different contract.
The adapter must receive aggregate cardinalities and park unchanged extra
metadata locally, or separately charge its descriptor input length. This
restriction is essential: arbitrarily many explicitly listed singleton
fields do not increase V and cannot be reparsed for free at every call.

Because E>=1, the scan term is absorbed into
(32C+C_adapter) V E^(1-a), for a fixed C_adapter. Fixed extra work tapes and
the completed locality contract preserve finite tape count under the inherited
parking wrapper. No faster callee is constructed by this reduction.

For PR2399's radix-q exchange, Q=q^u and u>=1, E<=ceil(log2 q)*u. Its same
O(V u^(1-a)) conclusion therefore follows even if the earlier binary theorem
only promises binary-complete spectators, with a larger constant. u=0 remains
the identity case and requires no zero-width invocation of B.

## Limits

This closes one logical contract extension identified explicitly in PR2399.
It does not establish its earlier completed callee, improve a stock cutoff,
change any moment, calculate a new selected coefficient or admit any stage.
The executable below checks finite semantic endpoints and actual sequential
padding/restriction. Its reference callee uses indexed host memory; it is not
a tape-time implementation or a fast backend. The universal statement is the
written reduction under the charged-scan and completed-callee hypotheses.
