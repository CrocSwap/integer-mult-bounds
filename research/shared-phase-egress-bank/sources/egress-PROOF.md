# Literal normalization and single toward-zero egress

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance.
Apache-2.0. Scoped constructive proof with finite corroboration; no independent
human or proof-kernel acceptance is claimed.

## 1. Exact source and theorem

Base: `e54523517d0f03e58352e647c403a5af3e525a57`. The selected record and
application review are frozen in `reference/`. In `05-layers.tex`,
`phase-butterfly-layer` and `simultaneous-layer` specify

\[
H_0^{\otimes D}=b^D\mathcal S_D C^{\otimes D}\mathcal S_D,\qquad b=(1-i)/2,
\]

followed by one componentwise truncation toward zero to the original p grid.
The actual header is

\[
\Gamma(p)\Gamma(d)\Gamma(r)\Gamma(D)\Gamma(P)\Gamma(S)
\Gamma(K)\Gamma(\rho+1)\Gamma(w).
\]

`02-streams.tex` defines `Gamma(v)=0^(bit_length(v)-1) bin(v)` for v>=1.
Selected application section 5 supplies a coupled format, not merely two
independent upper bounds. Write q=Q0 and D_total for its entire operated
dimension. Its remaining-root parameters are p'=p+q, h'=q+1 and
D_root=D_total-q. Thus F=p'+D_root=p+D_total and
W=p'+h'+2D_root+3=p+2D_total+4. Padding the fraction by d-D_total zeroes
enlarges this signed width to W'=p+d+D_total+4<=p+2d+4; sign padding then
gives our fixed F=p+d, H=p+2d+4. The nonrecursive small-root route uses the
same conservative guard in the cited section. The conversion is a supplied,
separately paid O(NH) format pass, not an operation performed by this table.
Here D=D_total is the actual operated dimension in the layer header, while
**d is the global bound**. Their different uses must not be interchanged.

Assume positive p,d,D,w, D<=d, w>=p+2, and five other positive header fields.
DATA contains N>=1 complete Gaussian pairs, real then imaginary, each a
signed H-bit two's-complement integer in MSB order. Their values are
`z_j=2^(-p-d)(a_j+i c_j)`. DATA starts at its supplied head with a blank end
cell. Its writable reserved window extends through `max(2HN,2wN)` cells,
including a blank end cell, so longer outputs have paid capacity. HEADER
begins at its supplied head. Eighteen physical tapes are distinct. Sixteen
private tapes have blank owned guard cells one position before their origins
and blank bodies wherever this program visits. Opaque exterior outside these
windows is preserved. Header validity and the packet's semantic relation to
its r,P,S,K fields are supplied premises: this program does not check N=Mr.

The one fixed table replaces DATA on the **same owner** by the N w-bit pairs
for `Q_p(b^D z_j)`, erases the old tail, restores all heads, preserves HEADER
and every exterior symbol, and erases all private bodies/guards, if all
outputs fit w signed bits. Otherwise it rejects at an output-range check
before any DATA write. DATA is unchanged on numerical range rejection;
head restoration, private cleanup and reuse after rejection are NOT claimed.
Malformed inputs, invalid caller promises and resource-fault recovery are
outside the theorem.

The table has 17,814 instruction locations, eighteen tapes and alphabet
`{blank,0,1,|}`. Only local-symbol branches, one-cell writes, unit moves,
fixed jumps and halt execute. A sink with no admissible branch is rejection.
No decoded parameter, numerical payload, input-sized lookup or host arithmetic
is available at runtime. Python constructs and simulates a fixed graph.

## 2. Header production

LENGTH counts each Gamma prefix's zeroes. After consuming its initial one,
exactly that many binary tail digits are consumed while LENGTH is erased.
Every header move is logged in HTRACE. The fields r,P,S,K,rho+1 are skipped
without unary expansion. For p,d,D,w, the initial one creates unary 1 and
each next bit t replaces v by 2v+t through DOUBLE, erasing the old value
and DOUBLE. This proves the unary value by induction. The preceding binary
prefix values sum to less than the final value, since consecutive values
at least double. Thus decoding costs linear work in the decoded value plus
Gamma length. This is appropriate for these O(p) quantities; it is not a
fast unary decoder for arbitrary huge r or P.

HTRACE restores HEADER exactly without scanning unknown exterior. Unary
comparisons check D<=d and w>=p+2. Copies form H=p+2d+4. Starting SHIFT with
d ones, a scan of D appends a marker on its first, third, fifth, ... symbol.
Its position modulo eight stays in fixed control. Therefore

