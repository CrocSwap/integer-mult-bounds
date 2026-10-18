# Sufficient coupled demotion and gap-consumption theorem

Assume the concrete checked alternate provider changes helpers 411/413/414/415 from width 4 to width 5, with exact local paid difference -8H1+8H2+4H3-4H4 and the same complete dirty-input maps. In a call choose four distinct existing width 4 role owners with pending remainders [1,1,1,r], r in {1,2,3}. The selected provider roles and those donor role occurrences partition into common/self occurrences and external occurrences. Fix common occurrences and bijectively exchange external ones within that call; this preserves one occurrence of every role and per-call family uniqueness. Increasing the selected widths consumes one axis in each donor owner. Fit follows from the specified positive remainders. Compact chronological offsets then establish disjoint axes for every actual pending owner.

The complete paid changes, including the remainder bill, are:

- r=1: -12H1+8H2+4H3-4H4;
- r=2: -10H1+7H2+4H3-4H4;
- r=3: -11H1+9H2+3H3-4H4.

These three changes strictly reduce the recursive moment for every 0 < b < 1. This is a sufficient improvement theorem, not only a necessary packing condition.

Proof of strict inequality: Set alpha=1-b, u=2^alpha in(1,2), p=ln(3)/ln(2). We have 14/9 < p < 2 because 3^9 = 19683 > 16384 = 2^14 and3 < 4. Removing the common positive factor73^b, the three moment changes are

h1(u)=-12+8u+4u^p-4u^2,
h2(u)=-10+7u+4u^p-4u^2,
h3(u)=-11+9u+3u^p-4u^2.

For u >= 1, p(p-1)u^(p-2) < 2. Thus h1''=h2''<0 and h3''<0. At u=2 their slopes are 6p - 8,6p - 9,9p/2 - 7, all strictly positive. Their derivatives on [1,2] are therefore positive, while h1(2)=h2(2)=h3(2)=0. Each h_j(u)<0 for u<2. Multiplying by73^b proves the universal strict moment saving. Every profile difference has zero rank mass; the local four-axis mass increase is exactly consumed by four fewer unclaimed axes.

## Actual construction, frozen PR1117

Before this coupling, an independently checked three-cycle concentrates two rank 6 pending remainders into rank 1 and rank 11, delta +H1-2H6+H11. New owner hash a6c2885268cfc5d7591d77494c099c7225904f88f0b97a24567e0e51c9d3c6fc. This concavity improvement holds for every 0 < b < 1.

Starting that map, the coupled construction changes 103 of 144 calls:100 four-unit patterns, one rank 2 and two rank 3. Final whole paid profile:

{1:347435,2:63049,3:61831,4:20036,5:11808,7:8,8:1152,11:2,48:4873}.

Rank mass 1041408 and deficit 5120 are unchanged. 1500 literal rows change relative to the checked three-cycle map; final root must independently audit mixed widths, actual orthogonal charts, phase validity and finite invoices before assigning an admitted kappa. The literal map, exact dispatch and complete before/after row edits are in `demote-many2-1117/`. No gains from different PRs are added numerically; the profile is recounted from the actual combined assignment.

The finite provider correctness belongs to the cells worker's exact 704-column forward/dual/low-end-cone replay. The owner lane checks replacement geometry; the recurrence lane independently checks all mixed 69,120 roles. Root prices and packages the combined result. Full inherited all-size, compiler, precision/recovery and analytic conditions remain explicit.
