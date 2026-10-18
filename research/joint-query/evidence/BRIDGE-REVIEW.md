# Exact operators for the phase-aware bridges

The bridge construction in `../cover-algebra/BRIDGES.md` implements the same
logical operator K_t as the centre-free local word. It does not leave a Pauli
conjugation in the logical content. This conclusion requires both listed
translation corrections in the stated order. A bare cover permutation does
not give the result.

`BRIDGE-OPERATOR-REVIEW.json` records an independent check. The checker imports
none of the route, bridge, or Clifford checkers. It reads the actual phase
recipes and hosted template from the
[pinned replay archive](https://github.com/CrocSwap/integer-mult-bounds/blob/bce54fb3f895cbe5cd4c0eb477c3afeed100190f/research/community-frontier1042-audit/selected-replay.tar.gz).
The archive hash is `22c3f4dce4b897a1d423d1388801933e288b6a6b1906cb15e1b16a5eb68db754`.
The receipt also records the hashes of both source members and the centre
matrix. This note is an operator review and a finite scalar invoice. It does
not admit a complete recursive supplier.

## 1. Native conventions

Let T_a be address translation by a. The native line operator is

    C_a = (1+i) I/2 + (1-i) T_a/2.

On the Fourier character indexed by u, its multiplier is i^(a dot u), where
the binary dot product is read as the integer zero or one. Hence a signed
product of line operators has multiplier i^phi(u), with

    phi(u) = sum_j epsilon_j (a_j dot u) modulo 4.

All operators here fix the constant character. There is no undetermined
global phase. A translation T_delta has multiplier (-1)^(delta dot u).

For an orthonormal coordinate space U, let F_U be the product of its
coordinate line operators. At a completed stage s, the boundary gauges are

    X at port q and cover d:  F_(d U_s),
    Y at port q and cover d:  F_(d U_s) C_(d q)^-1.

Here U_s=L+E_1+...+E_s, dim(L)=9, and dim(E_t)=8. The initial gauges are
C_(d q) on X and I on Y. These are the selected controller conventions.
The source check below binds the local entry and exit adapters to them.
It does not independently repeat the entire idle-child schedule proof.

Write B_q for the eight orthonormal chart columns in q-perp. The actual
involution rho_t(q) fixes q, swaps these columns with E_t, and fixes the
other external blocks. Let

    beta_q[i] = (weight(B_q[i])-1)/2 modulo 2.

The review checks the following complete operator identities:

    rho_t(F_(U_s) C_q^-1) = T_(q+lift_t(beta_q)) F_(E_1+...+E_s+E_t), s<t,
    rho_t(F_(U_s)) = T_(B_q beta_q+lift_t(beta_q)) F_(U_s),             s>=t.

The notation rho_t(F) means transport of every axis of F by rho_t. The
other external blocks are fixed, so their identical factors cancel from
each equation. It is enough to check the 17 coordinates in L+E_t.

The checker evaluates the full phase at zero, at every unit vector, and at
every sum of two distinct unit vectors. This determines the complete phase:
the integer expansion of a binary parity modulo four has degree at most two.
It gives 51,744 exact character checks for the two bridge identities and the
source entrance identity. Omission of either correction is rejected for all
112 ports. Reversal of the Y route and correction order is also rejected
for every port. There are 17,248 additional two-factor phase checks.

## 2. Which logical operator the bridge performs

Let T be one of the boundary gauges above, as a block diagonal operator on
all port-cover positions. Define D by

    (D v)_(d,q) = v_(d rho_t(q),q).

This operation only changes the selected cover position. It does not apply
rho_t to the payload address. These are independent input arrays, and their
contents must remain distinct.

Let Z be the block translation whose component at (d,q) is T_(d delta_q),
with delta from section 1. Put A=ZD. The exact phase identities give

    A T = T_common D.

At each fixed cover d, T_common is independent of q. Therefore every scalar
port matrix M commutes with it. In particular,

    (A^-1 M A) T = T D M D.

Since D is an involution and translations are involutions, the physical
sequence is D, then Z, then M, then Z, then D. On logical content its result
is exactly D M D. For M=J or M=J^-1 this is K_t or K_t^-1. The result holds
on Y before stage t and on X at or after stage t. It is valid at all cover
positions and on arbitrary payloads.

This proof also gives the general construction: any port matrix that has a
finite scalar implementation can be applied after alignment. Only its
coefficient and workspace costs change. Inverses and products use the same
logical gauges; each individual bridge returns to the original gauge.

## 3. Binding to the actual local shear

For t>0, the exact `DATA-PHASES.json` entries in owner coordinates are

    entry_X = entry_Y = q + B_q beta_q,
    exit_X  = exit_Y  = B_q beta_q + lift_t(beta_q).

The stage-zero entries are all zero. The independent check verifies all
1,008 port-stage recipes against these formulas. It also checks all 32,256
data owner routes in the hosted template. The source template refers to
this exact phase file and uses physical cover position d rho_t(q).

An owner-coordinate translation a is a translation by d rho_t(q) a in the
local cover sweep at d. Thus the entry correction is physically
T_(d(q+lift_t(beta_q))). The exit vector is rho_t-invariant, so its physical
correction is T_(d(B_q beta_q+lift_t(beta_q))).

After routing and the entry correction, X has native frame C_(d q) times
the common exterior factor, and Y has just that common exterior factor.
The local word thus receives its exact native entry gauges. Its scalar
forward map is L(J), and its backward map is U(-J^T). The exact local review
in `PROOF.md` proves these maps on arbitrary data and helper values. At exit,
both words have their prescribed full local frames. The exit correction
converts these frames to the routed global boundary frames. Routing back
therefore gives

    D L(J) D, or D U(-J^T) D.

Their off-diagonal coefficient is exactly K_t=D J D, or its transpose with
the backward sign. This is the same K_t as section 2. No payload permutation
or leftover translation has been removed by assumption.

## 4. Tensor powers and legal access

Replace every native frame and translation by its lambda-th tensor power.
Every operator equality above remains an equality. The scalar port matrix
acts on the port coordinate and commutes with the tensor address operators.
Its coefficients stay unchanged; they are not raised to power lambda.
Identity spectator factors can be added throughout. This proves the result
for every positive integer lambda and arbitrary spectator contents.

The cover route and translation can also define a view of the data array.
For each fixed port they are bijections. Distinct routed cover blocks thus
do not overlap, and gathering one block before its update is legal. A direct
implementation can use these views for its source reads and target writes;
it need not materialize a full additional data bank. This statement does not
make address computation free. The supplier must price the route, the
repeated tensor translation, stream access, and any physical realization.

One private accumulator suffices for the scalar step below. Its physical
contents are cleared before use, so it can carry the common frame without
a native preparation child. The final clear restores it to zero. No
assumption is made about its initial contents. No other borrowed register
is changed by the scalar step.

## 5. A one-accumulator scalar implementation

Let r_k be row k of R. The exact relation R R^T=56I gives r_j r_k^T=0 for
j different from k. Consequently the following eight row updates commute:

    v <- v - r_k^T (r_k v)/4.

An earlier row update does not change a later row sum. Their product is
J=I-R^T R/4. Replacing 4 by 52 gives J^-1, since

    (I-R^T R/4)(I-R^T R/52)=I.

For each row, clear one private accumulator, gather r_k v, divide the
accumulator by 4, scatter its signed value by -r_k^T, and clear it. For the
inverse, also divide the accumulator by 13 before the scatter. The source
matrix has 448 nonzero entries, all plus or minus one.

| Item per port-cover block | J | J^-1 |
|---|---:|---:|
| Signed ADD macros | 896 | 896 |
| Divide-by-four SCALE macros | 8 | 8 |
| CLEAR macros | 16 | 16 |
| Complex divide-by-13 scans | 0 | 8 |
| Maximum live private arrays | 1 | 1 |
| Added native children | 0 | 0 |

Under the retained primitive bounds, each signed ADD costs at most four
real primitives, each divide-by-four SCALE costs two, and each CLEAR costs
one. Including both real components gives 7,232 real primitives. The inverse
adds 16 real constant-division scans. Both emitted abstract scalar programs
were replayed on all 113 input columns. This includes the arbitrary private
input. The output private row and its input column are zero. Omitting the
first clear or the first inverse division fails the full map check.

The current dyadic compiler does not admit division by 13. Section 3 of
`COEFFICIENTS.md` identifies the repository's common odd-grid construction.
It applies with a fixed factor 13. This is an extension that must be included
in the changed compiler and recursive precision proof.

There is a concrete finite bit circuit for that division. In unsigned binary
long division, the state is a remainder r in {0,...,12}. On input bit b,
emit floor((2r+b)/13) and keep (2r+b) modulo 13. A truth-table circuit for
these 26 cases uses 161 two-input AND/OR or one-input NOT gates per bit.
Two conditional-negation scans handle a signed two's-complement numerator.
Each uses at most nine such gates per bit. Thus a signed ell-bit division
uses at most 179 ell Boolean gates, three linear scans, and at most 32 bits
of extra finite control. Stream reads, writes, and addressing are separate.
The checker verifies all 26 transitions and all 16,384 signed 14-bit inputs.
Nondivisible inputs have a nonzero remainder; they are not silently accepted.

Exactness on the supplier follows from the common-grid invariant, not from
arbitrary integer divisibility. Choose enough root factors of 13 for the
maximum unfinished recursion chain. Completed native children are Gaussian
dyadic and do not consume this reserve. Every division input numerator is
then divisible by 13. Root scaling and final unscaling remain part of the
complete assembly bill. The bridge alone does not prove this recursive
invariant for a proposed whole controller.

## 6. Review result and remaining work

No material phase or logical-operator defect was found in this bridge
construction. Its exact scope is a finite, reusable bridge on an allowed
side of a stage, with the scalar and native endpoints stated above. It does
not by itself cancel the full controller residual. The full compiler must
still lower the new routed accesses and odd division, bind the available
private array, prove all lifetime and recursive precision bounds, and add
the complete finite bill. A favourable rank count alone does not settle
those obligations.

Reproduce from the workspace root:

```sh
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/interface-proof/verify_bridge_operators.py --repo worktrees/k5-centre-sharing --interface work/centre-encoding-campaign-20261014/lanes/circuit-interface/INTERFACE.json --out work/centre-encoding-campaign-20261014/lanes/interface-proof/BRIDGE-OPERATOR-REVIEW.json
```

Expected status: `PASS_EXACT_BRIDGE_OPERATORS_AND_ACTUAL_LOCAL_GAUGE`.
All validation checks remain active under `-O`. The cover-algebra lane
supplied the bridge construction and phase formulas. This lane supplied
the independent operator binding, source replay, and one-accumulator bill.
The phase recipes and common-grid method are retained repository work.
This work used substantial OpenAI Codex assistance and independent agent
review. It is not independent human review.
