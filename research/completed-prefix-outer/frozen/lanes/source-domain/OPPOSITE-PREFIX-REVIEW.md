# Review of the changed opposite transform

The opposite procedure in the section **An opposite procedure with
completed slots** of `temporal-reuse/COMPLETED-PREFIX-CODES.md` is correct
under the retained all-size transform hypotheses. This review covers that
section. It does not accept a new encoded supplier or a recursive code.

The reviewed proof SHA-256 is
`c0050de40211bf06ddb386192795d7d2a4ebb0452aa61b1c8139b92f7041cdf5`.
The primary source is `upstream/build/sections/06-transforms.tex` at
commit `3ae9a6f3ac74ded022ab3b4872a7357a621af6fb`, SHA-256
`924316e4bc905066281d8f9e8746a49d8829aeb393688608deb1e61c3c87853c`.

## An independent entry proof

Let the axis length be 2^a and let it divide 2r. Write the original input
address as x and the final physical output address as y. At step h, the
lower slots already contain their final y bits, and the higher slots still
contain their original x bits. There is exactly one butterfly path from
x to y. Its scale is 2^-a. Its total root exponent is

    r sum_h x_h y_h
      + sum_(h<v) (2r/2^(a-h)) 2^(a-1-v) y_h x_v.

This equals `(2r/2^a) y rev_a(x)` modulo 2r. To see this, expand the latter
product by h and v. The h=v coefficient is r. The h<v coefficient is the
displayed twiddle coefficient. Every h>v coefficient is a multiple of 2r
and vanishes. Thus the exact matrix is F_plus B_inverse. The proof uses
the quotient ring directly and does not depend on a finite-field sample.

For several axes, the exponents add and the scales multiply. A twiddle
for one axis is constant on each butterfly pair of another axis. The
axis steps therefore admit the stated parallel grouping. A later step
uses only its current slot and the higher slots. It does not use a lower
completed slot. A code on completed physical slots consequently commutes
with every later exact round.

## Layout and numerical contract

The new opposite visits named positions in increasing h, just as the
retained opposite does. For a chunk round, all axes use the same physical
offset `(h-b) mod K` in consecutive K-bit chunks. The butterflies do not
require equal current recursive lengths. The new exponent uses the
separate value `2^(a_i-h)` for each axis. This distinction is required
when long and short axes participate in the same round.

The same prefix slots, chunk order, descriptor table, and L_inverse work
apply. Conjugating the new logical gate sequence by the retained L, then
restoring L, gives F_plus B_inverse L_inverse. No physical bit reversal is
inserted. An axis list with no long axes satisfies the same argument.

Each new round is a normalized parallel butterfly followed by a signed
coefficient permutation. It is a contraction in the source norm. The
permutation commutes with componentwise truncation toward zero, so the
existing one-truncation-per-round proof applies. There are at most ell
rounds. The source error bound remains `sqrt(2) ell 2^-p`. Prefix rounds
use the existing exact dyadic width bound before their one truncation.
The exponent calculation still takes polynomial work in p per record;
the source lower bound on r absorbs this work in its linear record scan.
No layer call, chunk move, prefix move, or output width changes. The
source asymptotic time bound and convolution error proof therefore remain
valid for this changed opposite.

This conclusion does not supply the precision proof for a code carried
through these rounds. Such a code can have a different norm and can need
additional precision.

## Executed checks

`review_opposite_prefix.py` is independent of the producer. It ran with
`python3 -I -O -B`. It checked 9,455 exact bit-coefficient identities and
27,988 complete matrix entries by root exponents in the polynomial ring.
The cases include unequal axis lengths. It also checked 455 retained
layouts and 3,510 common chunk rounds, including all-short axis lists.
The all-size conclusion rests on the proof above; these finite checks
protect its conventions.

The checker rejects use of one common recursive length for long and
short axes. It also distinguishes F_plus B_inverse from F_plus. The
receipt is `OPPOSITE-PREFIX-REVIEW.json`. This review does not cover the
other theorems in the producer note.
