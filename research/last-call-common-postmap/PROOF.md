# A common free post-map can be moved before the last call

## Result and model

Consider one prepared last call followed by one common free map on its output. When the shared part has one level-two leading term and only lower-level companion terms, this post-map adds no power to finishing a level-three target. A target-frame projection forces the post-map to be invertible in a specific subgroup algebra. It can then be moved before the call.

As a consequence, the nonplain kind B obstruction in [PR #7683](https://github.com/CrocSwap/integer-mult-bounds/pull/7683) also holds with arbitrary common free postprocessing. This includes arbitrary spare address bits and all nonzero rational coefficients. A second result within this same boundary check is an explicit false positive for a larger linear-span test: two independently prepared and independently postprocessed columns can span the target, while one prepared call cannot produce it. The distinction is the common post-map, not the availability of a free matrix.

Work in `Q[G]`, where `G=Sp(2m,2)`, `m>=3`, and `P=Stab_G(L)` for the raw Lagrangian L. Terms are formal group basis elements. Their level is `ell(g)=m-dim(L intersection g^-1 L)`. Level is invariant under free left or right factors and is subadditive. Free combinations form the algebra `Q[P]`. A paid call T is an involution of level one.

Let M have level two with `ell(TM)=3`. Let B be any finite collection of terms of level at most one. Let z be any rational combination of terms of level at most one, and set

```text
y = M+z,
U = sum_(b in B) Q[P] b + Q[P] y,
H = P intersection T P T.
```

Every term in U has level at most two. U is closed under left multiplication by `Q[P]`. The most general output under the present one-call contract is

```text
u+F T v,     u,v in U,     F in Q[P].
```

The same F acts on the whole output of the one call. It is not assumed invertible. Free preparation of v and free additions of earlier arrays are unrestricted within U. Several consecutive free post-maps compose to one F.

**Folding theorem.** The target TM has a representation `u+F T v` if and only if it lies in `U+TU`. In every such representation, F is a unit of `Q[H]`, and `F T = T (T F T)` with `T F T` free.

The statement concerns this fixed target TM and one last call. It does not cover a second last output, multiple call outputs with separate post-maps, a second level-two companion term, Pauli phases, or a physical realization of the free algebra. No new kappa or general two-in-five impossibility follows.

## Project onto the target's frame

Let C be the left coset `P TM` and let pi keep only coefficients with indices in C. Every term in C has level three. Since free left multiplication preserves each left coset of P, pi commutes with left multiplication by every F in `Q[P]`.

For any p in P and b in B, `Tpb` has level at most two. The same bound holds for every term of `Tpz`. Hence only the leading term `TpM` can contribute to `pi(Tv)`. It belongs to C exactly when

```text
(TpM)(TM)^-1 = TpT is in P.
```

In that case `h=TpT` lies in H, since `ThT=p` is also free. Conversely every h in H has this form with p free. Therefore

```text
pi(Tv) = A TM     for some A in Q[H].
```

Also `pi(u)=0`. If `TM=u+F T v`, projection gives `TM=F A TM`. The group term TM is invertible, so

```text
F A = 1.
```

This is an identity in the full free group algebra. It is not a coefficient equation in a quotient where extra support can be ignored.

## A one-sided inverse stays in the subgroup algebra

P and H are finite groups. From `FA=1`, left multiplication by A is injective on the finite-dimensional space `Q[H]`: `Ax=0` implies `x=FAx=0`. It is therefore surjective on that space. There is a B0 in `Q[H]` with `A B0=1`.

Now `F=F A B0=B0`. Thus F belongs to `Q[H]` and is the two-sided inverse of A. This proves invertibility rather than assuming it. It also excludes a singular post-map that tries to erase other level-three frames.

By the definition of H, `T F T` belongs to `Q[P]`. Consequently

```text
F T v = T (T F T) v is in TU.
```

The last inclusion uses the left `Q[P]` stability of U. Thus every postprocessed finishing witness is already a call-alone witness. The reverse direction uses F=1. This proves the folding theorem at every address width. It does not require an enumeration of the group or a choice of coefficients in z.

## Corollary for nonplain kind B

Take `B={1,D}`, `M=WD` and `z=cW gamma`, where D,W,T are paid calls, gamma is free, `c!=0`, `ell(TWD)=3`, and `W gamma` is outside PD. The sole companion term has level one. All hypotheses of the folding theorem hold.

The [call-alone proof at its exact head](https://github.com/aliromman/integer-mult-bounds/blob/9b99d7b30972a78e1ad0e90dd6ff3187bd3cc86c/research/kind-b-last-call-obstruction/PROOF.md) gives `TM` outside `U+TU`. It supplies a two- or three-coordinate separating functional for that space. Folding therefore rules out `TM=u+F T v` for every common F and every u,v in U. No nonplain kind B part finishes under this one-call postprocessing contract, including with spare bits.

This strengthens the stated call-alone boundary. It still leaves joint decoding, different shared-call arrangements and extra high-level terms open. It is a formal-frame result, not a physical engine lower bound.

## A relaxed span gives a false positive

Use three address bits and binary row-matrix encoding in order `(x0,x1,x2,z0,z1,z2)`. Let `D=t_1`, `W=t_2`, `T=t_5`, with pure horizontal normals given by those bit masks. Use the following free matrices, with each row written as its bit mask:

```text
gamma = (1,2,5,40,16,32),
R     = (5,4,2,8,40,16),
S     = (3,5,2,40,32,56).
```

Here gamma swaps D and T by conjugation and commutes with W. Also `R T R^-1=W` and `S=R^-1 gamma`. Set `M=WD`, `E=W gamma` and `y=M+cE`. The target TM has level three and E is nonplain. Exact multiplication gives

```text
TE = E D = R T S D,
TM = T y - c R T (S D).
```

The right side belongs to the linear span of independently prepared and independently postprocessed columns: one input is y with identity post-map, and the other input is SD with post-map R. Both inputs are in U. But the theorem proves that no single common F on one prepared call produces TM, for any nonzero rational c. This identity can be executed with two separate calls; treating its column span as one call loses the common-factor constraint.

The checker also verifies the exact call-alone separator for this example over all 10752 free preparations, with polynomial coefficients in c. Its support is `TM,TE,gamma E`, with weights `c^2,-c,1`. Every old or paid binomial and earlier singleton is killed. The relaxed identity is checked at five nonzero rational coefficients; its displayed symbolic equality proves it for all c. This is a counterexample to sufficiency of the relaxed test, not a construction of a two-in-five unit.

## Why the low-level companion condition matters

Kind A can have a second level-two term. The folding theorem then does not apply. A positive control uses `D=t_1`, `W=t_2`, `T=t_4`,

```text
gamma_A = (1,2,6,8,52,34),
E_A = W gamma_A D,
h = (1,6,4,8,20,50).
```

E_A has level two and a different frame from M. The free element h has order two, lies outside H, and satisfies `T E_A=h TM`. For coefficient two,

```text
T (M+2E_A) = (1+2h) TM,
F = (2h-1)/3,
F T (M+2E_A) = TM.
```

This is one actual prepared call followed by one common free map. The target-coset coefficient is now `1+2h`, which lies outside `Q[H]` because the second high-level term also contributes. This verifies the boundary of the new lemma. The existence of kind A post-call gains is prior work in [PR #7629](https://github.com/CrocSwap/integer-mult-bounds/pull/7629) and [PR #7649](https://github.com/CrocSwap/integer-mult-bounds/pull/7649); this example is a control, not a new claimed construction.

## Exact checks and limits

The finite checker enumerates all 10752 three-bit free elements and all 32 calls that raise the fixed `WD` to level three. It checks all 344064 preparation/call pairs. Exactly 768 columns survive the target-frame projection for each call, for 24576 surviving columns in total. Every survivor is in the intersection subgroup. All paid earlier inputs and every kind B companion family stay below level three. The latter check is independent of gamma because a free factor on the right does not change level.

For all 32 calls, explicit group-algebra units and their inverses verify the fold. Nonunit examples have a checked nonzero kernel, and an outside-subgroup unit has an inverse outside the required projection space. Ninety-six wider conjugated contracts at widths four through six verify these unit and nonunit statements with a spare coordinate in the conjugation. The relaxed false positive and the kind A positive control are checked as exact group-algebra identities. [Receipt and matrices](RESULT.json) · [Verifier](verify.py)

These finite checks support the proof; they do not enumerate arbitrary rational post-maps or all wider groups. The prior call-alone proof is a mathematical dependency, not a runtime import. Its full census was not rerun. Native operators, selected cold replay, Lean and Docker were not run. Independent human and formal-kernel review are unclaimed. All five selected assumptions and the selected frontier remain unchanged.

## Attribution

Prepared by Ali Romman with substantial OpenAI Codex assistance. Jacob Sussman supplied the kind B definitions and the untested post-call question in [PR #7629](https://github.com/CrocSwap/integer-mult-bounds/pull/7629), [pinned source](https://github.com/jacobalansussman/integer-mult-bounds/blob/c2a2131e7dba35f9396b16588e125a7e8b5fab8e/research/complex-m3-shared-call-finish-or-remove/README.md). Nick Petalas supplied the related coset method and post-call boundary in [PR #7649](https://github.com/CrocSwap/integer-mult-bounds/pull/7649), [pinned proof](https://github.com/petalas/integer-mult-bounds/blob/f642d2740265a61f8ac64b3a087f0118382c56e3/research/kind-a-last-call-coset/README.md). Ali Romman's [PR #7683](https://github.com/CrocSwap/integer-mult-bounds/pull/7683) supplies the call-alone obstruction used in the corollary. Binary matrix routines are reused from that package and its [PR #7679](https://github.com/CrocSwap/integer-mult-bounds/pull/7679) predecessor. The common-factor proof and exact separation from the relaxed column span are the new work. New work is Apache-2.0.
