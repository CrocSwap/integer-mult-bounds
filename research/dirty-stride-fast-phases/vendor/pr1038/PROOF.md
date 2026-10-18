# Reversible quadratic phases for a dirty cyclic inverse

## 1. Contract and the changed operator

Let `Z^w x` have entry `x_((i-w) mod L)`. Let

    D_i = exp(2 pi i a i^2 / m),  0 <= i < L,

where `a` is an integer and `m` is a positive integer. All phase residues
are reduced modulo `m`. No array of phase values is an input or a temporary.
The arrays are distinct arrays of complex dyadic numbers with grid spacing
`u=2^-W`. The source, target, and borrowed arrays can all contain arbitrary
nonzero data. The implementation measures an upper bound `B` on their
initial complex moduli by a paid scan of their component absolute sums.
Use the maximum complex modulus as the norm of an array, and use its
induced operator norm.

The main leaf, with no output shift or multiplier, approximates

    y <- y + (I - b D Z^w D^-1)^-1 x,

where `0 < beta <= 1/2` and `|b| <= 1-beta`. The source is restored exactly.
More generally, the optional constant multiplier `v` and allowed output
shift `s` give the increment

    D v Z^s (I-b Z^w)^-1 D^-1 x,  s=0 or s=w modulo L.

A negative call is the exact inverse instruction word. It approximates the
negative increment. It is not implemented by negating an approximate answer.
The error can depend on the initial dirty target. The precision bound below
includes that dependence.

The complete factor interface implements `D F D^-1`, where `F` is the
complete PR985 factor word. This needs four phase passes for the whole word,
independent of its leaf count. The borrowed arrays keep the PR985 budget
`h=ceil(log2 n)` for `n` factors. This interface requires exactly `h` arrays.
It restores every borrowed array exactly. Only the source and target pass
through the phase maps; borrowed data can stay arbitrary.

This changes the site coefficients. Put `U=D Z^w D^-1`. Its entry is

    (Ux)_i = exp(2 pi i a (i^2-j^2)/m) x_j,
    j=(i-w) mod L.

For the retained example `L=8, a=-3, m=16, w=3`, the phase residues on these
edges are `11, 9, 7, 5, 3, 1, 15, 13`. They are not one constant gauge.
The verifier separates its response from the unphased inverse by more than
`1/8` in a real component for a unit source and `b=1/2`.

## 2. Relation to a retained transform

PR479 and the retained manuscript use

    a_j = exp(-pi i sum_k s_k j_k^2/t_k).

The new interface covers each single-axis family exactly: set `L=t`,
`a=-s`, and `m=2t`. For even `t`, this is the retained periodic chirp
`exp(-pi i s j^2/t)`. The sign, including its conjugate, is available by
changing the sign of the integer numerator. Arbitrary positive moduli and
integer numerators also give a well-defined diagonal on a finite array;
periodicity outside that array is not assumed.

This is an executable dirty realization for that phase family. It is not a
complete transform. It does not implement the multi-axis mixed-radix stream,
arbitrary supplied phase arrays, variable coefficient magnitudes, or a
general variable-coefficient Euclidean solver. It does not replace PR479's
fast scalar interface or its asymptotic scalar row. The slower elementary
phase evaluator used here is fully charged in Section 7.

## 3. Phase generation and coefficient accuracy

Each array pass starts with `E=0` and `delta=a mod m`. After it uses index `j`,
it updates

    E <- (E+delta) mod m,
    delta <- (delta+2a) mod m.

Induction gives `E=a j^2 mod m` and `delta=a(2j+1) mod m` before each use.
This is the single-axis finite-difference rule from PR479. The implementation
restarts the rule on every pass. It never reads a stored coefficient table.

Set `C=W+8`, `P=C+2 bit_length(C+32)+20`, and `e=2^-P`. At each index let

    q = floor(4E/m + 1/2),
    h = 4E-q m,
    theta = pi h/(2m).

