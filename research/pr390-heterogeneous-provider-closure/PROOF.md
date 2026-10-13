# A closed source-specific heterogeneous provider and exact-RAM witness

## Statements and model

Write C_v=(1+i)I/2+(1-i)X_v/2 on binary addresses, and C_n for the product
along the n standard axes. Thus C_v^2=X_v and C_v^-1=X_v C_v. All native
inputs have a specified scalar i. Exact prepared scalar arithmetic and Nat
add/subtract/multiply/divide/remainder/compare have unit cost; indexed reads,
fresh arrays, stack, loops and recursion are charged. One fixed polynomial
integer/arena cap is required. Data remain linear and are not tested for zero.
These are the pinned Sussman `RAM.lean`/`ProgramBounds.lean` semantics, not a
finite-alphabet multitape model.

For every fixed K>=1, let m=16K+9. There is an effective finite physical word
on its declared live families whose operator is the direct sum of C_(mf) on
every actual live array, for every f>=1. Arbitrary correlated data/helper values
are admitted. Private work is cleared and ends zero; old private contents are
not restored. The simple all-K stock is W_K=1806K+783 per orthogonal owner.
Constants may depend on fixed K; K is not chosen as an unbounded function of
the input while treating those constants as fixed.

The optimized K=4 stock is W=58,899, m=73. It yields one fixed closed native
kernel/Walsh program with work O(2^n(n+1)^(1023/1024)). The pinned source already proves the distinct all-length cyclic exponent
1-7474546/10^10, with the canonical-root convention stated below. This native
provider is an alternative non-Lean witness for the same consuming premise;
it neither improves nor newly establishes that cyclic theorem.

## 1. The pinned finite leaf and exact charts

The three literal inputs are the public PR390 prefix word, preconditioning
and early-sink record listed in SOURCE.json. The complete reconstructed scalar
word has forward endpoint (x,y,h)->(x,y+x,h), backward endpoint (x-y,y,h),
and zero active-private output, on all 1,023 live plus eight initially dirty active scratch columns. Its guards
require identical exact current frame IDs at each live ADD, not equal spans.
The two sinks 355 and 403 stop in rank-eight frames 206 and 221; all other
781 helpers exit in the full rank-nine frame. Subsequent cleanup never touches
those sinks.

The local paid ranks are

```
r       1    2    3    4    5    6   7   8   9
H    2090  601  524  109  215  332  58  24   8
```

Their mass is 9,037. The eight rank-nine copied-center calls are included.
There are 14,940 rational additions and 16 outer clears. Denominators factor
into twos and threes. Binary doubling/accumulation, divisions and private
clearance give conservative real-component price 165,748 per orientation.
These finite facts are directly reproducible by the supplied own checker.

For an ordered independent frame U of rank r, extend its columns to G and set
Q=I+G^-T G^-1, K_U=D_Q P_G. Here
q_Q(x)=sum Q_jj x_j+2 sum_(j<k)Q_jk x_j x_k modulo four. The source canonical
chart is T_U=K_U C_r K_U^-1, with T_0=I and T_full=C9. Frame 1 is the ordered coordinate permutation
(256,128,64,32,16,8,4,2,1), so its G is orthogonal, Q=0 and its full chart
is C9. Its binary Z-image
Lagrangian is {(u,u+v):u in U,v in U-perp}. For U contained in V, the
intersection has dimension dim U+9-dim V. Involutivity of these binary charts
therefore gives relative B-block rank dim V-dim U.

That rank has a constructive exact lowering. For a Clifford with Z images
(B;D) and rank B=r, a binary permutation P_A moves im B to the first r axes.
Commutation implies D0=Q0 B0 with Q0 symmetric, where B0 is surjective on
those axes. A quadratic phase kills D0; H'=S C_r S exchanges the first r
binary X/Z coordinates. The resulting V=H' D_Q P_A U is monomial. Exact
inversion gives

```
U=(P_A^-1 D_Q^-1 S^-1) C_r (X_E S^-1 V), E=sum_(j<r)e_j.
```

