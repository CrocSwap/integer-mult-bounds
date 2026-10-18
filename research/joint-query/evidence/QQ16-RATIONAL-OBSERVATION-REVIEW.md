# Rational inversion does not close the fixed QQ16 observation set

The selected-output witness passes independent review. It rules out the
proposed selected solve from all selected endpoints, all completed-X
descendants and all five F-query histories. The statement holds over the
rational numbers. It does not rule out a paid old-Y query, a changed local
map or a different controller.

This review reads the frozen `QQ16-CONSERVED-CONTROLLER.md` and
`QQ16-SELECTED-WITNESS.md` in the encoded-controller lane. The receipt
records their exact hashes. The reviewer checker imports no producer code.
It reads the actual query matrix and the serialized native route columns.

## The actual nonzero input

Keep the producer's A, T and U96 sets. Let B_s be the stage-s query on U.
The exact column Grams give B_s B_s*=48I. On fields constant in every
payload coordinate, each retained payload translation is the identity.
The cover values are still arbitrary. This subspace is not the
cover-invariant subspace. The actual action is the regular right cover
action, as in the reviewed map M_(g,delta).

The reviewer reads the doubled geometry only to recover the original
73-dimensional route columns. It checks the diagonal doubling, each
original route's orthogonality and inverse, and all 96 products
rho_2(p) rho_1(p) for p in U. Those products are distinct. Therefore the
identity coefficient of B2 B1* B1 B2* is

    sum_p (r_p r_p^T)^2 = 4 sum_p r_p r_p^T = 192I.

For each centre coordinate e_k at the identity cover element, put

    h_k = (48I-B1* B1) B2* e_k.

Then B1 h_k=0 and the identity coefficient of B2 h_k is 2112 e_k.
These are eight independent missing query directions. The construction
has integer coefficients. It is valid at every positive tensor size by
using fields constant in all payload blocks. No approximation or omitted
complex phase is used. The exact endpoint phases are handled by the
inherited logical frame convention.

## Ordered first two calls

Write h for any one of these inputs. Set all other pairs to zero and set

    X_U=h, Y_U=0,
    X_A=-P_0,A B0 h-P_2,A B2 h, Y_A=-X_A,
    X_T=P_0,T ell_0,A P_2,A B2 h, Y_T=-X_T.

The selected sums are zero. In f0, the B0 h terms cancel. The remaining
terms are -ell_0,A P_2,A B2 h and its positive copy from X_T. Thus f0=0.
The two-sided selected inverse identities give, after F0,

    X_U=Y_U=h,
    X_A=P_2,A B2 h, Y_A=-P_2,A B2 h,
    X_T=Y_T=0.

At B1, q2=B2 h+ell_2,A Y_A=0. The future code E2 replaces the A field
by P_2,A q2=0. Its other selected field is zero, so its query b1 is
B1 h=0. The driver a1 is also zero. Substitution in each frozen B output
formula leaves only Y_0,U=h. No operator factors were commuted in this
calculation.

The checker then replays every remaining ordinary event from that exact
state. The first plus bridge places -h in Y1. F2 has zero X source and
leaves it unchanged. The minus bridge cancels it before B3. All later
active sources are zero. Every later selected state is zero. The final
terminal leaves h only in named X0, which has the old-Y native type.
Every completed-X descendant and every F query is zero. Removing the
first minus bridge makes the same check fail at B3.

The initial X_T is nonzero because P_0,T ell_0,A P_2,A is a unit between
the two selected coordinate spaces. The zero input has the same allowed
observations but a different required selected output. Thus rational
coefficients, including division by 3 or 13, cannot reconstruct this
input from those observations. Later homogeneous selected-only maps
cannot change the witness: they keep their zero input at zero. An
ordinary-to-selected read is a different interface and is outside this
result.

## Reproduction and scope

Run from the workspace root:

```text
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/interface-proof/rational-decoder/check_qq16_missing_observation.py
PASS_INDEPENDENT_QQ16_RATIONAL_OBSERVATION_WITNESS
96 distinct actual routes; B2*h identity coefficient 2112; all five F queries zero
```

The first-two-call proof is an ordered symbolic proof. The executable
checks its actual nonzero source, the retained tail schedule and the
mutation control. It does not emit a complete native QQ16 word. Its scope
is this fixed observation set; it is not a general native lower bound or
a kappa result.