Then `|h| <= m/2`, `|theta| <= pi/4`, and
`exp(2 pi i E/m) = i^q exp(i theta)`. The code keeps `q modulo 4` after it
forms `h`. A zero `h` has exact zero shear coefficients.

The remaining cases use the following explicit approximation. These are
error bounds for the executed routine, not assumptions supplied by its
admission guard.

1. Use `pi = 16 atan(1/5) - 4 atan(1/239)`. Each arctangent uses its first
   `P` alternating terms. Round each term separately to spacing `e`. Its
   rounding error is at most `e/2`. Its omitted tail is less than `e` by
   the alternating-series bound. Both Machin weights are included. Thus
   the error in `pi_approx` is at most `(10P+20)e`.
2. Round `pi_approx*h/(2m)` to the same spacing. The resulting angle `X`
   differs from `theta` by at most `(3P+6)e`. For the admitted `P` this
   also proves `|X|<1`.
3. Start the sine term at `X` and the cosine term at `1`. For `k=1,...,P-1`,
   multiply by `-X^2/((2k)(2k+1))` for sine and
   `-X^2/((2k-1)(2k))` for cosine, rounding each new term to spacing `e`.
   These recurrence factors have modulus at most `1/2`. If the preceding
   term error is at most `e`, the next is at most `e/2+e/2=e`. Summing the
   `P-1` term errors and the Taylor tail costs at most `Pe`. The tail is
   less than `e` since `|X|<1` and `(2P)! > 2^P`. Both sine and cosine
   are 1-Lipschitz on the real line. The total error against their values
   at `theta` is therefore at most `E0=(4P+8)e`.
4. The exact cosine is at least `sqrt(2)/2`; `E0<1/4`. Thus the computed
   `1+cosine` is greater than `1`, as is the exact denominator. Subtract
   the two quotients to bound the error in `sine/(1+cosine)` by `2E0`.
   The final internal division rounding adds at most `e/2`. The bound
   `(8P+17)e` covers this result.
5. Round sine and tangent once more to spacing `2^-C`. The program checks
   `(8P+17)2^-P <= 2^(-C-2)`. This holds for the stated `P`; it is also a
   fail-closed integer/rational guard. To check all admitted widths, put
   `b=bit_length(C+32)`. Then `C>=10`, `b>=6`, and `P<3*2^b`. Thus
   `8P+17<2^(b+5)<=2^(2b+18)=2^(P-C-2)`. Each final coefficient is within
   `3*2^-C/4 < 2^-C` of its exact value. In particular the rounded
   coefficients satisfy `|tangent|<=1/2` and `|sine|<=1`.

All polynomial sums are sums of dyadic values and are exact. No uncharged
trigonometric library call or supplied approximate root is used. The
independent oracle computes outward rational intervals for the full angle
`2 pi E/m`. It does not use the quadrant reduction, shears, recurrence of
residues, or production term rounding.

## 4. An exactly reversible grid rotation

For exact `t=tan(theta/2)` and `s=sin(theta)`, the three real shears

    x1 = x - t y,
    y1 = y + s x1,
    x2 = x1 - t y1

give the rotation by `theta`. This follows from
`1-st=cos(theta)` and `-2t+s t^2=-sin(theta)`. Append the exact quarter-turn
`i^q`. In the implementation each product in a shear is rounded to spacing
`u`, with ties toward positive infinity. Each subtraction or addition is
exact on the grid.

The inverse first reverses the quarter-turn, then executes

    x1 = x2 + rnd(t y1),
    y  = y1 - rnd(s x1),
    x  = x1 + rnd(t y).

Every rounded value in this inverse is the same rounded value that the
forward instruction used. Thus the inverse restores both components
exactly for every grid input, with no sign-symmetry assumption about the
rounding rule. Different array sites are disjoint, so both directions can
scan in increasing physical index order.