Both outside operators are affine-quadratic monomials. For r=0 there is no
child. All entries lie in Z[i,1/2]; a unit-modulus global monomial entry is a
fourth root of unity, since a^2+b^2=4^d repeatedly forces both integers even.
Thus this constructs one rank-r child and exact index/phase factors. The constructive lowering computes signed Pauli images and a nonzero vacuum
entry to fix the global phase, as well as binary action. Literal phased
recipe values are not supplied in this package; no unpublished audit is a
premise of this existence proof.

## 2. All-f transport, dirt and scratch

At every cut maintain physical role = F_j^tensor(f) times its logical array.
A frame change applies (E F^-1)^tensor(f). An equal-frame ADD is correct
because F^tensor(f)(u+a v)=F^tensor(f)u+a F^tensor(f)v. Tensor product is used
multiplicatively, never on an addition of role operators; a stays a.

Coefficient scratch is cleared, built in the common frame and cleared again.
A copied center copies a full-frame source, applies the downward full-to-base
child, scatters in the base frame and clears. The backward macro gathers,
applies the upward child and subtracts into the source. COPY/CLEAR are not
inverted; the effective live macro is the invertible shear being dualized.
Inverse-adjoint preserves chronology and fixes unitary chart jumps.

The complete operator is D_out(S tensor I)D_in^-1. Its helper block is
diag(E_h F0^-1)^tensor(f), with no data coupling. Right-composing an arbitrary
singular or role-mixing dirty operator Z requires no Z inverse and gives that
same residual times Z. Universal value identities include correlations with
data. Whole completed macros may share helpers serially; unfinished macros
are not interleaved.

A monomial phase i^(gamma+q(x)), address Gx+b, lifts to f gamma, repeated b and
the sum of lane phases. Both sink adapters require (-i)^f. An ordinary role
sign is one -1. The 793 private families are nine centers, 783 tableaux and
one coefficient family. Only eight centers and the coefficient stream are
read. The ninth center and 783 tableau streams are allocated, cleared and
charged but never read; all clearance is paid, including unused storage.

## 3. Global geometry, chronology and cover

Set s=2K+1. H is the first nine coordinates; Q_t is the first t fresh
eight-coordinate blocks. The local-owner window is
Phi_(d,t)(T)=P_d(T_H C_Qt)P_d^-1. All local jumps cancel the common base.

For a port q of weight three or seven, choose its least zero coordinate j,
w=q+e_j, and O_q=(I+w w^T)Swap(0,j). Its ordered columns are the orthonormal
basis (q,u1,...,u8). Rho_(q,0)=I. For t>=1, Rho_(q,t) fixes q and exchanges that perpendicular plane
with fresh block t; it is a symmetric orthogonal involution. Physical data
owner g uses d=g rho. The desired cuts are

```
D_X(-1)=C_q, D_Y(-1)=I;
D_X(t)=C_[0..8+8t], D_Y(t)=D_X(t) C_q^-1, t>=0.
```

Raw endpoints conjugate both the local chart and C_Qt.

**Local endpoint adapters.** Canonical charts generally are not C-products,
so the character lemma below does not apply to them directly. For port q,
let E_q (frame 122+j for target j) span q-perp and J_q=product_(j=1..8)C_uj.
The binary actions of T_<q>, C_q, T_Eq and J_q are involutions. The first
pair shares Z-image {(lambda q | lambda q+v): v perpendicular to q}; the
second shares {(u | u+lambda q): u perpendicular to q}. Thus
M_q=C_q T_<q>^-1 and N_q=J_q T_Eq^-1 preserve the Z-Lagrangian. They are
exact Z[i,1/2] monomials with fourth-root phases, by Section 1. Apply
P_d(M_q^-1 tensor I)P_d^-1 at every X entry (from the translated C-product
cut into the canonical T_<q> window), and P_d(N_q tensor I)P_d^-1 at every
Y exit and at sinks 355/403 (from T_E into J_q; frames 206/221, q=508/499). These
240+2 rank-zero local adapters are independent of K,t,f and owner. They
turn every endpoint into a product of C_v^±1 before the remaining translations.

**Character phase.** For signed directions v define
A=sum a_v vv^T over F2 and ell_j=sum a_v v_j modulo four. The multiplier is
i^(ell.z+2 sum_(j<k)A_jk z_j z_k). XOR expansion modulo four proves it, and
all C_v fix the uniform vector. Equal Gram matrices and even linear
differences give translation delta_j=(ell_wanted,j-ell_actual,j)/2 modulo two.
Orthogonal plane exchange proves Gram equality for every K and stage.
The diagonal Gram equality also forces the linear differences to be even. Entry
and exit corrections are computed separately; they generally differ.

