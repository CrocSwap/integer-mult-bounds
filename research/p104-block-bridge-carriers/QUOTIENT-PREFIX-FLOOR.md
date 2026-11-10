# Known prefix floors exclude the 54-incidence quotient census

**Verification consequence; no new κ.** Consider the exact eighteen-dimensional,
nineteen-query quotient in [the quotient support corollary](QUOTIENT-SUPPORT-COROLLARY.md).
Its eighteen full positions are 0,…,8 and 10,…,18; its sole thin position is 9.
Let P_i be an idempotent supporting full query R_i=x_i y_i on both sides.
Suppose the full-stage projectors commute pairwise and each P_i commutes with
its **actual chronological prefix** M_i=(I−2R_i)⋯(I−2R_0).
Work over any field of characteristic different from two.

Then the eight full positions

\[
\{2,4,6,8,10,12,14,16\}
\]

each require rank at least four, and

\[
\boxed{\sum_{\text{18 full positions }i}\operatorname{rank}P_i\ge60.}
\]

Consequently both eighteen rank-three stages and eighteen outputs each with
incidence degree three are impossible in this interface. The latter census
has total incidence54, below60 even if the individual stage ranks vary.
Rank60 is a necessary bound, not an attaining construction or a paid invoice.

## Relationship to known prefix bounds

The even-interior floor is inherited geometry, already stated in
CrocSwap/integer-mult-bounds#6717 at
`3c9072b8738323dda9f9c7dfb421d578ed3fc17a`, with credit to Ali Romman's
CrocSwap/integer-mult-bounds#6398. No new general prefix theorem or sharp total
rank bound is claimed here. The contribution of this appendix is an exact
source-bound transfer to this package's shortened quotient, together with
hypothesis controls and exclusion of the proposed 54-incidence census.

The at-most-two rank-two support theorem is already proved in Section 2 of
Ali Romman's #6398, without prefix commutation. The adjoining support corollary
reproduces it self-contained and identifies its exact source pins. Combining
it with the eight inherited rank-four floors gives the necessary total of 60.
No attainability or optimality at 60 is claimed.

## 1. Canonical coordinates preserve the required hypotheses

The source is DreamingOfClouds's CrocSwap/integer-mult-bounds#6833 at
`51f54e3c31f2f3a3e056a483b3ed66ae916ad06a`; the retained `chain_root.py` has
Git blob `ca1e0244f1329c153c1224b05bf0c0c5d5e2367b` and SHA256
`6f4046c804f27071d88ce05820c75baebe9cbf32533c4ba89285c413bfc8edaa`.
The adjoining corollary proves the exact quotient premise: nineteen nonzero
rank-one square-zero queries on eighteen independent coordinates, with
chronological product −I and thin query at position9.

For completeness, the scalar defect normalization is as follows. Stack query
columns X and rows Y, put G=YX and A=I+2 lower(G). Expansion of the product
gives XA⁻¹Y=I. Thus A−G has rank one and unit diagonal. Factoring it as uv
and gauging x_i↦u_i x_i, y_i↦u_i⁻¹y_i yields

\[
y_i x_j=\operatorname{sign}(i-j),\qquad y_i x_i=0.
\]

The first eighteen columns are a basis because their sign Gram is invertible.
In that basis,

\[
x_i=e_i\ (i<18),\quad
x_{18}=\sum_{j=0}^{17}(-1)^{j+1}e_j,\quad
y_i[j]=\operatorname{sign}(i-j).
\]

The factor gauges leave every R_i unchanged. An ambient basis change
simultaneously conjugates the queries, actual prefixes and supporting
projectors. It preserves rank, support equations and every commutator.
Therefore no coordinate or channel-mixing assumption is added by this normal
form. The exact source quotient already has the indicated Gram without
additional scalar gauges; the checker verifies all361 entries and the explicit
twenty-by-eighteen basis map for every query and prefix.

## 2. Eight actual prefixes force rank four

For even i with 2≤i≤16, put

\[
u_i=\sum_{j<i}(-1)^j e_j,\qquad
v_i=\sum_{j<i}e_j^*.
\]

Ordered multiplication of the canonical factors gives

\[
M_i x_i=x_i+2u_i,\qquad y_iM_i=y_i-2v_i.                 \tag{1}
\]

