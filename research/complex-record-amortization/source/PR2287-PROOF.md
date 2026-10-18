# A completed selected complex layer

We give a written all-size construction for the selected R480/T16 complex
layer. We use the completed ordinary-interchange contract of PR2234 and the
sequential compact monomial implementation of PR2250. Both contributions
remain under review. We retain the selected finite word and its credited
algebraic certificates, and close the recursive complex-child, row/work and
precision contracts below. We claim no outer multiplication theorem or
change to the selected frontier.

## 1. Statement and model

Write

    C = 1/2 [[1+i,1-i],[1-i,1+i]],
    H0 = 1/2 [[1,1],[1,-1]].

Fix the following rational parameters:

    epsilon=997/1000, spacing=1/500, beta=1/1000,
    tau=99830289/100000000, sigma=99833/100000,
    lambda=249583/250000, lambdaPrime=599/600.

For precision p>=2, let d=floor(p^epsilon) and K=floor(d^spacing). Consider
D<=d selected address bits at positions rho+jK in D consecutive K-bit
chunks, with 0<=rho<K. Other complete address fields are spectators. The
total address/descriptor length is O(p). Each record contains r Gaussian
coefficients, where r=2^Theta(p/d) with fixed positive constants. Initially
each coefficient lies in 2^-p Z[i] and has absolute value at most one.
We permit arbitrary correlations between records, fields and live families.

In the fixed-tape complete-stream model, the construction computes the
exact C^tensor-D layer, then the exact normalized H0^tensor-D layer, in

    O(V d^(599/600))

time. Here V is the original logical record volume, with O(p) bits per
coefficient component. The construction restores spectator and row labels,
clears local work, and can truncate toward zero to p fractional bits only
after the complete normalized layer. That final truncation preserves the
unit disk and has error at most sqrt(2)*2^-p per coefficient.

The bound uses an ordinary binary chunk interchange with cost O(V b^tau),
complete spectators and restored work. PR2234 proposes that contract with
the stated tau, starting from elementary interchanges. It does not depend
on a complex supplier. We therefore use no circular complex/bit assumption.

We specify an algorithm and prove its composition. Our code supplies exact
coefficient primitives, source-bound chronological checks and the numerical
inequalities. We have not emitted the entire architecture as a literal
transition table, run its full O(73,2) payload, or formalized this proof.
Independent review must assess the written argument and its dependencies.

## 2. Finite inputs and the correct tensor lift

The selected archive binds m=73, W=14336 live families, 144 local calls and
the R480 word on 112 source, 112 target and 480 helper registers. Each
orientation has 24767 literal events and an exact 704-column scalar shadow.
The native data include 2896 directed recipes, 224 endpoint adapters and
36 normalized helper-wrapper keys. We authenticate their archived bytes
through the selected invoice. We reuse the retained exact unary/phase
certificates; we do not recount their producers as new work.

The abstract Lemma G in `research/e8-lemma-g-lean/PROOF.md` applies to any
module. For well-labelled events and exact unary transports, it gives

    Run = diag(T_out) S diag(T_in^-1),

where S is the scalar shadow. We replay the current R480 common-frame,
wrapper and private-lifetime conditions with the retained `contains` and
`local` functions from `hpe_audit_local.py`. We compile only those pure
functions with assertions enabled; their writing CLI does not run.

For f columns, replace each unary label T by T^tensor-f and keep the
role-scalar coefficients in S unchanged. At an ADD gate, linearity gives

    T^tensor-f(u+c v)=T^tensor-f u+c T^tensor-f v.

An exact unary product or inverse remains exact after this tensor lift.
Consequently the same eventwise invariant gives

    Run_f = diag(T_out^tensor-f)(S tensor I)diag(T_in^-tensor-f).

This holds on the full function space, including arrays correlated across
columns and helpers. We do not tensor a sum-of-operators identity.

A directed rank-r recipe executes right_f, one C^tensor-(rf) child on the
first r local slots, then left_f. Each slot contains f selected axes; those
rf axes form one contiguous block of K-bit chunks. The source's pre/post
helper wrappers execute the actual inverse right/left monomials. Source
endpoint adapters keep their declared directions. We use the separately
supplied backward word, whose scalar shadow is inverse transpose.

