# Saturated body ranks in a three-query binary header

Theorem and independent review extension, Jerry Chen / @CubeJerry with substantial OpenAI Codex assistance, Apache-2.0. This strengthens the fixed-prefix finding under additional global header and body-budget hypotheses. A separate agent has checked the argument in this session; external human or formal-kernel acceptance is not claimed.

## Contract

Work over any field F with a formal central S satisfying S²=1, and one independent Laurent body variable D. At D=1, a scalar circuit uses exactly three rank-one central queries `I+S u_i v_i`, with ordinary u_i,v_i and `v_i u_i=0`, together with S-independent invertible ordinary controls. Arbitrarily many ordinary spectator inputs are allowed.

After normalization at S=1, its required header is

```
W(S,1) W(1,1)^(-1) = I + (S-1) K,
K = E_XY + I_E,
```

where E is a two-dimensional S-target space, X,Y are distinct directions outside E, `E_XY²=0`, and K vanishes on any remaining spectators. Thus rank K=3, `im K=F X ⊕ E`, and `row K=F Y* ⊕ E*`.

Every D-bearing gate is a positive unit-exponent projector factor `I+(D-1)P_j`, `P_j²=P_j`, with an ordinary factorization P_j=U_j V_j and V_j U_j=I_r_j. The required endpoint is

```
W(S,D) = [I+(D-1)P_D] W(S,1).
```

Saturation is automatic for this contract: specialize S=1 and compare determinants as Laurent polynomials in D. Every positive projector factor contributes D^(r_j), every ordinary/query factor has D-independent nonzero determinant, and the endpoint contributes D^(rank(P_D)). Hence `Σ r_j = rank(P_D)`. Additional positive transport cannot avoid this equality without changing the endpoint's body degrees. The final ordinary body projector P_D commutes with K. At least one of the three central queries is coupled to a D-native stage: its rank-one nilpotent N is supported on that stage's projector P on both sides, `PN=NP=N`. The query and body factor occur together as one atomic native factor, in either order, with no intervening gate. They commute. The support equation by itself would not align their suffixes if arbitrary noncommuting gates intervened.

**Claim:** the induced projector P_D on E has rank two. In particular, a saturated body with a native query cannot omit either of the two S-target directions.

## 1. Every query acts nontrivially on the S-target quotient

Normalize each query at S=1 and absorb all constant gates. Write `x=S-1`, so `x²=-2x`, in every characteristic. The three-query word has the form

```
(I+x N3)(I+x N2)(I+x N1) = I+x K.
```

Write `Ni=ui vi`, with `vi ui=0`. Expanding the product gives `K=U T V`, where U has the three columns ui, V has the three rows vi, and T is a unit triangular 3-by-3 matrix. Since rank K=3, U and V both have rank three. Therefore every ui lies in `im K=F X⊕E`, and every vi lies in `row K=F Y*⊕E*`.

The X component of a query image cannot feed a later query, because each row vanishes on X. Each query therefore induces a rank-at-most-one map Ai on the quotient `(im K)/(F X)`, identified with E. Its self-pairing is zero: the X/Y components contribute nothing to `vi ui`, so `Ai²=0`. The three quotient factors have endpoint `S I_E`.

None of the Ai is zero. Otherwise two rank-one nilpotent queries would produce S on two independent directions. To see why that is impossible in every characteristic, expand the two-factor normalized word as `I+x J`, with `J=U2 T2 V2` and T2 unit triangular. If J fixes a two-dimensional subspace, rank J=2, its image is precisely that subspace, and J²=J. Full column and row ranks imply `V2 U2=T2^(-1)`. Its diagonal is one, contradicting the zero diagonal self-pairings `vi ui=0`. This argument retains formal x in characteristic two; specializing S=1 would destroy it.

Thus every one of the three header queries induces a nonzero rank-one nilpotent on E.

## 2. Saturation forces every body-supported query into the final body space

Differentiate the endpoint in D at D=1 and multiply on the right by `W(S,1)^(-1)`. The logarithmic derivative is the sum of the D-projectors conjugated by their actual suffixes, and equals P_D.

This argument works over the commutative coefficient ring `F[S]/(S²-1)` without assuming it is a field. Factor each conjugated projector as `Uj Vj`, with r_j columns and rows. Concatenate U and V. Saturation gives a square-width factorization `UV=P_D`. In a fixed ordinary basis with `P_D=diag(I_r,0)`, write `U=[U1;U2]` and `V=[V1,V2]`, where U1,V1 are r-by-r. The equation `U1 V1=I_r` makes both matrices invertible over this commutative ring, so the other blocks force U2=0 and V2=0. Consequently every individual projector, and every nilpotent supported on one of those projectors, is supported by P_D on both sides.

Specialize S=1. The corresponding normalized central query is conjugated by exactly the same ordinary suffix used for its body factor. Because its query and body projector commute, their relative ordering does not matter. Therefore its normalized Ni satisfies `P_D Ni=Ni P_D=Ni`.

Since P_D commutes with K, it preserves the quotient E above. The induced Ai is supported on the induced body projector there. If this body projector had rank at most one, its supported endomorphisms would be scalar multiples of a rank-one projector; none can be nonzero and nilpotent over a field. This contradicts Section 1. Hence its rank is two.

## 3. Consequences and scope