Idle moves are the explicit perpendicular axes plus fresh blocks from cut -1,
or just new coordinate blocks from a nonnegative cut. Their rank is 8(v-u).
Both roles have the same desired cut before each same-side bridge ADD.

Use F1,B1,F1,B2,F2,...,BK,FK. Stage t moves cut t-1 to cut t.
Only for p<K, after B_p borrow X_(p+1) into X_p and subtract Y_p from
Y_(p+1); after F_p undo that borrow and add Y_p to Y_(p+1). B_K and F_K
have no bridge. Put
b0=0, b_p=y_p-b_(p-1). Induction gives active (x_p,x_p+b_p) before B_p and
X_p=-b_p afterward. Recover for p=K-1 down to 1 by Y_p-=Y_(p+1) and
X_(p+1)+=X_p. This descending recovery gives Y_p=x_p and
X_p=-(b_p+b_(p-1))=-y_p. Signed exchange restores the ordering. The original
X stream has accumulated C_m C_q^-2=C_m X_q, so terminal X_q is mandatory
in owner coordinates: its physical translation is X_(gq).

For any orthogonal g define delta_out(g)_j=(weight(row_j(g))-1)/2 modulo two,
in output coordinates. Then P_g C_m P_g^-1=X_delta_out(g) C_m: the Gram
matrix is I and the linear coefficients are the odd row weights. Apply
X_delta_out(g) to every final live stream. If using owner coordinates, define
delta_in(g)=g^-1 delta_out(g); the physical vector g delta_in is exactly
delta_out. These coordinate conventions must not be mixed.

The corrected sink residual is J_q=product_(j=1..8)C_uj. If A sends its
ordered axes to a coordinate slot I, the bank owner is g=d A^-1, so
P_d J_q P_d^-1=P_g C_I P_g^-1. For each fixed g and slot there is exactly
one d=gA. Distinct slots commute; paid padding completes C_m. Each call's
actual family/owner keys are distinct. This works for arbitrary accumulated
bank values by the complete block-diagonal endpoint, not a cleanliness claim.

The old homogeneous contract remains false: on chi_q for q=508 or 499,
J_q has multiplier 1 whereas C9 has i^7=-i. A monomial-only patch cannot raise
B-block rank eight to nine. A separate rank-one child repair is possible but
has a distinct stock/profile; the theorem here uses the heterogeneous stock.

## 4. Paid profiles

For B4, 32 replicas give 64 rank-eight and 24,992 rank-nine residuals per
stage. Eight banks have one 9-slot and eight 8-slots; 3,123 banks have eight
9-slots and one paid 1-pad. Thus W=30,720+9*3,131=58,899. The profile is

```
r        1       2       3      4     5     6     7     8    9    16    32    48
H   630027  173088  150912  31392 61920 95616 16704 29952 2304 15360 15360 15360
```

It includes 288 complete calls, all idle children and 28,107 bank pads; mass
4,289,643=73W-9,984. Local scalar price is 47,735,424. Endpoint, stage,
terminal and cover translations, scalar bridges, exchanges, owner generation,
addresses, materialization and private clearing have separate nonchild costs.
Zero-rank operations are not free.

For general K use one helper per bank per stage and pay its unused m-r axes.
The stock W_K=1806K+783 has deficit Delta_K=96K-72>0. All ranks are positive
and <m. With delta=Delta_K/(m W_K), kappa_K=delta/(4m), the moment at
1-kappa_K is at most (1-delta)m^kappa_K <=1-delta/2<1, using log m<=m and
exp x<=1+2x on [0,1/4]. This gives an effective positive saving for each fixed
K; the optimized B4 saving is not asserted for that simpler whole family.

## 5. Closed RAM compiler and recurrence

For an m-bit monomial repeated f times, seed the address table with repeated
b and phase f gamma. Adjoin one input bit at a time: copy the low half,
toggle at most m output bits in the high half, and add its linear phase plus
quadratic terms from prior INPUT bits of that lane. Nat division/remainder
extracts bits using precomputed powers. Fewer than 2N entries are built;
initial offset/powers take O(mf)<=O(N). Thus cost is O_m(N). A separate
f*m offset pass per output would not satisfy this bound.