PR2250 supplies the fixed monomial implementation. A recipe with constant
phase i^a receives phase i^(fa), and its affine offset repeats in each
column. A role SCALE coefficient, bridge sign or signed exchange retains
its original scalar. Literal `phase` events are section markers. The
DATA-PHASES translations also repeat columnwise. These distinctions apply
before any cost or precision inference.

For a helper with entrance E and terminal U, the retained exact normalized
identity is

    L_(E,U)^-1 T_U T_E^-1 R_(E,U)^-1 = C^tensor-w tensor I,
    w=dim(U)-dim(E).

Its scalar output row is the helper's unit row, and its input column is
zero off the diagonal. Lemma A therefore splits its completed endpoint
from the other outputs, including on correlated dirty inputs. We verify
the current wrapper keys and common labels; the old R560 instance checks
are not a substitute for these R480 bindings.

## 3. Complete rows and compact fields

Let Gamma=|O(73,2)| and L=W Gamma. The odd-dimensional binary orthogonal
group fixes the all-one vector; its orthogonal complement is a
72-dimensional symplectic space. Counting a nonzero first symplectic vector,
a partner of pairing one and the remaining symplectic basis gives

    Gamma = 2^1296 product_(i=1)^36 (2^(2i)-1),
    2^2627 < Gamma < 2^2628.

The lower bound follows from product(1-4^-i)>1-sum(4^-i)>1/2.
Define the sufficient depth

    D0(e)=0 for e<73;
    D0(e)=1+D0(48 floor(e/73)) otherwise.

Since 73^2>2*48^2, two levels halve the width and
D0(e)<=2 ceil(log2(max(2,e))). Every positive child r floor(e/73), r<=48,
has strictly smaller width and depth at most D0(e)-1.

Use the retained global compact parameters

    G=4 ceil(log2 p)+6, H=dG,
    q0=ceil(log2 L) D0(d), qF=ceil(2H/K), qB=ceil(H/K),
    Q0=q0+qF+qB.

If D<=Q0, apply the selected C kernels individually. Otherwise first
process the first q0+qF and last qB selected axes individually. The first
q0 whole chunks supply a preceding row range of size 2^(q0K)>=L^D0(d).
The next qF chunks supply two H-bit front compact fields; the last qB
chunks supply one H-bit back field. Collapse unused bits into spectators.
All these fields come from existing coordinates, and their initial values
may be arbitrary.

Pad only the row range to the next multiple of L^D0(d), increasing volume
by less than two. A padded row includes the entire compact/body/spectator
rectangle and its records. At an internal node with row count R_rows
divisible by L^D0(e), decode

    [W] x [Gamma] x [U],  U=R_rows/L.

For each family and cover class, the owner packet has exactly v=V/L bits
and the complete unused row range U. No compact-field bit enters this
selector. For a child e', L^D0(e') divides U. A completed child restores its
own row labels, so all subsequent siblings reuse the same stock.

Keep p,d,K,G,H global down the recursion. At width e, each local slot has
f=floor(e/73) axes. The monomial adapters carve (f-1)G<=H bits from each
compact field and preserve the unused parts as spectators. Restore the
compact fields before any scalar gate, child or return.

The row count need not be a power of two. The coefficient kernels scan an
arbitrary number of complete outer rows; `c_axis` implements this directly.
For PR2250's binary-field monomial interpreter, apply the same completed
routine successively to each outer row and concatenate its output in the
original order. Each row retains its complete compact and binary ranges.
Summing O(V_row b^tau) gives O(V b^tau); per-row setup is covered by the long
record allowance. This extension allocates no tape per row. Reassemble the
whole owner packet before invoking a recursive complex child. We do not
replace one complex child by a child per unused row.

At the completed root endpoint, every row receives the same C tensor on
the core and identity on its row coordinate. Padded zero rows are therefore
zero again and can be deleted. The reserved-axis kernels commute with
the completed core tensor because they act on disjoint axes. We recover
the desired layer on the original address rectangle.

## 4. A physical whole-call interpreter

Follow the exact 482-event selected execution schedule. It preserves each
replica's 30 source events, followed by the two global final events. The
source-bound check verifies all 144 call positions, actual bridge touches,
69120 hosted occurrences and their untouched windows. Each call owns
704 distinct live physical families. Thus its owner packets are distinct,
and its packets for different common cover classes are also disjoint.

