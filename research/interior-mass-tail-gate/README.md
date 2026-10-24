# Sharp adaptive tail gate with prescribed interior mass

This scoped theorem strengthens the range-and-mean tail screen with a specified amount of interior mass. It gives a sharp worst-case adaptive decision, an attaining law, and an integer histogram that the old screen cannot certify. It answers the released [Discussion #5335](https://github.com/CrocSwap/integer-mult-bounds/discussions/5335). Mirror and recurrence funding are separate. The complete kappa calculation is unchanged.

**Contract.** Use the normalization in Nick Petalas's cited proof: q=T(t)/P(t)>=1, Z=(log k-A)/(B-A), p=E Z, x=(mu_P-A)/(B-A), and h=lambda(B-A). The scalar tail criterion is q E exp[-h(Z-x)]<1 for some h>0. The source's equivalence from this strict criterion to the three compiler gates is a cited premise, not audited here.

Fix 0<rho<=1 and 0<ell<=u<1. Consider the class of probability laws supported in [0,1], with mean p and mass exactly rho in [ell,u]. It is nonempty precisely when rho ell<=p<=1-rho+rho u. The same worst-case result holds if the interior mass is at least rho. The class permits zero endpoint weights; requiring positive weights at both endpoints is a smaller class and can change attainment at boundary statistics. No arbitrary law is claimed to have an integer native realization.

**Two-law envelope.** Set

    L=max(ell,(p-1+rho)/rho),   U=min(u,p/rho).

For y in [L,U], let Q_y have masses

    at 0:   1-rho-p+rho y,
    at ell: rho (u-y)/(u-ell),
    at u:   rho (y-ell)/(u-ell),
    at 1:   p-rho y.

When ell=u, replace the two interior rows by mass rho at ell. Then L=U=ell. Zero weights can be omitted. Define

    E(h)=max(E_(Q_L) exp[-h(Z-x)], E_(Q_U) exp[-h(Z-x)]).

For each h>0, E(h) is the exact largest transform over the stated class. To prove this, split exactly rho of the interior mass from the law. Replace this part by its mean-preserving chord on ell,u; replace the remainder by its chord on 0,1. Convexity increases the transform. The interior mean y lies in [L,U], and the new transform is affine in y. Its maximum is at L or U. These endpoint laws belong to the exact-mass class, which proves attainment and also proves the at-least-rho claim.

**Sharp adaptive decision.** Every law in the class has a strict passing h if and only if

    q inf_(h>0) E(h) < 1.                              (1)

Thus there is no gap between choosing h after the law is known and this robust envelope test. Here is an explicit complete boundary rule. Let z0 be the smallest point with positive mass in either Q_L or Q_U. Let eta be the larger mass assigned to z0 by those two laws.

- If x>=p, all laws fail, by Jensen and q>=1.
- If x<z0, E(h) tends to zero, so all laws pass.
- If x=z0<p, E(h) decreases strictly to eta. Passing is equivalent to q eta<1. Equality fails, since every finite value of a law with mass eta at z0 is larger than eta.
- If z0<x<p, E is strictly convex, its right derivative at zero is x-p<0, and E(h) tends to infinity. It has a unique positive minimum h*. Use (1) with that attained minimum; equality fails.

In the last case this is a one-variable, two-function decision, not a search over laws. At h*, either one active function has zero derivative or the active derivatives straddle zero. Choose a convex combination of the active Q laws whose transform derivative is zero there. Call it Q*. Its transform is convex, so h* is its global minimum, equal to E(h*). Q* is feasible and fails whenever qE(h*)>=1. This proves necessity and the equality case without interchanging an unjustified supremum and infimum. Sufficiency follows directly from the envelope. The same proof applies when L=U. To locate h*, it suffices to check stationary points of the two transforms and their crossing points, retaining only points where the active derivatives contain zero. The theorem supplies this exact characterization; no general transcendental root solver is included.

**A literal integer discriminator.** Take W4=1, W16=1, W256=32, P16=8 and t=1/2. Then T(t)=518, P(t)=32, x=1/3 and rho=4/518 at the known interior atom ell=u=1/3. With y=4^lambda, the unnormalized transform is

    2y+4+512/y^2.

Its exact minimum is 28 at y=8, lambda=3/2. The sharp condition for the same target and P16=c is c>7; equality at c=7 fails. In contrast, the endpoint law with the same total weight and mean has weights 14/3 and 1540/3. Its minimum cubed is (27/4)(14/3)^2(1540/3)=75460, which exceeds 32^3. Thus the older range-and-mean guarantee fails for c=8 while the new screen passes.

The original compiler gates pass with a=1, b=31, M=2^132, s=1/2 and lambda=3/2. Direct substitution gives

    u_tail = 2^-66 (4106/259) 4^31 = 2053/2072 < 1,
    v_tail = 2^198 (7/512)^32 = 7^32/2^90 < 1,
    T(1)/T(1/2) = 4106/259 > 4 = P(1)/P(1/2).

All comparisons are exact integers or rationals. The exit interval (1/16,1/4] still has no inner-source coverage: the only nonempty inner interval is (1/256,1/16]. The added rank16 atom makes no interval. This fixture therefore fails mirror coverage. It is a tail/ordering improvement only.

**Evidence and limits.** The checker verifies 150 rational statistic fixtures, 1,050 envelope comparisons and attaining cases, 77 chord comparisons, the three original gate inequalities, and seven invalid-input/boundary/old-screen/mirror controls. The general proof covers arbitrary probability laws in the stated class; these finite rational checks corroborate it. Histogram realization, all mirror and recurrence predicates, source preparation, native execution, complete stock and analytic recovery remain open.

Credit Nick Petalas's [PR #5254](https://github.com/CrocSwap/integer-mult-bounds/pull/5254) supplies the normalized criterion, sharp endpoint screen and explicit interior-mass question in its [proof](https://github.com/CrocSwap/integer-mult-bounds/blob/f7c2625f5488b09e6d19b4bed7efe8b4e89a6782/research/adaptive-tail-entropy/PROOF.md). That proof records Dillon Amburgey's [PR #4532](https://github.com/CrocSwap/integer-mult-bounds/pull/4532) scalar-to-gate equivalence, and the compiler lineage of zxv, Jacob Alan Sussman and Ryanson Jonathan. Those are retained premises and credits. Convex chord bounds and extremal moment methods are classical; the contribution is the sharp interior-mass adaptive boundary and the source-gate discriminator.

Prepared by Ali Romman with substantial OpenAI Codex assistance; Apache-2.0.

## Reproduce

```sh
python3 -B scripts/research_package.py --package research/interior-mass-tail-gate
```

Use Python 3.12 with the standard library. The normal and optimized commands must print `PASS_INTERIOR_MASS_TAIL_GATE`. The launcher must print `PASS_REGISTERED_RESEARCH_PACKAGE`. The checker has no external runtime inputs.

## Open next questions

Apply the interior-mass screen to a source-bound histogram that also passes every mirror and recurrence predicate. The source binding and physical cost model are not supplied by this package. See `TASK.json` for the structured scope.