The proposed four-field mixed target `LR(I+S E_XY), SL, SR` has the stated rank-three header, but the L and R target projectors each include only one S-target direction. Its optimistic rank-three body tariff (one rank-two native stage plus one rank-one idle for each body) is saturated. The theorem therefore excludes a three-central-query realization in this projector/body model, despite its favorable concave invoice.

The same obstruction applies to one or two complete auxiliary fragmentations of the original binary macro when the total positive degree of each body remains four, each body retains its original native query, and the endpoint has exactly the original two S-target directions plus the active LR shear. After a fragment, at least one body omits an S-target direction. This includes mixed L/SL orientations. Extra central queries, different headers or body degrees, body-dependent ordinary controls, altered source/target contracts, and negative or otherwise non-projector/noninvertible body operations are outside this theorem. Extra positive transport with unchanged body degrees cannot evade the saturation identity.

This is an abstract source-relative obstruction. It does not audit any native physical action, supplier admission, finite compiler, precision/tape or analytic recovery assumption, and claims no new κ. The classical rank-factorization and derivative identities are not new; the contribution is their application to this precisely budgeted three-query binary fragmentation interface.

## 4. The one-fragment and mixed two-fragment price corollaries

The theorem raises the header requirement from the three original queries to at least four. One fragment gains strictly less than one rank-one query, as in the main cut proof, so it cannot fund this necessary extra query while all other charges are held to the same optimistic contract.

For the mixed two-fragment tariff, the total signed gain is

```
G(a,b) = i(a)+i(b)-2i(a+b),
i(x) = (x+1)^t-x^t,     0<t<1,     a,b>0.
```

This is also strictly less than one, uniformly over all positive body ranks. Assume a≤b. The increment i decreases, and

```
i(2b) = t ∫_0^1 (2b+s)^(t-1) ds
      >= 2^(t-1) t ∫_0^1 (b+s)^(t-1) ds
      = 2^(t-1) i(b).
```

The inequality follows from `2b+s <= 2(b+s)` and the negative exponent t-1. Therefore `2i(a+b) >= 2i(2b) >= 2^t i(b) > i(b)`, and `G(a,b)<i(a)<1`. Thus the mixed two-fragment gain cannot fund even the one necessary new query. This argument uses the power tariff; it does not claim the same inequality for every concave function.

Two equal-orientation fragments can instead gain `2[i(a)-i(a+b)]`, which need not be below one for arbitrarily asymmetric ranks. The four-query lower bound alone does not exclude that entire changed-history family economically. The fixed-prefix theorem separately prices its actual forward-and-restoration query debt. Do not infer a universal two-fragment no-go from the present header bound.


## 5. Coupled three-block extension

There is a coupled-width version of the algebraic obstruction. Give X and Y width w, let E have dimension 2w, and require `K=E_XY tensor I_w + I_E`, of rank 3w. Retain exactly three central query blocks `I+S Nj`, each with `Nj²=0` and rank at most w, allowing arbitrary ordinary coupling across the banks. The block factorization `K=U T V` has total width 3w and block-unit-triangular T. Rank saturation again puts every query image and row in `im K` and `row K`.

Each quotient query Ai on E is square-zero of rank at most w. The three quotient factors multiply to `S I_E`. A vector in the kernels of the first two quotient maps Ai would force the remaining Aj to have eigenvalue one, which is impossible for a nilpotent. Thus the kernels of those two Ai have zero intersection. The endpoint S I is central, so cyclically rotating the invertible factors proves this for every pair. Therefore `rank(Ai)+rank(Aj)>=2w`; since each is at most w, all three ranks equal w.

A square-zero rank-w endomorphism supported inside a projected carrier of dimension d requires `2w<=d`, because its w-dimensional image lies inside its kernel in that carrier. The final body projector must therefore include all 2w S-target dimensions. The determinant/saturation argument in Section 2 applies unchanged.

This extension fixes three square-zero query blocks. It does not cover arbitrary interleavings of 3w rank-one queries that cannot be regrouped into three such blocks. Nor does it price an added block as rank w: a fourth block could have smaller rank. The scalar price corollaries of Section 4 remain scalar statements, or apply to independent per-port replication. The fixed-prefix theorem supplies the separate arbitrary-width query-rank debt.


## Exact fixture evidence

`saturation.py` retains the exact three normalized source query fixtures, checks their full formal header and auxiliary quotient, and tests their ranks over Q, F2, F3 and F5 at widths 1,2,3. It rejects removing any quotient factor and checks that omitting any S-target coordinate from the body projector breaks native-query support. Five exact rational enclosures at t=7/8 corroborate the mixed price sign and upper bound. A deliberate limitation control with body ranks a=8, b=8*2^80 proves that two equal-orientation gains can exceed one; it prevents the scalar mixed-price corollary from being silently extended to that case. These finite fixtures corroborate the written proof and its limits. They do not supply its arbitrary-field, width, or rank quantifiers.

The fixture values were independently obtained from the literal normalized binary macro by conjugating each central query by its S=1 ordinary suffix. The full source correspondence is retained in the independent review; the frozen caller bytes are hash-bound. Normal and optimized runs have identical output, with canonical receipt SHA256 `f78d9394f96c924592844e12776ca9bd27f11c3729287d762d4e4ecef9ab18d7`.

The body identities are formal Laurent identities. An identity valid only
after imposing a physical relation such as D^4=1 is outside this determinant
argument; a quotient identity is not silently promoted to a formal one.
