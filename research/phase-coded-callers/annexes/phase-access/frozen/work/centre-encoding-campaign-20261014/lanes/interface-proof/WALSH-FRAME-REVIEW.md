# Exact Walsh frames for common centre phases

This note gives an exact native frame theorem. It does not give a closed
controller for the centre contents. The theorem includes all global phases
and applies to arbitrary input arrays.

The residual-syndrome lane proposed a partial Walsh transform on the even
nine-bit hyperplane. The root lane proposed the growing even hyperplane.
This review derives the exact kernels and native child recipes separately.
The input port table is `../coherent-port/COVARIANCE.json`, with SHA-256
`6466d082f376bcbd8f7d953d8a2625f5e31eb164ffa61f430b1cdf6e6ef30b38`.
The old 112 labels and eight completion labels are all odd.

## A fixed common line

Write

    C_q = ((1+i)I+(1-i)X_q)/2.

Choose an odd vector r, let H be the even hyperplane, and use coordinates
`x=z r+h`. Let G apply the normalized real Walsh transform to h and leave
z fixed. For `q=r+v`, with v in H, it gives

    G C_q G^-1 = C_r L_q.

At a Walsh coordinate xi, put `b=xi(v)`. The map L_q multiplies by `i^b`
and changes z to `z+b`. It is a monomial map. The proof reduces to

    C_r iX_r = ((1+i)I-(1-i)X_r)/2.

Thus the identity includes the scalar phase. The L_q commute with C_r.
The same factorization applies to each power of C_q.

For r=11 and the actual selected routes, the full operator

    G C_q P_(rho_t(q) rho_s(q)) G^-1

has binary native rank 17 when `(s,t)=(0,1)` or `(1,2)`, for all 120 labels.
Its rank is one when s=t. This is a statement about the full operator. It
does not prove a lower bound for its restriction to a centre image.

## A growing common frame

Let U_n be the first n coordinates, where `n=9+8s`. Put

    omega_n = (1,...,1) in U_n,       H_n = omega_n-perp.

Every vector in U_n has a unique form `a omega_n+h`, with h in H_n and
`a=parity(x)`. Define the exact real operator

    G_n |a omega_n+h>
      = 2^(-(n-1)/2) sum_(k in H_n) (-1)^(h dot k) |a omega_n+k>.

The form on H_n is nondegenerate, so G_n is a real symmetric involution.
It acts as the identity on coordinates outside U_n. Its binary native
rank is n-1. There is no unspecified scalar phase in this definition.

Let P_g be an orthogonal address map supported in U_n. It fixes omega_n,
since omega_n is the characteristic vector of the dot form. It preserves
H_n and every dot product in the displayed kernel. Hence

    G_n P_g = P_g G_n

as exact operators, including their phases.

For an odd q in U_n, put `v=q+omega_n`. The preceding fixed-line proof now
gives `G_n C_q G_n=C_omega_n L_q`. Here, on a physical coordinate x,

    L_q |x> = i^(x dot v) |x+(x dot v) omega_n>.

This is a monomial map with a linear address map and a quadratic phase
modulo four. It commutes with C_omega_n.

For `m=n-8`, let `A_n=G_n G_m`. If g is an actual transition route in U_n,
then

    G_n C_q^j P_g G_m
      = L_q^j P_g C_omega_n^j A_n.

The order on the right is part of the statement. P_g need not commute with
A_n. Both P_g and L_q commute with C_omega_n. The last common factor has
rank eight for even j and rank nine for odd j. Thus the label-dependent
part is monomial. The common factor still requires a native child.

## Exact rank-eight and rank-nine child recipes

The subspaces H_m and H_n are nested. Their orthogonal difference has the
eight-vector basis

    k_i = omega_m+e_(m+i),       1 <= i <= 8.

Call this space K. Its Gram matrix in that basis is
`B=I_8+11^T`, with `B^2=I`. The decomposition is

    U_n = H_m orthogonal-sum K orthogonal-sum span(omega_n).

The operator A_n is precisely the real Walsh transform on K and the
identity on its complement. This follows from the two exact Walsh kernels;
the transforms on H_m cancel with no scalar phase.

Choose an address chart A whose first eight columns are the k_i, whose
ninth column is omega_n, and whose remaining columns form a basis of H_m.
Let P_B apply B to the first eight chart coordinates. Let S_8 multiply a
chart basis vector by i to the power of its first eight bits' weight.
The native transform is `F_d=product_(i=1)^d C_(e_i)`. Since

    H_8 = S_8 F_8 S_8

