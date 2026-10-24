# Phase cells, Toeplitz convolution, and a smaller boundary inverse

Campaign `20261007T222521Z`: immutable start 2026-10-07 22:25:21 UTC,
deadline 2026-10-08 08:25:21 UTC. This continues the independently reviewed
[reusable banded inverse](downstream-reusable-banded-inverse.md).
The pinned upstream input is `bcd4ebde8692383539f8a48734e5fbf3a18a32c2`.

## Independently reviewed conditional result

The construction below changes the inverse application, preserving its
polynomial norm and linear work precision. It gives local convolution
cost O(t*p^(1+delta)) and boundary cost
O(t*p^(2+delta)/(u*d)), where u=alpha^2. With u=Theta(p^r), the normalized
tensor exponents are epsilon+delta and 1-r+delta. The remaining scaling
condition is epsilon+r<1. A dimension arbitrarily close to one is possible
when the stopped guard is refined with its actual piece count.

The [exact candidate assembly](../runs/20261007T234119Z-downstream-phase-assembly/results/certificate.json)
gives these ratios to the advertised 2^-59, rounded downward:

| h50 physical roles | epsilon=9/10 | Guard-optimized epsilon |
|---|---|---|
| 509194, unchanged graph | `4.559814936498` | `5.066445689177` |
| 494250, aligned pairs | `4.828865749804` | `5.365389474455` |
| 487650, retained controllers | `4.955330622614` | `5.505905239905` |

Every arithmetic candidate strictly exceeds 2^-57. The largest displayed
rational kappa is `1193902884521/(125*10^27)`. The complete phase,
Toeplitz, Schur, precision, fixed-tape and eight-row assembly transfer
passed independent campaign review after the four-ulp weight repair.
The [independent review](review-phase-cell-inverse.md) contains a
self-contained GS displacement proof, error chains, high-magnitude
rounding cases, full Schur composition checks and all eight assembly rows.
Exact arithmetic alone does not certify these analytic interfaces. The original
complete multiplication theorem and unaffected interfaces remain
conditional assumptions; composed finite graphs require their separate
scalar, rational frame, restoration, endpoint, and rank certificates.
The [cutoff-refined assembly](../runs/20261007T234812Z-downstream-phase-assembly-cutoffs/results/certificate.json)
also composes the parent's R486200 graph: its optimized conditional witness is
`9606057843781/10^30`, a ratio greater than `5.537515331296`.

The new structure is not claimed to be novel in the literature. Gaussian
similarity and the Gohberg–Semencul formula are established tools. The
campaign contribution is their phase-cell Schur composition, exact
precomputation/rounding argument, growing-dimension cost, and its explicit
conditional parameter witnesses.

## Exact phase-cell structure

Retain rho=1+theta=t/s, q_j=floor(rho*j+1/2), beta_j=rho*j-q_j,
u=alpha^2, and the exact matrix N=C T D=I+E. The previous report proves

```text
||E||<1-mu, mu=min(u*theta,1)/4>=1/(4p), ||N^-1||<=4p
```

when p>100, theta>1/(4p), and u>=ceil(log2(8p)). Keep its lattice
truncation width w=ceil(sqrt(16p/u))+2 and tail below 2^(-46p).

Partition the increasing physical index list into maximal phase cells on
which q_j-j is constant. If j and l belong to the same cell, and delta=l-j,
then g=q_l-q_j-delta=0. The exact weighted identity from the earlier branch
therefore gives

```text
u*phi(j,l-j)=u*rho*(l-j)^2 + F_j-F_l,
F_j=u*(1/4-beta_j^2)/theta.
```

Thus the cell matrix is diagonally similar to a symmetric Toeplitz matrix:
N_jl=a_j G_jl/a_l, with a_j=exp(-pi*F_j) and
G_jl=exp(-pi*u*rho*(j-l)^2). The added common term 1/4 scales all
similarity weights equally, so each a_j is at most one.