Let `S_i` be this grid permutation and let `D_i` be the exact unit phase.
A shear with coefficient modulus at most `1` has Euclidean operator norm
at most `2`. The product of the other two shears has norm at most `4`.
The difference caused by the three coefficient errors is at most
`12*2^-C |z|`. The three data-rounding errors contribute at most
`(4+2+1)u/2`. Quarter-turns have norm `1`. The same reasoning applies to the
reverse word. Hence, in both directions,

    |S_i(z)-D_i z| <= 4(|z|+1)u,
    |S_i^-1(z)-D_i^-1 z| <= 4(|z|+1)u.                 (1)

The sharper coefficient contribution is not needed. The program uses the
same immutable descriptor, precision and deterministic evaluator in both
directions. No coefficient approximation is recovered from modified data.

## 5. Conjugation, restoration, and the dirty-value error

Execute, in this order:

    S^-1 on x; S^-1 on y;
    the complete pinned dirty word A, with the requested sign;
    S on y; S on x.

The middle word restores its source and every borrowed array exactly. The
outer maps are exact grid inverses. Consequently the whole construction
restores the original source and all borrowed arrays exactly. Replacing
`A` by its complete inverse gives the exact inverse of this whole word.

Suppose the ideal increment of the middle word is `F x`, with operator norm
at most `K`, and its execution error at initial array bound `D0` is at most

    H(D0+1)u.

Both signs have the same bound. Require `W>=2`, the inherited PR985 admission,
and `3Hu<=1`. From (1), the transformed arrays have norm at most
`2(B+1)`; the unchanged borrowed arrays also satisfy this bound. Thus the
middle error is at most `3H(B+1)u <= B+1`. If `V` is the target just after
the middle word, then

    |V| <= (3+2K)(B+1).

The first target transformation contributes at most `4(B+1)u` to final
error. The first source transformation contributes at most `4K(B+1)u`.
The middle word contributes at most `3H(B+1)u`. The final target rotation
contributes at most `(16+8K)(B+1)u`. Their sum is at most

    32(1+K+H)(B+1)u.                                  (2)

This proves the stated error against the ideal phased operator, including
large dirty targets. It does not assume that the rounded increment is
independent of those targets. It does not tighten PR985's precision result.

For a leaf, let `M>=max(1,|v|)`. The program uses the component absolute sum
of the constant multiplier as one such bound. From the pinned leaf theorem,
we can use

    H=68 M/beta^5,  K=M/beta.

For a complete word with `n` factors, let `r>=1` bound every factor scale.
The validated inner multiplier has modulus at most `r`; the outer multiplier
also has modulus at most `r` since `|b|<1`. Put

    N(1)=1,
    N(n)=2N(floor(n/2))+2N(ceil(n/2)),
    G=2+r/beta,
    H=N*68(r+1)*G^(N-1)/beta^5,
    K=G^N.

PR985 supplies the middle execution bound with this `H`. Each ideal factor
has norm at most `r/beta`; `N>=n`, so `K` bounds the product. Exactly `N`
leaves and both signs of every dirty commutator are executed. The generic
kernel tests do not claim that arbitrary input factors are a certified
approximation to a particular retained polynomial.

To pay execution error to `2^(-p-1)`, `working_bits` takes the maximum of
incoming grid precision, `2`,

    p+1+ceil(log2(32(1+K+H)(B+1))),
    ceil(log2(3H)),
    ceil(log2(48(depth(L,w)+1)/beta^3)).

A retained factor certificate must separately pay its approximation error,
scaled by the source norm. Unit diagonal conjugation preserves that norm
bound. The radix-four test does this explicitly in Section 8.

## 6. Data tapes, magnitude, and storage

The local `dirty_stride.py` has two small changes from the pinned source.
Each input-validation loop reads `data[i]` once into a scalar before it
compares the rounded value. The predecessor expression read it twice but
charged one access. `DERIVATION.diff` records both changes. No arithmetic
or transport instruction in the inverse solver is changed. A separate array
observer checks literal reads and writes against the reported meter and
also gives a physical-movement lower bound. The original source stays in
`vendor/pr985/` with exact byte pins.

