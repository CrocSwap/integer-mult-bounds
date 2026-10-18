# A reversible quadratic phase stream

## Contract and source boundary

Let `L` be a positive integer. Let `a` be an integer and let `m>0` be an
integer. For `0<=j<L`, set

    z_j = exp(2 pi i a j^2/m),
    r_j = exp(2 pi i a(2j+1)/m),
    omega = exp(4 pi i a/m).

The exact recurrences are `z_(j+1)=r_j z_j` and
`r_(j+1)=omega r_j`. The implementation returns three-shear coefficients
for each `z_j`. It stores no array of phases. It also implements both
directions of the corresponding grid map on one dirty data array.

The data grid is `u=2^-W`, with `W>=2`. The phase state grid is `e=2^-Q`,
where

    b = bit_length(L+1),
    Q = W+2b+20.

There are two complex state values. Their forward update and their reverse
update are exact inverse permutations on the grid. After a pass, the code
runs all state updates backward. It then clears both initial state values.
An inverse data pass generates the same coefficients in forward index order
and reverses each data rotation. It does not invert a rounded complex
product, normalize a complex state, or infer a phase from the data.

`chirp.py` retains the PR1038 leaf, factor-word, precision, and data-layout
interfaces. It changes phase preparation, phase passes, and phase cleanup.
The source pin is `99c71d385171480ecc2c43287aa4a04e1027fcd9`. The exact
retained bytes are under `vendor/pr1038/`. This proof uses PR1038 Sections
4--7 for the grid rotation, dirty conjugation, and inherited PR985 word.
It does not assume PR1054's improved precision. It keeps the original
`ceil(log2 n)` borrowed arrays for `n` factors.

## 1. Bounded rotation coefficients

For an exact unit phase `v`, select a quarter-turn `q` so that the real
component of `i^-q v` is positive. Write that reduced phase as `(c,s)`.
Its three real shear coefficients are `(t,s,t)`, with `t=s/(1+c)`.
The corresponding matrix is exactly the reduced rotation. The product
of the three shears is followed by `i^q`.

The grid map rounds the product in each shear to the data grid. It adds
or subtracts that result exactly. Its inverse reverses the instruction
order and each addition. A shear source does not change in that shear.
Thus both directions use the same rounded product, including ties. The
map is an exact grid permutation for every input magnitude.

We use only `|t|<=1/2` and `|s|<=1`. Each shear matrix has Euclidean norm
at most 2. If both computed coefficients differ from their exact values
by at most `delta`, the difference of the matrix products is at most
`12 delta`. The three grid roundings contribute at most
`(4+2+1)u/2 < 4u`. Thus coefficients within `2^-(W+8)` give

    |S(v)-D v| <= 4(|v|+1)u,
    |S^-1(v)-D^-1 v| <= 4(|v|+1)u.                  (1)

Here the two uses of `v` denote an arbitrary data value, and `D` is the
unit phase. The same bounds apply to the reverse word. These are the
PR1038 bounds. They include the initial dirty value.

## 2. Read a phase state without normalization

Suppose that a dyadic state `v` is within Euclidean distance `E<=1/64`
of a unit phase `v0`. `chart` selects the largest component in absolute
value and rotates its sign to the positive real axis. Ties have a fixed
order. Let `(c,s)=i^-q v` and `(c0,s0)=i^-q v0`. Then

    c >= |s|,   c >= (1-E)/sqrt(2),
    c0 >= (2/3)(1-E)-E >= 41/64 > 3/5.

The exact reduced tangent satisfies `|s0/(1+c0)|<=1/2`. Compute
`s/(1+c)`, round it to spacing `delta`, and restrict it to `[-1/2,1/2]`.
Round `s` to that spacing and restrict it to `[-1,1]`. Restriction to an
interval cannot increase the error from a point in that interval.
The two denominators are at least 1. Therefore

    |t_hat-t0| <= 2E+delta/2,
    |s_hat-s0| <= E+delta/2.                         (2)

The quadrant need not agree with the exact phase's nearest quadrant.
The lower bound on `c0` applies to the quadrant actually selected. Thus
the proof also covers changes of chart near diagonal rays.

