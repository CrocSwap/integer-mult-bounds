# A restriction at one entrance chart

## The local identity

In the normalized circuit, a paid key names a scalar linear form together with its receiving chart. At a given chart, the program can take rational linear combinations of the banks it holds there. The physical schedule charges these operations. The operator between charts with frames $T_a$ and $T_b$ is $T_b T_a^{-1}$. This factorization lets the verifier check scalar identities in chart coordinates, then restore each paid operator with its actual phase. [Operator checks](catalogue.py)

Choose a helper $r$ and a linear form $s(x)=\sum_i a_i x_i$ with $a_r\ne0$. Every input in the sum is at the entrance chart of $r$. For every other public input, the compiler takes an arbitrary independent value. It substitutes

$$x_r=-\sum_{i\ne r}(a_i/a_r)x_i$$

in the rows that read the old helper. The definition is local and the final scalar schedule includes the expanded terms. In the parent contract all helper outputs are independent identity returns. Each main output depends only on its specified main partners. Thus the substitution preserves every requested surviving output. Remove the productive target for $r$ from the invoice.

At a receiving chart, suppose an exact calculation on the unrestricted parent gives $s(x)=\sum_j b_j h_j(x)$. Each $h_j$ is a bank at that chart. Choose a paid key $k$ with $b_k\ne0$. On the restricted input space its payload equals

$$h_k=-\sum_{j\ne k}(b_j/b_k)h_j.$$

Replace every read of $k$ with this expression and remove its paid send. Each receiver in one certificate step is at a different chart. The checker verifies each relation by propagating its coefficients back to the independent entrances of that step. It checks the final dependency order and the chart of every donor after each edit. This permits a later bank when the resulting graph has a valid execution order. [Constructor](quotient.py) · [Exact relation checker](witness.py)

## Helper 264

In the first step $s=x_{264}-x_{407}-x_{434}/4$. The same form has three representations on the unmodified #7708 graph. A subscript on $h$ is the paid key from the original source word.

| Receiver chart | Exact form of $s$ | Removed key | Rank |
| ---: | --- | ---: | ---: |
| 441 | $h_{94689}-h_{94690}-h_{94703}$ | 94703 | 2 |
| 527 | $h_{95863}$ | 95863 | 4 |
| 127 | $h_{103556}-h_{104045}/4-h_{104100}$ | 104100 | 3 |

Set $x_{264}=x_{407}+x_{434}/4$. The middle row in the table now gives a zero payload outright. The other two rows give a local replacement for the removed key. The productive rank for 264 is nine. The complete bill therefore removes paid ranks $(2,4,3)$ and one productive rank nine per invocation. A changed coefficient at either end of a certificate is detectable on an independent input. The replay includes an altered receiver coefficient in each orientation. [Literal certificates](QUOTIENTS.json) · [Per-step rank receipts](results/witness.json)

## Forward and transposed steps

For a transposed step, transpose the normalized scalar network. Reverse every paid edge, interchange public inputs and outputs, and transpose its scalar incidence matrix. Apply the same restriction to a helper of this transposed contract. Transpose the restricted network back. The surviving operator is the corresponding restriction of the original contract because the removed helper is an identity summand and the other outputs are independent of it. The physical catalogue uses the resulting forward circuit and its ordered chart frames.

The 14 forward and 19 transposed steps use stable source labels. For intermediate bookkeeping the constructor isolates each retired label as one formal identity row. At the end it checks that the row has no other reader, deletes it and renumbers every surviving entrance, output and hosted partner. The executable graph has 1,468 public fields, including 400 main fields. Its 1,068 helpers have distinct positive returns. All 16 calls assign fresh helper owners. [Compact graph and label checks](quotient.py) · [Caller binding](application.py)

## Complete price

For each step the paid ranks $d_1,\ldots,d_m$ are positive, $m\ge2$, and their sum is the rank $d$ of the lost target. With $0<t<1$, strict subadditivity gives $\sum_i d_i^t>d^t$. The change improves productive value minus paid cost by 16 times this difference over the complete caller. Both rank masses fall by 3,200. Their surplus stays at 1,328. The fixed caller and root jobs enter the bill at their actual multiplicities. A second count subtracts each certificate debit from the published parent and checks the result against the compact graph.

Two directed calculations give the raw crossing bracket. The compiler uses the interior probe 0.00376154487710 and gives the lower bound 0.00376154487703. The retained BIT pin is 0.00376669. All 54 strict and four functional inequalities pass. The implementation also charges the scalar loops, integer conversions, transfers, resets, private storage and occupied ancestor views under the inherited machine interfaces. [Signed invoice, power intervals and physical charges](results/application.json)

## How the restrictions were found

For an entrance chart, form the span of its independent input coordinates. Intersect this span with the scalar values held at each receiving chart. Intersections between two receiver spaces give candidate directions shared by several receivers. For each candidate, test which helper can serve as its pivot and which paid keys can be removed without a dependency cycle. Compare the lost productive rank with every removable paid rank. Recompute after an accepted restriction and repeat in the opposite orientation. The search used modular arithmetic. The published certificate checks every selected identity over the rationals. It establishes a feasible graph and leaves optimality open.
