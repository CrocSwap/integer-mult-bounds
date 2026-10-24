# Independent review of the raw and weighted controllers

Both controller proofs pass this review. Their formulas give the complete
ordered content endpoint for every positive pair count. No material
algebra error was found. The proof does not move Q through a stage matrix.

This review accepts content identities. It does not accept a physical
inter-call implementation, an idle-owner schedule, a decoder invoice, or
a new complete kappa value. The separate decoder note in this directory
does not enlarge this accepted scope.

## Inputs and independent method

`INPUTS.json` pins the two controller proofs, their checkers and receipts,
the local raw proofs, and the relevant local reviews. The six controller
files are also retained under `reviewed-inputs/`. No source file was
changed. The two main proof pins are:

```text
RAW-ORDINARY-CONTROLLER.md
1b6a6a86cda137b013cf4999c83ecb1f5131330ae642ce6ea61c96b2edc79382
WEIGHTED-RAW-CONTROLLER.md
22a986d9cf1a31be3d58f572d6552e6e6c30dd2ee6f4393893ea5125dd196280
```

The independent checker imports and runs no producer code. It constructs
each local from the physical selected exchange, the clean-core block
shears, and the stated scalar factors. It then constructs the controller
from its individual events. Starting from each output covector, it
propagates coefficients backward through that event tape. Coefficients
are finite sums of ordered words. It cancels only adjacent Q inverses
and adjacent H_j/K_j inverses. It does not use B_j D_j=13I in the
endpoint calculation. This makes the endpoint identity stronger than a
test on commuting scalar stages.

This reverse calculation is compared with a separately entered endpoint
recurrence. It checks both raw forward choices and both weighted
postupper choices, for m=1 through 8. It checks 13,056 endpoint operator
blocks and all active ordinary cuts. Twenty-two controls reject omitted
initial selected or ordinary F0 updates, the wrong final triangle order,
a wrong plus-Y sign, missing selected terms, and an early idle reset.

The checker also uses exact integer matrices with selected dimension two
and ordinary dimension three. Each stage has rectangular B_j,D_j with
B_j D_j=13I. The selected Q does not commute with a cross-stage product.
For three such instances, both raw forward choices, and m=1,2,4, an
integer determinant calculation and elimination over GF(3) check the
claimed determinant and nullity. These finite instances support the
implementation check; the argument below proves the dimension statements
for all m.

## Local derivation

Write the two input banks as `(a,u;b,v)`. The physical selected exchange
has content action `(a,b)->(q b,Q a)`, with q=Q^-1. It is not a logical
swap. The independent raw local reviews verify this distinction with the
actual input and output phase conventions.

For the raw split, the clean core is

```text
J_s = [[0,-B_s],[-D_s,I-D_s B_s]].
```

After the input exchange, clean backward operation, and completed-X
lower shear, the output is

```text
(q b+B_s v, u-v-D_s q b+D_s Q a; Q a,v).
```

Two selected exchanges around the clean forward core give

```text
(h-q B_t k,k; d,v+k-D_t B_t k-D_t q d).
```

The corrected forward input step adds D_t q d to v. It removes only the
last term. These derivations use no Q commutation and no division by 12.

For the weighted split write

```text
J_j = [[R_j,L_j],[C_j,H_j]],   K_j=H_j^-1.
```

The input exchange, backward core, and K_s on ordinary X give

```text
h=q b-R_s Q a-L_s v,
w=K_s u-v-K_s C_s Q a,
d=Q a.
```

Subtracting L_s w from h gives
`h=q b-L_s K_s u-T_s Q a`, where
`T_s=R_s-L_s K_s C_s`. For the forward local, apply H_t to v before
the two exchanges and the core. Its selected X is
`h+q R_t q d+q L_t k`; its ordinary Y is
`H_t v+C_t q d+H_t k`. In particular, the selected self-block term
`q R_t q d` is required. It is absent only when R_t=0.