The chart adds coefficients to a clean destination. After the rotation,
the code recomputes and subtracts those coefficients before it changes
their phase source. Both generation and erasure pay their division.

At state precision `Q`, use `delta=e/256`. The matrix error from (2) is
at most `4(2(2E+delta/2)+(E+delta/2)) <= 20E+e`.
For a state input of modulus at most 2, one rounded update therefore has
error at most `40E+6e` relative to multiplication by `v0`.

## 3. Paid seed preparation and exact cleanup

The code prepares coefficients for `exp(2 pi i a/m)` and `omega` only.
Let `C=Q+8` and `P=C+16`. For one phase residue `A=a mod m`, set

    q = floor(4A/m+1/2),
    h = 4A-qm,
    theta = pi h/(2m).

Then `|theta|<=pi/4`. A zero `h` gives exact zero shear coefficients.
Otherwise evaluate the first `P` terms of both Machin arctangent series
as exact rationals. Include the weights 16 and -4. The alternating tail
bound gives error below `20*2^-P`. Round the exact sum once to `2^-P`.
Round its product with `h/(2m)` once more. The angle error is less than
`6*2^-P`, and the rounded angle has absolute value less than 1.

Evaluate sine and cosine with `P` exact rational Taylor terms at this
angle. The omitted tails are less than `2^-P`, because
`(2P)!>2^P`. Each total error is less than `7*2^-P`. Both the exact and
computed denominators in `sine/(1+cosine)` exceed 1. The tangent error
before final rounding is less than `14*2^-P`. Round both coefficients
to `2^-C`. Since `P=C+16`, both errors are less than `2^-C`. Their
magnitudes satisfy the bounds in Section 1.

The exact series are not dropped. Each Machin power update is an exact
integer multiplication by 25 or 57121. Exact division reverses it.
Subtract the arctangent terms in reverse order to clear the sum. For a
nonzero rounded angle `X`, the Taylor term update is multiplication by
`-X^2/((2k)(2k+1))` or `-X^2/((2k-1)(2k))`. It is invertible over the
rationals. Subtract the last term from its sum, invert the term update,
and continue backward. Clear the initial terms `X` and 1. If `X=0`,
skip these term updates. This branch also covers a nonzero residue whose
angle rounds to zero. Finally, recompute and subtract the rounded angle
and rounded pi, and reverse the two Machin sums. The code checks zero
at each cleanup boundary.

The coefficient output is a reversible addition to its destination.
Preparation adds the coefficients; erasure subtracts the same values.
In both cases all exact series state is cleared. To prepare `r_hat_0`,
apply the first seed's grid rotation to 1, then erase those coefficients.
The fixed coefficients of `omega` remain for stream use. At the end,
prepare the first seed's coefficients again, reverse its rotation, clear
the resulting 1, and erase the first and second seed coefficients.

This uses a fixed number of rational arithmetic registers. Their widths
are polynomial in `P`; they are not all `O(P)`-bit registers. This change
is explicit in the work and workspace bill below.

Directly rounding a complex product does not provide the required inverse
on the full data grid. At angle `pi/4`, both `(u,0)` and `(2u,0)` round
to `(u,u)`. The three-shear map avoids this collision by retaining each
shear source until its controlled addition is complete. This observation
does not rule out a restricted or checkpointed rounded-product method.

## 4. Uniform drift bound

Let `E_r(j)=|r_hat_j-r_j|` and `E_z(j)=|z_hat_j-z_j|`.
The first seed rotation and (1) give `E_r(0)<=8e`. Set `z_hat_0=1`.
As long as the states have modulus at most 2, the fixed `omega` rotation
gives

    E_r(j+1) <= E_r(j)+12e,
    E_r(j) <= 12(j+1)e.                             (3)

Use `chart(r_hat_j,Q)` for the update of `z_hat_j`. Section 2 gives

    E_z(j+1) <= E_z(j)+40E_r(j)+6e.

Sum this inequality, starting at zero. For all `0<=j<=L`,

    E_z(j) <= (240j(j+1)+6j)e <= 256(j+1)^2 e.       (4)

