# Data-only retirement into a partner code

This packet proves an ordered local interface. It changes the selected
output set from `S` to its partner set `T`. It cancels all arbitrary
borrowed inputs from the retired Y bank. Eight values leave in the FULL
frame, and 104 values leave in their hole frames. The retired code is a
unit. No original-data record bank is used.

The proposed forward prefix uses 16 additional rank-one native lines.
This is an operation count, not a complete native invoice. The literal
forward word, inter-stage binding, helper leases, global controller,
and terminal decoder remain separate obligations.

## Pinned local response and notation

Use the response and selected set in
`../bipartite-eight-20261018/BIPARTITE-EIGHT-PROGRAM.json.gz`. Its
decompressed SHA256 is
`0c832994c1d06562a8db0b9b3d940f6f6143c37beed983f874a69f2bf6ecfdee`.

The selected set is `S=[0,7,15,36,42,46,79,89]`. Its partner set is
`T=[20,27,53,57,72,94,105,111]`. The sets are disjoint. Let `U` be the
complement of S, `V` the complement of T, and `R` the complement of
`S union T`. There are 112 ports.

Write `Q_p` for the intrinsic line operator at port p, and `q_p` for its
inverse. A current-entry X field is physically `Q_p h_p`. A current-entry
Y field is physically `d_p`. Remove only the common exterior operator
from these formulas. A completed X field has content `X_p`; a completed
Y field has physical content `q_p Y_p` in that exterior. A selected
completed Y field can instead carry a value in FULL.

All matrix products have their displayed order. A graph entry of `J_t`
includes its actual stage-t port route. The proof does not move a Q
operator across a graph entry. The same-port intrinsic Q is fixed by its
stage route, as checked in the existing access packets.

## The partner prefix

On arbitrary current input `(Qh,d)`, use this order:

1. For p in S, set `Y_p <- Y_p - X_p`.
2. For p in S, apply the positive line `Q_p` to physical `X_p`.
3. For p in T, apply the positive line `Q_p` to physical `Y_p`, then set
   `Y_p <- Y_p + X_p`.
4. Apply `H_t^(T)=J_t[V,V]` to the current Y fields in V.
5. Run the raw forward word with the selected physical exchanges on T.

Steps 2 and 3 use eight positive lines each. Steps 1 and 3 use sixteen
unit ADD operations. Step 4 acts on current-entry Y fields in their
common I view. It is not a future-stage query on X.

Define

```text
z_S = d_S,
z_U = h_U + d_U.
```

Then the completed physical Y output, with the common exterior removed,
is exactly

```text
Y_T = z_T                       (FULL),
Y_V = q_V (J_t z)_V             (hole frames).             (1)
```

To prove (1), consider the input to the raw forward word. On S, its
logical X is `Q_S h_S`, while the Y vector before the ordinary gauge is
`d_S-Q_S h_S`. Their sum is `d_S`. On R, their sum is `h_R+d_R`. On T,
the selected Y input is `Q_T(h_T+d_T)`, so the physical exchange gives
the raw word logical X equal to `z_T`. The ordinary Y output is therefore
`J_t[V,T] z_T + J_t[V,V] z_V`. The final selected exchange returns `z_T`
in FULL. Each cancellation is between adjacent equal operators.

For the complete X output, put

```text
hat_h_S = Q_S h_S,
hat_h_U = h_U,
w_T = z_T,
w_V = hat_h_V.
```

The exact output is

```text
X_V = hat_h_V,
X_T = h_T + q_T (J_t w)_T.                              (2)
```

These identities do not require J or any principal block to be a unit.
The ordinary precode is reversible when `H_t^(T)` is a unit.

## Composition with the diagonal backward interface

Let the preceding backward stage be s. Write its response as

```text
J_s = [[L_s, B_s], [D_s, H_s]]
```

in the S/U split. Its diagonal borrowed interface on original data
`x=(a,u)` and arbitrary borrowed state `y=(b,v)` has

```text
p = A_s (Q_S a,u),
h_S = p_S + q_S b,
h_U = p_U - v,
d_S = Q_S a,
d_U = v,
p_U = H_s^-1 (u-D_s Q_S a).
```

Substitution into (1) gives the data-only vector

```text
z_S = Q_S a,
z_U = H_s^-1 (u-D_s Q_S a).                              (3)
```

Thus every coefficient of every original borrowed field is zero in Y.
The cancellation holds for arbitrary borrowed state. It does not use a
clean record or a known baseline.

Let `K_s` have identity rows on S and the rows of `J_s` on U. Let `R_t`
have identity rows on T and the rows of `J_t` on V. Then

```text
(Q_S a,u) = K_s z,
retired logical row code = R_t z.
```

Both row codes are units if `H_s` and `H_t^(T)` are units. Their
determinants, in the corresponding block orders, are those of these
ordinary principal blocks. The physical row code also includes q on V.
This factor must remain in any terminal decoder.

For the pinned response, extend G by the identity on the separate
64-port block. Then `G^2=I`, `GJ=JG`, and `G(S)=T`. Signed port
relabeling therefore takes the S ordinary principal block to the T
ordinary principal block. The first has a proved dyadic inverse; the
second does as well. This is a statement in a single current chart.
It does not identify the globally routed responses at distinct stages.

## The complete borrowed-source response

The data-free part of (2) is

```text
X_S = b,
X_R = -v_R,
X_T = -v_T + q_T [J_t[T,S] b - J_t[T,R] v_R].            (4)
```

This is a unit triangular source code. Subtract
`q_T J_t[T,V] X_V` from its T component to obtain `(b,-v)`. This
subtraction is only an inverse of the source coefficient. Applied to
the full state, it also changes its data coefficient.

A stronger optional correction uses the actual completed values:

```text
X_T <- X_T - q_T (J_t w)_T,
w_T = completed FULL Y_T,
w_V = completed FULL X_V.                               (5)
```

Then all X output is `(Q_S h_S,h_U)`, and its source part is exactly
`(b,-v)`. Equation (5) needs eight inverse-line graph queries in a direct
FULL implementation, in addition to its scalar query and restore work.
No native cost for (5) is hidden in the 16-line prefix count.

## Verification and remaining work

The checker executes the physical prefix, the T exchanges, and the raw
physical forward matrix. It uses exact rational coefficients and free
ordered operator words. Only adjacent inverse powers of the same Q are
reduced. Every nontrivial graph edge retains its stage, source, and
target as a formal route token. No cross-stage identity or Q commutation
is used.

It checks the full 224-input local map, all 112 borrowed source
coefficients, (4), the source inverse, and (5). A control that omits the
positive Q on selected X fails. It also checks G and J directly from the
pinned native payload. Run:

```text
python3 work/centre-encoding-campaign-20261014/lanes/controller-followthrough-20261017/partner-retirement-20261018/check_partner_retirement.py
python3 -O work/centre-encoding-campaign-20261014/lanes/controller-followthrough-20261017/partner-retirement-20261018/check_partner_retirement.py
```

Both commands must print `PASS_PARTNER_RETIREMENT_ORDERED_CONTENT` and
produce an identical receipt. This proves the ordered local content
identity. It does not prove a native implementation, a complete supplier,
or an improvement in kappa. In particular, decoding (1) into the required
physical `q x` endpoint is open. A 104-field normalization is not by
itself a complete terminal decoder.

This is AI-assisted research. It uses the signed response and principal
gauges from the controller lane, the physical boundary interfaces from
the new-core-transfer lane, and the route and frame checks from the
bridge-access lane.
