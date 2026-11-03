# Exact error of the fixed coarse-output four-call reader

ToikY with substantial OpenAI Codex assistance and separate AI implementation
and review. Apache-2.0. Written quantitative corollary with exact bounded
corroboration; no independent human or proof-kernel acceptance.

## Prior result and changed operational boundary

Ali Romman PR1135 already gives the identical four-call endpoint
B(H+A(x))-B(H), the generic same-grid exact-additive obstruction, complete
rounding residues, safe translations and charged grid/state escapes. Nick
Petalas PR6666 gives the exact-dyadic/co-refined capacity result, the sharp
odd-scalar coefficient approximation and explicit arithmetic lowering. We
use those results and elementary floor arithmetic; none of those general
methods or obstructions is new here.

The addition is the exact worst-error and integer-lift minimax law when
only a dirty helper is refined but every reader call returns to a fixed
coarse output grid. This answers a particular operational part of6666's
released fixed-grid question. It does not implement that source's complete
capacity construction or its consumer, nor classify every rounded algorithm.

## Contract, including the inverse reader

Fix a coarse spacing gamma>0. Source and destination are integer numbers
x,Y of coarse cells. The source is preserved; Y may be arbitrarily dirty.
Let B>=0 be an integer bound on |x|. A helper has spacing delta=gamma/M,
where M=2^b and b>=0 is an integer, and has arbitrary dirty integer content H.
For one integral coefficient a, permit the following four calls in order:

    H <- H+a*x
    Y <- Y+O_M(H)
    H <- H-a*x
    Y <- Y-O_M(H),

    O_M(H)=floor(3H/M+1/2)=floor((6H+M)/(2M)).             (1)

O_M is nearest rounding, with half ties toward positive infinity. All
variables in(1) are integer cell indices; the physical reader increment is
gamma O_M(H). The helper displacement is physically a*gamma*x/M.
The inverse reader subtracts the SAME rounded integer, so it is an inverse
integer translation. Independently evaluating Q(-3H/M), or rounding a
negative real addend again, is a different operation: Q(1/2)=1 but
Q(-1/2)=0. Availability and price of the stipulated reader inverse are
hypotheses, not a native instruction supplied here.

The third call restores H exactly, including arbitrary dirt; x is untouched.
The destination increment is

    D_a(H,x)=O_M(H+a*x)-O_M(H).

The target is the copy increment x, so error in output cells is

    e_a(H,x)=D_a(H,x)-x.                                 (2)

An arbitrary initial Y cancels. There is no overflow in this abstract
integer model; finite widths and headroom must be supplied separately.
Direct source-to-output ADDs, nonlinear source preparation, saved residues,
other tie rules, different source grids and delayed output rounding are
outside this four-call fixed-linear-lift family.

## Fixed-coefficient theorem and complete phase distribution

For every integral a and B>=0,

    sup_(H in Z, x in Z, |x|<=B) |e_a(H,x)|
        = ceil(|3a-M| B/M).                              (3)

The supremum is attained. Put d=3a-M. First suppose b>=1, so M is even.
Write

    3H+M/2=kM+r, 0<=r<M.

Substitution into(1)--(2), using integral x, gives exactly

    e_a(H,x)=floor((r+d*x)/M).                           (4)

Since gcd(3,M)=1, as H traverses one period0,...,M-1, r traverses ALL
M residues once. Also O_M(H+M)=O_M(H)+3, so e_a(H+M,x)=e_a(H,x).
This justifies reducing arbitrary, including negative, helper dirt to a
complete finite phase set without restricting the theorem's dirty input.

More precisely, write d*x=qM+s by Euclidean division with0<=s<M,
including negative d*x. Over a full helper period, the error histogram is

    error q:   M-s occurrences,
    error q+1: s occurrences.                            (5)

A zero-count second value is omitted. In particular its maximum absolute
value is ceil(|d*x|/M). Taking |x|<=B yields the upper bound(3), since the
ceiling is monotone. At x=B, choose r=M-1 for positive dB or r=0 for
negative dB to attain the corresponding positive/negative extreme. Each
chosen r has an integral H because3 is invertible modulo M. If B=0, the
error is zero identically and any H attains it.

When b=0, M=1 and O_1(H)=3H for integral H. Thus e_a(H,x)=(3a-1)x,
which proves(3) directly. Formula(5) also holds with its single phase and
s=0. The unified doubled expression in(1) works for every b and negative H;
the b=0 argument is stated separately rather than relying on an even-M
phase derivation.

## Integer-lift minimax and its scope

Minimizing(3) over every integral a gives

    min_(a in Z) sup_(H, |x|<=B) |e_a(H,x)|=ceil(B/M).    (6)

Indeed, M=2^b is not divisible by3, so d=3a-M is never zero and |d|>=1.
A nearest integer a_*=(M+1)//3 has |3a_*-M|=1, proving attainment.
For B=0 every coefficient is optimal. For other B the ceiling can create
ties: nearest-coefficient attainment does NOT imply that a_* is the unique
minimizer. Any finite list of optimizing coefficients in the receipts is
explicitly limited to the declared seven-coefficient window. The written
argument, not that finite window, proves the global minimum VALUE(6).

In physical output units, multiply(3)--(6) by gamma. For any nontrivial
source range B>=1, every finite helper refinement retains at least one
coarse output cell of worst error. For1<=B<=M the optimum is exactly one
cell. This is dirt-dependent error in the stated reader ABI, not a theorem
that every method or every eventual consumer must suffer one cell.

## Why co-refining the output is a different contract

If the output instead stays on the helper's fine grid and the reader adds
3H fine cells EXACTLY, the four-call destination increment in physical units
is gamma*(3a/M)*x. Its error is gamma*d*x/M, with worst value
gamma*|d|B/M and nearest-coefficient value gamma*B/M. This is the elementary
co-refined scalar behavior already present in6666, with no independent
rounding of cancelling reader calls. The ceil staircase in(3) comes from
returning EACH reader call to the fixed coarse output grid; it cannot be
inferred from coefficient error alone. Converting once at the end, changing
the source alphabet or delivering x directly are different contracts whose
costs and errors require a separate comparison.

## Evidence and unpaid obligations

The written argument establishes all b,B,a,H,x quantifiers. The exact finite
domain in CASES.json corroborates all declared helper phases and source
integers, signed histograms, extrema and witnesses. Separate implementations
and later data-only complete row comparison are described in VALIDATION.md.
Finite enumeration does not prove the all-parameter minimum over integer a.
Four authenticated predecessor proof/README objects are inert provenance;
no predecessor scientific executable is imported or run.

The abstract call inventory is two reader translations and two integer
helper lifts of coefficient a (degenerate zero lifts may be omitted).
This inventory is not a complete paid invoice. Helper displacement requires
|a|B fine cells of headroom beyond incoming H. Actual incoming widths,
intermediate destination magnitudes, coefficient synthesis/access, inverse
reader implementation, source restriction/conversion and consumer tolerance
are missing. An allowed consumer tolerance below gamma cannot be met
uniformly for B>=1 by this family at finite b; that conclusion does not
rule out a changed algorithm or charged interface.

No native producer, physical compilation, independent targets, rounded full
caller, precision/stock/storage/tape or recursive/outer admission follows.
All five selected framework assumptions remain. No supplier, kappa or
selected-frontier change is claimed. Exact predecessor pins and full credit
are retained in SOURCE-PINS.json and NOTICE.
