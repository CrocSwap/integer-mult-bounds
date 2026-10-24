# A growing Walsh representation for odd source phases

This note states an exact frame construction. It does not state a decoded
supplier or a kappa improvement. The centre values must still enter and leave
the new mode representation through legal operations.

Let U_s have dimension m_s=9+8s, for s=0,...,8. Let omega_s be the sum of its
coordinate vectors. The vector omega_s has odd weight. Put

    H_s = omega_s-perp inside U_s,
    P_s = I_U_s + omega_s omega_s^T over F_2.

The subspace H_s is nondegenerate. Every vector has a unique form
`a omega_s+h`, with `a in F_2` and `h in H_s`. Define G_s by

    (G_s f)(a omega_s+h)
      = 2^(-(m_s-1)/2) sum_(k in H_s) (-1)^(h dot k) f(a omega_s+k).

It acts as the identity on unused coordinates. Its kernel fixes its global
phase. It satisfies G_s^2=I. Its binary symplectic action is

    (x,z) -> (x+P_s(x+z), z+P_s(x+z)).

Every orthogonal route supported in U_s fixes omega_s. It preserves H_s and
the dot product. Thus it commutes with G_s exactly, including the phase.
This statement applies to the old supplier's routes within completed U_s.

## One common line for every odd phase

Use the source convention

    C_p = ((1+i)/2) I + ((1-i)/2) X_p.

For odd p in U_s, put v=p+omega_s and b=v dot x. Define the monomial L_p by

    (L_p f)(x) = i^b f(x+b omega_s).

The value b is unchanged by adding omega_s. Thus L_p commutes with C_omega_s.
For b=0 and b=1, direct comparison of the two Gaussian coefficients gives

    G_s C_p G_s = C_omega_s L_p.

There is no omitted scalar phase. Tensor products give the identity for
every positive tensor size. The operator C_p is not replaced by a scalar;
the common C_omega_s factor is still a native operation.

## Growth across one fresh block

The subspaces H_(s-1) and H_s are nested. Their orthogonal difference is

    V_s = {parity(z) omega_(s-1)+z : z in E_s},

where E_s is the new eight-dimensional coordinate block. Thus
`Delta_s=G_s G_(s-1)` is a Walsh transform of native rank eight. It acts in
the nine-dimensional space `W_s=span(omega_(s-1), E_s)`.

Let g be an orthogonal route supported in U_s. For integer phase types a,b
and an integer j, the exact identity is

    T_s^a C_p^j g (T_(s-1)^b)^-1
      = C_omega_s^(a+j-b) L_p^j g L_omega_(s-1)^(-b) Delta_s,

where `T_s^a=C_omega_s^a G_s`. All L operators in this formula use U_s.
This follows by conjugating the old common line through G_s and by using
the exact route commutation above. The monomial factors commute with the
new common line. Therefore the native rank is eight when `a+j-b` is even,
and nine when it is odd.

The root check uses the old 112 port labels and all eight fresh stages.
It checks the binary operators directly. All 896 routed odd-phase cases
have rank eight when the input and output type parities differ. They have
rank nine when those parities agree. These are exact rank claims. This
root check does not by itself establish the full phases.

## Explicit full-transform adapters

On an odd coordinate space of dimension n congruent to 1 modulo 8, set

    D_n f(x) = (-1)^(sum_(i<j) x_i x_j) f(x).

The independent interface review proves the exact kernel identity

    C_omega_n G_n = D_n F_n D_n.

It checks the complete nine-dimensional kernel and proves the formula for
all n=9+8s. The same formula on W_s gives

    C_omega_s Delta_s = D_W_s F_W_s D_W_s.

Thus the rank-nine growth operator has two explicit monomial adapters.
At the final stage, T_8^1 has native rank 73 and is equivalent to F_73 by
the displayed adapters. This is an arbitrary-input endpoint identity.

An alternating sequence of types 1,0,1,...,1 uses one rank-nine transition
per stage and ends at T_8^1. Nine calls have total rank 81 and productive
endpoint rank 73 per mode. These figures describe the mode-frame schedule
only. They do not include source access, old-owner replacement or a content
controller.

## Exact limits

The representation cannot be used as a free final-stage centre encoder.
For example, direct extraction from a full data frame has coefficient
`T_s^a C_p^-1 F_U_s^-1`. Its native rank is m_s-1 for even a and m_s for
odd a. The source circuit must supply the needed coupling while the frame
grows, or pay for it explicitly.

The local isometry from the old nine-dimensional block to W_s need not
extend to the ambient orthogonal cover. At s=8 it cannot: the local
characteristic vector would map to the global characteristic vector.
General linear within-family address maps can lower the rank-nine child,
but this does not prove that its scalar couplings to other families are
legal. The history and temporal lanes are checking those couplings.

The native phase orbit for one local chart has 32 candidate centre modes.
This note does not prove that this same state represents all nine distinct
charts, that arbitrary initial modes are restored, or that a final decoder
has zero native cost. Those are construction obligations.

## Evidence

* `check_growing_walsh.py` and `GROWING-WALSH.json` give the root binary check.
* `../lanes/interface-proof/WALSH-FRAME-REVIEW.md` gives the independent full
  phase proof and exact child recipes.
* `../lanes/residual-syndrome/physical-algebra/` contains the phase-orbit and
  common-line work that led to this construction.

The source interface is pinned to commit
`bce54fb3f895cbe5cd4c0eb477c3afeed100190f`. Its JSON SHA256 is
`5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3`.
This research used substantial OpenAI Codex assistance.