The chosen `Q` makes the last bound at most `2^-(W+12)`. It also makes
the bound in (3) less than `1/64`. Hence each state is within `1/64`
of a unit phase and has modulus less than 2. Induction proves these
conditions and (3)--(4) together. There is no circular stability assumption.

At emission use `chart(z_hat_j,W)`. Substitute
`E<=u/4096` and `delta=u/256` in (2). The tangent error is at most
`5u/2048<u/256`. The sine error is at most `9u/4096<u/256`.
Thus every emitted coefficient meets Section 1 and the original PR1038
coefficient interface, uniformly over all sites, descriptors, and dirty
data values. Large data magnitudes require the same data precision as
PR1038, not a change to the phase recurrence.

## 5. Exact reconstruction and dirty composition

One forward state step first rotates `z_hat` with coefficients read from
the current `r_hat`. It then rotates `r_hat` with the fixed `omega`
coefficients. A reverse step first reverses the latter rotation. It now
has the identical old `r_hat`, so it recomputes the identical chart and
reverses the first rotation. Every step is an exact inverse, regardless
of the forward approximation error.

After all `L` data sites, execute `L` reverse state steps without touching
the data. The state is exactly `(1,r_hat_0)`. Subtract these initial
values. The next data pass starts from the same seeds and emits exactly
the same coefficient sequence. No checkpoints, phase array, or discarded
rounding residuals are required.

Let the pinned middle dirty word approximate an increment `F x`, where
`||F||<=K`, with error `H(B+1)u` at initial array bound `B`. Execute

    S^-1 on x; S^-1 on y;
    the complete middle word;
    S on y; S on x.

All four phase streams are reconstructed and cleared. The middle word
restores the source and borrowed arrays exactly. The two source phase
maps then cancel exactly. Replacing the middle word by its exact inverse
gives the exact inverse of the complete conjugated word. Its numerical
increment can depend on the target and borrowed data.

With `3Hu<=1`, PR1038 Section 5 and (1) give total error

    32(1+K+H)(B+1)u.                                (5)

For a leaf, `H=68M/beta^5` and `K=M/beta`. For a word, use the unchanged
PR1038 values `N=leaf_calls(n)`, `G=2+r/beta`,
`H=N*68(r+1)*G^(N-1)/beta^5`, and `K=G^N`.
The original `working_bits` admission and integer reserve therefore
suffice. This proof does not reduce the middle word's precision or its
borrowed-array budget. A certified factor approximation must still pay
its own error in addition to (5).

## 6. Scalar work, bit work, and tapes

One prepared `Phase` is shared by all four passes of one dirty call.
It is erased once, after the final pass. One pass performs `L` data
rotations, `2L` forward state rotations, and
`2L` reverse state rotations. It prepares and erases `3L` charts, for
`6L` chart evaluations. A complete dirty
word has four passes. The exact stream counters, including initial seed
rotation and its inverse, are

    60L+6 real products,
    24L rounded real divisions,
    4L forward state steps and 4L reverse state steps.

There are also `O(L)` additions, comparisons, clips, and control updates.
No term evaluation occurs inside the stream loop. At most six seed calls
have nonzero reduced angles. Each call evaluates and clears its series
in `O(P)` rational operations. For the explicit counters, `48P` bounds
all seed terms. Thus the scalar work is `O(L+P)`. The scalar operations
in setup and in the stream have different operand widths.

Let `V=bit_length(m)`, and let `A` be the full width of the original
numerator. Reading and reducing that numerator costs `O((A+V)^2)` with
elementary arithmetic. The original descriptor stays read-only. After
reduction its copied residue has at most `V` bits. Recompute that residue
from the original descriptor and subtract it after the final use. This
cleanup has the same order of work. A common denominator for the two
Machin sums divides `product_(k=0)^(P-1)(2k+1)*(5*239)^(2P+1)`, so its
width is `O(P log P)`. A common denominator for
the Taylor sums divides `2^(2P^2)(2P)!`. Their numerators and each
temporary product have `O(P^2+P log P)` bits. Angle preparation also
uses `V`-bit operands. The conservative bound

    S = 16(P+V+1)^2

