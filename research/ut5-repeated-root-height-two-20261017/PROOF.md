# Exact five-call minimum for one repeated-root UT5 target

## Statement and assumptions

Let `G = UT5(Z)`, the group of 5 by 5 upper-unitriangular integer matrices, and let `F2[G]` be its full formal group algebra. Write

```text
g_i = I + E_(i,i+1),       i=1,2,3,4.
```

There are four scalar roles, arbitrary and dirty at input. A paid factor is

```text
D_N(g) = I + ([g] + [1]) N,
```

where `g` is one of `g_i` or `g_i^-1`, and `N = x y^T` is any rank-one idempotent in `M4(F2)`: `x,y` are nonzero binary four-vectors with `y^T x = 1`. Each such factor costs one. There are no free address changes, clean roles, copies, erasures, or uncounted restorations in this model. Equality means coefficientwise equality in `Mat4(F2[G])`, not equality on a finite set of addresses.

The fixed endpoint is

```text
T = diag([g1], [g1], [g2], [g1*g2]).
```

The claim proved here is that this endpoint has minimum length five in exactly this alphabet. It says nothing about other targets, groups, address alphabets, or integer-multiplication suppliers.

## Five-factor upper bound

For `E_ii`, take `x=y=e_i`. The following word gives `T` exactly:

```text
D_E11(g1) D_E22(g1) D_E33(g2) D_E44(g1) D_E44(g2).
```

The factors act on separate diagonal roles except for the last two, whose group-algebra coefficients multiply in the required order `[g1][g2]=[g1*g2]`. The verifier replays all 16 matrix entries using exact finite supports in the full group algebra.

## Lower bound outside length three

Define the homomorphism `chi : G -> C2` by summing the four first-superdiagonal entries modulo two. The first-superdiagonal entries add under multiplication, so this is a group homomorphism. Every signed simple-root letter maps to the nonidentity element `z` of `C2`; `g1*g2` maps to `z^2=1`.

For any allowed idempotent `N`, its image and kernel split the four-dimensional binary scalar space into one-dimensional and three-dimensional summands. After applying the group-algebra map induced by `chi`, `D_N(g)` acts as `z` on the image and as `1` on the kernel. Thus its determinant is `z`. The determinant of the target is also `z`, since its diagonal maps to `(z,z,z,1)`. Any realizing word therefore has odd length.

Length zero is impossible because `T != I`. One factor is impossible because a single `D_N(g)` has address support contained in `{1,g}`, while `T` contains the three distinct nonidentity basis elements `g1`, `g2`, and `g1*g2`. So a word of length below five, if it existed, would have to have length three.

## Complete length-three exclusion

There are exactly 120 rank-one idempotents: `x,y` range over nonzero binary four-vectors with `y^T x=1`; the verifier checks each matrix satisfies `N^2=N` and `tr(N)=1`. With eight signed labels this gives 960 paid factors.

For `lambda_g=[g]+[1]`, two factors obey the exact identity

```text
D_N(g) D_M(h)
  = I + lambda_g N + lambda_h M + lambda_g lambda_h N M,
N M = x (y^T u) v^T   when N=x y^T and M=u v^T.
```

Each two-factor matrix entry has support among `{1,g,h,gh}`. The verifier forms the exact 16-entry coefficient key for every ordered pair of factors (all `960^2 = 921,600` pairs), using integer coordinates in `UT5(Z)` and binary coefficient masks. It then checks every possible final factor `C` by querying `T C^-1`; the inverse of `D_N(g)` is `D_N(g^-1)`, also in the alphabet. This covers every ordered three-factor word, `960^3 = 884,736,000` in total. The complete join has zero hits.

The exclusion is an exact finite enumeration of the declared finite alphabet and length-three words. It is not finite-address sampling: the support keys contain actual integer UT5(Z) elements, not a finite quotient. The verifier also checks all 960 right-query formulas by independent sparse multiplication in the full group algebra and checks the pair formula on all 16 pairs from a small positive-control alphabet.

Combining odd length, the zero/one-factor obstructions, the exact length-three exclusion, and the five-factor word proves the exact minimum is five.

## Native-address scope and limitations

Every signed address difference is exactly `+E_(i,i+1)` or `-E_(i,i+1)`, a rank-one integer matrix with an integer inverse. This establishes that the address labels themselves are literal rank-one elementary updates in the stated UT5(Z) model. It does not implement these calls inside the selected recursive integer-multiplication construction.

The exact formal-model theorem is computer-assisted and reproducible with the standard-library verifier; it is not proof-assistant verified. There is no numerical evidence, conditional estimate, supplier transfer, selected-record edit, or new `kappa` claim. The proved range is one fixed four-role endpoint, the eight signed simple-root labels, all 120 binary rank-one idempotents, and word lengths below five.
