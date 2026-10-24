# Exact rational centre operations in the selected arithmetic model

The current scalar emitter does not admit division by 3 or 13. The retained
fixed-tape model does admit these operations on a common exact grid. This
note gives two local implementations and states the complete representation
cost. It does not give a decoded Fourier supplier.

The first implementation applies the actual 112-port matrix

\[
J^{-1}=I-R^TR/52,
\qquad RR^T=56I_8.
\]

It uses one existing private array. Its local cost is 7,232 inherited real
scalar primitives and 16 real division scans. It adds no native child when
its operands already have one common frame. Its maximum additional
13-denominator height is **one at every prefix**. The second implementation
makes the selected-sum Smith repair invertible with division by 3. It still
needs eight native line copies into the selected Y hole frames.

## Sources and scope

`SOURCE-PINS.json` records the source commit and exact file hashes. The
source commit is `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`. The scalar
admission rule in `hpe_audit_and_transport.py` accepts dyadic ADD coefficients
and signed binary SCALE coefficients. `hpe_emit_local.py` gives their finite
primitive invoice. No change to those files is made here.

The retained `notes/stopped-product-complex.tex`, section "One exact
odd-denominator grid", already implements division by 21. It requires that
all completed recursive children are exactly Gaussian dyadic. The new
common-grid argument below is an application of that method. It is not a
claim to introduce odd grids. The new finite statements are the actual
J-inverse prefix bound, its literal scalar word, and the Smith inverse with
its representation and native-access obligations.

The underlying machine model is in
`upstream/build/sections/02-streams.tex`. It has a fixed alphabet and a fixed
number of tapes. The array kernels and exact guard are in
`upstream/build/sections/05-layers.tex`. The selected finite invoice is the
member `candidate/strict/global/audit/PREFIX-AND-INVOICE.json` of archive
`f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6`.
Its member SHA-256 is
`212cf4ee3b16081bf66f300fa18b4070d25c17210c21c78c2967892c91870d12`.

All scalar coefficients act once on each array value. They are not raised
to the tensor multiplicity. A scalar operation commutes with one common
native frame on all its operands. It does not commute through unequal
frames merely because its coefficient is rational.

## The one-accumulator inverse

Write the rows of R as r_0 through r_7. For each i, perform

\[
c\gets0;\quad c\gets r_i x;\quad c\gets c/4;\quad
c\gets c/13;\quad x\gets x-r_i^T c;\quad c\gets0.
\]

The C0 array is private and can be cleared. This is not a dirty-accumulator
construction. Every unrelated data or helper array is unchanged. C0 ends
at zero. Its initial value can be arbitrary because the first operation
clears that allocated private array.

For i unequal to j, r_i r_j^T=0. Thus distinct rank-one updates have zero
cross product. Their product is exactly I minus R^TR/52. Replacing the
13-division by the identity gives J. Since (R^TR)^2=56R^TR, both products
JJ^{-1} and J^{-1}J are I.

At the beginning of row i, the complete query r_i x equals its query on
the original module input. Prior row updates cancel from that query. In
particular, the complete query before each 13-division has no new odd
factor. A partial query can have one factor of 13 from the rows already
updated, but it is never divided before the query is complete. After the
division, the accumulator has at most one factor. Subtraction into x adds
no second factor. This proves the one-level bound for every prefix.

There are 896 unit-coefficient complex ADDs, eight complex quarter scales,
16 complex CLEARs and eight complex divisions by 13. The old emitter's
invoice is 7,232 real primitives, with the 16 real divisions separate.
The exact symbolic replay checks all 113 input columns. It obtains maximum
row 1-norm 56 for the inverse and 143 for the forward word. Both words use
at most two new binary denominator bits. These are scalar-word bounds;
address maps and their coefficient-work prefixes are separate.

At a legal common-frame cut, the scalar operation has no native rank.
For a routed J_t, use the previously reviewed exact phase alignment,
apply this word, then undo the alignment. A conservative count is four
monomial applications per port: 448 applications. This count keeps the
permutation and phase passes separate. The maps must be charged by the
73-axis monomial compiler. Their existence does not give access at a Y
endpoint outside the proved future-Y cone.

## A fixed-divisor scan

Fix p=3 or p=13. Use the inherited signed w-bit two's-complement
numerator, including its sign bit. No sign/magnitude conversion is used.
The grid proof below guarantees exact divisibility when division is called.

Move to the least significant bit, then overwrite the bits from least to
most significant. Keep a carry c in {0,...,p-1}, initially zero. For input
bit b, write

\[
a=(b-c)\bmod2,\qquad c'=(c+pa-b)/2.
\]

The parity choice makes c' an integer. If a=0, parity and c>=0 give
0<=c-b. If a=1, parity gives c<=p-2+b. These inequalities show
0<=c'<p in both cases. Summing the per-bit equality gives

