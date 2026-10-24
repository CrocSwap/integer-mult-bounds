# Exact diagonal extraction by a root-only Walsh average

Status: conditional recovery wrapper. This is standard character orthogonality
applied to the completed graded operator. It is not a new native supplier or a
proof that the actual recursive source has the required interface.

This is a simpler recovery option than the outer small-delta conjugation in
`README.md`. The graded height theorem remains useful: exact averaging does
not itself control large intermediate coefficients.

## Identity

Let the active input and output space have a fixed grading

    V = V_0 direct-sum ... direct-sum V_H.

The grade spaces can have different dimensions. Suppose a completed exact
linear program W_e has the correct Gaussian block on each same-grade block:

    (W_e)_(h,h) = G_(e,h).

All inter-grade blocks may be arbitrary. In particular, the extraction identity
does not itself require triangularity, although the preceding height theorem
uses the compatible filtered endpoint contract to bound exact arithmetic.

Put r=ceil(log2(H+1)), K=2^r, and identify each grade h with its r-bit binary
label. For t in {0,...,K-1}, let D_t multiply every coordinate of V_h by

    chi_t(h) = (-1)^(binary dot product of t and h modulo 2).

Then D_t^-1=D_t, and exact character orthogonality gives

    (1/K) sum_(t=0)^(K-1) D_t W_e D_t
      = direct-sum_(h=0)^H G_(e,h).

Indeed, the multiplier on block (h,k) is
K^-1 sum_t chi_t(h)chi_t(k), which is one for h=k and zero otherwise.
The proof remains valid for unequal grade dimensions and arbitrary operators
inside each block. There are no roots of unity other than +1 and -1; division
by K is a dyadic shift. For H=0, K=1 and the wrapper is just W_e.

For arbitrary input x, preserve x and run the already-expanded complete W_e
once on each signed copy D_t x. Apply D_t to that run's output, sum the K
outputs, and divide by K. This recovers the exact Gaussian output, without
an approximation parameter or final nearest-grid identification.

## One common exact grid

Assume the preceding height theorem has established that every intermediate
map in W_e has dyadic denominator exponent and logarithmic row norm at most

    a = ceil(Astar(e+1)).

Take input coordinates on grid 2^-b with magnitude at most 2^m, where b,m are
nonnegative integers. Every run of W_e can use the common exact grid
2^-(b+a), with numerator magnitude at most 2^(b+m+2a). Signs do not change
that bound. An accumulator for K signed outputs needs only log2 K additional
integer bits. Hence a sufficient signed word width is

    b + m + 2a + log2 K + O(1) = b + m + O(e+1)

for fixed H. Dividing the accumulator by K changes its binary-point location;
it need not increase the stored integer numerator. If desired, the output
grid can be recorded as 2^-(b+a+log2 K). Exact Gaussian semantics ensure the
mathematical result is also on the usual Gaussian output grid.

This removes the H-fold input magnification of the small-delta construction.
The alternative delta construction remains correct under its own hypotheses.

## Placement, storage, and cost obligations

The wrapper runs at the outermost boundary **after the entire recursive
program W_e is specified**. Each of its K runs executes that same program
with the same exact grid. It is not inserted at child returns or included in
every ordinary recursive template. Doing that would multiply the recursive
paid work repeatedly and would be a different algorithm.

For fixed H, K is an absolute constant. The wrapper multiplies the complete
execution cost of W_e by K once and adds explicitly chargeable sign changes,
input copying, and accumulation: O(K) passes over the active data at the stated
word width. A sequential schedule needs the original input, one reusable run
workspace with its original private-field contract, and one output accumulator.
It does not require K simultaneous workspaces. All of this storage and movement
must be carried through the native fixed-tape implementation.

Only the original independent inputs receive productive target credit.
Repeated signed copies are correlated work inputs and earn no additional
independent-output or row-stock credit. This wrapper does not lower the source
template's paid invoice or supply a missing exact Gaussian boundary call.

The constant-factor argument requires H fixed before the eventual input grows.
No assertion about a growing-H algorithm or its multiplication exponent follows
from this note.

## Open application obligations and verification

The actual source still needs the fixed native interface family, exact Gaussian
same-grade blocks on arbitrary inputs, compatible endpoint expansion, and the
full boundary/storage/inverse implementation required by `README.md`.

Run `python3 verify_extraction.py` (also supported under `python3 -O`). It checks
character orthogonality and exact block extraction for nine grade heights with
unequal block dimensions, an exact Gaussian input/output example, and a control
showing that too few characters can leave an inter-grade block untouched.
The general identity above is an algebraic proof; the finite cases are a
regression check rather than a proof of the native application.

The root-only Walsh observation was contributed by the parallel lane-cut
investigation. Prepared with OpenAI Codex assistance, October 23, 2026.
