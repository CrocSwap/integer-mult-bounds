# CK forests with arbitrary dyadic parent weights

This is a source-specific scalar cost result, not an integer-multiplication
lower bound. The forest mechanism and signed-unit optimum are PR816's work.
The finite reduction and same-parent exchange method follow concurrent PR961
on its different X4 matrix. The evidence here is an independently computed CK
census, corroborating Adam Gall's concurrent PR1220 discovered at final refresh.

## Interface and complete price

The pinned PR626 CK compensation is `(y,h) -> (y+C h,h)`. There are 112
targets, 254 used helper columns and 8,704 nonzero entries. Every entry is
`a/4` with `a in {-4,-3,-2,-1,1,2,3,4}`. Source and target registers are
disjoint and all these operations and entrance frames are zero. These facts
are checked from the immutable canonical word and its selected historical SPEC.

For nonzero reduced dyadic `q=n/2^d`, use the inherited independent binary
Horner price

```
H(q) = 3 + floor(log2 |n|) + popcount(|n|) + d; H(0)=0.
```

The three fixed operations are initial private-work clearing, signed target
accumulation and final clearing. Every source addition, numerator doubling
and denominator halving is charged. Each price is for one scalar component;
two real components of a complex register cost twice this number. PR816
calls these component prices its complex-primitive bill. This note does not
substitute PR696's cheaper lowering, share work, or silently omit clears.

For each nonroot target i, choose one parent j and nonzero dyadic lambda.
The directed parent graph must be a forest. Prepare `y_i -= lambda*y_j` in
leaf-before-parent order, so parents still carry their original target data.
The resulting matrix T has row `e_i-lambda*e_j`. Add `TC h`, then reverse
the preparation with negated coefficients. The exact endpoint is

```
T^-1 (T y + T C h) = y + C h.
```

This holds for arbitrary target and helper dirt; helpers are never changed in
the forward panel. T is unit triangular in a forest order. With
`R(v)=sum_k H(v_k)`, each root costs `R(C_i)` and each directed edge costs

```
E(i,j,lambda) = 2 H(lambda) + R(C_i-lambda*C_j).
```

Both preparation and restoration shears are paid. Descendants use the ORIGINAL
parent row C_j, even if that parent itself has a parent. There are no new
helpers, frame transitions, copied target registers or recursive children in
this class. Unchanged work outside the panel contributes the same bill to
every comparison. The result concerns this fixed scalar price, not a fresh
global compiler invoice or admission of an alternative recursive supplier.

## Infinite tails reduce to 1,086 coefficients

The original magnitude prices H(a/4), a=1,2,3,4, are 6,5,8,4; thus every
original coordinate costs at most eight.

Let lambda=s*m/2^k be reduced, m positive odd and s a sign, with k>=4.
For a parent quarter numerator b!=0, the residual is

```
(a*2^k-s*m*b)/2^(k+2).
```

The numerator has 2-adic valuation v2(b)<=2, because its two summands have
distinct valuations; this also holds when a=0. It is nonzero and its reduced
denominator exponent is k+2-v2(b)>=4. Consequently its H-price is at least
4+4=8. When b=0 the original coordinate is unchanged. Summing coordinates
and adding both positive-cost shears gives E>R(C_i).

For |lambda|>=68 and b!=0,

```
|(a-lambda*b)/4| >= (|lambda|-4)/4 >=16.
```

A reduced q=n/2^d with |q|>=16 has floor(log2|n|)>=d+4, and therefore
H(q)>=3+(d+4)+1+d>=8. Again coordinates with b=0 are unchanged, and E>root.

Every remaining nonzero dyadic has denominator exponent at most three and
magnitude below 68. It therefore belongs to

```
Lambda = {n/8 : n=-543,...,-1,1,...,543}.
```

These arguments prove the two infinite-tail exclusions; no finite replay of
large coefficients is represented as a proof of an infinite domain.

## CK-specific finite certificate

For each ordered pair i!=j, define

```
B(i,j)=min(R(C_i), E(i,j,1), E(i,j,-1)).
```

The two implementations enumerate all 1,086 coefficients and 112*111=12,432
ordered pairs: **13,501,152** exact edge prices, including **13,476,288**
nonunit comparisons. Histograms group equal quarter-numerator pairs; the
independent checker additionally identifies (a,b) with (-a,-b), which preserves
every sign-invariant H-price. All ordered cases are retained in the census
digest and multiplicities.
There is no stochastic cutoff or sampled pair subset.

The minimum nonunit `E-B` is **63**, attained four times. One witness is
child 123, parent 125, lambda=-3: E=453 and B=390. The complete receipt records
the domain, extrema, multiplicities, exact digest and an attaining unit tree.

**941 nonunit edges beat their root.** The minimum `E-root` is -116 at
child 114, parent 184, lambda=-3: E=353 versus root 469. Thus extending PR964's
power-of-two root-domination statement directly to all dyadics would be false.
The same-parent signed-unit alternative is essential. These are improving
edges relative to a root, not an improved complete forest or new supplier.

The quarter alphabet by itself does not imply finite dominance: two repeated
coordinates C_i=3/4 and C_j=1/4 have root 16, unit prices 18 and 16, but
E(i,j,3)=12. This adverse control must exhibit a negative margin (-4).
It guards against a checker that assumes its intended negative result.

## Forest exchange and the retained optimum

Take any nonunit edge in any admissible dyadic forest. If outside Lambda,
delete it, making its child a root, which strictly reduces its price. If
inside Lambda, choose the minimizing alternative in B: either delete the
edge or keep the SAME child/parent relation with coefficient +1 or -1.
Topology remains acyclic. The descendant subtree remains attached, and all
other local costs are unchanged because they depend on original parent rows.
The replacement has its own valid leaf-before-parent schedule and reverse
restoration. Repeating strictly decreases cost until all edges are units.

For signed units only, edge prices are symmetric, since
`C_j-s*C_i=-s*(C_i-s*C_j)` and H is sign invariant. The standard superroot
MST reduction then applies. The primary checker constructs a tree and checks
all 12,544 signed/root cycle inequalities. The independent checker uses Prim.
Both obtain **16,364 per scalar component**, or **32,728 real-component
primitives for the complex panel**. An existing signed-unit forest attains
this number, so the all-dyadic optimum is equal. Every optimizer in this
specific class has only signed-unit edges. The finite margin 63 is NOT claimed
as a uniform lower margin across the infinite tails.

Do not run an undirected MST directly on nonunit edges: their prices need not
be orientation symmetric. The exchange argument removes them first.

## Limits

This result fixes the CK matrix, one-parent acyclic preparation, clearing after
every coefficient, original binary-Horner lowering and separate boundary
shears. It excludes neither multiple parents, arbitrary sequential target
bases, helper-basis changes, shared coefficient work, other lowerings nor
folding work into neighboring phases. It closes PR964's non-power-of-two
coefficient gap only under this fixed model.

Logical inverse-transposition swaps target/source and negates each shear;
H is sign invariant, so the component bill is unchanged. It does not mean
transposing noninvertible private CLEAR instructions. The unchanged attaining
unit construction retains PR816's own scalar/precision checks; its independent
boundary verifier was replayed for this contribution. No new precision bound,
physical frame/phase replay, hosted supplier, global invoice, outer assembly,
or kappa certificate is issued. Inherited all-size/compiler, common-label and
mutable-source realization, whole-call hosting, precision/tape/recovery,
analytic transfer and bit H1-H5 obligations remain. This is not a formal
proof of the complete multiplication theorem or independent human review.
