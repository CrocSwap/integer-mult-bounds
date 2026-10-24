# Exact ordered interfaces and complete endpoint costs

This proof uses left actions on column contents. A product `AB` means
that `B` acts first. An inverse is used only next to its own operator.
Different stage operators need not commute.

The source contracts, all-size row compiler, and native recipe phases
are explicit premises where stated below. None is inferred from a
small scalar matrix or from a successful finite replay.

## 1. Raw and weighted normal forms

The full all-pair proofs are retained in the
[independent controller review](frozen/work/centre-encoding-campaign-20261014/lanes/controller-review-20261017/REVIEW.md).
Its [decoder proof](frozen/work/centre-encoding-campaign-20261014/lanes/controller-review-20261017/DECODER-REDUCTION.md)
gives the complete inverse formulas. Both proofs cover every positive
pair count. They state the selected and ordinary field types separately.

Here is the mechanism needed to interpret those results. Write each
input pair as `(a,u;b,v)`, with `a,b` selected and `u,v` ordinary.
The physical exchange acts as `(a,b)->(Q^-1 b,Qa)`. For a weighted
local response

```text
J_s = [[R_s,L_s],[C_s,H_s]],       K_s=H_s^-1,
```

the backward core and ordinary `K_s` factor give

```text
h=Q^-1 b-R_s Q a-L_s v,
w=K_s u-v-K_s C_s Q a,
d=Qa.
```

A selected update `h-=L_s w` gives

```text
h=Q^-1 b-L_s K_s u-(R_s-L_s K_s C_s)Qa.
```

This is a substitution in the displayed order. It does not move `Q`
through a stage matrix. Preparing the ordinary forward input by `H_t`
and applying its two physical exchanges gives ordinary retirement

```text
r_i = H_ti H_si^-1 (x_i-C_si Q a_i)+C_ti a_i.
```

Thus the exact ordered ordinary inverse is

```text
x_i = H_si H_ti^-1 (r_i-C_ti a_i)+C_si Q a_i.
```

The suffix recurrence and the descending final triangle in the full
review prove all remaining selected and ordinary endpoints. The full
decoder proof then recovers both original banks. The inverse can read
retired ordinary Y. It is not a native implementation of that read.

For the raw model, fix original X at zero. After the stated unit
triangular output changes, the original-Y map is a direct sum of

```text
M_s = [[Q^-1,B_s],[-D_s Q^-1,-I]],      B_s D_s=13I_d.
```

Eliminate its lower-left block. The Schur complement is `-I+D_s B_s`.
The rectangular determinant identity gives

```text
det(-I+D_s B_s)=(-1)^(n+d) 12^d.
```

With `Q` a unit at 3, each diagonal block has determinant valuation
`d`, and the causal `m`-pair map has valuation `dm`. Over characteristic
3, `B_sD_s=I`; hence `D_sB_s` is an idempotent of rank `d`. Each block
has nullity `d`, and the stated matched-bridge normal form has nullity
`dm`. The general causal determinant claim alone does not imply that
nullity. The explicit normal form is required.

This is an obstruction to a square dyadic inverse from the restricted
completed-X observation. It is not a characteristic-zero singularity,
a native-child lower bound, or a restriction on a decoder that also
reads retired Y. An odd-denominator grid has a separate cost question.

## 2. Five scalar codes for arbitrary unit responses

Assume the following three native local maps and the required in-place
scalar codes are available at their stated common-frame cuts:

```text
F0(x,y)=(x,y+E0x),
B1(x,y)=(x-G1y,y),
F2(x,y)=(x,y+E2x),
```

where `E0,G1,E2` are units. Execute, in chronological order,

```text
F0; X<-E0X; Y<-G1^-1Y; B1;
X<-G1^-1X; Y<-E2Y; F2; X<-G1X.
```

After the first two operations the state is `(E0x,y+E0x)`.
After the first Y code and B1 it is `(-y,G1^-1(y+E0x))`.
The next two codes give
`(-G1^-1y,E2G1^-1(y+E0x))`. The last native call cancels
the original-Y part of Y, and the last X code gives

```text
(-y,Tx),                     T=E2 G1^-1 E0.
```

No transpose, involution, or cross-stage equality is needed. The exact
content closure condition is `T=I`. A native transpose pair is covered
by `G1=E1^T`, provided its inverse scalar code is supplied.