\[
pQ_{\rm unsigned}=N_{\rm unsigned}+2^w c_{\rm final}.
\]

Let s_N and s_Q be the input and output sign bits. The signed result is
exact if and only if

\[
c_{\rm final}=p s_Q-s_N.
\]

On valid divisions this is zero for nonnegative values and p-1 for negative
values. The other sign combinations cannot pass. This invariant proves
exact signed division at every width, and detects a nonmultiple. Division
cannot overflow when its input fits the signed record.

The scan overwrites each input cell after it is read. It needs no second
numerical array. The carry and sign flags are finite control. A move to
the low end and a return computation scan, including delimiters, use at
most 4(w+1) arithmetic-head steps per real record. This is a record-kernel
bound. The retained descriptor and record-counter work is a separate O(V)
stream cost; its source does not give it the explicit coefficient four.
The scan is not identified with one old scalar primitive.

Multiplication by p uses the same record format. From the low end, write
b'=(pb+c) mod2 and set c'=floor((pb+c)/2). Again 0<=c'<p. Its final signed
condition is c_final=p s_N-s_output. The preallocated guard makes this
condition hold. The same arithmetic-head bound applies. No numerical
format is changed at either root conversion.

## One predetermined grid, including all borrowed state

Let L_3 and L_13 bound the respective additional odd-denominator heights
of every prefix of one finite parent word, after each completed child is
replaced by its exact Gaussian-dyadic operator. Let D bound the maximum
number of recursive edges on a live call chain. Set

\[
K_3=L_3(D+1),\qquad K_{13}=L_{13}(D+1),\qquad
S=3^{K_3}13^{K_{13}}.
\]

At the outer entrance, convert **every physical coefficient stream** to
one common grid 2^{-P}/S. Multiply its padded integer numerators by S.
This includes untouched data, arbitrary borrowed helpers, allocated private
arrays and coefficient work. The latter arrays contain zero when the
inherited interface requires zero. The conversion does not assume that
borrowed helper values are zero or divisible by an odd integer.

There is no per-field denominator tag. There is no rescaling when one
module uses a division. There is no encoding conversion at a recursive
entry or return. Every record keeps the same grid and width throughout the
outer operation. Unchanged fields retain the multiplied numerators while
other fields are divided.

The proof is induction on the live call chain. A completed child is the
same Gaussian-dyadic linear operator on all its input columns, including
arbitrary helpers. It cannot add an odd denominator. This matrix identity
also holds on rational inputs; it is not limited to dyadic numeric samples.
Only prefixes of unfinished calls can add odd factors. Their total heights
are at most K_3 and K_13. Therefore every stored value is on the common
grid, and every local exact division has an integer numerator. Binary
denominators are covered separately by the retained P guard.

The hypotheses are necessary. A proposed child which returns an uncancelled
J^{-1} has positive odd height. It cannot use this stack-depth proof without
a new bound on all such completed returns. A dyadic encoded map has zero
odd height and does meet this denominator condition. It can still fail the
required Fourier endpoint or helper-restoration contract. Denominator
preservation and semantic correctness are separate obligations.
Also, arbitrary integers on the finest grid are not admissible root inputs.
For example, numerator one cannot be divided by 13. Root inputs are the
arbitrary Gaussian-dyadic values of the inherited interface, converted by
S. The test of a nonmultiple must fail.

At an outer endpoint proved to be the required Gaussian-dyadic operator,
every numerator is divisible by S. Apply K_3 divisions by 3 and K_13
divisions by 13 to every physical output stream. This restores the old
encoding exactly. It restores each borrowed payload through its stipulated
complete owner operation, including its original native endpoint. No odd
scale remains on an untouched or restored helper. A dyadic encoded endpoint can also be unscaled arithmetically. That
operation does not establish its required Fourier or helper semantics.

Let N be the total number of real records over **all** physical streams,
and let w_g include the odd-grid bits. The root preparation and final
unscaling require at most

\[
8N(K_3+K_{13})(w_g+1)
\]

arithmetic-head steps for these scans. The bound counts both conversions.
The retained descriptor and counter cost adds O(N(K_3+K_{13})(w_g+1));
no explicit coefficient for that existing stream layer is asserted.
The added width is at most

\[
\lceil K_3\log_2 3+K_{13}\log_2 13\rceil
\le 2K_3+4K_{13}.
\]

For the selected 73-axis recurrence, every child has at most 48e/73 axes.
Since 2*48^2<73^2, two recursive levels at least halve e. Thus
D<=2 ceil(log_2(d+1)) is a safe bound. The added width is O(log d), and the
root conversion is O(V log d) when the original record width is Theta(p)
and d=floor(b_in^epsilon), p=6b_in. It adds no productive role, borrowed
array family or recursive native child. Fixed finite control and the
existing scan work tapes suffice. The outer log factor is absorbed by the
same strict time slack used in the retained odd-grid proof.

