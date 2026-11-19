# Ten minimal-grade cooperative repairs

## Frozen communication model

Use the 1,289-coordinate rational word from #7786. Delete paid slots 95914 and 88, the original route from chart 278 to chart 288 to chart 127. Keep every other paid rule, its schedule, the 1,103 chart assignments, the initial atoms and the exterior terminal operators fixed. Slot 95914 has only one reader, slot 88. The only readers of 88 are terminals 155442 and 155490 at 127. Thus every surviving paid deposit is the same function of the public input as before. Receiver 127 has no public atom or paid egress and retains 901 arrivals. We grant arbitrary local arithmetic and require exact terminal outputs. The only permitted senders and intermediate nodes are original chart labels. The inputs, coefficients, destinations and values of surviving paid rows stay fixed; new information can leave a chart only over a replacement message or the granted equal-span sharing. The paid comparison freezes the productive ledger and charges only the replacement communication. [Incumbent word](https://github.com/CrocSwap/integer-mult-bounds/tree/89a67c404226d51028e135de2b9169e9020d57af/research/p104-iterated-returns/continuation) · [Predecessor cut](https://github.com/CrocSwap/integer-mult-bounds/blob/864d15105ceb2f7a5cdbc6bedc72a9bc273d5e8e/research/p104-receiver-single-send/PROOF.md)

A chart's frame spans a binary subspace of the nine-dimensional ambient space. Each new paid send joins nested spans in either direction and has integer grade equal to the absolute difference of their dimensions. We even allow unrestricted sharing between labels with the same span. A fixed chronological protocol may add any finite number of sends, with arbitrary deterministic payloads depending on local stock and earlier arrivals. The lower bound gives each chart every surviving deposit it ever receives in the frozen word; the improved access can only help the protocol. Local choices cannot signal to other charts without communication. The constructive programs use only chronological rational-linear forms. [Predecessor chart-comparability and pricing check](https://github.com/CrocSwap/integer-mult-bounds/blob/0893abefcc894991b67b2315f7e85e0dc4d58c5e/research/p104-paid88-stock-cones/cones/portable.py)

## Information must travel seven grades

For a public input, call a chart live when its frozen local stock differs from its stock at zero. Quotient all equal-span labels into free communication classes. There is only one nonsingleton class, labels 1091 and 1092, and neither label is live on any of the four tests. The original terminal 155442 is one on every test and zero at the origin. Here are the only nonzero public coordinates of each test.

| Test | Input | Live charts | Use |
|---|---|---:|---|
| A | $x_{674}=x_{722}=1$ | 3 | Exactly 11, 58 and 278, of ranks 1, 1 and 2 |
| B | $x_{722}=1, x_{780}=-1$ | 293 | Chart 11 is silent |
| C | $x_{674}=1, x_{825}=-1$ | 295 | Chart 58 is silent |
| D | $x_{674}=x_{722}=1, x_{1288}=-1/845660160$ | 26 | Only 288 is live between the spans of 278 and 127, inclusive |

The underlying test inputs appeared in #7807; test D originates in #7795. We recompute their observations on the immutable word and independently intersect the live set with the span interval. All 901 receiver deposits vanish on each test. [Four-column and interval check](check_paths.py) · [Origin of D](https://github.com/CrocSwap/integer-mult-bounds/blob/0893abefcc894991b67b2315f7e85e0dc4d58c5e/research/p104-paid88-stock-cones/STOCK.md)

On each test there must be a chronological path from some live class to 127. Otherwise, induction over the transmissions shows that every datum reaching the receiver agrees with its value on zero. Even one paid send is impossible: its sending class must be live on all four tests, and their intersection is empty. Let $G$ be the sum of the grades of all new sends. The path forced by A starts at rank at most two and ends at rank nine. The triangle inequality for the rank differences gives $G\ge7$.

If $G=7$, its source must be chart 278. Every positive send belongs to this path, every rank step increases and every participating span lies in the closed interval from 278 to 127. In particular, other incoming branches, duplications and reverse sends each force a larger total grade. On D the path must pick up information in the same interval. The computed intersection forces chart 288. Below 288 the only possible strict intermediate chart above 278 is 561, of rank three. Above 288 and below 127 the only possibilities are 239, 267, 477 and 1100, all of rank eight, with distinct spans. Thus a minimal-grade path uses 561 optionally before 288 and at most one of the four upper charts afterwards. There are exactly ten paths.

For a receiver that directs successive sends using only its own transcript, the same lower bound applies to the zero-input branch and hence to the worst case. Until the receiver first distinguishes a test, it makes the same requests and broadcasts the same transcript as on zero. A differing arrival must therefore have a chronological paid path from a live class in this common prefix. Apply that observation to each test on the zero-input branch. The ten-path classification refers to a fixed successful topology or to such a branch when its total grade equals seven.

## Realizing every path

Take either original send $a\to b$. To insert chart $m$, transmit the exact original payload from $a$ to $m$ immediately before its old slot, and forward that one scalar from $m$ to $b$ at the old slot. The strict containments above give legal nested routes. Every original rule sees its original inputs at its original position. The substitutions on the two original legs can be chosen independently. Each path therefore determines a chronological word with the full original operator. The replay builds all ten words, checks source ownership and chronology at every instruction, contracts inserted copies and compares every original rule, then independently expands the two affected terminal rows in the 1,289 coordinates. A sign error on the lower subdivision changes the protected output. [Constructive operator check](check_operators.py)

## Target price and separation

Write $p(d)=d^{1-\kappa}$ with the enrolled $\kappa=0.00387981257853$. Any nonnegative increasing concave tariff with $p(0)=0$ orders the four grade-seven classes weakly in the table's order. The two optional subdivisions add $2p(1)-p(2)$ and $p(4)+p(1)-p(5)$ respectively. Concavity makes the former nonnegative and at most the latter. At the enrolled exponent both inequalities are strict. Across 48 rational calls, each printed decimal below is a strict lower endpoint with enclosure width $10^{-24}$, except for the exact zero.

| Grade sequence | Distinct routes | Additional paid cost against incumbent |
|---|---:|---:|
| 2, 5 | 1 | 0 |
| 1, 1, 5 | 1 | 0.257824154185337662623932 |
| 2, 4, 1 | 4 | 0.464055177013712144726725 |
| 1, 1, 4, 1 | 4 | 0.721879331199049807350658 |

All other successful positive-send topologies have $G\ge8$ and at least two positive grades. Their cost is at least $p(7)+p(1)$. If a grade is already seven or larger, a second positive grade proves this. Otherwise trim the integer grades to a sum of eight, then transfer units from smaller to larger entries until they reach seven and one. Increasingness allows trimming and concavity makes each concentration nonincreasing in cost. At the target, $48[p(7)+p(1)-p(2)-p(5)]$ lies in $47.224621260611063462113308+(0,10^{-24})$. We use this as a lower bound on the outside class, without claiming attainment. It strictly separates every other topology from all ten. [Rational tariff enclosure](check_prices.py) · [Enrolled target](https://github.com/CrocSwap/integer-mult-bounds/blob/0893abefcc894991b67b2315f7e85e0dc4d58c5e/research/p104-paid88-stock-cones/cones/SOURCE.json)

More generally the same strict separation holds whenever $p(7)+p(1)>p(4)+3p(1)$. At the enrolled tariff the incumbent is the unique optimal positive topology after free sharing is contracted. The four-return invoice needs a positive saving even before any local costs of a recoding are charged. This complete frozen-cut comparison yields zero best saving and leaves repairs that alter the surviving paid operators, frames or productive terms open.