At the physical boundary let `W=diag(Q,I)`, let `q=Q^-1`, and let the
preterminal frame be `F diag(I,q)`. The retained signed exchange is

```text
A=[[0,Q^2],[-I,0]].
```

Direct multiplication gives

```text
A diag(I,q) [[0,-I],[T,0]] W^-1 = diag(Q T Q^-1,I).
```

Thus the first-bank decoder is `Q T^-1 Q^-1`. Its chronological
operations are `Q^-1,E2^-1,G1,E0^-1,Q`. The order is part of the
claim. Equal local coefficient matrices do not establish equal routed
operators. The proof and its scalar circuit example are retained in
[GENERAL-UNITS.md](frozen/work/centre-encoding-campaign-20261014/lanes/encoded-controller/one-pair-general-units-20261018/GENERAL-UNITS.md).

The matched native instance has `G1=E1^-1`, so `T=E2E1E0`. Its five
codes use current Y entrance cuts and current or past completed X cuts.
The actual D25 route and phase check admits all five occurrences. The
original 2,668-primitive code and the separately reviewed 2,396-primitive
code implement the same local matrix. Those prices exclude view costs.

## 3. Complete-state physical monomial compiler

Let `G_j` be one operation of an admitted physical program. Include
every productive, arbitrary helper, and owned field in the state.
Assume a replacement `W_j=H_jG_j`, where `H_j` is an admitted physical
monomial and preserves the owned-zero subspace. Set `C_0=I`. Execute

```text
C_j W_j C_j^-1,                C_(j+1)=C_j H_j.
```

If the current state is `C_jz`, the new state is
`C_jH_jG_jz=C_(j+1)G_jz`. Induction proves the entire program.
Applying `C_final^-1` gives the original raw endpoint. The order
`C_jH_j` is necessary. Every later use of each field, including its
use as a helper, must use the same coordinate change.

This statement preserves a native child rank only when the composed
field, cover, and payload maps remain in the admitted map grammar.
Scalar work, map descriptors, stock, owner hosting, and precision
still need an invoice. A general permutation of payload columns or
an exchange of live and owned roles is not admitted by this theorem.

For reciprocal logical shears, `D(E)=diag(I,E)` gives
`F_E D(E)=D(E)F_I` and `B_(E^-1)D(E)=D(E)B_I`. A physical use requires
both `Phi_in D(E) Phi_in^-1` and `Phi_out D(E) Phi_out^-1` to be
admitted monomials. Logical monomiality of `E` is insufficient.

The exact line-flag result explains the failure in the pinned transfer.
For odd binary vectors `a,b`, write `P_a=aa^T`, `P_b=bb^T`, and let
`G` be invertible. If `b^TGa=0`, the upper-right symplectic block of
`F_n C_b^-1 K_G C_a^-1` is

```text
(I+P_b) G^-T (I+P_a),
```

of rank `n-2`. The first projection has image `a^perp`; its image under
`G^-T` contains `b`, so the last projection removes one more dimension.
After multiplication by `F_n^-1`, that block is

```text
P_b G(I+P_a)+(I+P_b)G^-T P_a.
```

Under the same orthogonality condition its two summands have independent
nonzero image lines, so its rank is two. The general zero-rank condition
is `G^Tb=a`. The actual 112 transfers for each provider have ranks
seven and two, respectively. The retained proof also states the exact
scope of the finite canonical-prefix screen. It does not exclude other
stabilizer choices or a changed multicall construction. See
[PHYSICAL-MONOMIAL-CODES.md](frozen/work/centre-encoding-campaign-20261014/lanes/encoded-controller/physical-monomial-compiler-20261018/PHYSICAL-MONOMIAL-CODES.md).

## 4. Retained helper completion

The helper packet keeps each event on live roles 224 through 631 in
the frozen independent skeleton. It also keeps all residual wrappers,
91 private allocations and returns, 16 owned clears, and phase markers.
It removes every data event. No retained event reads a data role or
couples two helpers.

For helper `h`, each child changes frame by `T_new T_old^-1`; each
signed warp changes it by `T_new K^epsilon T_old^-1`. The path is
therefore `T_f W_h T_i^-1`. Every ordered warp word `W_h` cancels by
adjacent inverse pairs. The exact map is `T_f T_i^-1`, with the
original phase and residual wrappers. A proper exit is not changed
to FULL. Arbitrary helper contents are allowed.