The source prime intervals give
1/(4d)<theta<1/(2d-1). Full cells have floor(1/theta) or ceil(1/theta)
indices; the two end cells have roughly half that length. Every cell has
length at most 4d+1 and at least d-2 for large d. The end cells remain
separate physical cells. Their cross-period interactions will be handled
by the cyclic boundary system, so no sort or undeclared cyclic merge is
needed. When epsilon>(1-r)/2, d/w tends to infinity. Eventually every
cell has more than 4w indices.

The phase generator uses additions and comparisons, with no division at
each index. Write K=t-s. Initialize phase=0 and remainder=s. At index j,
the invariant is remainder=2Kj+s-2s*phase in [0,2s). Thus
phase=q_j-j and beta_j=(remainder-s)/(2s). To advance, add 2K to
remainder; if it is at least 2s, subtract 2s and increment phase.
Since theta<1/2, at most one subtraction is needed. Each record update
takes O(p) bit cost, and its comparison also locates the cell changes.
The known endpoints generate the boundary selection positions. During
setup, the same remainder determines the rational Gaussian arguments.

## A structured rounded matrix

Set P=32768p and eta=2^(-P). The source scaling cutoff below ensures
u*d<=p. Since theta>1/(4d),

```text
0<=F_j<u*d<=p,
2^(-8p)<a_j<=1.
```

The loose lower bound follows from pi<4 and e<4. Apply the corrected
downward exponential routine on the P-grid to obtain a positive value
a_hat_j with absolute error below four eta. It is at least 2^(-8p-1).
Round the Toeplitz coefficient at each distance 1<=delta<=w downward,
with error below four eta using the same corrected real exponential
routine as before. Keep G_hat_0=1 and, critically, put G_hat_delta=0
for distances beyond w.

Within a phase cell define the rational matrix entry exactly as
a_hat_j*G_hat_(j-l)/a_hat_l. Across different cells use the downward
dyadic approximation of the original entry for abs(delta)<=w. Put all
other entries to zero and the diagonal exactly to one. Call this H.
Its entries have O(p)-bit rational numerators and denominators, but they
need not all be dyadic. This choice preserves the exact Toeplitz
similarity needed for local fast inverses.

The similarity ratio error is below 2^(16p+4)*eta, and a rounded ratio
has modulus at most 2^(8p+1). Consequently a uniform row bound is

```text
||H-N|| < p*2^(16p+7)*eta + 2^(-46p).
```

This is less than mu/2, so H has row-diagonal-dominance gap at least
mu/2>=1/(8p), row norm below two, and inverse norm at most 8p. The
gain in structure is not obtained by silently reusing the old exact
downward-row argument; the possible upwards ratio error is explicitly
absorbed by this perturbation bound.

## Four local convolutions compute an interior inverse

In every cell designate its first and last w indices as boundary vertices.
The remaining consecutive interior has a matrix
A_cell=diag(a_hat)*G_cell*diag(a_hat)^(-1), with the same width-w
truncated Toeplitz coefficients. The interior of one cell cannot reach
another cell through an H entry.

For u>=4, the row sum of the symmetric G_cell-I is below 1/8. Hence
G_cell is positive definite, ||G_cell^-1||_infinity<2, and its inverse
is symmetric. Precompute exactly x=G_cell^-1*e_0. Its column l1 norm
is below two, because the matrix is symmetric; also x_0>1/2 since
||G_cell^-1-I||<1/7. Put z=(0,x_(L-1),...,x_1), where L is its size,
and let L(v) be the lower triangular Toeplitz matrix with first column v.
The symmetric Gohberg–Semencul identity is

```text
G_cell^-1 = (L(x)*L(x)^T-L(z)*L(z)^T)/x_0.
```

Each of the four triangular Toeplitz products is a local convolution.
For upper triangular multiplication, reverse the input, apply the lower
convolution, then reverse its retained result. Retain the first L
coordinates of every ordinary convolution. The formula has the stated
orientation; the exact prototype checks every resulting matrix column.