Use the same two physical data tapes as PR985. A leaf puts one array on each
tape. A complete word puts its last borrowed array on tape B and its source,
target and other borrowed arrays consecutively on tape A. The inherited
routing swaps a leaf target onto B when necessary and restores that carrier.
No tape head is assigned separately to each array.

Every array read and write, including phase scans and input validation,
charges the distance from the previous physical head position plus one.
The wrapper returns both heads to their origins before the middle word and
after the final phase passes. The middle word also pays its own returns.
The phase generator uses constant scalar registers beside the parked data
head. Reading or writing a complex record costs its complete record width.

For a leaf, input validation costs at most `4L` record moves. The four phase
scans cost at most `16L` together. Their head returns cost at most `4L`.
Adding this to PR985's `4096L` bound gives the conservative bound `4160L`.
For a complete word, input validation, phase scans, travel between the
source and target slots, and returns cost at most `64(h+2)L`. Add this to
PR985's `8192(N+1)(h+2)L` bound. The result is at most

    8256(N+1)(h+2)L.

No control counter or coefficient tape is counted as a free data tape; their
bit costs are stated in Section 7.

A leaf uses no borrowed data array. A word uses exactly `h` arbitrary
borrowed arrays. The implementation holds only a constant number of clean
arithmetic registers in phase preparation, rotation, or one leaf. A phase
object contains scalar descriptors and one scalar pi approximation. There
is no list or cache of arithmetic values indexed by `L` or `W`. The array
list in the word contains references to existing arrays only. The `n`
factor descriptors are immutable input records, with `O(nS)` input bits
for descriptor width `S`. Their sequential access is paid below. This
input storage is distinct from clean arithmetic workspace.

The inherited leaf index stack occupies `O(log^2 L)` metadata bits. The word
also uses `O(log n (log n+log L))` metadata bits. The phase stream adds
`O(log m+log L+log P)` control bits and a constant number of `O(P)` scalar
values. Scalar arithmetic scratch is additional and is included below.
This is not a bit-reversible implementation of its scalar arithmetic.

An explicit data-magnitude bound is

    16384(M+1)(B+1)/beta^7                      for a leaf,
    16384(r+1)(B+1)G^N/beta^7                  for a word.

PR985 bounds the middle values with transformed input bound `2(B+1)`.
The additional factor covers all three shear intermediates, whose norms
are at most eight times the input plus `4u`. The bound also covers the
untransformed initial arrays. The integer reserve is the ceiling of the
base-two logarithm of this bound, plus two sign/rounding bits. There is no
silent fixed-width overflow assumption. The finite replay measures array
writes and each transient real/imaginary pair inside the phase shears. It
does not measure the internal Machin integer widths; those use the
analytical bound in Section 7.

## 7. Complete phase and bit cost

Let `V=bit_length(m)`, and include the original numerator's full input width
when its descriptor is read and reduced. The phase stream uses `O(V)` bit
additions and reductions at each site. Its exact quadratic residue needs
no large square. Initial descriptor normalization and all precision-control
arithmetic are paid setup operations.

One invocation prepares pi once, with `2P` rounded terms. It then evaluates
exactly `4L` phase coefficients. Each nontrivial evaluation has `2(P-1)`
Taylor terms. With the counters used by the reference, the phase layer has
at most

    2P(4L+1) Taylor/Machin terms,
    4P(4L+1) counted scalar products,
    2P(4L+1) counted scalar divisions.

The product total includes the three data shears per phase use. Integer
loop expressions and grid rounding are not extra unit-cost oracles: they
are included in the bit cost below. The scalar-operation count is
`O((L+1)P)`, not `O(L)`. The phase setup is not repeated at each inner leaf
of a complete factor word.