A paid bit-coordinate permutation gathers rf active bits for a rank-r
child. Call the same kernel once per fiber, store its array and flatten once;
there is no call per output element. Inverse C uses a paid X translation.

For odd m=2h+1, G=|O(m,2)|=2^(h^2) product_(j=1..h)(2^(2j)-1). Enumerate
all 2^(m^2) matrices, test orthogonality and prefix-compact owner codes.
This finite supplier-dependent preparation is charged, not an owner oracle.
Fresh pointer stock R=G(W+793) is rebuilt whenever a role changes; its R
factor and cumulative allocation are charged. Conservative bounds are

```
P=1237995; Mpass=11032740; Spass=49048320;
E=1+Mpass+Spass+16P=79888981;
A=2^24(m+1)^6(R+1)[G(E+W+(W+793))+1]+2^(m^2+20)(m+1)^6.
```

**Nonchild batch-cost lemma.** Let N=2^(mf), L=GW and
c_m=2^24(m+1)^6. The compiler uses the following conservative array-pass
*templates*, not measured optimal counts:

```
boundary=288*(240+2+480)+15360+W;
Mpass=8P+4*boundary;
Spass=288*165748+4*69120+8*15360+4*793*288;
E=1+Mpass+Spass+16P.
```

The 8P template allows input/output gather and flatten, pre/post monomials
and inverse translations for every positive-rank child. Four passes per
boundary monomial allow table construction, application and stock rebuilding:
240 data plus two sink local adapters and at most 480 entry/exit translations
per local call, 15,360 idle/terminal data slots, and W final cover corrections.
The scalar template includes all 288 local real-component prices. There are
at most 69,120 scalar bridge/recovery assignments: per replica and port,
4(K-1) forward bridge assignments and 2(K-1) descending assignments at K=4.
Four passes per assignment suffice. The 8*15,360 allowance covers signed
exchange and data-tail handling, and 4*793*288 covers private allocation and
clearance even for unused families. Finally 16P permits fiber/child metadata,
stack and flatten administrative passes. Thus E0<=E per owner per batch.

Each pass costs at most c_m(N+R+1), including a fresh R-entry pointer stock.
For address/phase tables, the doubling construction has fewer than 2N
entries, and each entry uses at most a fixed multiple of (m+1)^4 primitive
index operations for matrix products, quadratic phases and composition.
Gather/flatten/scalar/clear loops use fewer primitives; the displayed c_m
also covers loop counters, initialized powers and pointer work. All are
unit-cost scalar/index operations in the declared model. A fiber template
walks each fiber once and flattens once: its output entries total N. Child
work itself is charged to T, rather than repeated per output.

Enumerating all 2^(m^2) candidate matrices, orthogonality tests, owner prefix
compaction and fixed code tables costs at most 2^(m^2+20)(m+1)^6 per batch.
The chart dimension is fixed at nine; its finite normal forms are compiled
once and repeated lane-wise, rather than enumerating any f-dependent group.
Since N>=1, R>=W, L=GW>=G and
N+R+1 <= (R+2)N <= 2(R+1)N, the displayed A dominates both all-owner pass
costs and that code/enumeration cost in A*L*N. Indeed its first bracket is
at least G*E*(R+1)c_m, and L>=2 supplies the harmless factor two. This
charges source preparation, pointer rebuilding and enumeration, even for the
smallest batch. The bulk bill is therefore
G sum H_r 2^((m-r)f)T(rf)+A(GW)2^(mf).

Let L=GW, a=ceil log2 L=2644, B0=16(a+m+10)^2=118984464. Below B0 use
classical butterflies. Otherwise choose lambda=ceil log2(n+2),
f=floor((n-a-2lambda)/m), ell=n-mf. Then f>=1,
a+2lambda<=ell<a+2lambda+m, and rf<=48f<n. Bounded recursion with initial
fuel n suffices. Process only complete batches of L fibers, fewer than L
leftovers classically, then ell high directions. L/2^ell<=1/(n+2)^2 pays
the leftovers. If q=floor(2^ell/L), qG/2^ell<=1/W; no fractional bulk is used.

Define T as worst-case work over all inputs, Paint colors and Bool modes.
For t(n)=T(n)/2^n this gives