covers seed numerator and denominator widths, including intermediate
products. Exact rational arithmetic has an elementary `O(S^2)` bit
implementation. Use multiplication, exact division, and binary gcd;
the gcd loop has `O(S)` subtract/shift steps of `O(S)` bits. This is a
bit upper bound, not a timing claim about Python's `Fraction` class.

For stream work let `T` cover `Q`, the data fractional and integer widths,
`V`, and `log L`. All state values have modulus below 2; all shear
intermediates have bounded modulus. Grid products and chart divisions
reduce to bounded integer multiplication and division on `O(T)` bits.
Elementary fixed-tape arithmetic gives `O(T^2)` per operation. Phase
work, including preparation, erasure, and reverse reconstruction, is
therefore

    O((A+V)^2 + P S^2 + L T^2).                     (6)

The scalar-state maps are explicitly reversible. A bit implementation
must also clear arithmetic scratch. A direct compiler can retain a
bounded elementary arithmetic computation, copy its answer, and run it
backward. Each `O(T^2)`-step stream arithmetic operation then uses
`O(T^2)` clean scratch bits and the same order of work. Reuse that scratch
at the next operation. The corresponding seed scratch is `O(S^2)` bits.
For an in-place bijection, compute its result, swap the two registers,
and clear the old value with its specified inverse. Rounded products
are only used as controlled additions; their unchanged sources permit
this construction. No scratch grows with the number of phase sites.
The Python reference executes the reversible scalar state and exact
series cleanup. It does not emit a bit-gate program or claim the smaller
workspace of an optimized reversible arithmetic compiler.

The original numerator can be wider than `S` or `T`. Its initial
reduction uses the same retained-computation compiler and can require
`O((A+V)^2)` clean scratch bits. A safe peak scratch bound for the phase
interface is therefore `O((A+V)^2+S^2+T^2)`, in addition to its data arrays
and the inherited middle-word workspace. It does not assume `A<=S`.

Keep the same two physical data tapes as PR1038. Reverse state steps
leave both data heads parked. No additional data access occurs. Every
data record access pays its complete width and physical head travel.
The old bounds `4160L` moves per leaf and
`8256(N+1)(h+2)L` moves per complete word remain valid, where
`h=ceil(log2 n)`. Scalar registers use a fixed number of work tapes; seed
and arithmetic scratch are charged as above. Counters use `O(log L)`
bits. Metadata, descriptor scans, middle-word recursive children,
copies, source restoration, and data-head returns retain their original
charges.

For the complete word, replace only PR1038's phase term by (6). Add its
unchanged middle word, factor production, descriptor scans, and data
movement. In particular, the old `O((L+1)P C(T))` phase evaluation term
is replaced by a linear stream plus polynomial setup. No phase supplier,
common-label compiler, or outer assembly inequality is removed by this
substitution. The polynomial seed widths can make short streams slower.
There is no unconditional wall-time speedup or near-linear bit claim.

For example, in a size band with `A+V+log L=O(W)` and data width `T=O(W)`,
the old elementary phase bill is `O(L W^3)`. The new bill is
`O(L W^2+W^5)`. If `L/W^3` tends to infinity, its sufficient bit upper
bound saves a factor of order `W` in that phase bill. This statement
compares upper bounds in that stated size band. It does not prove a
lower bound for the old algorithm or a complete multiplication saving.

## 7. Relation to kappa and remaining scope

At the exact base `abdc6a7002abdbcd9e21bfc5e1a795784deacfdf`, the selected
PR942 certificate gives `kappa=1661960547713947/10^18`. Its binding
supplier is complex. This result replaces an explicit phase-interface
expense and proves its reversible, uniform-error contract. It does not
change a finite supplier invoice, the binding complex moment, the bit
supplier, or any selected certificate. No larger kappa follows here.

PR479 supplies the exact chirp family and its earlier scalar cost context.
PR1038 supplies the dirty conjugation interface. PR1054's constant-phase
precision and PR1025's analytic root-height work have separate hypotheses.
They are not combined in this package. Multi-axis streams, full transform
composition, factor production, common-label realization, physical supplier
hosting, and the multiplication reduction remain outside this result.

The all-length statements above are written mathematical proofs. The
finite exact verifier checks their implementation, selected bounds, and
failure controls. It is not a formal proof of the multiplication theorem
or independent human review.
