# Mode transport in the growing Walsh frame

This note gives two explicit monomial adapters for each call of the
full-output promoted-mode word. The adapters put each of its eight modes
in a canonical frame on the completed axes. They use the existing
nine-axis output of that mode. They add no recursive child. The result
includes the mixed data-to-mode and mode-to-data maps; it is not only an
endpoint rank calculation. A controller that restores the contents of
all data and mode families is still required.

## Conventions and source

All binary vectors use the standard dot product. An address map has
columns `A` and acts by `P_A|x> = |Ax>`. Operators act from right to left.
Let

    C_q = ((1+i)I + (1-i)X_q)/2.

On a coordinate space `W`, `F_W` is the product of its coordinate `C`
operators. Thus `F_W` is the compiler's native transform, including its
phase. Write `omega_W` for the sum of the coordinate vectors.

For odd-dimensional `W`, let `G_W` be the normalized Walsh transform on
the even space `omega_W-perp`, with the identity on the characteristic
line. In this note all dimensions are `1 mod 8`. The exact identity is

    C_(omega_W) G_W = Z_W F_W Z_W,
    Z_W|x> = (-1)^(sum_(i<j) x_i x_j)|x>.

The common-line identity and the native rank-eight/rank-nine recipes are
also checked in the residual-syndrome, root, and interface-proof lanes.
This note uses their canonical Walsh frame, then supplies the input and
output adapters needed by the actual promoted-mode circuit.

The base word is `FULL-MODE-PROGRAMS.json.gz`, with decompressed payload
SHA-256

    f271842a741584389e166e700e262f161b0dd570ce8c7a540f2717e90ead5205.

It has 112 old source wires, 112 old target wires, eight arbitrary mode
wires, and 472 arbitrary ordinary helpers. Its logical forward map is

    x' = x,
    y' = y + (I-P)x - Ku,
    u' = -u - 2Rx,
    h' = h,

where `K=R^T/4`, `P=KR`, and `RR^T=56I`. The backward map is

    x' = x - (I+P)y - 8Ku,
    y' = y,
    u' = -u - Ry/4,
    h' = h.

Each mode enters the local identity frame and leaves `F_local`. All 472
ordinary helpers are restored before the output adapter. The exact
704-column replay, scalar frame checks, and native event checks are in
`FULL-MODE-PORT-REVIEW.json` in the interface-proof lane.

## Literal adapters

At stage `s=0,...,8`, put

    n = 8s, m = n+1, N = n+9.

The previous completed space has dimension `m`, and the current one has
dimension `N`. Stage zero uses a one-dimensional previous space and
`G_previous=I`. Let `o` and `w` be their characteristic vectors.

Choose the basis

    h_i = e_i + e_n,  0 <= i < n,
    B = [h_0,...,h_(n-1), o, e_(n+1),...,e_(n+8)].

The first `n` columns span the old even space. Their Gram matrix is
`B_H=I_n+11^T`, which satisfies `B_H^2=I_n`, since `n` is even.
The last nine columns are an orthonormal basis of its perpendicular
complement.

Let `P_E` move the first `n` coordinates to positions `9,...,N-1` and the
last nine coordinates to positions `0,...,8`. Define

    A = P_E B^-1,
    q(z) = sum_(0<=i<j<9) z_i z_j mod 2,
    D_+|z> = i^wt(z_exterior) (-1)^q(z_local)|z>,
    D_-|z> = i^-wt(z_exterior) (-1)^q(z_local)|z>,
    M = D_+ P_A,
    A_in = D_- P_(P_E diag(B_H,I_9) B^-1),
    B_out = P_(A^T) D_+.

In particular, `M` includes the stated phase. It is not only `P_A`.
The receipt lists every address matrix by its columns, and states the
phase and order for each map. Each adapter is an invertible address
permutation followed or preceded by phases from `{1,-1,i,-i}`.

