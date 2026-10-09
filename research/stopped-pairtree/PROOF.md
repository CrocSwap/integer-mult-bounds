# Conditional stopped pair-tree refinement

The selected statement is

`T(n) = O(n (log n)^(1−κ))`,

with **κ = 7808981744031/100000000000000000** under all the inherited
analytic/fixed-tape interfaces and PR104's newly proposed stopped-product
interfaces. This section records the changed finite construction and the
composition obligations; it does not convert those interfaces into a fully
formalized theorem.

## 1. Explicit finite graph and matching

The preserved input is Rohan Arun's PR107 at
`b06b82a456409968ae3f2c6765ae63c3f0343548`, including its icekylinx PR104
proof lineage. All 330 original selected source fingerprints and the source
manifest itself are archived as original Git blobs. Prior notices, licenses
and AI-assistance disclosures remain intact.

For each pair {a,b}, the pair-star leaves are the distinct triple inputs
{a,b,i}. The selected order is the original forward aligned order. Split
each tree at the largest power of two strictly smaller than its leaf count.
Store the sum of each subtree. A downward traversal carries the sum outside
the current subtree, adding the sibling sum at each step. At a leaf the
carried value is precisely the requested pair-star sum excluding that leaf.
Every addition is disjoint, preserving its exact scalar support and the
nondegenerate binary span of shared-pair triple indicators.

The existing legal carrier matcher first produces a maximum-cardinality
matching. A bounded exchange pass uses a fixed 25-entry integer rank-price
table to choose free-use reassignments, replacements of donors and two-donor
swaps. Every exchange preserves cardinality and checks the original operand,
order and frame-inclusion predicates. The table is a discovery objective;
the accepted exponent is obtained from the fully rebuilt child histogram.
The chosen run performs 604 exchanges, then makes no further change.

The acceptance gate independently checks all 7,194 actual matching edges
using the serialized binary subspaces, not only their type labels or count.
It recomputes every removed and added rank charge and every resulting child
multiplicity. In addition, the literal role program is reconstructed and
checked. The full graph has 44,340 additions and 8,120 roots, so
`R = 44340+8120−7194 = 45266`.

The unchanged retained centers satisfy `sum_i A_i = 21 sum_T x_T`.
Their exact rational scatter, together with the disjoint and intersection-two
outputs, has coefficient one on the diagonal and zero off it. All 2024²
coefficients are checked. If L is the invertible middle word, V its injection
and J its signed readout, this proves `JLV=I`. The transparent old-value
subtraction and new-value addition obey

`JL(z+Vx)−JLz = x`

for arbitrary old role values z; inverse additions restore those roles.
The retained matching/word construction and signed two-stage endpoints
therefore apply to this new DAG. Both data connectors, copied centers,
inverse rank-one correction, sign wrappers and divisor 21 remain paid.
See [physical-proof.md](physical-proof.md) for the complete local argument.

## 2. Stopped ordinary bit interface

The coarse bit and ordinary leaf inputs are unchanged from PR104/107.
A common rational basis and opposite bank orders turn every proper
projector residual into one reversed contiguous child. The complete
factorization includes its complementary diagonal blocks and physically
lower adapters; discarding either is invalid.

Atoms are fixed-width product-ring components within one recursion.
Each adapter is a paid atom loop. Stopping at atom exponent `ν = 1/1000`
and using the inherited ordinary leaf with saving `384599/10^10` gives

`a_ordinary = (1−ν)(4019/50000000) + ν(384599/10^10)`

`= 803380799/10000000000000`.

Both the coarse rank moment and its exponent moment contract. The adapter
condition `ν > a_ordinary` is strict. Peeled remainders and incomplete atoms
use the retained ordinary leaf. A constant outer word containing two
sequential reversed calls and three lower updates returns ordinary
interchange on complete rows and spectators. Its constant multiplicity is
outside the recursive moment. `interface_check.py` checks full finite
matrix identities, lower orientation, atom-ring basis/carry examples and
the ordinary wrapper, with rejecting controls. The corresponding all-size
ordered-affine streaming cost remains the stated proof dependency.

## 3. Rational centers and precision

For the selected complex network:

- `m=576`, `v=2024`, `N=4096576`, `R=45266`, `W=191429920`.
- Copied-center loss `L=2234496`.
- `s=Wm−N+L=110261771840`; the largest child is 552.

The complete histogram contains auxiliary exteriors, both data macros,
all actual internal transitions, data fronts and rank-one endpoint copies.
The independent checker rebuilds each class; no child is inferred by
subtracting rank to force a desired deficit.

Unfinished complex values use one exact grid with odd factor `21^K`,
`K=G0(D+1)`, on the active unfinished chain. Completed children are exact
dyadic tensor operators and preserve the incoming odd-denominator exponent.
Reachable root-dyadic states supply the required divisibility; arbitrary
numerators on the finest grid are not assumed divisible. There is no child
return rounding. Outer scaling/unscaling restores dyadic encoding.

The selected scalar charge is `G0=1633627072`. The literal charge,
`E=64(W+m+G0+1)^3`, `B=s+E`, `C0=32mB²`, and completed-child induction
are regenerated. The common-grid overhead adds only the retained lower-order
outer work and logarithmic record allowance, preserving `C1=1` under the
same hypotheses.

## 4. Three nested row reserves and balanced assembly

The row field reserves the product of complex, coarse-bit and ordinary-leaf
stocks. Its exact coefficient is

`17·28 + 16·28 + 9·28 = 1176`.

Degree 4000 has positive gap `4000−(51/25)·1176 = 40024/25`, and suffix
slope 16000. A two-factor validator would omit a live nested reserve and
is rejected. Sequential outer wrappers restore and reuse this row field.

The completed ordinary interface supports the PR34/PR100 common positional
layout and paid arbitrary-coordinate router. Its prefix work margin is
`1−ε`; the distinct geometric constraint `1−ε(1+c)>0` remains necessary.
The balanced transfer does not reorder unfinished local network operations.
See [balanced-transfer.md](balanced-transfer.md) for the interface review.

The complete complex moment accepts the exact saving

`b = 4880994746013/62500000000000000`

and rejects its next `10^-18` grid point. Primary and independent rational
log/exponential enclosures agree. With `β=10^-12`, positive backoff `10^-18`,
and `a=min(a_ordinary,(1−β)b−10^-18)`, all 47 strict constraint slacks are positive, and all seven
cost margins exceed the selected κ. Its next `10^-18` grid point is rejected.
The arithmetic gate also rejects ten deliberately corrupted certificates.

## 5. Attribution and limits

The new pair-star tree, deterministic integer-weighted exchanges and combined
verification were prepared for Thomas DiFiore with substantial OpenAI Codex
assistance. **icekylinx** supplies the stopped factorization, atom interface,
rational-center construction and inherited ordinary leaf lineage.
**Rohan Arun** supplies the PR107 comparison, exact refinement precedents and
the PR100 application of the **James Chang / PR34** and **RaD / hipotures**
balanced layout. **Zhihao Chen** supplies the retained semantic/bulk and
two-stage interfaces; **Aurel Prosz / Paureel**, **Swapnil Jain**,
**eumemic**, **Dominik Scholz** and all preceding contributors remain credited
in the original notices. **Douglas Colkitt**, **OpenAI**, **David Harvey** and
**Joris van der Hoeven** retain the framework and analytic-work credits.

The finite graph audits and algebra controls do not prove the full streaming,
analytic, prime-existence, recovery or all-size tape hypotheses. The result
is conditional on those retained and newly proposed interfaces. This is not
a practical speedup, a proof of global optimality or independent human review.