The largest Machin power is below `239^(2P+1)`, so it has fewer than
`16P+8` bits. Every term is rounded before it is added to an accumulator.
The Taylor products and denominators have `O(P+V+log P)` bits. Include the
fractional precision, integer data reserve, original immutable coefficient
and phase-descriptor widths, and these phase temporaries in a scalar size
`T`. The exact rational budget constants `H` and `K` must also fit. If `S`
bounds the bit widths of each input scalar descriptor, their numerators and
denominators can have `O((N+1)S)` bits even when their magnitudes are small.
A constant multiple of `(N+1)S+P+V+2W+I+log L` suffices for `T`, where `I`
is the integer data reserve. This pays the rational control values as well
as the data arithmetic. It gives `O(T)` scalar storage, with a fixed number
of arithmetic work tapes.

Let `C(T)` pay a scalar product or quotient, including rounding, on that
workspace. Schoolbook fixed-width arithmetic gives the sufficient choice
`C(T)=O(T^2)` on a fixed number of tapes. The exact-rational Python program
is a reference for the instructions and rounding. It is not a timing
implementation of that tape bound.

For the complete `n`-factor word, a conservative paid bill is

    external factor production
    + O((N L + (L+1)P + n+N+1) C(T))
    + O(N(h+2)L T + n N T)
    + O((L+1)V + L log L).

The API takes the factor descriptors as inputs; their production is an
inherited external cost and is not improved here. The `n+N+1` term pays
descriptor normalization, factor-margin validation, and the exact rational
precision-control computation, including binary powers and leaf counting.
The `n N T` term pays worst-case sequential factor-descriptor access for
every leaf. Validation of factor margins, source reads, all copies and
swaps, inverse calls, rounding, Euclidean children, and both head returns
are included. The elementary phase setup and term counters fit the displayed
phase cost. Oversized input descriptors and computing the precision bound
are included in setup; their lengths are not inferred from their magnitudes.
For a leaf use `N=1`, `h=0` and its constant descriptor cost.

This construction does not inherit PR479's fast exponential complexity.
It supplies an explicit, slower complete phase interface. Fast phase
preparation can replace it only with a separate workspace and error proof.
No new supplier constant or kappa follows from this bill.

## 8. Independent checks and a retained kernel

The checker uses an outward rational interval oracle for full-angle sine
and cosine. It computes residues by direct integer squares. It evaluates
cyclic inverses by finite geometric sums. Thus it does not repeat the
production finite differences, shear rotation, or Euclidean recursion.
All error comparisons include the oracle interval width.

For the retained `r=4, k=1` polynomial, set `zeta=i`. Its coefficients are
`(1/r) product_(s=j+1)^(r-1)(1-zeta^s)`, hence

    Q(X)=1+(1+i)X/2+(1+i)X^2/4+X^3/4.

The unchanged PR628 root fixture, retained by PR985, gives a rational
factor polynomial `Qhat`. The checker expands its roots exactly and bounds
`epsilon=sum_j |Q_j-Qhat_j|` by component absolute sums. It checks each
stable factor margin. Therefore `A=4/beta^3` bounds `Qhat(U)^-1` for every
unitary weighted cyclic shift `U` in this family. If `A epsilon<1`, the
resolvent identity gives

    ||Q(U)^-1-Qhat(U)^-1|| <= A^2 epsilon/(1-A epsilon).

The checker adds this bound times the source norm to (2). It separately
uses exact rational Gaussian elimination on the matrix for `Q(tau Z^w)`,
with interval right-hand sides after the ideal chirp. Two executions use
nonconstant quadratic chirps, dirty borrowed arrays, and the 128-bit total
budget. The length-eight case is in the retained periodic phase family.
Both the dense ideal comparison and exact complete-word inverse
are checked. This validates these cases and their stated uniform analytic
bound. It is not a complete-transform or multiplication verification.

The finite replay is evidence for the written statements. It is not a Lean
proof, an independent human review, or a proof that the inherited PR985,
all-size compiler, common-label, physical supplier, analytic-transfer, and
multiplication assumptions hold.
