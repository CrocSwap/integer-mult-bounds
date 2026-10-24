# Combine the last completion with the terminal decoder

This packet replaces 64 final rank-seven target completions and their
64 rank-two terminal calls with 64 rank-nine calls. It applies to the
one-pair controller in dimension 25, with the preferred permutation on
the complementary 64 ports. The total native rank stays at 5,600.
The number of children decreases by 64.

This is an exact contraction of adjacent operations on each target.
It does not save native rank. It does not give a kappa improvement.
The exact full-cost budget remains a separate obligation.

## Pinned inputs

The checker uses the complete matched native word and the literal
permutation64 component. It checks that the latter is the unchanged
event suffix of the former. It also uses the full inverse triple from
[TRIPLE25.md](../matched-stage-access-20261018/TRIPLE25.md), including
its owner maps and full Fourier translations. All hashes are in the
program and receipt.

The controller has five scalar code cuts. After the final forward
call, its last scalar code acts only on the X bank. Each of the 64
target Y fields has no further local read after its last scalar
transfer. Thus its final rank-seven completion can be deferred.

## Local canonical adapter

Let p be the source of the last scalar transfer and let r be its
permutation partner. The source frame at this transfer is the
canonical line frame T_p. It is not the pure line C_(q_p).
Let M_p be the pinned source endpoint adapter. Its exact convention is

```text
T_p = M_p C_(q_p).
```

The rank-seven target completion, followed by the inverse target
endpoint adapter, has operator

```text
R_r = F9 C_(q_r)^-1 T_p^-1
    = F9 C_(q_r)^-1 C_(q_p)^-1 M_p^-1.             (1)
```

The checker reads both endpoint adapters and the actual rank-seven
recipe. It verifies (1) by signed Pauli conjugation and an exact
Gaussian state calculation.

The two labels q_r and q_p are orthogonal unit vectors. Extend them
to an orthonormal root basis

```text
(q_r, q_p, u_1,...,u_7).
```

The difference between the full Fourier phase in this basis and the
standard root basis is an even linear phase. The checker computes its
translation Delta from the complete Z4 phase polynomial. Hence

```text
R_r = X_Delta (product_j C_(u_j)) M_p^-1.          (2)
```

Both providers pass this full phase equation on all 64 targets.

## The exact final product

Write rho for the literal stage-two route of target r. Its current
exit map is X_exit P_rho, where exit is the pinned DATA translation.
The retained raw terminal applies C_(q_r)^2=X_(q_r) to this output.

Let A be the complete inverse-triple owner map from source r to
output p. The exact terminal correction is

```text
-X_delta C_a C_b^-1 P_A,
a=q_p,       b=A q_r.                              (3)
```

The full Fourier translation delta comes from the frozen triple
packet. Equations (2) and (3), in the required order, give

```text
-X_tau C_a C_b (product_j C_(A rho u_j)) P_(A rho) M_p^-1,
tau = delta + A(exit + rho Delta).                 (4)
```

All vector sums are binary. The inverse-line translation from
C_b^-1=X_b C_b cancels the transported old terminal map
A q_r=b. This cancellation is why (4) has two positive lines.
It does not remove either native direction.

For every literal path, the nine directions

```text
a, b, A rho u_1,...,A rho u_7
```

are orthonormal. The two terminal directions are orthogonal to the
transported seven-dimensional completion space. The complete product
therefore has Fourier rank nine.

The program extends these nine directions to an orthonormal basis G
of the 25-dimensional space. It emits two full affine monomial
records, with their quadratic phases, so that (4) is

```text
- L H9 R,
R = P_G^-1 P_(A rho) M_p^-1,
L = X_tau P_G.                                    (5)
```

The right record includes the canonical source adapter. The left
record includes the exact translation. The negative complex sign is
kept separate in the invoice. Each record contains its full binary
matrix, offset, quadratic phase, linear Z4 coefficients, and constant
phase. No endpoint adapter is implicit.

## In-place order and cover assignment

After the last scalar transfer to each of these 64 Y fields, omit
its rank-seven completion, target endpoint adapter, and stage exit
map. Complete the other native work and the final X-only scalar
code. The deferred fields are arbitrary; no zero-state assumption
is used.

Next apply the retained signed bank exchange. On these 64 ports,
omit its Q-squared map, since that map is already in (4). The old
Y values now occupy the first bank and the old X values, with a
negative sign, occupy the second bank. This exchange is valid on
arbitrary arrays. It does not require the deferred Y values to be
in a completed frame.

Apply the 64 recipes (5) to the first bank. A record for output p
reads source port r in the current body chart with owner map
A rho. The port assignment is a permutation and each owner map is
invertible. Thus the complete source assignment is a bijection.
It can be implemented as a field and address permutation before
the fieldwise children. It does not need a second copy of the bank.

The regular cover is the same O(25,2) cover as in the source access
packet. The local word uses complete cover sweeps. The contraction
does not assume that a source and target have the same invocation
body. The map A rho states which source body is read.

## Invoice and verification

The original complete native profile, with the mixed terminal, is

```text
{1:576, 2:208, 5:144, 7:336, 8:192}.
```

The contracted profile is

```text
{1:576, 2:144, 5:144, 7:272, 8:192, 9:64}.
```

Both have rank mass 5,600. The 64 new recipes use 128 monomial
wrappers and the same 64 complex negative signs as the replaced
terminal paths. These signs cost 128 real scalar primitives.
The old signed bank exchange remains. No owned or private field
is added. The change does not alter the scalar response or its
peak row norm.

For equal field volume and exponent sigma in (0,1), the change in
the native child moment is

```text
64 * (9^sigma - 7^sigma - 2^sigma) < 0.
```

This is a cost reduction at fixed rank mass. It does not by itself
make the complete supplier moment less than one. The inherited
full-cover correction, map cost, precision bound, and recursive row
hosting still belong in a complete supplier certificate.

Run with one process:

```text
python3 -I -B work/centre-encoding-campaign-20261014/lanes/bridge-access-20261017/rank9-completion-20261020/check_rank9.py
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/bridge-access-20261017/rank9-completion-20261020/check_rank9.py
```

Both runs must end with `PASS_MATCHED_LAST_COMPLETION_RANK9`. The
program and receipt must agree byte for byte.

For each provider, the checker verifies 64 complete signed Pauli
maps, 64 exact Gaussian state phases, 128 local phase identities,
and 20,864 native phase coefficients. It also checks the complete
source bijection, the literal event suffix, the absence of a later
target read, and 64 incorrect-translation controls. The full signed
Pauli map plus one exact state image proves operator equality on
arbitrary inputs. Tensor products preserve that equality at every
width.

The history lane supplied the native permutation word. The controller
lane supplied the five-cut one-pair identity. The bridge review lane
independently checked the preceding triple terminal. OpenAI Codex
assisted this work.

No PR, push, or publication commit is authorized. Before any future
PR description, read
/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md.
