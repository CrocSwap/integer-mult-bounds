# Exact prefix substitution

This contribution was produced by Nick Petalas. Apache-2.0.

## Identity and legal frames

Let the six distinct destination roles be `D = (119,169,191,193,204,206)`
and let the three disjoint source roles be `471,525,704`.
Put `z = r471 + r525/2 + 2*r704`. All nine public roles start in frame 3,
whose native label list is empty. The exact pinned source prefix is the
18 ADDs that add those terms separately to each destination. The sources
do not change during the prefix.

Use owned role 770 as t. Its first source occurrence is the INIT at source
event 8448, in frame 737. It is inactive throughout the replaced prefix.
The replacement is:

```text
INIT t in frame 3
t += r471
t += r525/2
t += 2*r704
for d in D: d += t
t -= 2*r704
t -= r525/2
t -= r471
CLEAR t in frame 3
```

All ADDs have distinct source and destination roles in the same frame.
After the first three ADDs, t=z. The six deliveries change each r_d by z
and leave the sources unchanged. The final three ADDs restore t to zero.
CLEAR therefore applies to zero. Every public role has the same value as
after the original prefix, and role 770 is inactive again.

This is an identity for arbitrary public values over Q, R or C. It is also
exact over a dyadic grid fine enough to represent the original half-source
term and the temporary. It assumes legal zero-owned INIT under the source
word's owned-slot grammar. No public helper is assumed zero.

The 14-event replacement leaves the literal source suffix unchanged. That
suffix starts in the same public and owned state, with the same frames.
It has the same subsequent behavior, regardless of whether a separate
correctness theorem about the suffix is true. No independent correctness
claim about that suffix is needed or made.

## Resource delta

Three computation, six delivery and three uncomputation ADDs give 12 ADDs
instead of 18. One INIT and one CLEAR give 14 events instead of 18.
The whole word changes from 18,561 to 18,557 events. These totals are literal
array lengths, not independently accepted supplier counts.

The prefix introduces one lifetime of an existing owned label. The old prefix
has no owned lifetime. The unchanged suffix has at least one, including the
first source use of 770. The new peak is `max(1, old_peak) = old_peak`, without
recounting the old peak. The number of distinct owned labels stays 29.
The new lifetime ends before any old lifetime begins and parks no public data.

Every new instruction is scalar or lifetime bookkeeping in empty frame 3.
There is no new MOVE, native query, paid recursive child or productive target.
All frame transitions and target declarations are retained literally.
The recursive signed-invoice delta is zero. At ADD, INIT and CLEAR prices
`a`, `i`, `c`, the local saving is `6*a-i-c`; unit event pricing saves four.
The physical caller must still price the new lifetime.

## Magnitudes and precision

Assume all real input components have absolute value at most A.
During computation, the temporary's coefficient absolute sums are
`1,3/2,7/2`. During reverse uncomputation they are `3/2,1,0`.
Thus `|t| <= 7*A/2` at every intermediate state. Public destinations have
bound `9*A/2` after delivery. The unchanged sources have bound A.
The old prefix's successive destination bounds were `2*A,5*A/2,9*A/2`.
Both public bounds and the temporary bound are attained by same-sign inputs.

All coefficients are integers or halves. On input grid h every intermediate
value lies on grid h/2, as in the original prefix. The statements apply
componentwise to complex data. They specify exact storage ranges and do not
prove equivalence of independently rounded implementations.

## Verification boundary

The checker authenticates the two retained source members and checks the
literal old prefix, nine entry frames, empty frame 3 and first source use of
770. It checks all metadata and the suffix for literal equality after
construction. It evaluates both local programs against the displayed formula
on nine basis columns, all 512 signed unit-box vertices and 17 signed dyadic
inputs, including the range and restoration checks. Seven mutants exercise
missing delivery, wrong uncompute, changed source coefficient, bad frame,
aliased ADD, premature owned use and bad entry frame.

The verifier does not execute the predecessor's native, caller, root or moment
checks. Finite cases corroborate the proof. They are not a full native supplier
certificate, a multiplication theorem or an optimality proof.