For one common cover matrix d, gather the 704 owned packets into local work.
An owner descriptor gives family F and g=d sigma^-1. Select that complete
(F,g) packet by a sequential scan of its family. Keep the original family
until the local word finishes. First apply P_d^-1 to the gathered packet,
then its stored entrance Pauli alignment, to obtain the common native view.
After the local word, apply the stored exit alignment and P_d before
scattering. These are fixed monomials for this d.
PR2250 compiles them columnwise. A finite cover table or an enumeration of
73-by-73 orthogonal binary matrices supplies d; this cost is a fixed
constant independent of p and f.

Execute the literal program in that common view:

* At a relabel, execute its stored monomial adapters and one proper-width
  child. The labels themselves are bookkeeping; we do not physically apply
  an entire entrance label before the program.
* At ADD or SCALE, execute the original dyadic coefficient pointwise on
  aligned Gaussian records. Copy preserves its source; clear writes a
  logical packet of zeros, with its extent unchanged.
* For a forward private centre, clear fresh C_k, copy its carrier, transport
  the rank-eight centre and scatter, then clear C_k.
* For a backward private centre, clear at frame zero, gather targets,
  transport to the centre frame, subtract into the carrier, then clear.

The backward private value need not equal a copy of the original source.
We use Lemma G's linear copy/clear semantics and zero private input, not
the BIT transported-source erasure guard. The eight private packets and
coefficient work are fresh scratch, outside the original live row range.
We leave live helper inputs arbitrary.

After completing the local word, invert the common view and scatter all
704 packets back into their original family/cover positions. A full-family
replacement finishes before another child call. We then erase the local
copies and release the zero private packets as empty work. This implements
the stream units and whole-invocation hypothesis
of Lemma A. Its unit helper rows and zero cross-columns permit deferral
of completed helper pieces within the checked untouched windows.

For an idle deadline, visit every original child/port, including children
whose positive-rank part hosting has fully consumed. Apply any remaining
C tensor on the exact pending-axis suffix, using an explicit completed
orthogonal chart to place those axes first, and then apply the declared
translation X_(g theta). The hosted pieces use disjoint actual axes; their
products and the remainder recover the original pending kernel. We retain
the exact axes, rather than only their span or rank.

There are 35840 original idle phase slots, 7526 positive remainders and
6822 fully hosted cases with a nonzero translation. For example, replica0,
child0, port0, family224 has no positive remainder but still needs mask15.
Omitting it maps a post-child delta at zero to zero instead of delta15.
Such a post-child state is possible because the completed hosted operator
is invertible. This is a caller constraint, not a defect in the source.

For one port and cover class g, put T=C_(gq) and
A_s=P_g C_[0,9+8s) P_g^-1. The retained unary DATA-PHASES identities give
initial labels X_(-1)=T, Y_(-1)=I and level-s labels

    X_s=A_s,  Y_s=A_s T^-1.

Idle advances put both pairs at the same level before each bridge. We
check these levels in the actual asynchronous schedule. Consequently each
global X-to-X or Y-to-Y bridge is another common-label ADD. Each completed
local macro advances both labels and applies its decoded scalar shear under
the conjugation formula in section2. The nine local
scalar shears, nine paired bridges and final signed exchange have scalar
matrix I_8; the exact eight-column replay rejects omission of each bridge.
This is a second application of the common-label invariant, not a tensor
power of a one-column role-mixing equality.

Before the exchange, the Y label is A_8 T^-1. The terminal translation
X_(gq)=T^2 changes it to A_8 T. After the signed exchange the labels are
(A_8 T,A_8), while the initial labels were (T,I). Since the complete scalar
shadow is identity, each family receives A_8=P_g C_all P_g^-1. These steps
use unary products, inverses and C_q^2=X_q, so they lift to every f.

Keep the terminal Y translation before the signed exchange. Finally
apply X_delta(g) on every live family, after bank padding and data exchange,
where delta_i=(wt(row_i(g))-1)/2 mod2.

For completeness, the full C tensor has Fourier multiplier i^wt(z).
Orthogonality makes wt(g^T z)-wt(z) modulo four an even additive function;
evaluation on e_i gives twice delta_i. Hence

    P_g C_all P_g^-1 = C_all X_delta(g).

The final translation removes that defect. These unary identities lift
columnwise. Together with the common-label and chronological arguments,
the whole core computes C^tensor-(73f) on every original live row, fixes
its row coordinate and leaves its spectators unchanged.

## 5. Proper-width recursion and fixed work

