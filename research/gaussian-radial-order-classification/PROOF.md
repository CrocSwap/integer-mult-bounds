# Finite order has a strict radial cost for exact-sum Gaussian rounding

Let `C_+(x,y)=((s+i*d)/2,(s-i*d)/2)`, with s=x+y and d=x-y.
Use the Euclidean norm on Gaussian-integer pairs. A map is admissible if
it is injective, preserves s exactly and has error at most one from C_+
at every input. Write Delta for its forward outward norm supremum.

**Theorem.** Put `rho=1/sqrt(2)`. Every admissible map with Delta<=rho
has the following exact classification on the sum-one fiber. On each
shell `|Re(d)|+|Im(d)|=R`, for odd R>=1, it is one of two permutations.
One has two cycles of length R, and the other has one cycle of length 2R.
Consequently, no such map has any finite global order.

More quantitatively, if `F^m=id` for a positive integer m, then 4 divides
m and

```text
Delta >= sqrt(2m^2+4m+3)-sqrt(2m^2+2m+1) > rho.
```

This bound is not claimed sharp for general m. For the fourth-power class
the exact optimum is

```text
beta=sqrt(19)-sqrt(13).
```

The fourth-power lower bound does not assume `F^2=swap`, phase covariance,
wire-swap covariance, a translation period or quarter-turn symmetry.
The global upper construction is prior work from
[CubeJerry's PR #7570](https://github.com/CrocSwap/integer-mult-bounds/pull/7570),
[pinned all-input proof](https://github.com/CubeJerry/integer-mult-bounds/blob/053c42c68165cf24fd4e8bc33c2b20d6ac3d399b/research/sharp-order-four-gaussian-rounding/proof/PROOF.md).
It has the stronger square-to-swap property and hence fourth power one.
The sharp fourth-power conclusion uses that source's upper theorem.

## 1. The exact graph and square boundary

Use real two-vectors and set

```text
J(a,b)=(-b,a), B(a,b)=(a+b,a-b), T=B/2, Q=-J.
```

For fixed s the output difference f(d) has the component parities of s.
The pair error squared is `|f(d)-Jd|^2/2`. In the sum-one fiber, both
components of this difference are odd integers. Error at most one is
therefore equivalent to both components being ±1.

Set `t=T Jd` and `u=T f(d)`. The input t ranges over color A, the even
coordinate-sum points in `L=(Z+1/2)^2`. The output u ranges over the odd
color B. The legal outputs are exactly the four unit neighbors of t.
Both changes of coordinates are bijections on their respective cosets.
The pair squared norms are `1/2+|t|^2` and `1/2+|u|^2`. Thus F gives an
injection M_A from A to B along unit edges. Its action on the input
coordinate space A is

```text
g=Q M_A,
```

because `T J B=Q`. This is a conjugate of F on this sum fiber, so their
cycle lengths agree. This half-grid framework is credited to PR #7570;
it does not impose that source's quarter-turn condition.

Let D_r be the square of half-grid points with maximum coordinate
magnitude at most `r=k+1/2`, for k>=0. Each color has `2(k+1)^2` points.
An edge from D_r to its exterior changes one boundary coordinate from
absolute value r to r+1. For a fixed squared-radius increment the radial
gap decreases as the other coordinate's magnitude increases. Hence every
such edge costs at least

```text
b(r)=sqrt(2r^2+2r+3/2)-sqrt(2r^2+1/2).
```

This exceeds rho for every r>=1/2. Positive squaring reduces the claim
to `(2r+1/2)^2>2(2r^2+1/2)`, or `2r>3/4`.

If Delta<b(r), M_A sends all A points in D_r into B points in D_r.
The two finite sets have equal size. Injectivity therefore makes this
restriction a bijection. Since Q preserves D_r and exchanges its colors,
g is a permutation of the A points in D_r. This finite-capacity argument
does not assume global surjectivity.

## 2. Classification at the optimal bound

Suppose Delta<=rho. The strict boundary inequality applies to every
D_r. The innermost square and each difference of consecutive squares
are therefore invariant under g. Equivalently M_A pairs each ring's A
points bijectively with that ring's B points.

A ring of radius `r=R/2`, for odd R>=1, is the cycle graph with 4R
vertices. Its unit edges within the ring are exactly consecutive edges
of this cycle. A perfect matching of an even cycle has only two choices:
choose either edge at one vertex, then every remaining edge is forced.
Thus the complete matching is one of the two alternating edge sets.
This classifies all possible maps; no matching ansatz was imposed on F.

Index the ring from its top right corner, through the top, left, bottom
and right sides. Each side includes its first corner and excludes its
last. The top right corner has color B, so A occupies the odd indices.
A matching sends these indices j to j+1 for all j, or to j-1 for all j,
modulo 4R. The clockwise quarter-turn Q subtracts R. Consequently g
acts on odd indices by

```text
j -> j-R+1,  or  j -> j-R-1        (mod 4R).
```

On the 2R source points this is a cyclic translation by `(1-R)/2` or
`(-1-R)/2`. Each step is relatively prime to R, and the two steps have
opposite parity. Their orders are exactly 2R and R. A translation with
order R has two cycles; one with order 2R has one cycle. The same formula
covers R=1, where the choices are identity and transposition.

Finally, `2 max(|t_1|,|t_2|)=|Re(d)|+|Im(d)|`, which identifies the
shell in the theorem. Both matchings use only tangential ring edges. For an edge with fixed
coordinate magnitude r and changing magnitudes u,u+1, one has r>=u+1.
With A=1/2+r^2+u^2, the inequality `(2u+1/2)^2<2A` gives radial gap
strictly below rho; a central sign toggle has zero gap. Arbitrary independent choices on
the rings therefore give exactly the stated sum-one possibilities.
They can be extended to other fibers with the existing global rounder
from [PR #7696](https://github.com/CrocSwap/integer-mult-bounds/pull/7696),
[pinned proof](https://github.com/aliromman/integer-mult-bounds/blob/d7be8d9131a948ea1d25833e96906ea3da979764/research/gaussian-exact-sum-global-optimum/PROOF.md).
No uniform finite m is a multiple of all these unbounded ring periods.

## 3. A positive gap for every prescribed finite order

On the zero-sum fiber the ideal Gaussian output is integral. Exact sum
and error at most one force exactness: its two Gaussian errors are e and
-e, and `2|e|^2<=1` implies e=0. Thus the nonzero difference rotates by
i at each step. If `F^m=id`, necessarily 4 divides m, so m>=4.

The function b(r) is strictly decreasing for r>=3/2. Differentiating its
two positive square roots and comparing the positive terms shows that
the derivative has the sign of `-2r^2+2r+1/2`, which is negative there.

Take `r=m+1/2` and `R=2m+1`. If Delta<b(r), the squares D_(r-1) and
D_r are both invariant: `b(r-1)>b(r)`. Their intervening ring therefore
has one of the two perfect matchings. Its periods R and 2R both exceed
m, so neither can occur under `F^m=id`. This contradiction gives
Delta>=b(m+1/2), the displayed quantitative bound. The strict inequality
above rho follows from Section 1. The result gives a necessary gap for
each fixed m; it is not an optimality theorem for every order.

## 4. Sharp fourth-power lower bound

Now assume only `F^4=id` in addition to the stated sum and error contract.
This identity itself implies injectivity. Put beta=`sqrt(19)-sqrt(13)`.
The two relevant square boundaries have costs

```text
b(3/2)=3-sqrt(5) > beta,
b(5/2)=sqrt(19)-sqrt(13)=beta.
```

For an exact rational separation, the first is greater than 763/1000,
while beta is less than 754/1000. These follow from
`2237^2>5*1000^2`, `4359^2>19*1000^2` and `3605^2<13*1000^2`.
All square-root comparisons use positive quantities.

If Delta<beta, D_(3/2) and D_(5/2) are both invariant. Their difference
has ten A points and is the ring R=5. The two complete matchings induce
two cycles of length five, or one cycle of length ten. Neither satisfies
fourth power one. Thus Delta>=beta. No square-to-swap or symmetry premise
has entered this lower argument.

The pinned global construction in PR #7570 preserves exact sum, has
error at most one, satisfies `F^2=swap` and has Delta=beta. Therefore it
also has `F^4=id` and attains the lower bound in this weaker class. Its
attaining cycle, retained here with credit, is

```text
(3,-2) -> (3i,1-3i) -> (-2,3) -> (1-3i,3i) -> (3,-2).
```

The pair squared norms alternate 13 and 19. The cycle crosses the
critical ring at equality, so the proof must use a strict lower-threshold
hypothesis. The finite cycle is not, by itself, evidence for a global
upper map; that conclusion uses the pinned all-input construction.

## 5. Evidence and limits

The verifier enumerates every perfect matching in each of 33 complete
rings, for odd R from 1 through 65. It finds exactly two in each ring.
A direct orbit traversal and a separate gcd calculation agree on all
66 induced maps. All 2244 exterior edges from the corresponding squares
have radial cost strictly above rho and the exact Gaussian error one.
The two critical squares retain every exterior edge and exact comparison
with beta. Both ten-point maps are explicit in RESULT.json.

Sixteen prescribed orders from 4 through 64 check the quantitative gap
and the incompatible large-ring orders. The source's attaining four-cycle
has direct sum, error and radial checks. Collision, forbidden central
outward-edge and strict-boundary controls pass. All arithmetic is integral.
These finite checks corroborate the all-ring argument, not a search-based
claim about arbitrary maps.

The optimal-bound classification is stated on the sum-one fiber. It does
not classify every sum fiber or all maps above rho. The general finite-order
gap is not claimed sharp except for the separately proved fourth-power
case. A larger-block representation, extra state, relaxed exact sum or
a different error allowance is outside this theorem. The conjugate-inverse
condition is not an upper-construction promise for the fourth-power class.

No physical provider, native tariff, full caller, multiplier invoice,
new kappa or selected-assumption discharge is supplied. The selected
frontier and all five assumptions remain unchanged. Full predecessor
package replays, selected cold replay, Lean and Docker were not run.
Independent human and formal-kernel review are unclaimed.

Prepared by Ali Romman with substantial OpenAI Codex assistance.
[CREDITS.md](CREDITS.md) gives the precise new and retained source roles.
Apache-2.0.