This prices the representation layer. It does not price an unspecified
controller, a missing decoder, new native children, or a new owner schedule.
The local division scans must still be counted in that controller's finite
node work.

## The selected-sum Smith repair

Use the actual selected set A=[0,7,20,27,36,46,57,111]. Put U equal to its
104-port complement, and B_t=R_A^{-1}R_U in the routed stage-t chart. The
actual R_A obeys R_A R_A^T=4I. Each graph row has 52 coefficients, all
plus or minus 1/2. Different stage graphs need not commute.

At the reviewed cut after F8, write selected X as k, selected Y as b,
ordinary X as f, and g=(B_7-B_8)f. The proposed sum-preserving repair is

\[
(k,b)\longmapsto (g-12k,\ b+13k-g).
\]

Its matrix on (g,k,b), with g fixed, is

\[
\begin{pmatrix}1&0&0\\1&-12&0\\-1&13&1\end{pmatrix}.
\]

It preserves k+b. Its inverse uses

\[
k=(g-k')/12,\qquad b=b'-13k+g.
\]

The only new odd prime is 3. Division by 13 is not required here. The map
is an automorphism over Z[1/2,1/3]. Its determinant on the selected pair is
-12 in each of the eight components, so it is not a dyadic automorphism.

A literal row interface for the forward map forms c=g_i-13k_i, adds c to
X_i, applies C_{p_i}^{-1} to private C0, subtracts the transformed c from
Y_i, then clears C0. For the inverse, form c=g_i-13k'_i and first divide
it by 4 and 3; then apply the same two target updates. This gives
c=k_i-k'_i. Both directions preserve the sum for arbitrary selected inputs.

At this cut, the complete X prefix is F_73 and the selected Y prefix is
F_73 C_{p_i}^{-1}, before the later retained terminal translation. The
past graphs B_7 and B_8 can be read from the completed X frame with the
reviewed rank-zero phases. The private copy uses the inherited exact
C_{p_i}^{-1} recipe. It must be inserted after the residual adapters and
before the terminal changes these endpoint types. Tensoring that recipe
proves the copy at every lambda. No equality between a canonical subspace
label and the full endpoint operator is used.

Both directions therefore need eight rank-one recursive children and
16 monomial child wrappers. A conservative route implementation applies
and undoes one complete rank-zero monomial for each graph read, each
selected-X read and each target update. This gives 1,712 additional map
applications. It uses 832 graph ADDs,
eight coefficient-13 ADDs, 16 unit ADDs and 16 CLEARs. The forward scalar
subtotal is 8,624 real primitives. The inverse adds eight quarter scales
and 16 real divisions by 3: 8,656 old real primitives plus those scans.
These counts keep all graph maps and native children separate. They do not
claim an optimized route or a complete parent invoice.

The inverse has at most one new factor of 3 at every row prefix. Each row
reads only f and its own selected X field; earlier rows do not change
those inputs. One existing C0 suffices. Unrelated helper arrays are not
touched, and the private field ends at zero. The native child's arbitrary
helper-restoration contract remains a premise.

This makes the paired repair legal in the rational exact format. It does
not save the eight Y-hole transfers. The reviewed 32-query endpoint
nonexposure witness is valid over Q as well as over the dyadic ring:
all selected and completed-X observations can be zero while the queries
vary. A rational scalar function of those zero observations cannot recover
the missing queries. A proposed use of the formulas
q_i=-12r_i-B_{2i}x_{i-1} must supply access to q_i; it cannot assume it.

## Approximation does not supply the exact interface for free

For a dyadic c, let T_c=I-cKR. Then

\[
T_cJ=I+(13c-1)KR.
\]

No dyadic c equals 1/13. Thus replacing the division by a finite dyadic
approximation leaves a nonzero operator on the centre image. On arbitrary
borrowed contents it fails exact restoration. More precision can reduce
this error, but it does not prove the exact completed-child identity used
by the current owner and guard arguments. A separate rounding theorem
could change that contract; none is needed for the exact grid above, and
none is claimed here.

## Verification and remaining work

Run the checker with -I -O -B. It checks both J inverse orders, all 113
formal input columns, every rational prefix denominator, both Smith inverse
orders, the selected-sum identity, the actual graph coefficients, all
finite-state transitions for divisions by 3 and 13, 65,540 signed integer division and multiplication
examples, and nonmultiple/missing-division controls. The transition proof,
not the finite integer examples, covers all widths.

The local scalar words and scan invariants pass. The full common-grid proof
and the native Smith insertion still need independent review. The selected
finite guards have space for additional fixed scans, but any closed new
supplier must bind the actual number of rational modules, its value-growth
prefix, its complete owner/native schedule, and its Gaussian-dyadic outer
endpoint before it can use the final unscaling or claim a kappa result.