\[
s=d+\lceil D/2\rceil < H+2.
\]

Erase unary p,d,D. Retain only H,W,SHIFT and the eight-state mode.

## 3. Exact signed numerator

Write D=2m+e, e in {0,1}. The credited identity
`b^D=(-i)^m(1-i)^e/2^(m+e)` gives unrotated rows a,c when D is even and
a+c,c-a when D is odd. Rotation by (-i)^m selects two signed rows with
coefficients alpha,beta in {-1,0,1} and row l1 norm at most two. D modulo
eight selects them at graph construction, without a runtime matrix operation.

Load each MSB component into X or Y while logging every DATA move in DTRACE.
Read X/Y from their LSB ends. Finite transitions implement

\[
t_k=c_k+\alpha x_k+\beta y_k,\quad u_k=t_k\bmod2,
\quad c_{k+1}=\lfloor t_k/2\rfloor.
\]

The carry set {-2,-1,0,1} is closed because -4<=t_k<=3. Induction gives

\[
\alpha\operatorname{low}_k(a)+\beta\operatorname{low}_k(c)
=\sum_{j<k}u_j2^j+2^k c_k.
\]

After H digits, the last input bits are their signs, retained in finite
control. Two additional transitions on these signs produce the exact
H+2-bit signed numerator. Its magnitude is at most 2^H. This covers the
most-negative H-bit input and odd-D sums/differences, without narrowing an
unhalved sum to H bits. A sum of two maximal positive H-bit integers can
therefore overflow H bits without causing a false rejection.

The last numerator bit determines the sign. A negative value is complemented
and incremented from the LSB end with carry in {0,1}; a nonnegative one is
unchanged. The H+2 width exceeds the absolute bound, so the magnitude of the
most-negative source value is obtained without signed-minimum overflow.

## 4. Single projection and necessary-and-sufficient range guard

For each row numerator n, the desired p-grid integer is

\[
\operatorname{trunc}_0(n/2^s),\qquad s=d+m+e.
\]

The d term changes the input p+d grid to p; m+e is the b^D denominator.
SHIFT drops exactly s bits from the **absolute** numerator. No divisibility
or low-zero test is required: nonintegral values are legal for the final
projection. In particular, negative fractions of magnitude below one become
zero, not minus one. There is no intermediate rounding.

Convert the remaining magnitude stream to signed bits: copy for positive n,
complement/increment for negative n. Past the finite magnitude, supply zeroes.
For a zero quotient the negative-path carry stays one, yielding canonical
zero. Write exactly w low signed bits into QBUF. All subsequent finite bits
and the infinite constant tail must equal the last retained bit. This is
exactly the two's-complement representability criterion. It accepts
-2^(w-1) and 2^(w-1)-1 and rejects both adjacent outside endpoints and every
larger overflow. It cannot reject a fitting answer.

Traverse QBUF backward to append MSB output while erasing QBUF. Erase NUM.
Evaluate the other row from unchanged X/Y, then erase X/Y. This preserves
pair order and real/imaginary order for arbitrary complete fields.

## 5. Original-owner commit and retained backing

Only a complete pair boundary can terminate DATA. Initial blank DATA is
rejected. During all arithmetic DATA is read-only and advances exactly 2HN
cells. OUTPUT receives exactly 2wN bits. Every range failure occurs before
a DATA write, so numerical rejection preserves the entire public payload,
although private contents and heads can be dirty.

After all components pass, DTRACE restores DATA and erases itself. Rewind
OUTPUT and copy the whole staged result to DATA, erasing OUTPUT as it is
consumed. Log each DATA move in the now-reused DTRACE. For shorter output,
erase remaining old DATA bits up to its original blank end; for longer
output use the reserved blank capacity. Restore DATA via DTRACE. Rewind
OUTPUT over its erased body and erase all parameters and private markers.
Thus every successful call restores all eighteen heads and private contents.

This is a paid destructive installation on the same owner, not a free owner
swap. All staging, rewinds, copies and erasures execute. Old backing is not
freed by erasure. If K0 is entry private history, the bound below adds new
possible extents to K0. A reused bank must have a blank guard and body over
the needed window; checking only its origin cannot establish that premise.

## 6. Complete instruction and historical-space bounds

Let E be the nine-Gamma header length. The following loose bounds count every
instruction, including reads, jumps, markers, copies, movement and returns.
Constants concern this table; no old source tariff is treated as tape steps.