Let a new data word act only on the 224 data roles and satisfy the
same physical data entrance and exit types. Give each private or
owned use a checked lifetime. Run the helper completion, return its
private stock, then run the data word. Their live operators act on
disjoint factors, so their product has both required contracts.

The helper profile is `{1:1609,2:512,3:172,4:33}`: 2,326 children
and mass 3,281. Its private-zero peak remains 91. The stated scalar
and map inventory must be added to the data invoice. This composition
does not prove a global owner schedule. Full details are in
[HELPER-COMPLETION.md](frozen/work/centre-encoding-campaign-20261014/lanes/encoded-controller/retained-helper-completion-20261018/HELPER-COMPLETION.md).

## 5. Actual D25 admission and paid terminal

The matched native payload uses only roles 0 through 223 in both
providers and directions. Every other slot has no event and keeps its
frame. Thus the data word is an exact direct summand for arbitrary
values in those slots. Each data field has total native rank eight.
The local profile is `{1:160,2:48,5:48,7:112,8:64}`, with mass 1,792.
Its physical types are `X_p:C_qp->F9` and `Y_p:I->F9 C_qp^-1`.
The source endpoint adapters are part of those types.

Use independent fields `(side,port,h)` with `h` in `G=O(25,2)`.
At a stage body `d`, the owner is `h=d rho_(s,p)`. Right multiplication
by the checked route is a bijection. Distinct side-port families are
disjoint. A complete cover sweep therefore partitions the productive
stock. The next sweep begins after the previous one ends.

The route check covers all 336 records, 672 entry identities, 672 exit
identities, 336 future-Y views, and 672 past-X views. Its Z4 phase
polynomials keep the full scalar phase. The regular cover has order
`2^144 product_(j=1..12)(2^(2j)-1)`, and the productive row count is
`224|G|`. The row split and LIFO arguments in the pinned primary source
apply to arbitrary roles of this finite count. The complete asymptotic
theorem from that source also requires a strict native moment inequality;
the present construction fails that requirement.

For the separated terminal, apply 112 inverse intrinsic lines, the
three stage inverse codes, then 112 positive intrinsic lines. If `q`
is nonzero, choose an invertible binary chart with first column `q`.
Conjugation of the first-coordinate line implements `C_q`, and
`C_q^-1=X_qC_q` supplies the exact inverse phase. This gives 224
rank-one children with no new field.

The mixed terminal uses the actual invariant sets of 48 dense ports
and 64 permutation ports. On the dense set, the separated construction
uses 96 rank-one children and three restricted scalar codes. On each
permutation path, the exact kernel is

```text
-X_(delta+b) P_G H2 P_G^-1 P_A.
```

The two leading columns of the checked orthogonal chart are its distinct
orthogonal line vectors `a,b`. Expanding the two line kernels checks
all four Gaussian rational coefficients and translation vectors.
These 64 paths form a field-and-cover bijection and use 64 rank-two
children. The sign and the inverse-line translation are required.

Both terminals add mass 224 to the three-call mass 5,376. For every
positive `b` and every paid child rank `r<25`,

```text
r^(1-b) > r*25^(-b).
```

Summing either complete profile gives

```text
sum_r n_r r^(1-b) > 5600*25^(-b) = 224*25^(1-b).
```

The cover factor multiplies both sides. Hence both specified completed
words fail every positive native moment. Scalar and map costs cannot
reverse that failure. This is not a lower bound for every decoder.

The complete source proof and independent review are retained in
[ONE-PAIR-ADMISSION.md](frozen/work/centre-encoding-campaign-20261014/lanes/history-encoding/one-pair-admission-20261018/ONE-PAIR-ADMISSION.md)
and [TERMINAL-HOSTING-REVIEW.md](frozen/work/centre-encoding-campaign-20261014/lanes/bridge-review-20261017/matched-stage-review-20261018/TERMINAL-HOSTING-REVIEW.md).
Arbitrary-size grouping, remainder handling, depth bounds, finite
coefficient width, map prices, and exact integer recovery remain
inherited or open obligations. No complete kappa improvement follows.