The raw native maps have separate independent reviews for the old and
new providers. The weighted local factors are stated in the pinned
five-minor packet. This review checks their algebra but does not repeat
their full native word or accept an unreviewed native extension by
inference. The global weighted theorem is conditional on its stated
local maps and on actual access to its idle operations.

## Complete raw endpoint for every m

Use original inputs `(a_i,x_i;b_i^0,y_i)`. Define the ordinary suffix
`z_i=x_i-z_(i+1)`, with z_m=0. The initial full F0 gives
`b_0=b_0^0+a_0` and `v_0=y_0+z_0`; for i>0, b_i=b_i^0.
At pair i let s=2i+1 and t=2i+2, and set

```text
c_i=Q a_i-q b_i,
w_i=z_i-v_i+D_s c_i,
k_i=w_i+z_(i+1),
f_i=B_s v_i+q b_i-q B_t k_i,
e_i=B_t k_i                 (corrected forward),
e_i=B_t k_i+a_i             (raw forward),
r_i=v_i+k_i-D_t e_i.
```

Inductively, the active pair enters B with ordinary X=z_i and Y=v_i.
B gives w_i. The plus-X write gives k_i and the minus-Y write changes
the next Y to y_(i+1)-v_i. F gives f_i and r_i. Subtracting the same
idle X returns the active ordinary X to w_i. The plus-Y write therefore
sets the next incoming value to
`v_(i+1)=y_(i+1)-v_i+r_i`. No operation changes the next idle X.
This proves the induction, including the last pair where z_m=0 and the
next-bank operations are absent.

Before the final triangle, the pair output is
`(f_i,w_i;Q a_i,r_i)`. The descending triangle changes ordinary X to
w_0 for i=0 and w_i+w_(i-1) for i>0. It uses old w_(i-1), not a value
that has already received its own predecessor. Substitution gives

```text
X_U,0=-y_0+D_s0 c_0,
X_U,i=-y_i+D_si c_i+D_t(i-1) e_(i-1),  i>0.
```

All other displayed raw endpoints follow. This proof covers every
positive m and both forward choices. The initial full F0 is essential
to the first line and to the b_0 selected response.

## Complete weighted endpoint for every m

Keep the same suffix and selected initial F0 update. Put
`eta_0=y_0+z_0`. Define

```text
c_i=-K_si C_si Q a_i,
w_i=K_si z_i-eta_i+c_i,
k_i=w_i+K_si z_(i+1),
E_i=H_ti K_si,
r_i=E_i x_i+H_ti c_i+C_ti a_i.
```

The idle preparation changes the next X from z_(i+1) to
K_si z_(i+1). Both the plus-X and minus-X operations use this same
value. Only after the minus-X operation does H_si return the idle bank
to z_(i+1). Thus the next pair has the input required for induction.
Resetting the idle bank before its subtraction gives a different map.

At the forward call,
`eta_i+k_i=K_si x_i+c_i`. Its ordinary output is therefore r_i and
has no original-Y dependence. The next Y is
`eta_(i+1)=y_(i+1)-eta_i+r_i`. Before the final triangle, completed
ordinary X is w_i. After the descending triangle it is

```text
Z_0=-y_0+(K_s0-I)z_0+c_0,
Z_i=-y_i+K_si z_i+K_s(i-1)z_(i-1)
    -r_(i-1)+c_i+c_(i-1),  i>0.
```

Selected Y is Q a_i. Without the postupper, selected X is

```text
f_i=q b_i-R_si Q a_i-L_si eta_i+q R_ti a_i+q L_ti k_i.
```

With the postupper, replace the two terms
`-R_si Q a_i-L_si eta_i` by
`-L_si K_si z_i-T_si Q a_i`. This proves both full endpoints.
The only inverse identities used are Qq=qQ=I and H_jK_j=K_jH_j=I.
Different stage matrices need not commute.

Undo the final ordinary triangle. In the postupper case, the selected
normalization is

```text
Q f_i-L_ti w_i
 = b_i-Q L_si K_si z_i-Q T_si Q a_i
   +R_ti a_i+L_ti K_si z_(i+1).
```