```
t(n)<=sum (H_r/W)t(rf(n))+A[a+m+2ceil log2(n+2)+1].
```

The exact integer-root certificate in PROFILE.json proves
mu(1023/1024)<=1538808304431335/1538896445833216=1-epsilon<1,
epsilon=88141401881/1538896445833216. With
C=A[B0+(a+m+9)/epsilon+1], strong induction covers the finite base and bounds
the child sum by C(1-epsilon)n^p and toll by C epsilon n^p. Hence
T(n)<=C2^n n^(1023/1024) for n>=1, with T(0)=O(1). Enlarging the
constant gives T(n)<=C'2^n(n+1)^(1023/1024) for every n>=0. Walsh conversion
H_n=(1-i)^n D_n C_n D_n, D_n=diag(i^weight(x)), costs O(N) extra.

Work, allocation and integers are bounded by K0(N+2)^2 for fixed K0. Choosing
fixed d>=2+ceil log3(max(1,K0)) gives the closed cap (N+2)^d. The program,
constants and cap precede every input family and color/mode. Scalar heights
are unrestricted; this does not establish bit complexity.

## 6. Attributed all-length cyclic consequence

Use the literal Sussman pin in SOURCE.json, without claiming equivalence to
another manuscript/Lean version. BinaryFrames/givenBits match this Gaussian
kernel and specified i. The stronger p=1023/1024 satisfies the exact consuming
`hillsZ_program` budget at alphaZ=1-7474547/10^10 for all Paint/Bool/families.
The pinned source already proves `transform_main_orderZ` and convolution
via its P193 `hillsZ_program`. This stronger native kernel is a second,
non-Lean witness for that same premise; no replacement Lean term has been
built. It neither newly proves nor improves the inherited cyclic exponent.

The source's charged exact-width compiler is acyclic: Newton evaluation gives
F=T diag(c^-1)T^T, with proved nonzero prepared denominators; classical FFT
pulses prepare truncated Toeplitz work. Disjoint dirty rectangular commutators
restore their intermediate arrays on all columns. Its fixed six-positive-C
shear decomposition uses nonzero prepared t1=1+mu conjugate(mu) and
t2=mu-t1, without a data-value test. Conjugation is of prepared coefficient
DAGs only; variable input data remain linear. The actual halo score is
quadratic in its exponent.

Materialized common-slot sectors have disjoint widths summing to the volume;
prefix metadata and gathering/scattering are charged. Synchronized transforms
and CRT relocation use address sum x_i M_i modulo L and root z^(M_i^2).
The source integer selection has 2N<=L<4N, pairwise-coprime axes and
halo exponent O(loglog N), with polynomial(log N) preparation. Dense doubling
power tables take fewer than twice their final entry counts. The positive
chirp identity i^2-(i-j)^2+j^2=2ij, with L>=2N, gives the full requested DFT.
Two forward working transforms, including the prepared fixed kernel, and one
inverse transform are all charged. This is not a free fixed-kernel transform.

The fixed order is D(N)=receipt(N): in the broad branch (2N)L2^orderE(N),
otherwise N. L<4N and 2^orderE(N)<=N give 0<D(N)<8N^3. Broad D is divisible
by 2N, L, four and the necessary dyadic orders. A supplied canonical positive
root exp(2pi i/D) powers to the canonical local roots and positive i. The
small branch uses the direct root-N DFT. Root acquisition is one separately
charged primitive, not an algebraic construction from rationals and i.

UniformBounds extracts one fixed order code and linear solver before N,x,
with order.work+1+solve.work and a common polynomial cap. The working price
is O(N(log N)^alphaZ(loglog N)^2), plus polynomial(log N) and an eventually
absent direct fallback. The positive gap 1/10^10 absorbs the loglog square,
giving O(N(log(N+2))^(1-7474546/10^10)). These inherited transfer mechanisms
and exponent are credited to the pinned sources, not presented as new.

Unpublished AI referee replays were reported. They are not included and are
not offered as evidence. The public finite scalar/root controls corroborate
only their explicit finite statements; the all-size claims rest on the written
arguments and are not a kernel certification. No finite-alphabet
root/precision/recovery theorem, tape routing or caller ABI, selected-bound
upgrade, practical crossover or integer multiplication conclusion follows.
