# Worker A review: exact-square affine-period obstruction

Review date: 2026-11-06 UTC. Worker A, with substantial OpenAI Codex
assistance, for @CubeJerry. Apache-2.0.

**Conclusion: no mathematical gap found in the stated theorem.** An odd
map on Z^16 commuting with K=SJ, with a full-rank affine A-period for
A=W16/4, has period index divisible by 4096. The exact-square condition
in the componentwise native architecture implies this commutation.
Existence at index 4096 and impossibility of generic F^4=I are not proved.

## Snapshot and review independence

Reviewed package: `worker-e/research/four-axis-exact-square-period-obstruction`,
relative to the session root. Worker B confirmed these final mathematical
bytes are stable in local commit `8614ef999f0dacd8b5e0038e9b66cd31b3d83790`:

- PROOF.md SHA-256: `605efb740932a218098734f4e91e9e54dd4e6c40fa12bb6f3384cc3b3a8a2eda`.
- verify.py SHA-256: `eec2e5212edae3e826dbc0a1c626fdd611633251e2d3988e05db3ed17dff6d3a`.

I independently challenged the implication, closure, lattice, and quotient
steps. I knew the proposed result and exchanged clarifications with B and
the lead; this was not a blind review. I did not edit the package. No
matching search or module census was needed or rerun. Finite witness tests
support the written argument; they do not formally verify the theorem.
Replaying B's checker is not an independently implemented oracle. The
independent portion of this review is the derivation and arithmetic below.

## 1. Exact square and closure of the declared period

S and J commute because complementation preserves four-bit parity, so
K=SJ is an involution. Walsh conjugation gives AS=JA and AJ=SA, hence
AK=KA and (SA)^2=K. If RSR=J, then T=SR satisfies T^2=K. Every map commutes
with its own square; because S commutes with K, R=ST commutes with K.
No unjustified commutation of R with S or J is used.

For lambda in an affine period Gamma and every integer z,

    R(z+K lambda) = K R(Kz+lambda) = R(z)+A K lambda.

Thus Gamma'=Gamma+K Gamma is a full-rank K-invariant affine period whose
index divides the index of Gamma. This removes any assumption that the
declared period is maximal or invariant.

The optional maximal-period route is sound too: RSR=J makes R bijective.
Apply that identity at z+lambda and use surjectivity of SR(z) to see that
SA lambda is a period. Since (SA)^4=I, the maximal period group is SA
invariant. The final proof needs only the simpler K closure.

## 2. Integrality and oddness

The displayed Walsh congruence modulo four is valid because terms with
two or more bit indicators have coefficients divisible by four. The map
given by total modulo four and four bit sums modulo two is onto: e0
supplies the total generator; e_(2^j)-e0 supplies each bit generator.
Therefore [Z:L]=64 and Z/L is Z4 direct-sum Z2^4. A preserves L since
A^2=I; K preserves L since it is integral and commutes with A.

V=L/2L has dimension 16. The map x+L -> 2x+2L identifies (Z/L)[2] with
E=(L intersect 2Z)/2L, giving dimension five and the displayed basis.
For an even period lambda=2x, translation at -x and oddness give
2R(x)=A lambda. Thus Ax is integral and lambda belongs to 2L.

Consequently H=(Gamma'+2L)/2L intersects E trivially, even without
2L contained in Gamma': if gamma+2ell is even, gamma is even, so gamma
belongs to 2L. H is K invariant, hence also invariant under C=K+I.
Its dimension is initially at most 11.

## 3. Two image classes force codimension at least six

The equalities C u0=0 and C uj=u0 hold in V, so C restricted to E has
rank one. The classes u0 and v=u1+u2+u3+u4 are independent in E and each
lies in C V. The displayed integer w gives the second preimage.

I checked the integer witnesses directly against the total/bit-sum
criterion. The first half-residual has total -4 and bit sums
(-2,-2,-2,-2); the second has total zero and bit sums (-2,0,0,0).
The vector w has total -8 and bit sums (-6,-4,-4,-4). Thus all are in L.
Also v/2 has odd bit sums, whereas u0/2 and (u0+v)/2 each have total two
modulo four. This checks independence of u0,v without the finite checker.

If dim H=11, V=E direct-sum H. Projection to V/H restricted to E is an
isomorphism intertwining C|E with the induced quotient operator. That
operator would have rank one. But the independent projections of u0,v
are both in its image because both have preimages in V. Contradiction.
Thus dim H<=10. This uses the image witnesses, not merely C^2=0.

The complete index calculation is

    [Z:Gamma'] = [Z:L] [L:Gamma'+2L] [Gamma'+2L:Gamma'].

The first factor is 64 and the second is 2^(16-dim H), divisible by 64.
Every factor is an integer, so [Z:Gamma'] and then [Z:Gamma] are divisible
by 4096. Neither saturation nor 2L contained in Gamma' is assumed.
This is stronger than just a numerical lower bound; attainment is open.

## 4. Exact-square scope

For the componentwise extension R_C, D_j=(-i)^wt(j), and F=-D R_C D,
oddness gives

    F^2 = D R_C S R_C D.

Only a global minus sign is pulled through R_C; R_C is not assumed to
commute with the nonuniform D. Since DJD=J, also D^-1 J D^-1=J. Hence
F^2=J is equivalent to R_C S R_C=J and to RSR=J on real components.
Oddness supplies R(0)=0 when restricting to a real component.

F^2=J implies F^4=I. A generic F^4=I does not specify the square required
for the commutation argument, and is not excluded by this proof. The
result also does not cover arbitrary coupled complex architectures or
nonperiodic maps. No kappa, admission, gate count, or storage claim follows.

The next-step correction-cycle condition is necessary, not a construction.
For a B=SA invariant period and T(z)=Bz+c([z])/4, comparison of T^2(z)
with Kz gives c(p(s))=-B c(s), as stated.

## 5. Verification evidence

Before packaging I executed, from lead-explore:

    python3 -I -W error -B fourth-power/obstruction_check.py
    python3 -I -O -W error -B fourth-power/obstruction_check.py

Both emitted PASS_INDEX4096_OBSTRUCTION_WITNESSES. The final package
checker adds a missing-sign-phase rejection control. Final package replay
is recorded separately below if executed. Metadata and publication checks
are separate gates, not mathematical premises.

After B confirmed the final bytes stable, I also executed from worker-e:

    python3 -I -W error -B research/four-axis-exact-square-period-obstruction/verify.py
    python3 -I -O -W error -B research/four-axis-exact-square-period-obstruction/verify.py

Both exited zero and emitted PASS_INDEX4096_OBSTRUCTION_WITNESSES with
the exact PROOF.md and verify.py hashes pinned above. All three controls
were present: malformed preimage, false image, and missing S phase. This
small deterministic replay corroborates the identities used by the proof;
it is not formal verification or a search establishing nonexistence.