At width e, stop if e<73 or e^1000<d and apply the selected C kernels
individually. Otherwise write e=73f+delta. First process the delta leftmost
selected axes individually and retain their chunks as completed spectators.
Run the core of section4 on the remaining 73f axes. Each positive child
has width rf with r<=48, so strong induction on e closes its endpoint and
restoration contract. We quantify over arbitrary arrays at each incoming
height t; only the root needs height zero. The leaves require only the
elementary C kernel.
No completed complex supplier is assumed.

For coefficient work, `arithmetic.py` splits the two values of one selected
bit into aligned streams, applies the fixed Gaussian C matrix, and merges
them. The source and scratch heads return to their origins. ADD, dyadic
Horner scaling, exact binary shifts, copy and clear likewise use sequential
word traversals. Each fixed numerical operation costs linear time in the
guarded component width. We supply its precision justification next.

Use W original family streams and at most 720 additional packet/control
slots at a recursive boundary: 704 local copies, eight private centres,
two coefficient streams and six control/return slots. Close monomial,
scalar and selection scratch before a child. The occupied volume is at
most V+720v, with v=V/(W Gamma). Descriptor size is polynomial in p and
fits the long-record charge. Additional fixed tapes used by the ordinary
primitive finish empty before the next complex child.

Apply the retained unequal-buffer parking wrapper with B_slots=W+720.
Its charge is at most

    5(V+720v)-v+9 B_slots-2,

excluding the child and separately charged descriptor setup. Move the
active packet to child I/O, park the other streams and caller state above
the entry delimiter, and restore them on return. The child uses only its
I/O, copied global parameters and fresh local work. It reads no buried
ancestor. Each primitive stops at its own markers and erases its own
visited region. Strong induction therefore gives trace locality, restored
work and a time bound uniform in ancestor contents and stack offset.

The 720 slots are an explicit sufficient compiler-work allocation. They
are not extra live input families and never replace W in the moment.
The selected finite inventory remains 14826; we are not asserting its
original optimized workspace invoice for this implementation. The source's
large precision allowance also covers the enlarged work inventory.

## 6. Exact common-grid precision

Prove the endpoint first for the ideal well-founded procedure over Q[i].
Then bound that procedure's values and simulate it on integer words. This
avoids assuming fixed-grid correctness to prove its own precision bound.

Say an incoming array has height t if its values lie in 2^-(p+t)Z[i] and
have absolute value at most 2^t. A completed C^tensor-u or its inverse has
coefficients in 2^-u Z[i] and absolute row sum at most 2^u. Its returned
array therefore has height at most t+u. A larger internal guard does not
accumulate again after that child completes.

Let

    s=1041408 Gamma, E=2^100000, B=s+E, C0=2^210000.

The rank mass here is unnormalized; the time denominator W does not belong
in this calculation. The selected invoice bounds its local scalar and
compiler work by E. We also count the new Horner implementation's actual
dyadic operations, including all calls and bridge fields; its full-cover
height allowance has 2652 bits and is below E. Monomial movements and
unit phases add no numerical height. The retained 32*73 slack covers
the bounded remainder kernels and local incidentals.

Only one complex child is unfinished under the depth-first schedule.
Before entering it, all previous children have their completed endpoints.
Their total width is at most sf. Let A(e) bound additional height at any
interpreted coefficient point, including an unfinished child. Then

    A(e)<=8e at a direct leaf,
    A(e)<=A(48f)+sf+E at an internal node.

For f>=1, E<=Ef. The inequality

    2B(73-48)>=s+E

therefore gives A(e)<=2Be by induction. It also covers the values parked
in the caller, since those values occur at preceding program points.
The source's finite prefix bounds52/68 and global397 bits are useful
bindings, but they are not this all-depth proof.

The reserved-axis kernels and final normalization add at most18d, so

    A_layer <= (2B+18)d < C0 d.

The source guard checks 32*73B^2<C0 and 2B+18<C0. We reproduce those exact
inequalities, including the cover factor. Enlarging the fixed work-slot
count to W+720 leaves the conservative literal allowance below E.

Choose Delta=ceil(C0d) once at the root. Represent each component on the
grid 2^-(p+Delta), with p+Delta fractional bits and Delta+3 integer/sign
bits. A height-t value has an encoded numerator divisible by 2^(Delta-t).
Before an exact division by2^k, the corresponding height charge leaves
t+k<=Delta, so the discarded bits are zeros. Addition, negation, fixed
Horner multiplication and these shifts therefore simulate the ideal
procedure exactly. Headroom prevents signed overflow.