This removes eta_i, as claimed. A positive Q operation on the selected
bank means an operation on each selected field. In the five-minor case
that bank has forty fields. This algebra does not price those operations
or supply the original suffixes in the required views.

## Factor 12, the coefficient ring, and exact nullity

Let d be the selected scalar dimension and n the ordinary scalar
dimension in a finite representation. With original X fixed at zero,
the causal raw controller has diagonal original-Y to completed-X block

```text
M_s = [[q,B_s],[-D_s q,-I]].
```

Eliminate its lower-left block using q. The Schur complement is
`-I+D_s B_s`. The determinant identity for rectangular products gives

```text
det(-I+D_s B_s)=(-1)^n det(I-B_s D_s)
              =(-1)^(n+d) 12^d.
```

If Q is a unit at 3, the 3-adic valuation of det M_s is d. Causal
earlier-pair contributions do not change the diagonal determinants.
Final unit operations do not change the valuation. Thus it is dm for
the restricted global map. For eight array-valued ports with array
dimension N, d=8N, not eight scalar coordinates.

This is a dyadic-ring obstruction. A square dyadic left inverse would
force the determinant to be a unit. It is not a characteristic-zero
singularity: `-I+D_s B_s` has the rational inverse
`-I+D_s B_s/12`. A legal implementation on an odd-denominator grid is
outside the dyadic-linear restriction. Its precision, access, and cost
must be checked separately. This review does not treat an odd denominator
as a general prohibition in the research model.

For the source note's scalar postlower parameter lambda, the lower row
is `[-lambda D_s q,-I+(1-lambda)D_s B_s]`. Its Schur complement is again
`-I+D_s B_s`, because the eliminated term is `-lambda D_s B_s`.
Thus the determinant statement has the stated parameter scope. This
does not extend the following matched-bridge normal form to a changed
controller without a new calculation.

For the matched bridges there is an exact stronger result. Undo the
final X triangle and set
`h_i=f_i+q B_ti w_i`. With original X zero, put
`L_i=I-D_ti B_ti`. Then

```text
v_0=y_0,
v_i=y_i+L_(i-1)w_(i-1).
```

Use the old w values to replace
`(h_i,w_i)` by
`(h_i-B_si L_(i-1)w_(i-1), w_i+L_(i-1)w_(i-1))`.
This is a unit lower triangular output change. It gives a direct sum
of the M_si blocks. Over a field of characteristic 3, B_sD_s=I, so
D_sB_s is an idempotent of rank d. Its 1-eigenspace is exactly im D_s.
Each M_s therefore has nullity d, and the matched controller has
nullity dm. The statement requires the displayed relations and an
invertible Q after reduction. It holds for both raw forward choices.

The determinant alone would not prove this nullity. The matrices
`diag(3,3)` and `[[3,1],[0,3]]` both have determinant 9, but have nullities
two and one over GF(3). The checker includes this control. For the more
general causal class, only the determinant claim is accepted without
an additional normal-form argument.

The resulting dm-dimensional information requirement is not a native
child lower bound. It does not apply to a decoder that also uses ordinary
retired Y, to a changed noncausal controller, or to a changed local map.

## Reproduction and limits

Run from the workspace root:

```text
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/controller-review-20261017/check_review.py
```

Expected output:

```text
PASS_INDEPENDENT_RAW_AND_WEIGHTED_CONTROLLERS
formal cases=32 blocks=13056 controls=22
```

All checks remain active under optimization. The receipt records the
exact source and checker hashes. The run uses one Python process and
no numerical library or floating arithmetic. It does not rerun the
producer checkers or any large native recipe sweep.

The review leaves actual inter-call Q views, idle K/H access, owner
hosting, finite-grid precision, the complete decoder, and the full
recursive invoice open. It adds no complete kappa claim. Research and
review used OpenAI Codex under the user's direction. No human review is
claimed. No PR, commit, push, or publication was made. Before any future
PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
