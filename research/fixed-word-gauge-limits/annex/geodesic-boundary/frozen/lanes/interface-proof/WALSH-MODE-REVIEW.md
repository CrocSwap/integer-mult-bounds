# Exact mixed-mode lift and transpose repair

The history-encoding lane's literal growing Walsh adapters pass this
independent review. The result supplies a typed mixed interface on the
actual raw mode primitive. It does not close the contents over nine calls.
The temporal-reuse lane derived the same mixed interface and Pauli repair
independently. The common-line and growing-frame inputs come from the
residual-syndrome and coordinating lanes.

The pinned raw program has payload SHA-256
`f271842a741584389e166e700e262f161b0dd570ce8c7a540f2717e90ead5205`.
`FULL-MODE-PORT-REVIEW.json` already checks its complete 704-column map,
all 472 arbitrary ordinary helpers, all native phases, and its scalar bill.
This note uses that checked primitive. The literal adapter receipt is
copied in `WALSH-MODE-ADAPTERS-SOURCE.json`, with SHA-256
`c8ea223ddd139387bbed17ef6dc1175324cec3e4e5431f834e121dc35dcb9bbd`.

## Literal adapter identities

At call s, put `n=8s`, `m=n+1`, and `N=n+9`. The first call has m=1 and
G_1=I. Let A be the address matrix listed as `M_address_columns`. In this
section P_A denotes its basis permutation. Define

    D_+(w)=i^wt(w_exterior) (-1)^q(w_local9),
    D_-(w)=i^-wt(w_exterior) (-1)^q(w_local9),
    q(w_local9)=sum_(i<j<=9) w_i w_j.

The logical input factor is the full monomial

    M_s=D_+ P_A.

Its phase is required. Treating M_s as the address permutation alone is
incorrect. The receipt now states both this phase and its operator order.

Let A_s use the listed input address followed by D_-. Let B_s use D_+
followed by the listed output address `A^T`. Then

    A_s G_m = F_exterior M_s,
    B_s F_local F_exterior M_s = C_omega_N G_N.

The first identity follows by comparing the exact kernels. In the old
even-space basis, G_m has phase `(-1)^(eta^T B t)`, with
`B=I_n+11^T`. The input address converts B t to t. The remaining phase is
the exact identity

    2 eta dot t-wt(t) = wt(eta)-wt(eta+t) mod4.

Both sides have amplitude `2^(-n/2)` because n is a multiple of eight.
The local-nine phase is retained on both sides.

For the second identity, the displayed A satisfies

    A omega_N=omega_9,       A^T omega_9=omega_N.

The two kernel addresses are `A y` and `A^-T x`, so their dot product is
x dot y. The two D_+ phases cancel the exterior weights. Their local
phases change each remaining local weight to its parity. Thus the kernel
is exactly that of `C_omega_N G_N`, including its scalar phase.

For the input type `a=s mod2`, put

    E_s=M_s C_omega_m^a,       T_m^a=C_omega_m^a G_m.

When a=1, compose B_s on the left with the monomial O_s

    O_s |x> = (-i)^(h dot x) |x+(1+h dot x) omega_N>,
    h=omega_N+omega_m.

This is `X_omega_N L_(omega_m,N)^-1`. It gives

    B_(s,a) F_local A_s T_m^a = T_N^(1-a).

This uses one existing rank-nine mode advance. The two added mode
adapters are monomial. They do not change the ordinary helper program.

## The actual mixed interface

Let D_p denote the already checked data routing operators. With
`K=R^T/4`, `P=KR`, and `RR^T=56I`, the forward map is

    x'=x,
    y'=y+(I-D_p^-1 P D_p)x-D_p^-1 K E_s u,
    u'=-u-2 E_s^-1 R D_p x.

The backward map from the same adapters is

    x'=x-(I+D_p^-1 P D_p)y-8 D_p^-1 K E_s u,
    y'=y,
    u'=-u-E_s^-1 R D_p y/4.

The input identity gives the raw primitive exactly its common exterior
frame, with logical mode E_s u. The output identity strips that same E_s
after the raw mode update. This proves the displayed order; E_s must not
move through D_p, R, or K. All modes and ordinary helpers are arbitrary.
The checked raw primitive restores all 472 ordinary helpers before the
new output adapter is applied to the eight modes.

The mode owner remains the same cover class d as the call. Conjugate each
within-array adapter by d. No new orthogonal cover generator is needed
for these adapters. A global emitter must still implement that owner
choice and the stated operations.

## Exact complex transpose repair

The same-E pair is an inverse-adjoint pair. It need not be an inverse
transpose pair. Let `ell=A^T 1_exterior`. For the emitted chart,

    ell=(1<<(8s))-1,       ell dot omega_m=0.

Since the square of D_+ is the exterior sign character,

    M_s^T M_s=Z_ell,
    E_s^T E_s=Z_ell X_omega_m^a=:R_s.

The factors in R_s commute, and `R_s^2=I`. Hence

    E_s^-T=E_s R_s.

Conjugate the backward logical mode coordinate by R_s before and after
the call. The resulting backward map is the complex inverse transpose
of the forward map. The two physical endpoint corrections are exactly

    input:  T_m^a R_s (T_m^a)^-1
            = X_(ell+a omega_m),

    output: T_N^(1-a) R_s (T_N^(1-a))^-1
            = X_(ell+a omega_N) Z_(a h).

There is no omitted scalar phase. In the output formula, ell dot h and
omega_N dot h are zero. This prevents a sign from reordering the Pauli
factors. The corrections need two Pauli maps per backward mode and no
recursive child. Their finite address and sign costs remain payable.

## Endpoint, verification, and limits

The nine frame types end at `T_73^1=D_73 F_73 D_73`. The full G_73 and
C_omega_73 commute with every orthogonal cover class, so this final frame
does not depend on d. Apply D_73 before the first call and after the last.
If the content controller restores its initial logical value D_73 h,
the final arbitrary mode value is exactly F_73 h. This is a conditional
content contract, not a proof that the controller restores that value.

Run:

```sh
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/interface-proof/review_walsh_mode_adapters.py
```

The expected output is `PASS_INDEPENDENT_MIXED_WALSH_MODE_ADAPTERS`.
The checker reads the literal address columns and reconstructs both
Gaussian integer kernels. It checks support conditions and a complete
quadratic phase witness at all nine stages. It detects omission of the
M_s phase. It also checks all nine exact transpose-repair Paulis and their
commutation with the native boundary line. It imports neither the adapter
producer nor its phase expressions. All requirements remain active under
`-O`.

The exact base identities tensor to every positive lambda. This result
resolves the local native access and phase binding for the supplied
mixed family. A controller must still close all old data and mode
contents. The global owner program, all scalar and address costs, and the
complete recursive invoice remain open. No supplier or kappa claim is
made.

Prepared with substantial OpenAI Codex assistance and independent agent
review. No independent human review is claimed.
