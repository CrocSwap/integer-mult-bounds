# Forward radial slack for exact-sum Gaussian rounding

Any injective rounding of the ideal Gaussian pair that preserves the sum
and has Euclidean error at most one must have forward outward norm slack at
least $\sqrt5-\sqrt3$. Eight inputs in the sum-one fiber suffice. Below
that threshold they have six distinct legal outputs. At equality they have
an explicit matching, so the bound is sharp on these eight inputs.

This is a scoped proof with an exact finite witness. It gives a necessary
bound on the whole Gaussian-integer domain for the exact-sum contract.
Global attainment remains open. The proof uses injectivity, exact sum and
the error cap. It applies to maps with arbitrary behavior outside the eight
inputs and makes no assumption about the inverse or powers of the map.

## Proof

Let $x,y\in\mathbb Z[i]$, $s=x+y$, and $d=x-y$. The ideal positive
Gaussian pair is
$$
C_+(x,y)=((s+id)/2,(s-id)/2).
$$
The norm on a pair is $\|(x,y)\|=\sqrt{|x|^2+|y|^2}$. Its forward
outward slack under a map $F$ is
$\sup_z\max(0,\|F(z)\|-\|z\|)$.

Restrict to $s=1$. Write $x=a+ib$, so $y=1-x$, and let
$$
N(a,b)=a^2+(1-a)^2+2b^2.
$$
This is the squared pair norm. The first ideal output has coordinates
$(1/2-b,a-1/2)$. An exact-sum output is determined by its first
coordinate $c+ie$. Its squared pair error is twice the squared
distance from $c+ie$ to the first ideal output. Each real coordinate
of that ideal output is a half-integer. Thus error at most one holds
exactly at the four candidates
$$
(c,e)\in\{-b,1-b\}\times\{a-1,a\}.
$$
Every candidate has error exactly one.

The following table exhausts $N(a,b)\le5$. The output column lists the
possible squared norms before imposing a radial bound.

| Input squared norm | First input coordinates | Inputs | Output squared norms |
| ---: | --- | ---: | --- |
| 1 | $a\in\{0,1\}, b=0$ | 2 | $1,3$ |
| 3 | $a\in\{0,1\}, b\in\{-1,1\}$ | 4 | $1,3,5,7$ |
| 5 | $a\in\{-1,2\}, b=0$ | 2 | $3,9$ |

Set $\alpha=\sqrt5-\sqrt3$. Below $\alpha$, a norm-one input
cannot reach squared norm 3 because $\sqrt3-1>\alpha$.
An input of squared norm 3 cannot reach 5 or 7, and an input of squared
norm 5 cannot reach 9 because $3-\sqrt5>\alpha$. To see the two strict
inequalities, square the equivalent positive comparisons
$2\sqrt3>1+\sqrt5$ and $3+\sqrt3>2\sqrt5$. They reduce to
$3>\sqrt5$ and $3\sqrt3>4$, respectively.

The union of all allowed outputs is contained in $N(c,e)\le3$. This set
has six points by the first two rows of the table. Eight inputs cannot
map injectively into six outputs. The matching below attains the threshold
on this finite domain. It lists the first input and first output
coordinates. In both cases the second Gaussian integer is one minus
the first.

| $(a,b)$ | $(c,e)$ |
| --- | --- |
| $(-1,0)$ | $(0,-1)$ |
| $(0,-1)$ | $(1,-1)$ |
| $(0,0)$ | $(0,0)$ |
| $(0,1)$ | $(-1,0)$ |
| $(1,-1)$ | $(2,0)$ |
| $(1,0)$ | $(1,0)$ |
| $(1,1)$ | $(0,1)$ |
| $(2,0)$ | $(1,1)$ |

The eight outputs are distinct and obey the candidate formula, with two
edges from squared norm 3 to 5 and the rest weakly inward. Hence
$\alpha$ is also the exact optimum on this part of the sum-one fiber.

## Reproduce

Run from the repository root with CPython 3.12 and its standard library.

~~~sh
python3.12 -B scripts/research_package.py --package research/gaussian-exact-sum-forward-slack
python3.12 -B scripts/check_research_commit.py --package research/gaussian-exact-sum-forward-slack --check-source-history
python3.12 -W error -B research/gaussian-exact-sum-forward-slack/verify.py
python3.12 -W error -O -B research/gaussian-exact-sum-forward-slack/verify.py
~~~

The verifier enumerates all eight inputs and checks the scaled error
directly in Gaussian-integer coordinates. The input scan covers
$-2\le a,b\le2$, which contains $N\le5$. Each possible first output
coordinate is within one of its half-integer center, so the output scan
over $[-3,3]^2$ includes every error-one candidate. All 32 edges have
error one. The verifier finds 16 strict edges to six distinct outputs and
four threshold ties. It checks every edge of the displayed matching and
uses integer comparisons to isolate the strict and tied cases. The
expected status is PASS_GAUSSIAN_EXACT_SUM_FORWARD_SLACK.

## Open next questions

Can an all-size exact-sum matching attain $\alpha$, or does a different
finite set in the sum-one fiber force more? First test complete
neighborhoods beyond squared norm five at the exact threshold. A finite
matching is only a local positive control. The existing square-to-swap
construction gives a global upper bound $\sqrt{19}-\sqrt{13}$. A
physical caller contract would also need to specify the inverse,
ordered stages and implementation cost.
[#7570 proof](https://github.com/CubeJerry/integer-mult-bounds/blob/053c42c68165cf24fd4e8bc33c2b20d6ac3d399b/research/sharp-order-four-gaussian-rounding/proof/PROOF.md)

## Credit

This contribution was produced by Nick Petalas. Ali Romman's #6509 supplies
the ideal pair and exact-sum rounding contract. Jerry Chen's #7570 uses
fixed-sum fibers in the square-to-swap class and leaves the forward bound
without that identity open. His #7571 gives finite Hall bounds for the
larger class of maps with no sum constraint. His #7572 treats affine
periods and the bounded-center family. The argument here uses the sum-one
fiber and the displayed finite table. Independent human and formal
proof-kernel review are unclaimed. Apache-2.0.
[#6509](https://github.com/CrocSwap/integer-mult-bounds/pull/6509),
[#7570](https://github.com/CrocSwap/integer-mult-bounds/pull/7570),
[#7571](https://github.com/CrocSwap/integer-mult-bounds/pull/7571),
[#7572](https://github.com/CrocSwap/integer-mult-bounds/pull/7572)
