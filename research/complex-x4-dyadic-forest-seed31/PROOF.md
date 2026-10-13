# All-dyadic single-parent forests for the pinned X4 compensation

This note extends a restricted cost comparison for the exact historical PR799
X4 compensation matrix. It does not assert a new supplier, a new exponent, or
a lower bound for arbitrary circuits. The finite census and the universal
coefficient reduction are distinct parts of the argument.

## 1. Exact circuit class and price

Write the pinned compensation as

```text
(y,h) -> (y+C h,h).
```

There are 112 target rows and 216 used helper columns. The source checker must
establish that all 6,320 nonzero matrix entries are a/4 with
`a in {-4,-3,-2,-1,1,2,3,4}`, and that the pinned panel is in the inherited
zero frame. Targets, helpers, and private work start with arbitrary inputs.

For a nonzero reduced dyadic q=n/2^d, where d>=0 and n is a nonzero integer,
the unchanged independent binary-Horner coefficient price per real component is

```text
H(q)=3+floor(log2(abs(n)))+popcount(abs(n))+d;  H(0)=0.
```

This charges initial work clearing, numerator doublings and source additions,
denominator halvings, signed accumulation, and final work clearing. In
particular H(-q)=H(q), H(1)=4, and all nonzero coefficients have positive price.
Put R(v)=sum_t H(v_t).

Choose any rooted forest on the target labels. Each nonroot i has one parent
p(i) and a nonzero dyadic coefficient lambda_i. Prepare with

```text
y_i <- y_i-lambda_i*y_p(i)
```

in leaf-before-parent order. Thus every child uses its parent's original input,
and the preparation matrix T has row e_i-lambda_i*e_p(i) at each nonroot and
e_i at each root. No ancestor terms occur. T is unit triangular in a forest
order. Compensate with rows TC, then restore the shears in reverse chronological
order. For arbitrary inputs, the endpoint is

```text
T^-1(Ty+TC h)=y+C h.
```

A root i costs R(C_i). A directed child-parent relation i->j costs exactly

```text
E(i,j,lambda)=R(C_i-lambda*C_j)+2H(lambda).
```

The complete forest cost is the sum of these local prices. The two boundary
shears are paid independently. Children use the original compensation row
C_j in this formula even when j itself has a parent.

This class fixes the preparation order, independent coefficient lowering,
public boundary, and source matrix. It excludes shared coefficient work,
multiple parents, helper-basis changes, and arbitrary sequential basis changes.

## 2. Universal reduction to a finite dyadic core

Every original quarter entry has price at most eight: the four nonzero
magnitude prices H(a/4), for |a|=1,2,3,4, are 6,5,8,4 respectively.

First let lambda=s*m/2^k be reduced, with m positive odd, s in {-1,+1}, and
k>=4. An entry of the transformed row is

```text
q=(a*2^k-s*m*b)/2^(k+2),  |a|,|b|<=4.
```

If b=0 its price is unchanged. If b!=0, the numerator has valuation v2(b)<=2:
the first summand, when nonzero, has valuation at least k>=4, and the second
has valuation v2(b). This also holds directly when a=0. Consequently the
numerator is nonzero and its reduced denominator exponent is
k+2-v2(b)>=k>=4. A nonzero dyadic with denominator exponent d costs at least
4+d, so H(q)>=8. Every coordinate therefore costs at least its original price.

Second let |lambda|>=68. For b!=0,

```text
|(a-lambda*b)/4| >= (|lambda|*|b|-|a|)/4 >=16.
```

For reduced q=n/2^d with |q|>=16, we have floor(log2|n|)>=d+4, and hence
H(q)>=3+(d+4)+1+d>=8. Coordinates with b=0 are unchanged. Again no coordinate
is cheaper than its original price.

Both cases give E(i,j,lambda)>R(C_i), since the two shears have positive price.
They cover every nonzero dyadic outside the finite set

```text
Lambda={n/8 : n=-543,...,-1,1,...,543}.
```

Indeed, a remaining coefficient has reduced denominator exponent at most three
and magnitude strictly below 68, so lies on this eighth grid. Lambda contains
exactly 1,086 signed coefficients, including both signed units. These are
universal tail proofs; finite samples of large coefficients are unnecessary.

## 3. The finite inequality that is actually needed

Define the best same-parent signed-unit or root alternative by

```text
B(i,j)=min{R(C_i), E(i,j,+1), E(i,j,-1)}.
```

The primary and independent finite censuses verify

```text
E(i,j,lambda)-B(i,j)>=0
```

