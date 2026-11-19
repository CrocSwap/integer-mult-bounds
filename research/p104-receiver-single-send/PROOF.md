# Sharp direct repair cost at receiver 127

## Cut and price

Fix the rational word with SHA-256 c447b6d5ba956fbe40834fe3c1bc69af2f225736f1b97ecd84b57bab9dd283cb on 1,289 independent rational coordinates. Its 5,709 paid transfers and 1,289 terminal rules run on 1,103 fixed charts. The old path is chart $278\to288\to127$ through slots 95914 and 88. Its grades are 2 and 5. Remove both transfers. Keep the original initial stocks, all other paid rows, all other routes, all other chart assignments, and the exterior terminal rules. The 901 surviving deposits at receiver 127 may be combined freely. It has no initial coordinates and no outgoing paid transfer. Slot 95914 had only one reader, slot 88. Slot 88 had only two readers, both receiver terminals. Thus removing the path leaves every surviving paid stock value equal to its original value. [Pinned incumbent](https://github.com/CrocSwap/integer-mult-bounds/tree/89a67c404226d51028e135de2b9169e9020d57af/research/p104-iterated-returns/continuation) · [Predecessor stock contract](https://github.com/CrocSwap/integer-mult-bounds/blob/0893abefcc894991b67b2315f7e85e0dc4d58c5e/research/p104-paid88-stock-cones/STOCK.md)

Allow any finite number of new direct transmissions from any original chart to receiver 127. The calculation charges only their paid grades and grants all local combining and receiving rules for free. Even the lower-bound relaxation lets each donor see every surviving arrival at its chart over the whole word. In its deterministic adaptive version the receiver may announce its entire transcript freely and choose the next donor from that transcript. Donors receive no other extra input. The upper bound uses a fixed chronological, rational-linear word with two sends at the original slots. No lower bound here requires speculative information about a later operator or the cost of a receiver addition.

Chart 127 spans the whole nine-dimensional binary frame space. Every original chart of dimension $r$ is contained in that space, so its direct send has grade $9-r$. For any nonnegative nondecreasing discrete concave tariff $p$ on grades $0,\ldots,9$, with $p(0)=0$, the minimum paid replacement cost is

$$
p(8)+p(1).
$$

The minimum number of direct sends is two. The proof separately establishes impossibility for one send and attains the displayed tariff with two.

## Four inputs separate all senders

Give all unlisted coordinates value zero. Evaluate the original local rational rules on the following four inputs. A chart is live if some initial coordinate or surviving deposit in its full-time stock differs from its value on zero input. Each test has zero on all 901 surviving receiver deposits and value one on terminal 155442. Each requires at least one message from a live chart.

| Test | Nonzero public coordinates | Number of live charts | Property used |
|---|---|---:|---|
| A | $x_{674}=1,\ x_{722}=1$ | 3 | Exactly charts 11, 58 and 278 |
| B | $x_{722}=1,\ x_{780}=-1$ | 293 | Chart 11 is silent and each live chart has grade at least 1 |
| C | $x_{674}=1,\ x_{825}=-1$ | 295 | Chart 58 is silent and each live chart has grade at least 1 |
| D | $x_{674}=1,\ x_{722}=1,\ x_{1288}=-1/845660160$ | 26 | Chart 278 is silent and each live chart has grade at least 5 |

Test D comes from Clear1nsight's paid-pair obstruction. Tests A–C and the full-chart stock census supply the simultaneous cover here. The forward verifier authenticates the exact compressed source and uncompressed payload, checks each rule against the sender's chronological stock, and propagates the four inputs in exact rational arithmetic. The earlier and later path slots are excluded from the census of surviving arrivals. The verifier also computes all binary frame ranks independently. [Original input D](https://github.com/CrocSwap/integer-mult-bounds/blob/0893abefcc894991b67b2315f7e85e0dc4d58c5e/research/p104-paid88-stock-cones/verify_stock.py) · [Forward verifier](verify_cut.py)

For any successful fixed strategy the chosen senders must intersect all four live sets. This applies also to the zero-input branch of a deterministic adaptive strategy. If its branch misses a live set, apply the corresponding test. The local input and prior transcript at every queried chart then coincide with their values on zero. The receiver takes the same branch and gets the same answer, although its required terminal changes from zero to one. Arbitrary deterministic encodings and nonlinear receiver postprocessing obey this implication.

Test A forces a donor from $\{11,58,278\}$. If chart 11 is used, its grade is 8 and B requires another sender at grade at least 1. If chart 58 is used, C does the same. Otherwise chart 278 is used at grade 7 and D requires another sender at grade at least 5. No individual chart passes all tests. Concavity and monotonicity yield $p(8)-p(7)\le p(2)-p(1)\le p(5)-p(1)$. Every allowed direct strategy therefore costs at least $p(8)+p(1)$. This bound includes arbitrary extra grade-zero messages.

## Chronological construction and exact operator

At slot 95914 send the initial $x_{674}$ from chart 11 directly to chart 127. At slot 88 send stock atom 101539 from chart 138 directly to chart 127. Its old deposit occurs at time 3396, strictly before the replacement send at time 4067, and its full public-coordinate expansion is $x_{780}$. In the original word it is the half difference of 98143 and 100323. Their expansions are $x_{825}+x_{780}$ and $x_{825}-x_{780}$. The new pair has grades 8 and 1. On predecessor witness D the first donor sees a nonzero value. The two senders together recover the difference required on all public inputs.

Let $y_1$ and $y_2$ be the original terminals 155442 and 155490, and let $t$ be the old outlet 88. Both rows have coefficient one on $t$. Write $r_i=y_i-t$ for the original rows with that local term removed. Reverse substitution gives $y_1=x_{674}-x_{780}$. The receiver returns
$$
y'_1=x_{674}-x_{780},\qquad
y'_2=r_2-r_1+x_{674}-x_{780}.
$$
Every term in this expression is available under the literal schedule. In particular, terminal 155490 is actually installed *before* 155442, so its evaluator uses the two arriving atoms and the old deposit rows directly. The implementation checks availability of every term at both installations. It changes exactly two transfers and two terminal forms. The other 1,287 terminals have no dependency path through a changed node. Independent backward substitution verifies both changed outputs as linear forms in all 1,289 coordinates. Omitting the second receiver recoding or reversing the two source signs is detected. [Constructive verifier](verify_operator.py)

## Price at the signed target

The incumbent tariff at $\kappa=0.00387981257853$ is $p(d)=d^{1-\kappa}$. Keeping the productive fields and other paid transfers fixed, the optimal direct replacement increases the 48-call paid cost by
$$
48\big(8^{1-\kappa}+1-2^{1-\kappa}-5^{1-\kappa}\big)
\ \in\ (94.666202960674077138503464,\ 94.666202960674077138503465).
$$
The enrolled 48-call invoice already needs more than 0.379442 signed units of saving at this target. Even granting all local recoding for free, the best direct replacement increases the paid bill. This rules out reaching that target by this family of changes alone. Additional modified paid rules, cooperative intermediate exchanges or altered productive credits change the optimization problem. [Frozen incumbent tariff and target shortfall](https://github.com/CrocSwap/integer-mult-bounds/blob/0893abefcc894991b67b2315f7e85e0dc4d58c5e/research/p104-paid88-stock-cones/cones/SOURCE.json)

For power tariffs $p(d)=d^s$, $0<s\le1$, this exact cost has a unique crossover relative to the old path. The ratio
$$
\frac{8^s-5^s}{2^s-1} =
\frac{\int_5^8 x^{s-1}\,dx}{\int_1^2 x^{s-1}\,dx}
$$
strictly increases with $s$. Indeed, raising $s$ by $h>0$ multiplies the numerator by at least $5^h$ and the denominator by at most $2^h$. At $s=0$ the continuous limiting ratio is $\log(8/5)/\log 2<1$, and at $s=1$ it is 3. The unique positive equality lies between 0.25985761 and 0.25985762. The direct optimum is dearer above that crossover. The price verifier bounds the logarithm by a rational atanh series and its geometric tail, then encloses the exponential between alternating Taylor sums. All published price endpoints are obtained without floating-point arithmetic.

Prepared by apoursh with substantial OpenAI Codex assistance. Apache-2.0.
