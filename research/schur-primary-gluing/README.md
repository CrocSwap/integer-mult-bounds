# Primary gluing for the whole ordered Schur residual

**Scoped written proof with exact finite corroboration.** For a sharp common
identity-block Schur deletion over any field, the compressed matrix H and the
four original ordered sector dimensions determine one simultaneous-conjugacy
orbit of the entire ordered residual pair. No extra sector00 factor invariant
survives. This finishes the general-H gluing question left by
[Ali Romman's #5348](https://github.com/CrocSwap/integer-mult-bounds/pull/5348),
following [ssafwann's #5267](https://github.com/CrocSwap/integer-mult-bounds/pull/5267)
and [the released handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/5337).

The new step is a constructive decomposition of the sector factors, especially
sector00, followed by explicit full residual intertwiners. The sector-capacity
criterion, full-rank factor extension lemma, and H=1 normal form retain
predecessor credit. We also justify the earlier nilpotent formula on the entire
W-invertible component; nilpotence is not assumed there.

This is an algebraic side result for one deletion, not a physical supplier or
an improvement to kappa. Distinct H/profile data may yield the same residual
orbit: the result is sufficiency of fixed data, not an injective classification
of all parameter choices. The selected conditional kappa remains 0.00302015.

**Concurrent independent work.** The final overlap refresh found Ali Romman's
[independent proof and constructive map](https://github.com/aliromman/integer-mult-bounds/blob/49373a6f433fef560a4297f65f3826a8add7cd44/research/general-ordered-schur/PROOF.md).
It reaches the same Fitting decomposition and ordered representative.
[The coordination reply](https://github.com/CrocSwap/integer-mult-bounds/discussions/5337#discussioncomment-19153030)
records that Ali moved the primary focus of that contribution to the
complementary fixed-H header weights. Our proof and separate checker were
frozen at `f69863ddefafa183babe2b59a8e5c91a92786fd1` before reading that proof.
The concurrent code is not imported or an executable dependency, and its
reported checks were not replayed here. Credit is shared for the independently
obtained gluing result; no exclusive discovery claim is made.

## Contract and explicit representative

Work over any field F. Let P0,Q0 be commuting idempotents on V, with ordered
joint sectors V00,V10,V01,V11 of dimensions r00,r10,r01,r11. Let
i:U->V and pi:V->U, U=F^d, d>=1, satisfy

```text
pi i = pi P0 i = pi Q0 i = I,       H = pi P0 Q0 i.
```

In any header M=[i,B] with B a basis of ker pi, write

```text
M^-1 P0 M = [I b; c D],    M^-1 Q0 M = [I f; g E],
S=D-cb,                    T=E-gf.
```

Require rank(ST-TS)=2d. Put W=I-H, a0=nullity H and a1=nullity W.
We retain Nick Petalas's [#4746](https://github.com/CrocSwap/integer-mult-bounds/pull/4746)
sharp criterion and capacity theorem:

```text
r00 >= d-a1,
r10 = d+a1+s10, r01 = d+a1+s01, r11 = d+a0+s11,   s10,s01,s11 >= 0. (1)
```

Every profile (1) is attainable for the prescribed H. This is a cited result,
not a new dimension minimum. The source construction permits larger r00 by
adding unused sector00 directions.

Use the Fitting decomposition for W, without a splitting-field extension:

```text
U = Uc direct-sum U1,     Uc=im W^d, U1=ker W^d,
dc=dim Uc, d1=dim U1,
H=Hc direct-sum H1,       Wc=I-Hc invertible, W1=I-H1 nilpotent.       (2)
```

Thus H1 is invertible, nullity Hc=a0 and nullity W1=a1. Choose
N0:F^a0->Uc complementing im Hc, and N1:F^a1->U1 complementing im W1.
Zero-dimensional components and empty blocks are allowed.

On Uc^3 direct-sum F^a0 define

```text
Sc(x,y,z,t) = (Hc(x-z)-N0t, 0, Wc(z-x)-N0t, t),
Tc(x,y,z,t) = (0, Hc(y-z)-N0t, Wc(z-y)-N0t, t).                       (3)
```

On E1=U1 direct-sum F^a1 put A=[W1 N1; 0 0]. On E1 direct-sum E1 set

```text
S1(u,v)=(u+Av,0),             T1(u,v)=(0,Au+v).                     (4)
```

**Theorem.** Every admitted ordered residual (S,T) is simultaneously similar to

```text
(Sc,Tc) direct-sum (S1,T1)
 direct-sum (0,0)^(r00-dc)
 direct-sum (1,0)^s10 direct-sum (0,1)^s01 direct-sum (1,1)^s11.      (5)
```

Here r00-dc>=d1-a1>=0. Its dimension is

```text
(3dc+a0) + 2(d1+a1) + (r00-dc) + s10+s01+s11
 = r00+r10+r01+r11-d.
```

All choices of primary bases and complements give the same ordered-pair
orbit. The formula includes arbitrary characteristic, repeated primary factors,
and irreducible factors that do not split over F. It never divides by two.

## Proof

### Source factors and active sectors

Let E_j be the original joint-sector projectors, Y_j=E_j i and X_j=pi|V_j.
The source equations are

```text
X00Y00=-W,    X10Y10=W,    X01Y01=W,    X11Y11=H.                    (6)
```

The source sharp criterion says that Y10,Y01,Y11 are injective and
X10,X01,X11 are onto. It imposes no such requirement in sector00.

For onto X and injective Y with XY=B, choose the columns Y of a basis of U,
then lifts under X of a basis N complementing im B, then a basis of the
remaining kernel directions. The resulting coordinates give

```text
X=[B N 0],            Y=[I;0;0].                                  (7)
```

Indeed im Y intersects ker X in Y ker B. The added lifts are independent
modulo im Y+ker X, and the remaining ker X directions complete the basis.
This is the full-rank extension principle of codyw912 #4735 and MatShep #4762,
also specialized explicitly in #5267; it is a credited lemma.

Under (2), choose N separately in Uc and U1. For sectors10 and01, only U1
needs the a1 extra lift directions because Wc is invertible. For sector11,
only Uc needs the a0 extra directions because H1 is invertible. Each active
sector splits into its two primary factor systems and s_j unused directions.
The unused directions give the last three scalar summands in (5).

### Splitting the arbitrary sector00 factor

This step cannot be replaced by applying (7) to sector00: its maps can have
deficient ranks. Write X=X00, Y=Y00 and let Pc:U->Uc be the projection in (2).
Since XY=-W, Y|Uc is injective. Define

```text
J = (Y|Uc) (-Wc)^-1 Pc X : V00 -> V00.                             (8)
```

For u in Uc, JYu=Yu. Thus J is the projection onto YUc and

```text
V00 = YUc direct-sum V001,       V001=ker(Pc X).                    (9)
```

Consequently dim V001=r00-dc. The map X sends V001 into U1, and Y sends U1
into V001 because Pc X Y|U1=-Pc W|U1=0. Choosing coordinates on YUc via Y gives

```text
X00 = (-Wc) direct-sum X1,       Y00 = I direct-sum Y1,
X1Y1=-W1.                                                        (10)
```

No rank assumption on X1 or Y1 was added. This also covers absent primary
components. The classical Fitting decomposition is applicable because the
image and kernel of W^d are stable, disjoint and have complementary dimensions;
W is invertible on the image and nilpotent on the kernel. All operations in
(8)-(10) are over F.

Together with the active-sector construction, both i and pi respect Uc+U1
and the corresponding ambient decomposition. P0,Q0 respect it too, since all
ambient basis changes occur within original joint sectors. Concatenating bases
of the two kernels makes the entire Schur residual a direct sum of the two
residuals and the active scalar padding. This proves the primary gluing before
any central-spectrum argument.

### The W-invertible component needs no nilpotence assumption

Its normalized factors are

```text
X00=-Wc, X10=X01=Wc, X11=[Hc N0],
Y00=Y10=Y01=I,       Y11=[I;0].                                  (11)
```

The kernel of their combined projection is parametrized by

```text
(v00,v10,v01,v11,extra11)
 = (x+y+Wc^-1 Hc z+Wc^-1 N0 t, x, y, z, t).                     (12)
```

On ker pi the residual of P0 is the restriction of P0-P0 i pi P0, and
similarly for Q0. These maps preserve ker pi because the common pivot is I.
In (12), pi P0 equals Wc x+Hc z+N0t. Subtracting its injection from the active
sectors gives Sc in (3); Q0 gives Tc. Nilpotence of Hc was not used: invertible
Wc is sufficient. This justifies extending the displayed model from #5267.
Its nilpotent Jordan and weight claims are not generalized here.

### The remaining sector00 data disappear on U1

Retain X1,Y1 in (10). For ambient coordinates (v,x,b,y,c,z) in
V001,U1,F^a1,U1,F^a1,U1, solve the kernel equation using invertible H1:

```text
z = -H1^-1(X1v+W1x+N1b+W1y+N1c).                                (13)
```

The literal residual maps on the five free coordinates are

```text
S(v,x,b,y,c)=(0, x+X1v+W1y+N1c, b, 0, 0),
T(v,x,b,y,c)=(0, 0, 0, y+X1v+W1x+N1b, c).                       (14)
```

Y1 has disappeared. Put C=(I+W1)^-1, which exists over every field since W1
is nilpotent. The invertible change

```text
xbar=x+C X1v,                 ybar=y+C X1v                       (15)
```

removes X1v from both formulas because (I+W1)C=I. The v directions become a
common zero summand of dimension r00-dc; the remaining maps are (4). This is
#5348's coordinate removal, applied after the justified split (9), without
assuming invertibility of I+W on all of U.

These steps prove (5) and construct an intertwiner. Compose the sector basis
changes with (12), (13), and the inverse of (15). All component maps are
invertible onto their claimed spaces. Express the resulting columns in any
header's ker pi basis to obtain invertible G with SG=GScan and TG=GTcan.
Mapping two admitted residuals to the same (5) proves the fixed-data orbit
statement. Choosing other complements or bases constructs another such map.

## Exact checks and reproduction

The standalone standard-library checker imports no predecessor code. It
constructs i,pi and diagonal P0,Q0, chooses a separate nullspace header M,
inverts M and computes both literal Schur complements. It constructs the proof's
embedding separately and checks invertible G, SG=GScan and TG=GTcan. Input
pivots, H, idempotence, original commutation and sharp rank are also checked.
Matching central spectra would not suffice.

- **111 complete H-domain cases:** every d=1,2 matrix over F2/F3 and every
  d=1 matrix over F4/F5, using the credited attaining factors.
- **364 arbitrary sector00 factor pairs:** every X in M_(d,r00) and Y in
  M_(r00,d), with H=I+XY, for F2,d=2,r00=0,1,2 and F3,d=1,r00=0,1,2.
  The active sectors use full-rank factors; deterministic invertible shears
  change sector bases. Deficient sector00 maps remain permitted.
- **40 larger fixtures:** mixed primary components, Jordan blocks through
  size three, repeated quadratic components, changed leading/sector bases and
  scalar padding over F2,F3,F4,F5. The quadratic x^2-x-1 is irreducible over
  F2/F3, so some fixtures genuinely cover nonsplit repeated factors.
- **Eight controls:** missing (15), globally singular W, wrong sector00 sign,
  a deficient active factor, an unstabilized Fitting split, wrong scalar
  padding, an empty leading block, and omission of the sector profile.

F4 is F2[t]/(t^2+t+1), not integers modulo four. Explicit exceptions remain
enabled under optimized Python. The checker prints executed domain counts, a
fixture digest and `PASS_SCHUR_PRIMARY_GLUING`; it accesses no network/Git and
writes no files. The arbitrary-field theorem rests on the written proof and
cited sharp-sector lemma; finite tests are corroboration, not proof-kernel or
independent human acceptance.

From the repository root with Python 3.12:

```sh
python -B scripts/research_package.py --package research/schur-primary-gluing
python -I -W error -B research/schur-primary-gluing/verify.py
python -I -W error -O -B research/schur-primary-gluing/verify.py
```

Registered commands run serially with a 60-second cap each. Source provenance
is pinned in `SOURCES.json`; the checker has no external runtime inputs.
`TASK.json` records scope, overlap and remaining obligations. Committed-byte
and export checks are recorded in the PR rather than embedding a self-commit.

No Lean, Docker, native operator, selected cold replay, physical stock/caller,
compiler or multiplication-theorem audit is part of this package. Selected
orientation reported sparse omissions, not a baseline pass. The selected
record, certificate, manifest and review were read; this result does not consume
their scientific inputs.

## Open next questions

Fixed-H/profile sufficiency is closed by the stated proof. A distinct question
is whether two different parameter data yield the same ordered residual orbit.
Begin with (5) on specified profiles only if a named consumer actually needs
state deduplication. No injectivity or full orbit algorithm is supplied, and no
larger census is proposed without that need.

Header probabilities, later-guard survival and physical use remain separate.
Before expanding into a supplier, name a consumer and its complete cost
allowance: selection/emission, reads, restoration, precision, storage, stock
and dispatch remain unknown. A local normal form does not make them zero.
Stop this contribution at the gluing result.

## Attribution

Prepared for **Mihir Srivastava (@mihir-s-05)** with substantial **OpenAI Codex**
assistance, one agent; Apache-2.0. No literature-wide novelty claim is made.

- **ssafwann #5267:** nilpotent whole-residual rigidity, explicit model and
  full-rank factor specialization. Its Jordan/weight claims retain their scope.
- **Ali Romman #5348:** H=1 ordered normal form and sector00 removal.
  **#5287** already answers the whole-central-class and characteristic-two
  questions; those are not new claims here.
- **Nick Petalas #4746/#4597:** signed sector criterion, attaining construction
  and ordered Schur factorization. **MatShep #4762** and **codyw912 #4735**:
  factor-system extension and the sufficient-invariant question.
- **JoyboyBrian:** released general-H handoff. **Ryanson Jonathan, lee-phys,
  ssafwann's earlier work, Cinna Davis, source527, commdata2338 and Jose Manuel**
  retain the Schur, dimension, header, BIT and normalizer lineage credited in
  the pinned sources. Fitting decomposition and basis extension are classical.

Predecessors are archived, partially reviewed contributions; merging is not
scientific acceptance. Their frozen files and attribution remain unchanged.