with exact scalar phase, the two recipes are

    A_n = P_A P_B S_8 F_8 S_8 P_A^-1,

    C_omega_n A_n = P_A P_B S_8 F_9 S_8 P_A^-1.

The order of these formulas is operator order. The right factor acts first.
Each recipe uses one native child and two composed monomial maps. It acts
on arbitrary input. The same rank-eight construction applies to G_9, with
an even basis of U_9 and complement omega_9.

Even powers of C_omega_n are translations. Its negative odd power differs
from its positive odd power by a translation. Thus these two recipes also
cover all four phase powers, with a further monomial factor when needed.

For a fully typed transition, put `T_n^a=C_omega_n^a G_n`. For arbitrary
integers a, b, and j, the exact ordered identity is

    T_n^a C_q^j P_g (T_m^b)^-1
      = C_omega_n^(a+j-b) L_(q,n)^j P_g
        L_(omega_m,n)^(-b) A_n.

To check the order, first move C_omega_m through G_m. Then use
`G_n C_omega_m^-b G_n=C_omega_n^-b L_(omega_m,n)^-b`.
The common line factors can move through all the displayed monomial maps.
This proves equation (3) in the residual-syndrome lane's
`physical-algebra/GROWING-FRAME.md`. It is an algebraic phase review; the
receipt's rank and kernel counts do not claim a separate full-matrix test
of all typed transitions. For the plain transition j=0, the alternating
types `a_s=1-(s mod 2)` have rank nine at all eight later stages. With the
initial rank-nine frame, this is an exact endpoint frame schedule.

## The exact productive endpoint

Define the diagonal monomial

    D_n |x> = i^(wt(x)-parity(x)) |x>
            = (-1)^(sum_(i<j) x_i x_j) |x>.

For every `n=9+8s`,

    C_omega_n G_n = D_n F_n D_n.

To prove this, write `a=parity(x)` and `b=parity(y)`. The kernel of the
left side is

    (1+i) 2^(-(n+1)/2) i^(2 x dot y-a-b).

The kernel of F_n is

    (1+i) 2^(-(n+1)/2) i^(2 x dot y-wt(x)-wt(y)),

because `n=1 mod 8`. The two diagonal factors give the required kernel.
For a general odd n, an extra scalar `i^((1-n)/2)` is needed; it is one
for the widths used here. In particular, the n=73 endpoint is exactly the
full required native transform with two diagonal adapters. It does not
require a rank-72 decoder.

This statement is conditional on the actual mode carrying that endpoint
frame with the required contents. If its contents are still changed by the
centre controller, the endpoint identity does not restore them.

## Verification and remaining obligations

Run:

```sh
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/interface-proof/review_walsh_frames.py
```

The expected output is `PASS_INDEPENDENT_EXACT_WALSH_FRAMES`. The checker
does not import either proposer script or the Clifford compiler. It uses
the earlier independent selected-route reconstruction. Its checks include:

- All 61,440 common-line coefficients and all 120 routed port labels.
- Every growing transition from width 9 through width 73, with ranks eight
  and nine and the exact kernel-preserving orthogonal route conditions.
- All 65,536 entries of the rank-eight child and all 262,144 entries of the
  rank-nine child, as Gaussian integers with their exact denominators.
- All 262,144 entries of the width-nine endpoint and complete quadratic
  phase witnesses on both kernel coordinates at every larger width.

Every check uses an explicit requirement and remains active under `-O`.
The base operator identities tensor to every positive lambda. Scalar
coefficients and address maps must be applied in the same stated order.

The monomial maps are explicit but are not free. A supplier must price
their phase and address operations, source access, initial frames, active
and idle mode schedules, arbitrary borrowed contents, final restoration,
and all recursive children. This review emits no such controller or owner
program and makes no kappa claim. It does resolve the phase and endpoint
obstacles for the stated growing-frame family.

There is also an address-group condition. The chart from the local
nine-space to `span(omega_m,E_s)` can be a general linear map. An isometry
between those spaces need not extend to an orthogonal map on the ambient
space. The child recipe is valid as written, but it does not replace an
actual cover route or an owner address without a further proof.

Prepared with substantial OpenAI Codex assistance and independent agent
review. No independent human review is claimed.