Primary source for the general identity and its implementation:
T.-t. Feng, G. Wu and Y. Wei, *Inexact Shift-and-Invert Arnoldi for Toeplitz
Matrix Exponential*, arXiv:1503.04886v1 (17 March 2015), equation (2.4);
[primary PDF](https://arxiv.org/pdf/1503.04886v1), inspected 2026-10-07.
The original identity is due to I. Gohberg and A. Semencul (1972).
The special norm bounds above are derived for this near-identity matrix,
rather than assumed from a generic numerical-stability claim.

Round x, z and 1/x_0 on the P-grid. Their norms are bounded by constants
plus O(p*eta). Store a_hat exactly, and store its reciprocal to P
fractional bits with O(p) integer guard bits. Scale the input by these
reciprocals, evaluate the four convolutions exactly on dyadics with one
completed-coordinate rounding per convolution, subtract and scale by
the reciprocal of x_0, and multiply by a_hat. All intermediate
magnitudes are bounded by 2^(8p+O(1))*max(1,||input||).

Using at most 4d+1<=5p coefficients per local product, the induced
rounding and factor-error bound can be chosen as

```text
||computed_A_inverse(b)-A_cell^-1 b||
 < 2^(32p)*p^8*eta*max(1,||b||).
```

For example, a rounded Toeplitz factor differs by row norm at most
5p*eta, each exact factor has row norm below two, reciprocal x_0 is
below two, and reciprocal a_hat is below 2^(8p+1). With
R=2^(8p+1) and B=max(1,||b||), the scaled input has norm below 3RB.
The first rounded Toeplitz product has error at most 20pR*eta*B;
the second has error at most 100pR*eta*B. Combining both branches,
rounding the subtraction and x_0 reciprocal, and applying a_hat gives
at most 512pR*eta*B. This is below the displayed allowance. Inputs to later operations
are the completed local inverses, whose exact map norm is at most 8p
by row diagonal dominance. The large similarity weights are internal
proof/accounting factors, not extra global normalization.

Signed dyadic convolution uses a fixed number of nonnegative Kronecker
packings. Each coefficient slot has O(p) bits, including the guard for
at most 5p summed terms. The packed operands have O(Lp) bits. The
published unconditional integer multiplier therefore gives
O(Lp*log(Lp))=O(L*p^(1+delta)) bit cost. Here L is polynomial in p,
so the logarithm is O(log p), not log t. All products and sums are
exact until the stated rounding boundaries.

## The Schur boundary remains small and well conditioned

Order the interior I and boundary B in their inherited physical orders.
H_II is block diagonal across cells, and its blocks are the local
matrices above. Form its exact rational Schur complement

```text
S=H_BB-H_BI*H_II^-1*H_IB.
```

Eliminating any interior vertex preserves the row-diagonal-dominance
gap and never increases the Schur row norm, by the induction already
proved for the reusable banded inverse. Thus S has gap at least mu/2,
row norm below two, and ||S^-1||<=8p. No positive-definite assumption
about H or S is needed.

Each cell contributes two ordered boundary groups of size w. Elimination
can join those two groups, but cannot join them to the interior of
another cell. Existing cross-cell entries join only the last group of
one cell to the first group of the next. Therefore S is circular-banded
with half bandwidth at most 2w in the boundary order. It has
O(s*w/d) vertices, including the two end cells. The wrap correction
connects the end groups exactly as in the previous cyclic solver.

Round S to P-bit dyadics before its LU precomputation. Its diagonal
remains positive and its gap is at least mu/4>=1/(16p). These rounded
online coefficients have O(p) bits. Exact rational S entries and its
construction are confined to setup. Use the previous no-pivot banded
LU and Woodbury border construction on this rounded S, now with the
looser row gap and wrap-factor norm below two. The same residual proof,
with these fixed constant changes, supplies for input b

```text
||computed_S_inverse(b)-S^-1 b||
 < 2^60*p^20*eta*max(1,||b||).
```

The bound includes perturbation from rounding S, as well as factor,
reciprocal and online residual errors. All factors and inverse norms
remain polynomial in p. Its cyclic correction still uses an ordered
row scan of a length-O(w) vector for each boundary row.

For explicit constants, the scalar half bandwidth is 2w<=2p. On the
rounded S with gap 1/(16p), the noncyclic factors satisfy
||U||<2, ||L||<=65p^2, ||L^-1||<32p, and
||U^-1||<=1040p^3. Their rounded/effective factor perturbations are
at most 2p*eta and 3p*eta respectively; the effective reciprocal
diagonal still has error below 8eta. The product perturbation is below
200p^3*eta, and its inverse is bounded by 32p. The same row-residual
argument gives a noncyclic solve error below 2^17*p^5*eta*B.
The wrap rank is at most 4w<=4p, ||V||<2, ||Z||<=16p, and
||K^-1||<=33p. Propagating V, K^-1 and Z table errors gives a full
cyclic solve allowance 2^32*p^7*eta*B. Finally rounding S changes its
inverse by at most 640p^3*eta, since each Schur row has at most
4w+1<=5p coefficients. All these terms are below 2^60*p^20*eta*B.

## Two interior passes and one boundary solve

The complete unnormalized inverse application is

```text
y_I=H_II^-1 b_I,
r_B=b_B-H_BI y_I,
x_B=S^-1 r_B,
x_I=H_II^-1 (b_I-H_IB x_B).
```

Both boundary coupling matrices have O(w^2) entries per cell. Round
these coupling coefficients to the P-grid during setup. Their row
norms remain below two, and the row error is O(p*eta). Dot products
are accumulated exactly then rounded once. The exact intermediate
norms are polynomial: y_I is bounded by 8p, r_B by 17p, and an
intentionally loose boundary-solve bound is O(p^2). The final recovery
right-hand side is O(p^2). Scaling the local and boundary error
interfaces by these norms, propagating the coupling errors, and using
the polynomial inverse bounds gives the common allowance

```text
||computed_x-H^-1 b|| < 2^(64p)*p^64*eta.
```

This has no factor that grows exponentially in the number of cells or
the line length. It is a norm/residual composition over a fixed number
of completed maps. The perturbation from H to the true N contributes
at most 32p^2*(p*2^(16p+7)*eta+2^(-46p)). The P=32768p margin therefore
makes the complete inverse error smaller than 2^(-p-10) for p>100.
All threshold comparisons are exact. The simple inequality log2 p<=p
already bounds the polynomial coefficients far below the linear
precision margin.

An explicit independent composition can use
LA=2^(32p)*p^8*eta and SB=2^60*p^20*eta. The boundary right-hand side
error is at most 3LA; its inverse error is at most
24p*LA+18p*SB. The recovery error is bounded by
1024p^2*LA+512p^2*SB+2048p^4*eta. Each completed map uses its
polynomial inverse norm; the large internal similarity factors do not
multiply across cells or successive complete inverse applications.
Using p<=2^p verifies that this sum is below the displayed
2^(64p)*p^64*eta for every p>100.

The final normalization and disk interface remain those of the reviewed
banded inverse: J_normalized=N^-1/2^j with j=ceil(log2(32p)),
D_normalized=D/2^(2u), and S_normalized=S/2. Divide the completed result
and round toward zero to the p-grid. The scalar identity has factor
2^(2u+j+1), and the tensor factor is gamma=d*(2u+j+1). Existing forward
blocked Gaussian evaluation and the positive diagonal exponential keep
the scalar error below p^2, output in the disk, and fixed tape count.

## The tape cost avoids a long convolution

Split each input line into ordered interior and boundary records by a
forward scan using the nearest-index generator. The cell lengths and
selection positions are generated, not advice. Metadata and counters
have O(p) bits. Local convolutions consume one cell at a time on a fixed
collection of work tapes, reset their heads and clear their temporary
records before proceeding. Rewinds cost O(Lp) per cell and are included
in the convolution bound. Each precomputed generator tape is scanned
and rewound once per required pass. No convolution has length s or t.

The coupling rows are in inherited cell order, so a buffer of O(w)
boundary or near-boundary interior records suffices. Repeated scans and
resets cost O(wp) per coupling row, within the O(w^2*p^(1+delta))
arithmetic per cell. The boundary inverse uses the previous ordered
banded forward/backward scans and cyclic correction; its volume is
O((s*w/d)*w*p). A final merge restores the complete increasing line.
One fixed set of tapes is reused for all cells, axes and lines.

Local generator, similarity, coupling, exact Schur, and cyclic-factor
precomputation is once per tensor axis. Each rational computation and
table operation is polynomial in s and p; exact determinant records
may be long during this setup. Since s=n^o(1), the total setup and
cleanup remain n^o(1). Retained online tables have O(p)-bit records.

The per-line inverse application cost is

```text
O(t*p^(1+delta)*(1+w^2/d)).
```

Tensoring costs O(d*T*p^(1+delta)+T*w^2*p^(1+delta)), while Tp=Theta(n)
and w^2=O(p/u). This gives precisely the two normalized exponents
epsilon+delta and 1-r+delta. It retains the computational model and
uses only the published unconditional short-record multiplier.

## Guard and parameters

Retain the BHP replacement prime proof in the previous report. Every
fixed epsilon<1 gives the same distinct prime intervals and capacity.
The stopped one-piece depth remains at most 9B_guard^2*d^(5-4beta).
For any fixed zeta>0,

```text
piece_count <= m*(1+1/zeta)*d^zeta,
C1=5-4beta+zeta,
C0=32m*B_guard^2*(1+1/zeta)
```

bound the complete arithmetic depth, preprocessing, phases and final
shift. The inequality log d<=d^zeta/zeta supplies the piece count.
This is a changed valid upper bound; it is not a universal lower bound
on possible guard exponents.

For a simple witness, use beta>=999/1000, zeta=1/20, C1=11/10,
C0=256m*B_guard^2, epsilon=9/10, r=1/20 and delta=1/1000. The piece
exponent is at most 1.054<1.1. Gaussian margins are 0.099 and 0.049;
guard margin is 0.01; normalization margin is 0.05. This already
strictly exceeds 2^-57 with the unchanged graph.
This C0 is a separate simple-witness estimate: the depth coefficient is
9*(1+1/zeta)+18=9*21+18=207<256, with B_guard>=1 and m>=1.
The generic coefficient 32*(1+1/zeta) is not substituted for it.

For the optimized witness, use the exact packed/leaf balance root
x=1-beta from the parameter report, take zeta=2^-30, and choose

```text
C1=1+4x+zeta,
epsilon=(1-2^-20)/C1,
r=(1-epsilon)/2,
delta=r/8.
```

The guard gap is exactly 2^-20. Both Gaussian margins, the normalization
gap r, cell/band separation, prime growth, and all retained assembly
constraints are strictly positive rational numbers. Kappa is rounded
down on the 10^-30 rational grid with a strictly positive absorption
gap. The original finite primitive logarithm savings and packed/leaf
root are recomputed with rigorous rational enclosures.

Within this particular guard family, the packed/leaf balance is again
optimal at their intersection: the packed term divided by 1+4x
decreases with x, and the leaf term b_complex*x/(1+4x) increases. The
scoped supremum is b_complex*x_star/(1+4x_star). This is not a ceiling
for sharper guard estimates, other recurrences or other finite graphs.

For gamma<17b^(epsilon+r), require b^(1-epsilon-r)>68; the checker
uses log2 b>=ceil(7/(1-epsilon-r)). For the logarithmic alpha and j
prerequisites, let k=ceil(1/r). The stronger fixed cutoff
log2 b>=16k^2+1 makes b^r exceed log2 b+10. Write g_guard=1-epsilon*C1
and g_cell=epsilon-(1-r)/2. The refined checker also uses

```text
log2 b>=ceil(bit_length(2*ceil(C0))/g_guard),
log2 b>=ceil(9/g_cell).
```

The first ensures b^g_guard>2C0 and hence the complete guard
Delta=ceil(C0*d^C1)<=b+1<=p. For the second, d>=b^epsilon/2,
w<=7p^((1-r)/2)<18b^((1-r)/2), and b^g_cell>=512. Thus d-2>4w,
including both partial endpoint cells. The original retained interfaces
and the BHP prime threshold still have additional eventual cutoffs.
These witnesses are asymptotic, and their large
constants and cutoffs do not imply practical performance.

## Finite evidence and continuation

The exact prototype is
[downstream_phase_inverse.py](../code/downstream_phase_inverse.py).
The [corrected small run](../runs/20261007T233708Z-downstream-phase-inverse-corrected/results/certificate.json)
passed two complete Gaussian cases with u*theta<1. It checks every
Gohberg–Semencul inverse column, exact phase conjugation, Schur gap and
packed bandwidth, rounded cyclic boundary solution, local convolution
packing, and an independent infinite-Gaussian residual enclosure.
Initial/final partial cells and signed real/imaginary inputs are included.
An independent dense check also passed 285 GS identity entries in sizes
one through nine. The expanded [five-case run](../runs/20261007T233832Z-downstream-phase-inverse-full/results/certificate.json)
passed all five cases, including three- and four-cell examples and
nearest-index ties. It used one CPU worker and less than 32 MiB RAM.

The first attempt failed an unnecessarily strict boundary dimension
check. With two phase cells the dimension equals twice the half
bandwidth; the first/last wrap groups are disjoint even at equality,
and the Woodbury formula still applies. The corrected test states this
explicitly. That failure is preserved in
`runs/20261007T233635Z-downstream-phase-inverse-small/`, with the source
hash and failed input. A wider finite tail window was also chosen to
satisfy the deliberately loose rigorous tail allowance.

The work precisions of 256–768 bits are bounded finite prototypes. They
do not simulate a complete tape machine or run the asymptotic P=32768p
interface. The mathematical proof supplies the latter and has passed
independent campaign review. This is not a formal verification of the
complete multiplication algorithm.

The [addition/comparison generator audit](../runs/20261007T234951Z-downstream-phase-generator/results/certificate.json)
passed 523,208 exact nearest-index records and 3,294,582 band edges,
including endpoint lengths, half-integer ties, cross-cell boundary
containment, and every permitted within-cell Schur fill. Its
[source](../code/downstream_phase_generator.py) keeps oracle divisions
outside the generator itself.

The [corrected universal-precision audit](../runs/20261007T235528Z-downstream-phase-precision-corrected/results/certificate.json)
records affine exponent inequalities valid for every integer p>=101.
It bounds the positive error sums, factor perturbations, dominance gap
and final target error using p^k<=2^(kp) only for nonnegative powers.
An [invalid first auxiliary checker](../runs/20261007T235429Z-downstream-phase-precision/report.md)
used that substitution for two negative-power comparisons. It is not
accepted evidence. Its exact source is recoverable from the retained
source-version JSON, and the corrected run uses direct p^3<=p^20 and
p^7<=p^20 comparisons. This repair changes no matrix test or kappa.

```sh
python3 -B research/integer-multiplication-bounds/code/downstream_phase_inverse.py \
  --upstream /path/to/pinned/integer-mult-bounds \
  --output /tmp/downstream-phase-inverse.json
python3 -B research/integer-multiplication-bounds/code/downstream_phase_assembly.py \
  --upstream /path/to/pinned/integer-mult-bounds \
  --roles 509194 494250 487650 \
  --output /tmp/downstream-phase-assembly.json
```

The next proof improvement should target the conservative scalar depth
count or the packed movement recurrence. Once this inverse is reviewed,
Gaussian dimension is close enough to one that those finite/recurrence
terms dominate the supported kappa.