Let `F_exterior` be the native transform on local positions `9,...,N-1`.
Then

    A_in G_previous = F_exterior M,                 (1)
    B_out F_local F_exterior M = C_w G_current.    (2)

These identities include their global phases.

For (1), write the old even-space input in coordinates `t`, the local
nine-coordinate input as `ell`, and the exterior output as `v`. Both
kernels have normalization `2^(-n/2)`. Their phase equality modulo four
is

    2(t dot v) - wt(v) + 2q(ell)
      = wt(t) - wt(t xor v) + 2q(ell).

The Gram factor in `A_in` is needed for this pairing. The native exterior
global phase is one, since `n` is a multiple of eight.

For (2), write `z=Ax` and `z'=A^-T y`. The two characteristic identities

    A w = omega_local,    A^T omega_local = w

give `parity(z_local)=parity(x)` and
`parity(z'_local)=parity(y)`. Also `z dot z'=x dot y`. The native kernel
has phase

    D_+(z) D_+(z') (-i)^(wt(z)+wt(z')) (-1)^(z dot z')
      = (-i)^(parity(x)+parity(y)) (-1)^(x dot y).

Its coefficient is `(1+i)/2^((N+1)/2)`, since `N=1 mod 8`. This is the
kernel of `C_w G_current`, with no omitted scalar phase.

## Alternating types

Use mode types

    T_previous^a = C_o^a G_previous,
    T_current^b = C_w^b G_current.

Set `a=s mod 2` and `b=1-a`. Start with `T_previous^0=I` at stage zero.
For `a=0`, use the adapters just stated. For `a=1`, append the following
monomial map to `B_out`:

    h = w+o,
    L|x> = (-i)^(h dot x) |x + (1+h dot x)w>.

The vector `h` is even, so `h dot w=0`. The common-line identity gives

    L B_out F_local A_in (C_o G_previous) = G_current.

Consequently, with `B_(s,a)=B_out` for `a=0` and `L B_out` for `a=1`,

    B_(s,a) F_local A_in T_previous^a = T_current^(1-a).  (3)

The extra map `L` composes with the output adapter. Each call therefore
still needs only two added monomial maps per mode. The ninth output type
is `C_(omega_73) G_73`.

The one-dimensional factor remains explicit in the mixed access:

    E_s = F_exterior^-1 A_in T_previous^a = M C_o^a.     (4)

Thus the mixed access contains a monomial operator when `a=0`, and a
monomial operator times one `C` line when `a=1`. It does not contain an
unpriced Walsh query on all completed axes. Equation (4) is an identity
used to state the contents. The implementation runs the original local
word between the two monomial adapters; it does not separately run
`C_o`, `G_previous`, or `F_exterior`.

## Binding to the actual mixed ports

Let `D_p` be the actual supplier router for the 112 old ports at this
stage. In a local call of cover class `d`, take the eight mode owners
from that same cover class `d`. Conjugate the within-array adapters above
by `d`. This needs no new orthogonal cover generator and no change to an
old port route.

In these local coordinates, the old target bank and the normalized old
source bank have common background `F_exterior`. Equation (1), or its
typed version (4), puts each adapted mode in the same background with
logical content `E_s u`. Thus every scalar gate of the old 704-register
word remains legal. This statement holds for arbitrary old data, modes,
and ordinary helper inputs.

Strip the stated data frames and the new mode output frame. The exact
forward update is

    x' = x,
    y' = y + (I-D_p^-1 P D_p)x - D_p^-1 K E_s u,
    u' = -u - 2E_s^-1 R D_p x.

The exact backward update is

    x' = x - (I+D_p^-1 P D_p)y - 8D_p^-1 K E_s u,
    y' = y,
    u' = -u - E_s^-1 R D_p y/4.

The first equation uses the actual phase-correct old entry and exit
frames. The mode equation uses (3) to cancel its background. Every
ordinary helper is restored by the base word before its own old endpoint
operation; the new adapters touch only the eight mode families.

The mode map `P_A` is a general invertible binary address map. No claim
is made that the nine-dimensional chart extends to an orthogonal chart
of all 73 axes. Such an extension can fail at the final stage. Within-array
monomial operations remove the need for that extension.

The forward and backward content maps with the same `E_s` need not be
inverse transposes, because `M` has nonreal phases. An explicit rank-zero
mode conjugation repairs this if a controller requires the dual pair.
Put

    ell = A^T omega_exterior,
    Q_s = Z_ell X_o^a.

Here `ell dot o=0`, and direct multiplication gives

    E_s^T E_s = Q_s,    E_s^-T = E_s Q_s.

Conjugate the backward logical mode coordinates by `Q_s` at both ends.
The resulting content map is the inverse transpose of the forward map.
The physical input repair is `X_(ell+a o)`. The physical output repair is
`X_(ell+a w) Z_(a h)`, where `h=w+o`. The independent kernel and Pauli
review in `temporal-reuse/GROWING-MODE-LIFT-REVIEW.json` checks that no
extra scalar phase is needed. Both maps can compose with the existing
adapters. This repair does not replace the obligation to compose the full
changing-stage controller.

## Endpoint and invoice

The bare nine-stage mode product is `C_(omega_73)G_73=Z_73 F_73 Z_73`.
Apply `Z_73` to each new mode family before the first call and after the
last call. If the content controller restores the initial logical mode
value `Z_73 h`, the physical mode output is exactly `F_73 h` for arbitrary
input `h`. The preparation is invertible and does not require a clean
mode.

For 16 replicas with eight modes each, the adapters add 2,304 monomial
maps across all 144 calls, and the boundary chirps add 256 maps. Each map
has explicit binary-linear addresses and phases from `{1,-1,i,-i}`. It
can be applied in place by binary elementary address permutations and
pointwise phases, with one coefficient of temporary storage. Its finite
address and scalar work must be included when the global implementation
is emitted. No extra array, clean state, or recursive child is assumed.

The local paid rank mass remains 5,522. The conditional owner patch from
`HOSTING-PATCH.json` retains all original old-family jobs, adds 128 mode
families, and replaces the 1,152 displaced width-nine helper jobs with
their exact old native operations at the same invocation. The complete
child-profile change is still

    {8:-1152, 9:+1152}.

This increases paid rank by 1,152 and productive output rank by 9,344.
The difference is 512 per replica. This is a conditional invoice. It is
not a supplier certificate or a kappa result: the coupled content
controller, its legal boundary operations, and its finite work remain
open.

## Exact check

`check_walsh_mode_adapters.py` pins the full-mode word, emits all nine
address recipes, verifies all address inverses and characteristic
vectors, and verifies the phase identities by extracting every
coefficient of their explicit quadratic polynomials modulo four. It also
checks the controlled phase in the alternating output correction. The
result is `WALSH-MODE-ADAPTERS.json`.

Run:

```text
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/history-encoding/check_walsh_mode_adapters.py --program work/centre-encoding-campaign-20261014/lanes/history-encoding/FULL-MODE-PROGRAMS.json.gz --out work/centre-encoding-campaign-20261014/lanes/history-encoding/WALSH-MODE-ADAPTERS.json
```

The expected first line is

```text
PASS_EXACT_GROWING_WALSH_MODE_ADAPTERS
```

The checker proves these finite-dimensional operator identities. Their
tensor powers give the same identities for every positive tensor size.
The independent physical-block and phase review in
`temporal-reuse/GROWING-MODE-LIFT-REVIEW.json` passed. It uses separate
exact kernels, checks the full first-call kernel, and includes the mode
duality repair. A second separate review passed in
`interface-proof/WALSH-MODE-REVIEW.json`, including the literal address
columns, global phases, and transpose repair. No global content closure
is claimed by these checks.