Keep this grid at every child. Completed-child cancellation restores
divisibility without rounding or re-encoding. The code checks exact
halving and rejects a rounded-child counterexample. Arithmetic buffers
are cleared after each coefficient. Bit-interchange work may hold arbitrary
strings; we interpret them as coefficients only after the completed bit
operation returns.

For fixed epsilon<1, Delta=C0d=o(p), and the guarded component width is
O(p). Even below the eventual regime it is at most a fixed multiple of p.
Inserting and removing guard bits thus changes V only by a fixed factor.
The long-record hypothesis remains valid. Constants are enormous; we
claim no practical precision or cutoff.

## 7. Uniform layer time

Use the selected child histogram

    {1:349604, 2:60192, 3:62585, 4:20448,
     5:11808, 7:7, 8:1152, 48:4866}.

For each cover matrix a child receives volume V/(W Gamma). Summing the
Gamma identical cover counts cancels Gamma in the recursive coefficient.
Selections, replacements, parking, scalar arithmetic and fixed monomial
routes contribute

    O(V((e log p)^tau+1))

per internal node. Their finite number may include large cover-dependent
constants. Per-record preparation is polynomial in p and is absorbed by
r=2^Theta(p/d). The same reasoning covers per-outer-row adapter dispatch.

Let mu_x=sum_r (H_r/W)(r/73)^x. Both retained rational engines give

    mu_sigma<1, 1-mu_sigma>15999/10^9,
    mu_1=1017/1022.

We evaluate one coarse point, 1-sigma=167/100000, rather than search for
a new root. Integer floors can only decrease the weighted widths.
The strict sigma-moment gives total leaf cost

    O(V d^(sigma+beta(1-sigma))).

The base cutoff is max(73,d^beta); the factor73 changes only the constant.
For internal widths e>=d^beta, e^tau<=d^(beta(tau-sigma))e^sigma, since
sigma>tau. Summing the strict weighted tree gives internal cost

    O(V (log p)^tau d^chi),
    chi=sigma+beta(tau-sigma).

Root reservations cost O(V(log(2d)+d^(1-spacing)log p+1)). In particular,
Gamma affects the row-depth constant, not the reservation exponent.
The exact exponents are

    chi=99832997289/10^11,
    leaf=99833167/10^8,
    reserve=499/500.

Each lies below lambda=249583/250000, and lambdaPrime-lambda=1/750000.
Thus the retained logarithmic factors fit O(V d^lambdaPrime). The small-D
reservation fallback obeys the same bound. For the finite initial range
where an asymptotic compact-field inequality fails, use individual kernels;
enlarge the fixed time constant to cover that range.

Finally, 1-epsilon(1+spacing)=503/500000>0 gives the required address
geometry, and 1-epsilon=3/1000>0 gives both the precision and long-record
conditions. Also epsilon*spacing>0, so K/log p tends to infinity. No
positive-rank fallback surcharge belongs to the complex moment.

## 8. Normalization and evidence limits

Let S_D multiply a record by i raised to the sum of its selected bits.
Evaluate that phase once per record, using polynomial control work, and
apply it coefficientwise in linear record time. The retained identity is

    H0^tensor-D = b^D S_D C^tensor-D S_D,  b=(1-i)/2.

For k=floor(D/2), use

    b^D=(-i)^k 2^-k b^(D mod2).

This needs an optional (z-iz)/2, one quarter-phase and one variable binary
shift, each linear in guarded word width. It does not perform D full
record passes. `normalize_b` executes that rule. Since H0 has absolute
row sum one, the completed normalized layer preserves the input unit
disk. Final truncation toward zero changes each component by less than
2^-p, preserves the disk and gives the stated sqrt(2)*2^-p error.

Our checks replay the retained current common-label/scalar conditions,
bind every current native recipe, reuse the selected chart/phase audit,
and verify chronological owner windows and all idle phase deadlines.
They also execute Gaussian kernels with a non-power-of-two outer row
count, exact scaling, normalization and inverse cancellation. The row,
height and coarse time inequalities have exact integer/rational checks.

These checks support the written construction; they are not a complete
payload execution or proof-assistant verification. We retain the finite
Clifford and hosting results as attributed source premises. The outer
FFT/convolution embedding, analytic error transfer and integer packing
remain outside this contribution. We have not changed the selected
frontier or proved an integer-multiplication exponent here.