One direct derivation of the first formula applies positions0,…,i−1 to e_i:
successive additions are 2e_0,−2e_1,…,2(−1)^(i−1)e_(i−1). Their pairing
with y_i is zero because i is even, so the final factor leaves that column
unchanged. On rows, multiplying y_i from the right by the same descending
prefix factors gives y_i+2Σ_(j<i)(−1)^j y_j=y_i−2v_i.

Because P_i supports the nonzero rank-one query, P_i x_i=x_i and y_iP_i=y_i.
Commutation with M_i therefore forces P_i to fix the column space
C_i=span(x_i,u_i) and the row space D_i=span(y_i,v_i). Each has dimension two:
x_i is outside the nonempty head support of u_i, while y_i has a nonzero
tail beyond i that v_i lacks. Every pairing between these spaces vanishes:

\[
y_ix_i=v_ix_i=0,\qquad
v_i u_i=\sum_{j<i}(-1)^j=0,\qquad y_i u_i=0.
\]

The two rows of D_i remain independent after restriction to im P_i, since
D_iP_i=D_i. Their common kernel in that image contains the two-dimensional
space C_i. Thus dim im P_i≥2+2=4. This proves the local bound over every
allowed field; the division by2 used to extract the closures is legitimate.

All eight even interiors are full positions, namely L2,L4,L6,L8,R0,R2,R4,R6
in the retained source's arm notation. The thin position9 removes none of them.

## 3. Combine with the known rank-two support cap

Every supporting idempotent has rank at least two: it fixes a nonzero column
and row whose pairing is zero. The adjoining known support corollary shows
that at most two rank-two projectors can occur in a commuting family for
this defect-one root.

Its short geometric argument is worth recalling. In a common diagonal basis,
rank-two projectors have pairwise-intersecting two-element supports because
their cross-Grams are nonzero. Such a family is a star or lies in a triangle.
A star cannot have three distinct leaves: the ordered cross-Gram signs on
three queries would factor through the common hub and require the same
nonzero product to equal both1 and−1. Thus the support union has dimension
at most three. Any three selected columns and rows are independent, by extending to a
four-site invertible sign Gram. Their union cannot have dimension three, since
that would make the three-site Gram invertible, whereas S3 has rank two.
Repeated supports do not change the argument.

The eight even interiors contribute at least8·4. Of the remaining ten full
stages, at most two have rank two and at least eight have rank at least
three. Therefore the total is at least

\[
8\cdot4+2\cdot2+8\cdot3=60.
\]

In a joint diagonal basis, the sum of stage ranks equals the sum of output
incidence degrees. Eighteen outputs of degree three would total54 and violate
this necessary bound. An optimistic price for that census cannot be used as
an open constructive target under these hypotheses.

## 4. Exact source-bound replay and hypothesis controls

After placing the checker beside this appendix, run

```bash
python3.12 -I -B research/p104-block-bridge-carriers/verify_quotient_prefix.py
python3.12 -I -B -O research/p104-block-bridge-carriers/verify_quotient_prefix.py
```

Both return `PASS_QUOTIENT_PREFIX_RANK60`. For a lab copy, pass `--package`
with the package directory containing `retained/chain_root.py`.

The checker authenticates that source's SHA256 and Git blob, extracts only
its four pure constructor functions, and builds the exact9|9 source. It
derives the replacement middle query from the retained thin factors, verifies
the quotient Gram, transfers every source query and actual prefix through
an explicit basis, and checks both formulas(1) and the zero-paired closures
at each of the eight full positions. It also verifies both endpoint identities.

The omitted-prefix control is an actual rank-two idempotent supporting the
canonical query at position2 on both sides. Its commutator with that query's
actual prefix has rank two, and the prefix-compatibility gate rejects it.
Thus mere query support does not justify the local rank-four conclusion.
Separate controls reject uniform rank three and total incidence54.
Normal and optimized modes were both executed successfully.

This is a proof-based verification consequence, not a parameter search.
It does not rule out larger or noncommuting representations, changed query
words, additional restored state or a different recursive interface. No
attainability at60, favorable complete invoice, or κ improvement is asserted.
The prefix floors retain the scalar-header geometry credited to Ali Romman,
thu-nmrc (CrocSwap/integer-mult-bounds#6717), and the query-defect lineage;
the rank-two cap is the self-contained corollary in this package.

Prepared for @CubeJerry with substantial OpenAI GPT-6 Astra Pro assistance.
Base `7c49fe32c55de02c2c873655c804b16e4c3fef0a`. Apache-2.0.
