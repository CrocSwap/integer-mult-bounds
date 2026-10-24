# Matched bridges for changing return projections

The projection-return controller permits an arbitrary plus-Y coefficient.
The final X triangle must use the same coefficient. This removes the
right-absorption condition from the earlier controller. It also identifies
the coefficient choices that preserve each original Y query.

This note extends `encoded-controller/PROJECTION-RETIREMENT.md` and its
independent review in `interface-proof/projection-retirement-review`. The
source files are unchanged. `CHECKS.json` records their SHA-256 pins.

## Ordered controller

Let there be `m>=1` pairs in a common module. Let `A_i`, `G_i`, and `C` be
units. Let `P_i`, `W_i`, `T_i`, and `V` be linear maps. Put `U_i=I-P_i`.
The maps `P_i` need not be projections for the endpoint identity below.

Use the local maps

```
B_i(x,y) = (U_i A_i x-y, y+P_i A_i x),
F_i(x,y) = (x, G_i(x+y)).
```

Their inverses are

```
B_i^-1(w,v) = (A_i^-1(w+v), U_i v-P_i w),
F_i^-1(w,v) = (w,G_i^-1 v-w).
```

Form `z_i=sum_(j>=i) (-1)^(j-i) x_j`, with `z_m=0`. Thus
`x_i=z_i+z_(i+1)`. First change Y0 to `C y0+V z0`. At each pair, run B_i.
If there is a next pair, do the following operations in order:

1. Change next X from `z_(i+1)` to `A_i z_(i+1)`.
2. Add next X to active X.
3. Subtract `W_i` times active Y from next Y.
4. Run F_i on the active pair.
5. Subtract next X from active X.
6. Add `T_i` times active Y to next Y.
7. Change next X back by `A_i^-1`.

At the last pair, only B and F are needed. In descending pair order apply
`X_i += W_(i-1) X_(i-1)`. Then apply `C^-1` to X0.

Set `E_i=G_i A_i`. The endpoint is

```
Y_i = E_i x_i,
X_i = -y_i + (H x)_i,

(H x)_0 = C^-1(U_0 A_0-V) z_0,
(H x)_i = U_i A_i z_i + W_(i-1) A_(i-1) z_(i-1)
          - T_(i-1) E_(i-1) x_(i-1),   i>0.             (1)
```

After the signed terminal, the map is `[[E,0],[-H,I]]`. Its inverse is
`[[E^-1,0],[H E^-1,I]]`. These are ordered operator identities.

### Proof

Let eta_i be the active Y input to B_i. Its two outputs are

```
w_i = U_i A_i z_i-eta_i,
v_i = eta_i+P_i A_i z_i.
```

Their sum is `A_i z_i`. The temporary next-X addition therefore gives
`r_i=G_i A_i(z_i+z_(i+1))=E_i x_i` after F. The subtraction restores w_i.
The next input is

```
eta_(i+1) = y_(i+1)-W_i eta_i-W_i P_i A_i z_i+T_i r_i.
```

The descending X triangle adds `W_i w_i` before w_i is changed. Its two
terms with eta_i cancel. Its two terms with A_i z_i add to
`W_i(P_i+U_i) A_i z_i=W_i A_i z_i`. This proves (1), including every
original Y input. The first pair follows from its stated initial code.
The proof uses neither idempotence nor commutation of different maps.

## Exact query-preservation criterion

Now assume `P_i^2=P_i`. For each `i>0`,

```
P_i(Hx)_i = P_i W_(i-1) A_(i-1) z_(i-1)
            -P_i T_(i-1) E_(i-1)(z_(i-1)+z_i).        (2)
```

The two suffix variables `z_(i-1)` and `z_i` are independent. Both A and E
are units. Thus (2) vanishes for every input if and only if

```
P_i W_(i-1)=0,       P_i T_(i-1)=0.                   (3)
```

Equivalently, `W_(i-1)=U_i Z_(i-1)` and
`T_(i-1)=U_i Z'_(i-1)` for some linear maps Z and Z'. No relation between
P_i and P_(i-1) is needed. In particular, both choices

```
W_i=U_(i+1), T_i=0,
W_i=U_(i+1), T_i=U_(i+1)
```

preserve the original query: `P_i X_i=-P_i y_i` for `i>0`. The same property
at pair zero requires its explicit first response to vanish under P0. It
does not follow from the later-pair argument.

The old choice `W_i=U_i` forces right absorption to remove its preceding
history term. It is one member of a larger family. The proof above does not
invalidate the earlier theorem within that fixed coefficient family.

## Actual signed kernel

Use the selected and ordinary split. In the actual construction,

```
Pi = [[I,0],[0,0]],
S_s = [[-I,-B_s],[-D_s,I-D_s B_s]],
A_s = S_s^-1 = [[12I,-B_s],[-D_s,I]],
B_s D_s = 13I,
P_s = [[I,B_s],[0,0]],    U_s = [[0,-B_s],[0,I]].
```

Then `P_s A_s=-Pi` and `U_s A_s=A_s+Pi`. The local return is

```
((A_s+Pi)x-y, y-Pi x).
```

It uses the actual original selected input in the returned Y value. Its
literal native implementation and arbitrary-helper proof are separate.

For pair i put `s_i=2i+1`, `t_i=2i+2`, and
`E_i=S_(t_i) A_(s_i)`. Choose `W_i=T_i=U_(s_(i+1))`.
For `i>0`, write `r_(i-1)=E_(i-1) x_(i-1)` and `a_j=(x_j)_A`. Its ordinary
response is

```
(H x)_(i,U) = (D_(s_(i-1))-D_(s_i)) (z_i)_A
              -D_(t_(i-1)) (r_(i-1))_A.              (4)
```

Its selected response is `-B_(s_i)(Hx)_(i,U)`. To check (4), use

```
(E_i x)_U = x_U-D_(s_i) x_A+D_(t_i)(E_i x)_A.
```

This follows by subtracting `S_(s_i) A_(s_i) x=x` from
`S_(t_i) A_(s_i) x=E_i x`. Substitute it in (1) and use
`z_(i-1)+z_i=x_(i-1)`. No D graph commutes through another graph.

The choice `T_i=0` preserves the query but leaves an additional dense
ordinary input term. Thus query preservation alone does not establish a
cheap endpoint decoder. Formula (4) still needs original selected X suffixes.
The preserved original Y query is a baseline value, not a clean X record.

## Native and claim scope

The future-graph access proof is in `bridge-access-20261017`. It treats both
Y bridge signs with coefficient U at the next odd stage, and the same
coefficient in the final completed-X triangle. Its receipt is a separate
dependency. The endpoint proof here does not replace its owner, phase, or
literal map checks. Changed selected FULL retirements must satisfy their
own local and later-helper contracts.

The present result removes a specific algebraic restriction and gives a
family with scalar future-Y bridges. It does not supply a complete decoder,
the first response, a native stock bound, a full recursive invoice, or a
new kappa value. Original selected-input acquisition remains an open issue
for the unchanged retired E outputs.

Run from the workspace root:

```
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/controller-followthrough-20261017/check_general_bridges.py
```

The expected result is `PASS_GENERAL_MATCHED_BRIDGES`. The checker uses exact
rational matrices and a direct event replay. It checks arbitrary returns,
noncommuting varying projections, both query-preserving choices, and the
signed-kernel identity. Finite checks support the proof for all pair counts.
The work was prepared with substantial OpenAI Codex assistance. No PR is
authorized or published.