| Part | Sufficient instruction count |
| --- | --- |
| Header parsing/return, unary decoding/comparisons, parameter construction/retirement | 512(E+p+d+D+w+H+1) |
| One pair's loads, two signed rows, projection, range scan, staging and buffer cleanup | 256(H+w+1) |
| Complete source/output rewinds, owner commit, tail cleanup and final retirement | 64N(H+w+1)+128(H+w+1) |

For a direct check, one component load costs at most 15H+8 instructions.
A row costs at most 21H+30 before absolute conversion; conversion costs at
most 7H+19. Dropping SHIFT costs at most 8s+6. Signed output, range scan,
MSB staging and NUM cleanup cost at most 13H+16w+42. Clearing both X/Y
costs at most 14H+10. These give the pair bound for H>=7,w>=3. A unary
binary-prefix doubling step v->2v+t costs at most 47v+38 instructions.
The sum of previous v is less than the final value and the number of tail
steps is at most that value. Skipped Gamma digits and their trace returns
have a constant instruction charge per symbol. These observations yield
the stated metadata bound by direct loop induction.

Since H=p+2d+4, the complete bound is

\[
T\le 65536\bigl(E+p+d+D+w+N(H+w+1)+1\bigr).
\]

A numerical rejection executes a prefix bounded by this expression. The
finite precompilation F of the fixed 17,814-location table is separate and
independent of all input parameters. A conventional simultaneous multitape
transition table expands local reads over the other seventeen tapes' four
symbols, a fixed finite expansion. This uses no unit-cost input-sized
instruction lookup.

OUTPUT visits at most 2wN+2 cells. DTRACE visits at most
2N max(H,w)+2: its later commit trace can be larger than its source trace.
X/Y visit H+2 cells each, NUM at most H+4 and QBUF at most w+2. Header
trace/length and unary setup occupy a fixed linear sum in E,H,w. Hence
private historical backing is at most

\[
K_0+4N(H+w)+16(H+w+E+1).
\]

The leading four covers simultaneous output staging and the wider reused
commit trace when w>H. Merely charging DTRACE's original 2HN length would
be incorrect. Public DATA installation capacity and HEADER are separate
existing caller extents. This bound includes erased private cells and all
markers, rather than counting only live nonblank contents.

For the selected family, d=O(p^epsilon), epsilon<1, D<=d, E=O(p),
p+2<=w=O(p), H=O(p), N=Mr. Therefore complete time and added historical
backing are O(Np)=O(V), V=2Mrw, including all returns and installation.
No numerical exchange rate is assigned to unrelated native/movement costs.

## 7. Join to the supplied final phase sweep

For real t, truncation toward zero satisfies trunc_0(-t)=-trunc_0(t).
Therefore componentwise Q_p commutes with every signed permutation of
real/imaginary components, including every multiplication by i^k. Pointwise,

\[
Q_p(b^D\mathcal S_D z)=\mathcal S_D Q_p(b^D z).
\]

The existing final S sweep can consequently act on the new w-bit return.
The egress needs no address or phase oracle. Initial S, recursive C and
final S remain supplied and separately charged. Their correct composition
returns Q_p(H0^tensor D z) by the already proved source identity.

For source-admitted disk inputs, H0^tensor D has absolute row sums one, so
its exact result lies in the complex unit disk. S preserves this disk.
Thus b^D C^tensor D S z also lies in the disk before the final S. Projection
can only decrease component magnitudes; each output p-grid integer has
magnitude at most 2^p and fits w>=p+2. Hence every intended admitted C output
passes the new numerical range guard. The strict error below sqrt(2)2^(-p)
and disk preservation are retained source consequences, not new analytic
error theorems.

## 8. Novelty, exclusions and next obligation

PR2287 already gives the normalized layer identity and linear scan recipe.
Tekalign's PR3127 already gives encoded one-pass b^D normalization in a
structured physical-tape program, with exact same-grid division, source
preservation and protected output. That proof explicitly retains root
truncation and finite-state lowering. This package does not claim to invent
normalization, finite carries, binary shifts or toward-zero rounding.

The new contribution is one fixed literal program consuming the actual
nine-Gamma header and selected conservative common grid, combining
normalization with the single required projection and committing to the
original owner, with a full instruction/history proof. It accepts
nondivisible intermediate numerators that PR3127's different exact-on-the-
same-grid interface correctly rejects.

No new kappa. None of the five global assumptions is wholly discharged.
The program does not construct C inputs, execute C, lower the S sweeps,
establish compiler/stock/row contracts, validate packet cardinality from
r,P,S,K, or implement integer recovery. The next useful join is an actual
completed C consumer supplying this MSB p+d-grid packet and unchanged
original header, then the final S sweep at width w. A different three-bit-
coded or LSB internal interface needs its own priced conversion.
