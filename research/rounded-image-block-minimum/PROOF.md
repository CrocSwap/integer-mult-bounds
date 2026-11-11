# The sharp block count for the rounded tensor image

This contribution was produced by Nick Petalas. Apache-2.0.
Claim type: scoped written proof with exact finite corroboration.

## Contract and predecessors

Use the original-coordinate layout of CubeJerry's
[PR6995](https://github.com/CrocSwap/integer-mult-bounds/pull/6995).
For an arbitrary positive number D of axes, let

\[
 t_i=2^{\ell_i},\qquad s_i<t_i<2s_i,\qquad
 Q_i(j)=\left\lfloor {t_i j\over s_i}+{1\over2}\right\rfloor,
 \quad 0\le j<s_i.
\]

Axis zero is fastest. Its target stride is one, and axis i has stride
\(\prod_{k<i}t_k\). The selected address set is

\[
 E=\left\{\sum_{i=0}^{D-1}Q_i(j_i)\prod_{k<i}t_k:
                  0\le j_i<s_i\right\},\qquad S=\prod_i s_i.
\]

The field is the linear interval of T=prod(t_i) records beginning at
address zero. Its seam is fixed; a cyclic change of origin is not free.
All records have the same framed length, and unselected hole contents
are arbitrary. An admitted block copy appends every record in one
nonempty contiguous source interval, in increasing order. The complete
readout copies every selected record exactly once in increasing order
and copies no hole. It does not copy a larger interval and filter it later.

The monotone rounded image, its one-or-two coordinate steps and the
physical extractor are predecessor work. Dugongue's
[PR5566](https://github.com/CrocSwap/integer-mult-bounds/pull/5566),
analysis A11.1, already decomposes the scalar rounded grid into Beatty
runs and permits a cyclic relabeling to obtain exactly t-s complete runs.
The new result is the exact fixed-seam tensor block count, including
which carry boundaries join, and its optimality in the contract above.
No scalar Beatty-run novelty is claimed.

## The formula

Put

\[
 d_i=t_i-s_i,\qquad
 b_i=\begin{cases}1&3s_i>2t_i,\\0&3s_i<2t_i.\end{cases}
\]

Equality cannot occur because t_i is a power of two. Empty products
below equal one. The sharp number of block copies is

\[
 \boxed{R=\sum_{k=0}^{D-1}d_k
           \left(\prod_{i<k}b_i\right)
           \left(\prod_{i>k}s_i\right)
          +\prod_{i=0}^{D-1}b_i.}                         \tag{1}
\]

Equivalently, if S_i and R_i are the selected volume and run count for
axes i through D-1, then

\[
 S_D=R_D=1,\qquad S_i=s_iS_{i+1},\qquad
 R_i=d_iS_{i+1}+b_iR_{i+1}.                              \tag{2}
\]

Thus D backward steps evaluate the answer without constructing T or S
individual records. This is an arithmetic-operation count for the formula,
not a constant-time bit-arithmetic or physical tape claim.

## Proof

First consider one axis and omit its subscript. The source indices
increase by one, and 1<t/s<2, so adjacent Q values differ by one or two.
The initial value is zero. At the last source index,

\[
 Q(s-1)=t-\left\lceil {t\over s}-{1\over2}\right\rceil.
\]

This is t-1 when 3s>2t and t-2 when 3s<2t. Therefore b is exactly the
indicator that the scalar image reaches its last target position t-1.
There are Q(s-1)-(s-1)=d-1+b internal gaps of size two. Every such gap
starts a new run, so the scalar image has d+b runs.

Now treat the lowest remaining axis i as the fast axis and flatten all
higher axes into their own target field. Write S_h and R_h for the
selected volume and run count in that higher field. Each selected
higher address contributes one translated fast-axis image with d_i+b_i
runs. Two successive such images join exactly when their higher
addresses differ by one and the fast image ends at t_i-1.

To see that no other join is possible, let delta be the positive
difference of those higher addresses. The next image's first address
minus the preceding image's last address is

\[
 t_i\,\mathit{delta}-Q_i(s_i-1).
\]

It equals one precisely when delta=1 and b_i=1. The higher image has
S_h-R_h adjacent selected pairs. Starting with the separate translated
images and subtracting exactly their joins therefore gives

\[
 R_i=(d_i+b_i)S_h-b_i(S_h-R_h)=d_iS_h+b_iR_h.
\]

This proves (2), with the empty higher field represented by one
selected point and one run. Expanding the finite recurrence proves (1).

Finally, a contiguous interval that copies no hole lies entirely in one
maximal selected run. Every run contains a selected record that must be
copied, so every admitted readout needs at least R intervals. Copying the
R maximal runs in order attains the lower bound and preserves arbitrary
record values. This proves sharpness for every admitted packet. The
unbounded statement follows from this argument, not finite extrapolation.

## Fixed-seam example and scope

For \((t_i,s_i)=((4,3),(8,7),(8,5))\), axis zero fastest,
the endpoint flags are (1,1,0), and (1) gives

\[
 R=1\cdot7\cdot5+1\cdot5+3=43.
\]

The image has 105 records in a 256-record target field. This is a new
layout invariant for that packet, not a recount of predecessor operation
totals. In particular, multiplying scalar run counts is incorrect, and
using the scalar cyclic count silently changes the prescribed seam.
If the fast axis already has b_0=0, (2) becomes R=d_0 S_1;
no carry into a slower axis can merge two fast images.

The theorem does not lower the cost of scanning the full input. It does
not implement a bulk-copy tape operation, change the producer's order,
prove that arbitrary axis permutations are free, or price native calls,
restoration, precision, storage or compiler work. It gives no new kappa,
supplier admission or complete multiplication theorem. All five selected
framework assumptions remain.