for every ordered distinct pair i,j and every nonunit lambda in Lambda.
There are 112*111=12,432 ordered pairs, 13,501,152 records including units,
and 13,476,288 nonunit records. All prices and comparisons are exact integers.

It would be incorrect to replace B(i,j) by the root price in this claim.
The primary finite census finds 970 nonunit directed edges cheaper than their
root alternative, with a minimum root margin of -56 per real component at
lambda=3, child 137, parent 191. This is the minus convention used above.
Such an edge is nevertheless dominated by a signed-unit relation to the same
parent. Both independent implementations reproduce these numbers. The minimum
finite-core margin E-B is **56**, attained by lambda=2 at child 125, parent 139;
there are no nonunit ties or improvements. This 56 margin is a finite-core
result, not a claimed uniform margin on the infinite tails.

Nor does the desired finite inequality follow from the quarter alphabet
alone. For a synthetic panel consisting of many repeated entries
C_i=3/4 and C_j=1/4, lambda=3 cancels the child row and eventually beats both
unit alternatives despite its larger shear bill. The actual X4 matrix is
therefore essential to the finite certificate.

## 4. Exchange lemma and the all-dyadic forest optimum

The verified inequalities in Section 3 now apply. Consider any nonunit edge
of any forest in Section 1. Outside Lambda it is strictly dominated by making
its child a root, by Section 2. Inside Lambda choose the cheapest alternative
in B(i,j).

If a signed unit is cheapest, keep the SAME directed child-parent relation and
change only its coefficient to that unit. The forest topology remains valid.
If the root is cheapest, delete the edge and make the child a root. Deleting
an edge preserves acyclicity. Its entire descendant subtree stays attached,
and every descendant keeps the same original parent compensation row and the
same local price. In either case only the selected edge's local price changes,
and the complete bill does not increase. Each resulting forest has valid
leaf-before-parent preparation and reverse restoration orders.

Repeat this operation for every nonunit edge. It converts an arbitrary dyadic
forest into a signed-unit forest of no greater cost. Signed-unit forests are
a subclass, so the two class optima are equal. The strict finite and tail inequalities also imply that
no optimizer in this exact class contains a nonunit edge.

The same source matrix has an exact signed-unit superroot spanning-tree floor
of **10,883 primitives per real component**, independently rechecked here.
Together with the verified finite inequalities, the exchange lemma extends
that floor to the entire single-parent dyadic forest class. The corresponding
complex-stream panel price is **21,766 real primitives** after charging both
real components. An existing signed-unit forest attains the floor; no new
emitted candidate is required by this exclusion.

For nonunit coefficients E(i,j,lambda) need not be independent of orientation.
It would therefore be invalid to apply the signed-unit undirected MST reduction
directly to arbitrary dyadic edges. The exchange lemma removes the nonunit
edges before using that established symmetric graph certificate.

## 5. Limits and inherited obligations

This is a finite, source-specific optimum under a prescribed lowering and
forest schedule. General overlapping or sequential shears can create ancestor
terms, so their transformed-row costs need not have the local form used here.
The argument excludes neither those circuits nor multiple-parent systems,
helper-basis changes, coefficient sharing, cheaper scalar lowering, or folding
boundary work into adjacent phases.

Logical inverse-transposition swaps source and target and negates each shear
coefficient while retaining chronological order; H is sign invariant, so the
same local coefficient bill applies. This cost argument does not invert or
transpose private-work CLEAR primitives. Any new circuit would need its own
full boundary, private-work, prefix, and geometric checks in both orientations.
The existing attaining signed-unit candidate keeps its own inherited checks.

No new prefix, precision, all-size, physical, hosting, compiler, analytic,
integer-multiplication, or kappa theorem is claimed. The unchanged supplier's
assumptions remain. The construction mechanism and signed-unit graph floor
are inherited from the cited restored-target-pair and target-forest work;
this note's added result is the all-dyadic finite reduction and matrix-specific
edge-replacement certificate within that class.

## 6. Predecessors and implementation scope

Credit Ross Richardson [PR932](https://github.com/CrocSwap/integer-mult-bounds/pull/932)
for the X4 signed-unit forest and its attained floor; ToikY
[PR909](https://github.com/CrocSwap/integer-mult-bounds/pull/909) for the prior
signed-power-of-two disjoint-pair exclusion; and the restored-pair/forest
lineage credited in [PR932’s proof](../complex-x4-target-forest/PROOF.md).
The primary census uses Fraction prices and Kruskal; the separately implemented
checker uses integer reduction, literal Horner-word lengths and dense Prim.
Both read the same immutable source, but neither imports the other checker.
Shared input pins and mathematical specifications are intentional. These are
independent implementations with AI assistance, not independent human review.
