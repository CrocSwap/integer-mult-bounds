# The extra query prevents a complete-tree improvement

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI Codex assistance.
Apache-2.0. This note uses the explicit caller in [PROOF-CALLER.md](PROOF-CALLER.md),
and credits the native invoice and two-fragment root of
CrocSwap/integer-mult-bounds#6726. It proves a scoped all-size bound, not a
universal obstruction to other recursive callers. **No new κ.**

The existing fork package at
[`d87e4a38890f6962162d00a68031ab2476f58f6e`](https://github.com/CubeJerry/integer-mult-bounds/tree/d87e4a38890f6962162d00a68031ab2476f58f6e/research/four-query-fragmentation-ceiling)
already establishes this mixed-tree exclusion and the corresponding BIT
ceiling. This note independently verifies the COMPLEX case using a distinct
directed-square-root arithmetic engine and the source-bound shorter caller.
It does not claim first proof of the all-size result. See
[CONCURRENT-WORK.md](CONCURRENT-WORK.md) for the exact comparison and credit.

## 1. Exact class and conclusion

Keep the six-full-site, two-paid-fragment root of #6726 fixed. Its six positive
child sizes may vary arbitrarily. Within each child allow any binary tree whose
internal nodes use either the original three-query binary caller or our explicit
four-query equal-orientation caller. Keep the pinned native tariffs, independently
paid whole-body idles, root retirements, and disjoint child/helper contracts.
There are no cross-node shared transforms or new native primitives.

For κ in `[0.00330720, 0.004]`, every such tree with at least 50 native leaves has
negative complete moment margin. For at most 49 leaves, replacing any old node
by the new node strictly decreases the margin. An independent exact replay of
the remaining 44 total sizes proves that none has nonnegative margin at

    κ* = 0.0033072446849.

This is the upper endpoint of the preceding root's raw crossing interval.
The maximal finite-tree margin at κ* occurs at 18 leaves and is below
`−1.01790666829957 × 10^−10` per port. Thus this explicit new caller cannot
raise that raw ceiling anywhere in the stated κ interval. The result does not
assert that every four-query implementation has our idle invoice, or cover
different roots, negative body powers, changed source access, cross-node sharing,
or κ outside the stated interval. No claim is made that the pending #6726 bound
is the selected result; the selected record at the pinned base remains unchanged.

## 2. Complete recurrence

Put `t=1−κ`, `h(r)=r^t` and

    i(n) = h(8n+1)−h(8n),
    ell = (sum_r H_r h(r)−sum_r P_r h(r))/104.

`H` and `P` are the literal `HELPERS` and `LOCAL_PAID` inventories in the pinned
#6726 pricing source. They include the inherited native invoice; this theorem
does not reprove that native construction or any of the five framework assumptions.

After its children have been priced, an old node with `n` leaves contributes
`2i(n)−1` per port. Our new node, with the same orientation assigned to a child
of size `j`, contributes `2i(j)−2`. The second unit is the additional thin query.
The optional two fresh suffix-only fields contribute equal target and paid
body moments and cancel exactly; omitting their complete independent jobs gives
the same four-register invoice.

Let `D(n)` be the sum of internal-node contributions in a chosen n-leaf tree.
For six positive sizes `(a,b,c,d,e,f)` with total `F`, the complete root margin,
divided by 104, is

    F ell + D(a)+D(b)+D(c)+D(d)+D(e)+D(f)
      + h(8F+1) + h(8(a+b+c)+1) + h(8(d+e+f)+1)
      + i(b+c) + i(c) + i(d+e) + i(d) − 2.                 (1)

This identity holds symbolically for arbitrary positive child sizes. In the
retained `ROOT.json` from #6726, the six full stages A through F have masks
`[3,195,195,53,53,5]`, respectively. Reading each field's bit across these masks
gives the following body factors, with one header S on every output:

| Field | Body factors before the two fragment retirements |
|---|---|
| 0 | ABCDEF |
| 1 | ABC |
| 2 | DEF |
| 3 | identity |
| 4, 5 | DE |
| 6, 7 | BC |

The child body ranks are `8a,...,8f` on disjoint axes, so the first three
fields give the three h terms in (1). Full stages B and C each pay two idle
directions that jointly produce the two BC fields; stages D and E similarly
pay the two DE directions. One BC field retires as plain B plus SC, giving
`i(c)` after cancellation of the independently paid body work. The other
gives `i(b+c)`. One DE field retires as SD plus plain E, giving `i(d)`;
the other gives `i(d+e)`. There are nine root queries, six of them full,
so the three thin queries cost three units per port. Field 3 contributes
one unit, leaving the constant `−2`. This derives (1) from the mask schedule
and the two stated retirement cuts; it does not infer the general formula
from a single numerical invoice.

The verifier authenticates the complete retained root and checks its mask
supports, full sites, and stage ranks. It also reconstructs the complete
signed rank histogram for the retained
`(4,4,1,1,4,4)` construction and checks literal equality with the frozen
`RESULT.json` targets minus paid calls. All 18 native invoices, 15 thin queries,
and root/internal-body jobs are consequently accounted for. The arithmetic
result is conditional on the original invoice's physical validity; it does not
replace the native and physical reviews.

## 3. Small trees: a strict local comparison

For `1<=n<=49` and `0<κ<=1/250`,

    i(n) = (1−κ) integral_0^1 (8n+s)^(-κ) ds
         > (249/250)(4/5) = 498/625 > 1/2.

The elementary integer inequality `393*4^250 < 5^250` proves the middle bound.
For every positive child size `j`, `i(j)<1`. Therefore

    (new node) − (old node) = 2[i(j)−i(n)]−1 < 0.          (2)

Replacing a new node by the old node preserves the child main-port boundary.
Its own productive auxiliary contract is priced separately in (1), so this is
a valid invoice comparison throughout the defined recursive class. Every
augmented tree of size at most 49 is dominated by its all-old counterpart.

The inequality is deliberately limited to small trees. For example, at
`κ=1/8`, body ranks `a=8`, `b=8*2^80` give a strictly positive local difference
of more than `0.3380379`. The verifier retains this positive control. The
negative conclusion comes from the complete tree, not a false universal claim
that equal-orientation fragmentation always loses locally.

## 4. Large trees: a uniform concave envelope

Write `A=2i(2)−1`. It is positive on the stated interval. An old internal node
has size at least two and contributes at most A because i decreases. A new
node contributes `2i(j)−2<0<A`. Hence every n-leaf augmented tree satisfies

    D(n) <= (n−1) A.

Concavity of h and `i(n)<=i(1)` bound (1) by

    B(F) = F ell + (F−6)A + 4i(1)
           + h(8F+1) + 2h(4F+1) − 2.                   (3)

This is concave as a function of real F. At `κ=0.00330720`, outward exact
interval arithmetic proves

    B(50)  < −0.9087944989967202,
    B'(50) < −0.0511981106830088.

The derivative used is
`ell+A+8t(401)^(-κ)+8t(201)^(-κ)` at F=50. Thus B(F)<0 for all F>=50.

The same bound holds throughout the κ interval. Every positive h term and
every i term decreases with κ here: the integral for i has a strictly
decreasing positive integrand. It remains to justify that ell decreases,
despite its signed native histogram. Let `c_r=H_r−P_r`, whose ranks lie in
`1,...,9`. The exact inequality `9*32^250 < 33^250` gives
`r^(1−κ) >= 32r/33`. Therefore

    ell'(κ)/log(2)
      <= [sum_(c_r<0) (−c_r) r ceil(log2 r)
          −sum_(c_r>=0) c_r (32r/33) floor(log2 r)]/104
       = −24273/572 < 0.                                (4)

Only integer bit lengths and rational arithmetic are needed for this bound.
Equations (3)–(4) propagate the large-tree exclusion from the lower endpoint
to the full stated interval.

## 5. Exhaustive finite recurrence

At κ*, maximize all-old children by the exact dynamic program

    d(1)=0,
    d(n)=max_(1<=j<n)[d(j)+d(n−j)] + 2i(n)−1.

For a three-child half-root define

    x(n)=max_(a,b,c>=1; a+b+c=n)
           [d(a)+d(b)+d(c)+i(b+c)+i(c)].

Reversing the order of `(d,e,f)` expresses the second half of (1) in the
same form. For each F=6,...,49 the exhaustive maximum is

    F ell+h(8F+1)−2
      +max_(3<=u<=F−3)[x(u)+x(F−u)+h(8u+1)+h(8(F−u)+1)]. (5)

The verifier covers all 1,176 binary splits up to size 49, all ordered positive
triples needed by (5), and all 44 totals. Every resulting upper endpoint is
negative. Equation (2) extends this conclusion to all allowed augmented trees.
For each fixed tree, its complete expression decreases with κ by the same
termwise argument and (4), so no omitted larger κ within the interval helps.

## 6. Independent arithmetic and failure controls

`verify_economics.py` does not import the predecessor's logarithm/exponential
interval engine. With scale `S=2^256`, repeated directed integer square roots
enclose `n^(1/2^j)` for j=1,...,192. The exact rational κ is bracketed by its
two adjacent 192-bit binary fractions. Directed products enclose `n^κ`;
directed reciprocal multiplication by n encloses `h(n)`. All subsequent sums,
rational products, and maxima retain both outward bounds. Decimal strings in
the receipt also use outward rounding. Signs are decided on the exact scaled
integer endpoints, not on printed decimals or floating point.

The six exact-power fixtures include both binary and nonbinary rational
exponents. The frozen construction has positive margin at the admitted lower
value and negative margin at κ*. A deliberately omitted thin query changes the
signed invoice and is rejected. Its falsely free local formula is positive
even at a small tree, demonstrating why that charge matters. The extreme-size
positive control prevents overstating the local obstruction. The frozen input
files are SHA256-bound, and all checks use explicit exceptions rather than
assertions, preserving coverage under `python -O`.

Run from the repository root:

```sh
python3 -B research/binary-equal-orientation-fragments/verify_economics.py
```

Expected marker: `PASS_EQUAL_ORIENTATION_COMPLETE_TREE_CEILING`.

## Open next questions

The next useful mechanism must change an excluded part of the model: the native
invoice, the root, an interface permitting shared body work, or the physically
paid idle contract. An arbitrary four-query implementation is not proved to
need this idle bill. A concrete alternative should first give its exact whole-
matrix boundary and complete recursive invoice; another unpriced local gain
does not address the obstruction above. The exact changed caller also remains
available as an algebraic building block where a different complete invoice
makes its positive local regime relevant.
